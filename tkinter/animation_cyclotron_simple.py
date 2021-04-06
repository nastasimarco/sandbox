import tkinter as tk
import random
import time
import math

window = tk.Tk()
window.title("Simple Cyclotron")

WIDTH = 800
HEIGHT = 600
window.resizable(False,False)

canvas = tk.Canvas(window, width=WIDTH, height=HEIGHT, bg='white')
canvas.grid(row=0, column=0)

# center features
x_c = WIDTH/2
y_c = HEIGHT/2

# animation features
fps = 100
dt = 1/fps # time step (s)
running_time = 90 # s
# n_frames=1000
n_frames = running_time*fps

# dees features
d_r = 250 # dee radius
d_gap = 50
d1_coord = (x_c - (d_r + d_gap/2), y_c - d_r, x_c + (d_r - d_gap/2), y_c + d_r)
d2_coord = (x_c - (d_r - d_gap/2), y_c - d_r, x_c + (d_r + d_gap/2), y_c + d_r)
d1_c_x = x_c - d_gap/2
d2_c_x = x_c + d_gap/2
d1_c_y = y_c
d2_c_y = y_c

# particle features
x = x_c - 1
y = y_c + 25
r_disc = 2
charge = 1
mass = 1
coord = (x - r_disc, y - r_disc, x + r_disc, y + r_disc)

# motion features
B_field = 5
E_field_0 = 300
vx = 0
vy = 0
ax = 0
ay = 0
cycl_freq = charge*B_field / mass

# graphical features
disc = canvas.create_oval(coord, outline="red", fill="red")
d1 = canvas.create_arc(d1_coord,
                       start=90, extent=180,
                       outline="blue", style=tk.PIESLICE)
d2 = canvas.create_arc(d2_coord,
                       start=270, extent=180,
                       outline="red", style=tk.PIESLICE)

region = canvas.create_text(100, 20, text="Region: gap")
E_text = canvas.create_text(100, 40, text=f"E_field = {E_field_0:.2f}")
vx_text = canvas.create_text(100, 60, text=f"v_x = {vx:.2f}")
vy_text = canvas.create_text(100, 80, text=f"v_y = {vy:.2f}")
v_text = canvas.create_text(100, 100, text=f"v = {0:.2f}")
K_text = canvas.create_text(100, 120, text=f"K = {0:.2f}")
R_text = canvas.create_text(100, 140, text=f"R = {0:.2f}")

time_scale = 1

delayed_frames = 0
ontime_frames = 1
over_delay = False

t0 = time.time()
canvas.update()
canvas.after(round(dt*1000))
delay_sum = 0


for i in range(n_frames - 1):
    t1 = time.time()
    t = i * dt
    # t = (i)*(dt/1000)
    E_field = E_field_0 * -math.sin(cycl_freq*t)
    v = math.sqrt(vx**2 + vy**2)
    radius = (mass*v) / (charge*B_field)

    canvas.itemconfigure(E_text, text=f"E_field = {E_field:.2f}")
    canvas.itemconfigure(vx_text, text=f"v_x = {vx:.2f}")
    canvas.itemconfigure(vy_text, text=f"v_y = {vy:.2f}")
    canvas.itemconfigure(v_text, text=f"v = {v:.2f}")
    canvas.itemconfigure(K_text, text=f"K = {0.5*mass*(v**2):.2f}")
    canvas.itemconfigure(R_text, text=f"R = {radius:.2f}")

    # print(f"t = {t:.3f}", f"E = {E_field/E_scale:.3f}")
    # print(f"x = {x:.2f}, vx = {vx:.2f}")
    # print(f"y = {y:.2f}, vy = {vy:.2f}")
    # print()
    # print(f"x = {x:.2f}, vx = {vx:.2f}, ax = {ax:.3f}")
    # print(f"y = {y:.2f}, vy = {vy:.2f}, ay = {ay:.3f}")

    if E_field > 0:
        canvas.itemconfigure(d1, outline="red")
        canvas.itemconfigure(d2, outline="blue")
    else:
        canvas.itemconfigure(d1, outline="blue")
        canvas.itemconfigure(d2, outline="red")

    if ( # inside the gap, E_field != 0
        (x < (x_c + d_gap/2)) and
        (x > (x_c - d_gap/2)) and
        (y < (y_c + d_r)) and
        (y > (y_c - d_r))
       ):
        canvas.itemconfigure(region, text="Region: gap")
        Fx = charge*E_field
        ax = Fx/mass + (cycl_freq)**2 * radius * (- math.cos(cycl_freq*t))
        ay = (cycl_freq)**2 * radius * (- math.sin(cycl_freq*t))
        # ax = Fx/mass
        # ay = 0
        dx = vx*dt + 0.5*ax*(dt**2)
        dy = vy*dt
        dvx = ax*dt
        dvy = ay*dt
        vx += dvx
        vy += dvy
        # vx = dvx + ((cycl_freq*radius) * (- math.sin(cycl_freq*t)))
        # vy = dvy + ((cycl_freq*radius) * (+ math.cos(cycl_freq*t)))
    elif ( # inside one of the dees, E_field = 0
          ((x <= d1_c_x) and ((x - d1_c_x)**2 + (y - d1_c_y)**2 <= d_r**2))
          or
          ((x >= d2_c_x) and ((x - d2_c_x)**2 + (y - d2_c_y)**2 <= d_r**2))
         ):
        canvas.itemconfigure(region, text="Region: dees")
        # radius = mass*math.sqrt(vx**2 + vy**2) / (charge*B_field)
        # dx = (radius*math.cos(cycl_freq*t) + x_c) - x
        # dy = (radius*math.sin(cycl_freq*t) + y_c) - y
        # dx = vx*dt
        # dy = vy*dt
        ax = (cycl_freq)**2 * radius * (- math.cos(cycl_freq*t))
        ay = (cycl_freq)**2 * radius * (- math.sin(cycl_freq*t))

        dx = vx*dt + 0.5*ax*(dt**2)
        dy = vy*dt + 0.5*ay*(dt**2)

        # dvx = ax*dt
        # dvy = ay*dt
        # vx += dvx
        # vy += dvy
        vx = (cycl_freq*radius) * (- math.sin(cycl_freq*t))
        vy = (cycl_freq*radius) * (+ math.cos(cycl_freq*t))
    else:
        canvas.itemconfigure(region, text="Region: outer")
    if x+dx < 0 or x+dx > WIDTH or y+dy < 0 or y+dy > HEIGHT:
        break
    # dy = -dy # fix the direction of y axis
    canvas.create_line(x, y, x + dx, y + dy, fill="red")
    x+=dx
    y+=dy
    canvas.move(disc, dx, dy)
    canvas.update()

    t2 = time.time()
    delay = t2-t1
    delay_sum += delay
    if delay < dt:
        canvas.after(round((dt - delay)*1000*time_scale))
        ontime_frames += 1
    else:
        canvas.after(0)
        over_delay = True
        delayed_frames += 1

t_end = time.time()
print(f"mean delay per frame: {delay_sum*1000/n_frames:2.2f} ms @ {fps} fps")
print(f"total delay: {delay_sum*1000:2.2f} ms @ {fps} fps")
print(f"given running time: {running_time:.2f} s")
print(f"actual running time: {t_end-t0:.2f} s")
if over_delay:
    print(f"Could not provide {delayed_frames} frame(s) fast enough.")
    print(f"{ontime_frames}/{delayed_frames+ontime_frames} frames on time.")
else:
    print(f"All {ontime_frames} frames on time!")

window.mainloop()
