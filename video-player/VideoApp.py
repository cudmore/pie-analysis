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
		top = self.top = tkinter.Toplevel(parentApp.root)
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
		item = self.parentApp.right_tree.focus()

##################################################################################
class VideoApp:
	def __init__(self, vs):
		"""
		TKInter application to create interface for loading, viewing, and annotating video
		
		vs: FileVideoStream
		"""

		myBakgroundColor = '#666666'
		
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
		self.pausedAtFrame = None
 		
		self.myFrameInterval = 30
		self.myApectRatio = 4.0/3.0
		
		myPadding = 10

		###
		# remember, there is still a ton of other code in VideoApp.py
		###
		
		###
		# from test2.py
		###
		self.root = tkinter.Tk()

		self.root.geometry("690x827")


		pane = ttk.PanedWindow(self.root, orient="vertical")
		pane.grid(row=0, column=0, sticky="nsew")
		self.root.grid_rowconfigure(0, weight=1)
		self.root.grid_columnconfigure(0, weight=1)

		upper_frame = ttk.Frame(pane)
		upper_frame.grid(row=0, column=0, sticky="nsew")

		left_buttons_frame = ttk.Frame(upper_frame)
		left_buttons_frame.grid(row=0, column=0, padx=myPadding, pady=myPadding)

		def myButtonCallback():
			print('myButtonCallback')

		loadButton = ttk.Button(left_buttons_frame, text="Folder", command=myButtonCallback)
		loadButton.pack(side="top")
		
		#
		# video file tree
		left_tree = ttk.Treeview(upper_frame)
		left_tree.grid(row=0,column=1, sticky="nsew", padx=myPadding, pady=myPadding)

		left_tree.insert("" , "end", text=fileName, values=(width,height,fps,numFrames))

		# video file tree scroll bar
		videoFileTree_scrollBar = ttk.Scrollbar(upper_frame, orient="vertical", command = left_tree.yview)
		videoFileTree_scrollBar.grid(row=0, column=1, sticky='nse', padx=myPadding, pady=myPadding)
		left_tree.configure(yscrollcommand=videoFileTree_scrollBar.set)
		
		left_tree.bind("<Double-1>", self.tree_double_click)
		left_tree.bind("<ButtonRelease-1>", self.video_tree_single_click)


		#
		# event tree
		#todo: add function to bEvent to get columns (so we change bEvent and it is reflected here)
		eventColumns = self.eventList.getColumns()
		self.right_tree = ttk.Treeview(upper_frame, columns=eventColumns, show='headings')
		self.right_tree.grid(row=0,column=2, sticky="nsew", padx=myPadding, pady=myPadding)

		# gEventColumns = ('index', 'path', 'cseconds', 'type', 'frame', 'note')
		hideColumns = ['path', 'cseconds'] # hide some columns
		displaycolumns = [] # build a list of columns not in hideColumns
		for column in eventColumns:
			self.right_tree.heading(column, text=column, command=lambda:self.treeview_sort_column(self.right_tree, 'Frame', False))
			self.right_tree.column(column, width=12)
			if column not in hideColumns:
				displaycolumns.append(column)
				
		# hide some columns
		self.right_tree["displaycolumns"] = displaycolumns

		#self.right_tree.bind("<Double-1>", self.event_tree_double_click)
		#self.right_tree.bind("<ButtonRelease-1>", self.event_tree_single_click)
		self.right_tree.bind('<<TreeviewSelect>>', self.event_tree_single_selected)

		# populate from bEventList
		self.populateEvents()

		#for i in range(20):
		#	self.right_tree.insert("", "end", text=str(i))

		# event tree scroll bar
		eventFileTree_scrollBar = ttk.Scrollbar(upper_frame, orient="vertical", command = self.right_tree.yview)
		eventFileTree_scrollBar.grid(row=0, column=2, sticky='nse', padx=myPadding, pady=myPadding)
		self.right_tree.configure(yscrollcommand=eventFileTree_scrollBar.set)

		#
		# feedback frame
		feedback_frame = ttk.Frame(upper_frame)
		feedback_frame.grid(row=1, column=0, columnspan=3, sticky="w", padx=myPadding, pady=myPadding)

		# Label also has 'justify' but is used when more than one line of text
		self.currentFrameLabel = ttk.Label(feedback_frame, width=11, anchor="w", text="Frame:")
		self.currentFrameLabel.grid(row=0, column=0)
		
		self.numFrameLabel = ttk.Label(feedback_frame, width=8, anchor="w", text="of " + str(self.vs.streamParams['numFrames']))
		self.numFrameLabel.grid(row=0, column=1)

		self.currentSecondsLabel = ttk.Label(feedback_frame, width=8, anchor="w", text="Sec:")
		self.currentSecondsLabel.grid(row=0, column=2, sticky="w")
		
		self.numSecondsLabel = ttk.Label(feedback_frame, width=8, anchor="w", text="of " + str(self.vs.streamParams['numSeconds']))
		self.numSecondsLabel.grid(row=0, column=3, sticky="w")
		
		self.currentFrameIntervalLabel = ttk.Label(feedback_frame, width=20, anchor="w", text="Interval (ms):")
		self.currentFrameIntervalLabel.grid(row=0, column=4, sticky="w")
		
		# configure sizing of upper_frame
		upper_frame.grid_rowconfigure(0,weight=1) # 
		#upper_frame.grid_rowconfigure(1,weight=0) # row 1 is feedback_frame
		upper_frame.grid_columnconfigure(0,weight=0) #  column 0 is left_buttons_frame
		upper_frame.grid_columnconfigure(1,weight=0) #  column 1 is left_tree
		upper_frame.grid_columnconfigure(2,weight=1) # column 2 is self.right_tree

		# video
		lower_frame = ttk.Frame(pane)
		lower_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")
		lower_frame.grid_rowconfigure(0,weight=1) # 
		lower_frame.grid_columnconfigure(0,weight=1) # 

		pane.add(upper_frame)
		pane.add(lower_frame)

		#
		# use self.set_aspect() with pad and content
		pad_frame = ttk.Frame(lower_frame, borderwidth=0, width=200, height=200)
		pad_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
		# put back in so we can see frame
		#self.content_frame = ttk.Frame(lower_frame, borderwidth=5,relief="groove")
		self.content_frame = ttk.Frame(lower_frame)
		self.set_aspect(self.content_frame, pad_frame, aspect_ratio=self.myApectRatio) 
				
		# insert image into content frame
		height = 480 #480
		width = 640 #640
		image = np.zeros((height,width,3), np.uint8)
		image = Image.fromarray(image)
		image = ImageTk.PhotoImage(image)
		self.videoPanel = ttk.Label(self.content_frame, image=image, text="", font=("Helvetica", 48), compound="center", foreground="green")
		self.videoPanel.grid(row=0, column=0, sticky="nsew")
		self.videoPanel.image = image

		
		#
		# frame slider
		self.frameSlider = ttk.Scale(lower_frame, from_=0, to=numFrames, orient="horizontal",
			command=self.frameSlider_callback) #, variable=self.frameSliderFrame)
		self.frameSlider.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=myPadding, pady=myPadding)
		
		###
		# end from test2.py
		###
		
		self.root.bind("<Key>", self.keyPress)
		#self.root.bind("<Key-Shift_L>", self.keyPress)

		# start a thread that constantly pools the video file for the most recently read frame
		#self.stopEvent = threading.Event()
		"""
		self.isRunning = True
		self.thread = threading.Thread(target=self.videoLoop, args=())
		self.thread.daemon = True
		self.thread.start()
		"""
		self.videoLoop()
		
		# set a callback to handle when the window is closed
		self.root.wm_title("PiE Video Analysis")
		self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

	def treeview_sort_column(self, tv, col, reverse):
		print('treeview_sort_column()', 'tv:', tv, 'col:', col, 'reverse:', reverse)
		l = [(tv.set(k, col), k) for k in tv.get_children('')]
		l.sort(reverse=reverse)

		# rearrange items in sorted positions
		for index, (val, k) in enumerate(l):
			tv.move(k, '', index)

		# reverse sort next time
		tv.heading(col, command=lambda:self.treeview_sort_column(tv, col, not reverse))
           
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

			#print('h:', self.root.winfo_height())
			#print('w:', self.root.winfo_width())
			#print('winfo_geometry:', self.root.winfo_geometry())

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
		item = self.right_tree.selection()[0]
		print("   event_tree_double_click()", self.right_tree.item(item,"text"))
		print("   event_tree_double_click()", self.right_tree.item(item,"values"))
		print('   item:', item)
	"""
	
	def event_tree_single_selected(self, event):
		print('=== event_tree_single_selected:', event)
		self.event_tree_single_click(event)
		
	def event_tree_single_click(self, event):
		"""
		On single click in event list tree --> Set the video to a frame
		event: <ButtonRelease event state=Button1 num=1 x=227 y=64>
		"""
		print('=== event_tree_single_click()')

		# get selection
		item = self.right_tree.focus()
		if item == '':
			return 0

		columns = self.right_tree['columns']				
		# assuming 'frame' exists
		frameColIdx = columns.index('frame')

		# get a tuple (list) of item names
		#children = self.right_tree.get_children()
		#print('   children:', children)
		
		#item = self.right_tree.selection()[0]
		print('   item:', item)
		print("   item text:", self.right_tree.item(item,"text"))
		print("   item values():", self.right_tree.item(item,"values"))
		values = self.right_tree.item(item, "values")
	
		frame = values[frameColIdx]
		frame = float(frame) # need first because frameNumber (str) can be 100.00000000001
		frame = int(frame)
		print('   event_tree_single_click() is progressing to frame:', frame)
		
		# set the video frame
		self.vs.setFrame(frame)
		#self.frameSlider_callback(str(frameNumber))
		
	# slider
	def myUpdate(self):
		self.frameSlider_update = False
		# set() triggers frameSlider_callback() in background! frameSlider_callback() needs to set self.frameSlider_update = True
		
		# put back in
		self.frameSlider.set(self.vs.currentFrame)
		
		# this does not work as self.frameSlider.set calls frameSlider_callback() in background (different thread?)
		#self.frameSlider_update = True
		
		self.root.after(20, self.myUpdate)
		
	def frameSlider_callback(self, frameNumber):
		"""
		frameNumber : str
		"""
		#print('gotoFrame()', frameNumber)
		frameNumber = int(float(frameNumber))
		if self.frameSlider_update:
			self.vs.setFrame(frameNumber)
		else:
			self.frameSlider_update = True
		
	# button
	def playPause(self):
		self.paused = not self.paused
		self.vs.paused = self.paused
		self.pausedAtFrame = self.vs.currentFrame
		print('playPause()', 'pause' if self.paused else 'play')
		
	# key
	def keyPress(self, event):
		frame = self.vs.stream.get(cv2.CAP_PROP_POS_FRAMES)
		frame = int(float(frame))
		ms = self.vs.stream.get(cv2.CAP_PROP_POS_MSEC)
		ms = int(float(ms))
		
		print('\nVideoApp.keyPress() pressed:', repr(event.char), 'frame:', frame, 'ms:', ms)
		print('event.keysym:', event.keysym)
		print('event.keysym_num:', event.keysym_num)
		print('event.state:', event.state)
		
		theKey = event.char

		# pause/play
		if theKey == ' ':
			self.playPause()
			
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

		if theKey == 's':
			# slower
			if self.myFrameInterval == 1:
				self.myFrameInterval = 0
			newFrameInterval = self.myFrameInterval + 10
			self.setFramesPerSecond(newFrameInterval)
		if theKey == 'f':
			# faster
			newFrameInterval = self.myFrameInterval - 10
			if newFrameInterval <= 0:
				newFrameInterval = 0
			self.setFramesPerSecond(newFrameInterval)
			
		if theKey == '\uf702' and event.state==97:
			# shift + left
			newFrame = self.vs.currentFrame - 100
			self.vs.setFrame(newFrame)
		elif theKey == '\uf702':
			# left
			newFrame = self.vs.currentFrame - 10
			self.vs.setFrame(newFrame)
		if theKey == '\uf703' and event.state==97:
			# shift + right
			newFrame = self.vs.currentFrame + 100
			self.vs.setFrame(newFrame)
		elif theKey == '\uf703':
			# right
			newFrame = self.vs.currentFrame + 10
			self.vs.setFrame(newFrame)
			
	def setNote(self):
		# get selection from event list
		print('setNote()')
		item = self.right_tree.focus()
		print(self.right_tree.item(item))
		d = myNoteDialog(self)
		
	def addEvent(self, theKey, frame, ms):
		frame = float(frame)
		frame = int(frame)
		ms = float(ms)
		ms = int(ms)

		# todo: switch this to internal data structure, DO NOT query actual list
		newEvent = self.eventList.appendEvent(theKey, frame, autoSave=True)
		
		# get a tuple (list) of item names
		children = self.right_tree.get_children()
		numInList = len(children)

		position = "end"
		numInList += 1
		text = str(numInList)
		self.right_tree.insert("" , position, text=text, values=newEvent.asTuple())
		
	def populateEvents(self):
		# todo: make bEventList iterable
		for idx, event in enumerate(self.eventList.eventList):
			position = "end"
			self.right_tree.insert("" , position, text=str(idx+1), values=event.asTuple())
			
	def videoLoop(self):
	
		# it is important to not vs.read() when paused
		if self.paused:
			self.videoPanel.configure(text="Paused")
			if (self.pausedAtFrame != self.vs.currentFrame):
				#print('VideoApp2.videoLoop() fetching new frame when paused', 'self.pausedAtFrame:', self.pausedAtFrame, 'self.vs.currentFrame:', self.vs.currentFrame)
				try:
					#print('VideoApp2.videoLoop() CALLING self.vs.read()')
					self.frame = self.vs.read()
				except:
					print('zzz qqq')
				#print('VideoApp2.videoLoop() got new frame')
				self.pausedAtFrame = self.vs.currentFrame
				#
				#self.vs.setFrame(self.vs.currentFrame)
		else:
			self.videoPanel.configure(text="")
			self.frame = self.vs.read()

		if self.frame is None:
			print('ERROR: VideoApp2.videoLoop() got None self.frame')
		else:
			## resize
			tmpWidth = self.content_frame.winfo_width()
			tmpHeight = self.content_frame.winfo_height()
			self.frame = cv2.resize(self.frame, (tmpWidth, tmpHeight)) 
		
			image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
			image = Image.fromarray(image)
		
			image = ImageTk.PhotoImage(image)

			self.videoPanel.configure(image=image)
			self.videoPanel.image = image

			#
			# update feedback labels
			self.currentFrameLabel.configure(text='Frame:' + str(self.vs.currentFrame))
			self.currentFrameIntervalLabel.configure(text='Interval (ms):' + str(self.myFrameInterval))
			self.currentSecondsLabel.configure(text='Sec:' + str(self.vs.seconds))

		# leave this here -- CRITICAL
		self.videoLoopID = self.videoPanel.after(self.myFrameInterval, self.videoLoop)
		
	def setFramesPerSecond(self, frameInterval):
		self.videoPanel.after_cancel(self.videoLoopID)
		self.myFrameInterval = frameInterval
		print('setFramesPerSecond() self.myFrameInterval:', self.myFrameInterval)
		self.videoLoop()
		
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
