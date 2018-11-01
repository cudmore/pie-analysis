# Author: Robert Cudmore
# Date: 20181101

"""
Continually stream a video from a file using OpenCV
"""

import os, time
from queue import Queue
import threading

import cv2

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
