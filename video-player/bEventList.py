# Author: Robert Cudmore
# Date: 20181101

"""
Manager a list of events. Each list is associated with one video file.
Each event denotes a position in the video file.
"""

import os
import numpy as np

class bEventList:
	def __init__(self,videoFilePath):
		# check that videoFilePath exists
		if not os.path.isfile(videoFilePath):
			print('error: bEvenList() did not find video file path:', videoFilePath)
			return 0
			
		self.videoFilePath = videoFilePath

		self.eventList = []
		
		# populate from txt file
		videoDirName = os.path.dirname(videoFilePath)
		videoFileName = os.path.basename(videoFilePath)
		
		textFileName = videoFileName.split('.')[0] + '.txt'
		self.textFilePath = os.path.join(videoDirName, textFileName)
		
		self.load()
		
	def load(self):
		"""Load list of events from text file"""
		if os.path.isfile(self.textFilePath):
			print('bEventList.load():', self.textFilePath)
			
			#data=np.loadtxt(textFilePath, skiprows=1, delimiter=',')

			with open(self.textFilePath, 'r') as file:
				# header
				headerStr = file.readline()
				# columns
				colStr = file.readline()
				# body
				for line in file:
					path, type, frameNumber, ms, note = line.split(',')
					event = bEvent(path, type, frameNumber,ms, note=note)
					self.eventList.append(event)
		
	def save(self):
		"""Save list of events to text file"""
		print('bEventList.save():', self.textFilePath)
		eol = '\n'
		with open(self.textFilePath, 'w') as file:
			# header
			file.write('#' + eol)
			# column headers
			colStr = 'video_path,type,framenumber,ms,note'
			file.write(colStr + eol)
			# one line per event
			for event in self.eventList:
				eventStr = event.asString()
				file.write(eventStr + eol)
		
	def getEvent(self, idx):
		return self.eventList[idx]
		
	def AppendEvent(self, type, frame, ms, autoSave=False):
		"""
		type: in (1,2,3,4,5)
		frame: frame number into video
		ms: millisconds (ms) into video (REDUNDANT)
		"""
		event = bEvent(self.videoFilePath, type, frame, ms)
		self.eventList.append(event)
		
		if autoSave:
			self.save()
			
class bEvent:
	def __init__(self, path, type, frameNumber, ms, note=''):
		"""
		path: (str) path to video file
		type: (int)
		frameNumber: (int)
		ms: (int)
		note: (str)
		"""
		self.path = path
		self.type = type
		self.frameNumber = frameNumber
		self.ms = ms
		self.note = ''
		# videoFilePath
		# ms into video (from frameNumber)
		# cSeconds : creation
		# mSeconds : modification
		# note: str
	
	def setNote(self, note):
		self.note = note
		
	def asString(self):
		theRet = self.path + ',' + \
			str(self.type) + ',' + \
			str(self.frameNumber) + ',' + \
			str(self.ms) + ',' + \
			self.note
		return theRet
