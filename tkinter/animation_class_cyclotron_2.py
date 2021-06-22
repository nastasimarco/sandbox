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
        self.scale = 1e3 # px/m
        self.default_timescale = 6.7e-5
        self.timescale = self.default_timescale

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
        self.default_data = (x0, y0, vx0, vy0, qp, mp, B0, E0, gap0, dr0)
        self.labels = ("x\u2080", "y\u2080", "vx\u2080", "vy\u2080",
                       "q", "m", "B", "E", "gap", "D radius")
        self.units = ("m", "m", "m/s", "m/s", "C", "Kg", "T", "V/m", "m", "m")
        self.monitors_texts = ["v = 0 m/s"]
        self.static_params = [0, 1, 2, 3, -2, -1] # indices

        self.input_data = np.array(self.default_data, dtype=float)
        
        z = self.input_data[:4]
        params = self.input_data[4:]
        self.x, self.y, self.vx, self.vy = z
        self.q, self.m, self.B, self.E, self.gap, self.d_r = params

        # animation features
        self.fps = 100
        self.ms = 1000/self.fps # time interval between frames (ms)
        
        self.dt = 1e-3 * self.ms * self.timescale # time step (s)
        self.t = np.array([0, self.dt])

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

    def monitors_update(self, monitors):
        self.v = np.sqrt(self.vx**2 + self.vy**2)

        monitors[0]["text"] = f"v = {self.v:.4e} m/s"
        # monitor_lbls = ["v"]
        # monitor_vars = [v]
        # monitor_dict = dict(zip(monitor_lbls, monitor_vars))
        # monitor_vars = [v]
        # monitor_dict = dict(zip(monitor_lbls, monitor_vars))
        # for i, m in enumerate(monitor_dict.items()):
        #     if isinstance(m[1], (int, float)) and (type(m[1]) != bool):
        #         monitors[i]["text"] = f"{m[0]} = {m[1]:.4e}"
        #     else:
        #         monitors[i]["text"] = f"{m[0]}: {m[1]}"

    def draw_first_frame(self, canvas):
        self.canvas = canvas

        # center features
        self.cx = int(self.canvas["width"])/2
        self.cy = int(self.canvas["height"])/2
        # self.cx = CANVAS_W/2
        # self.cy = CANVAS_H/2
        

        self.monitors_update(monitors)

        cx = self.cx
        cy = self.cy
        scale = self.scale
        self.set_colors()

        # dees features
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

    def move_particle(self, PlayPause_func, btn_play, status_bar):
        # global v
        t1 = time.time()
        # v = np.sqrt(self.vx**2 + self.vy**2)
        move_params = (PlayPause_func, btn_play, status_bar)
        self.set_colors()
        if run:
            self.monitors_update(monitors)
            z0 = self.x, self.y, self.vx, self.vy
            params = self.q, self.m, self.B, self.E, self.gap, self.d_r
            scale = self.scale
            cx = self.cx
            cy = self.cy
            p_r = self.p_r

            old_x = self.x * scale
            old_y = self.y * scale
            self.compute_coord(z0, self.t, params)
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
                # PlayPause()
                PlayPause_func
                btn_play["state"] = "disabled"
                msg = "Animation ended, next position would be out of canvas."
                status_bar["text"] = msg
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
                x1 = cx + old_x
                x2 = cx + x
                y1 = CANVAS_H - (cy + old_y)
                y2 = CANVAS_H - (cy + y)

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
                    d_ms = int(self.ms - delay)
                    # TODO: controllare se funziona
                    self.canvas.after(d_ms, self.move_particle, *move_params)
                else:
                    # print("delayed frame")
                    self.canvas.after(0, self.move_particle, *move_params)
                # self.canvas.after(int(self.ms - delay), self.move_particle)
        else:
            pass

def TscaleDown():
    global cycl, timescale, lbl_tscale
    timescale = timescale / 10**(1/5)
    lbl_tscale["text"] = f"Time scale = {timescale:.3e}"
    cycl.timescale = timescale

def TscaleUp():
    global cycl, timescale, lbl_tscale
    timescale = timescale * 10**(1/5)
    lbl_tscale["text"] = f"Time scale = {timescale:.3e}"
    cycl.timescale = timescale

def Animate():
    global cycl
    move_params = (PlayPause, btn_play, status_bar)
    cycl.move_particle(*move_params)

def UpdateParams():
    global cycl
    # z = input_data[:4]
    params = input_data[4:]
    cycl.q, cycl.m, cycl.B, cycl.E = params[:-2]
    cycl.timescale = timescale

def FirstFrame():
    # TODO: va resettato anche il tempo o istanziata da zero la classe
    global cycl, canvas
    canvas.delete(tk.ALL)
    z = input_data[:4]
    params = input_data[4:]
    # cycl = Cyclotron()
    cycl.t = np.array([0, cycl.dt])
    cycl.x, cycl.y, cycl.vx, cycl.vy = z
    cycl.q, cycl.m, cycl.B, cycl.E, cycl.gap, cycl.d_r = params
    cycl.draw_first_frame(canvas)

def PlayPause():
    global run, btn_play, stopped, entries
    run = not run
    stopped = False
    cycl.monitors_update(monitors)
    if run:
        status_bar["text"] = "Playing..."
        Animate()
        btn_play.configure(text="\u23F8")
        for i in cycl.static_params:
            entries[i]["state"] = "disabled"
    else:
        status_bar["text"] = "Paused"
        btn_play.configure(text="\u25B6")

def Stop():
    global stopped, btn_play, entries
    stopped = True
    cycl.monitors_update(monitors)
    if (btn_play["state"] == "disabled"):
        btn_play["state"] = "normal"
    else:
        pass

    for i in cycl.static_params:
        entries[i]["state"] = "normal"

    FirstFrame()

    if run:
        PlayPause()
        Stop()
    else:
        status_bar["text"] = "Ready"
        pass

def Read():
    global input_data, entries
    for i, entry in enumerate(entries):
        try:
            input_data[i] = float(entry.get())
        except ValueError:
            input_data[i] = cycl.default_data[i]
        entries[i].delete(0, tk.END)
        entries[i].insert(0, f"{input_data[i]:.3e}")
    
    if (not stopped):    
        UpdateParams()
    else:
        Stop()
    # UpdateParams()

def SetEntries():
    global entries
    for i, p in enumerate(input_data):
        entries[i].delete(0, tk.END)
        entries[i].insert(0, f"{p:.3e}")
    
def Reset():
    global input_data, timescale, lbl_tscale
    input_data = np.array(cycl.default_data, dtype=float)
    # input_data = cycl.input_data
    timescale = cycl.default_timescale
    lbl_tscale["text"] = f"Time scale = {timescale:.3e}"
    SetEntries()
    Read()
    
def SetWindow(labels, units, monitors_texts):
    global canvas, root
    global btn_play, btn_stop, btn_read, btn_tscale_down, btn_tscale_up
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
        entries.append(tk.Entry(master=frm_data))
        lbl_unit = tk.Label(master=frm_data, text=units[i])
        lbl_par.grid(row=i, column=0, sticky="SE", pady=3)
        entries[i].grid(row=i, column=1, sticky="S", pady=3)
        lbl_unit.grid(row=i, column=2, sticky="SW", pady=3)
    frm_data.pack(pady=25)

    # Timescale buttons and label inside their frame (inside side frame)
    frm_tscale = tk.Frame(master=frm_side, relief=tk.RIDGE, borderwidth=0)
    btn_tscale_down = tk.Button(master=frm_tscale, text="-", command=TscaleDown)
    btn_tscale_down.grid(row=0, column=0, sticky="nsew")
    lbl_tscale = tk.Label(master=frm_tscale)
    lbl_tscale.grid(row=0, column=1, padx=4)
    btn_tscale_up = tk.Button(master=frm_tscale, text="+", command=TscaleUp)
    btn_tscale_up.grid(row=0, column=2, sticky="nsew")
    frm_tscale.pack()
    
    # Monitor labels inside their frame (inside side frame)
    monitors = []
    frm_monitors = tk.Frame(master=frm_side, relief=tk.RIDGE, borderwidth=1)
    for i, _ in enumerate(monitors_texts):
        # monitors.append(tk.Label(master=frm_monitors, text=f"{m[0]}: {m[1]}"))
        monitors.append(tk.Label(master=frm_monitors))
        monitors[i].grid(row=i, column=0, sticky="W", padx=10, pady=3)
    # frm_monitors.pack(side="bottom", fill="both")
    frm_monitors.pack(pady=40)

    # Status bar inside his frame (inside side frame)
    frm_satus = tk.Frame(master=frm_side, relief=tk.RIDGE, borderwidth=1)
    status_text = "Ready"
    status_bar = tk.Label(master=frm_satus, text=status_text)
    status_bar.grid(row=0, column=0, sticky="E", pady=3)
    frm_satus.pack(side="bottom", fill="both")

    frm_side.grid(row=0, column=1, sticky="NSW")

    Reset()

    root.mainloop()

if __name__ == '__main__':
   global cycl
   Cyclo = Cyclotron()
   cycl = Cyclo
   SetWindow(Cyclo.labels, Cyclo.units, Cyclo.monitors_texts)
#    Reset()
