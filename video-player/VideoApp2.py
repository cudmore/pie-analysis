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
import bMenus
import bEventList
import bVideoList
from bNoteDialog import bNoteDialog

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
		
		self.vs = None
		self.frame = None # read from FileVideoStream
		self.scaledImage = None
		self.currentWidth = 640
		self.currentHeight = 480
 		
		self.myCurrentFrame = None
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

		# make window not resiazeable
		self.root.resizable(width=False, height=False)
		
		bMenus.bMenus(self.root)
		
		self.buildInterface()

		self.root.bind("<Key>", self.keyPress)

		self.videoLoop()

		# this will return but run in background using tkinter after()
		self.videoLoop()
		
		# set a callback to handle when the window is closed
		self.root.wm_title("PiE Video Analysis")
		self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)
		

	###################################################################################
	def populateVideoFiles(self, doInit=False):
		
		if doInit:
			videoFileColumns = self.videoList.getColumns()
			
			# configure columns
			self.videoFileTree['columns'] = videoFileColumns
			hideColumns = ['path'] # hide some columns
			displaycolumns = [] # build a list of columns not in hideColumns
			for column in videoFileColumns:
				self.videoFileTree.column(column, width=10)
				self.videoFileTree.heading(column, text=column, command=lambda c=column: self.treeview_sort_column(self.videoFileTree, c, False))
				if column not in hideColumns:
					displaycolumns.append(column)
			self.videoFileTree.column('index', width=5)
			
			# hide some columns
			self.videoFileTree["displaycolumns"] = displaycolumns
			
			self.videoFileTree.bind("<ButtonRelease-1>", self.video_tree_single_click)

		# first delete entries
		for i in self.videoFileTree.get_children():
		    self.videoFileTree.delete(i)

		for idx, videoFile in enumerate(self.videoList.getList()):
			position = "end"
			self.videoFileTree.insert("" , position, text=str(idx+1), values=videoFile.asTuple())

	
	###################################################################################
	def populateEvents(self, doInit=False):
		eventColumns = self.eventList.getColumns()
		
		if doInit:
			# configure columns
			self.eventTree['columns'] = eventColumns
			hideColumns = ['path', 'cseconds'] # hide some columns
			displaycolumns = [] # build a list of columns not in hideColumns
			for column in eventColumns:
				self.eventTree.column(column, width=20)
				self.eventTree.heading(column, text=column, command=lambda c=column: self.treeview_sort_column(self.eventTree, c, False))
				if column not in hideColumns:
					displaycolumns.append(column)
	
			# hide some columns
			self.eventTree["displaycolumns"] = displaycolumns

			self.eventTree.bind('<<TreeviewSelect>>', self.event_tree_single_selected)

		# first delete entries
		for i in self.eventTree.get_children():
		    self.eventTree.delete(i)

		# todo: make bEventList iterable
		for idx, event in enumerate(self.eventList.eventList):
			position = "end"
			self.eventTree.insert("" , position, text=str(idx+1), values=event.asTuple())

			
	###################################################################################
	def buildInterface(self):
		myPadding = 5
		myBorderWidth = 0

		self.root.grid_rowconfigure(0, weight=1)
		self.root.grid_columnconfigure(0, weight=1)

		#
		vPane = ttk.PanedWindow(self.root, orient="vertical")
		vPane.grid(row=0, column=0, sticky="nsew")

		upper_frame = ttk.Frame(vPane, borderwidth=myBorderWidth, relief="sunken")
		upper_frame.grid(row=0, column=0, sticky="nsew", padx=myPadding, pady=myPadding)
		upper_frame.grid_rowconfigure(0, weight=1)
		upper_frame.grid_columnconfigure(0, weight=1)
		vPane.add(upper_frame)

		#self.videoFileTree = ttk.Treeview(upper_frame, columns=gVideoFileColumns, show='headings')
		self.videoFileTree = ttk.Treeview(upper_frame, show='headings')
		self.videoFileTree.grid(row=0,column=0, sticky="nsew", padx=myPadding, pady=myPadding)
		videoFileTree_scrollbar = ttk.Scrollbar(upper_frame, orient="vertical", command = self.videoFileTree.yview)
		videoFileTree_scrollbar.grid(row=0, column=0, sticky='nse', padx=myPadding, pady=myPadding)
		self.videoFileTree.configure(yscrollcommand=videoFileTree_scrollbar.set)
		self.populateVideoFiles(doInit=True)


		#
		lower_frame = ttk.Frame(vPane, borderwidth=myBorderWidth, relief="sunken")
		#lower_frame.grid(row=0, column=0, sticky="nsew", padx=myPadding, pady=myPadding)
		lower_frame.grid_rowconfigure(0, weight=1)
		lower_frame.grid_columnconfigure(0, weight=1)
		vPane.add(lower_frame)

		#
		self.hPane = ttk.PanedWindow(lower_frame, orient="horizontal")
		# checking to see if panedWindow is causing crash -->> no it does not
		#self.hPane = ttk.Frame(lower_frame)
		self.hPane.grid(row=0, column=0, sticky="nsew")
		#hPane.bind("<Configure>", self.set_aspect2) # causing crash?
		self.hPane.grid_rowconfigure(0, weight=1)
		self.hPane.grid_columnconfigure(0, weight=0)
		self.hPane.grid_columnconfigure(1, weight=1)

		lower_left_frame = ttk.Frame(self.hPane, borderwidth=myBorderWidth, relief="sunken")
		lower_left_frame.grid(row=0, column=0, sticky="nsew", padx=myPadding, pady=myPadding)
		lower_left_frame.grid_rowconfigure(0, weight=1)
		lower_left_frame.grid_columnconfigure(0, weight=1)
		self.hPane.add(lower_left_frame)
		
		self.eventTree = ttk.Treeview(lower_left_frame, show='headings')
		self.eventTree.grid(row=0,column=0, sticky="nsew", padx=myPadding, pady=myPadding)
		eventTree_scrollbar = ttk.Scrollbar(lower_left_frame, orient="vertical", command = self.eventTree.yview)
		eventTree_scrollbar.grid(row=0, column=0, sticky='nse', padx=myPadding, pady=myPadding)
		self.eventTree.configure(yscrollcommand=eventTree_scrollbar.set)
		self.populateEvents(doInit=True)

		#
		self.lower_right_frame = ttk.Frame(self.hPane, borderwidth=myBorderWidth, relief="sunken")
		self.lower_right_frame.grid(row=0, column=1, sticky="nsew", padx=myPadding, pady=myPadding)
		self.lower_right_frame.grid_rowconfigure(0, weight=0)
		self.lower_right_frame.grid_rowconfigure(1, weight=0)
		###
		self.lower_right_frame.grid_rowconfigure(2, weight=1) # content_frame causing crash
		###
		self.lower_right_frame.grid_rowconfigure(3, weight=0)
		self.lower_right_frame.grid_columnconfigure(0, weight=1)
		self.hPane.add(self.lower_right_frame)

		# video
		myApectRatio = 4.0/3.0
	
		#
		# random chunks
		showRandomChunks = False # toggle this when we load random chunks file
		random_chunks_frame = ttk.Frame(self.lower_right_frame)
		random_chunks_frame.grid(row=0, column=0, sticky="new")
		# this removes and then re-adds a frame from the grid ... very useful
		if showRandomChunks:
			random_chunks_frame.grid()
		else:
			random_chunks_frame.grid_remove()

		random_chunks_label1 = ttk.Label(random_chunks_frame, text="random param 1")
		random_chunks_label1.grid(row=0, column=0, sticky="nw", padx=myPadding, pady=myPadding)

		random_chunks_label2 = ttk.Label(random_chunks_frame, text="random param 2")
		random_chunks_label2.grid(row=0, column=1, sticky="nw", padx=myPadding, pady=myPadding)
	
		#
		# video feedback
		video_feedback_frame = ttk.Frame(self.lower_right_frame)
		video_feedback_frame.grid(row=1, column=0, sticky="nw")

		self.currentFrameLabel = ttk.Label(video_feedback_frame, width=11, anchor="w", text='Frame:')
		self.currentFrameLabel.grid(row=0, column=0)
		
		self.numFrameLabel = ttk.Label(video_feedback_frame, width=8, anchor="w", text='of ' + str(self.vs.streamParams['numFrames']))
		self.numFrameLabel.grid(row=0, column=1)

		self.currentSecondsLabel = ttk.Label(video_feedback_frame, width=8, anchor="w", text='Sec:')
		self.currentSecondsLabel.grid(row=0, column=2, sticky="w")
		
		self.numSecondsLabel = ttk.Label(video_feedback_frame, width=8, anchor="w", text='of ' + str(self.vs.streamParams['numSeconds']))
		self.numSecondsLabel.grid(row=0, column=3, sticky="w")
		
		self.currentFrameIntervalLabel = ttk.Label(video_feedback_frame, width=20, anchor="w", text='Interval (ms):')
		self.currentFrameIntervalLabel.grid(row=0, column=4, sticky="w")

		#
		# video frame
		
		# tried extra frame, 
		#videoFrame2 = ttk.Frame(self.lower_right_frame, borderwidth=0, width=200, height=200)
		#videoFrame2.grid(row=2, column=0, sticky="nsew", padx=myPadding, pady=myPadding)
		#videoFrame2.grid_rowconfigure(0, weight=1)
		#videoFrame2.grid_columnconfigure(0, weight=1)

		self.pad_frame = ttk.Frame(self.lower_right_frame, borderwidth=0, width=200, height=200)
		#self.pad_frame = ttk.Frame(self.root, borderwidth=0, width=200, height=200)
		#self.pad_frame = ttk.Frame(videoFrame2, borderwidth=0, width=200, height=200)
		# when in lower_right_frame
		self.pad_frame.grid(row=2, column=0, sticky="nsew", padx=myPadding, pady=myPadding)
		# when in root
		#self.pad_frame.grid(row=0, column=0, sticky="nsew", padx=myPadding, pady=myPadding)
	
		contentBorderWidth = 1
		self.content_frame = ttk.Frame(self.lower_right_frame, borderwidth=contentBorderWidth) # PARENT IS ROOT
		self.content_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
		#self.content_frame.grid(row=2, column=0, padx=5, pady=5)
		self.content_frame.grid_rowconfigure(0, weight=1)
		self.content_frame.grid_columnconfigure(0, weight=1)
	
		# insert image into content frame
		tmpImage = np.zeros((480,640,3), np.uint8)
		tmpImage = Image.fromarray(tmpImage)
		tmpImage = ImageTk.PhotoImage(tmpImage)
		self.videoLabel = ttk.Label(self.content_frame, text="xxx", font=("Helvetica", 48), compound="center", foreground="green")
		self.videoLabel.grid(row=0, column=0, sticky="nsew")
		self.videoLabel.configure(image=tmpImage)
		self.videoLabel.image = tmpImage

		#
		# video controls
		self.video_control_frame = ttk.Frame(self.lower_right_frame, borderwidth=myBorderWidth,relief="groove")
		self.video_control_frame.grid(row=3, column=0, sticky="w", padx=myPadding, pady=myPadding)
		self.video_control_frame.grid_columnconfigure(5, weight=1) # to expand video_frame_slider

		video_fr_button = ttk.Button(self.video_control_frame, width=1, text="<<", command=lambda: self.doCommand('fast-backward'))
		video_fr_button.grid(row=0, column=0)
		#video_fr_button.bind("<Key>", self.keyPress)

		video_r_button = ttk.Button(self.video_control_frame, width=1, text="<", command=lambda: self.doCommand('backward'))
		video_r_button.grid(row=0, column=1)
		#video_r_button.bind("<Key>", self.keyPress)

		video_play_button = ttk.Button(self.video_control_frame, width=3, text="Play", command=lambda: self.doCommand('playpause'))
		video_play_button.grid(row=0, column=2)
		#video_play_button.bind("<Key>", self.keyPress)
	
		video_f_button = ttk.Button(self.video_control_frame, width=1, text=">", command=lambda: self.doCommand('forward'))
		video_f_button.grid(row=0, column=3)
		#video_f_button.bind("<Key>", self.keyPress)
	
		video_ff_button = ttk.Button(self.video_control_frame, width=1, text=">>", command=lambda: self.doCommand('fast-forward'))
		video_ff_button.grid(row=0, column=4)
		#video_ff_button.bind("<Key>", self.keyPress)
	
		self.video_frame_slider = ttk.Scale(self.video_control_frame, from_=0, to=self.vs.streamParams['numFrames'], orient="horizontal", command=self.frameSlider_callback)
		self.video_frame_slider.grid(row=0, column=5, sticky="ew")

		#
		# set aspect of video frame
		#self.set_aspect(self.lower_right_frame, self.content_frame, self.pad_frame, self.video_control_frame, aspect_ratio=myApectRatio) 
		self.set_aspect(self.hPane, self.lower_right_frame, self.content_frame, self.pad_frame, self.video_control_frame, self.videoLabel, aspect_ratio=myApectRatio) 
			
		#
		# configure panel
		"""
		vPane.add(upper_frame)
		vPane.add(lower_frame)

		self.hPane.add(lower_left_frame)
		self.hPane.add(self.lower_right_frame)
		"""
		
		# do this at end to get window panels to size correctly
		self.root.geometry("1285x815")

		self.root.update()
		vPane.sashpos(0, 100)
		self.hPane.sashpos(0, 400)

	def switchvideo(self, videoPath, paused=False, gotoFrame=None):
		if self.vs is not None:
			self.vs.stop()
		
		self.vs = FileVideoStream(videoPath, paused, gotoFrame) #.start()
		self.vs.start()
		
		self.setFrame(0)

		# set the selection in video tree
		# select the first video
		#child_id = self.videoFileTree.get_children()[-1] #last
		#child_id = self.videoFileTree.get_children()[0] #first
		
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
		           
	"""
	def set_aspect2(self, event):
		print('set_aspect2')
	"""
	
    # see: https://stackoverflow.com/questions/16523128/resizing-tkinter-frames-with-fixed-aspect-ratio
	#def set_aspect(self, lower_right_frame, content_frame, pad_frame, video_control_frame, aspect_ratio):
	def set_aspect(self, hPane, lower_right_frame, content_frame, pad_frame, video_control_frame, videoLabel, aspect_ratio):
		# a function which places a frame within a containing frame, and
		# then forces the inner frame to keep a specific aspect ratio

		def enforce_aspect_ratio(event):
			# when the pad window resizes, fit the content into it,
			# either by fixing the width or the height and then
			# adjusting the height or width based on the aspect ratio.

			print('0')
			print('enforce_aspect_ratio() event:', event)
			try:
				buttonHeight = 36

				#event.width = lower_right_frame.winfo_width()
				#event.height = lower_right_frame.winfo_height()
				
				# start by using the width as the controlling dimension
				desired_width = event.width - buttonHeight
				desired_height = int(desired_width / aspect_ratio)

				# if the window is too tall to fit, use the height as
				# the controlling dimension
				if desired_height > event.height:
					desired_height = event.height - buttonHeight
					desired_width = int(desired_height * aspect_ratio)

				self.currentWidth = desired_width
				self.currentHeight = desired_height
			
				# place the window, giving it an explicit size
				print('   1')
				#content_frame.place(in_=pad_frame, x=0, y=0, width=desired_width, height=desired_height)
				if 1:
					#content_frame.place(in_=pad_frame, x=0, y=0, width=desired_width, height=desired_height)
					#content_frame.place(in_=lower_right_frame, x=0, y=0, width=desired_width, height=desired_height)
					# laast attempt
					videoLabel.place(in_=content_frame, x=0, y=0, width=desired_width, height=desired_height)
					
				# place the video controls just below the video frame
				print('   2')
				#video_control_frame.place(in_=lower_right_frame, x=0, y=desired_height + buttonHeight, width=desired_width)
				if 1:
					#video_control_frame.place(in_=pad_frame, x=0, y=desired_height + buttonHeight, width=desired_width)
					#video_control_frame.place(in_=lower_right_frame, x=0, y=desired_height + buttonHeight, width=desired_width)
					video_control_frame.place(x=0, y=desired_height + buttonHeight, width=desired_width)
			
				print('   3')
				#print('winfo_geometry:', self.root.winfo_geometry())
			except:
				print('bingo: exception in enforce_aspect_ratio()')
			print('   4')
		#content_frame.bind("<Configure>", enforce_aspect_ratio)
		pad_frame.bind("<Configure>", enforce_aspect_ratio)
		#lower_right_frame.bind("<Configure>", enforce_aspect_ratio)
		#hPane.bind("<Configure>", enforce_aspect_ratio)
		#self.root.bind("<Configure>", enforce_aspect_ratio)

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
		path, item = self._getTreeVidewSelection(self.videoFileTree, 'path')
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
		self.video_frame_slider['to'] = self.vs.streamParams['numFrames']
		
	def event_tree_single_selected(self, event):
		print('=== event_tree_single_selected()')
		self.event_tree_single_click(event)
		
	def event_tree_single_click(self, event):
		"""
		On single click in event list tree --> Set the video to a frame
		event: <ButtonRelease event state=Button1 num=1 x=227 y=64>
		"""
		print('=== event_tree_single_click()')
		frameStart, item = self._getTreeVidewSelection(self.eventTree, 'frameStart')
		frameStart = float(frameStart) # need first because frameNumber (str) can be 100.00000000001
		frameStart = int(frameStart)
		print('   event_tree_single_click() is progressing to frameStart:', frameStart)
		#self.vs.setFrame(frameStart) # set the video frame
		self.setFrame(frameStart) # set the video frame
		
	def frameSlider_callback(self, frameNumber):
		frameNumber = int(float(frameNumber))
		print('VideoApp.frameSlider_callback()', frameNumber)
		self.setFrame(frameNumber)

	def doCommand(self, cmd):
		smallFrameStep = 10
		largeFrameStep = 100

		if cmd == 'playpause':
			self.vs.playPause()
				
		if cmd == 'forward':
			 newFrame = self.myCurrentFrame + smallFrameStep
			 self.setFrame(newFrame)
		if cmd == 'fast-forward':
			 newFrame = self.myCurrentFrame + largeFrameStep
			 self.setFrame(newFrame)
		if cmd == 'backward':
			 newFrame = self.myCurrentFrame - smallFrameStep
			 self.setFrame(newFrame)
		if cmd == 'fast-backward':
			 newFrame = self.myCurrentFrame - largeFrameStep
			 self.setFrame(newFrame)
			 
	def keyPress(self, event):
		print('=== VideoApp.keyPress() pressed:', repr(event.char), 'self.myCurrentFrame:', self.myCurrentFrame)
		"""
		print('event.keysym:', event.keysym)
		print('event.keysym_num:', event.keysym_num)
		print('event.state:', event.state)
		"""
		
		theKey = event.char

		# pause/play
		if theKey == ' ':
			#self.vs.playPause()
			self.doCommand('playpause')
			
		# add event
		validEventKeys = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
		if theKey in validEventKeys:
			print('keyPress() adding event')
			self.addEvent(theKey, self.myCurrentFrame)
		
		# set note of selected event
		if theKey == 'n':
			self.setNote()
			
		# delete event
		if theKey == 'd':
			print('keyPress() d will delete -->> not implemented')

		# set event start frame
		if theKey == 'f':
			self.setStartFrame(self.myCurrentFrame)
		# set stop frame
		if theKey == 'l':
			self.setEndFrame(self.myCurrentFrame)
			
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
			self.doCommand('fast-backward')
		elif theKey == '\uf702':
			# left
			self.doCommand('backward')
		if theKey == '\uf703' and event.state==97:
			# shift + right
			self.doCommand('fast-forward')
		elif theKey == '\uf703':
			# right
			self.doCommand('forward')
			
		# figuring out 'tab' between widgets
		# i am intercepting all keystrokes at app level, not widget level
		if theKey == '\t':
			focused_widget = self.root.focus_get()
			print('focused_widget.name:', focused_widget)
			
	def setFrame(self, theFrame):
		self.myCurrentFrame = theFrame
		self.vs.setFrame(self.myCurrentFrame)
		
	def setStartFrame(self, frame):
		print('setStartFrame()')

		index, item = self._getTreeVidewSelection(self.eventTree, 'index')
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
		self.eventTree.item(item, values=event.asTuple())

	def setEndFrame(self, frame):
		print('setEndFrame()')

		index, item = self._getTreeVidewSelection(self.eventTree, 'index')
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
		self.eventTree.item(item, values=event.asTuple())		
		
	def setNote(self):
		"""
		Open modal dialog to set note of selected event
		"""
		print('setNote()')
		# get selection from event list
		d = bNoteDialog(self)
		
	def addEvent(self, theKey, frame):
		"""
		Append a new event at the current frame
		"""
		frame = float(frame)
		frame = int(frame)

		newEvent = self.eventList.appendEvent(theKey, frame)
		self.eventList.save()
		
		# get a tuple (list) of item names
		children = self.eventTree.get_children()
		numInList = len(children)

		position = "end"
		numInList += 1
		text = str(numInList)
		#print('newEvent.asTuple():', newEvent.asTuple())
		self.eventTree.insert("" , position, text=text, values=newEvent.asTuple())
		
	def setFramesPerSecond(self, frameInterval):
		# make sure I cancel using the same widget at end of videoloop()
		"""
		self.videoLabel.after_cancel(self.videoLoopID)
		self.myFrameInterval = frameInterval
		print('setFramesPerSecond() self.myFrameInterval:', self.myFrameInterval)
		self.videoLoop()
		"""
		
	def videoLoop(self):
	
		if self.vs.paused:
			self.videoLabel.configure(text="Paused")
			if (self.pausedAtFrame != self.myCurrentFrame):
				#print('VideoApp2.videoLoop() fetching new frame when paused', 'self.pausedAtFrame:', self.pausedAtFrame, 'self.myCurrentFrame:', self.myCurrentFrame)
				try:
					#print('VideoApp2.videoLoop() CALLING self.vs.read()')
					[self.frame, self.myCurrentFrame] = self.vs.read()
				except:
					print('zzz qqq')
				self.pausedAtFrame = self.myCurrentFrame
		else:
			self.videoLabel.configure(text="")
			[self.frame, self.myCurrentFrame] = self.vs.read()

		if self.frame is None:
			#print('ERROR: VideoApp2.videoLoop() got None self.frame')
			pass
		else:
			## resize
			#tmpWidth = self.content_frame.winfo_width()
			#tmpHeight = self.content_frame.winfo_height()
			tmpWidth = self.currentWidth
			tmpHeight = self.currentHeight
			#print('   tmpWidth:', tmpWidth, 'tmpHeight:', tmpHeight)
			tmpImage = None
			try:
				#tmpImage = self.frame
				tmpImage = cv2.resize(self.frame, (tmpWidth, tmpHeight))
			except:
				#print('exception: in videoLoop() ... cv2.resize()')
				pass
				
			if tmpImage is not None:
				tmpImage = cv2.cvtColor(tmpImage, cv2.COLOR_BGR2RGB)
				tmpImage = Image.fromarray(tmpImage)
			
				#tmpImage = tmpImage.resize((tmpWidth, tmpHeight), Image.ANTIALIAS)
				
				tmpImage = ImageTk.PhotoImage(tmpImage)
	
				try:
					self.videoLabel.configure(image=tmpImage)
					self.videoLabel.image = tmpImage
				except:
					print('exception: videoLoop() configure self.videoLabel')
			#
			# update feedback labels
			if 1:
				self.currentFrameLabel['text'] = 'Frame:' + str(self.myCurrentFrame)
				self.currentFrameIntervalLabel['text'] ='Interval (ms):' + str(self.myFrameInterval)
				self.currentSecondsLabel['text'] = 'Sec:' + str(round(self.myCurrentFrame / self.vs.streamParams['fps'],2))
				self.video_frame_slider['value'] = self.myCurrentFrame

		# leave this here -- CRITICAL
		#self.videoLoopID = self.videoLabel.after(self.myFrameInterval, self.videoLoop)
		#self.videoLoopID = self.content_frame.after(self.myFrameInterval, self.videoLoop)
		self.videoLoopID = self.root.after(self.myFrameInterval, self.videoLoop)
		
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
