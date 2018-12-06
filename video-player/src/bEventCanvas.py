# canvas

import tkinter
from tkinter import ttk

"""
0,/Users/cudmore/Dropbox/PiE/scrambled/s_4022.mp4,1544068926.995682,2018-12-05,23:02:06,1,a,2891,5685,2793,96.46,189.69,93.23,None,None,,,
1,/Users/cudmore/Dropbox/PiE/scrambled/s_4022.mp4,1544068933.7629151,2018-12-05,23:02:13,3,c,45986,49491,3504,1534.4,1651.35,116.95,None,None,,,
2,/Users/cudmore/Dropbox/PiE/scrambled/s_4022.mp4,1544102886.373027,2018-12-06,08:28:06,1,a,17073,,None,569.67,,None,None,None,,
3,/Users/cudmore/Dropbox/PiE/scrambled/s_4022.mp4,1544102888.576926,2018-12-06,08:28:08,2,b,17143,,None,572.0,,None,None,None,,
4,/Users/cudmore/Dropbox/PiE/scrambled/s_4022.mp4,1544102890.894222,2018-12-06,08:28:10,3,c,17256,,None,575.78,,None,None,None,,
"""
videoFile = {
	'vs': {},
	'events': [
	{'startFrame':2891, 'stopFrame':5685},
	{'startFrame':17073, 'stopFrame':19000},
	{'startFrame':45986, 'stopFrame':49491}
	]
}

# a subclass of Canvas for dealing with resizing of windows
class bEventCanvas(tkinter.Canvas):
	def __init__(self,parent,**kwargs):
		width = 1000
		height = 100
		
		self.numFrames = 54000
		
		tkinter.Canvas.__init__(self,parent,width=width, height=height, **kwargs)
		self.bind("<Configure>", self.on_resize)
		self.height = self.winfo_reqheight()
		self.width = self.winfo_reqwidth()

		self.rowHeight = 10

		self.myEventRectList = []
		
	def on_resize(self,event):
		# determine the ratio of old width/height to new width/height
		wscale = float(event.width)/self.width
		hscale = float(event.height)/self.height
		hscale = 1.0
		self.width = event.width
		self.height = event.height
		# resize the canvas 
		self.config(width=self.width, height=self.height)
		# rescale all the objects tagged with the "all" tag
		self.scale("all",0,0,wscale,hscale)

	def setFrame(self, theFrame):
		pass
	
	def populateVideoFile(self, videoFile):
		events = videoFile['events']
		
		t = 0
		b = t + self.rowHeight
		canvas_height = len(events) * self.rowHeight

		self.eventRectDict = {}
		
		for idx, event in enumerate(events):
			print(event)
			l = event['startFrame'] * self.width / self.numFrames
			r = event['stopFrame'] * self.width / self.numFrames
			currentTag = 'e' + str(idx)

			id = self.create_rectangle(l, t, r, b, fill="gray", width=0, tags=currentTag)
			print('id:', id)
			self.myEventRectList.append(id)
			self.eventRectDict[id] = idx
			
			# lambda c=column: self.sort_column(c, False)
			#self.tag_bind(currentTag, "<Button-1>", self.onObjectClick)
			#self.tag_bind(tmp, "<Button-1>", lambda currentTag: self.onObjectClick2(currentTag))
			self.tag_bind(id, "<Button-1>", self.onObjectClick)
			
			# vertical line at end of event
			self.create_line(r, t, r, b, fill="red", width=2)

			# horizontal line below
			left = 1
			right = self.width
			self.create_line(left, b, right, b, fill="gray", width=1)

			t += self.rowHeight
			b += self.rowHeight
		
		# frame slider
		self.myFrameSlider = self.create_line(0, t, 0, b, fill="green", width=5, tags='frameSlider')
		self.tag_bind(self.myFrameSlider, "<Button-1>", lambda x: self.onObjectClick2('xxx'))

		self.addtag_all("all")
		
	def onObjectClick2(self, idx):
		print('onObjectClick2() idx:', idx)
	
	def onObjectClick(self, event):                  
		print('Got object click', event.x, event.y)
		id = event.widget.find_closest(event.x, event.y)
		print(id, self.type(id))
	
		id = id[0]
		print(self.eventRectDict[id])
		
def main():

	
	root = tkinter.Tk()
	root.columnconfigure(0, weight=1)
	root.rowconfigure(0, weight=1)

	myFrame = tkinter.Frame(root)
	myFrame.grid(row=0, column=0, sticky="nsew")
	myFrame.columnconfigure(0, weight=1)
	myFrame.rowconfigure(0, weight=1)
	
	#myCanvas = bEventCanvas(myFrame,bg="gray", highlightthickness=0)
	myCanvas = bEventCanvas(myFrame,highlightthickness=0)
	myCanvas.grid(row=0, column=0, sticky="nsew")

	# add some widgets to the canvas
	"""
	myCanvas.create_line(0, 0, 200, 100)
	myCanvas.create_line(0, 100, 200, 0, fill="red", dash=(4, 4))
	myCanvas.create_rectangle(50, 25, 150, 75, fill="blue")
	"""

	myCanvas.populateVideoFile(videoFile)
	
	# tag all of the drawn widgets
	#myCanvas.addtag_all("all")
	
	root.mainloop()

if __name__ == "__main__":
	main()
