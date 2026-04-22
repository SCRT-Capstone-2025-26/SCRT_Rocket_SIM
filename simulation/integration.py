# from numpy import pi
import numpy as np
import scipy
import matplotlib.pyplot as plt

## Given an intial condition (u) a  scipy scheme
## a forcing function (f) an end time (T)
## and a time step (dt)
## This function records the time series made by the
## output u such that u'=f and u(0)=u0


def scipyintegrate(u0, scheme, f, max_t, dt, t0=0):
    # print(u0,'u0')
    u = [u0,u0]
    t = [t0,t0]
    solution = scheme(f, t0, u0, max_t, max_step=dt)
# while the change in height is not largely negative 
# (so we simulate the rise and the start of the fall of our flight path)
    while (u[-1][0]-u[-2][0])/dt >= -10  and t[-1]< max_t:  #
        solution.step()
        t += [solution.t]
        u += [solution.y]
        # print(t[-1],u[-1][0])
    return np.array(u), np.array(t)
    # return np.array(solution.y),np.array(solution.t)


# Finite Difference Scheme(FDS) integrator
def integrate(u0, scheme, f, t, dt):
    u = u0
    # print(u)
    num_steps = np.ceil(t / dt)
    for n in range(num_steps):
        u += [scheme(f, dt * n, dt, u)]
        if u[-1][0] < 0:
            return u
    return u


def double_step(scheme):
    return lambda f, t, dt, u: scheme(
        f, t + dt / 2, dt / 2, u + [scheme(f, t, dt / 2, u)]
    )


def integrate_adaptive(u0, scheme, f, t, dt, t0=0, batch=1, scheme2=None, tol=None):
    if tol is None:
        tol = dt / 1000
    if scheme2 is None:
        scheme2 = double_step(scheme)
    u = [u0[0] for i in range(batch + 1)]
    t = [t0 for i in range(batch + 1)]
    # print(u)
    while t[-1] < t + t0:
        err = np.linalg.norm(scheme(f, t[-1], dt, u) - scheme2(f, t[-1], dt, u))
        # err/=np.linalg.norm(scheme(f,t[-1],dt,u))
        if err > tol:
            # print(err,dt,t[-1])
            u = u[:-batch]
            t = t[:-batch]
            dt /= 4.0
        else:
            dt *= 1.1
        for i in range(batch):
            t += [t[-1] + dt]
            u += [scheme(f, t[-1], dt, u)]
            if u[-1][0] < 0 or t[-1] > t:
                return np.array(u), np.array(t)
    return np.array(u), np.array(t)


if __name__ == "__main__":
    u, t = scipyintegrate(
        np.array([1.0, 0]),
        scipy.integrate.RK45,
        lambda t, u: np.array([-u[1], np.sin(u[0])]),
        200,
        0.01,
        t0=-0.5,
    )
    print("time steps: " + str(t))
    print("u values: "+  str(u[:, 0]))
    plt.plot(t, u[:, 0])
    plt.show()
