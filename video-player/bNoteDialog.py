# Author: Robert Cudmore
# Date: 20181101

import tkinter
from tkinter import ttk

##################################################################################
class bNoteDialog:
	"""
	Opens a modal dialog to set the note of an event
	"""
	def __init__(self, parentApp):
		self.parentApp = parentApp
		
		#
		# grab the note of selected event
		self.item = self.parentApp.eventTree.focus()
		if self.item == '':
			print('bNoteDialog() please select an event')
			return None
		columns = self.parentApp.eventTree['columns']				
		noteColIdx = columns.index('note') # assuming 'note' exists
		values = self.parentApp.eventTree.item(self.item, "values")
		self.index = int(values[0]) # assuming [0] is index
		noteStr = values[noteColIdx]
		
		print('original note is noteStr:', noteStr)

		# to make modal
		#self.grab_set()
		# see: http://effbot.org/tkinterbook/tkinter-dialog-windows.htm
		
		self.top = tkinter.Toplevel(parentApp.root)
		
		#top.focus_force() # added
		#top.grab_set()
		
		tkinter.Label(self.top, text="Note").pack()

		#
		self.e = tkinter.Entry(self.top)
		#self.e.delete(0, "end")
		self.e.insert(0, noteStr)
		
		self.e.bind('<Key-Return>', self.okKeyboard_Callback)
		self.e.focus_set()
		self.e.pack(padx=5)

		cancelButton = tkinter.Button(self.top, text="Cancel", command=self.cancelButton_Callback)
		cancelButton.pack(side="left", pady=5)
		
		okButton = tkinter.Button(self.top, text="OK", command=self.okButton_Callback)
		okButton.pack(side="left", pady=5)

	def cancelButton_Callback(self):
		print('cancelButton_Callback()')
		self.top.destroy()
		
	def okKeyboard_Callback(self, event):
		print('okKeyboard_Callback()')
		#print("value is:", self.e.get())
		self.okButton_Callback()
		
	def okButton_Callback(self):
		print('okButton_Callback()')
		newNote = self.e.get()
		print("new note is:", newNote)
		
		# set in our eventList
		self.parentApp.eventList.eventList[self.index].dict['note'] = newNote
		self.parentApp.eventList.save()
		
		# get the event we just set
		event = self.parentApp.eventList.eventList[self.index]
		
		# update the tree
		# todo: get this 'item' when we open dialog and use self.item
		#item = self.eventTree.focus()
		self.parentApp.eventTree.item(self.item, values=event.asTuple())

		#print('bNoteDialog.okButton_Callback() is calling destroy')
		self.top.destroy() # destroy *this, the modal
		
	def _setNote(txt):
		item = self.parentApp.eventTree.focus()
