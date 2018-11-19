# Author: Robert Cudmore
# Date: 20181116

"""
Manager a list of video files
"""

import os
from collections import OrderedDict 

import cv2

gVideoFileColumns = ('index', 'path', 'file', 'width', 'height', 'frames', 'fps', 'seconds')

#############################################################
class bVideoList:

	def __init__(self, path):
		"""
		path: path to folder with .mp4 files
		"""
		
		self.videoFileList = []

		self.populateFolder(path)
		
	def populateFolder(self, path):
		"""
		populate with list of .mp4 files in a folder specified by path
		"""
		useExtension = '.mp4'
		videoFileIdx = 0
		for file in os.listdir(path):
			if file.endswith(useExtension):
				fullPath = os.path.join(path, file)
				newVideoFile = bVideoFile(videoFileIdx, fullPath)
				self.videoFileList.append(newVideoFile)
				videoFileIdx += 1
		
	def getColumns(self):
		return gVideoFileColumns

	def getList(self):
		return self.videoFileList
	
#############################################################
class bVideoFile:

	def __init__(self, index, path):
		"""
		path: (str) full path to .mp4 video file
		"""
		
		if not os.path.isfile(path):
			print('error: bVideoFile() could not open file path:', path)
			return
			
		# open file using cv2
		myFile = cv2.VideoCapture(path)

		if not myFile.isOpened(): 
			print('error: bVideoFile() found file but could not open it:', path)
			return

		filename = os.path.basename(path)
		
		self.dict = OrderedDict()
		self.dict['index'] = index
		self.dict['path'] = path
		self.dict['file'] = filename
		
		self.dict['width'] = int(myFile.get(cv2.CAP_PROP_FRAME_WIDTH))
		self.dict['height'] = int(myFile.get(cv2.CAP_PROP_FRAME_HEIGHT))
		self.dict['frames'] = int(myFile.get(cv2.CAP_PROP_FRAME_COUNT))
		self.dict['fps'] = int(myFile.get(cv2.CAP_PROP_FPS))
		self.dict['seconds'] = round(self.dict['frames'] / self.dict['fps'],2)
		
		cv2.VideoCapture.release(myFile)
		
	def asString(self):
		theRet = ''
		for i, (k,v) in enumerate(self.dict.items()):
			theRet += str(v) + ','
		return theRet
				
	def asTuple(self):
		str = self.asString()
		strList = []
		for s in str.split(','):
			strList.append(s)
		retTuple = tuple(strList)
		return retTuple
	
if __name__ == '__main__':
	videoPath = '/Users/cudmore/Dropbox/PiE/homecage-movie.mp4'
	videoPath = '/Users/cudmore/Dropbox/PiE/'
	myList = bVideoList(videoPath)
	
	for videoFile in myList.getList():
		print(videoFile.asString())
		