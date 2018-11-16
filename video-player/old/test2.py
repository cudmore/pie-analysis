import threading

import numpy as np

from PIL import Image
from PIL import ImageTk

import tkinter
from tkinter import ttk

# see: https://stackoverflow.com/questions/16523128/resizing-tkinter-frames-with-fixed-aspect-ratio
def set_aspect(content_frame, pad_frame, aspect_ratio):
    # a function which places a frame within a containing frame, and
    # then forces the inner frame to keep a specific aspect ratio

    def enforce_aspect_ratio(event):
        # when the pad window resizes, fit the content into it,
        # either by fixing the width or the height and then
        # adjusting the height or width based on the aspect ratio.

        # start by using the width as the controlling dimension
        desired_width = event.width
        desired_height = int(event.width / aspect_ratio)

        # if the window is too tall to fit, use the height as
        # the controlling dimension
        if desired_height > event.height:
            desired_height = event.height
            desired_width = int(event.height * aspect_ratio)

        # place the window, giving it an explicit size
        content_frame.place(in_=pad_frame, x=0, y=0, 
            width=desired_width, height=desired_height)

    pad_frame.bind("<Configure>", enforce_aspect_ratio)

root = tkinter.Tk()

pane = tkinter.PanedWindow(root, orient=tkinter.VERTICAL)
pane.grid(row=0, column=0, sticky="nsew")
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

upper_frame = tkinter.Frame(pane)
upper_frame.grid(row=0, column=0, sticky="nsew")

left_buttons_frame = tkinter.Frame(upper_frame, background="bisque", width=100, height=100)
left_buttons_frame.grid(row=0, column=0)

def myButtonCallback():
	print('myButtonCallback')

loadButton = tkinter.Button(left_buttons_frame, anchor="n", text="Folder", command=myButtonCallback)
loadButton.pack()

left_tree = ttk.Treeview(upper_frame, padding=(25,25,25,25))
left_tree.grid(row=0,column=1, sticky="nsew")
for i in range(20):
	left_tree.insert("", "end", text=str(i))

right_tree = ttk.Treeview(upper_frame, padding=(25,25,25,25))
right_tree.grid(row=0,column=2, sticky="nsew")
for i in range(20):
	right_tree.insert("", "end", text=str(i))

upper_frame.grid_rowconfigure(0,weight=1) # 
upper_frame.grid_columnconfigure(2,weight=1) # 

# video
lower_frame = tkinter.Frame(pane, borderwidth=5, width=640, height=480)
lower_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")
lower_frame.grid_rowconfigure(0,weight=1) # 
lower_frame.grid_columnconfigure(0,weight=1) # 

# use set_aspect() with pad and content
pad_frame = tkinter.Frame(lower_frame, borderwidth=0, background="bisque", width=200, height=200)
pad_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=20)
content_frame=tkinter.Frame(lower_frame, borderwidth=5,relief=tkinter.GROOVE, background="blue")
set_aspect(content_frame, pad_frame, aspect_ratio=4.0/3.0) 

# insert image into content frame
height = 480 #480
width = 640 #640
image = np.zeros((height,width,3), np.uint8)
image = Image.fromarray(image)
image = ImageTk.PhotoImage(image)
videoPanel = tkinter.Label(content_frame, image=image)
videoPanel.grid(row=0, column=0, sticky="nsew")
videoPanel.image = image

#
# insert video
from FileVideoStream import FileVideoStream

videoPath = '/Users/cudmore/Dropbox/PiE/homecage-movie.mp4'
vs = FileVideoStream(videoPath) #.start()
vs.start()

path = vs.streamParams['path']
fileName = vs.streamParams['fileName']
width = vs.streamParams['width']
height = vs.streamParams['height']
fps = vs.streamParams['fps']
numFrames = vs.streamParams['numFrames']

# start a thread that constantly pools the video file for the most recently read frame
#self.stopEvent = threading.Event()
isRunning = True
thread = threading.Thread(target=videoLoop, args=())
thread.daemon = True
thread.start()

##
# main
##
pane.add(upper_frame)
pane.add(lower_frame, stretch="always")
#pane.add(lower_tree, stretch="always")

root.geometry("640x480")
root.mainloop()