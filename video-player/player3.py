# import the necessary packages
import threading
import sys, time
import cv2
import tkinter
from PIL import Image
from PIL import ImageTk

from queue import Queue
	
class PhotoBoothApp:
	def __init__(self, vs):

		self.vs = vs
		self.frame = None
		self.thread = None
		self.stopEvent = None
 
		self.paused = False
 		
		# initialize the root window and image panel
		self.root = tkinter.Tk()
		self.panel = None
		
		# create a button, that when pressed, will take the current
		# frame and save it to file
		btn = tkinter.Button(self.root, text="Play/Pause",
			command=self.playPause)
		btn.pack(side="bottom", fill="both", expand="yes", padx=10, pady=10)

		frameSlider = tkinter.Scale(self.root, from_=0, to=2000, orient=tkinter.HORIZONTAL,
			command=self.gotoFrame)
		frameSlider.pack(side="bottom", fill="both", expand="yes", padx=10, pady=10)

		self.root.bind("<Key>", self.keyPress)

		# start a thread that constantly pools the video sensor for
		# the most recently read frame
		self.stopEvent = threading.Event()
		self.thread = threading.Thread(target=self.videoLoop, args=())
		self.thread.start()

		# set a callback to handle when the window is closed
		self.root.wm_title("PyImageSearch PhotoBooth")
		self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

	def videoLoop(self):
		# DISCLAIMER:
		# I'm not a GUI developer, nor do I even pretend to be. This
		# try/except statement is a pretty ugly hack to get around
		# a RunTime error that Tkinter throws due to threading
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
						pass
					else:
						self.frame = self.vs.read()
					#self.frame = imutils.resize(self.frame, width=300)
			
					# OpenCV represents images in BGR order; however PIL
					# represents images in RGB order, so we need to swap
					# the channels, then convert to PIL and ImageTk format
					image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
					image = Image.fromarray(image)
					image = ImageTk.PhotoImage(image)
		
					# if the panel is not None, we need to initialize it
					if self.panel is None:
						self.panel = tkinter.Label(image=image)
						self.panel.image = image
						self.panel.pack(side="left", padx=10, pady=10)
		
					# otherwise, simply update the panel
					else:
						self.panel.configure(image=image)
						self.panel.image = image
 
		except (RuntimeError) as e:
			print("[INFO] caught a RuntimeError")
 		
	def playPause(self):
		self.paused = not self.paused
		print('playPause()', 'pause' if self.paused else 'play')
		
	def gotoFrame(self, frameNumber):
		#frameNumber : str
		print('gotoFrame()', frameNumber)
		self.frame = self.vs.setFrame(int(frameNumber))

	def keyPress(self, event):
		frame = self.vs.stream.get(cv2.CAP_PROP_POS_FRAMES)
		ms = self.vs.stream.get(cv2.CAP_PROP_POS_MSEC)
		print('pressed:', repr(event.char), 'frame:', frame, 'ms:', ms)
		
	# Tkinter
	def onClose(self):
		# set the stop event, cleanup the camera, and allow the rest of
		# the quit process to continue
		print("onClose()")
		self.stopEvent.set()
		self.vs.stop()
		self.root.quit()
	
class FileVideoStream:
	def __init__(self, path, queueSize=128):
		# initialize the file video stream along with the boolean
		# used to indicate if the thread should be stopped or not
		self.stream = cv2.VideoCapture(path)

		self.streamParams = {}
		self.streamParams['width'] = self.stream.get(cv2.CAP_PROP_FRAME_WIDTH)
		self.streamParams['height'] = self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)
		self.streamParams['fps'] = self.stream.get(cv2.CAP_PROP_FPS)
		self.streamParams['numFrames'] = int(self.stream.get(cv2.CAP_PROP_FRAME_COUNT))
		
		self.stopped = False
 
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
		while True:
			time.sleep(0.05)
			# if the thread indicator variable is set, stop the thread
			if self.stopped:
				return
 
			if self.gotoFrame is not None:
				print('update gotoFrame:', self.gotoFrame)
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

	def read(self):
		# return next frame in the queue
		#return self.Q.get()
		try:
			ret = self.Q.get(block=True, timeout=2.0)
		except:
			print('exception in FileVideoStream.read()')
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
			print('setFrame() newFrame:', newFrame)
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
		
###
#cv2.namedWindow('myVideoWindow')

videoPath = '/Users/cudmore/Dropbox/PiE/homecage-movie.mp4'

fvs = FileVideoStream(videoPath).start()

pba = PhotoBoothApp(fvs)
pba.root.mainloop()

play = True
gotNewFrame = False # use this to only overlay text on new frame

"""
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

