# Author: Robert Cudmore
# Date: 20181101

"""
Continually stream a video from a file using OpenCV
"""

import os, time
from queue import Queue
import threading

import cv2
from PIL import Image

class FileVideoStream:
	def __init__(self, path, paused=False, gotoFrame=None, queueSize=256):
		print('FileVideoStream() path:', path, 'paused:', paused, 'gotoFrame:', gotoFrame, 'queueSize:', queueSize)
		
		self.switchingStream = False
		self.stream = None
		
		# initialize the queue used to store frames read from the video file
		self.Q = Queue(maxsize=queueSize)

		#print('   calling switchStream')
		self.switchStream(path, paused, gotoFrame)
		
		"""
		self.stream = cv2.VideoCapture(path)
			
		self.streamParams = {}
		if not self.isOpened:
			#print('   DID NOT OPEN')
			self.streamParams['path'] = ''
			self.streamParams['fileName'] = ''
			self.streamParams['width'] = None
			self.streamParams['height'] = None
			self.streamParams['aspectRatio'] = None
			self.streamParams['fps'] = None
			self.streamParams['numFrames'] = None
			self.streamParams['numSeconds'] = None
		else:
			self.streamParams['path'] = path
			self.streamParams['fileName'] = os.path.basename(path)
			self.streamParams['width'] = self.stream.get(cv2.CAP_PROP_FRAME_WIDTH)
			self.streamParams['height'] = self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)
			self.streamParams['aspectRatio'] = round(self.streamParams['height'] / self.streamParams['width'],2)
			self.streamParams['fps'] = self.stream.get(cv2.CAP_PROP_FPS)
			self.streamParams['numFrames'] = int(self.stream.get(cv2.CAP_PROP_FRAME_COUNT))
			self.streamParams['numSeconds'] = round(self.streamParams['numFrames'] / self.streamParams['fps'],2)
		
		self.stopped = False
		self.gotoFrame = gotoFrame #None
		self.paused = paused #False
		self.currentFrame = 0
		self.milliseconds = 0
		self.seconds = 0
		# initialize the queue used to store frames read from the video file
		self.Q = Queue(maxsize=queueSize)
 		"""

		"""
		print('   calling start')
		self.start()
		print('   done calling start')
		"""
		
	def switchStream(self, path, paused=False, gotoFrame=None):
		#print('=== switchStream() path:', path, 'paused:', paused, 'gotoFrame:', gotoFrame)

		self.switchingStream = True
		
		if self.stream is not None:
			print('   self.stream.release()')
			self.stream.release()
		
		self.stream = cv2.VideoCapture(path)
			
		self.streamParams = {}
		if not self.isOpened:
			print('   DID NOT OPEN')
			self.streamParams['path'] = ''
			self.streamParams['fileName'] = ''
			self.streamParams['width'] = None
			self.streamParams['height'] = None
			self.streamParams['aspectRatio'] = None
			self.streamParams['fps'] = None
			self.streamParams['numFrames'] = None
			self.streamParams['numSeconds'] = None
		else:
			self.streamParams['path'] = path
			self.streamParams['fileName'] = os.path.basename(path)
			self.streamParams['width'] = self.stream.get(cv2.CAP_PROP_FRAME_WIDTH)
			self.streamParams['height'] = self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)
			self.streamParams['aspectRatio'] = round(self.streamParams['height'] / self.streamParams['width'],2)
			self.streamParams['fps'] = self.stream.get(cv2.CAP_PROP_FPS)
			self.streamParams['numFrames'] = int(self.stream.get(cv2.CAP_PROP_FRAME_COUNT))
			self.streamParams['numSeconds'] = round(self.streamParams['numFrames'] / self.streamParams['fps'],2)
		
		self.stopped = False
		self.gotoFrame = None #None
		self.paused = paused
		self.currentFrame = 0
		self.milliseconds = 0
		self.seconds = 0

		with self.Q.mutex:
			self.Q.queue.clear()

		self.switchingStream = False

		self.gotoFrame = gotoFrame

	@property
	def isOpened(self):
		return self.stream.isOpened()
		
	# start thread (call this after constructor)
	def start(self):
		# start a thread to read frames from the file video stream
		t = threading.Thread(target=self.update, args=())
		t.daemon = True
		t.start()
		return self
	
	def stop(self):
		"""
		indicate that the thread should be stopped
		actual stopping is in main thread/loop in self.update()
		"""
		self.stopped = True

	# the actual thread function
	def update(self):

		while not self.stopped:
		
			time.sleep(0.001)
			
			if self.switchingStream:
				#print('   self.switchingStream:', self.switchingStream)
				continue
			
			if self.gotoFrame is not None:
				#print('~~~ FileVideoStream.update() gotoFrame:', self.gotoFrame, 'self.paused:', self.paused)
				#print('   setting stream CAP_PROP_POS_FRAMES to self.gotoFrame:', self.gotoFrame)
				self.stream.set(cv2.CAP_PROP_POS_FRAMES, self.gotoFrame)
				self.gotoFrame = None
				if self.paused:
					#print('   FileVideoStream.update() going to frame when paused')
					#print("      self.streamParams['path']:", self.streamParams['path'])
					self.currentFrame = int(self.stream.get(cv2.CAP_PROP_POS_FRAMES))
					self.milliseconds = round(self.stream.get(cv2.CAP_PROP_POS_MSEC),2)
					self.seconds = round(self.stream.get(cv2.CAP_PROP_POS_MSEC)/1000,2)
					#print('      self.currentFrame:', self.currentFrame)
					try:
						#print('FileVideoStream.update() gotoFrame is clearing queue when paused')
						with self.Q.mutex:
							self.Q.queue.clear()
						(grabbed, frame) = self.stream.read()
						#print('      grabbed:', grabbed)
					except:
						print('xxx yyy')
					"""
					self.currentFrame = int(self.stream.get(cv2.CAP_PROP_POS_FRAMES))
					self.milliseconds = round(self.stream.get(cv2.CAP_PROP_POS_MSEC),2)
					self.seconds = round(self.stream.get(cv2.CAP_PROP_POS_MSEC)/1000,2)
					print('   self.currentFrame:', self.currentFrame)
					"""
					self.Q.put([frame, self.currentFrame, self.seconds])
					#print('FileVideoStream.update() self.Q.put(frame) done')
				else:
					#print('FileVideoStream.update() gotoFrame is clearing queue when playing')
					#print('   going to frame when playing')
					with self.Q.mutex:
						self.Q.queue.clear()
				
			# otherwise, ensure the queue has room in it
			if self.paused:
				pass
			else:
				if not self.Q.full():
					self.currentFrame = int(self.stream.get(cv2.CAP_PROP_POS_FRAMES))
					self.milliseconds = round(self.stream.get(cv2.CAP_PROP_POS_MSEC),2)
					self.seconds = round(self.stream.get(cv2.CAP_PROP_POS_MSEC)/1000,2)

					# read the next frame from the file
					(grabbed, frame) = self.stream.read()

					"""
					self.currentFrame = int(self.stream.get(cv2.CAP_PROP_POS_FRAMES))
					self.milliseconds = round(self.stream.get(cv2.CAP_PROP_POS_MSEC),2)
					self.seconds = round(self.stream.get(cv2.CAP_PROP_POS_MSEC)/1000,2)
					"""
					
					# if the `grabbed` boolean is `False`, then we have
					# reached the end of the video file
					if grabbed:
						# add the frame to the queue
						self.Q.put([frame, self.currentFrame, self.seconds])
					else:
						#self.stop()
						#return
 						pass
 						
		print('FileVideoStream.update() exited while loop')
		# this causes fault ???
		#self.stream.release()
		
	def read(self):
		# return next frame in the queue
		#return self.Q.get()
		try:
			if self.Q.qsize() == 0:
				#print('FileVideoStream.read() self.Q.qsize():', self.Q.qsize())
				pass
			ret = self.Q.get(block=True, timeout=2.0)			
			#ret = self.Q.get()
		except:
			print('my exception in FileVideoStream.read()')
			ret = [None, None, None]
		#print('FileVideoStream.read() done')
		return ret #self.Q.get(block=True, timeout=2.0)
		
	def more(self):
		# return True if there are still frames in the queue
		#return self.Q.qsize() > 0
		return not self.stopped
		
	def playPause(self, doThis=None):
		if doThis is not None:
			if doThis == 'play':
				self.paused = False
			elif doThis == 'pause':
				self.paused = True
		else:
			# toggle
			self.paused = not self.paused
		#self.pausedAtFrame = self.currentFrame
		print('FileVideoStream.playPause()', 'pause' if self.paused else 'play')
		
	def setFrame(self, newFrame):
		#print('FileVideoStream.setFrame() newFrame:', newFrame)
		if not self.isOpened:
			print('error: setFrame() file is not open')
			return False
		
		newFrame = int(float(newFrame))
		if newFrame<0:
			# error
			print('FileVideoStream.setFrame() error, newFrame:', newFrame)
		elif newFrame > (self.streamParams['numFrames']-1):
			print('FileVideoStream.setFrame() error, newFrame:', newFrame, 'is beyond end of video frame:', self.streamParams['numFrames']-1)
		else:
			#print('   setting self.gotoFrame = ', self.gotoFrame)
			self.gotoFrame = newFrame
		return True

	def getParam(self, param):
		return self.streamParams[param]
		
	def getFrameFromSeconds(self, seconds):
		if not self.isOpened:
			print('error: getFrameFromSeconds() file is not open')
			return None
		theFrame = int(float(seconds * self.streamParams['fps']))
		if theFrame > self.streamParams['numFrames']:
			theFrame = self.streamParams['numFrames'] - 1
		return theFrame
		
	def getSecondsFromFrame(self, frame):
		if not self.isOpened:
			print('error: getSecondsFromFrame() file is not open')
			return None
		theSeconds = round(int(float(frame)) / self.streamParams['fps'],2)
		return theSeconds
		
if __name__ == '__main__':

	videoPath = '/Users/cudmore/Dropbox/PiE/video/1-homecage-movie.mp4'
	paused = True
	gotoFrame = 100
	vs = FileVideoStream(videoPath, paused, gotoFrame)
	
	print('fps:', vs.streamParams['fps'], 'gives frame interval (sec) of', 1/vs.streamParams['fps'])
	print('second 2 is at frame:', vs.getFrameFromSeconds(2))
	print('frame 2 is at seconds:', vs.getSecondsFromFrame(2))
	
	
	