import numpy as np
import tkinter as tk
from scipy.integrate import odeint
from scipy import signal
import time

# global variables
CANVAS_W = 1000 # px
CANVAS_H = CANVAS_W
scale = 1e3 # px/m
default_timescale = 6.7e-5
timescale = default_timescale

x0 = 0 # m
y0 = 0 # m
vx0 = 0 # m/s
vy0 = 0 # m/s
qp = 1.602176e-19 # elementary charge (Coulomb)
mp = 1.67262e-27 # proton mass (Kg)
B0 = 1e-3 # T
E0 = 1e1 # V/m
gap0 = 0.02 # m
dr0 = 0.45 # m

run = False
stopped = True
default_data = (x0, y0, vx0, vy0, qp, mp, B0, E0, gap0, dr0)
input_data = np.array(default_data, dtype=np.double)
labels = ("x0", "y0", "vx0", "vy0", "q", "m", "B", "E", "gap", "D radius")
units = ("m", "m", "m/s", "m/s", "C", "Kg", "T", "V/m", "m", "m")
# units = ("unit",)*10
static_params = [0, 1, 2, 3, -2, -1] # indices
entries = []

v = np.sqrt(vx0**2 + vy0**2)

monitor_lbls = ["run", "stopped", "v"]
monitor_vars = [run, stopped, v]
monitor_dict = dict(zip(monitor_lbls, monitor_vars))
monitors = []

class Cyclotron:
    def __init__(self, canvas, z, params, timescale):
        self.canvas = canvas
        self.x, self.y, self.vx, self.vy = z
        self.q, self.m, self.B, self.E, self.gap, self.d_r = params
        self.timescale = timescale

        # center features
        self.c_x = CANVAS_W/2
        self.c_y = CANVAS_H/2

        # animation features
        self.fps = 100
        self.ms = 1000/self.fps # time interval between frames (ms)
        
        self.dt = 1e-3 * self.ms * self.timescale # time step (s)
        self.t = np.array([0, self.dt])
        # running_time = 600 # s
        # # n_frames=1000
        # n_frames = running_time*fps

    def set_colors(self):
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

    def draw_first_frame(self):
        global v
        v = np.sqrt(self.vx**2 + self.vy**2)
        monitors_update()

        self.set_colors()

        c_x = self.c_x
        c_y = self.c_y

        # dees features
        d_r = self.d_r * scale
        d_gap = self.gap * scale
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
                                         outline=self.d1_color,
                                         style=tk.PIESLICE)
        self.d2 = self.canvas.create_arc(d2_coord,
                                         start=270, extent=180,
                                         outline=self.d2_color,
                                         style=tk.PIESLICE)

        # particle features
        self.p_r = 3 # particle radius (pixel)
        p_r = self.p_r
        x = self.x * scale
        y = self.y * scale
        coord = (c_x - (x - p_r),
                 c_y - (y - p_r),
                 c_x - (x + p_r),
                 c_y - (y + p_r))
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

    def move_particle(self):
        global v
        t1 = time.time()
        v = np.sqrt(self.vx**2 + self.vy**2)
        monitors_update()
        self.set_colors()
        if run:
            z0 = self.x, self.y, self.vx, self.vy
            params = self.q, self.m, self.B, self.E, self.gap, self.d_r
            old_x = self.x * scale
            old_y = self.y * scale
            self.compute_coord(z0, self.t, params)
            c_x = self.c_x
            c_y = self.c_y
            p_r = self.p_r
            x = self.x * scale
            y = self.y * scale
            if ( # particle would go out of canvas
                 (c_x - x < 0)
                 or
                 (c_x - x > CANVAS_W)
                 or
                 (c_y - y < 0)
                 or
                 (c_y - y > CANVAS_H)
                ):
                PlayPause()
                btn_play["state"] = "disabled"
                return
            else:
                coord = (c_x + (x - p_r),
                         CANVAS_H - (c_y + (y - p_r)),
                         c_x + (x + p_r),
                         CANVAS_H - (c_y + (y + p_r)))
                self.canvas.coords(self.particle, coord)
                self.canvas.itemconfigure(self.particle,
                                          fill=self.p_color,
                                          outline=self.p_color)
                self.canvas.itemconfigure(self.d1, outline=self.d1_color)
                self.canvas.itemconfigure(self.d2, outline=self.d2_color)
                x1 = c_x + old_x
                x2 = c_x + x
                y1 = CANVAS_H - (c_y + old_y)
                y2 = CANVAS_H - (c_y + y)

                self.canvas.create_line(x1, y1, x2, y2, fill=self.p_color)
                self.dt = 1e-3 * self.ms * self.timescale # time step (s)
                if (self.t[1] - self.t[0]) == self.dt:
                    self.t += self.dt
                else:
                    self.t[0] = self.t[1]
                    self.t[1] = self.t[0] + self.dt
                t2 = time.time()
                delay = (t2 - t1)*1000
                if self.ms >= delay:
                    self.canvas.after(int(self.ms - delay), self.move_particle)
                else:
                    # print("delayed frame")
                    self.canvas.after(0, self.move_particle)
                # self.canvas.after(int(self.ms - delay), self.move_particle)
        else:
            pass

def monitors_update():
    global monitors, monitor_dict
    # monitor_lbls = ["run", "stopped"]
    monitor_vars = [run, stopped, v]
    monitor_dict = dict(zip(monitor_lbls, monitor_vars))
    for i, m in enumerate(monitor_dict.items()):
        if isinstance(m[1], (int, float)) and (type(m[1]) != bool):
            monitors[i]["text"] = f"{m[0]} = {m[1]:.4e}"
        else:
            monitors[i]["text"] = f"{m[0]}: {m[1]}"

def TscaleDown():
    global cycl, timescale
    timescale = timescale / 10**(1/5)
    lbl_tscale["text"] = f"Time scale = {timescale:.3e}"
    cycl.timescale = timescale


def TscaleUp():
    global cycl, timescale
    timescale = timescale * 10**(1/5)
    lbl_tscale["text"] = f"Time scale = {timescale:.3e}"
    cycl.timescale = timescale

def Animate():
    cycl.move_particle()

def UpdateParams():
    global cycl
    # z = input_data[:4]
    params = input_data[4:]
    cycl.q, cycl.m, cycl.B, cycl.E = params[:-2]
    cycl.timescale = timescale

def FirstFrame():
    global cycl, canvas
    canvas.delete(tk.ALL)
    z = input_data[:4]
    params = input_data[4:]
    cycl = Cyclotron(canvas, z, params, timescale)
    cycl.draw_first_frame()

def SetEntries():
    global entries
    for i, p in enumerate(input_data):
        entries[i].delete(0, tk.END)
        entries[i].insert(0, f"{p:.3e}")

def PlayPause():
    global run, btn_play, stopped
    run = not run
    stopped = False
    monitors_update()
    if run:
        Animate()
        btn_play.configure(text="\u23F8")
        for i in static_params:
            entries[i]["state"] = "disabled"
    else:
        btn_play.configure(text="\u25B6")

def Stop():
    global stopped
    stopped = True
    monitors_update()
    if (btn_play["state"] == "disabled"):
        btn_play["state"] = "normal"
    else:
        pass

    for i in static_params:
        entries[i]["state"] = "normal"
    FirstFrame()
    if run:
        PlayPause()
        Stop()
    else:
        pass

def Read():
    global input_data, entries
    for i, entry in enumerate(entries):
        try:
            input_data[i] = float(entry.get())
        except ValueError:
            input_data[i] = default_data[i]
        entries[i].delete(0, tk.END)
        entries[i].insert(0, f"{input_data[i]:.3e}")
    
    if (not stopped):    
        UpdateParams()
    else:
        Stop()
    # UpdateParams()
    
def Reset():
    global input_data, timescale
    input_data = np.array(default_data, dtype=float)
    timescale = default_timescale
    lbl_tscale["text"] = f"Time scale = {timescale:.3e}"
    SetEntries()
    Read()
    
def SetWindow():
    global canvas
    global btn_play, btn_stop, btn_read, btn_tscale_down, btn_tscale_up
    global entries, lbl_tscale, monitors
    # initialize root Window
    root = tk.Tk()
    root.title("Cyclotron")
    root.resizable(False,False)
    
    # Two principal frames, for canvas and sidebar
    frm_canvas = tk.Frame(master=root, relief=tk.RIDGE, borderwidth=2)
    frm_side = tk.Frame(master=root, relief=tk.RIDGE, borderwidth=1)
    
    # Canvas inside his frame
    canvas = tk.Canvas(frm_canvas, width=CANVAS_W, height=CANVAS_H, bg="white")
    canvas.pack()
    frm_canvas.grid(row=0, column=0)
    
    # Buttons inside buttons frame (inside side frame)
    frm_btns = tk.Frame(master=frm_side, relief=tk.RIDGE, borderwidth=1)
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
    frm_btns.pack()
    
    # Labels and entries inside data frame (inside side frame)
    frm_data = tk.Frame(master=frm_side, relief=tk.RIDGE, borderwidth=1)
    entries = []
    for i, label in enumerate(labels):
        lbl_par = tk.Label(master=frm_data, text=f"{label} =")
        entries.append(tk.Entry(master=frm_data))
        lbl_unit = tk.Label(master=frm_data, text=units[i])
        
        lbl_par.grid(row=i, column=0, sticky="SE", pady=3)
        entries[i].grid(row=i, column=1, sticky="S", pady=3)
        lbl_unit.grid(row=i, column=2, sticky="SW", pady=3)
    frm_data.pack(pady=25)

    # Timescale buttons and label inside their frame (inside side frame)
    frm_tscale = tk.Frame(master=frm_side, relief=tk.RIDGE, borderwidth=1)
    btn_tscale_down = tk.Button(master=frm_tscale, text="-", command=TscaleDown)
    btn_tscale_down.grid(row=0, column=0, sticky="nsew")
    lbl_tscale = tk.Label(master=frm_tscale)
    lbl_tscale.grid(row=0, column=1)
    btn_tscale_up = tk.Button(master=frm_tscale, text="+", command=TscaleUp)
    btn_tscale_up.grid(row=0, column=2, sticky="nsew")
    frm_tscale.pack()
    

    # Monitor labels inside monitor frame (inside side frame)
    monitors = []
    frm_monitors = tk.Frame(master=frm_side, relief=tk.RIDGE, borderwidth=1)
    for i, m in enumerate(monitor_dict.items()):
        # monitors.append(tk.Label(master=frm_monitors, text=f"{m[0]}: {m[1]}"))
        monitors.append(tk.Label(master=frm_monitors))
        monitors[i].grid(row=i, column=0, sticky="W", pady=3)
    frm_monitors.pack(side="bottom", fill="both")

    frm_side.grid(row=0, column=1, sticky="NSW")

    Reset()

    root.mainloop()

if __name__ == '__main__':
   SetWindow()
