# Author: Robert Cudmore
# Date: 20181101

"""
Create a video editing interface using tkinter
"""

import os, time
import threading
import json
from collections import OrderedDict 

import numpy as np

from PIL import Image
from PIL import ImageTk
from PIL import ImageFont
from PIL import ImageDraw

import cv2

import tkinter
from tkinter import ttk
from tkinter import filedialog

from FileVideoStream import FileVideoStream
import bMenus
import bEventList
import bVideoList
import bNoteDialog
import bChunkView

##################################################################################
class VideoApp:
	def loadFolder(self, path=''):
		if len(path) < 1:
			path = tkinter.filedialog.askdirectory()
		
		self.videoList = bVideoList.bVideoList(path)		
		self.populateVideoFiles(doInit=False)
	
		# initialize with first video in path
		firstVideoPath = self.videoList.videoFileList[0].dict['path']

		self.eventList = bEventList.bEventList(firstVideoPath)
		self.populateEvents(doInit=False)
		
		# fire up a video stream
		self.switchvideo(firstVideoPath, paused=True, gotoFrame=0)
	
	def __init__(self, path):
		"""
		TKInter application to create interface for loading, viewing, and annotating video
		
		path: path to folder with video files
		"""
		
		self.vs = None # FileVideoStream
		self.frame = None # the current frame, read from FileVideoStream
		#self.scaledImage = None
		#self.currentWidth = 640
		#self.currentHeight = 480
 		
		self.myCurrentFrame = None
		self.pausedAtFrame = None

		self.videoList = bVideoList.bVideoList(path)		

		# initialize with first video in path
		firstVideoPath = ''
		if len(self.videoList.videoFileList) > 0:
			firstVideoPath = self.videoList.videoFileList[0].dict['path']

		self.eventList = bEventList.bEventList(firstVideoPath)
		
		self.myFrameInterval = 30 # ms per frame
		self.myFramesPerSecond = round(1 / self.myFrameInterval,3) * 1000
		
		self.configDict = OrderedDict()
		self.configDict['showRandomChunks'] = True
		self.configDict['showVideoFiles'] = True
		self.configDict['showEvents'] = True
		self.configDict['videoFileSash'] = 200 # pixels
		self.configDict['eventSash'] = 400 # pixels
		self.configDict['smallSecondsStep'] = 1 # seconds
		self.configDict['largeSecondsStep'] = 10 # seconds
		self.configDict['lastPath'] = path
		
		###
		# tkinter interface
		###
		self.root = tkinter.Tk()
		self.root.title('PiE Video Analysis')
		
		# make window not resiazeable
		#self.root.resizable(width=False, height=False)
				
		# remove the default behavior of invoking the button with the space key
		self.root.unbind_class("Button", "<Key-space>")

		self.root.bind("<Key>", self.keyPress)

		self.buildInterface()

		self.chunkView.chunkInterface_populate()
		
		bMenus.bMenus(self)

		# fire up a video stream
		# removed when adding loadFOlder
		if len(firstVideoPath) > 0:
			self.switchvideo(firstVideoPath, paused=True, gotoFrame=0)

		# this will return but run in background using tkinter after()
		self.videoLoop()
		
		# set a callback to handle when the window is closed
		self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)
		
		self.root.mainloop()
		
	###################################################################################
	def toggleInterface(self, this):
		"""
		toggle window panel/frames on and off, including
			videofiles
			events
			chunks
		"""
		if this == 'videofiles':
			self.configDict['showVideoFiles'] = not self.configDict['showVideoFiles']
			if self.configDict['showVideoFiles']:
				self.vPane.sashpos(0, self.configDict['videoFileSash'])
			else:
				self.vPane.sashpos(0, 0)
		if this == 'events':
			self.configDict['showEvents'] = not self.configDict['showEvents']
			if self.configDict['showEvents']:
				self.hPane.sashpos(0, self.configDict['eventSash'])
			else:
				self.hPane.sashpos(0, 0)
		if this == 'randomchunks':
			self.configDict['showRandomChunks'] = not self.configDict['showRandomChunks']
			if self.configDict['showRandomChunks']:
				self.random_chunks_frame.grid()
			else:
				self.random_chunks_frame.grid_remove()
						
	###################################################################################
	def buildInterface(self):
		myPadding = 5
		myBorderWidth = 0

		self.lastResizeWidth = None
		self.lastResizeHeight = None
		
		self.root.grid_rowconfigure(0, weight=1)
		self.root.grid_columnconfigure(0, weight=1)

		#
		self.vPane = ttk.PanedWindow(self.root, orient="vertical")
		self.vPane.grid(row=0, column=0, sticky="nsew")

		upper_frame = ttk.Frame(self.vPane, borderwidth=myBorderWidth, relief="sunken")
		upper_frame.grid(row=0, column=0, sticky="nsew", padx=myPadding, pady=myPadding)
		upper_frame.grid_rowconfigure(0, weight=1)
		upper_frame.grid_columnconfigure(0, weight=1)
		self.vPane.add(upper_frame)

		#self.videoFileTree = ttk.Treeview(upper_frame, columns=gVideoFileColumns, show='headings')
		self.videoFileTree = ttk.Treeview(upper_frame, show='headings')
		self.videoFileTree.grid(row=0,column=0, sticky="nsew", padx=myPadding, pady=myPadding)
		videoFileTree_scrollbar = ttk.Scrollbar(upper_frame, orient="vertical", command = self.videoFileTree.yview)
		videoFileTree_scrollbar.grid(row=0, column=0, sticky='nse', padx=myPadding, pady=myPadding)
		self.videoFileTree.configure(yscrollcommand=videoFileTree_scrollbar.set)
		self.populateVideoFiles(doInit=True)


		#
		lower_frame = ttk.Frame(self.vPane, borderwidth=myBorderWidth, relief="sunken")
		#lower_frame.grid(row=0, column=0, sticky="nsew", padx=myPadding, pady=myPadding)
		lower_frame.grid_rowconfigure(0, weight=1)
		lower_frame.grid_columnconfigure(0, weight=1)
		self.vPane.add(lower_frame)

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
		# video
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

		#
		# random chunks
		self.random_chunks_frame = ttk.Frame(self.lower_right_frame)
		self.random_chunks_frame.grid(row=0, column=0, sticky="new")
		# this removes and then re-adds a frame from the grid ... very useful
		if self.configDict['showRandomChunks']:
			self.random_chunks_frame.grid()
		else:
			self.random_chunks_frame.grid_remove()
		self.chunkView = bChunkView.bChunkView(self, self.random_chunks_frame)
		
		#
		# video feedback
		video_feedback_frame = ttk.Frame(self.lower_right_frame)
		video_feedback_frame.grid(row=1, column=0, sticky="nw")

		self.currentFrameLabel = ttk.Label(video_feedback_frame, width=11, anchor="w", text='Frame:')
		self.currentFrameLabel.grid(row=0, column=0)
		
		self.numFrameLabel = ttk.Label(video_feedback_frame, width=8, anchor="w", text='of ')
		self.numFrameLabel.grid(row=0, column=1)

		self.currentSecondsLabel = ttk.Label(video_feedback_frame, width=8, anchor="w", text='Sec:')
		self.currentSecondsLabel.grid(row=0, column=2, sticky="w")
		
		self.numSecondsLabel = ttk.Label(video_feedback_frame, width=8, anchor="w", text='of ')
		self.numSecondsLabel.grid(row=0, column=3, sticky="w")
		
		self.currentFrameIntervalLabel = ttk.Label(video_feedback_frame, width=20, anchor="w", text='Frame Interval (ms):')
		self.currentFrameIntervalLabel.grid(row=0, column=4, sticky="w")

		self.currentFramePerScondLabel = ttk.Label(video_feedback_frame, width=20, anchor="w", text='fps:')
		self.currentFramePerScondLabel.grid(row=0, column=5, sticky="w")

		#
		# video frame
		
		# tried extra frame, 
		#videoFrame2 = ttk.Frame(self.lower_right_frame, borderwidth=0, width=200, height=200)
		#videoFrame2.grid(row=2, column=0, sticky="nsew", padx=myPadding, pady=myPadding)
		#videoFrame2.grid_rowconfigure(0, weight=1)
		#videoFrame2.grid_columnconfigure(0, weight=1)

		#self.pad_frame = ttk.Frame(self.lower_right_frame, borderwidth=0, width=200, height=200)
		#self.pad_frame = ttk.Frame(self.root, borderwidth=0, width=200, height=200)
		#self.pad_frame = ttk.Frame(videoFrame2, borderwidth=0, width=200, height=200)
		# when in lower_right_frame
		#self.pad_frame.grid(row=2, column=0, sticky="nsew", padx=myPadding, pady=myPadding)
		# when in root
		#self.pad_frame.grid(row=0, column=0, sticky="nsew", padx=myPadding, pady=myPadding)
	
		contentBorderWidth = 1
		self.content_frame = ttk.Frame(self.lower_right_frame, borderwidth=contentBorderWidth) # PARENT IS ROOT
		self.content_frame.grid(row=2, column=0, sticky="nsew") #, padx=5, pady=5)
		#self.content_frame.grid(row=2, column=0, padx=5, pady=5)
		self.content_frame.grid_rowconfigure(0, weight=1)
		self.content_frame.grid_columnconfigure(0, weight=1)
	
		# insert image into content frame
		tmpImage = np.zeros((480,640,3), np.uint8)
		tmpImage = Image.fromarray(tmpImage)
		tmpImage = ImageTk.PhotoImage(tmpImage)
		self.videoLabel = ttk.Label(self.content_frame, text="xxx", font=("Helvetica", 48), compound="center", foreground="green")
		#self.videoLabel.grid(row=0, column=0, sticky="nsew")
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
	
		self.video_frame_slider = ttk.Scale(self.video_control_frame, from_=0, to=0, orient="horizontal", command=self.frameSlider_callback)
		self.video_frame_slider.grid(row=0, column=5, sticky="ew")

		#
		# set aspect of video frame
		#self.set_aspect(self.lower_right_frame, self.content_frame, self.pad_frame, self.video_control_frame, aspect_ratio=myApectRatio) 
		#self.set_aspect(self.hPane, self.lower_right_frame, self.content_frame, self.pad_frame, self.video_control_frame, self.videoLabel) #, aspect_ratio=myApectRatio) 
				
		#
		# configure panel

		# do this at end to get window panels to size correctly
		#self.root.geometry("1285x815") # home
		self.root.geometry("1100x700") # home2
		#self.root.geometry("1810x1198") # work

		self.root.update()
		self.vPane.sashpos(0, self.configDict['videoFileSash'])
		self.hPane.sashpos(0, self.configDict['eventSash'])

		#self.videoLabel.bind("<Configure>", self.mySetAspect)
		#self.mySetAspect()
		
	###################################################################################
		
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
			
			# set some column widths, width is in pixels?
			#gVideoFileColumns = ('index', 'path', 'file', 'width', 'height', 'frames', 'fps', 'seconds', 'numevents', 'note')
			defaultWidth = 80
			self.videoFileTree.column('index', minwidth=50, width=50, stretch="no")
			self.videoFileTree.column('file', width=150)
			self.videoFileTree.column('width', minwidth=defaultWidth, width=defaultWidth, stretch="no")
			self.videoFileTree.column('height', minwidth=defaultWidth, width=defaultWidth, stretch="no")
			self.videoFileTree.column('frames', minwidth=defaultWidth, width=defaultWidth, stretch="no")
			self.videoFileTree.column('fps', minwidth=defaultWidth, width=defaultWidth, stretch="no")
			self.videoFileTree.column('seconds', minwidth=defaultWidth, width=defaultWidth, stretch="no")
			self.videoFileTree.column('numevents', minwidth=defaultWidth, width=defaultWidth, stretch="no")
			
			# hide some columns
			self.videoFileTree["displaycolumns"] = displaycolumns
			
			self.videoFileTree.bind("<ButtonRelease-1>", self.video_tree_single_click)

			# right-click popup
			# see: https://stackoverflow.com/questions/12014210/tkinter-app-adding-a-right-click-context-menu
			self.popup_menu = tkinter.Menu(self.videoFileTree, tearoff=0)
			self.popup_menu.add_command(label="Delete",
										command=self.delete_selected) #command=self.delete_selected
			self.popup_menu.add_command(label="Set Note",
										command=self.select_all) #command=self.select_all
			self.videoFileTree.bind("<Button-2>", self.popup)
			self.videoFileTree.bind("<Button-3>", self.popup) # Button-2 on Aqua
		
		# first delete entries
		for i in self.videoFileTree.get_children():
			self.videoFileTree.delete(i)

		for idx, videoFile in enumerate(self.videoList.getList()):
			position = "end"
			self.videoFileTree.insert("" , position, text=str(idx+1), values=videoFile.asTuple())

	
	# right click interface
	def popup(self, event):
		print('popup()')
		try:
			self.popup_menu.tk_popup(event.x_root, event.y_root) #, 0)
		finally:
			self.popup_menu.grab_release()

	def delete_selected(self):
		print('delete_selected() not implemented')
		#for i in self.curselection()[::-1]:
		#	self.delete(i)

	def select_all(self):
		print('select_all() not implemented')
		#self.selection_set(0, 'end')

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
	
			# set some column widths, width is in pixels?
			self.eventTree.column('index', minwidth=50, width=50, stretch="no")
			self.eventTree.column('type', minwidth=50, width=50, stretch="no")

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

			
	def switchvideo(self, videoPath, paused=False, gotoFrame=None):
		print('=== switchvideo() videoPath:', videoPath)
		if self.vs is not None:
			self.vs.stop()
		
		self.vs = FileVideoStream(videoPath, paused, gotoFrame) #.start()
		self.vs.start()
		
		if gotoFrame is None:
			self.setFrame(0)
		else:
			self.setFrame(gotoFrame)

		# set the selection in video tree
		# select the first video
		#child_id = self.videoFileTree.get_children()[-1] #last
		#child_id = self.videoFileTree.get_children()[0] #first

		# switch event list
		self.eventList = bEventList.bEventList(videoPath)
		
		# populate event list tree
		self.populateEvents()
		
		# set feedback frame
		self.numFrameLabel['text'] = 'of ' + str(self.vs.streamParams['numFrames'])
		self.numSecondsLabel['text'] = 'of ' + str(self.vs.streamParams['numSeconds'])
		
		# set frame slider
		self.video_frame_slider['to'] = self.vs.streamParams['numFrames']
		
		# select in video file tree view
		self._selectTreeViewRow(self.videoFileTree, 'path', videoPath)
		
	def treeview_sort_column(self, tv, col, reverse):
		print('treeview_sort_column()', 'tv:', tv, 'col:', col, 'reverse:', reverse)
		l = [(tv.set(k, col), k) for k in tv.get_children('')]
		
		print('   l:', l)
		
		#newlist = sorted(list_to_be_sorted, key=lambda k: k['name'])
		
		l.sort(reverse=reverse)

		# rearrange items in sorted positions
		for index, (val, k) in enumerate(l):
			tv.move(k, '', index)

		# reverse sort next time
		tv.heading(col, command=lambda:self.treeview_sort_column(tv, col, not reverse))
				   
	"""
	def set_aspect2(self, event):
		print('set_aspect2')
	"""
	
	#def mySetAspect(self):
	def mySetAspect(self, event):
		print('~~~~~ mySetAspect() event:')
		print('   event:', event)
		"""
		print('   event.widget:', event.widget)
		print('   event.type:', event.type)
		"""
		aspect_ratio = self.vs.streamParams['aspectRatio']
		buttonHeight = 36
		
		#desired_width = event.width - buttonHeight
		#desired_height = int(desired_width * aspect_ratio)
		
		#print(self.lower_right_frame.winfo_width(), self.lower_right_frame.winfo_height())
		
		#width = event.width
		#height = event.height
		width = self.videoLabel.winfo_width()
		height = self.videoLabel.winfo_height()
		desired_width = self.videoLabel.winfo_width() - buttonHeight
		desired_height = int(desired_width * aspect_ratio)
		
		if desired_height > height:
			desired_height = height - buttonHeight
			desired_width = int(desired_height / aspect_ratio)
		
		print('   width:', width, 'height:', height)
		print('   desired_width:', desired_width, 'desired_height:', desired_height)

		#self.content_frame.place(in_=self.lower_right_frame, x=0, y=0, width=desired_width, height=desired_height)

		#self.videoLabel.place(in_=self.content_frame, x=0, y=0, width=desired_width, height=desired_height)
		#self.video_control_frame.place(x=0, y=desired_height + buttonHeight, width=desired_width)
		
		print('~~~~~ mySetAspect() done')
		#self.root.after(100, self.mySetAspect)
  		
	# treeview util
	def _selectTreeViewRow(self, tv, col, isThis):
		"""
		Given a treeview (tv), a column name (col) and a value (isThis)
		Visually select the row in tree view that has column mathcing isThis
		
		tv: treeview
		col: (str) column name
		isThis: (str) value of a cell in column (col)
		"""
		theRow = self._getTreeViewRow(tv, col, isThis)
		
		# get the item
		children = tv.get_children()
		item = children[theRow]
		#print('item:', item)
		
		# select the row
		tv.focus(item) # select internally
		tv.selection_set(item) # visually select
		
	def _getTreeViewRow(self, tv, col, isThis):
		"""
		Given a treeview, a col name and a value (isThis)
		Return the row index of the column col mathing isThis
		"""
		# get the tree view columns and find the col we are looking for
		columns = tv['columns']				
		colIdx = columns.index(col) # assuming 'frameStart' exists

		#print('tv.get_children():', tv.get_children())
		
		rowIdx = 0
		for child in tv.get_children():
			values = tv.item(child)["values"] # values at current row
			if values[colIdx] == isThis:
				theRet = rowIdx
				break
			rowIdx += 1
		return rowIdx

	def _getTreeVidewSelection(self, tv, col):
		"""
		Get value of selected column
			tv: treeview
			col: (str) column name
		"""
		item = tv.focus()
		if item == '':
			print('_getTreeVidewSelection() did not find a selection in treeview  tv:', tv)
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
		
		"""
		# switch event list
		self.eventList = bEventList.bEventList(path)
		
		# populate event list tree
		self.populateEvents()
		
		# set feedback frame
		self.numFrameLabel['text'] = 'of ' + str(self.vs.streamParams['numFrames'])
		self.numSecondsLabel['text'] = 'of ' + str(self.vs.streamParams['numSeconds'])
		
		# set frame slider
		self.video_frame_slider['to'] = self.vs.streamParams['numFrames']
		"""
		
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

		myCurrentSeconds = self.vs.getSecondsFromFrame(self.myCurrentFrame)
		
		if cmd == 'playpause':
			self.vs.playPause()
				
		if cmd == 'forward':
			 newSeconds = myCurrentSeconds + self.configDict['smallSecondsStep']
			 self.setSeconds(newSeconds)
		if cmd == 'fast-forward':
			 newSeconds = myCurrentSeconds + self.configDict['largeSecondsStep']
			 self.setSeconds(newSeconds)
		if cmd == 'backward':
			 newSeconds = myCurrentSeconds - self.configDict['smallSecondsStep']
			 self.setSeconds(newSeconds)
		if cmd == 'fast-backward':
			 newSeconds = myCurrentSeconds - self.configDict['largeSecondsStep']
			 self.setSeconds(newSeconds)
			 
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
		if theKey in ['-', '_']:
			if self.myFrameInterval == 1:
				self.myFrameInterval = 0
			newFrameInterval = self.myFrameInterval + 10
			self.setFramesPerSecond(newFrameInterval)
		# faster, decrease frame interval
		if theKey in ['+', '=']:
			newFrameInterval = self.myFrameInterval - 10
			if newFrameInterval <= 0:
				newFrameInterval = 1
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
			
	def setSeconds(self, seconds):
		"""
		move to position in video seconds
		"""
		theFrame = self.vs.getFrameFromSeconds(seconds)
		self.setFrame(theFrame)
		
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
		item = self.eventTree.focus()
		if item == '':
			print('Please select an event')
			return
			
		d = bNoteDialog.bNoteDialog(self)
		
		if d is not None:
			self.root.wait_window(d.top)
		
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
		
		# todo: update 'numevents' in video file list
		
	def setFramesPerSecond(self, frameInterval):
		"""
		frameInterval: the interval (sec) between frames
		"""
		print('setFramesPerSecond() frameInterval:', frameInterval)
		# make sure I cancel using the same widget at end of videoloop()
		# cancel existing after()
		
		print('   shutting down video loop')
		self.root.after_cancel(self.videoLoopID)
		
		self.myFrameInterval = frameInterval
		self.myFramesPerSecond = round(1 / self.myFrameInterval,3) * 1000
		print('   starting video loop with self.myFrameInterval:', self.myFrameInterval)
		self.videoLoop()
		
	def videoLoop(self):
	
		if self.vs is not None and self.vs.paused:
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
			if self.vs is not None:
				[self.frame, self.myCurrentFrame] = self.vs.read()

		if self.vs is None or self.frame is None:
			#print('ERROR: VideoApp2.videoLoop() got None self.frame')
			pass
		else:
			## resize
			#tmpWidth = self.videoLabel.winfo_width()
			#tmpHeight = self.videoLabel.winfo_height()

			buttonHeight = 32
			
			width = self.content_frame.winfo_width()
			height = self.content_frame.winfo_height()
			
			tmpWidth = self.content_frame.winfo_width() - buttonHeight
			#tmpHeight = self.content_frame.winfo_height()
			tmpHeight = int(tmpWidth * self.vs.streamParams['aspectRatio'])

			if tmpHeight > height:
				tmpHeight = height - buttonHeight
				tmpWidth = int(tmpHeight / self.vs.streamParams['aspectRatio'])

			#tmpWidth = self.currentWidth
			#tmpHeight = self.currentHeight
			#print('   tmpWidth:', tmpWidth, 'tmpHeight:', tmpHeight)
			tmpImage = None
			try:
				tmpImage = self.frame
				#tmpImage = cv2.resize(self.frame, (tmpWidth, tmpHeight))
			except:
				#print('exception: in videoLoop() ... cv2.resize()')
				pass
				
			if tmpImage is not None:
				tmpImage = cv2.cvtColor(tmpImage, cv2.COLOR_BGR2RGB)
				tmpImage = Image.fromarray(tmpImage)
			
				tmpImage = tmpImage.resize((tmpWidth, tmpHeight), Image.ANTIALIAS)
				#tmpImage = tmpImage.resize((width, height), Image.ANTIALIAS)
				
				tmpImage = ImageTk.PhotoImage(tmpImage)
	
				try:
					self.videoLabel.configure(image=tmpImage)
					self.videoLabel.image = tmpImage
				except:
					print('exception: videoLoop() configure self.videoLabel')
			
			self.videoLabel.place(x=0, y=0, width=tmpWidth, height=tmpHeight)
			self.video_control_frame.place(x=0, y=tmpHeight + buttonHeight, width=tmpWidth)
			
			#
			# update feedback labels
			if 1:
				self.currentFrameLabel['text'] = 'Frame:' + str(self.myCurrentFrame)
				self.currentFrameIntervalLabel['text'] ='Frame Interval (ms):' + str(self.myFrameInterval)
				self.currentFramePerScondLabel['text'] ='fps:' + str(self.myFramesPerSecond)
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
