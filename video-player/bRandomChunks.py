# Author: Robert Cudmore
# Date: 20181116

"""
Break each video file into numChunks = floor(numFrames / chunkInterval)

Randomly select chunksPerFile without replacement

"""

import math
import numpy as np

import bVideoList

class bRandomChunks:
	def __init__(self, path):
		"""
		path: (str) path to folder with video files
		"""
		self.videoList = bVideoList.bVideoList(path)
		
	def generate(self, chunkInterval, chunksPerFile):
		"""
		chunkInterval: Number of frames in each chunk
		chunksPerFile:
		"""
		for videoFile in self.videoList.videoFileList:
			#print(file.asString())
			file = videoFile.dict['file']
			numFrames = videoFile.dict['numFrames']
			numChunks = math.floor(numFrames / chunkInterval)
			print(file, 'numFrames:', numFrames, 'numChunks:', numChunks)
			
			# make a list of start frame of each of the numChunks chunks
			
			# randomly select chunksPerFile without replacement
			r = np.random.choice(range(numChunks), chunksPerFile, replace=False)
			print(r)
			
			# now we know the chunks, get the start frame of each selected chunk
			
			# maybe also tally the start AND stop frame of each random chunk
			
			# 2) we need to RANDOMLY iterate through all selected chunks in all files
			
if __name__ == '__main__':
	path = '/Users/cudmore/Dropbox/PiE/video'
	chunks = bRandomChunks(path)
	
	chunkInterval = 10 #frames
	chunksPerFile = 5
	chunks.generate(chunkInterval, chunksPerFile)
		


	
