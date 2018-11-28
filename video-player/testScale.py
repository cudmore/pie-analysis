import tkinter
from tkinter import ttk

def scale_callback(val):
	print('scale_callback() val:', val)

def button_callback():
	print('button_callback()')
	from_ = 500
	to = 600
	"""
	myScale['value'] = from_
	myScale['from'] = from_
	myScale['to'] = to
	"""
	myScale.set(from_)
	myScale.configure(from_=from_)
	myScale.configure(to=to)
	
root = tkinter.Tk()

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

myFrame = ttk.Frame(root)
myFrame.grid(row=0, column=0)

from_ = 100
to = 1000

myScale = tkinter.Scale(myFrame, from_=from_, to=to, orient="horizontal", command=scale_callback)
myScale.grid(row=0, column=0)

myButton = ttk.Button(root, text='click me', command=button_callback)
myButton.grid(row=1, column=0)

#button_callback()

root.geometry('640x480')

root.mainloop()
