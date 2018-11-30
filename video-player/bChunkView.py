# Author: Robert Cudmore
# Date: 20181120

import os, time, json
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
	
		# previous chunk
		self.previousChunkButton = ttk.Button(self.random_chunks_frame, width=1, text="<", command=self.chunk_previous)
		self.previousChunkButton.grid(row=0, column=3)
		self.previousChunkButton.bind("<Key>", self.ignore)

		self.startOfChunkButton = ttk.Button(self.random_chunks_frame, width=1, text="|<", command=self.chunk_start)
		self.startOfChunkButton.grid(row=0, column=4)
		self.startOfChunkButton.bind("<Key>", self.ignore)

		# next chunk
		self.nextChunkButton = ttk.Button(self.random_chunks_frame, width=1, text=">", command=self.chunk_next)
		self.nextChunkButton.grid(row=0, column=5)
		self.nextChunkButton.bind("<Key>", self.ignore)
		
		self.gotoChunkButton = ttk.Button(self.random_chunks_frame, width=4, text="Go To", command=self.chunk_goto2)
		self.gotoChunkButton.grid(row=0, column=6)
		self.gotoChunkButton.bind("<Key>", self.ignore)

		#self.gotoChunkEntry = ttk.Entry(self.random_chunks_frame, width=5)
		self.gotoChunkEntry = ttk.Spinbox(self.random_chunks_frame, width=5, from_=0, to=0)
		self.gotoChunkEntry.grid(row=0, column=7)
		self.gotoChunkEntry.insert(0, '0')
		self.gotoChunkEntry.bind("<Key>", self.ignore)

		"""
		self.hijackControlsCheckbox_Value = tkinter.IntVar()
		self.hijackControlsCheckbox = ttk.Checkbutton(self.random_chunks_frame, text='Limit Controls', 
														command=self.checkbox_callback,
														variable=self.hijackControlsCheckbox_Value)
		"""
		self.hijackControlsCheckbox = ttk.Checkbutton(self.random_chunks_frame, text='Limit Controls', 
														command=self.checkbox_callback)
		#self.hijackControlsCheckbox.value = False
		self.hijackControlsCheckbox.state(['!alternate'])
		self.hijackControlsCheckbox.state(['!selected'])
		self.hijackControlsCheckbox.grid(row=1, column=0)
		self.hijackControlsCheckbox.bind("<Key>", self.ignore)
		
	def ignore(self, event):
		"""
		This function will take all key-presses (except \r) and pass to main app.
		return "break" is critical to stop propogation of event
		"""
		#print('bChunkView.ignore() event.char:', event.char)
		if event.char == '\r':
			pass
		else:
			self.app.keyPress(event)
			return 'break'

	def checkbox_callback(self):
		#print('self.hijackControlsCheckbox.state:', self.hijackControlsCheckbox.state)
		self.app.hijackInterface(self.isHijacking())

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
		
	def findChunk(self, path, startFrame):
		theIdx = None
		currIdx = 0
		for chunk in self.chunkData['chunks']:
			if chunk['path'] == path:
				if startFrame > chunk['startFrame'] and startFrame < chunk['stopFrame']:
					theIdx = currIdx
					break
				currIdx += 1
		return theIdx
				
	def chunk_previous(self):
		print('chunk_previous()')
		self.currentChunk -= 1
		if self.currentChunk < 0:
			self.currentChunk = 0
		self.chunk_goto(self.currentChunk)
		
	def chunk_start(self):
		""" Go to first frame in chunk"""
		#actualChunkNumber = self.chunkData['chunkOrder'][self.currentChunk]
		#currentChunk = self.chunkData['chunks'][actualChunkNumber]
		currentChunk = self.getCurrentChunk()
		startFrame = currentChunk['startFrame']
		print('chunk_start()')
		print('   index:', currentChunk['index'])
		print('   path:', currentChunk['path'])
		print('   startFrame:', startFrame)
		self.app.setFrame(startFrame, withDelay=True)
		
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
		
		#actualChunkNumber = self.chunkData['chunkOrder'][chunkNumber]
		#chunk = self.chunkData['chunks'][actualChunkNumber]
		chunk = self.getCurrentChunk()
		
		path = chunk['path']
		startFrame = chunk['startFrame']
		stopFrame = chunk['stopFrame']
		
		"""
		print('   path:', path)
		print('   startFrame:', startFrame)
		print('   stopFrame:', stopFrame)
		"""
		
		print('   calling self.app.switchvideo() gotoFrame:', startFrame)
		self.app.switchvideo(path, paused=True, gotoFrame=startFrame)
		
		#time.sleep(0.05)
		
		#self.app.setFrame(startFrame)

		#self.app.hijackInterface(self.hijackControlsCheckbox_Value.get() == 1)
		self.app.hijackInterface(self.isHijacking())
		
		# update chunk interface
		self.currentChunkLabel['text'] = str(self.currentChunk)
	
	def isHijacking(self):
		#return self.hijackControlsCheckbox_Value.get() == 1
		return self.hijackControlsCheckbox.instate(['selected'])

	def printChunk(self, chunk):
		print('   index:', chunk['index'])
		print('   path:', chunk['path'])
		print('   startFrame:', chunk['startFrame'])
		print('   stopFrame:', chunk['stopFrame'])
			
	def getCurrentChunk(self):
		if self.currentChunk is not None:
			actualChunkNumber = self.chunkData['chunkOrder'][self.currentChunk]
			chunk = self.chunkData['chunks'][actualChunkNumber]
			return chunk
		else:
			return None
			
	@property
	def numChunks(self):
		return len(self.chunkData['chunkOrder'])
