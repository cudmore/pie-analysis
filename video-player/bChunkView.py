# Author: Robert Cudmore
# Date: 20181120

import os, json
import tkinter
from tkinter import ttk

class bChunkView:
	
	def __init__(self, app, random_chunks_frame):
		self.app = app
		self.random_chunks_frame = random_chunks_frame
		
		self.currentChunk = None
		self.chunkData = None # loaded from file, data is a dict of {'chunks', 'chunkOrder'}
		
		# insert into self.random_chunks_frame

		self.chunkFileLabel = ttk.Label(self.random_chunks_frame, width=11, anchor="w", text='File:')
		self.chunkFileLabel.grid(row=0, column=0)
	
		self.currentChunkLabel = ttk.Label(self.random_chunks_frame, width=11, anchor="w", text='')
		self.currentChunkLabel.grid(row=0, column=1)
	
		self.numChunksLabel = ttk.Label(self.random_chunks_frame, width=11, anchor="w", text='')
		self.numChunksLabel.grid(row=0, column=2)
	
		self.previousChunkButton = ttk.Button(self.random_chunks_frame, width=1, text="<", command=self.chunk_previous)
		self.previousChunkButton.grid(row=0, column=3)

		self.nextChunkButton = ttk.Button(self.random_chunks_frame, width=1, text=">", command=self.chunk_next)
		self.nextChunkButton.grid(row=0, column=4)

		self.gotoChunkButton = ttk.Button(self.random_chunks_frame, width=4, text="Go To", command=self.chunk_goto2)
		self.gotoChunkButton.grid(row=0, column=5)

		#self.gotoChunkEntry = ttk.Entry(self.random_chunks_frame, width=5)
		self.gotoChunkEntry = ttk.Spinbox(self.random_chunks_frame, width=5, from_=0, to=0)
		self.gotoChunkEntry.grid(row=0, column=6)
		self.gotoChunkEntry.insert(0, '0')
		
	def chunkInterface_populate(self, askForFile=False):
		"""
		Open a chunks file and populate interface
		"""
		self.currentChunk = 0

		print('chunkInterface_populate()')
		initialdir = self.app.videoList.path # get folder from video list
		defaultFile = 'randomChunks.txt' # look for default file in video folder
		filepath = os.path.join(initialdir,defaultFile)
		if os.path.isfile(filepath):
			pass	
		elif askForFile:
			filepath =  tkinter.filedialog.askopenfilename(initialdir = initialdir,title = "Select a random chunk file",filetypes = (("text files","*.txt"),("all files","*.*")))
		print('   filepath:', filepath)
		
		if not os.path.isfile(filepath):
			print('   did not find chunk file')
			return
		
		#chunkFile = bRandomChunks(filename).open()
		#print(chunkFile)
		with open(filepath) as f:
			self.chunkData = json.load(f) # data is a dict of {'chunks', 'chunkOrder'}
				
		# interface
		self.chunkFileLabel['text'] = os.path.basename(filepath)
		self.chunkFileLabel['width'] = len(os.path.basename(filepath))
		
		self.currentChunkLabel['text'] = str(self.currentChunk)
		self.numChunksLabel['text'] = 'of ' + str(self.numChunks)
		
		self.gotoChunkEntry['to'] = self.numChunks - 1
		
	def chunk_previous(self):
		print('chunk_previous()')
		self.currentChunk -= 1
		if self.currentChunk < 0:
			self.currentChunk = 0
		self.chunk_goto(self.currentChunk)
		
	def chunk_next(self):
		#print('chunk_next()')
		self.currentChunk += 1
		if self.currentChunk > self.numChunks:
			self.currentChunk = self.numChunks - 1
		self.chunk_goto(self.currentChunk)
		
	def chunk_goto2(self):
		# get value from gotoChunkEntry
		chunkNumber = int(self.gotoChunkEntry.get())
		self.chunk_goto(chunkNumber)
		
	def chunk_goto(self, chunkNumber):
		print('chunk_goto() chunkNumber:', chunkNumber)
		
		# check valid chunkNumber
		if chunkNumber > self.numChunks-1:
			print('chunk_goto() error')
			return
			
		self.currentChunk = chunkNumber
		
		actualChunkNumber = self.chunkData['chunkOrder'][chunkNumber]
		chunk = self.chunkData['chunks'][actualChunkNumber]
		
		path = chunk['path']
		startFrame = chunk['startFrame']
		stopFrame = chunk['stopFrame']
		
		print('   path:', path)
		print('   startFrame:', startFrame)
		print('   stopFrame:', stopFrame)
		
		self.app.switchvideo(path, paused=True, gotoFrame=startFrame)
		
		self.app.setFrame(startFrame)

		self.app.hijackInterface(chunk)
		
		# update chunk interface
		self.currentChunkLabel['text'] = str(chunkNumber)
		
	@property
	def numChunks(self):
		return len(self.chunkData['chunkOrder'])
