# Author: Robert Cudmore
# Date: 20181203

import sys

import cv2

import tkinter
from tkinter import ttk

import VideoApp

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

