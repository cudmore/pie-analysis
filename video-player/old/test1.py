#from Tkinter import *
#import ttk

# In Python 3.x
import tkinter
from tkinter import *
from tkinter import ttk

root = Tk()

pane = PanedWindow(orient=VERTICAL)
pane.pack( side = tkinter.TOP , fill=tkinter.X, expand=1, anchor=tkinter.N)

upper_container = Frame(pane)
upper_container.pack(side=tkinter.TOP, anchor=tkinter.NE)

left_tree = ttk.Treeview(upper_container, padding=(25,25,25,25))
left_tree.pack(side=LEFT, fill=tkinter.BOTH, expand=1)

right_tree = ttk.Treeview(upper_container, padding=(25,25,25,25))
right_tree.pack(side=LEFT, fill=tkinter.BOTH, expand=1)

lower_tree = ttk.Treeview(pane)
lower_tree.pack(side=tkinter.TOP)

pane.add(upper_container)
pane.add(lower_tree)

root.mainloop()