# Author: Robert Cudmore
# Date: 20181118

import json

import tkinter
from tkinter import ttk
from tkinter import filedialog

from pprint import pprint

#from bRandomChunks import bRandomChunks
import bDialog

#
# menus
class bMenus:

	def __init__(self, app):

		self.app = app
		self.root  = app.root
		
		self.showVideoFilesBool = tkinter.BooleanVar()
		self.showVideoFilesBool.set(self.app.configDict['showVideoFiles'])
		
		self.showEventsBool = tkinter.BooleanVar()
		self.showEventsBool.set(self.app.configDict['showEvents'])
		
		self.blindInterfaceBool = tkinter.BooleanVar()
		self.blindInterfaceBool.set(self.app.configDict['blindInterface'])
		
		"""
		self.showRandomChunksBool = tkinter.BooleanVar()
		self.showRandomChunksBool.set(self.app.configDict['showRandomChunks'])
		"""
		
		# main menu bar
		menubar = tkinter.Menu(self.root)
		
		# app
		appmenu = tkinter.Menu(menubar, name='apple')
		appmenu.add_command(label="About Video Annotate", command=self.about)
		appmenu.add_separator()
		appmenu.add_command(label="Preferences...", command=self.preferences)
		menubar.add_cascade(menu=appmenu)

		# file
		filemenu = tkinter.Menu(menubar, tearoff=0)
		filemenu.add_command(label="Open Folder ...", command=self.open_folder)
		filemenu.add_separator()
		filemenu.add_command(label="Generate Chunks ...", command=self.generateChunks)
		filemenu.add_separator()
		#filemenu.add_command(label="Open Random Chunks ...", command=self.open_random)
		#filemenu.add_separator()
		filemenu.add_command(label="Save Preferences", command=self.app.savePreferences)
		filemenu.add_separator()
		#filemenu.add_command(label="Quit", command=self.root.quit)
		filemenu.add_command(label="Quit", command=self.app.onClose) #, accelerator="Command-P")

		# chunk
		"""
		chunkmenu = tkinter.Menu(menubar, tearoff=0)
		chunkmenu.add_command(label="Limit Video Controls", command=self.limitvideocontrols)
		chunkmenu.add_command(label="Limit Interface", command=self.limitInterface)
		chunkmenu.add_separator()
		chunkmenu.add_command(label="Generate Chunks ...", command=self.generateChunks)
		"""
		
		# window
		self.windowmenu = tkinter.Menu(menubar, tearoff=0)
		self.windowmenu.add_checkbutton(label="Video Files", onvalue=1, offvalue=False, variable=self.showVideoFilesBool, command=self.togglevideofiles)
		self.windowmenu.add_checkbutton(label="Events", onvalue=1, offvalue=False, variable=self.showEventsBool, command=self.toggleevents)
		self.windowmenu.add_separator()
		self.windowmenu.add_checkbutton(label="Blind Interface", onvalue=1, offvalue=False, variable=self.blindInterfaceBool, command=self.blindInterface)
		"""
		self.windowmenu.add_separator()
		self.windowmenu.add_checkbutton(label="Random Chunks", onvalue=1, offvalue=False, variable=self.showRandomChunksBool, command=self.togglerandomchunks)
		"""
		
		# append all menus to main menu bar
		menubar.add_cascade(menu=filemenu, label='File')
		#menubar.add_cascade(menu=chunkmenu, label='Chunks')
		menubar.add_cascade(menu=self.windowmenu, label='Window')

		# display the menu
		self.root['menu'] = [menubar]
	
	def setState(self, menuItem, onoff):
		"""
		Set the state of menu checkboxes from man app.
		Used when turning blinding on/off
		"""
		if menuItem == 'Video Files':
			self.showVideoFilesBool.set(onoff)
		if menuItem == 'Events':
			self.showEventsBool.set(onoff)
			
	def blindMenus(self, onoff):
		if onoff:
			state = "disabled"
		else:
			state = "normal"
		
		self.windowmenu.entryconfig(0,state=state) # Video Files
		self.windowmenu.entryconfig(1,state=state) # Events

		# don't change state of on/off
		self.setState('Video Files', not onoff)
		self.setState('Events', not onoff)
		
	def about(self):
		bDialog.bAboutDialog(self.app.root)
		#self.app.showAboutDialog()
	
	def preferences(self):
		print('not implemented')
		bDialog.bPreferencesDialog(self.app)
		#self.app.showAboutDialog()
	
	def open_folder(self):
		print("open a folder with video files")
		path = ''
		#path =  filedialog.askdirectory()
		#print('path:', path)
		self.app.loadFolder(path)
		
	def generateChunks(self):
		bDialog.bGenerateChunksDialog(self.app)
	
	def togglevideofiles(self):
		print('bMenus.togglevideofiles()', self.showVideoFilesBool.get())
		#self.app.toggleVideoFiles()
		self.app.toggleInterface('videofiles', self.showVideoFilesBool.get())
		
	def toggleevents(self):
		print('bMenus.toggleevents()', self.showEventsBool.get())
		#self.app.toggleEvents()
		self.app.toggleInterface('events', self.showEventsBool.get())
	
	def blindInterface(self):
		print('bMenus.blindInterface()', self.blindInterfaceBool.get())
		self.app.blindInterface(self.blindInterfaceBool.get())