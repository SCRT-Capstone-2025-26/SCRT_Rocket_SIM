import matplotlib.pyplot as plt
import time
import numpy as np
from math import sin,cos,pi
from utilities import sign
from integration import scipyintegrate, integrate_adaptive
# from data_utilities.dataimport_utilities import np_thrust_data,read_drag_data_np

from data_utilities.interpolation import Cd_init
from FDS import Heun
import scipy






#physical constants



def AirDensity(h):
    return 1.2*.99988**h
def Thrust(t):
    return 3000 if t<4 else 0
g=-10
body_mass=15#TODO consider change in mass
def motor_mass(t):
    return 10

def M(t):
    return body_mass+motor_mass(t)

Exts=[0,5,15,30]
Cd=[Cd_init(ext) for ext in Exts]
def Drag(h,v,exti):
    return AirDensity(h)*Cd[exti](v/343)
#acceleration=-(A*rho*Cd*v^2+thrust)/m+g
def Accel(t,h,v,exti):
    return (Drag(h,v,exti)+Thrust(t))/M(t)+g

#FDS bs
def Fext(t,u,exti):#the derivative of the state space
    return np.array([u[1],Accel(t,u[0],u[1],exti)])


def run_integrate_adaptive(dt,exti=0):
    T=200
    dt=.05
    U0=np.array([0,0])#u[0]=height u[1]=velocity
    def F(t,u):
       return Fext(t,u,exti) 
    return integrate_adaptive([U0,U0],Heun,F,T,dt)


def run_scipy(dt,exti=0):
    T=200
    dt=.05
    U0=np.array([0,0])#u[0]=height u[1]=velocity
    def F(t,u):
       return Fext(t,u,exti) 
    return scipyintegrate([U0,U0], scipy.integrate.RK45, F, T, dt)


def run(headless=False,exti=0):
#initial conditions
    T=200
    dt=.05
    U0=np.array([0,0])#u[0]=height u[1]=velocity
    #run code
    def F(t,u):
       return Fext(t,u,exti) 
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
