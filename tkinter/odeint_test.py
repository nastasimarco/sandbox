"""Odeint test for the motion of a particle in a cyclotron."""

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import odeint, solve_ivp
from scipy import signal
import time

def derive(t, z, params):
    """Compute the derivative of input z (tuple containing x, y, vx, vy)
    at time t.
    params contains: charge, mass, B field, E field, gap size, dee radius.
    """
    x, y, vx, vy = z
    q, m, B, E, gap, d_r = params
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
        # ax = (q/m * B * (vy)) + (q/m * E*np.cos(q*B*t/m))
        ax = (q/m * B * (vy)) + (q/m * E*signal.square(q*B*t/m + np.pi/2))
        ay = - q/m * B * (vx)
    else: # outer region, E_field = 0, B_field = 0
        ax = 0
        ay = 0

    derivs = [vx, vy, ax, ay]
    return derivs

# initial conditions
x0 = 0
y0 = 0
vx0 = 0
vy0 = 0
v0 = np.sqrt(vx0**2 + vy0**2)
z0 = [x0, y0, vx0, vy0]

# constant parameters (arbitrary units)
q = 1 # charge
m = 1 # mass
B = 1 # B field
E = 10 # E field
gap = 20 # gap size
d_r = 250 # dee radius
params = [q, m, B, E, gap, d_r]

# define t array 
n_periods = 100
ppp = 200 # points per period
t = np.linspace(0, np.round(2*np.pi*n_periods + np.pi/2), num=ppp*n_periods)

t1 = time.time()
# solve the differential equations using odeint
sol = odeint(derive, z0, t, args=(params,), tfirst=True)
# ivp_sol = solve_ivp(derive, (t[0], t[-1]), z0, args=(params,), dense_output=True)
t2 = time.time()
print("Time taken to solve with odeint:",t2-t1)
x = sol[:, 0]
y = sol[:, 1]
vx = sol[:, 2]
vy = sol[:, 3]

v = np.sqrt(vx**2 + vy**2)
R = (m*v) / (q*B)

ax = np.zeros(x.shape)
ay = np.zeros(y.shape)

for i in range(len(x)):
    _, _, ax[i], ay[i] = derive(t[i], sol[i,:], params)

plt.figure()

plt.subplot(1, 2, 1)
plt.plot(x, y, '.-', markersize=1, linewidth=0.5)
plt.axvline(x=-gap/2)
plt.axvline(x=gap/2)
plt.xlabel("x (a.u.)")
plt.ylabel("y (a.u.)")
plt.gca().set_aspect('equal', adjustable='box')
plt.xlim([- (d_r + 50) , (d_r + 50)])
plt.ylim([- (d_r + 50) , (d_r + 50)])


# plt.figure()
plt.subplot(1, 2, 2)
plt.axhline(y=-gap/2, color="black", linewidth=0.5)
plt.axhline(y=+gap/2, color="black", linewidth=0.5)
plt.plot(t, v0 + np.sqrt(2*m*q*E*gap*t/np.pi), label='Theoretic velocity increase')
plt.plot(t, v, '.', markersize=1, label='velocity magnitude')
plt.plot(t, x, '.', markersize=1, label='x coordinate')
# plt.plot(t, vx, '.', markersize=1, label='vx')
plt.plot(t, ax, '.', markersize=1, label='ax')
# plt.plot(t, y, '.', markersize=0.5, label='y coordinate')
# plt.plot(t, (q/m * E*np.cos(q*B*t/m)), '.', markersize=1, label='qE/m')
plt.plot(t, (q/m * E*signal.square(q*B*t/m + np.pi/2)), label='qE/m')
plt.xlabel("time (a.u.)")
plt.ylim([-d_r, d_r])
plt.legend()
plt.grid()
# plt.ion()

plt.show()
