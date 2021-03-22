import tkinter as tk
import random
import time
import math

window = tk.Tk()
window.title("Second animation")

WIDTH = 800
HEIGHT = 600
window.resizable(False,False)

canvas = tk.Canvas(window, width=WIDTH, height=HEIGHT, bg='white')
canvas.grid(row=0, column=0)


# center features
x_c = 400
y_c = 300
r_c = 1

# animation features
fps = 24
dt = round(1000/fps) # time step
running_time = 10 # s
# n_frames=1000
n_frames = running_time*fps

# motion features
omega = math.pi # rad/s
theta0 = math.pi/8
radius = 100 # pixels

# disc features
x = radius*math.cos(theta0) + x_c
y = radius*math.sin(theta0) + y_c
r_disc = 5

center = canvas.create_oval(x_c-r_c, y_c-r_c, x_c+r_c, y_c+r_c, fill="black")
circle = canvas.create_oval(x_c-radius, y_c-radius, x_c+radius, y_c+radius)
disc = canvas.create_oval(x-r_disc, y-r_disc, x+r_disc, y+r_disc, fill="red")

canvas.update()
canvas.after(dt)

t0 = time.time()
delay_sum = 0
for i in range(n_frames):
    t1 = time.time()

    dx = (radius*math.cos(theta0 + (i+1)*dt/1000*omega) + x_c) - x
    dy = (radius*math.sin(theta0 + (i+1)*dt/1000*omega) + y_c) - y
    x+=dx
    y+=dy
    canvas.move(disc, dx, dy)
    canvas.update()

    t2 = time.time()
    delay = t2-t1
    delay_sum += delay

    canvas.after(dt)


tend = time.time()
print(f"mean delay per frame: {delay_sum*1000/n_frames:2.2f} ms @ {fps} fps")
print(f"total delay: {delay_sum*1000:2.2f} ms @ {fps} fps")
print(f"given running time: {running_time:.2f} s")
print(f"actual running time: {tend-t0:.2f} s")

# window.mainloop()
