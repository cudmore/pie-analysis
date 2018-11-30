# Author: Robert Cudmore
# Date: 20181101

"""
Manager a list of events. Each list is associated with one video file.
Each event denotes a position in the video file.
"""

import os, time
import numpy as np
from collections import OrderedDict 

#import FileVideoStream

gEventColumns = ('index', 'path', 'cSeconds', 'cDate', 'cTime', 
				'typeNum', 'typeStr', 'frameStart', 'frameStop', 
				'numFrames', 'sStart', 'sStop', 'numSeconds',
				'chunkIndex', 'note')

class bEventList:
	def __init__(self, parentApp, videoFilePath):
		
		"""
		# check that videoFilePath exists
		if not os.path.isfile(videoFilePath):
			print('error: bEvenList() did not find video file path:', videoFilePath)
			return 0
		"""
			
		#print('bEventList() videoFilePath:', videoFilePath)
		
		self.parentApp = parentApp
		self.videoFilePath = videoFilePath

		self.eventList = []
		
		self.videoFileNote = ''
		
		# populate from txt file
		if os.path.isfile(videoFilePath):
			videoDirName = os.path.dirname(videoFilePath)
			videoFileName = os.path.basename(videoFilePath)
		
			textFileName = videoFileName.split('.')[0] + '.txt'
			self.textFilePath = os.path.join(videoDirName, textFileName)
		
			#vs = FileVideoStream.FileVideoStream(videoFilePath)
			#self.streamParams = vs.streamParams
			self.streamParams = self.parentApp.vs.streamParams
			self.load()

		
	@property
	def numEvents(self):
		return len(self.eventList)
		
	def getColumns(self):
		return gEventColumns
	
	def set(self, index, col, val):
		print('bEventList.set() index:', index, 'col:', col, 'val:', val)
		
		self.eventList[index].dict[col] = val
		
		# update seconds
		if col == 'frameStart':
			frameStart = self.get(index, 'frameStart')
			sStart = self.parentApp.vs.getSecondsFromFrame(frameStart)
			#print('   sStart:', sStart)
			self.eventList[index].dict['sStart'] = sStart
		if col == 'frameStop':
			frameStop = self.get(index, 'frameStop')
			sStop = self.parentApp.vs.getSecondsFromFrame(frameStop)
			#print('   sStop:', sStop)
			self.eventList[index].dict['sStop'] = sStop
			
		# update durations
		frameStart = self.get(index, 'frameStart')
		frameStop = self.get(index, 'frameStop')
		#print('frameStart:', type(frameStart), 'frameStop:', type(frameStop))
		if (frameStart is not None) and (frameStop is not None):
			numFrames = int(float(frameStop)) - int(float(frameStart)) - 1
			#print('   numFrames:', numFrames)
			self.eventList[index].dict['numFrames'] = numFrames

		sStart = self.get(index, 'sStart')
		sStop = self.get(index, 'sStop')
		#print('sStart:', sStart, 'sStop:', sStop)
		if (sStart is not None) and (sStop is not None):
			numSeconds = round(float(sStop) - float(sStart),2)
			#print('   numSeconds:', numSeconds)
			self.eventList[index].dict['numSeconds'] = numSeconds

	def get(self, index, col):
		return self.eventList[index].dict[col]
		
	def load(self):
		"""Load list of events from text file"""
		if os.path.isfile(self.textFilePath):
			#print('bEventList.load():', self.textFilePath)
			with open(self.textFilePath, 'r') as file:
				# header
				commentLine = file.readline().strip()
				# columns
				headerLine = file.readline().strip()
				# body
				for eventLine in file:
					eventLine = eventLine.strip()
					if eventLine == '\n':
						pass
					#print('   eventLine:', eventLine)
					event = bEvent(self)
					event.fromFile(headerLine, eventLine)
					self.eventList.append(event)
		
	def save(self):
		"""Save list of events to text file"""
		print('bEventList.save():', self.textFilePath)
		eol = '\n'
		with open(self.textFilePath, 'w') as file:
			# header
			headerStr = ''
			for (k,v) in self.streamParams.items():
				headerStr += k + '=' + str(v) + ','
			headerStr += 'numEvents=' + str(self.numEvents) + ','
			headerStr += 'videoFileNote=' + self.videoFileNote + ','
			
			file.write(headerStr + eol)
			# column headers
			#print('   ', gEventColumns)
			for col in gEventColumns:
				file.write(col + ',')
			file.write(eol)
			# one line per event
			for event in self.eventList:
				eventStr = event.asString()
				#print('   ', eventStr)
				file.write(eventStr + eol)
		
	def asString(self):
		for event in self.eventList:
			print(event.asString)
	
	def getEvent(self, idx):
		return self.eventList[idx]
		
	def appendEvent(self, type, frame, chunkIndex=None, autoSave=False):
		"""
		type: in (1,2,3,4,5)
		frame: frame number into video
		"""
		idx = len(self.eventList)
		event = bEvent(self, idx, self.videoFilePath, type, frame, chunkIndex=chunkIndex)
		self.eventList.append(event)
		
		if autoSave:
			self.save()
		
		return event

class bEvent:
	def __init__(self, parentList, index='', path='', type='', frame='', chunkIndex=None):
		"""
		path: (str) path to video file
		type: (int)
		frameNumber: (int)
		ms: (int)
		note: (str)
		"""
		
		self.parentList = parentList # to get video parameters
		
		now = time.time()
		
		"""
		gEventColumns = ('index', 'path', 'cSeconds', 'cDate', 'cTime', 
				'typeNum', 'typeStr', 'frameStart', 'frameStop', 
				'numFrames', 'sStart', 'sStop', 'numSeconds'
				'chunkIndex', 'note')
		"""
		self.eventColumns = gEventColumns
		self.dict = OrderedDict()
		for column in self.eventColumns:
			self.dict[column] = None
		self.dict['index'] = index
		self.dict['path'] = path
		self.dict['cSeconds'] = now
		self.dict['cDate'] = time.strftime('%Y-%m-%d', time.localtime(now))
		self.dict['cTime'] = time.strftime('%H:%M:%S', time.localtime(now))
		self.dict['typeNum'] = type
		if type is not None and len(type) > 0:
			self.dict['typeStr'] = self.parentList.parentApp.getEventTypeStr(type)
		else:
			self.dict['typeStr'] = ''
		self.dict['frameStart'] = frame
		self.dict['frameStop'] = ''
		if frame == '':
			self.dict['sStart'] = ''
		else:
			self.dict['sStart'] = self.parentList.parentApp.vs.getSecondsFromFrame(frame)
		self.dict['chunkIndex'] = chunkIndex
		self.dict['note'] = ''
		
		"""
		self.streamParams['path'] = path
		self.streamParams['fileName'] = os.path.basename(path)
		self.streamParams['width'] = self.stream.get(cv2.CAP_PROP_FRAME_WIDTH)
		self.streamParams['height'] = self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)
		self.streamParams['aspectRatio'] = round(self.streamParams['height'] / self.streamParams['width'],2)
		self.streamParams['fps'] = self.stream.get(cv2.CAP_PROP_FPS)
		self.streamParams['numFrames'] = int(self.stream.get(cv2.CAP_PROP_FRAME_COUNT))
		self.streamParams['numSeconds'] = round(self.streamParams['numFrames'] / self.streamParams['fps'],2)
		"""
	def fromFile(self, headerLine, eventLine):
		"""
		Initialize a bEvent from one line in a text file
		"""
		colValues = eventLine.split(',')
		idx = 0
		for column in headerLine.split(','):
			self.dict[column] = colValues[idx]
			idx += 1
			
	def get(self, column):
		return self.dict[column]
	
	def setNote(self, note):
		self.dict['note'] = note
		
	def asString(self):
		theRet = ''
		for (k,v) in self.dict.items():
			theRet += str(v) + ','
		return theRet

	def asTuple(self):
		str = self.asString()
		strList = []
		for s in str.split(','):
			if s == 'None':
				strList.append('')
			else:
				strList.append(s)
		retTuple = tuple(strList)
		return retTuple
		
if __name__ == '__main__':
	videoPath = '/Users/cudmore/Dropbox/PiE/video/homecage-movie.mp4'
	eventList = bEventList(videoPath)
	eventList.appendEvent(type=1, frame=1)
	eventList.appendEvent(type=2, frame=10)
	eventList.appendEvent(type=3, frame=100)
	eventList.asString()
	eventList.save()
	
	