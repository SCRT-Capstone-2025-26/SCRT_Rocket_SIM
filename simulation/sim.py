import matplotlib.pyplot as plt
import time
import numpy as np
from math import sin,cos,pi
from utilities import sign
from integration import scipyintegrate, integrate_adaptive
from FDS import Heun
import scipy



#initial conditions
T=200;dt=.05;
U0=np.array([0,0,0,0])#u[0]=height u[1]=velocity

#physical constants
def DrafCoeff(h,v,a):#TODO consider Angle
    return -sign(v)*0.55
def AirDensity(h):
    return 1.2*.99988**h
def Thrust(t):
    return 3000 if t<4 else 0
g=-10
Area=(pi/4)*(6/39)**2#TODO consider angle
def motor_mass(t):
    return 5
body_mass=20

M=lambda t:body_mass+motor_mass(t)

Drag=lambda t,h,v,a:Area*AirDensity(h)*DrafCoeff(h,v,a)*v**2
#acceleration=-(A*rho*Cd*v^2+thrust)/m+g
Accel=lambda t,h,v,a:(Drag(t,h,v,a)*cos(a)+Thrust(t))/M(t)+g

body_center=2
motor_center=1
def cg(t):
    return (body_mass*body_center+motor_mass(t)*motor_center)/M(t)
def cp(extension):
    return 0.5
def Moment(M):
    return M*10
def extension(t):
    return 0

AngleAccel=lambda t,h,v,a:(cp(extension(t))-cg(t))*Drag(t,h,v,a)*sin(a)/Moment(M(t))

#FDS bs
def F(t,u):#the derivative of the state space
    return np.array([u[1],Accel(t,u[0],u[1],u[3]),AngleAccel(t,u[0],u[1],u[3]),u[2]])


def run_integrate_adaptive(dt):
    return integrate_adaptive([U0,U0],Heun,F,T,dt)


def run_scipy(dt):
    return scipyintegrate([U0,U0], scipy.integrate.RK45, F, T, dt)


def run(headless=False):
    #run code
    start=[]
    start+=[(time.perf_counter())]
    U,Time=run_integrate_adaptive(dt/1000)
    start+=[(time.perf_counter())]
    print(start[-1]-start[-2])
    U45,Time45=run_scipy(dt)
    start+=[(time.perf_counter())]
    print(start[-1]-start[-2])

    if not headless:
        # plotting
        plt.plot(Time45,U45[:,0],label="dt/1000")
        plt.plot(Time45,U45[:,1],label="dt/1000")
        plt.plot(Time,U[:,0],label="adaptive")
        plt.plot(Time,U[:,1],label="adaptive")
        plt.legend()
        plt.xlabel("time (s)")
        plt.ylabel("velocity(m/s)/Height(m)")
        plt.show()


if __name__ == '__main__':
    run()
