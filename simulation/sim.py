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

##################CD is actually just drag rn

Dragdata=[]


#physical constants



def AirDensity(h):
    return 1.2*.99988**h
def Thrust(t):
    return 3000 if t<4 else 0
g=-10
body_mass=15
def motor_mass(t):
    return 10

def M(t):
    return body_mass+motor_mass(t)

Exts=[0,5,15,30]
Cd=[Cd_init(ext) for ext in Exts]
def Drag(h,v,exti,t):
    if t<4:
        exti=0
    global Dragdata
    Dragdata+=[AirDensity(h)*Cd[exti](v/343)]
    return AirDensity(h)*Cd[exti](v/343)
#acceleration=-(A*rho*Cd*v^2+thrust)/m+g
def Accel(t,h,v,exti):
    return (-Drag(h,v,exti,t)+Thrust(t))/M(t)+g

#FDS bs
def Fext(t,u,exti):#the derivative of the state space
    return np.array([u[1],Accel(t,u[0],u[1],exti)])


def run_integrate_adaptive(dt,exti=3,t0=0):
    T=200
    dt=.05
    U0=np.array([0,0])#u[0]=height u[1]=velocity
    def F(t,u):
       return Fext(t,u,exti) 
    return integrate_adaptive([U0,U0],Heun,F,T,dt,t0=t0)


def run_scipy(dt,exti=3):
    T=200
    dt=.05
    U0=np.array([0,0])#u[0]=height u[1]=velocity
    def F(t,u):
       return Fext(t,u,exti) 
    return scipyintegrate([U0,U0], scipy.integrate.RK45, F, T, dt)


def apogee(exti,U0,T,t0,dt=.05):
    T=200
    dt=.05
    U0=np.array([0,0])#u[0]=height u[1]=velocity
    #run code
    def F(t,u):
       return Fext(t,u,exti) 
    U,Time=run_integrate_adaptive(dt/1000,exti=exti,t0=t0)
    return np.max(U[:,0])

def run(headless=False,exti=3):
#initial conditions
    T=200
    dt=.05
    U0=np.array([0,0])#u[0]=height u[1]=velocity
    #run code
    def F(t,u):
       return Fext(t,u,exti) 
    U45,Time45=run_scipy(dt,exti=exti)

    if not headless:
        # plotting
        plt.plot(Time45,U45[:,0],label="scipyh")
        plt.plot(Time45,U45[:,1],label="scipyv")
        # plt.plot(Time,U[:,0],label="Height")
        # plt.plot(Time,U[:,1],label="Velocity")
        plt.legend()
        plt.xlabel("time (s)")
        plt.ylabel("velocity(m/s)/Height(m)")
        # plt.show()
        # plt.plot(np.array(Dragdata),label="Dragdata")
        # plt.show()


if __name__ == '__main__':
    run(exti=0)
    run(exti=1)
    run(exti=2)
    run(exti=3)
    plt.show()
