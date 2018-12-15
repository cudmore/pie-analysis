# Author: Robert Cudmore
# Date: 20181120

import os, time, json
import tkinter
from tkinter import ttk

import bDialog

class bChunkView:
	
	def __init__(self, app, random_chunks_frame):
		self.app = app
		#self.random_chunks_frame = random_chunks_frame
		
		self.currentChunkIndex = None # index into random list of chunks (chunkData['chunkOrder'])
		self.chunkData = None # loaded from file, data is a dict of {'chunks', 'chunkOrder'}
		
		self.myWidgetList = []

		"""
		self.chunkFileLabel = ttk.Label(random_chunks_frame, width=6, anchor="w", text='File:')
		self.chunkFileLabel.grid(row=0, column=0)
		"""
		
		self.currentChunkLabel = ttk.Label(random_chunks_frame, anchor="w", text='chunk none')
		self.currentChunkLabel.grid(row=0, column=0, sticky="w")
		self.myWidgetList.append(self.currentChunkLabel)
		
		self.numChunksLabel = ttk.Label(random_chunks_frame, anchor="w", text='')
		self.numChunksLabel.grid(row=0, column=1, sticky="w")
		self.myWidgetList.append(self.numChunksLabel)
	
		# previous chunk
		self.previousChunkButton = ttk.Button(random_chunks_frame, width=4, text="<Prev", command=self.chunk_previous)
		self.previousChunkButton.grid(row=0, column=2, sticky="w")
		self.previousChunkButton.bind("<Key>", self.keyPress)
		self.myWidgetList.append(self.previousChunkButton)

		self.startOfChunkButton = ttk.Button(random_chunks_frame, width=1, text="|<", command=self.chunk_start)
		self.startOfChunkButton.grid(row=0, column=3, sticky="w")
		self.startOfChunkButton.bind("<Key>", self.keyPress)
		self.myWidgetList.append(self.startOfChunkButton)

		# next chunk
		self.nextChunkButton = ttk.Button(random_chunks_frame, width=4, text="Next>", command=self.chunk_next)
		self.nextChunkButton.grid(row=0, column=4, sticky="w")
		self.nextChunkButton.bind("<Key>", self.keyPress)
		self.myWidgetList.append(self.nextChunkButton)
		
		self.gotoChunkButton = ttk.Button(random_chunks_frame, width=4, text="Go To", command=self.chunk_goto2)
		self.gotoChunkButton.grid(row=0, column=5, sticky="w")
		self.gotoChunkButton.bind("<Key>", self.keyPress)
		self.myWidgetList.append(self.gotoChunkButton)

		# did not work because all key strokes are being grabbed to make events
		"""
		self.gotoChunkEntry = ttk.Spinbox(random_chunks_frame, width=5, from_=0, to=0)
		self.gotoChunkEntry.grid(row=0, column=7)
		self.gotoChunkEntry.insert(0, '0')
		self.gotoChunkEntry.bind("<Key>", self._gotoChunkEntry)
		"""
		
		self.hijackControlsCheckbox = ttk.Checkbutton(random_chunks_frame, text='Limit Video Controls', 
														command=self.limitVideoControls_callback)
		self.hijackControlsCheckbox.state(['!alternate'])
		self.hijackControlsCheckbox.state(['!selected'])
		#self.hijackControlsCheckbox.grid(row=1, column=0, columnspan=2, sticky="w")
		self.hijackControlsCheckbox.grid(row=0, column=6, sticky="w")
		self.hijackControlsCheckbox.bind("<Key>", self.keyPress)
		self.myWidgetList.append(self.hijackControlsCheckbox)
		
		"""
		self.limitInterfaceCheckbox = ttk.Checkbutton(random_chunks_frame, text='Limit Interface', 
														command=self.limitVideoControls_callback2)
		self.limitInterfaceCheckbox.state(['!alternate'])
		self.limitInterfaceCheckbox.state(['!selected'])
		#self.limitInterfaceCheckbox.grid(row=1, column=2, columnspan=4, sticky="w") # +1 col because hijackControlsCheckbox has columnspan=2
		self.limitInterfaceCheckbox.grid(row=0, column=7, sticky="w") # 
		self.limitInterfaceCheckbox.bind("<Key>", self.keyPress)
		"""
		
		#self.chunk_goto(0)
		
	"""
	def _gotoChunkEntry(self, event):
		print('_gotoChunkEntry event:', event)
		#self.gotoChunkEntry.value = val
		return 'break'
	"""
		
	def enableInterface(self, onoff):
		if self.chunkData is None:
			print('bChunkView.enableInterface() is forcing off, self.chunkData is None')
			onoff = False
		
		if onoff:
			state = 'enabled'
		else:
			state = 'disabled'
		
		for item in self.myWidgetList:
			#item['state'] = state
			#item['state'] = ['!alternate']
			
			# tkinter is kind of shit here
			# need to use dictionary ['state'] to enable/disable
			# and use .state() to make sure it does not go to alternate
			item['state'] = state
			item.state(['!alternate'])
			
	def keyPress(self, event):
		"""
		This function will take all key-presses (except \r) and pass to main app.
		return "break" is critical to stop propogation of event
		"""
		#print('bChunkView.keyPress() event.char:', event.char)
			
		if event.char == '\r':
			pass
		else:
			self.app.keyPress(event)
			return 'break'

	def blindInterface(self, onoff, gotoFirstChunk=False):
		if self.chunkData is None:
			print('bChunkView.blindInterface() did nothing, self.chunkData is None')
			return 0
			
		if onoff:
			self.hijackControlsCheckbox['state'] = "disabled"

			self.hijackControlsCheckbox.state(['!alternate'])
			self.hijackControlsCheckbox.state(['selected'])

			"""
			if gotoFirstChunk:
				self.chunk_goto(self.currentChunkIndex)
			"""
			
		else:
			self.hijackControlsCheckbox['state'] = "normal"
			self.hijackControlsCheckbox.state(['!alternate'])
				
			
	def limitVideoControls_callback(self):
		#print('self.hijackControlsCheckbox.state:', self.hijackControlsCheckbox.state)
		
		self.chunk_goto(self.currentChunkIndex)
		
		#self.app.hijackInterface(self.isHijacking())

	"""
	def checkbox_callback2(self):
		if self.limitInterfaceCheckbox.instate(['selected']):
			print('hiding video list and feedback')
			self.app.limitInterface(True)
		else:
			print('showing video list and feedback')
			self.app.limitInterface(False)
	"""
		

	def isHijacking(self):
		#return self.hijackControlsCheckbox_Value.get() == 1
		return self.hijackControlsCheckbox.instate(['selected'])

	def chunkInterface_populate(self, askForFile=False):
		"""
		Open a chunks file and populate interface
		"""
		print('chunkInterface_populate()')

		self.chunkData = None
		self.currentChunkIndex = 0

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
			self.enableInterface(False)
			return
		
		#chunkFile = bRandomChunks(filename).open()
		#print(chunkFile)
		with open(filepath) as f:
			self.chunkData = json.load(f) # data is a dict of {'chunks', 'chunkOrder'}
				
		self.currentChunkLabel['text'] = 'chunk ' + str(self.currentChunkIndex)
		self.numChunksLabel['text'] = 'of ' + str(self.numChunks)

		self.enableInterface(True)
				
	def findChunk(self, path, startFrame):
		"""
		Return: retChunkIdx, retRandomIdx
			retChunkIdx (int): the absolute index of the chunk
			retRandomIdx (int): the index into the random list of chunks (in chunkData['chunkOrder']
		"""
		if self.chunkData is None:
			return None, None
			
		retRandomIdx = None # index into random list
		retChunkIdx = None # absolute chunk number
		# step through the random chunk order
		for randomIdx, chunkNumber in enumerate(self.chunkData['chunkOrder']):
			chunk = self.chunkData['chunks'][chunkNumber]
			if chunk['path'] == path:
				if startFrame >= chunk['startFrame'] and startFrame < chunk['stopFrame']:
					retChunkIdx = chunk['index']
					retRandomIdx = randomIdx
					break
		print('bChunkView.findChunk() path:', path, 'startFrame:', startFrame)
		print('   returning retChunkIdx:', retChunkIdx, 'retRandomIdx:', retRandomIdx)
		return retChunkIdx, retRandomIdx
				
	def chunk_previous(self):
		print('chunk_previous()')
		self.currentChunkIndex -= 1
		if self.currentChunkIndex < 0:
			self.currentChunkIndex = 0
		self.chunk_goto(self.currentChunkIndex)
		
	def chunk_start(self):
		""" Go to first frame in chunk"""
		#actualChunkNumber = self.chunkData['chunkOrder'][self.currentChunkIndex]
		#currentChunk = self.chunkData['chunks'][actualChunkNumber]
		currentChunk, randomIdx = self.getCurrentChunk()
		if currentChunk is not None:
			startFrame = currentChunk['startFrame']
			print('chunk_start()')
			print('   index:', currentChunk['index'])
			print('   path:', currentChunk['path'])
			print('   startFrame:', startFrame)
			self.app.setFrame(startFrame, withDelay=True)
		
	def chunk_next(self):
		#print('chunk_next()')
		if self.numChunks > 0:
			self.currentChunkIndex += 1
			if self.currentChunkIndex > self.numChunks - 1:
				self.currentChunkIndex = self.numChunks - 1
			self.chunk_goto(self.currentChunkIndex)
		
	def chunk_goto2(self):
		# get value from gotoChunkEntry
		#chunkNumber = int(self.gotoChunkEntry.get())
		bDialog.bNumberDialog(self.app.root, from_=0, to=self.numChunks - 1, callback=self._chunk_goto2)
		# flow goes to _chunk_goto2()
		#self.chunk_goto(chunkNumber)
		
	def _chunk_goto2(self, gotoChunk):
		# callback from bNumberDialog()
		print('_chunk_goto2() gotoChunk:', gotoChunk, type(gotoChunk))
		self.chunk_goto(gotoChunk)
		
	def chunk_goto(self, chunkNumber):
		"""
		chunkNumber (int): index into random list of chunks (e.g. self.chunkData['chunkOrder'])
		"""
		print('chunk_goto() chunkNumber:', chunkNumber)
		
		if self.numChunks == 0:
			print('    no chunks')
			return False
		
		# check valid chunkNumber
		if chunkNumber > self.numChunks-1:
			print('    error, chunkNumber > numChunks')
			return
			
		self.currentChunkIndex = chunkNumber
		
		#actualChunkNumber = self.chunkData['chunkOrder'][chunkNumber]
		#chunk = self.chunkData['chunks'][actualChunkNumber]
		chunk, randomIdx = self.getCurrentChunk()
		
		if chunk is None:
			print('    chunk is none?')
			return 0
		
		path = chunk['path']
		startFrame = chunk['startFrame']
		stopFrame = chunk['stopFrame']
		
		#print('   calling self.app.switchvideo() gotoFrame:', startFrame)
		self.app.switchvideo(path, paused=True, gotoFrame=startFrame)
		
		self.app.hijackInterface(self.isHijacking())
		
		# update chunk interface
		self.currentChunkLabel['text'] = 'chunk ' + str(self.currentChunkIndex)
	
		return True
		
	def printChunk(self, chunk):
		print('   index:', chunk['index'])
		print('   path:', chunk['path'])
		print('   startFrame:', chunk['startFrame'])
		print('   stopFrame:', chunk['stopFrame'])
			
	def getCurrentChunk(self):
		"""
		Return:
			chunk (bChunk): Current Chunk
			idx (int): Index into list of random chunks
		"""
		print('getCurrentChunk()')
		if self.chunkData is not None:
			actualChunkNumber = self.chunkData['chunkOrder'][self.currentChunkIndex]
			chunk = self.chunkData['chunks'][actualChunkNumber]
			print('    chunk:', chunk, 'self.currentChunkIndex:', self.currentChunkIndex)
			return chunk, self.currentChunkIndex
		else:
			return None, None
			
	@property
	def numChunks(self):
		if self.chunkData is not None:
			return len(self.chunkData['chunkOrder'])
		else:
			return 0