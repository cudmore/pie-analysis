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
class VideoApp:
	def __init__(self, vs):
		"""
		vs: FileVideoStream
		"""

		# parameters from FileVideoStream
		path = vs.streamParams['path']
		fileName = vs.streamParams['fileName']
		width = vs.streamParams['width']
		height = vs.streamParams['height']
		fps = vs.streamParams['fps']
		numFrames = vs.streamParams['numFrames']

		self.events = bEventList.bEventList(path)
		
		self.vs = vs
		self.frame = None
		self.thread = None
		#self.stopEvent = None
 
		self.paused = False
 		
		# initialize the root window and image panel
		self.root = tkinter.Tk()

		#
		# video file tree
		self.videoFileTree = ttk.Treeview(self.root)
		self.videoFileTree["columns"]=("one","two","three","four")
		self.videoFileTree.column("one", width=100 )
		self.videoFileTree.column("two", width=100)
		self.videoFileTree.column("three", width=100)
		self.videoFileTree.column("four", width=100)
		self.videoFileTree.heading("one", text="coulmn A")
		self.videoFileTree.heading("two", text="column B")
		self.videoFileTree.heading("three", text="column C")
		self.videoFileTree.heading("four", text="column D")

		"""
		self.videoFileTree.insert("" , 0,    text="Line 1", values=("1A","1b"))

		id2 = self.videoFileTree.insert("", 1, "dir2", text="Dir 2")
		self.videoFileTree.insert(id2, "end", "dir 2", text="sub dir 2", values=("2A","2B"))

		##alternatively:
		self.videoFileTree.insert("", 3, "dir3", text="Dir 3")
		self.videoFileTree.insert("dir3", 3, text=" sub dir 3",values=("3A"," 3B"))
		"""
		
		self.videoFileTree.insert("" , "end",    text=fileName, values=(width,height,fps,numFrames))

		self.videoFileTree.bind("<Double-1>", self.tree_double_click)
		self.videoFileTree.bind("<ButtonRelease-1>", self.video_tree_single_click)
		
		self.videoFileTree.pack()

		self.videoFileTree.pack(padx=5, pady=10, side=tkinter.TOP)
		#self.videoFileTree.pack()
		# end videoFileTree

		#
		# event tree
		self.eventTree = ttk.Treeview(self.root)
		self.eventTree["columns"]=("one","two","three","four")
		self.eventTree.heading("one", text="Type")
		self.eventTree.heading("two", text="Frame")
		self.eventTree.heading("three", text="ms")
		self.eventTree.heading("four", text="Note")

		#self.eventTree.bind("<Double-1>", self.event_tree_double_click)
		self.eventTree.bind("<ButtonRelease-1>", self.event_tree_single_click)
		self.eventTree.bind('<<TreeviewSelect>>', self.event_tree_single_selected)

		self.eventTree.pack(side=tkinter.TOP)

		# event tree scroll bar
		self.eventTree_scrollBar = ttk.Scrollbar(self.root, orient="vertical")
		self.eventTree_scrollBar.config(command = self.eventTree.yview)
		self.eventTree_scrollBar.pack(side=tkinter.TOP)
		self.eventTree.configure(yscrollcommand=self.eventTree_scrollBar.set)
		
		# video 
		height = 480
		width = 640
		image = np.zeros((height,width,3), np.uint8)
		image = Image.fromarray(image)
		#self.frame = image # sloppy
		image = ImageTk.PhotoImage(image)
		#self.videoPanel_isinit = False
		self.videoPanel = tkinter.Label(image=image)
		self.videoPanel.image = image
		self.videoPanel.pack(side=tkinter.TOP, padx=10, pady=10, fill=tkinter.BOTH, expand=tkinter.YES)
		#self.videoPanel.bind('<Configure>', self._resize_image)

		# play/pause button (keyboard 'space' does the same)
		btn = tkinter.Button(self.root, text="Play/Pause",
			command=self.playPause)
		btn.pack(side=tkinter.TOP, fill="both", expand="yes", padx=10, pady=10)

		# frame slider
		self.frameSlider_update = None # used by self.myUpdate()
		self.frameSliderFrame = tkinter.IntVar()
		self.frameSliderFrame.set(100)
		# if 'variable=self.frameSliderFrame' is used -->> slow
		self.frameSlider = tkinter.Scale(self.root, from_=0, to=numFrames, orient=tkinter.HORIZONTAL,
			showvalue=True,
			command=self.frameSlider_callback) #, variable=self.frameSliderFrame)
		self.frameSlider.pack(side=tkinter.TOP, fill="both", expand="yes", padx=10, pady=10)
		
		#
		# callback for key presses (main window and all children)
		self.root.bind("<Key>", self.keyPress)

		# start a thread that constantly pools the video file for the most recently read frame
		#self.stopEvent = threading.Event()
		self.isRunning = True
		self.thread = threading.Thread(target=self.videoLoop, args=())
		self.thread.start()

		# set a callback to handle when the window is closed
		self.root.wm_title("PiE Video Analysis")
		self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

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
		item = self.eventTree.identify('item',event.x,event.y)
		
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
		ms = self.vs.stream.get(cv2.CAP_PROP_POS_MSEC)
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
		
		# set not of selected event
		if theKey == 'n':
			print('keyPress() n will set note of selected event -->> not implemented')
			
		# delete vent
		if theKey == 'd':
			print('keyPress() d will delete -->> not implemented')
			
	def addEvent(self, theKey, frame, ms):
		# events have 

		# todo: switch this to internal data structure, DO NOT query actual list
		self.events.AppendEvent(theKey, frame, ms)
		
		# get a tuple (list) of item names
		children = self.eventTree.get_children()
		numInList = len(children)

		position = "end"
		numInList += 1
		text = str(numInList)
		self.eventTree.insert("" , position, text=text, values=(theKey, frame, ms))
		
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
						#cv2.putText(self.frame, "Queue Size: {}".format(self.vs.Q.qsize()),
						#	(10, 30), cv2.FONT_HERSHEY_PLAIN, fontScale, (0, 0, 255), 2)	
						cv2.putText(self.frame, "Frame Number: {currentFrame}/{numFrames}".format(currentFrame=self.vs.currentFrame, numFrames=self.vs.streamParams['numFrames']),
							(10, 50), cv2.FONT_HERSHEY_PLAIN, fontScale, (0, 255, 0), 2)	
						cv2.putText(self.frame, "ms: {ms}".format(ms=self.vs.milliseconds),
							(10, 70), cv2.FONT_HERSHEY_PLAIN, fontScale, (0, 255, 0), 2)

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
		time.sleep(0.2)
		print('1')
		self.vs.stop()
		print('2')
		time.sleep(0.2)
		self.root.quit()