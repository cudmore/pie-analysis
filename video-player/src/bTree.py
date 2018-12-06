# Robert Cudmore
# 20181127

"""
self.eventTree
"""

import numpy as np

import tkinter
from tkinter import ttk
from tkinter import messagebox

import bEventList
import bDialog

###################################################################################
class bTree(ttk.Frame):
	def __init__(self, parent, parentApp, *args, **kwargs):
		ttk.Frame.__init__(self, parent)
		
		self.myParentApp = parentApp
		self.myParent = parent
		
		myPadding = 5

		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(0, weight=1)

		self.treeview = ttk.Treeview(self, selectmode="browse", show=['headings'], *args, **kwargs)
		self.treeview.grid(row=0,column=0, sticky="nsew", padx=myPadding, pady=myPadding)

		self.scrollbar = ttk.Scrollbar(self, orient="vertical", command = self.treeview.yview)
		self.scrollbar.grid(row=0, column=0, sticky='nse', padx=myPadding, pady=myPadding)
		self.treeview.configure(yscrollcommand=self.scrollbar.set)

	def sort_column(self, col, reverse):
		print('=== bTree.sort_column()()', 'col:', col, 'reverse:', reverse)

		sortType = 'float'
		if col in ['file', 'note']:
			sortType = 'str'
			#print('   not allowed to sort on:', col)
			#return 0
		
		itemList = self.treeview.get_children()
		
		frameStartList = []
		valuesList = [] # list of each rows 'values'
		for item in self.treeview.get_children(''):
			# set() here is actually getting row as dict (names are column name)
			itemColValue = self.treeview.set(item, col) # itemColValue is always a string
			if sortType == 'str':
				currentFrameStart = itemColValue # itemColValue is a str
			else:
				if itemColValue:
					currentFrameStart = float(itemColValue)
				else:
					# handles empy string ''
					currentFrameStart = np.NaN
			frameStartList.append(currentFrameStart)

			values = self.treeview.item(item, 'values')
			valuesList.append(values)
			
		#print('frameStartList:', frameStartList)
		
		sortOrder = np.argsort(frameStartList).tolist()
		
		if reverse:
			sortOrder = list(reversed(sortOrder))
		
		#print('sortOrder:', sortOrder)
		
		"""
		# get current selection
		selectedIndex, selectedItem = self._getTreeViewSelection('index')
		"""
		
		# first delete entries
		"""for i in self.treeview.get_children():
			self.treeview.delete(i)
		"""
		
		# re-insert in proper order
		for idx, i in enumerate(sortOrder):
			#event = self.eventList.eventList[i]
			position = idx
			values = valuesList[i]
			#self.treeview.insert("" , position, text=str(idx+1), values=values)
			self.treeview.move(itemList[i], '', idx)
			
		# re-select original selection
		#print('selectedIndex:', selectedIndex, type(selectedIndex))
		"""
		if selectedIndex is not None:
			selectedIndex = int(selectedIndex)
			self._selectTreeViewRow('index', selectedIndex)
		"""
		
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
		Given a column name (col) and a value (isThis)
		Visually select the row in tree view that has column mathcing isThis
		
		col: (str) column name
		isThis: (str) value of a cell in column (col)
		"""
		if not isinstance(isThis, str):
			print('warning: _selectTreeViewRow() expecting string isThis, got', type(isThis))
		
		theRow, theItem = self._getTreeViewRow(col, isThis)
		
		if theRow is not None:
			# get the item
			children = self.treeview.get_children()
			item = children[theRow]
			#print('item:', item)
			
			# select the row
			self.treeview.focus(item) # select internally
			self.treeview.selection_set(item) # visually select
		else:
			print('warning: _selectTreeViewRow() did not find row for col:', col, 'matching:', isThis, type(isThis))
			
	def _getTreeViewRow(self, col, isThis):
		"""
		Given a treeview, a col name and a value (isThis)
		Return the row index of the column col matching isThis
		"""
		if not isinstance(isThis, str):
			print('warning: _getTreeViewRow() expecting string isThis, got', type(isThis))

		#print('_getTreeViewRow col:', col, 'isThis:', isThis)

		# get the tree view columns and find the col we are looking for
		columns = self.treeview['columns']				
		try:
			colIdx = columns.index(col) # assuming 'frameStart' exists
		except (ValueError):
			print('warning: _getTreeViewRow() did not find col:', col)
			colIdx = None
					
		theRet = None
		theItem = None
		if colIdx is not None:
			rowIdx = 0
			for child in self.treeview.get_children():
				values = self.treeview.item(child)["values"] # values at current row
				#print('type(values[colIdx])', type(values[colIdx]))
				#print('values[colIdx]: "' + values[colIdx] + '"', 'looking for isThis "' + isThis + '"')
				if values[colIdx] == isThis:
					theRet = rowIdx
					theItem = child
					break
				rowIdx += 1
		#else:
		#	print('_getTreeViewRow() did not find col:', col)
		
		return theRet, theItem
		

###################################################################################
class bEventTree(bTree):
	def __init__(self, parent, parentApp, videoFilePath='', *args, **kwargs):
		bTree.__init__(self, parent, parentApp, *args, **kwargs)
		
		#self.eventList = bEventList.bEventList(videoFilePath)
		self.eventList = None
		self.populateEvents(videoFilePath, doInit=True)
		
	def populateEvents(self, videoFilePath, doInit=False):
		#print('bEventTree.populateEvents() videoFilePath:', videoFilePath)
		
		# not sure if previous version of self.eventList will be deleted?
		self.eventList = bEventList.bEventList(self.myParentApp, videoFilePath)
		
		"""
		eventColumns = ('index', 'path', 'cseconds', 'cDate', 'cTime', 
						'typeNum', 'typeStr', 'frameStart', 'frameStop', 
						'numFrames', 'sStart', 'sStop', 'numSeconds'
						'chunkIndex', 'note')
		"""
		eventColumns = self.eventList.getColumns()
		
		if doInit:
			# configure columns
			self.treeview['columns'] = eventColumns
			displaycolumns_ = ['index', 'typeNum', 'sStart', 'sStop', 'numSeconds', 'rChunkIndex', 'note']
			displaycolumns_ = ['index', 'typeNum', 'frameStart', 'frameStop', 'sStart', 'sStop', 'numSeconds', 'rChunkIndex', 'note']
			displaycolumns = [] # build a list of columns not in hideColumns
			for column in eventColumns:
				self.treeview.column(column, width=20)
				self.treeview.heading(column, text=column, command=lambda c=column: self.sort_column(c, False))
				if column in displaycolumns_:
					displaycolumns.append(column)
	
			# set some column widths, width is in pixels?
			self.treeview.column('index', minwidth=50, width=50, stretch="no")
			self.treeview.column('typeNum', minwidth=50, width=50, stretch="no")

			# rename some columns
			self.treeview.heading('typeNum', text="Type")
			self.treeview.heading('sStart', text="Start")
			self.treeview.heading('sStop', text="Stop")
			self.treeview.heading('numSeconds', text="Dur")
			self.treeview.heading('rChunkIndex', text="Chunk")
			
			# hide some columns
			#print('bEventTree.populateEvent() displaycolumns:', displaycolumns)
			self.treeview["displaycolumns"] = displaycolumns

			# we need this so user scroll up/down triggers selection
			self.treeview.bind('<<TreeviewSelect>>', self.single_click)
			#self.treeview.bind('<ButtonRelease-1>', self.single_click)
			self.treeview.bind("<Key>", self.key)


		# first delete entries
		for i in self.treeview.get_children():
			self.treeview.delete(i)

		# todo: make bEventList iterable
		for idx, event in enumerate(self.eventList.eventList):
			position = "end"
			self.treeview.insert("" , position, text=str(idx+1), values=event.asTuple())

		# this also deletes then inserts (fix it)
		self.sort_column('frameStart', False)
		
	def filter(self, chunkIdx):
		"""
		Only show events with chunkIdx (int).
		Pass chunkIdx as None to show all
		"""
		print('filter() chunkIdx:', chunkIdx, type(chunkIdx))
		
		# first delete entries
		for i in self.treeview.get_children():
			self.treeview.delete(i)

		# todo: make bEventList iterable
		for idx, event in enumerate(self.eventList.eventList):
			currentChunkIndex = self.eventList.get(idx, 'rChunkIndex')
			#print('filter() chunkIdx:', chunkIdx, 'currentChunkIndex:', currentChunkIndex, type(currentChunkIndex))
			print('filter() idx:', idx, 'currentChunkIndex:', currentChunkIndex, type(currentChunkIndex))
			if currentChunkIndex is not None and currentChunkIndex != 'None':
				currentChunkIndex = int(float(currentChunkIndex))
			#print('currentChunkIndex:', type(currentChunkIndex), 'chunkIdx:', type(chunkIdx))
			if chunkIdx is None:
				self.treeview.insert("" , "end", text=str(idx+1), values=event.asTuple())
			elif currentChunkIndex == chunkIdx:
				print('todo: insert with start/stop frame relative to start of chunk')
				self.treeview.insert("" , "end", text=str(idx+1), values=event.asTuple())

		self.sort_column('frameStart', False)
		
	def key(self, event):
		print('\n=== bEventTree.key() event.char: "' +  event.char + '"')
		theKey = event.char
		passToParent = False
		if theKey == '\uf702' and event.state==97:
			# shift + left
			passToParent = True
		elif theKey == '\uf702':
			# left
			passToParent = True
		if theKey == '\uf703' and event.state==97:
			# shift + right
			passToParent = True
		elif theKey == '\uf703':
			# right
			passToParent = True

		if passToParent:
			self.myParentApp.keyPress(event)
			return 'break'
		else:
			return ''
		"""
		if event.char == '\r':
			pass
		else:
			self.myParentApp.keyPress(event)
			return 'break'
		"""
		
	def single_click(self, event):
		"""
		On single click in event list tree --> Set the video to a frame
		event: <ButtonRelease event state=Button1 num=1 x=227 y=64>
		"""
		print('\n=== bEventTree.single_click()', event.x, event.y)
		#region = self.treeview.identify("region", event.x, event.y)
		#print('   region:', region)
		
		frameStart, item = self._getTreeViewSelection('frameStart')
		if frameStart is None and item is  None:
			print('bEventTree.single_click() did not find selection')
			return 0
			
		frameStart = int(float(frameStart)) # need first because frameNumber (str) can be 100.00000000001
		print('   bEventTree.single_click() is progressing to frameStart:', frameStart)
		#self.vs.setFrame(frameStart) # set the video frame
		self.myParentApp.setFrame(frameStart, withDelay=False) # set the video frame
		
	def appendEvent(self, type, frame, chunkIndex=None, randomChunkIndex=None):
		
		newEvent = self.eventList.appendEvent(type, frame, chunkIndex=chunkIndex, randomChunkIndex=randomChunkIndex)
		self.eventList.save()

		# interface
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
		self._selectTreeViewRow('index', newEvent.dict['index'])		
		# scroll to bottom of event tree
		self.treeview.yview_moveto(1) # 1 is fractional

		self.sort_column('frameStart', False)
		
		item = self.treeview.focus()
		self.flagOverlap(item)
		
	def deleteEvent(self):
		print('=== bEventTree.deleteEvent()')
		# get selected event
		index, item = self._getTreeViewSelection('index')
		if index is None or item is None:
			print('   please select an event')
			return 0
			
		# ask user
		result = messagebox.askyesno("Delete Event","Do you want to delete event " + str(index) + "?", icon='warning')
		if not result:
			print('   deleteEvent cancelled by user')
			return 0
			
		print('   deleteEvent() is deleting event index:', index)
		
		# delete from internal list
		index = int(index)
		self.eventList.deleteEvent(index)
		self.eventList.save()
		
		# remove selection
		# 1.1) before we remove, get next item (can be none)
		children = self.treeview.get_children()
		itemIndex = children.index(item)
		if itemIndex < len(children)-1:
			nextItem = children[itemIndex+1]
			print('nextItem:', nextItem)
		else:
			nextItem = None
			
		# 2) remove
		self.treeview.selection_remove(item) # remove visual seleciton
		
		# todo: write wrapper function in VideoApp to tell us about chunk view (don't reference directly)
		# this should represent the 'state' of the video app
		randomIndex = None
		if self.myParentApp.chunkView.isHijacking():
			currentChunk, randomIndex = self.myParentApp.chunkView.getCurrentChunk() # can be nan
			print('bEventTree.deleteEvent() got currentChunk:', currentChunk)
		self.filter(randomIndex)
		
		# visually select the next item
		# 1.2) see 1.1) above
		if nextItem is not None:
			# get children again, invalid after selection_remove
			children = self.treeview.get_children()
			nextItem = children[itemIndex]
			# select the row
			self.treeview.focus(nextItem) # select internally
			self.treeview.selection_set(nextItem) # visually select

	def set(self, col, val):
		"""
		Set a value in selected row of tree
		
		Parameters:
			col: column name in (frameStart, frameStop)
			val: thevalue to set to
		"""
		print('bEventTree().set() col:', col, 'val:', val)

		index, item = self._getTreeViewSelection('index')
		if index is None:
			print('   warning: please select an event')
			return None
			
		print('todo: re-calculate chunk index !!!')
		
		index = int(index)
		print('   modifying event index:', index)
		
		# set in our eventList
		#self.eventList.eventList[index].dict[col] = val
		self.eventList.set(index, col, val)
		self.eventList.save()
		
		# grab event we just set
		event = self.eventList.eventList[index]

		# update treeview with new event
		self.treeview.item(item, values=event.asTuple())

		"""
		# colorize if start/stop out of order
		if col in ['frameStart', 'frameStop']:
			#print('treeview.set() colorize start/stop order')
			frameStart, item = self._getTreeViewSelection('frameStart')
			frameStop, item = self._getTreeViewSelection('frameStop')
			#print('   frameStart:', frameStart, type(frameStart))
			#print('   frameStop:', frameStop, type(frameStop))
			if frameStart and frameStop:
				self.treeview.tag_configure('itemOrange', background='orange')
				#print('   item:', item)
				frameStart = int(frameStart)
				frameStop = int(frameStop)
				if frameStop < frameStart:
					print('   colorize -- out of order')
					self.treeview.item(item, tags='itemOrange')
				else:
					self.treeview.item(item, tags='')
		"""
		
		if col in ['frameStart']:
			self.sort_column('frameStart', False)
			self.flagOverlap(item)
		if col in ['frameStop']:
			self.flagOverlap(item)
		"""
			if index>0:
				prevIndex = index - 1
				prevRowIdx, prevItem = self._getTreeViewRow('index', prevIndex)
				prevItemDict = self.treeview.set(prevItem)
				prevFrameStop = prevItemDict['frameStop']
				
				thisItemDict = self.treeview.set(item)
				thisFrameStart = thisItemDict['frameStart']
				
				self.treeview.tag_configure('itemRed', background='red')
				if thisFrameStart and prevFrameStop:
					if int(thisFrameStart) <= int(prevFrameStop):
						print('setting red thisFrameStart:', thisFrameStart, 'prevFrameStop:', prevFrameStop)
						self.treeview.item(item, tags='itemRed')
					else:
						print('setting normal')
						self.treeview.item(item, tags='')
		"""
		
	def flagOverlap(self, theItem):
		"""
		do this on
			new
			set frame start (look at previous)
			set frame stop (look at next)
		"""
		
		#
		#
		# this is fucked up by empty string
		#
		#
		#
		#
		#
		#
		#
		# this almost works, make it remove/add to 'item' tags
		def removeFromTags(item, this):
			tags = self.treeview.item(item)['tags']
			tags = (tags,)
			print('\nremoveFromTags() tags:', tags, 'type(tags):', type(tags))
			if this in tags:
				tagList = list(tags)
				tagList.remove(this)
				tags = tuple(tagList)
			self.treeview.item(item, tags=tags)
			print('   ', self.treeview.item(item)['tags'])
		def addToTags(item, this):
			tags = self.treeview.item(item)['tags']
			tags = (tags,)
			print('\naddToTags() tags:', tags, 'type(tags):', type(tags))
			if not this in tags:
				tags = tags + (this,)
			self.treeview.item(item, tags=tags)
			print('   ', self.treeview.item(item)['tags'])
			
		children = self.treeview.get_children()
		itemIndex = children.index(theItem)
		
		#returns item as dict which includes ['tags']
		print('self.treeview.item(theItem):', self.treeview.item(theItem))
		# returns item 'values' as dict
		print('self.treeview.set(theItem):', self.treeview.set(theItem))
		
		# colorize if start/stop out of order
		frameStart = self.treeview.set(theItem)['frameStart']
		frameStop = self.treeview.set(theItem)['frameStop']
		if frameStart and frameStop:
			self.treeview.tag_configure('itemOrange', background='orange')
			if int(frameStop) < int(frameStart):
				print('   colorize -- out of order')
				origTags = self.treeview.item(theItem)['tags']
				print('origTags:', origTags)
				#self.treeview.item(theItem, tags='itemOrange')
				#addToTags(theItem, 'itemOrange')
			else:
				#self.treeview.item(theItem, tags='')
				#removeFromTags(theItem, 'itemOrange')
				
		"""
		if col in ['frameStart', 'frameStop']:
			#print('treeview.set() colorize start/stop order')
			frameStart, item = self._getTreeViewSelection('frameStart')
			frameStop, item = self._getTreeViewSelection('frameStop')
			#print('   frameStart:', frameStart, type(frameStart))
			#print('   frameStop:', frameStop, type(frameStop))
			if frameStart and frameStop:
				self.treeview.tag_configure('itemOrange', background='orange')
				#print('   item:', item)
				frameStart = int(frameStart)
				frameStop = int(frameStop)
				if frameStop < frameStart:
					print('   colorize -- out of order')
					self.treeview.item(item, tags='itemOrange')
				else:
					self.treeview.item(item, tags='')
		"""

		# make sure does not overlap with previous
		if itemIndex > 0:
			previousItemIndex = itemIndex - 1
			previousItem = children[previousItemIndex]
			prevItemDict = self.treeview.set(previousItem)
			prevFrameStop = prevItemDict['frameStop'] # str?
			
			theItemStruct = self.treeview.set(theItem)
			thisFrameStart = theItemStruct['frameStart'] # str?
			
			if prevFrameStop and thisFrameStart:
				self.treeview.tag_configure('itemRed', background='red')
				if int(thisFrameStart) <= int(prevFrameStop):
					print('flagOverlap() setting THIS red thisFrameStart:', thisFrameStart, 'prevFrameStop:', prevFrameStop)
					#self.treeview.item(theItem, tags='itemRed')
					#addToTags(theItem, 'itemRed')
				else:
					print('setting normal')
					#self.treeview.item(theItem, tags='')
					#removeFromTags(theItem, 'itemRed')

		# make sure it does not overlap with next
		if itemIndex < len(children) - 1:
			nextItemIndex = itemIndex + 1
			nextItem = children[nextItemIndex]
			nextItemDict = self.treeview.set(nextItem)
			nextFrameStart = nextItemDict['frameStart'] # str?
			
			theItemStruct = self.treeview.set(theItem)
			thisFrameStop = theItemStruct['frameStop'] # str?
			
			if nextFrameStart and thisFrameStop:
				self.treeview.tag_configure('itemRed', background='red')
				if int(thisFrameStop) >= int(nextFrameStart):
					print('flagOverlap() setting NEXT red thisFrameStop:', thisFrameStop, 'nextFrameStart:', nextFrameStart)
					self.treeview.item(nextItem, tags='itemRed')
				else:
					#print('setting normal')
					self.treeview.item(nextItem, tags='')
		
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

		self.myEditNoteIndex = int(values[0]) # assuming [0] is index

		noteStr = values[noteColIdx]
		
		print('original note is noteStr:', noteStr)

		myDialog = bDialog.bNoteDialog(self, noteStr, self.editNote_Callback)
		
		"""
		# to make modal
		#self.grab_set()
		# see: http://effbot.org/tkinterbook/tkinter-dialog-windows.htm
		
		self.top = tkinter.Toplevel(self.myParent)
		
		#top.focus_force() # added
		#top.grab_set()
		
		tkinter.Label(self.top, text="Note").pack()

		#
		self.noteEntryWidget = tkinter.Entry(self.top)
		#self.noteEntryWidget.delete(0, "end")
		self.noteEntryWidget.insert(0, noteStr)
		self.noteEntryWidget.select_range(0, "end")
		
		self.noteEntryWidget.bind('<Key-Return>', self.editNote_okKeyboard_Callback)
		self.noteEntryWidget.focus_set()
		self.noteEntryWidget.pack(padx=5)

		cancelButton = tkinter.Button(self.top, text="Cancel", command=self.editNote_cancelButton_Callback)
		cancelButton.pack(side="left", pady=5)
		
		okButton = tkinter.Button(self.top, text="OK", command=self.editNote_okButton_Callback)
		okButton.pack(side="left", pady=5)
		"""
		
	def editNote_Callback(self, event, newNoteStr):
		print('bTree.editNote_Callback() event:', event, 'newNoteStr:', newNoteStr)
	
		# set in our eventList
		self.eventList.eventList[self.myEditNoteIndex].dict['note'] = newNoteStr
		self.eventList.save()
		
		#todo: pass to edit note dialog constructor and pass back here as parameter
		# get the event we just set
		event = self.eventList.eventList[self.myEditNoteIndex]
		
		# update the tree
		# todo: get this 'item' when we open dialog and use self.item
		#item = self.eventTree.focus()
		self.treeview.item(self.item, values=event.asTuple())

	"""
	def editNote_cancelButton_Callback(self):
		print('cancelButton_Callback()')
		self.top.destroy()
		
	def editNote_okKeyboard_Callback(self, event):
		print('okKeyboard_Callback()')
		#print("value is:", self.noteEntryWidget.get())
		self.editNote_okButton_Callback()
		
	def editNote_okButton_Callback(self):
		print('okButton_Callback()')
		newNote = self.noteEntryWidget.get()
		print("new note is:", newNote)
		
		# set in our eventList
		self.eventList.eventList[self.myEditNoteIndex].dict['note'] = newNote
		self.eventList.save()
		
		# get the event we just set
		event = self.eventList.eventList[self.myEditNoteIndex]
		
		# update the tree
		# todo: get this 'item' when we open dialog and use self.item
		#item = self.eventTree.focus()
		self.treeview.item(self.item, values=event.asTuple())

		#print('bNoteDialog.okButton_Callback() is calling destroy')
		self.top.destroy() # destroy *this, the modal
	"""
	
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
			self.treeview.column('minutes', minwidth=defaultWidth, width=defaultWidth, stretch="no")
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
		#print('   path:', path)

		if path is None:
			# when heading is clicked
			pass
		else:
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
	#eventList = bEventList.bEventList(firstVideoPath)
	
	# this will not work because we do not have VideoApp parent app
	parentApp = None
	et = bEventTree(root, parentApp, firstVideoPath)
	et.grid(row=0,column=0, sticky="nsew", padx=myPadding, pady=myPadding)
	
	#et.populateEvents(eventList, doInit=True)
	
	root.mainloop()
	