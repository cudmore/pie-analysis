# Author: Robert Cudmore
# Date: 20181101

"""
Create a video editing interface using tkinter
"""

import time
import threading

import numpy as np

from PIL import Image
from PIL import ImageTk
from PIL import ImageFont
from PIL import ImageDraw

import cv2

import tkinter
from tkinter import ttk

import bEventList

##################################################################################
class myNoteDialog:
	"""Opens a modal dialog to set the note of an event"""
	def __init__(self, parentApp):
		self.parentApp = parentApp
		top = self.top = tkinter.Toplevel(parentApp.parent)
		tkinter.Label(top, text="Note").pack()

		self.e = tkinter.Entry(top)
		self.e.bind('<Key-Return>', self.ok0)
		self.e.focus_set()
		self.e.pack(padx=5)

		b = tkinter.Button(top, text="OK", command=self.ok)
		b.pack(pady=5)

	def ok0(self, event):
		print("value is:", self.e.get())
		self.top.destroy()
	def ok(self):
		print("value is:", self.e.get())
		self.top.destroy()
	def _setNote(txt):
		item = self.parentApp.eventTree.focus()

##################################################################################
class VideoApp:
	def __init__(self, vs):
		"""
		TKInter application to create interface for loading, viewing, and annotating video
		
		vs: FileVideoStream
		"""

		# parameters from FileVideoStream
		path = vs.streamParams['path']
		fileName = vs.streamParams['fileName']
		width = vs.streamParams['width']
		height = vs.streamParams['height']
		fps = vs.streamParams['fps']
		numFrames = vs.streamParams['numFrames']

		self.eventList = bEventList.bEventList(path)
		
		self.vs = vs
		self.frame = None
		self.thread = None
		#self.stopEvent = None
 
		self.paused = False
 		
		###
		# remember, there is still a ton of other code in VideoApp.py
		###
		
		###
		# from test2.py
		###
		self.root = tkinter.Tk()

		pane = tkinter.PanedWindow(self.root, orient=tkinter.VERTICAL)
		pane.grid(row=0, column=0, sticky="nsew")
		self.root.grid_rowconfigure(0, weight=1)
		self.root.grid_columnconfigure(0, weight=1)

		upper_frame = tkinter.Frame(pane)
		upper_frame.grid(row=0, column=0, sticky="nsew")

		left_buttons_frame = tkinter.Frame(upper_frame, background="bisque", width=100, height=100)
		left_buttons_frame.grid(row=0, column=0)

		def myButtonCallback():
			print('myButtonCallback')

		loadButton = tkinter.Button(left_buttons_frame, anchor="n", text="Folder", command=myButtonCallback)
		loadButton.pack()

		left_tree = ttk.Treeview(upper_frame, padding=(25,25,25,25))
		left_tree.grid(row=0,column=1, sticky="nsew")
		for i in range(20):
			left_tree.insert("", "end", text=str(i))

		right_tree = ttk.Treeview(upper_frame, padding=(25,25,25,25))
		right_tree.grid(row=0,column=2, sticky="nsew")
		for i in range(20):
			right_tree.insert("", "end", text=str(i))

		upper_frame.grid_rowconfigure(0,weight=1) # 
		upper_frame.grid_columnconfigure(2,weight=1) # 

		# video
		lower_frame = tkinter.Frame(pane, borderwidth=5, width=640, height=480)
		lower_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")
		lower_frame.grid_rowconfigure(0,weight=1) # 
		lower_frame.grid_columnconfigure(0,weight=1) # 

		pane.add(upper_frame)
		pane.add(lower_frame, stretch="always")

		#
		# use self.set_aspect() with pad and content
		pad_frame = tkinter.Frame(lower_frame, borderwidth=0, background="bisque", width=200, height=200)
		pad_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=20)
		self.content_frame=tkinter.Frame(lower_frame, borderwidth=5,relief=tkinter.GROOVE, background="blue")
		self.set_aspect(self.content_frame, pad_frame, aspect_ratio=4.0/3.0) 

		# insert image into content frame
		height = 480 #480
		width = 640 #640
		image = np.zeros((height,width,3), np.uint8)
		image = Image.fromarray(image)
		image = ImageTk.PhotoImage(image)
		self.videoPanel = tkinter.Label(self.content_frame, image=image)
		self.videoPanel.grid(row=0, column=0, sticky="nsew")
		self.videoPanel.image = image

		###
		# end from test2.py
		###
		
		# start a thread that constantly pools the video file for the most recently read frame
		#self.stopEvent = threading.Event()
		self.isRunning = True
		self.thread = threading.Thread(target=self.videoLoop, args=())
		self.thread.daemon = True
		self.thread.start()

		# set a callback to handle when the window is closed
		self.root.wm_title("PiE Video Analysis")
		self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

		self.root.geometry("640x480")

	# see: https://stackoverflow.com/questions/16523128/resizing-tkinter-frames-with-fixed-aspect-ratio
	def set_aspect(self, content_frame, pad_frame, aspect_ratio):
		# a function which places a frame within a containing frame, and
		# then forces the inner frame to keep a specific aspect ratio

		def enforce_aspect_ratio(event):
			# when the pad window resizes, fit the content into it,
			# either by fixing the width or the height and then
			# adjusting the height or width based on the aspect ratio.

			# start by using the width as the controlling dimension
			desired_width = event.width
			desired_height = int(event.width / aspect_ratio)

			# if the window is too tall to fit, use the height as
			# the controlling dimension
			if desired_height > event.height:
				desired_height = event.height
				desired_width = int(event.height * aspect_ratio)

			# place the window, giving it an explicit size
			content_frame.place(in_=pad_frame, x=0, y=0, 
				width=desired_width, height=desired_height)

		pad_frame.bind("<Configure>", enforce_aspect_ratio)

	"""
	def noteEntry_callback(self, event):
		print('noteEntry_callback():', self.noteEntry.get())
		d = myNoteDialog(self.root)
	"""
		
	"""
	def _resize_image(self, event):
		new_width = event.width
		new_height = event.height

		#print('self.frame:', self.frame)
		
		#image = Image.fromarray(self.frame)
		self.frame = self.frame.resize((new_width, new_height))
		image = ImageTk.PhotoImage(self.frame)
		self.videoPanel.image = image

		#self.background_image = ImageTk.PhotoImage(self.image)
		#self.background.configure(image =  self.background_image)
	"""
	
	# video file tree
	def tree_double_click(self, event):
		"""
		event seems to be a ButtonPress
		"""
		print('tree_double_click()')
		item = self.videoFileTree.selection()[0]
		print("   tree_double_click()", self.videoFileTree.item(item,"text"))
		print("   tree_double_click()", self.videoFileTree.item(item,"values"))
		print('   item:', item)
		
	def video_tree_single_click(self, event):
		print('=== video_tree_single_click()')
		print('   event:', event)
		# use coordinates of event to get item
		item = self.videoFileTree.identify('item',event.x,event.y)
		print('   item:', item)
		print("   item text:", self.videoFileTree.item(item,"text"))
		print("   item values():", self.videoFileTree.item(item,"values"))

	# event tree
	# there should be no response to double-click
	"""
	def event_tree_double_click(self, event):
		print('event_tree_double_click()')
		item = self.eventTree.selection()[0]
		print("   event_tree_double_click()", self.eventTree.item(item,"text"))
		print("   event_tree_double_click()", self.eventTree.item(item,"values"))
		print('   item:', item)
	"""
	
	def event_tree_single_selected(self, event):
		print('=== event_tree_single_selected:', event)
		
	def event_tree_single_click(self, event):
		"""
		On single click in event list tree --> Set the video to a frame
		event: <ButtonRelease event state=Button1 num=1 x=227 y=64>
		"""
		print('=== event_tree_single_click()')

		print('   event:', event)
		
		# use coordinates of event to get item
		#item = self.eventTree.identify('item',event.x,event.y)
		
		# get selection
		item = self.eventTree.focus()
		
		if item == '':
			return 0
			
		# get a tuple (list) of item names
		#children = self.eventTree.get_children()
		#print('   children:', children)
		
		#item = self.eventTree.selection()[0]
		print('   item:', item)
		print("   item text:", self.eventTree.item(item,"text"))
		print("   item values():", self.eventTree.item(item,"values"))
		value = self.eventTree.item(item, "values")
	
		frameNumber = self.eventTree.item(item,"values")[1] # [1] is frame number
		print('   frameNumber:', frameNumber)
		frameNumber = float(frameNumber) # need first because frameNumber (str) can be 100.00000000001
		frameNumber = int(frameNumber)
		print('   event_tree_single_click() is progressing to frame number:', frameNumber)
		
		# set the video frame
		self.frame = self.vs.setFrame(frameNumber)
		#self.frameSlider_callback(str(frameNumber))
		
	# slider
	def myUpdate(self):
		# trying to impose an update interval so this does not block
		#print('myUpdate()', self.vs.currentFrame)
		# this line seems to block no matter what
		#self.frameSliderFrame.set(self.vs.currentFrame)
		
		self.frameSlider_update = False
		# set() triggers frameSlider_callback() in background! frameSlider_callback() needs to set self.frameSlider_update = True
		
		# put back in
		"""
		self.frameSlider.set(self.vs.currentFrame)
		"""
		
		#self.frameSlider.value = self.vs.currentFrame
		# this does not work as self.frameSlider.set calls frameSlider_callback() in background (different thread?)
		#self.frameSlider_update = True
		
		self.root.after(500, self.myUpdate)
		
	def frameSlider_callback(self, frameNumber):
		"""
		frameNumber : str
		"""
		#print('gotoFrame()', frameNumber)
		if self.frameSlider_update:
			self.frame = self.vs.setFrame(int(frameNumber))
		else:
			self.frameSlider_update = True
		
	# button
	def playPause(self):
		self.paused = not self.paused
		print('playPause()', 'pause' if self.paused else 'play')
		
	# key
	def keyPress(self, event):
		frame = self.vs.stream.get(cv2.CAP_PROP_POS_FRAMES)
		frame = int(float(frame))
		ms = self.vs.stream.get(cv2.CAP_PROP_POS_MSEC)
		ms = int(float(ms))
		
		print('VideoApp.keyPress() pressed:', repr(event.char), 'frame:', frame, 'ms:', ms)
		
		theKey = event.char

		# pause/play
		if theKey == ' ':
			print('space')
			self.paused = not self.paused

		# add event
		validEventKeys = ['1', '2', '3', '4', '5']
		if theKey in validEventKeys:
			print('keyPress() adding event')
			self.addEvent(theKey, frame, ms)
		
		# set note of selected event
		if theKey == 'n':
			self.setNote()
			
		# delete vent
		if theKey == 'd':
			print('keyPress() d will delete -->> not implemented')
			
	def setNote(self):
		# get selection from event list
		print('setNote()')
		item = self.eventTree.focus()
		print(self.eventTree.item(item))
		d = myNoteDialog(self)
		
	def addEvent(self, theKey, frame, ms):
		frame = float(frame)
		frame = int(frame)
		ms = float(ms)
		ms = int(ms)

		# todo: switch this to internal data structure, DO NOT query actual list
		self.eventList.AppendEvent(theKey, frame, ms, autoSave=True)
		
		# get a tuple (list) of item names
		children = self.eventTree.get_children()
		numInList = len(children)

		position = "end"
		numInList += 1
		text = str(numInList)
		self.eventTree.insert("" , position, text=text, values=(theKey, frame, ms))
		
	def populateEvents(self):
		# todo: make bEventList iterable
		for idx, event in enumerate(self.eventList.eventList):
			path = event.path
			type = event.type
			frameNumber = event.frameNumber
			ms = event.ms
			note = event.note
			
			position = "end"
			self.eventTree.insert("" , position, text=str(idx+1), values=(type, frameNumber, ms, note))
			
	# thread
	def videoLoop(self):
		try:
			# keep looping over frames until we are instructed to stop
			#while not self.stopEvent.is_set():
			while self.isRunning:
				time.sleep(0.02)
				if 0: # self.paused:
					pass
				else:
					# grab the frame from the video stream and resize it to
					# have a maximum width of 300 pixels
					if self.paused:
						fontScale = 1.4
						cv2.putText(self.frame, "Paused",
							(10, 90),
							cv2.FONT_HERSHEY_PLAIN,
							fontScale,
							(0, 0, 255),
							lineType=2,
							thickness = 2)	
						pass
					else:
						self.frame = self.vs.read()
						# update the visual display in frame slider
						# 1) this slows down video
						#self.frameSliderFrame.set(self.vs.currentFrame)
						# 2) this slows down too
						#self.frameSlider.set(self.vs.currentFrame)
						
					#self.frame = imutils.resize(self.frame, width=300)
			
					# watermark the frame using open cv
					if self.frame is not None:
						# color order is (blue, green, red)
						# using cv2 to draw on image, limited by fonts BUT way nore simple than loading a font in PIL
						fontScale = 1.2
						cv2.putText(self.frame, "Queue Size: {}".format(self.vs.Q.qsize()),
							(10, 30), cv2.FONT_HERSHEY_PLAIN, fontScale, (0, 0, 255), 2)	
						cv2.putText(self.frame, "Frame Number: {currentFrame}/{numFrames}".format(currentFrame=self.vs.currentFrame, numFrames=self.vs.streamParams['numFrames']),
							(10, 50), cv2.FONT_HERSHEY_PLAIN, fontScale, (0, 255, 0), 2)	
						cv2.putText(self.frame, "ms: {ms}".format(ms=self.vs.milliseconds),
							(10, 70), cv2.FONT_HERSHEY_PLAIN, fontScale, (0, 255, 0), 2)
						
					# OpenCV represents images in BGR order; however PIL
					# represents images in RGB order, so we need to swap
					# the channels, then convert to PIL and ImageTk format
					
					# now doing this in FileVideoStream
					image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
					image = Image.fromarray(image)

					
					## resize
					tmpWidth = self.content_frame.winfo_width()
					tmpHeight = self.content_frame.winfo_height()
					#self.frame = self.frame.resize((tmpWidth, tmpHeight), Image.ANTIALIAS)

					"""
					# resize video image to match size of window
					#print(self.videoPanel.winfo_width(), self.videoPanel.winfo_height())
					#width = self.videoPanel.winfo_width() - 20
					height = self.videoPanel.winfo_height() - 20
					width = int(height * (4/3))
					#print(width,height)
					if width>1 and height>1:
						image = image.resize((width, height), Image.ANTIALIAS)
					"""
					
					# WTF: fonts are too complicated in PIL
					# use PIL to draw text on image
					"""
					draw = ImageDraw.Draw(image)
					print('a')
					font = ImageFont.load_default()
					#font = ImageFont.load("arial.pil")
					#font = ImageFont.truetype("Roboto-Regular.ttf", 50)
					print('b')
					textLine1 = "Frame Number: {currentFrame}/{numFrames}".format(currentFrame=self.vs.currentFrame, numFrames=self.vs.streamParams['numFrames'])
					draw.text((0, 0), textLine1, font=font)
					"""
					
					image = ImageTk.PhotoImage(image)

					# if the panel is not None, we need to initialize it
					self.videoPanel.configure(image=image)
					self.videoPanel.image = image
					
					"""
					if self.videoPanel_isinit:
						self.videoPanel.configure(image=image)
						self.videoPanel.image = image
						
						#self.videoPanel = tkinter.Label(image=image)
						#self.videoPanel.image = image
						#self.videoPanel.pack(side="bottom", padx=10, pady=10)
					# otherwise, simply update the panel
					else:
						self.videoPanel.image = image
						self.videoPanel_isinit = True
					"""
						
			print('VideoApp.videoLoop() exited while')
			 
		except (RuntimeError) as e:
			print("my exception in VideoApp.videoLoop()")
			raise
 		
	def onClose(self):
		# set the stop event, cleanup the camera, and allow the rest of
		# the quit process to continue
		print("onClose()")
		self.isRunning = False
		#self.stopEvent.set()
		#time.sleep(0.2)
		self.vs.stop()
		#time.sleep(0.2)
		self.root.quit()
