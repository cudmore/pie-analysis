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

##################################################################################
class FileVideoStream:
	def __init__(self, path, queueSize=256):
		self.stream = cv2.VideoCapture(path)
		self.stopped = False

		self.streamParams = {}
		self.streamParams['path'] = path
		self.streamParams['fileName'] = os.path.basename(path)
		self.streamParams['width'] = self.stream.get(cv2.CAP_PROP_FRAME_WIDTH)
		self.streamParams['height'] = self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)
		self.streamParams['fps'] = self.stream.get(cv2.CAP_PROP_FPS)
		self.streamParams['numFrames'] = int(self.stream.get(cv2.CAP_PROP_FRAME_COUNT))
		self.streamParams['numSeconds'] = round(self.streamParams['numFrames'] / self.streamParams['fps'],2)
		
		print('queueSize:', queueSize)
		print('path:', path)
		print('width:', self.streamParams['width'])
		print('height:', self.streamParams['height'])
		print('fps:', self.streamParams['fps'])
		print('numFrames:', self.streamParams['numFrames'])
		
		self.gotoFrame = None
		#self.clearQueue = False
		self.paused = False
		self.currentFrame = 0
		self.milliseconds = 0
		self.seconds = 0
 		
		# initialize the queue used to store frames read from
		# the video file
		self.Q = Queue(maxsize=queueSize)
		#self.Q = Queue(maxsize=self.streamParams['numFrames'])

	# start thread (call this after constructor)
	def start(self):
		# start a thread to read frames from the file video stream
		t = threading.Thread(target=self.update, args=())
		t.daemon = True
		t.start()
		return self
	
	# the actual thread function
	def update(self):

		while not self.stopped:
		
			time.sleep(0.001)
			
			# stop the thread
			#if self.stopped:
			#	return
 
			if self.gotoFrame is not None:
				#print('FileVideoStream.update() gotoFrame:', self.gotoFrame, 'self.paused:', self.paused)
				self.stream.set(cv2.CAP_PROP_POS_FRAMES, self.gotoFrame)
				if self.paused:
					try:
						with self.Q.mutex:
							self.Q.queue.clear()
						(grabbed, frame) = self.stream.read()
					except:
						print('xxx yyy')
					self.currentFrame = int(self.stream.get(cv2.CAP_PROP_POS_FRAMES))
					self.milliseconds = round(self.stream.get(cv2.CAP_PROP_POS_MSEC),2)
					self.seconds = round(self.stream.get(cv2.CAP_PROP_POS_MSEC)/1000,2)
					self.Q.put(frame)
					#print('FileVideoStream.update() self.Q.put(frame) done')
				else:
					with self.Q.mutex:
						self.Q.queue.clear()
				self.gotoFrame = None
				
			# otherwise, ensure the queue has room in it
			if self.paused:
				pass
			else:
				if not self.Q.full():
					# read the next frame from the file
					(grabbed, frame) = self.stream.read()

					#frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
					#frame = Image.fromarray(frame)

					self.currentFrame = int(self.stream.get(cv2.CAP_PROP_POS_FRAMES))
					self.milliseconds = round(self.stream.get(cv2.CAP_PROP_POS_MSEC),2)
					self.seconds = round(self.stream.get(cv2.CAP_PROP_POS_MSEC)/1000,2)
					
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
			if self.Q.qsize() == 0:
				print('FileVideoStream.read() self.Q.qsize():', self.Q.qsize())
			ret = self.Q.get(block=True, timeout=2.0)			
			#ret = self.Q.get()
		except:
			print('my exception in FileVideoStream.read()')
			ret = None
		#print('FileVideoStream.read() done')
		return ret #self.Q.get(block=True, timeout=2.0)
		
	def more(self):
		# return True if there are still frames in the queue
		#return self.Q.qsize() > 0
		return not self.stopped
		
	def stop(self):
		"""
		indicate that the thread should be stopped
		actual stopping is in main thread/loop in self.update()
		"""
		self.stopped = True

	def setFrame(self, newFrame):
		if newFrame<0 or newFrame>self.streamParams['numFrames']-1:
			# error
			print('setFrame() error:', newFrame)
		else:
			#print('FileVideoStream.setFrame() newFrame:', newFrame)
			self.gotoFrame = newFrame
		return True

