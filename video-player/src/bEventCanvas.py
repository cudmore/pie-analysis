# Robert H Cudmore
# 20181206

import tkinter
from tkinter import ttk

# a subclass of Canvas for dealing with resizing of windows
class bEventCanvas(tkinter.Canvas):
	def __init__(self, parentApp, parent,**kwargs):
		self.parentApp = parentApp
		
		width = 1000
		height = 100
		
		self.numFrames = 54000
		
		tkinter.Canvas.__init__(self, parent, width=width, height=height, background='snow4', **kwargs)
		#self.bind("<Configure>", self.on_resize)
		self.height = self.winfo_reqheight()
		self.width = self.winfo_reqwidth()

		self.rowHeight = 18

		self.frameSliderLeft = None
		self.chunkFrameOffset = 0
		self.selectedEventRectID = None
		
		self.chunkList = None
		self.myEventRectList = [] # not used
		
	def on_resize2(self, yPos, width, height):
		# determine the ratio of old width/height to new width/height
		wscale = float(width)/self.width
		hscale = float(height)/self.height
		
		if self.width==width and self.height==height:
			return 0
		
		#print('bEventCanvas.on_resize2()')
		self.width = width
		self.height = height
		
		# resize the canvas 
		# the width is controlle by grid, if set here, canvas will grow like an animation
		#self.config(width=self.width, height=self.height)
		
		#self.config(y=yPos, width=self.width, height=self.height)
		self.place(y=yPos, width=self.width, height=self.height)
		#self.place(width=self.width, height=self.height)
		
		# rescale all the objects tagged with the "all" tag
		self.scale("all", 0, 0, wscale, hscale)
			
	def refreshWithEventTree(self, eventTree):
		"""
		the original chunk json data is in
		self.eventTree.myParentApp.chunkView.chunkData['chunks']
		"""
		print('=== bEventCanvas.refreshWithEventTree()')

		# delete all existing canvas objects
		self.delete("all")
		
		self.eventTree = eventTree
		
		# self.chunkList
		# self.eventRectDict
		
		#myCurrentChunk = self.eventTree.myParentApp.myCurrentChunk
		myCurrentChunk = self.parentApp.myCurrentChunk
		print('   myCurrentChunk:', myCurrentChunk)
		if myCurrentChunk is not None:
			# show one chunk
			self.chunkFrameOffset = myCurrentChunk['startFrame']
			self.numFrames = myCurrentChunk['stopFrame'] - myCurrentChunk['startFrame'] + 1
		else:
			# show entire file
			self.chunkFrameOffset = 0
			self.numFrames = self.parentApp.vs.getParam('numFrames')
			
			# build a list of chunk start/stop frame in this file
			filePath = self.parentApp.vs.getParam('path')
			self.chunkList = []
			#if self.eventTree.myParentApp.chunkView.chunkData is not None:
			if self.parentApp.chunkView.chunkData is not None:
				#for chunk in self.eventTree.myParentApp.chunkView.chunkData['chunks']:
				# don't iterate absolut chunk
				#for chunk in self.parentApp.chunkView.chunkData['chunks']:
				# iterate random chunk order
				"""
				for idx, chunkIndex in enumerate(self.parentApp.chunkView.chunkData['chunkOrder']):
					print('chunkIndex:', chunkIndex)
					chunk = self.parentApp.chunkView.chunkData['chunks'][chunkIndex]
					if chunk['path'] == filePath:
						#print('appending chunk:', chunk)
						self.chunkList.append(chunk)
				"""
				for chunk in self.parentApp.chunkView.chunkData['chunks']:
					if chunk['path'] == filePath:
						#print('appending chunk:', chunk)
						self.chunkList.append(chunk)
				
		events = self.eventTree.treeview.get_children()

		if len(events) > 0:
			self.rowHeight = int(self.height / len(events))
		
		t = 0
		b = t + self.rowHeight
		canvas_height = len(events) * self.rowHeight

		self.eventRectDict = {}
		
		#
		# append all chunk in file
		genericDict = {}
		if myCurrentChunk is None:
			textTop = 0
			for idx, chunk in enumerate(self.chunkList):
				randomIndex = chunk['randomIndex'] # random chunk interface, shown in interface
				startFrame = chunk['startFrame']
				stopFrame = chunk['stopFrame']
				l = startFrame * self.width / self.numFrames
				t = 0
				r = stopFrame * self.width / self.numFrames
				b = self.height

				genericDict = {
					'idx': idx,
					'randomIndex': randomIndex,
					'typeNum': None,
					'frameStart': startFrame,
					'frameStop': stopFrame,
					'eventListIdx': None,
					'l': l,
					't': t,
					'r': r,
					'b': b
				}

				currentTag = 'chunk' + str(idx)
				id = self.create_rectangle(l, t, r, b, fill='darkslategray', width=0, tags=currentTag)
				self.tag_bind(id, "<Button-1>", self.onObjectClick)
				self.myEventRectList.append(id)
				self.eventRectDict[id] = genericDict

				# hold off on this, my list of chunks (in randomChunks.txt) are in 'file' order but not 'frame order'
				"""
				# chunk number
				print('text l:', l)
				textTag = 'textTag' + str(idx)
				#textTop = t + ( (b-t) / 2 )
				textTop += 12
				if textTop > self.height:
					print('resetting textTop self.height:', self.height)
					textTop = 0
				textLeft = l + ( (r-l) / 2 ) - 5 # -6 for width of text
				id = self.create_text(textLeft, textTop, anchor="w", text=genericDict['randomIndex'], tags=textTag)
				self.tag_bind(id, "<Button-1>", self.onObjectClick)
				self.myEventRectList.append(id)
				self.eventRectDict[id] = genericDict
				"""
				
		# frame slider
		top = 0
		bottom = b
		frameSliderWidth = 3
		if self.frameSliderLeft is not None:
			left = self.frameSliderLeft
			right = self.frameSliderLeft
		else:
			left = frameSliderWidth
			right = frameSliderWidth
		self.myFrameSlider = self.create_line(left, top, right, bottom, fill="gold", width=frameSliderWidth, tags='frameSlider')
		self.tag_bind(self.myFrameSlider, "<Button-1>", lambda x: self.frameSlider_Callback)

		# append all events
		prevEventDict = None
		for idx, event in enumerate(events):
			eventDict = eventTree.treeview.set(event) # set is actually get
			
			frameStart0 = int(eventDict['frameStart']) #- self.chunkFrameOffset
			frameStart = int(eventDict['frameStart']) - self.chunkFrameOffset
			if eventDict['frameStop']:
				frameStop0 = int(eventDict['frameStop']) #- self.chunkFrameOffset
				frameStop = int(eventDict['frameStop']) - self.chunkFrameOffset
			else:
				frameStop0 = None
				frameStop = None
				
			l = frameStart * self.width / self.numFrames
			if frameStop is not None:
				r = frameStop * self.width / self.numFrames
			else:
				r = l

			genericDict = {
				'idx': idx,
				'randomIndex': None,
				'typeNum': eventDict['typeNum'],
				'frameStart': frameStart0,
				'frameStop': frameStop0,
				'eventListIdx': int(eventDict['index']),
				'l': l,
				't': t,
				'r': r,
				'b': b
			}
			
			# event rectangle
			currentTag = 'e' + str(idx)
			if r < l:
				eventColor = 'indianred1'
			else:
				eventColor='gray'
			id = self.create_rectangle(l, t, r, b, fill=eventColor, width=0, tags=currentTag)
			self.tag_bind(id, "<Button-1>", self.onObjectClick)
			self.myEventRectList.append(id)
			self.eventRectDict[id] = genericDict
			
			# rectangle showing overlap
			if prevEventDict is not None:
				# only if prev and this have frameStop
				if eventDict['frameStop'] and prevEventDict['frameStop']:
					#prevEventDict = eventTree.treeview.set(prevEvent) # set is actually get
					rPrev = max(int(float(prevEventDict['frameStart'])), int(float(prevEventDict['frameStop'])))
					rPrev -= self.chunkFrameOffset
					#print(eventDict['frameStart'])
					#print(eventDict['frameStop'])
					lThis = min(int(float(eventDict['frameStart'])), int(float(eventDict['frameStop'])))
					lThis -= self.chunkFrameOffset
					if lThis < rPrev:
						# colorize
						rPrev = rPrev * self.width / self.numFrames
						lThis = lThis * self.width / self.numFrames
						eventColor = 'blue'
						currentTag = 'overlap' + str(idx)
						id = self.create_rectangle(lThis, t, rPrev, b, fill=eventColor, width=0, tags=currentTag)
						self.tag_bind(id, "<Button-1>", self.onObjectClick)
						self.myEventRectList.append(id)
						self.eventRectDict[id] = genericDict
						
			# event number
			if myCurrentChunk is not None:
				textTag = 'textTag' + str(idx)
				textTop = t + ( (b-t) / 2 )
				textLeft = l + ( (r-l) / 2 ) - 5 # -6 for width of text
				id = self.create_text(textLeft, textTop, anchor="w", text=genericDict['typeNum'], tags=textTag)
				self.tag_bind(id, "<Button-1>", self.onObjectClick)
				self.myEventRectList.append(id)
				self.eventRectDict[id] = genericDict
			
			# vertical line at end of event
			if frameStop is not None:
				id = self.create_line(r, t, r, b, fill="red", width=2)
				self.tag_bind(id, "<Button-1>", self.onObjectClick)
				self.myEventRectList.append(id)
				self.eventRectDict[id] = genericDict

			# vertical line at start of event
			id = self.create_line(l, t, l, b, fill="green", width=2)
			self.tag_bind(id, "<Button-1>", self.onObjectClick)
			self.myEventRectList.append(id)
			self.eventRectDict[id] = genericDict


			# horizontal line below
			left = 1
			right = self.width
			id = self.create_line(left, b, right, b, fill="gray", width=1)
			#self.tag_bind(id, "<Button-1>", self.onObjectClick)
			#self.myEventRectList.append(id)
			#self.eventRectDict[id] = genericDict

			t += self.rowHeight
			b += self.rowHeight
			prevEventDict = eventDict
			
		# gold selection
		"""
		self.selectedEventRectID = self.create_rectangle(0, 0, 0, 0, fill="gold", width=0, tags='eventSelection')
		self.tag_bind(self.selectedEventRectID, "<Button-1>", self.onObjectClick)
		self.myEventRectList.append(self.selectedEventRectID)
		self.eventRectDict[self.selectedEventRectID] = genericDict
		"""

		self.addtag_all("all")
			
	def onObjectClick(self, event):
		id = event.widget.find_closest(event.x, event.y)
		print('=== bEventCanvas.onObjectClick()', event.x, event.y, 'id:', id)
	
		if len(id) < 1:
			return 0
		
		id = id[0]
		print(self.eventRectDict[id])
		#frameStart= self.eventRectDict[id]['frameStart']
		eventIndex= self.eventRectDict[id]['idx']
		randomIndex = self.eventRectDict[id]['randomIndex'] # will be None for events
		
		# make a rectangle selection
		if self.selectedEventRectID is not None:
			self.delete(self.selectedEventRectID)

		# two kinds of selection: chunks and events
		if randomIndex is not None:
			# select a chunk
			print('=== user selected random chunk:', randomIndex)
			chunkRectangle = 'chunk' + str(eventIndex)
			chunkCoords = self.coords(chunkRectangle)
			l = chunkCoords[0]
			t = chunkCoords[1]
			r = chunkCoords[2]
			b = chunkCoords[3]
			
			# todo: need to fill in randomIndex in chunk view
			self.parentApp.chunkView._chunk_goto2(randomIndex)
			
		else:
			# select an event
			eventRectangle = 'e' + str(eventIndex)
			eventCoords = self.coords(eventRectangle)
			l = eventCoords[0]
			t = eventCoords[1]
			r = eventCoords[2]
			b = eventCoords[3]
		
		# can not use these as they are not scaled when widget resizes
		"""
		l = self.eventRectDict[id]['l']
		t = self.eventRectDict[id]['t']
		r = self.eventRectDict[id]['r']
		b = self.eventRectDict[id]['b']
		"""
		
		# todo: make tag reflect either (chunk or event)
		self.selectedEventRectID = self.create_rectangle(l, t, r, b, fill="yellow", width=0, tags='eventSelection')
		"""
		print('ltrb:', l, t, r, b)
		self.coords(self.selectedEventRectID, l, t, l, b)
		"""
		
		# raise text tag of selected event
		textTag = 'textTag' + str(eventIndex)
		self.tag_raise(textTag)
		
		# go to first frame of event
		newFrame = self.eventRectDict[id]['frameStart']
		if randomIndex is not None:
			#self.eventTree.myParentApp.setFrame(newFrame)
			self.parentApp.setFrame(newFrame)
		else:
			eventListIdx = self.eventRectDict[id]['eventListIdx']
			if eventListIdx is not None:
				self.eventTree._selectTreeViewRow('index', eventListIdx)

	def setFrame(self, theFrame):
		theFrame -= self.chunkFrameOffset
		left = int(theFrame) * self.width / self.numFrames
		#print('=== bEventCanvas.setFrame() left:', left, 'self.chunkFrameOffset:', self.chunkFrameOffset)

		if left<=0:
			left = 5
		
		self.frameSliderLeft = left
		
		top = 0
		bottom = self.height #top + 200
		self.coords('frameSlider', left, top, left, bottom)
		
	
	def frameSlider_Callback(self):
		print('=== bEventCanvas.frameSlider_Callback()')
	
		
if __name__ == "__main__":
	pass
