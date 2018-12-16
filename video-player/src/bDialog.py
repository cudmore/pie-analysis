# Author: Robert Cudmore
# Date: 20181203

import os, sys

import cv2

import tkinter
from tkinter import ttk

import VideoApp
import bChunk

##################################################################################
class bGenerateChunksDialog:
	"""
	Dialog for user to specify chunk parameters and generate a random chunks .txt file
	"""
	def __init__(self, parentApp):
		self.myParentApp = parentApp
		
		self.myPath = self.myParentApp.path
		
		self.top = tkinter.Toplevel(self.myParentApp.root)
		self.top.title('Generate Chunks')
		self.top.geometry('600x500')

		self.top.grid_rowconfigure(0, weight=1) # main
		self.top.grid_rowconfigure(1, weight=0) # keys
		self.top.grid_columnconfigure(0, weight=1)

		myPadding = 10

		myFrame = ttk.Frame(self.top, borderwidth=2,relief="groove")
		myFrame.grid(row=0, column=0, sticky="nsew", padx=myPadding, pady=myPadding)
		myFrame.grid_rowconfigure(4, weight=1) # IMPORTANT: row 4 is feedback label
		myFrame.grid_columnconfigure(0, weight=1)
		myFrame.grid_columnconfigure(1, weight=1)

		from_ = 0
		to = 2**32-1
		
		# usePieces
		row = 0
		usePiecesText = 'Use Pieces' #'usePieces'
		usePiecesLabel = ttk.Label(myFrame, text=usePiecesText)
		usePiecesLabel.grid(row=row, column=0, sticky="w", padx=myPadding, pady=myPadding)

		self.usePiecesCheckbutton = ttk.Checkbutton(myFrame, text='Use Pieces')
		self.usePiecesCheckbutton.state(['!alternate'])
		self.usePiecesCheckbutton.state(['selected'])
		self.usePiecesCheckbutton.grid(row=row, column=1, sticky="w", padx=myPadding, pady=myPadding)

		# pieceDurationSeconds
		row = 1
		pieceDurationSecondsText = 'Piece Duration (Sec)' #'pieceDurationSeconds'
		pieceDurationSecondsLabel = ttk.Label(myFrame, text=pieceDurationSecondsText)
		pieceDurationSecondsLabel.grid(row=row, column=0, sticky="w", padx=myPadding, pady=myPadding)

		pieceDurationSecondsVal = 10 * 60
		self.pieceDurationSecondsSpinbox = ttk.Spinbox(myFrame, from_=from_, to=to)
		self.pieceDurationSecondsSpinbox.set(pieceDurationSecondsVal)
		self.pieceDurationSecondsSpinbox.selection_range(0, "end")
		self.pieceDurationSecondsSpinbox.icursor("end")
		self.pieceDurationSecondsSpinbox.grid(row=row, column=1, sticky="w", padx=myPadding, pady=myPadding)

		# chunkDurationSeconds
		row = 2
		chunkDurationSecondsText = 'Chunk Duration (sec)' #'chunkDurationSeconds'
		chunkDurationSecondsLabel = ttk.Label(myFrame, text=chunkDurationSecondsText)
		chunkDurationSecondsLabel.grid(row=row, column=0, sticky="w", padx=myPadding, pady=myPadding)

		chunkDurationSecondsVal = 10
		self.chunkDurationSecondsSpinbox = ttk.Spinbox(myFrame, from_=from_, to=to)
		self.chunkDurationSecondsSpinbox.set(chunkDurationSecondsVal)
		self.chunkDurationSecondsSpinbox.selection_range(0, "end")
		self.chunkDurationSecondsSpinbox.icursor("end")
		self.chunkDurationSecondsSpinbox.grid(row=row, column=1, sticky="w", padx=myPadding, pady=myPadding)

		# chunksPerFile
		row = 3
		chunksPerFileText = 'Chunks Per File' #'chunksPerFile'
		chunksPerFileLabel = ttk.Label(myFrame, text=chunksPerFileText)
		chunksPerFileLabel.grid(row=row, column=0, sticky="w", padx=myPadding, pady=myPadding)

		chunksPerFileVal = 30
		self.chunksPerFileSpinbox = ttk.Spinbox(myFrame, from_=from_, to=to)
		self.chunksPerFileSpinbox.set(chunksPerFileVal)
		self.chunksPerFileSpinbox.selection_range(0, "end")
		self.chunksPerFileSpinbox.icursor("end")
		self.chunksPerFileSpinbox.grid(row=row, column=1, sticky="w", padx=myPadding, pady=myPadding)

		# feeback with results
		row = 4
		self.resultsLabel = ttk.Label(myFrame, text='results', anchor="w", justify="left", borderwidth=2, relief="groove")
		self.resultsLabel.grid(row=row, column=0, columnspan=2, sticky="nsew", padx=myPadding, pady=myPadding)
		
		#
		# cancel/ok (has its own frame)
		buttonPadding = 20
		myFrameOK = ttk.Frame(self.top) #, borderwidth=5,relief="groove")
		myFrameOK.grid(row=1, column=0, sticky="e", padx=buttonPadding, pady=buttonPadding)
		"""
		myFrameOK.grid_columnconfigure(0, weight=1)
		myFrameOK.grid_columnconfigure(1, weight=1)
		myFrameOK.grid_columnconfigure(3, weight=1)
		"""
		
		cancelButton = ttk.Button(myFrameOK, text="Cancel", command=self.cancelButton_Callback)
		cancelButton.grid(row=0, column=1)

		s = ttk.Style()
		s.configure('Kim.TButton', foreground='forest green')
		okButton = ttk.Button(myFrameOK, text="Generate", style='Kim.TButton', command=self.generateButton_Callback)
		okButton.grid(row=0, column=2)

		okButton = ttk.Button(myFrameOK, text="Done", command=self.doneButton_Callback)
		okButton.grid(row=0, column=3)

	def doneButton_Callback(self):
		self.top.destroy() # destroy *this, the modal

	def cancelButton_Callback(self):
		self.top.destroy() # destroy *this, the modal

	def generateButton_Callback(self):
		print('=== bGenerateChunksDialog.generateButton_Callback()')

		if not os.path.isdir(self.myParentApp.path):
			# error
			print('    generateButton_Callback() did not find app path, there is no loaded folder')
			return 0
		
		chunks = bChunk.bChunk(self.myParentApp.path)
	
		# pieces is 10 min
		# chunk duration is 10 seconds
		# chunksPerVideo is 30
	
		
		# was this for jessie 'scrambled' folder
		pieceDurationSeconds = 10 * 60 # seconds
		chunkDurationSeconds = 10 # seconds
		chunksPerFile = 30

		# is this for my 'video' folder
		pieceDurationSeconds = 35
		chunkDurationSeconds = 10 # seconds
		chunksPerFile = 2
		
		usePieces = 'selected' in self.usePiecesCheckbutton.state()
		if usePieces:
			pieceDurationSeconds = self.pieceDurationSecondsSpinbox.get()
			pieceDurationSeconds = int(pieceDurationSeconds)
		else:
			pieceDurationSeconds = None

		chunkDurationSeconds = self.chunkDurationSecondsSpinbox.get()
		chunkDurationSeconds = int(chunkDurationSeconds)

		chunksPerFile = self.chunksPerFileSpinbox.get()
		chunksPerFile = int(chunksPerFile)

		print('    Use Pieces:', usePieces)
		print('    pieceDurationSeconds:', pieceDurationSeconds, type(pieceDurationSeconds))
		print('    chunkDurationSeconds:', chunkDurationSeconds, type(chunkDurationSeconds))
		print('    chunksPerFile:', chunksPerFile, type(chunksPerFile))
		
		# outList is a list of dict {'file', 'result'}
		# 'result' will either be 'ok' or have error
		outFilePath, outList = chunks.generate(pieceDurationSeconds, chunkDurationSeconds, chunksPerFile)
		
		if not outFilePath:
			outFilePath = 'none'
		
		# show results in dialog
		self.resultsLabel['text'] = 'out file path: ' + outFilePath + '\n'
		for idx, out in enumerate(outList):
			print('out:', out)
			#self.resultsLabel['text'] += '===' + "\n"
			self.resultsLabel['text'] += 'file ' + str(idx+1) + ': ' + out['file'] + "\n"
			self.resultsLabel['text'] += '    ' + out['result'] + "\n"
			
		# user needs to rename the file 'randomChunks.txt'
		# user needs to load folder again
		
		# keep here
		#self.top.destroy() # destroy *this, the modal

##################################################################################
class bNoteDialog:
	"""
	Opens a modal dialog to set the note of an event
	"""
	def __init__(self, parentApp, noteStr, myCallback):
		#self.noteStr = noteStr
		self.myCallback = myCallback
		
		#print('original note is noteStr:', noteStr)

		# to make modal
		#self.grab_set()
		# see: http://effbot.org/tkinterbook/tkinter-dialog-windows.htm
		
		self.top = tkinter.Toplevel(parentApp)
		
		self.top.bind('<Button-1>', self._ignore)
		
		#top.focus_force() # added
		#top.grab_set()
		
		tkinter.Label(self.top, text="Note").pack()

		#
		self.noteEntryWidget = tkinter.Entry(self.top)
		#self.noteEntryWidget.delete(0, "end")
		self.noteEntryWidget.insert(0, noteStr)
		self.noteEntryWidget.select_range(0, "end")
		
		self.noteEntryWidget.bind('<Key-Return>', self.okKeyboard_Callback)
		self.noteEntryWidget.focus_set()
		self.noteEntryWidget.pack(padx=5)

		cancelButton = tkinter.Button(self.top, text="Cancel", command=self.cancelButton_Callback)
		cancelButton.pack(side="left", pady=5)
		
		okButton = tkinter.Button(self.top, text="OK", command=self.okButton_Callback)
		okButton.pack(side="left", pady=5)


	def _ignore(self, event):
		print('_ignore event:', event)
		
	def cancelButton_Callback(self):
		#print('cancelButton_Callback()')
		self.top.destroy()
		
	def okKeyboard_Callback(self, event):
		#print('okKeyboard_Callback()')
		#print("value is:", self.e.get())
		self.okButton_Callback()
		
	def okButton_Callback(self):
		#print('okButton_Callback()')
		newNote = self.noteEntryWidget.get()
		#print("   new note is:", newNote)
		
		self.myCallback('ok', newNote)
		
		self.top.destroy() # destroy *this, the modal

##################################################################################
class bPreferencesDialog:
	"""
	Opens a modal dialog to set the note of an event
	"""
	def __init__(self, parentApp):

		# to make modal
		#self.grab_set()
		# see: http://effbot.org/tkinterbook/tkinter-dialog-windows.htm
		
		self.top = tkinter.Toplevel(parentApp.root)
		self.top.grab_set()
		self.top.bind('<Button-1>', self._ignore)
		
		print(parentApp.configDict)
		
		self.top.title('Preferences')
		self.top.geometry('500x320')
		
		includeOptions = ('smallSecondsStep', 'largeSecondsStep', 'smallSecondsStep_chunk', 'largeSecondsStep_chunk')
		
		myPadding = 5
		
		self.top.grid_rowconfigure(0, weight=1) # main
		self.top.grid_rowconfigure(1, weight=1) # keys
		self.top.grid_rowconfigure(2, weight=0) # ok
		self.top.grid_columnconfigure(0, weight=1)

		myFrame = ttk.Frame(self.top, borderwidth=5,relief="groove")
		myFrame.grid(row=0, column=0, sticky="nsew", padx=myPadding, pady=myPadding)
		myFrame.grid_columnconfigure(0, weight=1)
		myFrame.grid_columnconfigure(1, weight=1)
		
		from_ = 0
		to = 2**32-1
		
		# small/big steps
		for idx, option in enumerate(includeOptions):
			myFrame.grid_rowconfigure(idx, weight=1)

			myText = parentApp.configDict[option]
			myInt = int(myText)
			
			myLabel = ttk.Label(myFrame, text=option)
			myLabel.grid(row=idx, column=0, sticky="w", padx=myPadding, pady=myPadding)

			mySpinbox = ttk.Spinbox(myFrame, from_=from_, to=to)
			mySpinbox.set(myInt)
			mySpinbox.selection_range(0, "end")
			mySpinbox.icursor("end")

			mySpinbox.grid(row=idx, column=1, sticky="w", padx=myPadding, pady=myPadding)
		
		
		# keys
		myFrameKeys = ttk.Frame(self.top, borderwidth=5,relief="groove")
		myFrameKeys.grid(row=1, column=0, sticky="nsew", padx=myPadding, pady=myPadding)
		myFrameKeys.grid_columnconfigure(0, weight=1)
		myFrameKeys.grid_columnconfigure(1, weight=1)

		for idx, (key, value) in enumerate(parentApp.configDict['keyMap'].items()):
			myFrameKeys.grid_rowconfigure(idx, weight=1)

			myText = value #parentApp.configDict[option]
			#myInt = int(myText)
			
			myLabel = ttk.Label(myFrameKeys, text=key)
			myLabel.grid(row=idx, column=0, sticky="w", padx=myPadding, pady=myPadding)

			entryWidget = tkinter.Entry(myFrameKeys)
			#entryWidget.configure(command=lambda widget=entryWidget: self.editKey(widget))
			#entryWidget.delete(0, "end")
			entryWidget.insert(0, myText)
			entryWidget.select_range(0, "end")

			entryWidget.grid(row=idx, column=1, sticky="w", padx=myPadding, pady=myPadding)
			#entryWidget.bind('<Key>', self.keyPress)
			entryWidget.bind('<Key>', lambda widget=entryWidget: self.keyPress(widget))
			
		# ok
		buttonPadding = 10
		myFrameOK = ttk.Frame(self.top) #, borderwidth=5,relief="groove")
		myFrameOK.grid(row=2, column=0, sticky="e", padx=buttonPadding, pady=buttonPadding)
		myFrameOK.grid_columnconfigure(0, weight=1)
		myFrameOK.grid_columnconfigure(1, weight=1)

		cancelButton = ttk.Button(myFrameOK, text="Cancel", command=self.cancelButton_Callback)
		cancelButton.grid(row=0, column=1)

		okButton = ttk.Button(myFrameOK, text="Save Preferences", command=self.okButton_Callback)
		okButton.grid(row=0, column=2)

		#self.top.focus_force()
		
		# none of this fucking works !!!
		self.top.grab_set()
		self.top.grab_set_global()
		self.top.wait_window(self.top)
		


	def _ignore(self, event):
		print('_ignore event:', event)
		return 'break'
		
	def editKey(self, widget):
		print('editKey() widget:', widget)
	
	def keyPress(self, event):
		print('keyPress() event:', event)
		print('event.widget._name:', event.widget._name)
		value = event.widget.get()
		print('value:', value)
		
	def cancelButton_Callback(self):
		self.top.destroy() # destroy *this, the modal

	def okButton_Callback(self):
		print('todo: actually save preferences')
		self.top.destroy() # destroy *this, the modal

##################################################################################
class bAboutDialog:
	"""
	Opens a modal dialog to set the note of an event
	"""
	def __init__(self, parentApp):

		# to make modal
		#self.grab_set()
		# see: http://effbot.org/tkinterbook/tkinter-dialog-windows.htm
		
		self.top = tkinter.Toplevel(parentApp)
		
		self.top.title('About PiE Video Analysis')
		self.top.geometry('320x240')
		
		myPadding = 10
		
		self.top.grid_rowconfigure(0, weight=1)
		self.top.grid_columnconfigure(0, weight=1)

		myFrame = ttk.Frame(self.top)
		myFrame.grid(row=0, column=0, sticky="nsew", padx=myPadding, pady=myPadding)
		
		platformStr = 'Platform: ' + sys.platform
		ttk.Label(myFrame, text=platformStr, anchor="nw").pack(side="top")

		videoAppVersionStr = 'Video App: ' + VideoApp.__version__
		ttk.Label(myFrame, text=videoAppVersionStr, anchor="nw").pack(side="top")

		pythonVersionStr = 'Python: ' + str(sys.version_info[0]) + '.' + str(sys.version_info[1]) + '.' + str(sys.version_info[2])
		ttk.Label(myFrame, text=pythonVersionStr, anchor="nw").pack(side="top")
		
		opencvVersionStr = 'opencv: ' + str(cv2.__version__)
		ttk.Label(myFrame, text=opencvVersionStr, anchor="nw").pack(side="top")
		
		tkinterVersionStr = 'tkinter: ' + str(tkinter.TkVersion)
		ttk.Label(myFrame, text=tkinterVersionStr, anchor="nw").pack(side="top")

		okButton = ttk.Button(myFrame, text="OK", command=self.okButton_Callback)
		okButton.pack(side="top", pady=5)

		#self.top.focus_force() # added
		
		self.top.grab_set()
		
		#self.top.grab_set_global()


	def okButton_Callback(self):
		self.top.destroy() # destroy *this, the modal

##################################################################################
class bNumberDialog:
	"""
	Opens a modal dialog to set an integer
	"""
	def __init__(self, parentApp, initValue=0, from_=0, to=2**32-1, callback=None):
		#self.noteStr = noteStr
		self.myCallback = callback
		
		#print('original note is noteStr:', noteStr)

		# to make modal
		#self.grab_set()
		# see: http://effbot.org/tkinterbook/tkinter-dialog-windows.htm
		
		self.top = tkinter.Toplevel(parentApp)
		
		#top.focus_force() # added
		#top.grab_set()
		
		tkinter.Label(self.top, text="Note").pack()

		###
		self.gotoChunkEntry = ttk.Spinbox(self.top, width=5, from_=from_, to=to)
		self.gotoChunkEntry.set(initValue)
		self.gotoChunkEntry.selection_range(0, "end")
		self.gotoChunkEntry.icursor("end")
		self.gotoChunkEntry.grid(row=0, column=7)
		#self.gotoChunkEntry.bind("<Key>", self._gotoChunkEntry)

		self.gotoChunkEntry.bind('<Key-Return>', self.okKeyboard_Callback)
		self.gotoChunkEntry.focus_set()
		self.gotoChunkEntry.pack(padx=5)
		###
		
		cancelButton = tkinter.Button(self.top, text="Cancel", command=self.cancelButton_Callback)
		cancelButton.pack(side="left", pady=5)
		
		okButton = tkinter.Button(self.top, text="OK", command=self.okButton_Callback)
		okButton.pack(side="left", pady=5)

	def cancelButton_Callback(self):
		#print('cancelButton_Callback()')
		self.top.destroy()
		
	def okKeyboard_Callback(self, event):
		print('okKeyboard_Callback()')
		#print("value is:", self.e.get())
		self.okButton_Callback()
		
	def okButton_Callback(self):
		print('okButton_Callback()')
		returnValue = int(self.gotoChunkEntry.get())
		#print("   new note is:", newNote)
		
		if self.myCallback is not None:
			self.myCallback(returnValue)
		
		self.top.destroy() # destroy *this, the modal

