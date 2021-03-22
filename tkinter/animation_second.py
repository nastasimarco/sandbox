import tkinter as tk
import random
import time
window = tk.Tk()
window.title("Second animation")

WIDTH = 800
HEIGHT = 600
window.resizable(False,False)

canvas = tk.Canvas(window, width=WIDTH, height=HEIGHT, bg='white')
canvas.grid(row=0, column=0)

x_c = 400
y_c = 300
radius = 20
fps = 30
delay = round(1000/fps)
running_time = 30 # s
# n_frames=1000
n_frames = running_time*fps

speed_scale = .1
v_x = 800*speed_scale # pixels/s
v_y = 600*speed_scale # pixels/s
dx = v_x/fps
dy = v_y/fps

# fps_counter = tk.Label(window, text=f"dt =", font="TkFixedFont", width=25)
# fps_counter.grid(row=0, column=1, sticky="nw")

disc = canvas.create_oval(x_c-radius, y_c-radius, x_c+radius, y_c+radius, fill="red")
canvas.update()
canvas.after(delay)
# time.sleep(delay/1000)
t0 = time.time()
dt_sum = 0
for i in range(n_frames):
    t1 = time.time()
    x_min, y_min, x_max, y_max = canvas.coords(disc)
    if (x_min<=0) or (x_max>=WIDTH):
        dx = -dx
    if (y_min<=0) or (y_max>=HEIGHT):
        dy = -dy
    # canvas.move(disc, random.randint(-10, 10), random.randint(-10, 10))
    canvas.move(disc, dx, dy)
    canvas.update()
    t2 = time.time()
    dt = t2-t1
    dt_sum += dt
    # fps_counter["text"]=f"dt_sum = {dt_sum*1000:2.2f} ms"
    # if dt*1000 < delay:
    #     canvas.after(round(delay-dt*1000))
    # time.sleep(delay/1000 - dt)
    canvas.after(delay)


tend = time.time()
print(f"mean dt per frame: {dt_sum*1000/n_frames:2.2f} ms @ {fps} fps")
print(f"total dt: {dt_sum*1000:2.2f} ms @ {fps} fps")
print(f"given running time: {running_time:.2f} s")
print(f"actual running time: {tend-t0:.2f} s")

# for i in range(n_frames):
#     canvas.after(delay)
#     x_c+=random.randint(-10, 10)
#     y_c+=random.randint(-10, 10)
#     canvas.create_oval(x_c-radius, y_c-radius, x_c+radius, y_c+radius, fill="red")
#     canvas.update()


# window.mainloop()
