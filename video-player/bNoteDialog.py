# Author: Robert Cudmore
# Date: 20181101

import tkinter
from tkinter import ttk

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

