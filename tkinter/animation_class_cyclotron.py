import numpy as np
import tkinter as tk
from random import randint # da rimuovere
from scipy.integrate import odeint
from scipy import signal
import time

# global variables
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 800

run = False
# default_data = (10, 30, 60, 80)
# input_data = np.array(default_data)
# labels = ("x 1", "y 1", "x 2", "y 2")
# units = ("unit 1", "unit 2", "unit 3", "unit 4")
# entries = []
default_data = (0, 0, 0, 0, 1, 1, 1, 100, 20, 250)
input_data = np.array(default_data)
labels = ("x0", "y0", "vx0", "vy0", "q", "m", "B", "E", "gap", "D radius")
units = ("unit",)*10
entries = []


class Cyclotron:
    def __init__(self, canvas, z, params):
        self.canvas = canvas
        self.x, self.y, self.vx, self.vy = z
        self.q, self.m, self.B, self.E, self.gap, self.d_r = params

        self.omega = self.q*self.B / self.m # cyclotron frequency
        
        # center features
        self.c_x = CANVAS_WIDTH/2
        self.c_y = CANVAS_HEIGHT/2
        # # animation features
        self.fps = 50
        self.dt = 1/self.fps # time step (s)
        self.t = np.array([0, self.dt])
        # running_time = 600 # s
        # # n_frames=1000
        # n_frames = running_time*fps


    def draw_first_frame(self):
        c_x = self.c_x
        c_y = self.c_y

        # dees features
        d_r = self.d_r
        d_gap = self.gap
        d1_coord = (c_x - (d_r + d_gap/2),
                    c_y - d_r,
                    c_x + (d_r - d_gap/2),
                    c_y + d_r)
        d2_coord = (c_x - (d_r - d_gap/2),
                    c_y - d_r,
                    c_x + (d_r + d_gap/2),
                    c_y + d_r)
        self.d1 = self.canvas.create_arc(d1_coord,
                                         start=90, extent=180,
                                         outline="blue", style=tk.PIESLICE)
        self.d2 = self.canvas.create_arc(d2_coord,
                                         start=270, extent=180,
                                         outline="red", style=tk.PIESLICE)

        # particle features
        self.p_r = 3 # particle radius (pixel)
        p_r = self.p_r
        x = self.x
        y = self.y
        coord = (c_x - (x - p_r),
                 c_y - (y - p_r),
                 c_x - (x + p_r),
                 c_y - (y + p_r))
        if self.q > 0:
            p_color = "red"
        elif self.q < 0:
            p_color = "blue"
        else:
            p_color = "black"
        self.particle = self.canvas.create_oval(coord, fill=p_color, outline=p_color)
        # self.particle = self.canvas.create_oval(coord, outline="red", fill="red")

    def derive(self, t, z, params):
        """Compute the derivative of input z (tuple containing x, y, vx, vy)
        at time t.
        params contains: charge, mass, B field, E field, gap size, dee radius.
        """
        x, y, vx, vy = z
        q, m, B, E, gap, d_r = params
        omega = q*B/m # cyclotron frequency
        if ( # inside one of the dees, E_field = 0
            ((x <= - gap/2) and ((x + gap/2)**2 + (y)**2 <= d_r**2))
            or
            ((x >= + gap/2) and ((x - gap/2)**2 + (y)**2 <= d_r**2))
            ):
            ax = (q/m * B * (vy))
            ay = - q/m * B * (vx)
        elif ( # inside the gap, E_field != 0
            (x > - gap/2) and (x < gap/2) and (y > - d_r) and (y < d_r)
            ):
            # ax = (q/m * B * (vy)) + (q/m * E*np.cos(omega*t))
            ax = (q/m * B * (vy)) + (q/m * E*signal.square(omega*t + np.pi/2))
            ay = - q/m * B * (vx)
        else: # outer region, E_field = 0, B_field = 0
            ax = 0
            ay = 0

        derivs = [vx, vy, ax, ay]
        return derivs

    def compute_coord(self, z0, t, params):
        # solve the differential equations using odeint
        sol = odeint(self.derive, z0, t, args=(params,), tfirst=True)
        self.x = sol[:, 0][-1]
        self.y = sol[:, 1][-1]
        self.vx = sol[:, 2][-1]
        self.vy = sol[:, 3][-1]
        pass

    def move_particle(self):
        if run:
            z0 = self.x, self.y, self.vx, self.vy
            params = self.q, self.m, self.B, self.E, self.gap, self.d_r
            old_x = self.x
            old_y = self.y
            self.compute_coord(z0, self.t, params)
            c_x = self.c_x
            c_y = self.c_y
            p_r = self.p_r
            x = self.x
            y = self.y
            if c_x - x < 0 or c_x - x > CANVAS_WIDTH or c_y - y < 0 or c_y - y > CANVAS_HEIGHT:
                PlayPause()
                return
            else:
                coord = (c_x + (x - p_r),
                         CANVAS_HEIGHT - (c_y + (y - p_r)),
                         c_x + (x + p_r),
                         CANVAS_HEIGHT - (c_y + (y + p_r)))
                self.canvas.coords(self.particle, coord)
                x1 = c_x + old_x
                x2 = c_x + self.x
                y1 = CANVAS_HEIGHT - (c_y + old_y)
                y2 = CANVAS_HEIGHT - (c_y + self.y)

                self.canvas.create_line(x1, y1, x2, y2, fill="red")
                self.t += self.dt
                self.canvas.after(int(self.dt*1000), self.move_particle)

            pass
        else:
            pass

def FirstFrame():
    global cycl, canvas
    canvas.delete(tk.ALL)
    z = input_data[:4]
    params = input_data[4:]
    cycl = Cyclotron(canvas, z, params)
    cycl.draw_first_frame()

def Animate():
    cycl.move_particle()
    pass

def UpdateParams():
    global cycl
    z = input_data[:4]
    params = input_data[4:]
    cycl.x, cycl.y, cycl.vx, cycl.vy = z
    cycl.q, cycl.m, cycl.B, cycl.E, cycl.gap, cycl.d_r = params


def SetEntries():
    global entries
    for i, p in enumerate(input_data):
        entries[i].delete(0, tk.END)
        entries[i].insert(0, f"{p:.2f}")

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
    global input_data, entries
    for i, entry in enumerate(entries):
        try:
            input_data[i] = float(entry.get())
        except ValueError:
            input_data[i] = default_data[i]
            entries[i].delete(0, tk.END)
            entries[i].insert(0, f"{input_data[i]:.2f}")
    
    if run:    
        UpdateParams()
    else:
        Stop()
    
def Reset():
    global input_data
    input_data = np.array(default_data)
    SetEntries()
    Read()
    
def SetWindow():
    global canvas, btn_play, btn_stop, btn_read, entries
    # initialize root Window
    root = tk.Tk()
    root.title("Class animation")
    root.resizable(False,False)

    frm_canvas = tk.Frame(master=root, relief=tk.RIDGE, borderwidth=2)
    frm_side = tk.Frame(master=root, relief=tk.RIDGE, borderwidth=0)

    canvas = tk.Canvas(frm_canvas, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white")
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
        
        lbl_par.grid(row=i, column=0, sticky="SE", pady=3)
        entries[i].grid(row=i, column=1, sticky="S", pady=3)
        lbl_unit.grid(row=i, column=2, sticky="SW", pady=3)

    frm_data.pack(pady=25)

    frm_side.grid(row=0, column=1, sticky="NW")

    Reset()

    root.mainloop()

if __name__ == '__main__':
   SetWindow()
