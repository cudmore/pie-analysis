# Author: Robert Cudmore
# Date: 20181116

"""
Break each video file into numChunks = floor(numFrames / chunkInterval)

Randomly select chunksPerFile without replacement

"""

import os, time, math, json
import datetime
from collections import OrderedDict 
from pprint import pprint
from random import shuffle

import numpy as np

import bVideoList

class bRandomChunks:
	def __init__(self, path):
		"""
		path: (str) path to folder with video files
		"""
		self.path = path
		self.videoList = bVideoList.bVideoList(path)
		
	def generate(self, chunkInterval, chunksPerFile):
		"""
		chunkInterval: Number of frames in each chunk
		chunksPerFile:
		"""
		totalChunkIndex = 0
		outChunkList = []
		outChunkOrder = [] # random order
		for videoFile in self.videoList.videoFileList:
			#print(file.asString())
			path = videoFile.dict['path']
			file = videoFile.dict['file']
			numFrames = videoFile.dict['frames']
			numChunksInFile = math.floor(numFrames / chunkInterval)
			print(file, 'numFrames:', numFrames, 'numChunksInFile:', numChunksInFile)
			
			# make a list of start frame of each of the numChunksInFile chunks
			
			# randomly select chunksPerFile without replacement
			# r is a list of chunk number
			r = np.random.choice(range(numChunksInFile), chunksPerFile, replace=False)
			print(r)
			
			for i in r:
				newEntry = OrderedDict()
				newEntry['index'] = totalChunkIndex
				newEntry['path'] = path
				newEntry['startFrame'] = int(i * chunkInterval)
				newEntry['stopFrame'] = newEntry['startFrame'] + chunkInterval - 1
				newEntry['numFrames'] = chunkInterval
				#print('newEntry:', newEntry)
				outChunkList.append(newEntry)

				# 2) we need to RANDOMLY iterate through all selected chunks in all files
				outChunkOrder.append(totalChunkIndex)

				totalChunkIndex += 1			
			
		# randomize outChunkOrder
		shuffle(outChunkOrder)
		
		# package chunk list and chunk order into a dict
		outDict = {'chunks':outChunkList, 'chunkOrder':outChunkOrder}
		
		now = datetime.datetime.now()
		dateTimeFile = "chunks_" + now.strftime("%Y%m%d_%H%m%S.txt")
		outFilePath = os.path.join(self.path, dateTimeFile)
		print('writing file:', outFilePath)
		with open(outFilePath, 'w') as outfile:
			json.dump(outDict, outfile, indent=4, sort_keys=True)
    
	def load(self, path=''):
		with open(path) as f:
			data = json.load(f)
		pprint(data)
		# data is a dict of {'chunks', 'chunkOrder'}
if __name__ == '__main__':
	path = '/Users/cudmore/Dropbox/PiE/video'
	chunks = bRandomChunks(path)
	
	chunkInterval = 30 #frames
	chunksPerFile = 5
	chunks.generate(chunkInterval, chunksPerFile)
		
	chunks.load(path=path + '/' + 'chunks_20184319_221111.txt')


	
