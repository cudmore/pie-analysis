# Author: Robert Cudmore
# Date: 20181101

"""
Create a video editing interface using tkinter
"""

import os, time, math
import threading
import json
#from collections import OrderedDict 

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
#import bNoteDialog
import bChunkView
import bTree # gives us bEventTree and (eventually) bVideoFileTree

##################################################################################
class VideoApp:
	def __init__(self, path=''):
		"""
		TKInter application to create interface for loading, viewing, and annotating video
		
		path: path to folder with video files
		"""
		
		self.path = path
		self.vs = None # FileVideoStream
		self.frame = None # the current frame, read from FileVideoStream

		# keep track of current with and only scale in VideoLoop() when neccessary
		self.currentWidth = 640
		self.currentHeight = 480
 		
		self.myCurrentFrame = None
		self.myCurrentSeconds = None
		self.pausedAtFrame = None

		#self.myCurrentChunk = None
		self.chunkFirstFrame = -2**32-1
		self.chunkLastFrame = 2**32-1
		
		self.configDict = {}
		# load config file
		self.optionsFile = 'options.json'
		if os.path.isfile(self.optionsFile):
			with open(self.optionsFile) as f:
				self.configDict = json.load(f)
		else:
			self.optionsDefaults()
		if os.path.isdir(self.configDict['lastPath']):
			self.path = self.configDict['lastPath']
		
		self.videoList = bVideoList.bVideoList(path)		

		# initialize with first video in path
		firstVideoPath = ''
		if len(self.videoList.videoFileList) > 0:
			firstVideoPath = self.videoList.videoFileList[0].dict['path']
		
		"""
		self.eventList = bEventList.bEventList(firstVideoPath)
		"""
		
		self.myFrameInterval = 30 # ms per frame
		self.myFramesPerSecond = round(1 / self.myFrameInterval,3) * 1000 # frames/second
				
		#
		# tkinter interface
		self.root = tkinter.Tk()
		self.root.title('PiE Video Analysis')
		
		# make window not resiazeable
		#self.root.resizable(width=False, height=False)
				
		# remove the default behavior of invoking the button with the space key
		self.root.unbind_class("Button", "<Key-space>")

		self.root.geometry(self.configDict['appWindowGeometry']) # home2

		self.buildInterface()

		self.chunkView.chunkInterface_populate()
		
		bMenus.bMenus(self)

		self.root.bind("<Key>", self.keyPress)

		# fire up a video stream
		# removed when adding loadFolder
		if len(firstVideoPath) > 0:
			self.switchvideo(firstVideoPath, paused=True, gotoFrame=0)

		# this will return but run in background using tkinter after()
		self.videoLoop()
		
		# set a callback to handle when the window is closed
		self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

		self.root.bind('<Command-q>', self.onClose)		

		self.root.mainloop()
		
	def loadFolder(self, path=''):
		if len(path) < 1:
			path = tkinter.filedialog.askdirectory()
		
		if not os.path.isdir(path):
			return
		
		self.path = path
		
		self.videoList = bVideoList.bVideoList(path)		
		self.populateVideoFiles(doInit=False)
	
		# initialize with first video in path
		firstVideoPath = self.videoList.videoFileList[0].dict['path']

		#self.eventList = bEventList.bEventList(firstVideoPath)
		# bTree switch
		#self.populateEvents(doInit=False)
		self.eventTree.populateEvents(firstVideoPath)
		
		# fire up a video stream
		self.switchvideo(firstVideoPath, paused=True, gotoFrame=0)
	
	def getEventTypeStr(self, type):
		return self.configDict['eventTypes'][type]
		
	def optionsDefaults(self):
		self.configDict['appWindowGeometry'] = "1100x700"
		self.configDict['showVideoFiles'] = True
		self.configDict['showEvents'] = True
		self.configDict['videoFileSash'] = 200 # pixels
		self.configDict['eventSash'] = 400 # pixels
		self.configDict['showRandomChunks'] = True
		self.configDict['showVideoFeedback'] = True
		self.configDict['smallSecondsStep'] = 10 # seconds
		self.configDict['largeSecondsStep'] = 60 # seconds
		self.configDict['fpsIncrement'] = 5 # seconds
		self.configDict['lastPath'] = self.path
		# map event number 1..9 to a string
		self.configDict['eventTypes'] = {
			'1': 'a',
			'2': 'b',
			'3': 'c',
			'4': 'd',
			'5': 'e',
			'6': 'f',
			'7': 'g',
			'8': 'h',
			'9': 'i'
			}
		
	def saveOptions(self):
		print('saveOptions()')

		if self.vPane.sashpos(0) > 0:
			self.configDict['videoFileSash'] = self.vPane.sashpos(0)
		if self.hPane.sashpos(0) > 0:
			self.configDict['eventSash'] = self.hPane.sashpos(0)
		geometryStr = str(self.root.winfo_width()) + "x" + str(self.root.winfo_height())
		self.configDict['appWindowGeometry'] = geometryStr
		
		with open(self.optionsFile, 'w') as outfile:
			json.dump(self.configDict, outfile, indent=4, sort_keys=True)
	
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
		if this == 'videofeedback':
			self.configDict['showVideoFeedback'] = not self.configDict['showVideoFeedback']
			if self.configDict['showVideoFeedback']:
				self.video_feedback_frame.grid()
			else:
				self.video_feedback_frame.grid_remove()
						
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

		# bTree switch
		self.videoFileTree = bTree.bVideoFileTree(upper_frame, self, videoFileList='', show='headings')
		self.videoFileTree.grid(row=0,column=0, sticky="nsew", padx=myPadding, pady=myPadding)
		"""
		self.videoFileTree = ttk.Treeview(upper_frame, show='headings')
		self.videoFileTree.grid(row=0,column=0, sticky="nsew", padx=myPadding, pady=myPadding)
		videoFileTree_scrollbar = ttk.Scrollbar(upper_frame, orient="vertical", command = self.videoFileTree.yview)
		videoFileTree_scrollbar.grid(row=0, column=0, sticky='nse', padx=myPadding, pady=myPadding)
		self.videoFileTree.configure(yscrollcommand=videoFileTree_scrollbar.set)
		"""
		
		"""
		if self.configDict['showVideoFiles']:
			self.videoFileTree.grid()
		else:
			self.videoFileTree.grid_remove()
		"""
		# bTree switch
		#self.populateVideoFiles(doInit=True)
		self.videoFileTree.populateVideoFiles(self.videoList, doInit=True)

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
		
		# bTree switch
		self.eventTree = bTree.bEventTree(lower_left_frame, self, videoFilePath='', show='headings')
		self.eventTree.grid(row=0,column=0, sticky="nsew", padx=myPadding, pady=myPadding)
		"""
		self.eventTree = ttk.Treeview(lower_left_frame, show='headings')
		self.eventTree.grid(row=0,column=0, sticky="nsew", padx=myPadding, pady=myPadding)
		eventTree_scrollbar = ttk.Scrollbar(lower_left_frame, orient="vertical", command = self.eventTree.yview)
		eventTree_scrollbar.grid(row=0, column=0, sticky='nse', padx=myPadding, pady=myPadding)
		self.eventTree.configure(yscrollcommand=eventTree_scrollbar.set)
		"""
		if self.configDict['showEvents']:
			pass
			#self.eventTree.grid()
		else:
			self.eventTree.grid_remove()
		# btree switch
		"""
		self.populateEvents(doInit=True)
		"""
		#self.eventTree.populateEvents(self.eventList, doInit=True)
		
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
		self.video_feedback_frame = ttk.Frame(self.lower_right_frame)
		self.video_feedback_frame.grid(row=1, column=0, sticky="nw")

		self.currentFrameLabel = ttk.Label(self.video_feedback_frame, width=11, anchor="w", text='Frame:')
		self.currentFrameLabel.grid(row=0, column=0)
		
		self.numFrameLabel = ttk.Label(self.video_feedback_frame, width=8, anchor="w", text='of ')
		self.numFrameLabel.grid(row=0, column=1)

		self.currentSecondsLabel = ttk.Label(self.video_feedback_frame, width=8, anchor="w", text='Sec:')
		self.currentSecondsLabel.grid(row=0, column=2, sticky="w")
		
		self.numSecondsLabel = ttk.Label(self.video_feedback_frame, width=8, anchor="w", text='of ')
		self.numSecondsLabel.grid(row=0, column=3, sticky="w")
		
		self.currentFrameIntervalLabel = ttk.Label(self.video_feedback_frame, width=20, anchor="w", text='Frame Interval (ms):')
		self.currentFrameIntervalLabel.grid(row=0, column=4, sticky="w")

		self.currentFramePerScondLabel = ttk.Label(self.video_feedback_frame, width=20, anchor="w", text='fps:')
		self.currentFramePerScondLabel.grid(row=0, column=5, sticky="w")

		if self.configDict['showVideoFeedback']:
			#self.video_feedback_frame.grid()
			pass
		else:
			self.video_feedback_frame.grid_remove()

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
		video_fr_button.bind("<Key>", self.ignore)

		video_r_button = ttk.Button(self.video_control_frame, width=1, text="<", command=lambda: self.doCommand('backward'))
		video_r_button.grid(row=0, column=1)
		video_r_button.bind("<Key>", self.ignore)

		self.video_play_button = ttk.Button(self.video_control_frame, width=4, text="Play", command=lambda: self.doCommand('playpause'))
		self.video_play_button.grid(row=0, column=2)
		self.video_play_button.bind("<Key>", self.ignore)
	
		video_f_button = ttk.Button(self.video_control_frame, width=1, text=">", command=lambda: self.doCommand('forward'))
		video_f_button.grid(row=0, column=3)
		video_f_button.bind("<Key>", self.ignore)
	
		video_ff_button = ttk.Button(self.video_control_frame, width=1, text=">>", command=lambda: self.doCommand('fast-forward'))
		video_ff_button.grid(row=0, column=4)
		video_ff_button.bind("<Key>", self.ignore)
	
		#self.video_frame_slider = ttk.Scale(self.video_control_frame, from_=0, to=0, orient="horizontal", command=self.frameSlider_callback)
		self.frameSliderVar = tkinter.IntVar()
		self.video_frame_slider = tkinter.Scale(self.video_control_frame, from_=0, to=0, orient="horizontal", showvalue=False,
													command=self.frameSlider_callback,
													variable=self.frameSliderVar)
		self.video_frame_slider.grid(row=0, column=5, sticky="ew")
		self.buttonDownInSlider = False
		self.video_frame_slider.bind("<Button-1>", self.buttonDownInSlider_callback)
		self.video_frame_slider.bind("<ButtonRelease-1>", self.buttonUpInSlider_callback)
		#self.video_frame_slider.bind("<B1-Motion>", self.buttonMotionInSlider_callback)
		
		#
		# set aspect of video frame
		#self.set_aspect(self.lower_right_frame, self.content_frame, self.pad_frame, self.video_control_frame, aspect_ratio=myApectRatio) 
		#self.set_aspect(self.hPane, self.lower_right_frame, self.content_frame, self.pad_frame, self.video_control_frame, self.videoLabel) #, aspect_ratio=myApectRatio) 
				
		#
		# do this at very end
		self.root.update()
		self.vPane.sashpos(0, self.configDict['videoFileSash'])
		self.hPane.sashpos(0, self.configDict['eventSash'])

		#self.videoLabel.bind("<Configure>", self.mySetAspect)
		#self.mySetAspect()
		
	"""
	def buttonMotionInSlider_callback(self, event):
		print('buttonMotionInSlider_callback() event:', event)
	"""
	
	def ignore(self, event):
		"""
		This function will take all key-presses (except \r) and pass to main app.
		return "break" is critical to stop propogation of event
		"""
		print('ignore event.char:', event.char)
		if event.char == '\r':
			pass
		else:
			self.keyPress(event)
			return 'break'

	def buttonDownInSlider_callback(self,event):
		#print('buttonDownInSlider() event:', event.type, type(event.type))
		self.buttonDownInSlider = True
		
	def buttonUpInSlider_callback(self,event):
		#print('buttonUpInSlider_callback() event:', event.type, type(event.type))
		self.buttonDownInSlider = False
		
	###################################################################################

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
		#self.eventList = bEventList.bEventList(videoPath)
		
		# bTree switch
		# populate event list tree
		#self.populateEvents()
		#self.eventTree.populateEvents(self.eventList)
		self.eventTree.populateEvents(videoPath)
		
		# set feedback frame
		self.numFrameLabel['text'] = 'of ' + str(self.vs.getParam('numFrames'))
		self.numSecondsLabel['text'] = 'of ' + str(self.vs.getParam('numSeconds'))
		
		# set frame slider
		self.video_frame_slider['from_'] = 0
		self.video_frame_slider['to'] = self.vs.getParam('numFrames') - 1
		
		# select in video file tree view
		self.videoFileTree._selectTreeViewRow('path', videoPath)
		
	def hijackInterface(self, onoff):
		print('hijackInterface() onoff:', onoff)
		if onoff:
			currentChunk = self.chunkView.getCurrentChunk()
			chunkIndex = currentChunk['index']
			startFrame = currentChunk['startFrame']
			stopFrame = currentChunk['stopFrame']
			
			print('   startFrame:', startFrame, 'stopFrame:', stopFrame)
			#print('   ', type(startFrame), type(stopFrame), type(numFrames))

			# need to set value first, if outside start/stop then slider get stuck
			#self.video_frame_slider['value'] = startFrame + 1
			#self.video_frame_slider['from_'] = startFrame
			#self.video_frame_slider['to'] = stopFrame

			self.chunkFirstFrame = startFrame
			self.chunkLastFrame = stopFrame
			
			#self.video_frame_slider.set(startFrame)
			self.video_frame_slider['from_'] = startFrame
			self.video_frame_slider['to'] = stopFrame
			self.frameSliderVar.set(startFrame)
			
			# WHAT THE FUCK IS GOING ON ??????????
			self.buttonDownInSlider = True
			
			self.setFrame(startFrame)
			
			self.buttonDownInSlider = False
			
			# need to limit event tree to just events in this chunk!!!
			# todo: write event tree filter(chunkIndex)
			self.eventTree.filter(chunkIndex)
		else:
			#print('hijackInterface() chunk is none')
			self.chunkFirstFrame = -2**32-1
			self.chunkLastFrame = 2**32-1
			self.video_frame_slider['from_'] = 0
			self.video_frame_slider['to'] = self.vs.getParam('numFrames') - 1
			#self.video_frame_slider['value'] = startFrame
			self.eventTree.filter(None)
			
	#def mySetAspect(self):
	def old_mySetAspect(self, event):
		print('~~~~~ mySetAspect() event:')
		print('   event:', event)
		"""
		print('   event.widget:', event.widget)
		print('   event.type:', event.type)
		"""
		aspect_ratio = self.vs.getParam('aspectRatio')
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
  		
	# video file tree
	def frameSlider_callback(self, frameNumber):
		frameNumber = int(float(frameNumber))
		print('VideoApp.frameSlider_callback() frameNumber:', frameNumber, 'self.myCurrentFrame:', self.myCurrentFrame)
		print('   from:', self.video_frame_slider['from'], 'to:', self.video_frame_slider['to']) #, 'value:', self.video_frame_slider['value'])
		
		#frameNumber = self.video_frame_slider['from'] + frameNumber
		
		self.setFrame(frameNumber)

		#time.sleep(0.01)
		
	def doCommand(self, cmd):

		#myCurrentSeconds = self.vs.getSecondsFromFrame(self.myCurrentFrame)
		
		if cmd == 'playpause':
			if not self.vs.isOpened:
				print('playpause, video is not opened')
			else:
				self.vs.playPause()
				if self.vs.paused:
					self.video_play_button['text'] = 'Play'
				else:
					self.video_play_button['text'] = 'Pause'
		if cmd == 'forward':
			if self.myCurrentSeconds is not None:
				newSeconds = self.myCurrentSeconds + self.configDict['smallSecondsStep']
				newFrame = self.vs.getFrameFromSeconds(newSeconds)
				print('doCommand FORWARD newSeconds:', newSeconds, 'newFrame:', newFrame, 'self.chunkLastFrame:', self.chunkLastFrame)
				if newFrame > self.chunkLastFrame:
					newSeconds = self.vs.getSecondsFromFrame(self.chunkLastFrame)
					print('   forcing frame to chunkLastFrame', self.chunkLastFrame, 'newSeconds:', newSeconds)
				self.setSeconds(newSeconds)
		if cmd == 'fast-forward':
			if self.myCurrentSeconds is not None:
				newSeconds = self.myCurrentSeconds + self.configDict['largeSecondsStep']
				newFrame = self.vs.getFrameFromSeconds(newSeconds)
				print('doCommand fast-forward newSeconds:', newSeconds, 'newFrame:', newFrame, 'self.chunkLastFrame:', self.chunkLastFrame)
				if newFrame > self.chunkLastFrame:
					newSeconds = self.vs.getSecondsFromFrame(self.chunkLastFrame)
					print('   forcing frame to chunkLastFrame', self.chunkLastFrame, 'newSeconds:', newSeconds)
				self.setSeconds(newSeconds)
		if cmd == 'backward':
			if self.myCurrentSeconds is not None:
				newSeconds = self.myCurrentSeconds - self.configDict['smallSecondsStep']
				newFrame = self.vs.getFrameFromSeconds(newSeconds)
				print('doCommand backward newSeconds:', newSeconds, 'newFrame:', newFrame, 'self.chunkLastFrame:', self.chunkFirstFrame)
				if newFrame < self.chunkFirstFrame:
					newSeconds = self.vs.getSecondsFromFrame(self.chunkFirstFrame)
					print('   forcing frame to chunkFirstFrame', self.chunkFirstFrame, 'newSeconds:', newSeconds)
				self.setSeconds(newSeconds)
		if cmd == 'fast-backward':
			if self.myCurrentSeconds is not None:
				newSeconds = self.myCurrentSeconds - self.configDict['largeSecondsStep']
				newFrame = self.vs.getFrameFromSeconds(newSeconds)
				print('doCommand fast-backward newSeconds:', newSeconds, 'newFrame:', newFrame, 'self.chunkLastFrame:', self.chunkFirstFrame)
				if newFrame < self.chunkFirstFrame:
					newSeconds = self.vs.getSecondsFromFrame(self.chunkFirstFrame)
					print('   forcing frame to chunkFirstFrame', self.chunkFirstFrame, 'newSeconds:', newSeconds)
				self.setSeconds(newSeconds)
			 
	def keyPress(self, event):
		print('=== VideoApp.keyPress() pressed:', repr(event.char), 'event.state:', event.state, 'self.myCurrentFrame:', self.myCurrentFrame)
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
			if self.myCurrentFrame is not None:
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
			if self.myCurrentFrame is not None:
				self.setStartFrame(self.myCurrentFrame)
		# set stop frame
		if theKey == 'l':
			if self.myCurrentFrame is not None:
				self.setEndFrame(self.myCurrentFrame)
			
		# slower (increase frame interval)
		if theKey in ['-', '_']:
			newFramesPerSecond = self.myFramesPerSecond - self.configDict['fpsIncrement']
			# todo: make sure we can get back to original frames per seconds !!!
			if newFramesPerSecond<1:
				newFramesPerSecond += self.configDict['fpsIncrement']
			self.setFramesPerSecond(newFramesPerSecond)
		# faster, decrease frame interval
		if theKey in ['+', '=']:
			newFramesPerSecond = self.myFramesPerSecond + self.configDict['fpsIncrement']
			if newFramesPerSecond>90:
				newFramesPerSecond -= self.configDict['fpsIncrement']
			self.setFramesPerSecond(newFramesPerSecond)
			
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
		if self.vs is not None and self.vs.setFrame(theFrame):
			self.myCurrentFrame = theFrame
		else:
			print('VideoApp.setFrame() failed')
			
	def setStartFrame(self, frame):
		print('setStartFrame() frame:', frame)
		self.eventTree.set('frameStart', frame)
		
	def setEndFrame(self, frame):
		print('setEndFrame() frame:', frame)
		self.eventTree.set('frameStop', frame)
		
	def setNote(self):
		"""
		Open modal dialog to set note of selected event
		"""
		print('VideoApp.setNote()')
		
		# btree switch
		"""
		# get selection from event list
		item = self.eventTree.focus()
		if item == '':
			print('Please select an event')
			return
			
		d = bNoteDialog.bNoteDialog(self)
		
		if d is not None:
			self.root.wait_window(d.top)
		"""
		self.eventTree.editNote()
		
	def addEvent(self, theKey, frame):
		"""
		Append a new event at the current frame
		"""
		# just in case
		frame = int(float(frame))
		
		# bTree switch
		videoFilePath = self.vs.streamParams['path']
		chunkIndex = self.chunkView.findChunk(videoFilePath, frame)
		self.eventTree.appendEvent(theKey, frame, chunkIndex=chunkIndex)
		
	def setFramesPerSecond(self, newFramesPerSecond):
		"""
		newFramesPerSecond: frames/second
		"""
		print('setFramesPerSecond()')
		# make sure I cancel using the same widget at end of videoloop()
		# cancel existing after()
		
		print('   shutting down video loop')
		self.root.after_cancel(self.videoLoopID)
		
		self.myFrameInterval = math.floor(1000 / newFramesPerSecond)
		self.myFramesPerSecond = newFramesPerSecond #round(1 / self.myFrameInterval,3) * 1000
		print('self.myFrameInterval:', self.myFrameInterval, 'self.myFramesPerSecond:', self.myFramesPerSecond)
		print('   starting video loop with self.myFrameInterval:', self.myFrameInterval)
		self.videoLoop()
		
	def videoLoop(self):
	
		if self.vs is not None and self.vs.paused:
			self.videoLabel.configure(text="Paused")
			if (self.pausedAtFrame != self.myCurrentFrame):
				#print('VideoApp2.videoLoop() fetching new frame when paused', 'self.pausedAtFrame:', self.pausedAtFrame, 'self.myCurrentFrame:', self.myCurrentFrame)
				try:
					#print('VideoApp2.videoLoop() CALLING self.vs.read()')
					[self.frame, self.myCurrentFrame, self.myCurrentSeconds] = self.vs.read()
				except:
					print('zzz qqq')
				self.pausedAtFrame = self.myCurrentFrame
		else:
			self.videoLabel.configure(text="")
			if self.vs is not None and (self.myCurrentFrame != self.vs.getParam('numFrames')-1) and ( self.myCurrentFrame < self.chunkLastFrame):
				[self.frame, self.myCurrentFrame, self.myCurrentSeconds] = self.vs.read()

		if not self.vs.isOpened or self.vs is None or self.frame is None:
			#print('ERROR: VideoApp2.videoLoop() got None self.frame')
			pass
		else:

			buttonHeight = 32
			
			aspectRatio = self.vs.getParam('aspectRatio')
			
			width = self.content_frame.winfo_width()
			height = self.content_frame.winfo_height()
			
			tmpWidth = self.content_frame.winfo_width() - buttonHeight
			#tmpHeight = self.content_frame.winfo_height()
			tmpHeight = int(tmpWidth * aspectRatio)

			if tmpHeight > height:
				tmpHeight = height - buttonHeight
				tmpWidth = int(tmpHeight / aspectRatio)

			tmpImage = self.frame
			
			tmpImage = cv2.resize(self.frame, (tmpWidth, tmpHeight))
				
			if tmpImage is not None:
				tmpImage = cv2.cvtColor(tmpImage, cv2.COLOR_BGR2RGB)
				tmpImage = Image.fromarray(tmpImage)
				#tmpImage = tmpImage.resize((tmpWidth, tmpHeight), Image.ANTIALIAS)
				tmpImage = ImageTk.PhotoImage(tmpImage)
	
				self.videoLabel.configure(image=tmpImage)
				self.videoLabel.image = tmpImage
			
			self.videoLabel.place(x=0, y=0, width=tmpWidth, height=tmpHeight)
			
			if self.configDict['showRandomChunks']:
				chunksHeight = self.random_chunks_frame.winfo_height()
			else:
				chunksHeight = 0
			if self.configDict['showVideoFeedback']:
				feedbackHeight = self.video_feedback_frame.winfo_height()
			else:
				feedbackHeight = 0
			yPos = tmpHeight + chunksHeight + feedbackHeight + 2 #+ buttonHeight
			self.video_control_frame.place(x=0, y=yPos, width=tmpWidth)
			
			#
			# update feedback labels
			self.currentFrameLabel['text'] = 'Frame:' + str(self.myCurrentFrame)
			self.currentFrameIntervalLabel['text'] ='Frame Interval (ms):' + str(self.myFrameInterval)
			self.currentFramePerScondLabel['text'] ='fps:' + str(self.myFramesPerSecond)
			self.currentSecondsLabel['text'] = 'Sec:' + str(self.myCurrentSeconds) #str(round(self.myCurrentFrame / self.vs.streamParams['fps'],2))
			
			#print('self.myCurrentFrame:', self.myCurrentFrame)
			# for ttk
			#self.video_frame_slider['value'] = self.myCurrentFrame
			# for tkinter
			#self.video_frame_slider.set(self.myCurrentFrame)
			if not self.buttonDownInSlider:
				self.frameSliderVar.set(self.myCurrentFrame)
			
		# leave this here -- CRITICAL
		self.videoLoopID = self.root.after(self.myFrameInterval, self.videoLoop)
		
	def onClose(self, event=None):

		# set the stop event, cleanup the camera, and allow the rest of
		# the quit process to continue
		print("VideoApp.onClose()")
		self.isRunning = False
		self.vs.stop()
		
		self.saveOptions()
		
		self.root.quit()
