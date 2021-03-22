import tkinter as tk

window = tk.Tk()

entry = tk.Entry(width=40, bg="white", fg="black")
entry.pack()

entry.insert(0, "What is your name?")

window.mainloop()