import tkinter 
 
root = tkinter.Tk() 
 
root.title("Hello!") 
 
root.resizable(width="false", height="false") 
 
root.minsize(width=300, height=50)   
root.maxsize(width=300, height=50) 
 
simple_label = tkinter.Label(root, text="Easy, right?")   
closing_button = tkinter.Button(root, text="Close window", command=root.destroy) 
 
simple_label.pack()   
closing_button.pack() 
 
root.mainloop()   