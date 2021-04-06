# import numpy as np
# from scipy.integrate import odeint
# import matplotlib.pyplot as plt

# def dydt(y0, t, params):
#     x, v = y0
#     g, = params
#     derivs = [v, g]
#     return derivs

# x0 = 0
# v0 = 0
# y0 = [x0, v0]

# g = -9.8
# params = [g]

# t = np.linspace(0, 100)

# sol = odeint(dydt, y0, t, args=(params,))
# x = sol[:, 0]
# plt.plot(t, x)
# plt.plot(t, x0 + v0*t + 0.5*g*t**2, "--")
# plt.show()


import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import odeint

def func(z, t, params):
    x, y, vx, vy = z
    q, m, B, E, gap, D_r = params
    if ( # inside one of the dees, E_field = 0
          ((x <= - gap/2) and ((x + gap/2)**2 + (y)**2 <= D_r**2))
          or
          ((x >= + gap/2) and ((x - gap/2)**2 + (y)**2 <= D_r**2))
        ):
        ax = (q/m * B * (vy))
        ay = - q/m * B * (vx)
    elif ( # inside the gap, E_field != 0
          (x > - gap/2) and (x < gap/2) and (y > - D_r) and (y < D_r)
         ):
        ax = (q/m * B * (vy)) + (q/m * E*np.cos(q*B*t/m))
        ay = - q/m * B * (vx)
    else:
        ax = 0
        ay = 0
    derivs = [vx, vy, ax, ay]
    return derivs

x0 = 0
y0 = 0
vx0 = 0
vy0 = 0
v0 = np.sqrt(vx0**2 + vy0**2)
z0 = [x0, y0, vx0, vy0]

q = 1
m = 1
B = 1
E = 50
gap = 10
D_r = 200 # dee radius
params = [q, m, B, E, gap, D_r]

n_periods = 10
t = np.linspace(0, 2*np.pi*n_periods + np.pi/2, num=200*n_periods)

sol = odeint(func, z0, t, args=(params,))
x = sol[:, 0]
y = sol[:, 1]
vx = sol[:, 2]
vy = sol[:, 3]
v = np.sqrt(vx**2 + vy**2)
R = (m*v) / (q*B)

plt.plot(x, y, '.-')
plt.axvline(x=-gap/2)
plt.axvline(x=gap/2)
# plt.plot(t, vx, '.', t, vy, '.')
plt.gca().set_aspect('equal', adjustable='box')
# plt.xlim([-100, 100])
# plt.ylim([-100, 100])

plt.figure()
plt.plot(t, v0 + np.sqrt(2*m*q*E*gap*t/np.pi), t, R)

plt.show()
