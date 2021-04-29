import tkinter as tk
from random import randint
import time
import numpy as np

# global variables
CANVAS_WIDTH = 500
CANVAS_HEIGTH = 500

run = False
default_params = (10, 30, 60, 80)
input_params = np.array(default_params)
labels = ("x 1", "y 1", "x 2", "y 2")
units = ("unit 1", "unit 2", "unit 3", "unit 4")
entries = []

class Ball:
    def __init__(self, canvas, params):
        self.x1 = params[0]
        self.y1 = params[1]
        self.x2 = params[2]
        self.y2 = params[3]
        self.canvas = canvas
        self.ball = canvas.create_oval(self.x1, self.y1, self.x2, self.y2, fill="red")

    def move_ball(self):
        if run:
            dx = randint(0,5)
            dy = randint(0,5)
            # self.canvas.move(self.ball, dx, dy)
            coords = (self.x1 + dx, self.y1 + dy, self.x2 + dx, self.y2 + dy)
            self.canvas.coords(self.ball, coords)
            self.x1 += dx
            self.y1 += dy
            self.x2 += dx
            self.y2 += dy
            self.canvas.after(50, self.move_ball)
        else:
            pass

def FirstFrame():
    global ball1, ball2, canvas
    canvas.delete(tk.ALL)
    p1, p2, p3, p4 = input_params
    ball1 = Ball(canvas, (p1, p1, p2, p2))
    ball2 = Ball(canvas, (p3, p3, p4, p4))

def UpdateParams():
    global ball1, ball2, canvas
    p1, p2, p3, p4 = input_params

    ball1.x1 = p1
    ball1.y1 = p1
    ball1.x2 = p2
    ball1.y2 = p2

    ball2.x1 = p3
    ball2.y1 = p3
    ball2.x2 = p4
    ball2.y2 = p4

def Animate():
    ball1.move_ball()
    ball2.move_ball()

def PlayPause():
    global run, btn_play
    run = not run
    if run:
        Animate()
        btn_play.configure(text="\u23F8")
    else:
        btn_play.configure(text="\u25B6")

def Stop():
    FirstFrame()
    if run:
        PlayPause()

def Read():
    global input_params, entries
    for i, entry in enumerate(entries):
        try:
            input_params[i] = float(entry.get())
        except ValueError:
            input_params[i] = default_params[i]
            entries[i].delete(0, tk.END)
            entries[i].insert(0, f"{input_params[i]:.2f}")
    
    if run:    
        UpdateParams()
    else:
        Stop()
    
def Reset():
    global input_params
    input_params = np.array(default_params)
    SetEntries()
    Read()

def SetEntries():
    global entries
    for i, p in enumerate(input_params):
        entries[i].delete(0, tk.END)
        entries[i].insert(0, f"{p:.2f}")
    
def SetWindow():
    global canvas, btn_play, btn_stop, btn_read, entries
    # initialize root Window
    root = tk.Tk()
    root.title("Class animation")
    root.resizable(False,False)

    frm_canvas = tk.Frame(master=root, relief=tk.RIDGE, borderwidth=2)
    frm_side = tk.Frame(master=root, relief=tk.RIDGE, borderwidth=0)

    canvas = tk.Canvas(frm_canvas, width=CANVAS_WIDTH, height=CANVAS_HEIGTH, bg="white")
    canvas.pack()
    frm_canvas.grid(row=0, column=0)

    frm_buttons = tk.Frame(master=frm_side, relief=tk.RIDGE, borderwidth=0)
    frm_data = tk.Frame(master=frm_side, relief=tk.RIDGE, borderwidth=1)

    btn_exit = tk.Button(master=frm_buttons, text="Exit", command=root.destroy)
    btn_exit.grid(row=0, column=3, sticky="NE", pady=5)

    btn_play = tk.Button(master=frm_buttons, text="\u25B6", command=PlayPause, width=5)
    btn_stop = tk.Button(master=frm_buttons, text="\u23F9", command=Stop, width=5)
    btn_read = tk.Button(master=frm_buttons, text="Read data", command=Read)
    btn_reset = tk.Button(master=frm_buttons, text="Reset data", command=Reset)

    btn_play.grid(row=1, column=0, sticky="W", pady=10, padx=3)
    btn_stop.grid(row=1, column=1, sticky="W", pady=10, padx=3)
    btn_read.grid(row=1, column=2, sticky="N", pady=10)
    btn_reset.grid(row=1, column=3, sticky="N", pady=10)

    frm_buttons.pack()

    entries = []

    for i, label in enumerate(labels):
        lbl_par = tk.Label(master=frm_data, text=f"{label} =")
        entries.append(tk.Entry(master=frm_data))
        lbl_unit = tk.Label(master=frm_data, text=units[i])
        
        lbl_par.grid(row=i, column=0, sticky="s", pady=3)
        entries[i].grid(row=i, column=1, sticky="s", pady=3)
        lbl_unit.grid(row=i, column=2, sticky="s", pady=3)

    frm_data.pack(pady=25)

    frm_side.grid(row=0, column=1, sticky="NW")

    Reset()

    root.mainloop()

if __name__ == '__main__':
   SetWindow()
