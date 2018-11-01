# Author: Robert Cudmore
# Date: 20181101

"""
Manager a list of events. Each list is associated with one video file. Each event denotes a position in the video file.
"""

class bEventList:
	def __init__(self,videoFilePath):
		# check that videoFilePath exists
		
		self.eventList = []
		
	def load(self):
		"""Load list of events from text file"""
		pass
		
	def save(self):
		"""Save list of events to text file"""
		pass
		
	def getEvent(self, idx):
		return self.eventList[idx]
		
	def AppendEvent(self, type, frame, ms):
		"""
		type: in (1,2,3,4,5)
		frame: frame number into video
		ms: millisconds (ms) into video (REDUNDANT)
		"""
		event = bEvent(type, frame, ms)
		self.eventList.append(event)
		
class bEvent:
	def __init__(self, type, frameNumber, ms):
		self.type = type
		self.frameNumber = frameNumber
		self.ms = ms
		# videoFilePath
		# ms into video (from frameNumber)
		# cSeconds : creation
		# mSeconds : modification
		# note: str
		

