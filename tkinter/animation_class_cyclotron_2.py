"""Project for the "Algoritmi di spettroscopia" course by Prof. Moruzzi.
Author: Marco Nastasi

Cyclotron animation script.
Use a class to manage the physical simulation and the animation.
The window layout is managed outside the class.
The GUI is implemented in tkinter, the differential equations are solved
with odeint package.
"""

import numpy as np
import tkinter as tk
from scipy.integrate import odeint
from scipy import signal
import time

# global variables
CANVAS_W = 1000 # px
CANVAS_H = CANVAS_W
run = False
stopped = True

class Cyclotron:
    def __init__(self):
        """Cyclotron constructor. Set the default data, the timescale, 
        the length scale, the variables to monitor, the animation features.
        """
        # default data
        self.scale = 1e3 # length scale (pixel/m)
        self.default_timescale = 6.7e-5
        self.fps = 100 # framerate (frame/s)
        self.delayed = 0
        x0 = 0 # m
        y0 = 0 # m
        vx0 = 0 # m/s
        vy0 = 0 # m/s
        qp = 1.602176e-19 # elementary charge (Coulomb)
        mp = 1.67262e-27 # proton mass (Kg)
        me = 9.10938e-31 # electron mass (Kg)
        B0 = 1e-3 # T
        E0 = 1e1 # V/m
        gap0 = 0.02 # m
        dr0 = 0.45 # m
        self.default_data = (x0, y0, vx0, vy0, qp, mp, B0, E0, gap0, dr0)
        self.labels = ("x\u2080", "y\u2080", "vx\u2080", "vy\u2080",
                       "q", "m", "B", "E", "gap", "D radius")
        self.units = ("m", "m", "m/s", "m/s", "C", "Kg", "T", "V/m", "m", "m")

        # indices of parameters that cannot be changed while playing animation
        self.static_params = (0, 1, 2, 3, -2, -1)
        
        # prepare the texts for the variables to monitor
        self.monitors_texts = (
                               "T = ... s",
                               "v = ... m/s",
                               "p = ... eV/c",
                               "\u03B3 = ...",
                              )

        # set initial values for input_data and timescale
        self.input_data = np.array(self.default_data, dtype=float)
        self.timescale = self.default_timescale
        
        # animation features
        self.ms = 1000/self.fps # time interval between frames (ms)
        self.dt = 1e-3 * self.ms * self.timescale # time step (s)
        # time array to solve differential equations
        self.t = np.array([0, self.dt])

    def restore_default(self):
        """Restore to default self.input_data and self.timescale"""
        self.input_data = np.array(self.default_data, dtype=float)
        self.timescale = self.default_timescale
    
    def set_data(self, static_flag):
        """Set data reading input. If static_flag=False set only non
        static paramters. If static_flag=True set all data and reset time.
        """
        if static_flag:
            z = self.input_data[:4]
            params = self.input_data[4:]
            self.x, self.y, self.vx, self.vy = z
            self.q, self.m, self.B, self.E, self.gap, self.d_r = params
            self.t = np.array([0, self.dt])
        else:
            self.q, self.m, self.B, self.E = self.input_data[4:-2]

    def set_colors(self):
        """Set the particle color checking the charge and the dees colors
        checking the sign of the electric field.
        """
        # particle and track color
        if self.q > 0:
            self.p_color = "red"
        elif self.q < 0:
            self.p_color = "blue"
        else:
            self.p_color = "black"
        
        # dees colors
        omega = self.q*self.B / self.m # cyclotron frequency
        if (self.E*signal.square(omega*self.t[0] + np.pi/2)) > 0:
            self.d1_color = "red"
            self.d2_color = "blue"
        elif (self.E*signal.square(omega*self.t[0] + np.pi/2)) < 0:
            self.d1_color = "blue"
            self.d2_color = "red"
        else:
            self.d1_color = "black"
            self.d2_color = "black"

    def monitors_update(self, monitors):
        """Update the monitors with the current variables."""
        c = 2.99792458e8 # m/s
        qp = 1.602176e-19 # elementary charge (Coulomb)
        self.v = np.sqrt(self.vx**2 + self.vy**2)
        # p_eV = (self.v * self.m) / 5.344286e-28
        p_eV = (self.v * self.m * c) / qp # impulse of particle (eV/c)
        omega = self.q*self.B/self.m # cyclotron frequency
        gamma = 1 / (np.sqrt(1 - (self.v/c)**2))
        monitors[0]["text"] = f"T = {np.abs((2*np.pi)/omega):.3e} s"
        monitors[1]["text"] = f"v = {self.v:.3e} m/s"
        monitors[2]["text"] = f"p = {p_eV/1e3:.3e} KeV/c"
        monitors[3]["text"] = f"\u03B3 = {gamma:.3e}"

    def draw_first_frame(self, canvas):
        """Draw the first frame of the animation on the given canvas."""
        self.canvas = canvas

        self.set_colors()

        # center features
        self.cx = int(self.canvas["width"]) / 2
        self.cy = int(self.canvas["height"]) / 2
        
        cx = self.cx
        cy = self.cy
        scale = self.scale

        # dees features
        # canvas coordinates of dees
        d_r = self.d_r * scale
        d_gap = self.gap * scale
        d1_coord = (cx - (d_r + d_gap/2),
                    cy - d_r,
                    cx + (d_r - d_gap/2),
                    cy + d_r)
        d2_coord = (cx - (d_r - d_gap/2),
                    cy - d_r,
                    cx + (d_r + d_gap/2),
                    cy + d_r)
        self.d1 = self.canvas.create_arc(d1_coord,
                                         start=90, extent=180,
                                         outline=self.d1_color,
                                         style=tk.PIESLICE)
        self.d2 = self.canvas.create_arc(d2_coord,
                                         start=270, extent=180,
                                         outline=self.d2_color,
                                         style=tk.PIESLICE)

        # particle features
        self.p_r = 3 # particle radius (pixel)
        p_r = self.p_r
        # canvas coordinates of particle
        x = self.x * scale
        y = self.y * scale
        coord = (cx + (x - p_r),
                 CANVAS_H - (cy + (y - p_r)),
                 cx + (x + p_r),
                 CANVAS_H - (cy + (y + p_r)))
        self.particle = self.canvas.create_oval(coord,
                                                fill=self.p_color,
                                                outline=self.p_color)

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
            ay = - (q/m * B * (vx))
        elif ( # inside the gap, E_field != 0
            (x > - gap/2) and (x < gap/2) and (y > - d_r) and (y < d_r)
            ):
            # ax = (q/m * B * (vy)) + (q/m * E*np.cos(omega*t))
            ax = (q/m * B * (vy)) + (q/m * E*signal.square(omega*t + np.pi/2))
            ay = - (q/m * B * (vx))
        else: # outer region, E_field = 0, B_field = 0
            ax = 0
            ay = 0

        derivs = [vx, vy, ax, ay]
        return derivs

    def compute_coord(self, z0, t, params):
        """Solve the differential equations using odeint at times in t array.
        z0 is a tuple containing x0, y0, vx0, vy0.
        params contains: charge, mass, B field, E field, gap size, dee radius.
        Then updates self.x, self.y, self.vx, self.vy.
        """
        sol = odeint(self.derive, z0, t, args=(params,), tfirst=True)
        self.x = sol[:, 0][-1]
        self.y = sol[:, 1][-1]
        self.vx = sol[:, 2][-1]
        self.vy = sol[:, 3][-1]

    def move_particle(self, PlayPause_func, btn_play, status_bar, monitors):
        # TODO: lascio la variabile "run" globale?
        """Perform the animation. Use PlayPause_func to pause the 
        animation in the case the particle would go out of canvas, 
        disable the play button (btn_play) and update the status_bar and
        the monitors.
        Compute the time taken to produce a frame attempting to keep
        the animation fps constant, limitations depends on hardware.
        """
        t1 = time.time()
        move_params = (PlayPause_func, btn_play, status_bar, monitors)
        self.set_colors()
        self.monitors_update(monitors)
        if run:
            z0 = self.x, self.y, self.vx, self.vy
            params = self.q, self.m, self.B, self.E, self.gap, self.d_r
            scale = self.scale
            cx = self.cx
            cy = self.cy
            p_r = self.p_r

            # canvas old coordinates of particle
            old_x = self.x * scale
            old_y = self.y * scale

            # update the dt and check t array
            self.dt = 1e-3 * self.ms * self.timescale # time step (s)
            if (self.t[1] - self.t[0]) == self.dt:
                pass
            else:
                self.t[1] = self.t[0] + self.dt

            self.compute_coord(z0, self.t, params)
            
            # canvas coordinates of particle
            x = self.x * scale
            y = self.y * scale
            if ( # particle would go out of canvas
                 (cx + x < 0)
                 or
                 (cx + x > CANVAS_W)
                 or
                 (cy + y < 0)
                 or
                 (cy + y > CANVAS_H)
                ):
                PlayPause_func
                btn_play["state"] = "disabled"
                msg = "Animation ended, next position would be out of canvas."
                status_bar["text"] = msg
                # print("Delayed frames:", self.delayed)
            else:
                coord = (cx + (x - p_r),
                         CANVAS_H - (cy + (y - p_r)),
                         cx + (x + p_r),
                         CANVAS_H - (cy + (y + p_r)))
                self.canvas.coords(self.particle, coord)
                self.canvas.itemconfigure(self.particle,
                                          fill=self.p_color,
                                          outline=self.p_color)
                self.canvas.itemconfigure(self.d1, outline=self.d1_color)
                self.canvas.itemconfigure(self.d2, outline=self.d2_color)
                # canvas coordinates of track segment
                x1 = cx + old_x
                x2 = cx + x
                y1 = CANVAS_H - (cy + old_y)
                y2 = CANVAS_H - (cy + y)
                self.canvas.create_line(x1, y1, x2, y2, fill=self.p_color)

                # update the dt, check and increment t array
                self.dt = 1e-3 * self.ms * self.timescale # time step (s)
                if (self.t[1] - self.t[0]) == self.dt:
                    self.t += self.dt
                else:
                    self.t[0] = self.t[1]
                    self.t[1] = self.t[0] + self.dt

                t2 = time.time()
                delay = (t2 - t1)*1000
                if self.ms >= delay:
                    d_ms = int(self.ms - delay)
                    self.canvas.after(d_ms, self.move_particle, *move_params)
                else: # delayed frame
                    self.delayed += 1
                    self.canvas.after(0, self.move_particle, *move_params)
                # self.canvas.after(int(self.ms - delay), self.move_particle)
        else:
            # print("Delayed frames:", self.delayed)
            pass

def TscaleDown():
    global Cycl, lbl_tscale
    Cycl.timescale = Cycl.timescale / 10**(1/5)
    lbl_tscale["text"] = f"Time scale = {Cycl.timescale:.3e}"

def TscaleUp():
    global Cycl, lbl_tscale
    Cycl.timescale = Cycl.timescale * 10**(1/5)
    lbl_tscale["text"] = f"Time scale = {Cycl.timescale:.3e}"

def Animate():
    global Cycl
    move_params = (PlayPause, btn_play, status_bar, monitors)
    Cycl.move_particle(*move_params)

def UpdateParams():
    global Cycl
    Cycl.set_data(static_flag=False)
    Cycl.monitors_update(monitors)

def FirstFrame():
    global Cycl, canvas
    canvas.delete(tk.ALL)
    Cycl.draw_first_frame(canvas)

def PlayPause():
    global run, btn_play, stopped, status_bar, entries, Cycl
    run = not run
    stopped = False
    if run:
        status_bar["text"] = "Playing..."
        Animate()
        btn_play.configure(text="\u23F8")
        for i in Cycl.static_params:
            entries[i]["state"] = "disabled"
    else:
        status_bar["text"] = "Paused"
        btn_play.configure(text="\u25B6")

def Stop():
    global stopped, btn_play, entries, Cycl
    stopped = True
    if (btn_play["state"] == "disabled"):
        btn_play["state"] = "normal"
    else:
        pass

    if run:
        PlayPause()
        Stop()
    else:
        for i in Cycl.static_params:
            entries[i]["state"] = "normal"
        Cycl.set_data(static_flag=True)
        Cycl.monitors_update(monitors)
        FirstFrame()
        status_bar["text"] = "Ready"

def Read():
    global entries
    for i, entry in enumerate(entries):
        try:
            Cycl.input_data[i] = float(entry.get())
        except ValueError:
            Cycl.input_data[i] = Cycl.default_data[i]
        entries[i].delete(0, tk.END)
        entries[i].insert(0, f"{Cycl.input_data[i]:.3e}")
    
    if (not stopped):    
        UpdateParams()
    else:
        Stop()

def SetEntries():
    global entries
    for i, p in enumerate(Cycl.input_data):
        entries[i].delete(0, tk.END)
        entries[i].insert(0, f"{p:.3e}")
    
def Reset():
    global lbl_tscale, Cycl
    Cycl.restore_default()
    lbl_tscale["text"] = f"Time scale = {Cycl.timescale:.3e}"
    SetEntries()
    Read()
    
def SetWindow(labels, units, monitors_texts):
    global canvas
    global btn_play
    global entries, lbl_tscale, monitors, status_bar
    # initialize root Window
    root = tk.Tk()
    root.title("Interactive Cyclotron animation")
    root.resizable(False,False)
    
    # Two principal frames, for canvas and sidebar
    frm_canvas = tk.Frame(master=root, relief=tk.RIDGE, borderwidth=1)
    frm_side = tk.Frame(master=root, relief=tk.RIDGE, borderwidth=0)
    
    # Canvas inside his frame
    canvas = tk.Canvas(frm_canvas, width=CANVAS_W, height=CANVAS_H, bg="white")
    canvas.pack()
    frm_canvas.grid(row=0, column=0)
    
    # Buttons inside their frame (inside side frame)
    frm_btns = tk.Frame(master=frm_side, relief=tk.RIDGE, borderwidth=0)
    btn_exit = tk.Button(master=frm_btns, text="Exit", command=root.destroy)
    btn_exit.grid(row=0, column=3, sticky="NE", pady=5)
    btn_play = tk.Button(master=frm_btns, text="\u25B6", command=PlayPause, width=5)
    btn_stop = tk.Button(master=frm_btns, text="\u23F9", command=Stop, width=5)
    btn_read = tk.Button(master=frm_btns, text="Read data", command=Read)
    btn_reset = tk.Button(master=frm_btns, text="Reset data", command=Reset)
    btn_play.grid(row=1, column=0, sticky="W", pady=10, padx=3)
    btn_stop.grid(row=1, column=1, sticky="W", pady=10, padx=3)
    btn_read.grid(row=1, column=2, sticky="N", pady=10)
    btn_reset.grid(row=1, column=3, sticky="N", pady=10)
    frm_btns.pack(padx=10, pady=10)
    
    # Labels and entries inside data frame (inside side frame)
    frm_data = tk.Frame(master=frm_side, relief=tk.RIDGE, borderwidth=0)
    entries = []
    for i, label in enumerate(labels):
        lbl_par = tk.Label(master=frm_data, text=f"{label} =")
        entries.append(tk.Entry(master=frm_data, width=10))
        lbl_unit = tk.Label(master=frm_data, text=units[i])
        lbl_par.grid(row=i, column=0, sticky="SE", pady=3)
        entries[i].grid(row=i, column=1, sticky="S", pady=3, padx=5)
        lbl_unit.grid(row=i, column=2, sticky="SW", pady=3)
    frm_data.pack(pady=25)

    # Timescale buttons and label inside their frame (inside side frame)
    frm_tscale = tk.Frame(master=frm_side, relief=tk.RIDGE, borderwidth=0)
    btn_tscale_down = tk.Button(master=frm_tscale, text=" - ", command=TscaleDown)
    lbl_tscale = tk.Label(master=frm_tscale)
    btn_tscale_up = tk.Button(master=frm_tscale, text=" + ", command=TscaleUp)
    lbl_tscale.grid(row=0, column=1, padx=4)
    btn_tscale_down.grid(row=0, column=0, sticky="nsew")
    btn_tscale_up.grid(row=0, column=2, sticky="nsew")
    frm_tscale.pack()
    
    # Monitor labels inside their frame (inside side frame)
    monitors = []
    frm_monitors = tk.Frame(master=frm_side, relief=tk.SUNKEN, borderwidth=1)
    for i, _ in enumerate(monitors_texts):
        monitors.append(tk.Label(master=frm_monitors))
        monitors[i].grid(row=i, column=0, sticky="W", padx=10, pady=3)
    frm_monitors.pack(pady=40)

    # Status bar inside his frame (inside side frame)
    frm_satus = tk.Frame(master=frm_side, relief=tk.SUNKEN, borderwidth=1)
    status_text = "Ready"
    status_bar = tk.Label(master=frm_satus, text=status_text)
    status_bar.grid(row=0, column=0, sticky="E", pady=3)
    frm_satus.pack(side="bottom", fill="both")

    frm_side.grid(row=0, column=1, sticky="NSW")

    Reset()

    root.mainloop()

if __name__ == '__main__':
   Cycl = Cyclotron()
   SetWindow(Cycl.labels, Cycl.units, Cycl.monitors_texts)
