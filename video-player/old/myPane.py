#

import numpy as np

from PIL import Image, ImageTk

import tkinter
from tkinter import ttk
from tkinter import filedialog

import bMenus

def set_aspect(content_frame, pad_frame, video_control_frame, aspect_ratio):
	# a function which places a frame within a containing frame, and
	# then forces the inner frame to keep a specific aspect ratio

	def enforce_aspect_ratio(event):
		# when the pad window resizes, fit the content into it,
		# either by fixing the width or the height and then
		# adjusting the height or width based on the aspect ratio.

		buttonHeight = 36

		# start by using the width as the controlling dimension
		desired_width = event.width - buttonHeight
		#desired_height = int(event.width / aspect_ratio)
		desired_height = int(desired_width / aspect_ratio)

		# if the window is too tall to fit, use the height as
		# the controlling dimension
		if desired_height > event.height:
			desired_height = event.height - buttonHeight
			#desired_width = int(event.height * aspect_ratio)
			desired_width = int(desired_height * aspect_ratio)

		# place the window, giving it an explicit size
		content_frame.place(in_=pad_frame, x=0, y=0, 
			width=desired_width, height=desired_height)

		# place the video controls just below the video frame
		video_control_frame.place(x=0, y=desired_height + buttonHeight, width=desired_width)

		print('winfo_geometry:', root.winfo_geometry())

	pad_frame.bind("<Configure>", enforce_aspect_ratio)


# main
root = tkinter.Tk()

print('windowingsystem:', root.tk.call('tk', 'windowingsystem'))

myPadding = 5
myBorderWidth = 0

gEventColumns = ('index', 'path', 'cseconds', 'type', 'frameStart', 'frameStop', 'note')
gVideoFileColumns = ('index', 'path', 'file', 'width', 'height', 'fps', 'numFrames')

#
# menus
myMenus = bMenus.bMenus(root)

def populatevideo():
	for i in range(20):
		videoFileTree.insert("" , "end", text=str(i), values=(str(i), 'a', 'b', 'c'))

def populateevents():
	for i in range(20):
		eventTree.insert("" , "end", text=str(i), values=(str(i), 'a', 'b', 'c'))


if 1:
	root.grid_rowconfigure(0, weight=1)
	root.grid_columnconfigure(0, weight=1)

	#
	vPane = ttk.PanedWindow(root, orient="vertical")
	vPane.grid(row=0, column=0, sticky="nsew")

	upper_frame = ttk.Frame(vPane, borderwidth=myBorderWidth, relief="sunken")
	upper_frame.grid(row=0, column=0, sticky="nsew", padx=myPadding, pady=myPadding)
	upper_frame.grid_rowconfigure(0, weight=1)
	upper_frame.grid_columnconfigure(0, weight=1)

	videoFileTree = ttk.Treeview(upper_frame, columns=gVideoFileColumns, show='headings')
	videoFileTree.grid(row=0,column=0, sticky="nsew", padx=myPadding, pady=myPadding)
	# configure columns
	for column in gVideoFileColumns:
		videoFileTree.column(column, width=10)
		videoFileTree.heading(column, text=column)
	populatevideo()
	videoFileTree_scrollbar = ttk.Scrollbar(upper_frame, orient="vertical", command = videoFileTree.yview)
	videoFileTree_scrollbar.grid(row=0, column=0, sticky='nse', padx=myPadding, pady=myPadding)
	videoFileTree.configure(yscrollcommand=videoFileTree_scrollbar.set)


	#
	lower_frame = ttk.Frame(vPane, borderwidth=myBorderWidth, relief="sunken")
	#lower_frame.grid(row=0, column=0, sticky="nsew", padx=myPadding, pady=myPadding)
	lower_frame.grid_rowconfigure(0, weight=1)
	lower_frame.grid_columnconfigure(0, weight=1)

	#
	hPane = ttk.PanedWindow(lower_frame, orient="horizontal")
	hPane.grid(row=0, column=0, sticky="nsew")

	lower_left_frame = ttk.Frame(hPane, borderwidth=myBorderWidth, relief="sunken")
	lower_left_frame.grid(row=0, column=0, sticky="nsew", padx=myPadding, pady=myPadding)
	lower_left_frame.grid_rowconfigure(0, weight=1)
	lower_left_frame.grid_columnconfigure(0, weight=1)

	eventTree = ttk.Treeview(lower_left_frame, columns=gEventColumns, show='headings')
	eventTree.grid(row=0,column=0, sticky="nsew", padx=myPadding, pady=myPadding)
	# configure columns
	for column in gEventColumns:
		eventTree.column(column, width=10)
		eventTree.heading(column, text=column)
	# populate rows
	populateevents()
	eventTree_scrollbar = ttk.Scrollbar(lower_left_frame, orient="vertical", command = eventTree.yview)
	eventTree_scrollbar.grid(row=0, column=0, sticky='nse', padx=myPadding, pady=myPadding)
	eventTree.configure(yscrollcommand=eventTree_scrollbar.set)

	#
	lower_right_frame = ttk.Frame(hPane, borderwidth=myBorderWidth, relief="sunken")
	lower_right_frame.grid(row=0, column=0, sticky="nsew", padx=myPadding, pady=myPadding)
	lower_right_frame.grid_rowconfigure(0, weight=0)
	lower_right_frame.grid_rowconfigure(1, weight=0)
	lower_right_frame.grid_rowconfigure(2, weight=1)
	lower_right_frame.grid_rowconfigure(3, weight=0)
	lower_right_frame.grid_columnconfigure(0, weight=1)
	#lower_right_frame.grid_columnconfigure(1, weight=0)


	# video
	myApectRatio = 4.0/3.0
	
	#
	# random chunks
	showRandomChunks = False # toggle this when we load random chunks file
	random_chunks_frame = ttk.Frame(lower_right_frame)
	random_chunks_frame.grid(row=0, column=0, sticky="new")
	# this removes and then re-adds a frame from the grid ... very useful
	if showRandomChunks:
		random_chunks_frame.grid()
	else:
		random_chunks_frame.grid_remove()

	random_chunks_label1 = ttk.Label(random_chunks_frame, text="random param 1")
	random_chunks_label1.grid(row=0, column=0, sticky="nw", padx=myPadding, pady=myPadding)

	random_chunks_label2 = ttk.Label(random_chunks_frame, text="random param 2")
	random_chunks_label2.grid(row=0, column=1, sticky="nw", padx=myPadding, pady=myPadding)
	
	#
	# video feedback
	video_feedback_frame = ttk.Frame(lower_right_frame)
	video_feedback_frame.grid(row=1, column=0, sticky="nw")

	number_of_frames_label = ttk.Label(video_feedback_frame, text="current frame, etc...")
	number_of_frames_label.grid(row=0, column=0, sticky="nw", padx=myPadding, pady=myPadding)

	fps_label = ttk.Label(video_feedback_frame, text="fps")
	fps_label.grid(row=0, column=1, sticky="nw", padx=myPadding, pady=myPadding)

	#
	# video frame
	pad_frame = ttk.Frame(lower_right_frame, borderwidth=0, width=200, height=200)
	pad_frame.grid(row=2, column=0, sticky="nsew", padx=myPadding, pady=myPadding)
	
	contentBorderWidth = 1
	content_frame = ttk.Frame(lower_right_frame, borderwidth=contentBorderWidth, relief="groove")
	content_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
	#content_frame.grid_rowconfigure(0, weight=1)
	#content_frame.grid_columnconfigure(0, weight=1)
	
	# insert image into content frame
	image = np.zeros((480,640,3), np.uint8)
	image = Image.fromarray(image)
	image = ImageTk.PhotoImage(image)
	videoLabel = ttk.Label(content_frame, image=image, text="xxx", font=("Helvetica", 48), compound="center", foreground="green")
	videoLabel.grid(row=0, column=0, sticky="nsew")
	videoLabel.image = image

	#
	# video controls
	video_control_frame = ttk.Frame(lower_right_frame, borderwidth=myBorderWidth,relief="groove")
	video_control_frame.grid(row=3, column=0, sticky="w", padx=myPadding, pady=myPadding)
	video_control_frame.grid_columnconfigure(5, weight=1) # to expand video_frame_slider
	
	video_fr_button = ttk.Button(video_control_frame, width=1, text="<<")
	video_fr_button.grid(row=0, column=0)

	video_r_button = ttk.Button(video_control_frame, width=1, text="<")
	video_r_button.grid(row=0, column=1)

	video_play_button = ttk.Button(video_control_frame, width=3, text="Play")
	video_play_button.grid(row=0, column=2)
	
	video_f_button = ttk.Button(video_control_frame, width=1, text=">")
	video_f_button.grid(row=0, column=3)
	
	video_ff_button = ttk.Button(video_control_frame, width=1, text=">>")
	video_ff_button.grid(row=0, column=4)
	
	numFrames = 4500
	video_frame_slider = ttk.Scale(video_control_frame, from_=0, to=numFrames, orient="horizontal")
	video_frame_slider.grid(row=0, column=5, sticky="ew")

	#
	# set aspect of video frame
	set_aspect(content_frame, pad_frame, video_control_frame, aspect_ratio=myApectRatio) 
			
	#
	# configure panel
	vPane.add(upper_frame)
	vPane.add(lower_frame)

	hPane.add(lower_left_frame)
	hPane.add(lower_right_frame)

root.geometry("1285x815")

root.update()
vPane.sashpos(0, 100)
hPane.sashpos(0, 400)

root.mainloop()

