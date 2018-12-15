# Author: Robert Cudmore
# Date: 20181116

"""
Break each video file into numChunks = floor(numFrames / chunkIntervalSeconds)

Randomly select chunksPerFile without replacement

todo: Add parameters used when saving json

"""

import os, time, math, json
import datetime
from collections import OrderedDict 
from pprint import pprint
from random import shuffle

import numpy as np

import bVideoList

class bChunk:
	def __init__(self, path):
		"""
		path: (str) path to folder with video files
		"""
		self.path = path
		self.videoList = bVideoList.bVideoList(path)
		
	def generate(self, pieceDurationSeconds, chunkDurationSeconds, chunksPerFile):
		"""
		pieceDurationSeconds (int): Duration of each piece
			Each file is split into a number of pieces to evenly distribute the random chunk selection
		chunkDurationSeconds (int): Number of seconds in each chunk
		chunksPerFile:
		"""
		
		"""
		After speaking to Jessie 20181121
		Add another layer to random selection
		- files will be 30 min long
		- split each file into a number of 'big chunks' or parts, 10 min each
		- distribute the number we are going to select evenly across each 'big chunk'
		- e.g. for a 30 min file, make 3x 10 min 'big chunk'
		- randomly choose chunksPerFile/(num big chunk) for each of these big chunks
		
		The goal her is to ensure our random selection of chunksPerFile gets distributed 
		throughout the file
		"""
		totalChunkIndex = 0
		outChunkList = []
		outChunkOrder = [] # random order
		for videoFile in self.videoList.videoFileList:
			#print(file.asString())
			path = videoFile.dict['path']
			file = videoFile.dict['file']
			fps = videoFile.dict['fps']
			numFrames = videoFile.dict['frames']
			
			print('    path:', path)
			print('    file:', file)
			print('    fps:', fps)
			print('    numFrames:', numFrames)
			
			pieceDurationFrame = math.floor(pieceDurationSeconds * fps)
			numPiecesInFile = math.floor(numFrames / pieceDurationFrame) # constrain to integer
			
			if numPiecesInFile < 1:
				# error
				print('ERROR: bChunk.generate() numPiecesInFile:', numPiecesInFile)
				
			chunkDurationFrames = math.floor(chunkDurationSeconds * fps) # constrain to integer
			numChunksInFile = math.floor(numFrames / chunkDurationFrames) # constrain to integer

			# for each piece, randomly choose (without replacement) chunksPerPiece
			numChunksPerPiece = math.floor(numChunksInFile / numPiecesInFile) # total # of chunks per piece
			chooseNumChunksPerPiece = math.floor(chunksPerFile / numPiecesInFile)
			
			# todo: expand outChunkList so we can insert in order using outChunkList[i]
			#		make sure outChunkOrder still works
			
			print('file:', file)
			print('   input:pieceDurationSeconds', pieceDurationSeconds)
			print('   input:chunkDurationSeconds', chunkDurationSeconds)
			print('   input:chunksPerFile', chunksPerFile)
			print('   numFrames:', numFrames)
			print('   fps:', fps)
			print('   pieceDurationFrame:', pieceDurationFrame)
			print('   numPiecesInFile:', numPiecesInFile)
			print('   chunkDurationFrames:', chunkDurationFrames)
			print('   numChunksInFile:', numChunksInFile)
			print('   numChunksPerPiece:', numChunksPerPiece) # total number of chunks in each piece
			print('   chooseNumChunksPerPiece:', chooseNumChunksPerPiece)
			
			for pieceIdx in range(numPiecesInFile):
				# chooseNumChunksPerPiece can not be more than numChunksPerPiece
				randomChunksInPiece = np.random.choice(range(numChunksPerPiece), chooseNumChunksPerPiece, replace=False)
				for chunkIdx in randomChunksInPiece:
					newEntry = OrderedDict()
					#newEntry['randomIndex'] = xxx # assigned below
					newEntry['index'] = totalChunkIndex
					newEntry['path'] = path
					newEntry['piece'] = pieceIdx
					startFrame = int((pieceIdx * pieceDurationFrame) + (chunkIdx * chunkDurationFrames))
					newEntry['startFrame'] = startFrame
					newEntry['stopFrame'] = startFrame + chunkDurationFrames - 1
					newEntry['numFrames'] = chunkDurationFrames
					#print('newEntry:', newEntry)

					outChunkList.append(newEntry)

					# 2) we need to RANDOMLY iterate through all selected chunks in all files
					outChunkOrder.append(totalChunkIndex)

					totalChunkIndex += 1 # across all files		
				
			# make a list of start frame of each of the numChunksInFile chunks
			
			# randomly select chunksPerFile without replacement
			# r is a list of chunk number
			
			#print('generated', totalChunkIndex, 'total chunks')
		
		# randomize outChunkOrder
		shuffle(outChunkOrder)
		
		# mark each original chunk with its position in random sort order
		for idx, randomIndex in enumerate(outChunkOrder):
			print(idx, randomIndex)
			outChunkList[randomIndex]['randomIndex'] = idx
			
		# save the results
		now = datetime.datetime.now()
		timeStampStr = now.strftime('%Y%m%d_%H%M%S')

		# params
		params = {
			'generated': timeStampStr,
			'pieceDurationSeconds': pieceDurationSeconds,
			'chunkDurationSeconds': chunkDurationSeconds,
			'chunksPerFile': chunksPerFile
		}
		
		# package params, chunk list and chunk order into a dict
		outDict = {'params':params, 'chunks':outChunkList, 'chunkOrder':outChunkOrder}
		
		dateTimeFile = "chunks_" + now.strftime("%Y%m%d_%H%M%S.txt")
		outFilePath = os.path.join(self.path, dateTimeFile)
		print('writing file:', outFilePath)
		with open(outFilePath, 'w') as outfile:
			json.dump(outDict, outfile, indent=4, sort_keys=True)
	
		return outFilePath
		
	def load(self, path=''):
		with open(path) as f:
			data = json.load(f)
		#pprint(data)
		# data is a dict of {'chunks', 'chunkOrder'}
		
if __name__ == '__main__':
	path = '/Users/cudmore/Dropbox/PiE/video'
	path = '/Users/cudmore/Dropbox/PiE/scrambled'
	chunks = bChunk(path)
	
	# pieces is 10 min
	# chunk duration is 10 seconds
	# chunksPerVideo is 30
	
	pieceDurationSeconds = 10 * 60 # seconds
	chunkDurationSeconds = 10 # seconds
	chunksPerFile = 30
	outFile = chunks.generate(pieceDurationSeconds, chunkDurationSeconds, chunksPerFile)
		
	#chunks.load(path=path + '/' + 'chunks_20184319_221111.txt')


	
