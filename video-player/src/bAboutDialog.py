# Author: Robert Cudmore
# Date: 20181202

import sys

import cv2

import tkinter
from tkinter import ttk

import VideoApp

##################################################################################
class bAboutDialog:
	"""
	Opens a modal dialog to set the note of an event
	"""
	def __init__(self, parentApp):

		# to make modal
		#self.grab_set()
		# see: http://effbot.org/tkinterbook/tkinter-dialog-windows.htm
		
		self.top = tkinter.Toplevel(parentApp)
		self.top.geometry('400x400')
		
		
		myFrame = tkinter.Frame(self.top, padx=20, pady=20)
		myFrame.pack(side="left", fill="both")
		
		platformStr = 'Platform: ' + sys.platform
		tkinter.Label(myFrame, text=platformStr, anchor="nw").pack(side="top")

		videoAppVersionStr = 'Video App: ' + VideoApp.__version__
		tkinter.Label(myFrame, text=videoAppVersionStr, anchor="nw").pack(side="top")

		pythonVersionStr = 'Python: ' + str(sys.version_info[0]) + '.' + str(sys.version_info[1]) + '.' + str(sys.version_info[2])
		tkinter.Label(myFrame, text=pythonVersionStr, anchor="nw").pack(side="top")
		
		opencvVersionStr = 'opencv: ' + str(cv2.__version__)
		tkinter.Label(myFrame, text=opencvVersionStr, anchor="nw").pack(side="top")
		
		tkinterVersionStr = 'tkinter: ' + str(tkinter.TkVersion)
		tkinter.Label(myFrame, text=tkinterVersionStr, anchor="nw").pack(side="top")

		okButton = tkinter.Button(myFrame, text="OK", command=self.okButton_Callback)
		okButton.pack(side="top", pady=5)

		#self.top.focus_force() # added
		
		self.top.grab_set()
		
		#self.top.grab_set_global()

	def okButton_Callback(self):
		self.top.destroy() # destroy *this, the modal

