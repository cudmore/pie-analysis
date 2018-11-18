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

##################################################################################
class myNoteDialog:
	"""Opens a modal dialog to set the note of an event"""
	def __init__(self, parentApp):
		self.parentApp = parentApp
		
		# to make modal
		#self.grab_set()
		# see: http://effbot.org/tkinterbook/tkinter-dialog-windows.htm
		
		top = self.top = tkinter.Toplevel(parentApp.root)
		
		#top.focus_force() # added
		#top.grab_set()
		
		tkinter.Label(top, text="Note").pack()

		#
		# grab the note of selected event
		self.item = self.parentApp.eventTree.focus()
		if self.item == '':
			return 0
		columns = self.parentApp.eventTree['columns']				
		noteColIdx = columns.index('note') # assuming 'frameStart' exists
		values = self.parentApp.eventTree.item(self.item, "values")
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
		#item = self.eventTree.focus()
		self.parentApp.eventTree.item(self.item, values=event.asTuple())

		self.top.destroy()
	def _setNote(txt):
		item = self.parentApp.eventTree.focus()

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
		self.frame = None
 
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

		#
		hPane = ttk.PanedWindow(lower_frame, orient="horizontal")
		hPane.grid(row=0, column=0, sticky="nsew")

		lower_left_frame = ttk.Frame(hPane, borderwidth=myBorderWidth, relief="sunken")
		lower_left_frame.grid(row=0, column=0, sticky="nsew", padx=myPadding, pady=myPadding)
		lower_left_frame.grid_rowconfigure(0, weight=1)
		lower_left_frame.grid_columnconfigure(0, weight=1)

		self.eventTree = ttk.Treeview(lower_left_frame, show='headings')
		self.eventTree.grid(row=0,column=0, sticky="nsew", padx=myPadding, pady=myPadding)
		eventTree_scrollbar = ttk.Scrollbar(lower_left_frame, orient="vertical", command = self.eventTree.yview)
		eventTree_scrollbar.grid(row=0, column=0, sticky='nse', padx=myPadding, pady=myPadding)
		self.eventTree.configure(yscrollcommand=eventTree_scrollbar.set)
		self.populateEvents(doInit=True)

		#
		lower_right_frame = ttk.Frame(hPane, borderwidth=myBorderWidth, relief="sunken")
		lower_right_frame.grid(row=0, column=0, sticky="nsew", padx=myPadding, pady=myPadding)
		lower_right_frame.grid_rowconfigure(0, weight=0)
		lower_right_frame.grid_rowconfigure(1, weight=0)
		lower_right_frame.grid_rowconfigure(2, weight=1)
		lower_right_frame.grid_rowconfigure(3, weight=0)
		lower_right_frame.grid_columnconfigure(0, weight=1)
		#lower_right_frame.grid_columnconfigure(1, weight=0)


		# video
		myApectRatio = 4.0/3.0
	
		#
		# random chunks
		showRandomChunks = False # toggle this when we load random chunks file
		random_chunks_frame = ttk.Frame(lower_right_frame)
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
		video_feedback_frame = ttk.Frame(lower_right_frame)
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
		pad_frame = ttk.Frame(lower_right_frame, borderwidth=0, width=200, height=200)
		pad_frame.grid(row=2, column=0, sticky="nsew", padx=myPadding, pady=myPadding)
	
		contentBorderWidth = 1
		self.content_frame = ttk.Frame(lower_right_frame, borderwidth=contentBorderWidth, relief="groove")
		self.content_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
		#self.content_frame.grid_rowconfigure(0, weight=1)
		#self.content_frame.grid_columnconfigure(0, weight=1)
	
		# insert image into content frame
		image = np.zeros((480,640,3), np.uint8)
		image = Image.fromarray(image)
		image = ImageTk.PhotoImage(image)
		self.videoLabel = ttk.Label(self.content_frame, image=image, text="xxx", font=("Helvetica", 48), compound="center", foreground="green")
		self.videoLabel.grid(row=0, column=0, sticky="nsew")
		self.videoLabel.image = image

		#
		# video controls
		video_control_frame = ttk.Frame(lower_right_frame, borderwidth=myBorderWidth,relief="groove")
		video_control_frame.grid(row=3, column=0, sticky="w", padx=myPadding, pady=myPadding)
		video_control_frame.grid_columnconfigure(5, weight=1) # to expand video_frame_slider
	
		video_fr_button = ttk.Button(video_control_frame, width=1, text="<<")
		video_fr_button.grid(row=0, column=0)

		video_r_button = ttk.Button(video_control_frame, width=1, text="<")
		video_r_button.grid(row=0, column=1)

		video_play_button = ttk.Button(video_control_frame, width=3, text="Play")
		video_play_button.grid(row=0, column=2)
	
		video_f_button = ttk.Button(video_control_frame, width=1, text=">")
		video_f_button.grid(row=0, column=3)
	
		video_ff_button = ttk.Button(video_control_frame, width=1, text=">>")
		video_ff_button.grid(row=0, column=4)
	
		self.video_frame_slider = ttk.Scale(video_control_frame, from_=0, to=self.vs.streamParams['numFrames'], orient="horizontal", command=self.frameSlider_callback)
		self.video_frame_slider.grid(row=0, column=5, sticky="ew")

		#
		# set aspect of video frame
		self.set_aspect(self.content_frame, pad_frame, video_control_frame, aspect_ratio=myApectRatio) 
			
		#
		# configure panel
		vPane.add(upper_frame)
		vPane.add(lower_frame)

		hPane.add(lower_left_frame)
		hPane.add(lower_right_frame)

		# do this at end to get window panels to size correctly
		self.root.geometry("1285x815")

		self.root.update()
		vPane.sashpos(0, 100)
		hPane.sashpos(0, 400)

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
	def set_aspect(self, content_frame, pad_frame, video_control_frame, aspect_ratio):
		# a function which places a frame within a containing frame, and
		# then forces the inner frame to keep a specific aspect ratio

		def enforce_aspect_ratio(event):
			# when the pad window resizes, fit the content into it,
			# either by fixing the width or the height and then
			# adjusting the height or width based on the aspect ratio.

			buttonHeight = 36

			# start by using the width as the controlling dimension
			desired_width = event.width - buttonHeight
			desired_height = int(desired_width / aspect_ratio)

			# if the window is too tall to fit, use the height as
			# the controlling dimension
			if desired_height > event.height:
				desired_height = event.height - buttonHeight
				desired_width = int(desired_height * aspect_ratio)

			# place the window, giving it an explicit size
			content_frame.place(in_=pad_frame, x=0, y=0, 
				width=desired_width, height=desired_height)

			# place the video controls just below the video frame
			video_control_frame.place(x=0, y=desired_height + buttonHeight, width=desired_width)

			#print('h:', self.root.winfo_height())
			#print('w:', self.root.winfo_width())
			#print('winfo_geometry:', self.root.winfo_geometry())

		pad_frame.bind("<Configure>", enforce_aspect_ratio)

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
		self.vs.setFrame(frameStart) # set the video frame
		
	# slider
	"""
	def myUpdate(self):
		self.frameSlider_update = False
		# set() triggers frameSlider_callback() in background! frameSlider_callback() needs to set self.frameSlider_update = True
		
		# put back in
		self.video_frame_slider.set(self.vs.currentFrame)
		
		# this does not work as self.frameSlider.set calls frameSlider_callback() in background (different thread?)
		#self.frameSlider_update = True
		
		self.root.after(20, self.myUpdate)
	"""
		
	def frameSlider_callback(self, frameNumber):
		"""
		frameNumber : str
		"""
		
		print('VideoApp.frameSlider_callback()', frameNumber)
		self.vs.setFrame(frameNumber)
		
		"""
		#print('gotoFrame()', frameNumber)
		frameNumber = int(float(frameNumber))
		if self.frameSlider_update:
			self.vs.setFrame(frameNumber)
		else:
			self.frameSlider_update = True
		"""
	# key
	def keyPress(self, event):
		"""
		frame = self.vs.stream.get(cv2.CAP_PROP_POS_FRAMES)
		frame = int(float(frame))
		"""
		
		print('=== VideoApp.keyPress() pressed:', repr(event.char), 'self.myCurrentFrame:', self.myCurrentFrame)
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
			newFrame = self.myCurrentFrame - 100
			#self.vs.setFrame(self.myCurrentFrame)
			self.setFrame(newFrame)
		elif theKey == '\uf702':
			# left
			newFrame = self.myCurrentFrame - 10
			#self.vs.setFrame(newFrame)
			self.setFrame(newFrame)
		if theKey == '\uf703' and event.state==97:
			# shift + right
			newFrame = self.myCurrentFrame + 100
			#self.vs.setFrame(newFrame)
			self.setFrame(newFrame)
		elif theKey == '\uf703':
			# right
			newFrame = self.myCurrentFrame + 10
			#self.vs.setFrame(newFrame)
			self.setFrame(newFrame)
			
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
		# get selection from event list
		print('setNote()')
		item = self.eventTree.focus()
		print(self.eventTree.item(item))
		d = myNoteDialog(self)
		
	def addEvent(self, theKey, frame):
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
		print('newEvent.asTuple():', newEvent.asTuple())
		self.eventTree.insert("" , position, text=text, values=newEvent.asTuple())
		
	def videoLoop(self):
	
		# it is important to not vs.read() when paused
		if self.vs.paused:
			self.videoLabel.configure(text="Paused")
			if (self.pausedAtFrame != self.myCurrentFrame):
				print('VideoApp2.videoLoop() fetching new frame when paused', 'self.pausedAtFrame:', self.pausedAtFrame, 'self.myCurrentFrame:', self.myCurrentFrame)
				try:
					#print('VideoApp2.videoLoop() CALLING self.vs.read()')
					[self.frame, self.myCurrentFrame] = self.vs.read()
				except:
					print('zzz qqq')
				#print('VideoApp2.videoLoop() got new frame')
				self.pausedAtFrame = self.myCurrentFrame
				#
				#self.vs.setFrame(self.vs.currentFrame)
		else:
			self.videoLabel.configure(text="")
			[self.frame, self.myCurrentFrame] = self.vs.read()

		if self.frame is None:
			#print('ERROR: VideoApp2.videoLoop() got None self.frame')
			pass
		else:
			## resize
			tmpWidth = self.content_frame.winfo_width()
			tmpHeight = self.content_frame.winfo_height()
			#print('tmpWidth:', tmpWidth, 'tmpHeight:', tmpHeight)
			try:
				image = self.frame
				#image = cv2.resize(image, (tmpWidth, tmpHeight))
			except:
				print('my exception: cv2.resize()')
				
			image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
			image = Image.fromarray(image)
		
			image = ImageTk.PhotoImage(image)

			self.videoLabel.configure(image=image)
			self.videoLabel.image = image

			#
			# update feedback labels
			self.currentFrameLabel.configure(text='Frame:' + str(self.myCurrentFrame))
			self.currentFrameIntervalLabel.configure(text='Interval (ms):' + str(self.myFrameInterval))
			# todo: fix this, keep track of current seconds from current frame and fps
			#self.currentSecondsLabel.configure(text='Sec:' + str(self.vs.seconds))
			self.video_frame_slider['value'] = self.myCurrentFrame

		# leave this here -- CRITICAL
		self.videoLoopID = self.videoLabel.after(self.myFrameInterval, self.videoLoop)
		
	def setFramesPerSecond(self, frameInterval):
		self.videoLabel.after_cancel(self.videoLoopID)
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
