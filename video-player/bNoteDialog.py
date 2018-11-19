# Author: Robert Cudmore
# Date: 20181101

##################################################################################
class bNoteDialog:
	"""
	Opens a modal dialog to set the note of an event
	"""
	def __init__(self, parentApp):
		self.parentApp = parentApp
		
		# to make modal
		#self.grab_set()
		# see: http://effbot.org/tkinterbook/tkinter-dialog-windows.htm
		
		top = self.top = tkinter.Toplevel(parentApp.root)
		
		#top.focus_force() # added
		#top.grab_set()
		
		tkinter.Label(top, text="Note").pack()

		#
		# grab the note of selected event
		self.item = self.parentApp.eventTree.focus()
		if self.item == '':
			return 0
		columns = self.parentApp.eventTree['columns']				
		noteColIdx = columns.index('note') # assuming 'frameStart' exists
		values = self.parentApp.eventTree.item(self.item, "values")
		self.index = int(values[0]) # assuming [0] is index
		noteStr = values[noteColIdx]
		
		print('original note is noteStr:', noteStr)
		
		#
		self.e = tkinter.Entry(top)
		#self.e.delete(0, "end")
		self.e.insert(0, noteStr)
		
		self.e.bind('<Key-Return>', self.ok0)
		self.e.focus_set()
		self.e.pack(padx=5)

		cancelButton = tkinter.Button(top, text="Cancel", command=self.top.destroy)
		cancelButton.pack(side="left", pady=5)
		
		okButton = tkinter.Button(top, text="OK", command=self.ok)
		okButton.pack(side="left", pady=5)

	def ok0(self, event):
		""" Called when user hits enter """
		#print("value is:", self.e.get())
		self.ok()
		
	def ok(self):
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

		self.top.destroy() # destroy *this, the modal
	def _setNote(txt):
		item = self.parentApp.eventTree.focus()
