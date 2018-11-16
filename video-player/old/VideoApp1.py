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
		self.lastFrameTime = 0
		self.lastFrameInterval = None
		
		self.myFrameInterval = 30
		
		self.thread = None
		#self.stopEvent = None
 
		self.paused = False
 		
		# initialize the root window and image panel
		self.root = tkinter.Tk()

		topFrame = tkinter.Frame(self.root)
		topFrame.pack( side = tkinter.TOP )

		#
		# video file tree
		self.videoFileTree = ttk.Treeview(topFrame, padding=(5,5,5,5))
		self.videoFileTree["columns"]=("one","two","three","four")
		self.videoFileTree.column("one", width=100 )
		self.videoFileTree.column("two", width=100)
		self.videoFileTree.column("three", width=100)
		self.videoFileTree.column("four", width=100)
		self.videoFileTree.heading("one", text="coulmn A")
		self.videoFileTree.heading("two", text="column B")
		self.videoFileTree.heading("three", text="column C")
		self.videoFileTree.heading("four", text="column D")

		self.videoFileTree.insert("" , "end", text=fileName, values=(width,height,fps,numFrames))

		self.videoFileTree.bind("<Double-1>", self.tree_double_click)
		self.videoFileTree.bind("<ButtonRelease-1>", self.video_tree_single_click)
		
		self.videoFileTree.pack(side=tkinter.LEFT)

		# video file tree scroll bar
		self.videoFileTree_scrollBar = ttk.Scrollbar(topFrame, orient="vertical")
		self.videoFileTree_scrollBar.config(command = self.videoFileTree.yview)
		#self.videoFileTree_scrollBar.pack(side=tkinter.TOP)
		self.videoFileTree.configure(yscrollcommand=self.videoFileTree_scrollBar.set)
		
		#
		# event tree
		self.eventTree = ttk.Treeview(topFrame, padding=(5,5,5,5))
		self.eventTree["columns"]=("one","two","three","four")
		self.eventTree.heading("one", text="Type")
		self.eventTree.heading("two", text="Frame")
		self.eventTree.heading("three", text="ms")
		self.eventTree.heading("four", text="Note")

		# populate from bEventList
		self.populateEvents()
		
		#self.eventTree.bind("<Double-1>", self.event_tree_double_click)
		self.eventTree.bind("<ButtonRelease-1>", self.event_tree_single_click)
		self.eventTree.bind('<<TreeviewSelect>>', self.event_tree_single_selected)

		self.eventTree.pack(side=tkinter.LEFT)

		# event tree scroll bar
		self.eventTree_scrollBar = ttk.Scrollbar(topFrame, orient="vertical")
		self.eventTree_scrollBar.config(command = self.eventTree.yview)
		#self.eventTree_scrollBar.pack(side=tkinter.TOP)
		self.eventTree.configure(yscrollcommand=self.eventTree_scrollBar.set)
		
		"""
		# depreciated
		# edit event note
		tkinter.Label(self.root, text="Note").pack(side=tkinter.TOP)
		self.noteEntry = tkinter.Entry(self.root)
		self.noteEntry.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=tkinter.YES)
		self.noteEntry.bind('<Key-Return>', self.noteEntry_callback)
		"""
		
		# video 
		middleFrame = tkinter.Frame(self.root)
		middleFrame.pack( side = tkinter.BOTTOM )

		height = 120 #480
		width = 160 #640
		image = np.zeros((height,width,3), np.uint8)
		image = Image.fromarray(image)
		image = ImageTk.PhotoImage(image)
		self.videoPanel = tkinter.Label(middleFrame, image=image)
		self.videoPanel.image = image
		self.videoPanel.pack(side=tkinter.TOP, padx=10, pady=10) #, fill=tkinter.BOTH, expand=tkinter.YES)
		#self.videoPanel.bind('<Configure>', self._resize_image)

		bottomframe = tkinter.Frame(self.root)
		bottomframe.pack( side = tkinter.BOTTOM )

		# play/pause button (keyboard 'space' does the same)
		btn = tkinter.Button(bottomframe, text="Play/Pause",
			command=self.playPause)
		btn.pack(side=tkinter.TOP) #, fill="both", expand="yes", padx=10, pady=10)

		# frame slider
		self.frameSlider_update = None # used by self.myUpdate()
		self.frameSliderFrame = tkinter.IntVar()
		self.frameSliderFrame.set(100)
		# if 'variable=self.frameSliderFrame' is used -->> slow
		self.frameSlider = tkinter.Scale(bottomframe, from_=0, to=numFrames, orient=tkinter.HORIZONTAL,
			showvalue=True,
			command=self.frameSlider_callback) #, variable=self.frameSliderFrame)
		self.frameSlider.pack(side=tkinter.TOP) #, fill="both", expand="yes", padx=10, pady=10)
		
		#
		# callback for key presses (main window and all children)
		self.root.bind("<Key>", self.keyPress)

		"""
		# start a thread that constantly pools the video file for the most recently read frame
		#self.stopEvent = threading.Event()
		self.isRunning = True
		self.thread = threading.Thread(target=self.videoLoop, args=())
		self.thread.daemon = True
		self.thread.start()
		"""
		self.videoLoop()
		
		# set a callback to handle when the window is closed
		self.root.wm_title("PiE Video Analysis")
		self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

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
		
		#print('VideoApp.myUpdate()')
		self.frameSlider_update = False
		# set() triggers frameSlider_callback() in background! frameSlider_callback() needs to set self.frameSlider_update = True
		self.frameSlider.set(self.vs.currentFrame)
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
			
		if theKey == 'z':
			self.setFramesPerSecond(33)
		if theKey == 'x':
			self.setFramesPerSecond(100)
		if theKey == 'c':
			self.setFramesPerSecond(500)
		if theKey == '\uf700':
			# faster
			if self.myFrameInterval == 1:
				self.myFrameInterval = 0
			newFrameInterval = self.myFrameInterval + 10
			self.setFramesPerSecond(newFrameInterval)
		if theKey == '\uf701':
			# faster
			newFrameInterval = self.myFrameInterval - 10
			if newFrameInterval <= 0:
				newFrameInterval = 0
			self.setFramesPerSecond(newFrameInterval)
			
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

		image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
		image = Image.fromarray(image)
		
		image = ImageTk.PhotoImage(image)

		self.videoPanel.configure(image=image)
		self.videoPanel.image = image

		self.videoLoopID = self.videoPanel.after(self.myFrameInterval, self.videoLoop)
		
	def setFramesPerSecond(self, frameInterval):
		self.videoPanel.after_cancel(self.videoLoopID)
		self.myFrameInterval = frameInterval
		print('setFramesPerSecond() self.myFrameInterval:', self.myFrameInterval)
		self.videoLoop()
		
	def videoLoop_old(self):
		try:
			# keep looping over frames until we are instructed to stop
			#while not self.stopEvent.is_set():
			while self.isRunning:
			
				#time.sleep(0.01)
				
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
					"""
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
					"""
					
					# OpenCV represents images in BGR order; however PIL
					# represents images in RGB order, so we need to swap
					# the channels, then convert to PIL and ImageTk format
					
					image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
					image = Image.fromarray(image)

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
					
					image = ImageTk.PhotoImage(image)

					tmpNow = time.time()
					self.lastFrameInterval = tmpNow - self.lastFrameTime
					self.lastFrameTime = tmpNow
					if self.lastFrameInterval > 0.2:
						print('last interval:', self.lastFrameInterval, 'Q.qsize():', self.vs.Q.qsize(), 'currentFrame:', self.vs.currentFrame)

					# update the panel so we see image
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
