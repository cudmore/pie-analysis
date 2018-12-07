# Robert H Cudmore
# 20181206

import tkinter
from tkinter import ttk

# a subclass of Canvas for dealing with resizing of windows
class bEventCanvas(tkinter.Canvas):
	def __init__(self,parent,**kwargs):
		width = 1000
		height = 100
		
		self.numFrames = 54000
		
		tkinter.Canvas.__init__(self,parent,width=width, height=height, **kwargs)
		#self.bind("<Configure>", self.on_resize)
		self.height = self.winfo_reqheight()
		self.width = self.winfo_reqwidth()

		self.rowHeight = 10

		self.frameSliderLeft = None
		self.myEventRectList = []
		self.chunkFrameOffset = 0
		self.selectedEventRectID = None
		
	def on_resize2(self, width, height):
		# determine the ratio of old width/height to new width/height
		wscale = float(width)/self.width
		hscale = float(height)/self.height
		
		if self.width==width and self.height==height:
			return 0
		
		#print('bEventCanvas.on_resize2()')
		self.width = width
		self.height = height
		
		# resize the canvas 
		#self.config(width=self.width, height=self.height)
		
		# rescale all the objects tagged with the "all" tag
		self.scale("all", 0, 0, wscale, hscale)
			
	def refreshWithEventTree(self, eventTree):
		print('=== bEventCanvas.refreshWithEventTree()')

		self.delete("all")
		
		self.eventTree = eventTree
		
		myCurrentChunk = self.eventTree.myParentApp.myCurrentChunk
		print('   myCurrentChunk:', myCurrentChunk)
		if myCurrentChunk is not None:
			self.chunkFrameOffset = myCurrentChunk['startFrame']
			self.numFrames = myCurrentChunk['stopFrame'] - myCurrentChunk['startFrame'] + 1
		else:
			self.chunkFrameOffset = 0
			self.numFrames = self.eventTree.myParentApp.vs.getParam('numFrames')

		events = self.eventTree.treeview.get_children()

		t = 0
		b = t + self.rowHeight
		canvas_height = len(events) * self.rowHeight

		self.eventRectDict = {}
		
		# frame slider
		top = 0
		bottom = b
		frameSliderWidth = 5
		if self.frameSliderLeft is not None:
			left = self.frameSliderLeft
			right = self.frameSliderLeft
		else:
			left = frameSliderWidth
			right = frameSliderWidth
		self.myFrameSlider = self.create_line(left, top, right, bottom, fill="gold", width=frameSliderWidth, tags='frameSlider')
		self.tag_bind(self.myFrameSlider, "<Button-1>", lambda x: self.frameSlider_Callback)

		for idx, event in enumerate(events):
			eventDict = eventTree.treeview.set(event)
			
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
			id = self.create_rectangle(l, t, r, b, fill="gray", width=0, tags=currentTag)
			self.tag_bind(id, "<Button-1>", self.onObjectClick)
			self.myEventRectList.append(id)
			self.eventRectDict[id] = genericDict
			
			# event number
			if myCurrentChunk is not None:
				textTop = t + ( (b-t) / 2 )
				textLeft = l + ( (r-l) / 2 )
				id = self.create_text(textLeft, textTop, anchor="w", text=genericDict['typeNum'])
				self.tag_bind(id, "<Button-1>", self.onObjectClick)
				self.myEventRectList.append(id)
				self.eventRectDict[id] = genericDict
			
			# vertical line at start of event
			id = self.create_line(l, t, l, b, fill="green", width=2)
			self.tag_bind(id, "<Button-1>", self.onObjectClick)
			self.myEventRectList.append(id)
			self.eventRectDict[id] = genericDict


			# vertical line at end of event
			if frameStop is not None:
				id = self.create_line(r, t, r, b, fill="red", width=2)
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
		
		# gold selection
		"""
		self.selectedEventRectID = self.create_rectangle(0, 0, 0, 0, fill="gold", width=0, tags='eventSelection')
		self.tag_bind(self.selectedEventRectID, "<Button-1>", self.onObjectClick)
		self.myEventRectList.append(self.selectedEventRectID)
		self.eventRectDict[self.selectedEventRectID] = genericDict
		"""

		self.addtag_all("all")
			
		
	def setFrame(self, theFrame):
		theFrame -= self.chunkFrameOffset
		left = int(theFrame) * self.width / self.numFrames
		#print('=== bEventCanvas.setFrame() left:', left, 'self.chunkFrameOffset:', self.chunkFrameOffset)

		self.frameSliderLeft = left
		
		top = 0
		bottom = top + 200
		self.coords('frameSlider', left, top, left, bottom)
		
	
	def frameSlider_Callback(self):
		print('=== bEventCanvas.frameSlider_Callback()')
	
	def onObjectClick(self, event):
		id = event.widget.find_closest(event.x, event.y)
		print('=== bEventCanvas.onObjectClick()', event.x, event.y, 'id:', id)
	
		if len(id) < 1:
			return 0
		
		id = id[0]
		print(self.eventRectDict[id])
		
		# make a rectangle selection
		"""
		if self.selectedEventRectID is not None:
			self.delete(self.selectedEventRectID)
		"""
		l = self.eventRectDict[id]['l']
		t = self.eventRectDict[id]['t']
		r = self.eventRectDict[id]['r']
		b = self.eventRectDict[id]['b']
		self.selectedEventRectID = self.create_rectangle(l, t, r, b, fill="gold", width=0, tags='eventSelection')
		"""
		print('ltrb:', l, t, r, b)
		self.coords(self.selectedEventRectID, l, t, l, b)
		"""
		
		newFrame = self.eventRectDict[id]['frameStart']
		
		#self.eventTree.myParentApp.setFrame(newFrame)
		eventListIdx = self.eventRectDict[id]['eventListIdx']
		self.eventTree._selectTreeViewRow('index', eventListIdx)
		
if __name__ == "__main__":
	pass
