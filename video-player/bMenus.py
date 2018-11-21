# Author: Robert Cudmore
# Date: 20181118

import json

import tkinter
from tkinter import ttk
from tkinter import filedialog

from pprint import pprint

#from bRandomChunks import bRandomChunks

#
# menus
class bMenus:

	def __init__(self, app):

		self.app = app
		self.root  = app.root
		
		menubar = tkinter.Menu(self.root)
		appmenu = tkinter.Menu(menubar, name='apple')
		menubar.add_cascade(menu=appmenu)

		filemenu = tkinter.Menu(menubar, tearoff=0)
		filemenu.add_command(label="Open Folder ...", command=self.open_folder)
		filemenu.add_separator()
		filemenu.add_command(label="Open Random Chunks ...", command=self.open_random)
		filemenu.add_separator()
		#filemenu.add_command(label="Quit", command=self.root.quit)
		filemenu.add_command(label="Quit", command=self.app.onClose)

		windowmenu = tkinter.Menu(menubar, tearoff=0)
		windowmenu.add_command(label="Toggle Video Files", command=self.togglevideofiles)
		windowmenu.add_command(label="Toggle Events", command=self.toggleevents)
		windowmenu.add_separator()
		windowmenu.add_command(label="Toggle Random Chunks", command=self.togglerandomchunks)
		windowmenu.add_command(label="Toggle Video Feedback", command=self.togglevideofeedback)
		
		menubar.add_cascade(menu=filemenu, label='File')
		menubar.add_cascade(menu=windowmenu, label='Window')

		# display the menu
		self.root['menu'] = [menubar]
	
	def open_folder(self):
		print("open a folder with video files")
		path = ''
		#path =  filedialog.askdirectory()
		#print('path:', path)
		self.app.loadFolder(path)
		
	def open_random(self):
		print("open a random chunks file")
		self.app.chunkView.chunkInterface_populate(askForFile=True)
				
	def togglevideofiles(self):
		print('bMenus.togglevideofiles()')
		#self.app.toggleVideoFiles()
		self.app.toggleInterface('videofiles')
		
	def toggleevents(self):
		print('bMenus.toggleevents()')
		#self.app.toggleEvents()
		self.app.toggleInterface('events')
		
	def togglerandomchunks(self):
		print('bMenus.togglerandomchunks()')
		#self.app.toggleRandomChunks()
		self.app.toggleInterface('randomchunks')

	def togglevideofeedback(self):
		print('bMenus.togglevideofeedback()')
		#self.app.toggleRandomChunks()
		self.app.toggleInterface('videofeedback')
