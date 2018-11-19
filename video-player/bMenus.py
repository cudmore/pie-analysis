# Author: Robert Cudmore
# Date: 20181118

import tkinter
from tkinter import ttk
from tkinter import filedialog

#
# menus
class bMenus:

	def __init__(self, app):
		root  = app
		
		menubar = tkinter.Menu(root)
		appmenu = tkinter.Menu(menubar, name='apple')
		menubar.add_cascade(menu=appmenu)

		filemenu = tkinter.Menu(menubar, tearoff=0)
		filemenu.add_command(label="Open Folder ...", command=self.open_folder)
		filemenu.add_separator()
		filemenu.add_command(label="Open Random Chunks ...", command=self.open_random)
		filemenu.add_separator()
		filemenu.add_command(label="Quit", command=root.quit)

		windowmenu = tkinter.Menu(menubar, tearoff=0)
		windowmenu.add_command(label="Toggle Video Files", command=self.togglevideofiles)
		windowmenu.add_command(label="Toggle Events", command=self.toggleevents)
		windowmenu.add_separator()
		windowmenu.add_command(label="Toggle Random Chunks", command=self.togglerandomchunks)
		
		menubar.add_cascade(menu=filemenu, label='File')
		menubar.add_cascade(menu=windowmenu, label='Window')

		# display the menu
		root['menu'] = [menubar]
	
	def open_folder(self):
		print("open a folder with video files")
		path =  filedialog.askdirectory()
		print('path:', path)

	def open_random(self):
		print("open a random chunks file")
		filename =  filedialog.askopenfilename(initialdir = "/",title = "Select a random chunk file",filetypes = (("text files","*.txt"),("all files","*.*")))
		print('filename:', filename)

	def togglevideofiles(self):
		print('bMenus.togglevideofiles()')

	def toggleevents(self):
		print('bMenus.toggleevents()')

	def togglerandomchunks(self):
		print('bMenus.togglerandomchunks()')
