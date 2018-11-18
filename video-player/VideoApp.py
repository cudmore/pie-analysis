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

from FileVideoStream import FileVideoStream
import bEventList
import bVideoList

##################################################################################
class myNoteDialog:
	"""Opens a modal dialog to set the note of an event"""
	def __init__(self, parentApp):
		self.parentApp = parentApp
		top = self.top = tkinter.Toplevel(parentApp.root)
		tkinter.Label(top, text="Note").pack()

		#
		# grab the note of selected event
		self.item = self.parentApp.right_tree.focus()
		if self.item == '':
			return 0
		columns = self.parentApp.right_tree['columns']				
		noteColIdx = columns.index('note') # assuming 'frameStart' exists
		values = self.parentApp.right_tree.item(self.item, "values")
		self.index = int(values[0]) # assuming [0] is index
		noteStr = values[noteColIdx]
		
		print('original note is noteStr:', noteStr)
		
		#
		self.e = tkinter.Entry(top)
		#self.e.delete(0, "end")
		self.e.insert(0, noteStr)
		
		self.e.bind('<Key-Return>', self.ok0)
		self.e.focus_set()
		self.e.pack(padx=5)

		cancelButton = tkinter.Button(top, text="Cancel", command=self.top.destroy)
		cancelButton.pack(side="left", pady=5)
		
		okButton = tkinter.Button(top, text="OK", command=self.ok)
		okButton.pack(side="left", pady=5)

	def ok0(self, event):
		""" Called when user hits enter """
		#print("value is:", self.e.get())
		#self.top.destroy()
		self.ok()
		
	def ok(self):
		newNote = self.e.get()
		print("new note is:", newNote)
		
		# set in our eventList
		self.parentApp.eventList.eventList[self.index].dict['note'] = newNote
		self.parentApp.eventList.save()
		
		# get the event we just set
		event = self.parentApp.eventList.eventList[self.index]
		
		# update the tree
		# todo: get this 'item' when we open dialog and use self.item
		#item = self.right_tree.focus()
		self.parentApp.right_tree.item(self.item, values=event.asTuple())

		self.top.destroy()
	def _setNote(txt):
		item = self.parentApp.right_tree.focus()

##################################################################################
class VideoApp:
	#def __init__(self, path, vs):
	def __init__(self, path):
		"""
		TKInter application to create interface for loading, viewing, and annotating video
		
		path: path to folder with video files
		vs: FileVideoStream
		"""
		
		"""
		# on selection need to make one of these, make sure it is destroyed correctly
		fvs = FileVideoStream(videoPath) #.start()
		fvs.start()
		"""
		
		# parameters from FileVideoStream
		"""
		tmpVideoFilePath = vs.streamParams['path']
		fileName = vs.streamParams['fileName']
		width = int(vs.streamParams['width'])
		height = int(vs.streamParams['height'])
		fps = int(vs.streamParams['fps'])
		numFrames = vs.streamParams['numFrames']
		"""
		
		#self.vs = vs
		self.vs = None
		self.frame = None
 
		#self.paused = False
		self.pausedAtFrame = None

		self.videoList = bVideoList.bVideoList(path)
		
		# initialize with first video in path
		firstVideoPath = self.videoList.videoFileList[0].dict['path']

		# fire up a video stream
		self.switchvideo(firstVideoPath, paused=True, gotoFrame=0)
		
		self.eventList = bEventList.bEventList(firstVideoPath)
		
 		
		self.myFrameInterval = 30
		self.myApectRatio = 4.0/3.0
		
		myPadding = 10

		###
		# tkinter interface
		###
		self.root = tkinter.Tk()

		self.root.geometry("690x827")

		self.root.grid_rowconfigure(0, weight=1)
		self.root.grid_columnconfigure(0, weight=1)

		pane = ttk.PanedWindow(self.root, orient="vertical")
		pane.grid(row=0, column=0, sticky="nsew")

		upper_frame = ttk.Frame(pane)
		upper_frame.grid(row=0, column=0, sticky="nsew")

		#
		# left button frame
		"""
		left_buttons_frame = ttk.Frame(upper_frame)
		left_buttons_frame.grid(row=0, column=0, padx=myPadding, pady=myPadding)

		def myButtonCallback():
			print('myButtonCallback')

		loadButton = ttk.Button(left_buttons_frame, text="Folder", command=myButtonCallback)
		loadButton.pack(side="top")
		"""
		
		#
		# video file tree
		videoFileColumns = self.videoList.getColumns()
		self.left_tree = ttk.Treeview(upper_frame, columns=videoFileColumns, show='headings')
		self.left_tree.grid(row=0,column=0, sticky="nsew", padx=myPadding, pady=myPadding)

		hideColumns = ['path'] # hide some columns
		displaycolumns = [] # build a list of columns not in hideColumns
		for column in videoFileColumns:
			self.left_tree.column(column, width=50)
			self.left_tree.heading(column, text=column, command=lambda c=column: self.treeview_sort_column(self.left_tree, c, False))
			if column not in hideColumns:
				displaycolumns.append(column)

		# hide some columns
		self.left_tree["displaycolumns"] = displaycolumns
		
		#self.left_tree.insert("" , "end", text=fileName, values=(fileName, width,height,fps,numFrames))
		self.populateVideoFiles()

		# video file tree scroll bar
		videoFileTree_scrollBar = ttk.Scrollbar(upper_frame, orient="vertical", command = self.left_tree.yview)
		videoFileTree_scrollBar.grid(row=0, column=0, sticky='nse', padx=myPadding, pady=myPadding)
		self.left_tree.configure(yscrollcommand=videoFileTree_scrollBar.set)
		
		#self.left_tree.bind("<Double-1>", self.video_tree_double_click)
		self.left_tree.bind("<ButtonRelease-1>", self.video_tree_single_click)

		#
		# event tree
		#todo: add function to bEvent to get columns (so we change bEvent and it is reflected here)
		"""
		eventColumns = self.eventList.getColumns()
		self.right_tree = ttk.Treeview(upper_frame, columns=eventColumns, show='headings')
		self.right_tree.grid(row=0,column=2, sticky="nsew", padx=myPadding, pady=myPadding)

		# gEventColumns = ('index', 'path', 'cseconds', 'type', 'frameStart', 'frameStop', 'note')
		hideColumns = ['path', 'cseconds'] # hide some columns
		displaycolumns = [] # build a list of columns not in hideColumns
		for column in eventColumns:
			self.right_tree.column(column, width=12)
			# lambda here is tricky, requires declaration of 'c=column'
			self.right_tree.heading(column, text=column, command=lambda c=column: self.treeview_sort_column(self.right_tree, c, False))
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
		"""
				
		# configure sizing of upper_frame
		upper_frame.grid_rowconfigure(0,weight=1) # 
		upper_frame.grid_columnconfigure(0,weight=1) #  column 0 is left_buttons_frame

		# video
		lower_frame = ttk.Frame(pane)
		lower_frame.grid(row=1, column=0, sticky="nsew")
		lower_frame.grid_rowconfigure(0,weight=0) # 
		lower_frame.grid_rowconfigure(1,weight=1) # 
		lower_frame.grid_rowconfigure(2,weight=0) # 
		lower_frame.grid_columnconfigure(0,weight=1) # event list
		lower_frame.grid_columnconfigure(1,weight=2) #  video

		pane.add(upper_frame)
		pane.add(lower_frame)

		#
		# feedback frame
		feedback_frame = ttk.Frame(lower_frame)
		feedback_frame.grid(row=0, column=1, sticky="nsew", padx=myPadding, pady=myPadding)

		# Label also has 'justify' but is used when more than one line of text
		self.currentFrameLabel = ttk.Label(feedback_frame, width=11, anchor="w", text='Frame:')
		self.currentFrameLabel.grid(row=0, column=0)
		
		self.numFrameLabel = ttk.Label(feedback_frame, width=8, anchor="w", text='of ' + str(self.vs.streamParams['numFrames']))
		self.numFrameLabel.grid(row=0, column=1)

		self.currentSecondsLabel = ttk.Label(feedback_frame, width=8, anchor="w", text='Sec:')
		self.currentSecondsLabel.grid(row=0, column=2, sticky="w")
		
		self.numSecondsLabel = ttk.Label(feedback_frame, width=8, anchor="w", text='of ' + str(self.vs.streamParams['numSeconds']))
		self.numSecondsLabel.grid(row=0, column=3, sticky="w")
		
		self.currentFrameIntervalLabel = ttk.Label(feedback_frame, width=20, anchor="w", text='Interval (ms):')
		self.currentFrameIntervalLabel.grid(row=0, column=4, sticky="w")

		#
		# use self.set_aspect() with pad and content
		pad_frame = ttk.Frame(lower_frame, borderwidth=0, width=200, height=200)
		pad_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
		# put back in so we can see frame
		#self.content_frame = ttk.Frame(lower_frame, borderwidth=5,relief="groove")
		self.content_frame = ttk.Frame(lower_frame)
		self.content_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
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

		# event view 2
		if 1:
			# this works
			#self.eventTree = ttk.Treeview(lower_frame, columns=('1','2'), show='headings')
			#self.eventTree.grid(row=0, column=1, sticky="nsew", padx=myPadding, pady=myPadding)

			eventColumns = self.eventList.getColumns()
			
			# was this
			#self.right_tree = ttk.Treeview(upper_frame, columns=eventColumns, show='headings')
			#self.right_tree.grid(row=0,column=2, sticky="nsew", padx=myPadding, pady=myPadding)
			self.right_tree = ttk.Treeview(lower_frame, columns=eventColumns, show='headings')
			self.right_tree.grid(row=0,column=0, rowspan=3, sticky="nsew", padx=myPadding, pady=myPadding)

			# gEventColumns = ('index', 'path', 'cseconds', 'type', 'frameStart', 'frameStop', 'note')
			hideColumns = ['path', 'cseconds'] # hide some columns
			displaycolumns = [] # build a list of columns not in hideColumns
			for column in eventColumns:
				self.right_tree.column(column, width=12)
				# lambda here is tricky, requires declaration of 'c=column'
				self.right_tree.heading(column, text=column, command=lambda c=column: self.treeview_sort_column(self.right_tree, c, False))
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
			eventFileTree_scrollBar = ttk.Scrollbar(lower_frame, orient="vertical", command = self.right_tree.yview)
			eventFileTree_scrollBar.grid(row=0, column=0, rowspan=2, sticky='nse', padx=myPadding, pady=myPadding)
			self.right_tree.configure(yscrollcommand=eventFileTree_scrollBar.set)
		
		#
		# frame slider
		self.frameSlider = ttk.Scale(lower_frame, from_=0, to=self.vs.streamParams['numFrames'], orient="horizontal",
			command=self.frameSlider_callback) #, variable=self.frameSliderFrame)
		self.frameSlider.grid(row=2, column=1, sticky="nsew", padx=myPadding, pady=myPadding)
		
		#
		# video control buttons
		"""
		self.frButton = ttk.Button(lower_frame, text="<<")
		self.frButton.grid(row=2, column=0, sticky="w", padx=myPadding, pady=myPadding)

		self.rButton = ttk.Button(lower_frame, text="<")
		self.rButton.grid(row=2, column=1, sticky="w", padx=myPadding, pady=myPadding)

		self.playButton = ttk.Button(lower_frame, text="Play")
		self.playButton.grid(row=2, column=2, sticky="w", padx=myPadding, pady=myPadding)
		#playButtonImage = Image.open("icons/round_play_arrow_black_18dp.jpg").convert("RGBA")
		#playButtonImage = tkinter.PhotoImage("icons/round_play_arrow_white_18dp.png")
		#self.playButton.config(image=playButtonImage)
		#self.playButton.image = playButtonImage # store a reference

		self.fButton = ttk.Button(lower_frame, text=">")
		self.fButton.grid(row=2, column=3, sticky="w", padx=myPadding, pady=myPadding)

		self.ffButton = ttk.Button(lower_frame, text=">>")
		self.ffButton.grid(row=2, column=4, sticky="w", padx=myPadding, pady=myPadding)
		"""
		
		###
		# end from test2.py
		###
		
		self.root.bind("<Key>", self.keyPress)
		#self.root.bind("<Key-Shift_L>", self.keyPress)

		self.root.update()
		pane.sashpos(0, 120)

		# this will return but run in background using tkinter after()
		self.videoLoop()
		
		# set a callback to handle when the window is closed
		self.root.wm_title("PiE Video Analysis")
		self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

	def switchvideo(self, videoPath, paused=False, gotoFrame=None):
		if self.vs is not None:
			self.vs.stop()
		
		self.vs = FileVideoStream(videoPath, paused, gotoFrame) #.start()
		self.vs.start()
		
	def treeview_sort_column(self, tv, col, reverse):
		print('treeview_sort_column()', 'tv:', tv, 'col:', col, 'reverse:', reverse)
		l = [(tv.set(k, col), k) for k in tv.get_children('')]
		
		print(l)
		
		"""
		l.sort(reverse=reverse)

		# rearrange items in sorted positions
		for index, (val, k) in enumerate(l):
			tv.move(k, '', index)

		# reverse sort next time
		tv.heading(col, command=lambda:self.treeview_sort_column(tv, col, not reverse))
		"""
		           
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
	
	# treeview util
	def _getTreeVidewSelection(self, tv, col):
		"""
		Get value of selected column
			tv: treeview
			col: (str) column name
		"""
		item = tv.focus()
		if item == '':
			return None, None
		columns = tv['columns']				
		colIdx = columns.index(col) # assuming 'frameStart' exists
		values = tv.item(item, "values") # tuple of a values in tv row
		theRet = values[colIdx]
		return theRet, item
		
	# video file tree
	def video_tree_single_selected(self, event):
		print('=== video_tree_single_selected()')
		self.video_tree_single_click(event)

	def video_tree_single_click(self, event):
		""" display events """
		print('=== video_tree_single_click()')		
		
		# get video file path
		path, item = self._getTreeVidewSelection(self.left_tree, 'path')
		print('   path:', path)

		# switch video stream
		self.switchvideo(path, paused=True, gotoFrame=0)
		
		# switch event list
		self.eventList = bEventList.bEventList(path)
		
		# populate event list tree
		self.populateEvents()
		
		# set feedback frame
		self.numFrameLabel['text'] = 'of ' + str(self.vs.streamParams['numFrames'])
		self.numSecondsLabel['text'] = 'of ' + str(self.vs.streamParams['numSeconds'])
		
		# set frame slider
		self.frameSlider['to'] = self.vs.streamParams['numFrames']
		
	def event_tree_single_selected(self, event):
		print('=== event_tree_single_selected()')
		self.event_tree_single_click(event)
		
	def event_tree_single_click(self, event):
		"""
		On single click in event list tree --> Set the video to a frame
		event: <ButtonRelease event state=Button1 num=1 x=227 y=64>
		"""
		print('=== event_tree_single_click()')
		frameStart, item = self._getTreeVidewSelection(self.right_tree, 'frameStart')
		frameStart = float(frameStart) # need first because frameNumber (str) can be 100.00000000001
		frameStart = int(frameStart)
		print('   event_tree_single_click() is progressing to frameStart:', frameStart)
		self.vs.setFrame(frameStart) # set the video frame
		
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
		
	# key
	def keyPress(self, event):
		frame = self.vs.stream.get(cv2.CAP_PROP_POS_FRAMES)
		frame = int(float(frame))
		
		print('=== VideoApp.keyPress() pressed:', repr(event.char), 'frame:', frame)
		"""
		print('event.keysym:', event.keysym)
		print('event.keysym_num:', event.keysym_num)
		print('event.state:', event.state)
		"""
		
		theKey = event.char

		# pause/play
		if theKey == ' ':
			self.vs.playPause()
			
		# add event
		validEventKeys = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
		if theKey in validEventKeys:
			print('keyPress() adding event')
			self.addEvent(theKey, frame)
		
		# set note of selected event
		if theKey == 'n':
			self.setNote()
			
		# delete event
		if theKey == 'd':
			print('keyPress() d will delete -->> not implemented')

		# set event start frame
		if theKey == 'f':
			self.setStartFrame(frame)
		# set stop frame
		if theKey == 'l':
			self.setEndFrame(frame)
			
		# slower (increase frame interval)
		if theKey == '-':
			if self.myFrameInterval == 1:
				self.myFrameInterval = 0
			newFrameInterval = self.myFrameInterval + 10
			self.setFramesPerSecond(newFrameInterval)
		# faster, decrease frame interval
		if theKey == '+':
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
			
		# figuring out 'tab' between widgets
		# i am intercepting all keystrokes at app level, not widget level
		if theKey == '\t':
			focused_widget = self.root.focus_get()
			print('focused_widget.name:', focused_widget)
			
	def setStartFrame(self, frame):
		print('setStartFrame()')

		index, item = self._getTreeVidewSelection(self.right_tree, 'index')
		if index is None:
			print('   warning: please select an event')
			return None
		index = int(index)
		print('   modifying event index:', index)
		
		# set in our eventList
		self.eventList.eventList[index].dict['frameStart'] = frame
		self.eventList.save()
		
		# grab event we just set
		event = self.eventList.eventList[index]

		# update treeview with new event
		self.right_tree.item(item, values=event.asTuple())

	def setEndFrame(self, frame):
		print('setEndFrame()')

		index, item = self._getTreeVidewSelection(self.right_tree, 'index')
		if index is None:
			print('   warning: please select an event')
			return None
		index = int(index)
		print('   modifying event index:', index)
		
		# set in our eventList
		self.eventList.eventList[index].dict['frameStop'] = frame
		self.eventList.save()
		
		# grab event we just set
		event = self.eventList.eventList[index]

		# update treeview with new event
		self.right_tree.item(item, values=event.asTuple())		
		
	def setNote(self):
		# get selection from event list
		print('setNote()')
		item = self.right_tree.focus()
		print(self.right_tree.item(item))
		d = myNoteDialog(self)
		
	def addEvent(self, theKey, frame):
		frame = float(frame)
		frame = int(frame)

		newEvent = self.eventList.appendEvent(theKey, frame)
		self.eventList.save()
		
		# get a tuple (list) of item names
		children = self.right_tree.get_children()
		numInList = len(children)

		position = "end"
		numInList += 1
		text = str(numInList)
		print('newEvent.asTuple():', newEvent.asTuple())
		self.right_tree.insert("" , position, text=text, values=newEvent.asTuple())
		
	def populateEvents(self):
		# first delete entries
		for i in self.right_tree.get_children():
		    self.right_tree.delete(i)

		# todo: make bEventList iterable
		for idx, event in enumerate(self.eventList.eventList):
			position = "end"
			self.right_tree.insert("" , position, text=str(idx+1), values=event.asTuple())
			
	def populateVideoFiles(self):
		for idx, videoFile in enumerate(self.videoList.getList()):
			position = "end"
			self.left_tree.insert("" , position, text=str(idx+1), values=videoFile.asTuple())
	
	def videoLoop(self):
	
		# it is important to not vs.read() when paused
		if self.vs.paused:
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
			#print('ERROR: VideoApp2.videoLoop() got None self.frame')
			pass
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
