from tkinter import *

root = Tk()

scrollbar = Scrollbar(root)
scrollbar.pack(side=RIGHT, fill=Y)

listbox = Listbox(root)


# attach listbox to scrollbar
listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=listbox.yview)

for i in range(100):
    listbox.insert(END, i)
listbox.pack()

# 2
scrollbar2 = Scrollbar(root)
scrollbar2.pack(side=RIGHT, fill=Y)

listbox2 = Listbox(root)
listbox2.pack()

for i in range(100):
    listbox2.insert(END, i)

# attach listbox to scrollbar
listbox2.config(yscrollcommand=scrollbar2.set)
scrollbar2.config(command=listbox2.yview)

mainloop()