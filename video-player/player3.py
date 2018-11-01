# Author: Robert Cudmore
# Date: 20181030

import threading
import os, sys, time

import cv2

import tkinter
from tkinter import ttk

from PIL import Image
from PIL import ImageTk
from PIL import ImageFont
from PIL import ImageDraw

import numpy as np

from queue import Queue
	
##################################################################################
class PhotoBoothApp:
	def __init__(self, vs):
		"""
		vs: FileVideoStream
		"""

		# parameters from FileVideoStream
		fileName = vs.streamParams['fileName']
		width = vs.streamParams['width']
		height = vs.streamParams['height']
		fps = vs.streamParams['fps']
		numFrames = vs.streamParams['numFrames']

		self.events = {}
		
		self.vs = vs
		self.frame = None
		self.thread = None
		self.stopEvent = None
 
		self.paused = False
 		
		# initialize the root window and image panel
		self.root = tkinter.Tk()

		#
		# start videoFileTree, a tree of video files in a folder
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
		# a tree of events
		self.eventTree = ttk.Treeview(self.root)
		self.eventTree["columns"]=("one","two","three","four")
		self.eventTree.heading("one", text="Type")
		self.eventTree.heading("two", text="Frame")
		self.eventTree.heading("three", text="ms")

		#self.eventTree.bind("<Double-1>", self.event_tree_double_click)
		self.eventTree.bind("<ButtonRelease-1>", self.event_tree_single_click)
		# insert events
		#self.eventTree.insert("" , 0,    text="Line 1", values=("1A","1b"))
		self.eventTree.pack(padx=5, pady=10, side=tkinter.TOP)
		#self.eventTree.pack()
		# end event tree

		# video 
		height = 480
		width = 640
		image = np.zeros((height,width,3), np.uint8)
		image = Image.fromarray(image)
		image = ImageTk.PhotoImage(image)
		#self.videoPanel_isinit = False
		self.videoPanel = tkinter.Label(image=image)
		self.videoPanel.image = image
		self.videoPanel.pack(side=tkinter.TOP, padx=10, pady=10)

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
		self.stopEvent = threading.Event()
		self.thread = threading.Thread(target=self.videoLoop, args=())
		self.thread.start()

		# set a callback to handle when the window is closed
		self.root.wm_title("PiE Video Analysis")
		self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

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
		print('PhotoBoothApp.keyPress() pressed:', repr(event.char), 'frame:', frame, 'ms:', ms)
		
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
		
		# delete vent
		if theKey == 'd':
			print('keyPress() d will delete -->> not implemented')
			
	def addEvent(self, theKey, frame, ms):
		# events have 

		# todo: switch this to internal data structure, DO NOT query actual list
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
			while not self.stopEvent.is_set():
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
						
			print('PhotoBoothApp.videoLoop() exited while')
			 
		except (RuntimeError) as e:
			print("my exception in PhotoBoothApp.videoLoop()")
			raise
 		
	def onClose(self):
		# set the stop event, cleanup the camera, and allow the rest of
		# the quit process to continue
		print("onClose()")
		self.stopEvent.set()
		print('1')
		self.vs.stop()
		print('2')
		self.root.quit()
	
##################################################################################
class FileVideoStream:
	def __init__(self, path, queueSize=128):
		# initialize the file video stream along with the boolean
		# used to indicate if the thread should be stopped or not
		self.stream = cv2.VideoCapture(path)
		self.stopped = False

		self.streamParams = {}
		self.streamParams['path'] = path
		self.streamParams['fileName'] = os.path.basename(path)
		self.streamParams['width'] = self.stream.get(cv2.CAP_PROP_FRAME_WIDTH)
		self.streamParams['height'] = self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)
		self.streamParams['fps'] = self.stream.get(cv2.CAP_PROP_FPS)
		self.streamParams['numFrames'] = int(self.stream.get(cv2.CAP_PROP_FRAME_COUNT))
		
		print(path, self.streamParams)
		
		self.gotoFrame = None
		#self.clearQueue = False
		self.paused = False
		self.currentFrame = 0
		self.milliseconds = 0
 		
		# initialize the queue used to store frames read from
		# the video file
		self.Q = Queue(maxsize=queueSize)

	# start thread (call this after constructor)
	def start(self):
		# start a thread to read frames from the file video stream
		t = threading.Thread(target=self.update, args=())
		t.daemon = True
		t.start()
		return self
	
	# the actual thread function
	def update(self):
		# keep looping infinitely
		while not self.stopped:
			#time.sleep(0.05)
			# if the thread indicator variable is set, stop the thread
			if self.stopped:
				return
 
			if self.gotoFrame is not None:
				#print('update gotoFrame:', self.gotoFrame)
				self.stream.set(cv2.CAP_PROP_POS_FRAMES, self.gotoFrame)
				if self.paused:
					self.Q.queue.clear()
					(grabbed, frame) = self.stream.read()
					self.currentFrame = self.stream.get(cv2.CAP_PROP_POS_FRAMES)
					self.milliseconds = round(self.stream.get(cv2.CAP_PROP_POS_MSEC),2)
					self.Q.put(frame)
				else:
					self.Q.queue.clear()
				self.gotoFrame = None
				
			#if self.clearQueue:
			#	self.Q.queue.clear()
			#	self.clearQueue = False

			# otherwise, ensure the queue has room in it
			if self.paused:
				pass
			else:
				if not self.Q.full():
					# read the next frame from the file
					(grabbed, frame) = self.stream.read()
					self.currentFrame = self.stream.get(cv2.CAP_PROP_POS_FRAMES)
					self.milliseconds = round(self.stream.get(cv2.CAP_PROP_POS_MSEC),2)
					
					# if the `grabbed` boolean is `False`, then we have
					# reached the end of the video file
					if not grabbed:
						self.stop()
						return
 
					# add the frame to the queue
					self.Q.put(frame)
		print('FileVideoStream.update() exited while loop')
		# this causes fault ???
		#self.stream.release()
		
	def read(self):
		# return next frame in the queue
		#return self.Q.get()
		try:
			ret = self.Q.get(block=True, timeout=2.0)
		except:
			print('my exception in FileVideoStream.read()')
			ret = None
		return ret #self.Q.get(block=True, timeout=2.0)
		
	def more(self):
		# return True if there are still frames in the queue
		#return self.Q.qsize() > 0
		return not self.stopped
		
	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True

	def setFrame(self, newFrame):
		if newFrame<0 or newFrame>self.streamParams['numFrames']-1:
			# error
			print('setFrame() error:', newFrame)
		else:
			#print('setFrame() newFrame:', newFrame)
			self.gotoFrame = newFrame
			time.sleep(0.1)
		return self.read()

	def frameOffset(self, frameOffset):
		newFrame = self.currentFrame + frameOffset
		if newFrame<0 or newFrame>self.streamParams['numFrames']-1:
			# error
			print('frameOffset error:', newFrame)
		else:
			print('newFrame:', newFrame)
			self.gotoFrame = newFrame
			time.sleep(0.1)
			"""
			self.currentFrame = newFrame
			self.stream.set(cv2.CAP_PROP_POS_FRAMES, self.currentFrame)
			self.milliseconds = round(self.stream.get(cv2.CAP_PROP_POS_MSEC),2)
			if self.paused:
				self.clearQueue = True
				(grabbed, frame) = self.stream.read()
				self.Q.put(frame)
			else:
				#self.Q.queue.clear()
				self.clearQueue = True
				while self.Q.qsize() == 0:
					pass # let the queu start to fill again
			"""
		return self.read()
		
##################################################################################
# Main
##################################################################################

videoPath = '/Users/cudmore/Dropbox/PiE/homecage-movie.mp4'

fvs = FileVideoStream(videoPath) #.start()
fvs.start()

pba = PhotoBoothApp(fvs)

# this still blocks, any updates to tk slider blocks video thread?
pba.root.after(500, pba.myUpdate)

pba.root.mainloop()
# 2)
"""
while True:
	pba.root.update_idletasks()
	pba.root.update()
	#time.sleep(0.01)
"""
    
"""
play = True
gotNewFrame = False # use this to only overlay text on new frame

while fvs.more():
	gotNewFrame = False
	
	key = cv2.waitKey(1) & 0xff
	keyStr = chr(key)
	
	if keyStr == 'q':
		break
	if keyStr == 'p' or keyStr == ' ':
		play = not play
		print('play' if play else 'pause')
		fvs.paused = not play
	# rewind is 'z'
	if keyStr == 'z':
		frame = fvs.frameOffset(-300)
		gotNewFrame = True
	# forward is 'x'
	if keyStr == 'x':
		frame = fvs.frameOffset(+300)
		gotNewFrame = True
		
	# grab the frame from the threaded video file stream, resize
	# it, and convert it to grayscale (while still retaining 3
	# channels)
	if play:
		frame = fvs.read()
		gotNewFrame = True
	#frame = imutils.resize(frame, width=450)
	#frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	#frame = np.dstack([frame, frame, frame])
 
	# display the size of the queue on the frame
	if gotNewFrame and frame is not None:
		cv2.putText(frame, "Queue Size: {}".format(fvs.Q.qsize()),
			(10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)	
		cv2.putText(frame, "Frame Number: {currentFrame}/{numFrames}".format(currentFrame=fvs.currentFrame, numFrames=fvs.streamParams['numFrames']),
			(10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)	
		cv2.putText(frame, "ms: {ms}".format(ms=fvs.milliseconds),
			(10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)	
 
	# show the frame and update the FPS counter
	if frame is not None:
		cv2.imshow("myVideoWindow", frame)
	#cv2.waitKey(1)
	#fps.update()

cv2.destroyAllWindows()
fvs.stop()
"""

