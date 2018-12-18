# Author: Robert Cudmore
# Date: 20181101

"""
Create a video editing interface using tkinter
"""

import sys # for drag and drop in app created by pyinstaller
import os, time, math
import threading
import json

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
import bChunkView
import bTree # gives us bEventTree and bVideoFileTree
import bDialog
import bEventCanvas

__version__ = '20181217'

##################################################################################
class VideoApp:
	def __init__(self, path=''):
		"""
		TKInter application to create interface for loading, viewing, and annotating video
		
		path: path to folder with video files (only works with mp4)
		"""
		
		#self.needsUpdate = False
		self.pausedNeedsUpdate = False

		self.lastUpdateSeconds = None
		self.thisUpdateSeconds = None

		self.buttonIsDown = False
		#self.myCurrentImage = None
		self.lrWidth = None
		self.rHeight = None
		self.videoLoopID = None
		
		self.path = path
		self.vs = None # FileVideoStream
		self.frame = None # the current frame, read from FileVideoStream
		
		# keep track of current with and only scale in VideoLoop() when neccessary
		self.currentWidth = 640
		self.currentHeight = 480
		 
		#self.inConfigure = False
		self.switchingVideo = False
		self.switchingFrame = False
		
		self.myCurrentFrame = None
		self.myCurrentSeconds = None
		self.pausedAtFrame = None
		self.switchedVideo = False
		self.setFrameWhenPaused = None

		self.myCurrentChunk = None # bChunk object
		self.chunkFirstFrame = -2**32-1
		self.chunkLastFrame = 2**32-1
		
		self.myEventCanvas = None
		
		self.currentVideoWidth = 1
		self.currentVideoHeight = 1
		
		self.configDict = {}
		# load config file
		# todo: put this in a 'loadOption' function
		if getattr(sys, 'frozen', False):
			# we are running in a bundle (frozen)
			bundle_dir = sys._MEIPASS
		else:
			# we are running in a normal Python environment
			bundle_dir = os.path.dirname(os.path.abspath(__file__))

		# load preferences
		self.optionsFile = os.path.join(bundle_dir, 'options.json')
		
		if os.path.isfile(self.optionsFile):
			print('    loading options file:', self.optionsFile)
			with open(self.optionsFile) as f:
				self.configDict = json.load(f)
		else:
			print('    using program provided default options')
			self.preferencesDefaults()

		# path to video file list, can be None
		if os.path.isdir(self.configDict['lastPath']):
			self.path = self.configDict['lastPath']
		
		# video file list
		# HANDLED BY loadFolder
		"""
		self.videoList = bVideoList.bVideoList(self.path)		
		"""
		
		# HANDLED BY loadFolder
		"""
		# initialize with first video in path
		firstVideoPath = ''
		if len(self.videoList.videoFileList) > 0:
			firstVideoPath = self.videoList.videoFileList[0].dict['path']
		"""
		
		self.myFrameInterval = 30 # ms per frame
		self.myFramesPerSecond = round(1 / self.myFrameInterval * 1000, 2) # frames/second
				
		#
		# tkinter interface
		self.root = tkinter.Tk()
		
		# hide while building
		#self.root.withdraw()
		
		self.root.title('Video Annotate')
		
		self.root.bind("<Key>", self.keyPress)
		self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)
		self.root.bind('<Command-q>', self.onClose)		
		# remove the default behavior of invoking the button with the space key
		self.root.unbind_class("Button", "<Key-space>")

		# position root window
		x = self.configDict['appWindowGeometry_x']
		y = self.configDict['appWindowGeometry_y']
		w = self.configDict['appWindowGeometry_w']
		h = self.configDict['appWindowGeometry_h']
		self.root.geometry('%dx%d+%d+%d' % (w, h, x, y))

		self.buildInterface()

		# HANDLED BY loadFolder
		"""
		self.chunkView.chunkInterface_populate()
		"""
		
		self.myMenus = bMenus.bMenus(self)

		# fire up a video stream
		# this is redundant with above
		#self.loadFolder(self.path)
		"""
		if len(firstVideoPath) > 0:
			self.switchvideo(firstVideoPath, paused=True, gotoFrame=0)
		"""
			
		# this will return but run in background using tkinter after()
		self.videoLoop()
		
		if os.path.isdir(self.path):
			self.loadFolder(self.path)
		
		self.blindInterface(self.configDict['blindInterface'], gotoFirstChunk=True)

		# show at very end, paired with self.root.withdraw()
		#self.root.update()
		#self.root.deiconify()


		# this will not return until we quit
		self.root.mainloop()
		
	def loadFolder(self, path=''):
		if len(path) < 1:
			path = tkinter.filedialog.askdirectory()
		
		if not os.path.isdir(path):
			print('error: did not find path:', path)
			return
		
		self.path = path
		self.configDict['lastPath'] = path
		
		self.videoList = bVideoList.bVideoList(path)		
		self.videoFileTree.populateVideoFiles(self.videoList, doInit=True)
	
		# initialize with first video in path
		firstVideoPath = ''
		if len(self.videoList.videoFileList):
			firstVideoPath = self.videoList.videoFileList[0].dict['path']

		self.chunkView.chunkInterface_populate()

		# fire up a video stream
		"""
		if len(firstVideoPath) > 0:	
			self.switchvideo(firstVideoPath, paused=True, gotoFrame=0)
		"""
		
		# removed when adding loadFolder
		if self.configDict['blindInterface']:
			print('*** VideoApp.loadFolder() is blinded, going to chunk 0')
			wentToChunk0 = self.chunkView.chunk_goto(0) # if the new folder has no random chunks, this makes no sense
			if wentToChunk0:
				# done
				self.hijackInterface(True)
				# this (Self) interface will remain blinded, make sure chunk view is also blinded
				self.chunkView.blindInterface(True)
			else:
				if len(firstVideoPath) > 0:	
					self.switchvideo(firstVideoPath, paused=True, gotoFrame=0)
		else:
			print('*** VideoApp.loadFolder() is not blinded and calling switchvideo()')
			if len(firstVideoPath) > 0:	
				self.switchvideo(firstVideoPath, paused=True, gotoFrame=0)
			# no matter what, turn this off
			self.chunkView.hijackControlsCheckbox.state(['!selected'])
			self.hijackInterface(False)
			
	def getEventTypeStr(self, type):
		return self.configDict['eventTypes'][type]
		
	def preferencesDefaults(self):
		self.configDict['appWindowGeometry_w'] = 1100
		self.configDict['appWindowGeometry_h'] = 700
		self.configDict['appWindowGeometry_x'] = 100
		self.configDict['appWindowGeometry_y'] = 100
		self.configDict['showVideoFiles'] = True
		self.configDict['showEvents'] = True
		self.configDict['videoFileSash'] = 200 # pixels
		self.configDict['eventSash'] = 400 # pixels
		#self.configDict['showRandomChunks'] = True
		self.configDict['showVideoFeedback'] = True
		self.configDict['smallSecondsStep'] = 10 # seconds
		self.configDict['largeSecondsStep'] = 60 # seconds
		self.configDict['smallSecondsStep_chunk'] = 1 # seconds
		self.configDict['largeSecondsStep_chunk'] = 2 # seconds
		self.configDict['fpsIncrement'] = 5 # seconds
		self.configDict['warnOnEventDelete'] = False
		self.configDict['lastPath'] = self.path
		self.configDict['blindInterface'] = False
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
		self.configDict['keyMap'] = {
			'prevChunk': '[',
			'nextChunk': ']',
			'setEventFrameStart': 'f',
			'setEventFrameStop': 'l',
			'event1': '1',
			'event2': '2',
			'event3': '3',
			'event4': '4',
			'event5': '5',
			'event6': '6',
			'event7': '7',
			'event8': '8',
			'event9': '9',
		}
		
	def savePreferences(self):
		print('=== VideoApp.savePreferences() file:', self.optionsFile)

		x = self.root.winfo_x()
		y = self.root.winfo_y()
		w = self.root.winfo_width()
		h = self.root.winfo_height()

		self.configDict['appWindowGeometry_x'] = x
		self.configDict['appWindowGeometry_y'] = y
		self.configDict['appWindowGeometry_w'] = w
		self.configDict['appWindowGeometry_h'] = h

		with open(self.optionsFile, 'w') as outfile:
			json.dump(self.configDict, outfile, indent=4, sort_keys=True)
	
	###################################################################################
	def blindInterface(self, onoff, gotoFirstChunk=False):
		"""
		turn video list and controls on/off
		"""

		# video file and event sash are opposite, use 'not onoff'
		self.toggleInterface('videofiles', not onoff)
		self.toggleInterface('events', not onoff)
		
		# turns on 'limit' checkbox and deactive(s) it
		self.chunkView.blindInterface(onoff, gotoFirstChunk=gotoFirstChunk)
		
		# turns off some 'windows' menus
		self.myMenus.blindMenus(onoff)
		
		self.configDict['blindInterface'] = onoff
		
		#self.myMenus.setState('Video Files', not onoff)
		#self.myMenus.setState('Events', not onoff)
		
	def toggleInterface(self, this, onoff):
		"""
		toggle window panel/frames on and off, including (videofiles, events)
		"""
		if this == 'videofiles':
			self.configDict['showVideoFiles'] = onoff
			if onoff:
				print("self.configDict['videoFileSash']:", self.configDict['videoFileSash'])
				self.vPane.sashpos(0, self.configDict['videoFileSash'])
				self.videoFileTree.grid()
			else:
				self.vPane.sashpos(0, 0)
				self.videoFileTree.grid_remove()
		if this == 'events':
			self.configDict['showEvents'] = onoff
			if onoff:
				self.hPane.sashpos(0, self.configDict['eventSash'])
				self.eventTree.grid()
			else:
				self.hPane.sashpos(0, 10)
				self.eventTree.grid_remove()

	###################################################################################
	def buildInterface(self):
		myPadding = 5
		myBorderWidth = 0

		self.lastResizeWidth = None
		self.lastResizeHeight = None
		
		self.root.grid_rowconfigure(0, weight=1)
		self.root.grid_columnconfigure(0, weight=1)

		#
		self.vPane = ttk.PanedWindow(self.root, orient="vertical") #, showhandle=True)
		self.vPane.grid(row=0, column=0, sticky="nsew")

		upper_frame = ttk.Frame(self.vPane, borderwidth=myBorderWidth, relief="sunken")
		upper_frame.grid(row=0, column=0, sticky="nsew", padx=myPadding, pady=myPadding)
		upper_frame.grid_rowconfigure(0, weight=1)
		upper_frame.grid_columnconfigure(0, weight=1)
		self.vPane.add(upper_frame)

		self.videoFileTree = bTree.bVideoFileTree(upper_frame, self, videoFileList='')
		self.videoFileTree.grid(row=0,column=0, sticky="nsew", padx=myPadding, pady=myPadding)
		# HANDLED BY loadfolder
		#self.videoFileTree.populateVideoFiles(self.videoList, doInit=True)
		if self.configDict['showVideoFiles']:
			pass
			#self.videoFileTree.grid()
		else:
			self.videoFileTree.grid_remove()

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

		#self.hPane.state(['disabled'])

		lower_left_frame = ttk.Frame(self.hPane, borderwidth=myBorderWidth, relief="sunken")
		lower_left_frame.grid(row=0, column=0, sticky="nsew", padx=myPadding, pady=myPadding)
		lower_left_frame.grid_rowconfigure(0, weight=1)
		lower_left_frame.grid_columnconfigure(0, weight=1)

		self.hPane.add(lower_left_frame) #, stretch="always")
		
		# event tree
		self.eventTree = bTree.bEventTree(lower_left_frame, self, videoFilePath='')
		self.eventTree.grid(row=0,column=0, sticky="nsew", padx=myPadding, pady=myPadding)
		if self.configDict['showEvents']:
			pass
			#self.eventTree.grid()
		else:
			self.eventTree.grid_remove()
		
		#
		# video
		randomChunkRow = 4
		#videoFeedbackRow = 2
		contentFrameRow = 0 # contains video label
		videoControlRow = 1
		videoFrameSlider = 2
		eventCanvasRow = 3
		
		lowerRightPadding = 0 # was myPadding
		self.lower_right_frame = ttk.Frame(self.hPane, borderwidth=myBorderWidth, relief="sunken")
		self.lower_right_frame.grid(row=0, column=1, sticky="nsew", padx=lowerRightPadding, pady=lowerRightPadding)

		self.lower_right_frame.grid_rowconfigure(0, weight=0) # row 0 col 0 is random_chunks_frame
		self.lower_right_frame.grid_rowconfigure(1, weight=0) # row 1 col 0 is video_feedback_frame
		###
		#self.lower_right_frame.grid_rowconfigure(2, weight=0) # row 2 col 0 is content_frame -->> content_frame causing crash
		###
		self.lower_right_frame.grid_rowconfigure(2, weight=0) # row 3 col 0 is video_control_frame
		self.lower_right_frame.grid_rowconfigure(3, weight=0) # row 4 col 0 is video_frame_slider
		self.lower_right_frame.grid_rowconfigure(4, weight=0) # row 5 col 0 is myEventCanvas
		
		self.lower_right_frame.grid_columnconfigure(0, weight=1)

		#self.lower_right_frame.bind("<Configure>", self._configureLowerRightFrame) # causing crash?

		# add to horizontal pane
		#self.hPane.add(self.lower_right_frame)

		#
		# random chunks
		self.random_chunks_frame = ttk.Frame(self.lower_right_frame)
		tmpPad = 0
		self.random_chunks_frame.grid(row=randomChunkRow, column=0, sticky="w", padx=tmpPad, pady=tmpPad)
		"""
		if self.configDict['showRandomChunks']:
			print('buildInterface() is SHOWING random_chunks_frame')
			pass
			#self.random_chunks_frame.grid()
		else:
			print('buildInterface() is HIDING random_chunks_frame')
			self.random_chunks_frame.grid_remove()
		"""
		self.chunkView = bChunkView.bChunkView(self, self.random_chunks_frame)
		
		#
		# video feedback
		"""
		self.video_feedback_frame = ttk.Frame(self.lower_right_frame)
		self.video_feedback_frame.grid(row=videoFeedbackRow, column=0, sticky="nw")

		self.currentFrameLabel = ttk.Label(self.video_feedback_frame, width=11, anchor="w", text='Frame:')
		self.currentFrameLabel.grid(row=0, column=0)
		
		self.numFrameLabel = ttk.Label(self.video_feedback_frame, width=8, anchor="w", text='of ')
		self.numFrameLabel.grid(row=0, column=1)

		self.currentSecondsLabel = ttk.Label(self.video_feedback_frame, width=9, anchor="w", text='Sec:')
		self.currentSecondsLabel.grid(row=0, column=2, sticky="w")
		
		self.numSecondsLabel = ttk.Label(self.video_feedback_frame, width=8, anchor="w", text='of ')
		self.numSecondsLabel.grid(row=0, column=3, sticky="w")
		
		#self.currentFrameIntervalLabel = ttk.Label(self.video_feedback_frame, width=20, anchor="w", text='Frame Interval (ms):')
		#self.currentFrameIntervalLabel.grid(row=0, column=4, sticky="w")

		self.currentFramePerScondLabel = ttk.Label(self.video_feedback_frame, width=20, anchor="w", text='file FPS')
		self.currentFramePerScondLabel.grid(row=0, column=4, sticky="w")

		if self.configDict['showVideoFeedback']:
			#self.video_feedback_frame.grid()
			pass
		else:
			self.video_feedback_frame.grid_remove()
		"""
		
		#
		# video frame
		
		contentBorderWidth = 0 # was 5
		self.content_frame = ttk.Frame(self.lower_right_frame, borderwidth=contentBorderWidth, relief="groove") #
		self.content_frame.grid(row=contentFrameRow, column=0, sticky="nsew") #, padx=5, pady=5)
		# 20181207 10:30
		#self.content_frame.grid_rowconfigure(0, weight=1)
		#self.content_frame.grid_columnconfigure(0, weight=1)
	
		# insert image into content frame
		tmpImage = np.zeros((480,640,3), np.uint8)
		tmpImage = Image.fromarray(tmpImage)
		tmpImage = ImageTk.PhotoImage(tmpImage)
		#self.myCurrentImage = tmpImage

		self.videoLabel = ttk.Label(self.content_frame, text="No Folder", font=("Helvetica", 48), compound="center", foreground="green")
		self.videoLabel.grid(row=0, column=0, sticky="nsew")
		
		self.videoLabel.configure(image=tmpImage)
		self.videoLabel.image = tmpImage
		"""
		self.videoLabel.configure(image=self.myCurrentImage)
		self.videoLabel.image = self.myCurrentImage
		"""
		
		#
		# video controls
		self.video_control_frame = ttk.Frame(self.lower_right_frame, borderwidth=myBorderWidth,relief="groove")
		self.video_control_frame.grid(row=videoControlRow, column=0, sticky="w", padx=myPadding, pady=myPadding)
		# was this
		#self.video_control_frame.grid_columnconfigure(5, weight=1) # to expand video_frame_slider
		#self.video_control_frame.grid_rowconfigure(0, weight=1) # to expand video_frame_slider
		#self.video_control_frame.grid_rowconfigure(1, weight=1) # to expand video_frame_slider

		video_fr_button = ttk.Button(self.video_control_frame, width=1, text="<<", command=lambda: self.doCommand('fast-backward'))
		video_fr_button.grid(row=0, column=0, sticky="w")
		video_fr_button.bind("<Key>", self._ignoreKey)

		video_r_button = ttk.Button(self.video_control_frame, width=1, text="<", command=lambda: self.doCommand('backward'))
		video_r_button.grid(row=0, column=1, sticky="w")
		video_r_button.bind("<Key>", self._ignoreKey)

		self.video_play_button = ttk.Button(self.video_control_frame, width=4, text="Play", command=lambda: self.doCommand('playpause'))
		self.video_play_button.grid(row=0, column=2, sticky="w")
		self.video_play_button.bind("<Key>", self._ignoreKey)
	
		video_f_button = ttk.Button(self.video_control_frame, width=1, text=">", command=lambda: self.doCommand('forward'))
		video_f_button.grid(row=0, column=3, sticky="w")
		video_f_button.bind("<Key>", self._ignoreKey)
	
		video_ff_button = ttk.Button(self.video_control_frame, width=1, text=">>", command=lambda: self.doCommand('fast-forward'))
		video_ff_button.grid(row=0, column=4, sticky="w")
		video_ff_button.bind("<Key>", self._ignoreKey)

		#
		self.currentSecondsLabel = ttk.Label(self.video_control_frame, width=9, anchor="w", text='Sec:')
		self.currentSecondsLabel.grid(row=0, column=5, sticky="w")
		
		self.numSecondsLabel = ttk.Label(self.video_control_frame, width=8, anchor="w", text='of ')
		self.numSecondsLabel.grid(row=0, column=6, sticky="w")

		self.currentFramePerScondLabel = ttk.Label(self.video_control_frame, width=20, anchor="w", text='file FPS')
		self.currentFramePerScondLabel.grid(row=0, column=7, sticky="w")

		self.actualFramesPerSecondLabel = ttk.Label(self.video_control_frame, width=20, anchor="w", text='actual fps:')
		self.actualFramesPerSecondLabel.grid(row=0, column=8, sticky="w")

		#
		
		sliderPadding = 0 # shared by video_frame_slider and myEventCanvas

		#
		# frame slider
		#self.video_frame_slider = ttk.Scale(self.video_control_frame, from_=0, to=0, orient="horizontal", command=self.frameSlider_callback)
		self.frameSliderVar = tkinter.IntVar()
		# was this
		"""
		self.video_frame_slider = tkinter.Scale(self.video_control_frame, from_=0, to=0, orient="horizontal", showvalue=False,
													command=self.frameSlider_callback,
													variable=self.frameSliderVar)
		"""
		# put video_frame_slider in its own row
		self.video_frame_slider = tkinter.Scale(self.lower_right_frame, from_=0, to=0, orient="horizontal", showvalue=False,
													command=self.frameSlider_callback,
													variable=self.frameSliderVar)
		
		# was this
		#self.video_frame_slider.grid(row=0, column=5, sticky="ew")
		#self.video_frame_slider.grid(row=1, column=0, columnspan=4, sticky="ew", padx=sliderPadding)
		# put video_frame_slider in its own row
		self.video_frame_slider.grid(row=videoFrameSlider, column=0, sticky="ew", padx=sliderPadding)
		self.buttonDownInSlider = False
		self.video_frame_slider.bind("<Button-1>", self.buttonDownInSlider_callback)
		self.video_frame_slider.bind("<ButtonRelease-1>", self.buttonUpInSlider_callback)
		#self.video_frame_slider.bind("<B1-Motion>", self.buttonMotionInSlider_callback)
		
		#
		# event canvas
		#self.myEventCanvas = bEventCanvas.bEventCanvas(self.video_control_frame)
		self.myEventCanvas = bEventCanvas.bEventCanvas(self, self.lower_right_frame)
		# was this
		#self.myEventCanvas.grid(row=2, column=0, columnspan=5, sticky="nsew", padx=sliderPadding)
		self.myEventCanvas.grid(row=eventCanvasRow, column=0, sticky="ew", padx=sliderPadding)
		
		# add to horizontal pane
		self.hPane.add(self.lower_right_frame) #, stretch="always")

		#
		# do this at very end
		
		# not sure if this is needed
		#self.root.update()
		
		if self.configDict['showVideoFiles']:
			self.vPane.sashpos(0, self.configDict['videoFileSash'])
		else:
			self.vPane.sashpos(0, 0)
		if self.configDict['showEvents']:
			self.hPane.sashpos(0, self.configDict['eventSash'])
		else:
			self.hPane.sashpos(0, 0)

		#self.videoLabel.bind("<Configure>", self.mySetAspect)
		#self.mySetAspect()

		self.root.bind('<ButtonRelease-1>', self.myButtonUp)
		self.root.bind('<Button-1>', self.myButtonDown)
		self.lower_right_frame.bind('<Configure>', self._configureContentFrame) # causing crash?

	def _ignoreKey(self, event):
		"""
		This function will take all key-presses (except \r) and pass to main app.
		return "break" is critical to stop propogation of event
		"""
		#print('ignore event.char:', event.char)
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

	def hijackInterface(self, onoff):
		"""
		Limit video controls to a chunk (for blinding)
		"""
		print('\n=== VideoApp.hijackInterface() onoff:', onoff)
		if onoff:
			self.myCurrentChunk, randomIdx = self.chunkView.getCurrentChunk()
			if self.myCurrentChunk is None:
				print('error: VideoApp.hijackInterface() did not find any chunks')
				return 0
			
			chunkIndex = self.myCurrentChunk['index'] # absolute index
			startFrame = self.myCurrentChunk['startFrame']
			stopFrame = self.myCurrentChunk['stopFrame']
			
			#self.chunkView.printChunk(self.myCurrentChunk)

			self.chunkFirstFrame = startFrame # -inf when off
			self.chunkLastFrame = stopFrame # +inf when off
			
			self.video_frame_slider.config(from_=startFrame)
			self.video_frame_slider.config(to=stopFrame)
			
			#print('   hijackInterface calling self.setFrame() startFrame:', startFrame)
			self.setFrame(startFrame)
			
			# limit event tree to just events in this chunk!!!
			self.eventTree.filter(randomIdx) # randomIdx is index into random list of chunks

			# set feedback frame relative to chunk duration
			tmpNumFrames = self.myCurrentChunk['stopFrame'] - self.myCurrentChunk['startFrame'] + 1
			#self.numFrameLabel['text'] = 'of ' + str(tmpNumFrames)
			tmpNumSeconds = round(tmpNumFrames / self.vs.getParam('fps'), 2)
			self.numSecondsLabel['text'] = 'of ' + str(tmpNumSeconds)
		else:
			#print('hijackInterface() chunk is none')
			self.myCurrentChunk = None
			self.chunkFirstFrame = -2**32-1
			self.chunkLastFrame = 2**32-1
			self.video_frame_slider['from_'] = 0
			self.video_frame_slider['to'] = self.vs.getParam('numFrames') - 1
			#self.video_frame_slider['value'] = startFrame
			self.eventTree.filter(None)

			# set feedback frame
			#self.numFrameLabel['text'] = 'of ' + str(self.vs.getParam('numFrames'))
			self.numSecondsLabel['text'] = 'of ' + str(self.vs.getParam('numSeconds'))
			
	# video file tree
	def frameSlider_callback(self, frameNumber):
		#print('VideoApp.frameSlider_callback()')
		if self.buttonDownInSlider:
			frameNumber = int(float(frameNumber))
			"""
			print('VideoApp.frameSlider_callback()')
			print('   frameNumber:', frameNumber)
			print('   self.myCurrentFrame:', self.myCurrentFrame)
			print('   from:', self.video_frame_slider['from'])
			print('   to:', self.video_frame_slider['to'])
			#print('   get():', self.video_frame_slider.get())
			
			print('   calling self.setFrame(frameNumber)', frameNumber)
			"""
			self.setFrame(frameNumber, withDelay=False)
		else:
			print('VideoApp.frameSlider_callback() skipped when not self.buttonDownInSlider')
				
	def doCommand(self, cmd):

		#myCurrentSeconds = self.vs.getSecondsFromFrame(self.myCurrentFrame)
		if self.myCurrentChunk is None:
			smallSecondsStep = self.configDict['smallSecondsStep']
			largeSecondsStep = self.configDict['largeSecondsStep']
		else:
			smallSecondsStep = self.configDict['smallSecondsStep_chunk']
			largeSecondsStep = self.configDict['largeSecondsStep_chunk']
			
		if cmd == 'playpause':
			if self.vs is None or not self.vs.isOpened:
				print('playpause - video is not opened')
			else:
				self.vs.playPause()
				if self.vs.paused:
					self.video_play_button['text'] = 'Play'
				else:
					self.video_play_button['text'] = 'Pause'
		if cmd == 'forward':
			if self.myCurrentSeconds is not None:
				newSeconds = self.myCurrentSeconds + smallSecondsStep
				newFrame = self.vs.getFrameFromSeconds(newSeconds)
				#print('doCommand FORWARD newSeconds:', newSeconds, 'newFrame:', newFrame, 'self.chunkLastFrame:', self.chunkLastFrame)
				if newFrame > self.chunkLastFrame:
					newSeconds = self.vs.getSecondsFromFrame(self.chunkLastFrame)
					#print('   forcing frame to chunkLastFrame', self.chunkLastFrame, 'newSeconds:', newSeconds)
				if newFrame > self.vs.getParam('numFrames')-1:
					newSeconds = self.vs.getSecondsFromFrame(self.vs.getParam('numFrames')-1)
					#print('   (1) forcing frame to newSeconds:', newSeconds)
				self.setSeconds(newSeconds)
		if cmd == 'fast-forward':
			if self.myCurrentSeconds is not None:
				newSeconds = self.myCurrentSeconds + largeSecondsStep
				newFrame = self.vs.getFrameFromSeconds(newSeconds)
				#print('doCommand fast-forward newSeconds:', newSeconds, 'newFrame:', newFrame, 'self.chunkLastFrame:', self.chunkLastFrame)
				if newFrame > self.chunkLastFrame:
					newSeconds = self.vs.getSecondsFromFrame(self.chunkLastFrame)
					#print('   forcing frame to chunkLastFrame', self.chunkLastFrame, 'newSeconds:', newSeconds)
				if newFrame > self.vs.getParam('numFrames')-1:
					newSeconds = self.vs.getSecondsFromFrame(self.vs.getParam('numFrames')-1)
					#print('   (2) forcing frame to newSeconds:', newSeconds)
				self.setSeconds(newSeconds)
		if cmd == 'backward':
			if self.myCurrentSeconds is not None:
				newSeconds = self.myCurrentSeconds - smallSecondsStep
				newFrame = self.vs.getFrameFromSeconds(newSeconds)
				#print('doCommand backward newSeconds:', newSeconds, 'newFrame:', newFrame, 'self.chunkLastFrame:', self.chunkFirstFrame)
				if newFrame < self.chunkFirstFrame:
					newSeconds = self.vs.getSecondsFromFrame(self.chunkFirstFrame)
					#print('   forcing frame to chunkFirstFrame', self.chunkFirstFrame, 'newSeconds:', newSeconds)
				if newFrame < 0:
					newSeconds = 0
					#print('   (3) forcing frame to newSeconds:', newSeconds)
				self.setSeconds(newSeconds)
		if cmd == 'fast-backward':
			if self.myCurrentSeconds is not None:
				newSeconds = self.myCurrentSeconds - largeSecondsStep
				newFrame = self.vs.getFrameFromSeconds(newSeconds)
				#print('doCommand fast-backward newSeconds:', newSeconds, 'newFrame:', newFrame, 'self.chunkLastFrame:', self.chunkFirstFrame)
				if newFrame < self.chunkFirstFrame:
					newSeconds = self.vs.getSecondsFromFrame(self.chunkFirstFrame)
					#print('   forcing frame to chunkFirstFrame', self.chunkFirstFrame, 'newSeconds:', newSeconds)
				if newFrame < 0:
					newSeconds = 0
					#print('   (4) forcing frame to newSeconds:', newSeconds)
				self.setSeconds(newSeconds)
			 
	def keyPress(self, event):
		#print('=== VideoApp.keyPress() pressed:', repr(event.char), 'event.state:', event.state, 'self.myCurrentFrame:', self.myCurrentFrame)
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
			
		if theKey == self.configDict['keyMap']['prevChunk']:
			self.chunkView.chunk_previous()
		if theKey == self.configDict['keyMap']['nextChunk']:
			self.chunkView.chunk_next()


		# add event
		"""
		validEventKeys = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
		validEventKeys = [
			self.configDict['keyMap']['event1'],
			self.configDict['keyMap']['event2'],
			self.configDict['keyMap']['event3'],
			self.configDict['keyMap']['event4'],
			self.configDict['keyMap']['event5'],
			self.configDict['keyMap']['event6'],
			self.configDict['keyMap']['event7'],
			self.configDict['keyMap']['event8'],
			self.configDict['keyMap']['event9'],
			
		]
		if theKey in validEventKeys:
			if self.myCurrentFrame is not None:
				print('keyPress() adding event, theKey:', theKey)
				eventNum = 
				self.addEvent(theKey, self.myCurrentFrame)
		"""
		
		if theKey == self.configDict['keyMap']['event1']:
			if self.myCurrentFrame is not None:
				print('keyPress() adding event, theKey:', theKey)
				eventNum = "1"
				self.addEvent(eventNum, self.myCurrentFrame)
		if theKey == self.configDict['keyMap']['event2']:
			if self.myCurrentFrame is not None:
				print('keyPress() adding event, theKey:', theKey)
				eventNum = "2"
				self.addEvent(eventNum, self.myCurrentFrame)
		if theKey == self.configDict['keyMap']['event3']:
			if self.myCurrentFrame is not None:
				print('keyPress() adding event, theKey:', theKey)
				eventNum = "3"
				self.addEvent(eventNum, self.myCurrentFrame)
		if theKey == self.configDict['keyMap']['event4']:
			if self.myCurrentFrame is not None:
				print('keyPress() adding event, theKey:', theKey)
				eventNum = "4"
				self.addEvent(eventNum, self.myCurrentFrame)
		if theKey == self.configDict['keyMap']['event5']:
			if self.myCurrentFrame is not None:
				print('keyPress() adding event, theKey:', theKey)
				eventNum = "5"
				self.addEvent(eventNum, self.myCurrentFrame)
		if theKey == self.configDict['keyMap']['event6']:
			if self.myCurrentFrame is not None:
				print('keyPress() adding event, theKey:', theKey)
				eventNum = "6"
				self.addEvent(eventNum, self.myCurrentFrame)
		if theKey == self.configDict['keyMap']['event7']:
			if self.myCurrentFrame is not None:
				print('keyPress() adding event, theKey:', theKey)
				eventNum = "7"
				self.addEvent(eventNum, self.myCurrentFrame)
		if theKey == self.configDict['keyMap']['event8']:
			if self.myCurrentFrame is not None:
				print('keyPress() adding event, theKey:', theKey)
				eventNum = "8"
				self.addEvent(eventNum, self.myCurrentFrame)
		if theKey == self.configDict['keyMap']['event9']:
			if self.myCurrentFrame is not None:
				print('keyPress() adding event, theKey:', theKey)
				eventNum = "9"
				self.addEvent(eventNum, self.myCurrentFrame)
		
		# delete event
		if theKey in ['d', '\x7f']:
			self.deleteEvent()

		# set note of selected event
		if theKey == 'n':
			self.setNote()
			
		# set event start frame
		#if theKey == 'f':
		if theKey == self.configDict['keyMap']['setEventFrameStart']:
			if self.myCurrentFrame is not None:
				self.setStartFrame(self.myCurrentFrame)
		# set stop frame
		#if theKey == 'l':
		if theKey == self.configDict['keyMap']['setEventFrameStop']:
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
			if newFramesPerSecond>120:
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
		"""
		if theKey == '\t':
			focused_widget = self.root.focus_get()
			print('focused_widget.name:', focused_widget)
		"""
			
	def setSeconds(self, seconds):
		"""
		move to position in video seconds
		"""
		theFrame = self.vs.getFrameFromSeconds(seconds)
		self.setFrame(theFrame, withDelay=True)
		
	def setFrame(self, theFrame, withDelay=False):
		#print('VideoApp.setFrame() theFrame:', theFrame)
		#self.switchingFrame = True
		if self.vs is not None and self.vs.setFrame(theFrame):
			self.myCurrentFrame = theFrame
			#print('   self.myCurrentFrame:', self.myCurrentFrame)
			#print('   self.pausedAtFrame:', self.pausedAtFrame)
			if self.vs.paused:
				self.setFrameWhenPaused = theFrame
				#print('   self.setFrameWhenPaused:', self.setFrameWhenPaused)
			if withDelay:
				print('VideoApp.setFrame() is pausing')
				#time.sleep(0.01)
				
			self.myEventCanvas.setFrame(theFrame)
		else:
			print('VideoApp.setFrame() failed')
		#self.switchingFrame = False
			
	def setStartFrame(self, frame):
		print('setStartFrame() frame:', frame)
		self.eventTree.set('frameStart', frame)
		
		# sort events
		self.eventTree.sort_column('frameStart', False)
		
	def setEndFrame(self, frame):
		print('setEndFrame() frame:', frame)
		self.eventTree.set('frameStop', frame)
		
	def setNote(self):
		"""
		Open modal dialog to set note of selected event
		"""
		self.eventTree.editNote()
		
	def addEvent(self, theKey, frame):
		"""
		Append a new event at the current frame
		"""
		print('=== VideoApp.addEvent()')
		
		# just in case
		frame = int(float(frame))
		
		videoFilePath = self.vs.streamParams['path']
		
		# chunkIndex is NOT sort order (As in interface)
		# chunkIndex is absolute index into chunk list in randomChunks.txt
		chunkIndex, randomChunkIndex = self.chunkView.findChunk(videoFilePath, frame)
		
		print('   frame:', frame)
		print('   videoFilePath:', videoFilePath)
		print('   chunkIndex:', chunkIndex, type(chunkIndex))
		print('   randomChunkIndex:', randomChunkIndex, type(randomChunkIndex))
		
		self.eventTree.appendEvent(theKey, frame, chunkIndex=chunkIndex, randomChunkIndex=randomChunkIndex)
	
	def deleteEvent(self):
		self.eventTree.deleteEvent()
		
	def setFramesPerSecond(self, newFramesPerSecond):
		"""
		newFramesPerSecond: frames/second
		"""
		print('setFramesPerSecond()')
		# make sure I cancel using the same widget at end of videoloop()
		# cancel existing after()
		
		if self.videoLoopID is not None:
			print('   shutting down video loop')
			self.root.after_cancel(self.videoLoopID)
		
			self.myFrameInterval = math.floor(1000 / newFramesPerSecond)
			self.myFramesPerSecond = round(newFramesPerSecond,2)
			print('   self.myFrameInterval:', self.myFrameInterval, 'self.myFramesPerSecond:', self.myFramesPerSecond)
			print('   starting video loop with self.myFrameInterval:', self.myFrameInterval)
			self.videoLoop()
		
	def switchvideo(self, videoPath, paused=False, gotoFrame=None):
		print('=== VideoApp.switchvideo() videoPath:', videoPath, 'paused:', paused, 'gotoFrame:', gotoFrame)

		self.switchingVideo = True # temporarily shit down videoLoop
		
		if self.vs is None:
			print('   switchvideo() is instantiating stream')
			self.vs = FileVideoStream(videoPath, paused, gotoFrame) #.start()
			#print('   self.vs.start()')
			self.vs.start()
			time.sleep(0.02)
		else:
			print('   switchvideo() is switching stream')
			self.vs.switchStream(videoPath, paused, gotoFrame)
			time.sleep(0.02)
		
		# so (paused) videoLoop loop will update
		self.switchedVideo = True
		
		# select in video file tree view
		self.videoFileTree._selectTreeViewRow('path', videoPath)

		self.eventTree.populateEvents(videoPath)
		
		# set feedback frame
		#self.numFrameLabel['text'] = 'of ' + str(self.vs.getParam('numFrames'))
		self.numSecondsLabel['text'] = 'of ' + str(self.vs.getParam('numSeconds'))
		
		self.currentFramePerScondLabel['text'] ='file ' + str(round(self.vs.streamParams['fps'],2)) + ' FPS'

		# set frame slider
		self.video_frame_slider.config(from_=0)
		self.video_frame_slider.config(to=self.vs.getParam('numFrames') - 1)

		# THIS CAUSES INFINITE LOOP
		# if blinding is on, we need to keep it on
		"""
		self.blindInterface(self.configDict['blindInterface'], gotoFirstChunk=True)
		if self.configDict['blindInterface']:
			self.chunkView.chunk_goto(0)
		#self.chunkView.blindInterface(self.configDict['blindInterface'])
		"""
		
		# THIS CAUSES INFINITE LOOP
		# if we are blinded then ALWAYS hijack interface
		# isually called from bChunkView
		"""
		print('*************** switchvideo calling xxx')
		if self.configDict['blindInterface']:
			self.hijackInterface(True)
		"""
		
		# leave this here
		self.switchingVideo = False
		
	####################################################################################
	def myButtonDown(self, event):
		#print('~~~ myButtonDown()')
		self.buttonIsDown = True
		#self.inConfigure = True
		#return 'break'
		#print('    returning')
	def myButtonUp(self, event):
		#print('myButtonUp()')
		self.buttonIsDown = False
		#self.inConfigure = False
	
	def _configureContentFrame(self, event=None, forceUpdate=False):
		print('\n=== _configureContentFrame() event:', event)
		
		#print('   self.lower_right_frame.coords():', self.lower_right_frame.coords())
		
		if 0 and not self.buttonIsDown and not forceUpdate:
			print('_configureContentFrame() returning - button is not down')
			return 0
		
		if self.vs is None:
			return 0
		
		#self.inConfigure = True

		aspectRatio = self.vs.getParam('aspectRatio')

		chunksHeight = self.random_chunks_frame.winfo_height()
			
		"""
		if self.configDict['showVideoFeedback']:
			feedbackHeight = self.video_feedback_frame.winfo_height()
		else:
			feedbackHeight = 0
		"""
			
		buttonHeight = 32
		eventCanvasHeight = 100
		
		if forceUpdate:
			width = self.lower_right_frame.winfo_width()	
			height = self.lower_right_frame.winfo_height()
			print('    _configureContentFrame forceUpdate width:', width, 'height:', height)
		else:
			width = event.width
			height = event.height
		
		myBorder = 20
		newWidth = width - myBorder #- eventCanvasHeight
		if newWidth < 0:
			newWidth = 1
		newHeight = int(newWidth * aspectRatio)

		print('    newWidth:', newWidth, 'newHeight:', newHeight)
		if newHeight > height:
			newHeight = height - myBorder #- eventCanvasHeight
			if newHeight < 0:
				newHeight = 1
			newWidth = int(newHeight / aspectRatio)
			print('    swapped w/h newHeight:', newHeight, 'newWidth:', newWidth)

		self.currentVideoWidth = newWidth
		self.currentVideoHeight = newHeight
		
		self.content_frame.place(width=newWidth, height=newHeight)
		
		#
		# IMPORTANT
		# scale background filevideostream
		if self.vs is not None:
			self.vs.setScale(newWidth, newHeight)
		
		yPos = newHeight + int(buttonHeight/2) #+ chunksHeight + feedbackHeight #+ buttonHeight
		self.video_control_frame.place(y=yPos, width=newWidth)

		yPos += buttonHeight
		self.video_frame_slider.place(y=yPos, width=newWidth)

		chunkHeight = self.random_chunks_frame.winfo_height()
		
		yPos += buttonHeight
		newCanvasHeight = height - newHeight - buttonHeight - buttonHeight - 2*chunkHeight - int(buttonHeight/2)
		"""
		print('    height:', height)
		print('    newHeight:', newHeight)
		print('    buttonHeight:', buttonHeight)
		print('    feedbackHeight:', feedbackHeight)
		print('    newCanvasHeight:', newCanvasHeight)
		"""
		if newCanvasHeight < 50:
			newCanvasHeight = 50
			print('    LIMITING newCanvasHeight:', newCanvasHeight)
		self.myEventCanvas.on_resize2(yPos, newWidth, newCanvasHeight)		
		
		# chunks
		#self.random_chunks_frame.grid()
		yPos += newCanvasHeight + int(chunkHeight/2)
		self.random_chunks_frame.place(y=yPos, width=newWidth)

		# turned off in myButtonUp() when button is released
		#self.inConfigure = False

		self.pausedNeedsUpdate = True
		
		#print('    done')
		
	####################################################################################
	def videoLoop(self):
		
		#print('videoLoop()', time.time())
		myContinue = True
		#if 0 and self.inConfigure:
		#	myContinue = False
		if self.switchingVideo:
			# was this
			#pass
			myContinue = False
		if self.vs is None:
			myContinue = False
		if myContinue:
			if self.vs is not None and self.vs.gotoFrame is not None:
				pass
			else:
				#self.vs.scaleWidth = self.currentVideoWidth
				#self.vs.scaleHeight = self.currentVideoHeight

				#print('inner videoLoop()', time.time())
				if self.vs is not None and self.vs.paused:
					self.videoLabel.configure(text="Paused")
					if (self.pausedAtFrame is None or (self.pausedAtFrame != self.myCurrentFrame) or self.switchedVideo or self.setFrameWhenPaused is not None):
						self.switchedVideo = False
						#self.pausedNeedsUpdate = False
						#print('VideoApp2.videoLoop() fetching new frame when paused', 'self.pausedAtFrame:', self.pausedAtFrame, 'self.myCurrentFrame:', self.myCurrentFrame)
						try:
							#print('VideoApp2.videoLoop() CALLING self.vs.read()')
							[self.frame, self.myCurrentFrame, self.myCurrentSeconds] = self.vs.read()
							self.frameSliderVar.set(self.myCurrentFrame)
							#self.thisUpdateSeconds = time.time()
							#print('   got self.myCurrentFrame:', self.myCurrentFrame)
						except:
							print('my exception in VideoApp.videoLoop(), self.vs.read() failed when PAUSED')
							print('    self.frame:', self.frame)
							print('    self.myCurrentFrame:', self.myCurrentFrame)
							print('    self.myCurrentSeconds:', self.myCurrentSeconds)
							
						# this is to fix not progressing on click to new eent (we are reading too fast)
						if self.setFrameWhenPaused is not None:
							print('   videoLoop() grabbed frame when paused after setFrame')
							print('      self.myCurrentFrame:', self.myCurrentFrame, 'self.setFrameWhenPaused:', self.setFrameWhenPaused)
							if self.myCurrentFrame != self.setFrameWhenPaused:
								print('      *** OUT OF SYNCH ***\n')
								#[self.frame, self.myCurrentFrame, self.myCurrentSeconds] = self.vs.read()
								#print('      self.myCurrentFrame:', self.myCurrentFrame)
							#self.frameSliderVar.set(self.myCurrentFrame)
							self.setFrameWhenPaused = None
						self.pausedAtFrame = self.myCurrentFrame
					elif self.pausedNeedsUpdate:
						self.pausedNeedsUpdate = False
						print('paused needs updating')
						if self.frame is not None:
							self.frame = cv2.resize(self.frame, (self.currentVideoWidth, self.currentVideoHeight))
						
				else:
					self.videoLabel.configure(text="")
					try:
						if self.vs is not None and (self.myCurrentFrame != self.vs.getParam('numFrames')-1) and ( self.myCurrentFrame < self.chunkLastFrame):
							[self.frame, self.myCurrentFrame, self.myCurrentSeconds] = self.vs.read()
							self.frameSliderVar.set(self.myCurrentFrame)
							#self.thisUpdateSeconds = time.time()
					except:
						print('****** my exception in videoLoop(), self.vs.read() failed when NOT paused')
						print('    self.frame:', self.frame)
						print('    self.myCurrentFrame:', self.myCurrentFrame)
						print('    self.myCurrentSeconds:', self.myCurrentSeconds)
				
				if self.vs is None or not self.vs.isOpened or self.vs is None or self.frame is None:
					#print('ERROR: VideoApp2.videoLoop() got None self.frame')
					pass
				else:

					buttonHeight = 32
					eventCanvasHeight = 100
				
					tmpImage = self.frame
								
					#self.vs.scaleWidth = self.currentVideoWidth
					#self.vs.scaleHigth = self.currentVideoHeight
					
					# self.currentVideoWidth set in _configureContentFrame
					#this works, best we can do is 33-35 fps
					#tmpImage = cv2.resize(self.frame, (self.currentVideoWidth, self.currentVideoHeight))
				
					if tmpImage is not None:
						tmpImage = cv2.cvtColor(tmpImage, cv2.COLOR_BGR2RGB)
						tmpImage = Image.fromarray(tmpImage)
						# this works too, best we can do is 18 fps
						#tmpImage = tmpImage.resize((self.currentVideoWidth, self.currentVideoHeight), Image.ANTIALIAS)
						tmpImage = ImageTk.PhotoImage(tmpImage)
							
						"""
						# make video noise for debugging
						tmpImage = np.random.randint(0, 255, (480,640,3)).astype('uint8')
						tmpImage = Image.fromarray(tmpImage)
						tmpImage = tmpImage.resize((self.currentVideoWidth, self.currentVideoHeight), Image.ANTIALIAS)
						tmpImage = ImageTk.PhotoImage(tmpImage)
						"""
						
						# swap image
						self.videoLabel.configure(image=tmpImage)
						self.videoLabel.image = tmpImage
						
					self.myEventCanvas.setFrame(self.myCurrentFrame)

					#
					# update feedback labels
					"""
					if self.myCurrentChunk is not None:
						tmpFrame = self.myCurrentFrame - self.myCurrentChunk['startFrame']
						self.currentFrameLabel['text'] = 'Frame:' + str(tmpFrame)
				
					else:
						self.currentFrameLabel['text'] = 'Frame:' + str(self.myCurrentFrame)
					"""
					
					if self.myCurrentChunk is not None:
						tmpCurrentSeconds = self.vs.getSecondsFromFrame(self.myCurrentFrame) - self.vs.getSecondsFromFrame(self.myCurrentChunk['startFrame'])
						tmpCurrentSeconds = round(tmpCurrentSeconds,2)
						self.currentSecondsLabel['text'] = 'Sec:' + str(tmpCurrentSeconds)
					else:
						self.currentSecondsLabel['text'] = 'Sec:' + str(self.myCurrentSeconds) #str(round(self.myCurrentFrame / self.vs.streamParams['fps'],2))
					#self.currentFrameIntervalLabel['text'] ='Frame Interval (ms):' + str(self.myFrameInterval)
					# todo: remove self.myFramesPerSecond
					#self.currentFramePerScondLabel['text'] ='file ' + str(self.myFramesPerSecond) + ' FPS'
					#self.currentFramePerScondLabel['text'] ='file ' + str(round(self.vs.streamParams['fps']),2) + ' FPS'
					
					self.thisUpdateSeconds = time.time()
					if not self.vs.paused:
						if self.lastUpdateSeconds is not None:
							if self.thisUpdateSeconds - self.lastUpdateSeconds > 0:
								actualFramesPerSecond = round(1/(self.thisUpdateSeconds - self.lastUpdateSeconds),2)
								#print('actualFramesPerSecond:', actualFramesPerSecond)
								self.actualFramesPerSecondLabel['text'] ='playing ' + str(actualFramesPerSecond) + ' FPS'
					#self.lastUpdateSeconds = self.thisUpdateSeconds

					#self.root.update()
				
		#print('    videoloop() done')

		#
		# HOLY FUCKING SHIT - update() SOLVES WINDOW SIZING CRASH !!!!!!!!!!!!!!!!!!
		#
		# see: http://effbot.org/tkinterbook/widget.htm
		#self.root.update_idletasks()
		# update() is faster - but should only be called after _configureContentFrame
		# this does not work
		"""
		if self.needsUpdate:
			self.root.update()
			self.needsUpdate = False
		"""

		# CRITICAL - Leave this here
		self.root.update()
			
		self.lastUpdateSeconds = self.thisUpdateSeconds
		
		# CRITICAL - Leave this here
		actualInterval = int(self.myFrameInterval)
		self.videoLoopID = self.root.after(actualInterval, self.videoLoop)
		# was this
		#self.videoLoopID = self.lower_right_frame.after(actualInterval, self.videoLoop)
		
		#self.root.after_idle(self.videoLoop)
		#self.videoLoopID = self.root.after_idle(self.videoLoop)
		#self.vPane.after_idle(self.videoLoop)
		
	def onClose(self, event=None):
		print("VideoApp.onClose()")
		self.isRunning = False
		self.vs.stop()
		self.savePreferences()
		self.root.quit()

if __name__ == '__main__':
	print('VideoApp.__main__() sys.argv:', sys.argv)
	va = VideoApp()
