# Robert Cudmore
# 20181127

"""
self.eventTree
"""

import tkinter
from tkinter import ttk

import bEventList

###################################################################################
class bTree(ttk.Frame):
	def __init__(self, parent, parentApp, *args, **kwargs):
		ttk.Frame.__init__(self, parent)
		
		self.myParentApp = parentApp
		self.myParent = parent
		
		myPadding = 5

		self.treeview = ttk.Treeview(self, *args, **kwargs)
		self.treeview.grid(row=0,column=0, sticky="nsew", padx=myPadding, pady=myPadding)

		self.scrollbar = ttk.Scrollbar(self, orient="vertical", command = self.treeview.yview)
		self.scrollbar.grid(row=0, column=0, sticky='nse', padx=myPadding, pady=myPadding)
		self.treeview.configure(yscrollcommand=self.scrollbar.set)

	def sort_column(self, col, reverse):
		print('bTree.sort_column()()', 'col:', col, 'reverse:', reverse)
		l = [(self.treeview.set(k, col), k) for k in self.treeview.get_children('')]
		
		print('   l:', l)
		
		#newlist = sorted(list_to_be_sorted, key=lambda k: k['name'])
		
		l.sort(reverse=reverse)

		# rearrange items in sorted positions
		for index, (val, k) in enumerate(l):
			self.treeview.move(k, '', index)

		# reverse sort next time
		self.treeview.heading(col, command=lambda:self.sort_column(col, not reverse))

	def _getTreeViewSelection(self, col):
		"""
		Get value of selected column
			tv: treeview
			col: (str) column name
		"""
		item = self.treeview.focus()
		if item == '':
			print('_getTreeViewSelection() did not find a selection in treeview')
			return None, None
		columns = self.treeview['columns']				
		colIdx = columns.index(col) # assuming 'frameStart' exists
		values = self.treeview.item(item, "values") # tuple of a values in tv row
		theRet = values[colIdx]
		return theRet, item

	def _selectTreeViewRow(self, col, isThis):
		"""
		Given a treeview (tv), a column name (col) and a value (isThis)
		Visually select the row in tree view that has column mathcing isThis
		
		tv: treeview
		col: (str) column name
		isThis: (str) value of a cell in column (col)
		"""
		theRow = self._getTreeViewRow(col, isThis)
		
		if theRow is not None:
			# get the item
			children = self.treeview.get_children()
			item = children[theRow]
			#print('item:', item)
			
			# select the row
			self.treeview.focus(item) # select internally
			self.treeview.selection_set(item) # visually select

	def _getTreeViewRow(self, col, isThis):
		"""
		Given a treeview, a col name and a value (isThis)
		Return the row index of the column col mathing isThis
		"""
		# get the tree view columns and find the col we are looking for
		columns = self.treeview['columns']				
		colIdx = columns.index(col) # assuming 'frameStart' exists

		#print('tv.get_children():', tv.get_children())
		
		rowIdx = 0
		theRet = None
		for child in self.treeview.get_children():
			values = self.treeview.item(child)["values"] # values at current row
			if values[colIdx] == isThis:
				theRet = rowIdx
				break
			rowIdx += 1
		return theRet
		

###################################################################################
class bEventTree(bTree):
	def __init__(self, parent, parentApp, eventList, *args, **kwargs):
		bTree.__init__(self, parent, parentApp, *args, **kwargs)
		
		self.eventList = eventList # bEventList object
		
	def populateEvents(self, eventList, doInit=False):
		print('bEventTree.populateEvents()')
		
		self.eventList = eventList
		
		eventColumns = self.eventList.getColumns()
		
		if doInit:
			# configure columns
			self.treeview['columns'] = eventColumns
			"""
			gEventColumns = ('index', 'path', 'cseconds', 'cDate', 'cTime', 
							'typeNum', 'typeStr', 'frameStart', 'frameStop', 
							'numFrames', 'sStart', 'sStop', 'numSeconds'
							'chunkIndex', 'note')
			"""
			displaycolumns_ = ['index', 'typeNum', 'frameStart', 'frameStop', 'chunkIndex', 'note'] # hide some columns
			displaycolumns = [] # build a list of columns not in hideColumns
			for column in eventColumns:
				self.treeview.column(column, width=20)
				self.treeview.heading(column, text=column, command=lambda c=column: self.sort_column(c, False))
				if column in displaycolumns_:
					displaycolumns.append(column)
	
			# set some column widths, width is in pixels?
			self.treeview.column('index', minwidth=50, width=50, stretch="no")
			self.treeview.column('typeNum', minwidth=50, width=50, stretch="no")

			# hide some columns
			print('bEventTree.populateEvent() displaycolumns:', displaycolumns)
			self.treeview["displaycolumns"] = displaycolumns

			self.treeview.bind('<<TreeviewSelect>>', self.single_click)

		# first delete entries
		for i in self.treeview.get_children():
			self.treeview.delete(i)

		# todo: make bEventList iterable
		for idx, event in enumerate(self.eventList.eventList):
			position = "end"
			self.treeview.insert("" , position, text=str(idx+1), values=event.asTuple())

	def single_click(self, event):
		"""
		On single click in event list tree --> Set the video to a frame
		event: <ButtonRelease event state=Button1 num=1 x=227 y=64>
		"""
		print('=== bEventTree.single_click()')
		frameStart, item = self._getTreeViewSelection('frameStart')
		frameStart = float(frameStart) # need first because frameNumber (str) can be 100.00000000001
		frameStart = int(frameStart)
		print('   event_tree_single_click() is progressing to frameStart:', frameStart)
		#self.vs.setFrame(frameStart) # set the video frame
		self.myParentApp.setFrame(frameStart) # set the video frame
		
	def appendEvent(self, newEvent):
		# get a tuple (list) of item names in event tree view
		children = self.treeview.get_children()
		numInList = len(children)

		# append to end of list in tree view
		position = "end"
		numInList += 1
		text = str(numInList)
		#print('newEvent.asTuple():', newEvent.asTuple())
		self.treeview.insert("" , position, text=text, values=newEvent.asTuple())

		# interface
		# visually select row
		self.treeview._selectTreeViewRow('index', newEvent.dict['index'])		
		# scroll to bottom of event tree
		self.treeview.yview_moveto(1) # 1 is fractional

	def editNote(self):

		print('bEventTree.editNote()')
		
		# grab the note of selected event
		self.item = self.treeview.focus()
		if self.item == '':
			print('bEventTree.editNote() please select an event')
			return None
		columns = self.treeview['columns']				
		noteColIdx = columns.index('note') # assuming 'note' exists
		values = self.treeview.item(self.item, "values")
		self.index = int(values[0]) # assuming [0] is index
		noteStr = values[noteColIdx]
		
		print('original note is noteStr:', noteStr)

		# to make modal
		#self.grab_set()
		# see: http://effbot.org/tkinterbook/tkinter-dialog-windows.htm
		
		self.top = tkinter.Toplevel(self.myParent)
		
		#top.focus_force() # added
		#top.grab_set()
		
		tkinter.Label(self.top, text="Note").pack()

		#
		self.e = tkinter.Entry(self.top)
		#self.e.delete(0, "end")
		self.e.insert(0, noteStr)
		
		self.e.bind('<Key-Return>', self.editNote_okKeyboard_Callback)
		self.e.focus_set()
		self.e.pack(padx=5)

		cancelButton = tkinter.Button(self.top, text="Cancel", command=self.editNote_cancelButton_Callback)
		cancelButton.pack(side="left", pady=5)
		
		okButton = tkinter.Button(self.top, text="OK", command=self.editNote_okButton_Callback)
		okButton.pack(side="left", pady=5)

	def editNote_cancelButton_Callback(self):
		print('cancelButton_Callback()')
		self.top.destroy()
		
	def editNote_okKeyboard_Callback(self, event):
		print('okKeyboard_Callback()')
		#print("value is:", self.e.get())
		self.editNote_okButton_Callback()
		
	def editNote_okButton_Callback(self):
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

###################################################################################
class bVideoFileTree(bTree):
	def __init__(self, parent, parentApp, videoFileList, *args, **kwargs):
		bTree.__init__(self, parent, parentApp, *args, **kwargs)
		
		self.videoFileList = videoFileList # bVideoList object

	def populateVideoFiles(self, videoFileList, doInit=False):
		print('bVideoFileTree.populateVideoFiles()')
		
		self.videoFileList = videoFileList # bVideoList object

		if doInit:
			videoFileColumns = self.videoFileList.getColumns()
			
			# configure columns
			self.treeview['columns'] = videoFileColumns
			hideColumns = ['path'] # hide some columns
			displaycolumns = [] # build a list of columns not in hideColumns
			for column in videoFileColumns:
				self.treeview.column(column, width=10)
				self.treeview.heading(column, text=column, command=lambda c=column: self.sort_column(c, False))
				if column not in hideColumns:
					displaycolumns.append(column)

			# set some column widths, width is in pixels?
			self.treeview.column('index', width=5)
			
			# set some column widths, width is in pixels?
			#gVideoFileColumns = ('index', 'path', 'file', 'width', 'height', 'frames', 'fps', 'seconds', 'numevents', 'note')
			defaultWidth = 80
			self.treeview.column('index', minwidth=50, width=50, stretch="no")
			self.treeview.column('file', width=150)
			self.treeview.column('width', minwidth=defaultWidth, width=defaultWidth, stretch="no")
			self.treeview.column('height', minwidth=defaultWidth, width=defaultWidth, stretch="no")
			self.treeview.column('frames', minwidth=defaultWidth, width=defaultWidth, stretch="no")
			self.treeview.column('fps', minwidth=defaultWidth, width=defaultWidth, stretch="no")
			self.treeview.column('seconds', minwidth=defaultWidth, width=defaultWidth, stretch="no")
			self.treeview.column('numevents', minwidth=defaultWidth, width=defaultWidth, stretch="no")
			
			# hide some columns
			self.treeview["displaycolumns"] = displaycolumns
			
			self.treeview.bind("<ButtonRelease-1>", self.single_click)

			# right-click popup
			# see: https://stackoverflow.com/questions/12014210/tkinter-app-adding-a-right-click-context-menu
			self.popup_menu = tkinter.Menu(self.treeview, tearoff=0)
			self.popup_menu.add_command(label="Set Note",
										command=self.setNote)
			self.treeview.bind("<Button-2>", self.popup)
			self.treeview.bind("<Button-3>", self.popup) # Button-2 on Aqua
		
		# first delete entries
		for i in self.treeview.get_children():
			self.treeview.delete(i)

		for idx, videoFile in enumerate(self.videoFileList.getList()):
			position = "end"
			self.treeview.insert("" , position, text=str(idx+1), values=videoFile.asTuple())

	def single_click(self, event):
		""" display events """
		print('=== bVideoFileTree.single_click()')		
		
		# get video file path
		path, item = self._getTreeViewSelection('path')
		print('   path:', path)

		# switch video stream
		self.myParentApp.switchvideo(path, paused=True, gotoFrame=0)
		
		"""
		# switch event list
		self.eventList = bEventList.bEventList(path)
		
		# populate event list tree
		self.populateEvents()
		
		# set feedback frame
		self.numFrameLabel['text'] = 'of ' + str(self.vs.streamParams['numFrames'])
		self.numSecondsLabel['text'] = 'of ' + str(self.vs.streamParams['numSeconds'])
		
		# set frame slider
		self.video_frame_slider['to'] = self.vs.streamParams['numFrames']
		"""

	def setNote(self):
		print('bVideoFileTree.setNote() not implemented')
		#self.selection_set(0, 'end')

	def popup(self, event):
		print('popup()')
		try:
			self.popup_menu.tk_popup(event.x_root, event.y_root) #, 0)
		finally:
			self.popup_menu.grab_release()
		

###################################################################################
if __name__ == '__main__':
	print('testing')
	
	myPadding = 5
	
	# fire up a small tkinter app
	import tkinter
	root = tkinter.Tk()

	# load an event list
	firstVideoPath = '/Users/cudmore/Dropbox/PiE/video/1-homecage-movie.mp4'
	eventList = bEventList.bEventList(firstVideoPath)
	
	# this will not work because we do not have VideoApp parent app
	"""
	et = bEventTree(root, parentApp, eventList)
	et.grid(row=0,column=0, sticky="nsew", padx=myPadding, pady=myPadding)
	
	et.populateEvents(eventList, doInit=True)
	"""
	
	root.mainloop()
	