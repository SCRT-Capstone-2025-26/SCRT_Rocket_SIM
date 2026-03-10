import matplotlib.pyplot as plt
import time
from numpy import sin,cos,pi
import numpy as np
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
def Drag(h,v,theta,exti,t):
    if t<4 or theta*180/pi>20:
        exti=0
    global Dragdata
    Dragdata+=[AirDensity(h)*Cd[exti](v/343)]
    return AirDensity(h)*Cd[exti](v/343)
#acceleration=-(A*rho*Cd*v^2+thrust)/m+g
def Accel(t,u,exti):
    h,v,theta=u
    return (-Drag(h,v,theta,exti,t)+Thrust(t))/M(t)+g

#FDS bs
def Fext(t,u,exti):#the derivative of the state space
    Acceleration=Accel(t,u,exti)
    return np.array([u[1]*cos(u[2]),    #Change in Height
                     Acceleration,      #Change in Velocity 
        -g*sin(u[2])/(u[1]+Acceleration)#Change in Zenith 
                                   ])



def run_scipy(dt,exti=3,t0=0,
            U0=np.array([0,0])#u[0]=height u[1]=velocity
              ):
    T=200
    dt=.05
    def F(t,u):
       return Fext(t,u,exti) 
    return scipyintegrate(U0, scipy.integrate.RK45, F, T, dt,t0=t0)

def apogee(exti,U0,T,t0,dt=.0005):
    def F(t,u):
       return Fext(t,u,exti) 
    U,Time=run_scipy(dt,exti=exti,t0=t0,U0=U0)
    return np.max(U[:,0])

def run(headless=False,exti=3,U0=np.array([0,0,1/15]),t0=4):
#initial conditions
    T=200
    dt=.05
    #run code
    def F(t,u):
       return Fext(t,u,exti) 
    U45,Time45=run_scipy(dt,U0=U0,exti=exti,t0=t0)

    if not headless:
        # plotting
        plt.plot(Time45,U45[:,0],label="scipyh,exti="+str(exti))
        plt.plot(Time45,U45[:,1],label="scipyv,exti="+str(exti))
        plt.plot(Time45,U45[:,2]*1000,label="scipytheta,exti="+str(exti))
        plt.plot(Time45,[10000/3.3 for t in Time45],label="goalheight")
        
        # plt.plot(Time,U[:,0],label="Height")
        # plt.plot(Time,U[:,1],label="Velocity")
        plt.legend()
        plt.xlabel("time (s)")
        plt.ylabel("velocity(m/s)/Height(m)")
        # plt.show()
        # plt.plot(np.array(Dragdata),label="Dragdata")
        # plt.show()

def mach2v(V):
    #TODO add more decimal points
    return [343.*v for v in V]

if __name__ == '__main__':
    if False:
        run(exti=3,U0=np.array([0,0,20*pi/180]),t0=0)
        run(exti=3,U0=np.array([0,0,0]),t0=0)
        plt.show()
    elif False:
        run(exti=3,U0=np.array([0,0,5*pi/180]),t0=0)
        run(exti=0,U0=np.array([0,0,5*pi/180]),t0=0)
        plt.show()
    else:
        heights=[200*i+800 for i in range(11)]
        angles=[pi/180*i**2 for i in range(4)]
        Tol=0.001 
        print("Angles:",angles)
        print("Heights:",heights)
        print("Exts:",Exts)
        lookup=[[[] for ai in angles] for hi in heights]
        for hi in range(len(heights)):
            for ai in range(len(angles)):
                OptimalVels=[]
                for exti in range(len(Exts)):
                    va=0
                    vb=1.1
                    U0=np.array([heights[hi],mach2v([va])[0],angles[ai]])
                    apogee_a=abs(apogee(exti,U0,200,t0=4)-10000/3.3) 
                    U0=np.array([heights[hi],mach2v([vb])[0],angles[ai]])
                    apogee_b=abs(apogee(exti,U0,200,t0=4)-10000/3.3) 
                    while(vb-va>Tol):
                        mid_v=(va+vb)/2
                        # print(mid_v,va,vb)
                        U0=np.array([heights[hi],mach2v([mid_v])[0],angles[ai]])
                        apogee_mid=abs(apogee(exti,U0,200,t0=4)-10000/3.3) 
                        if apogee_a>apogee_b:
                            # print('a has more error')
                            va=mid_v
                            apogee_a=apogee_mid
                        else:
                            # print('b has more error')
                            vb=mid_v
                            apogee_b=apogee_mid
                    OptimalVels+=[mid_v]
                print(f"Height:{heights[hi]} Angle:{angles[ai]:.3f} %vel diff:{(max(OptimalVels)-min(OptimalVels))/min(OptimalVels):.3f}")
                lookup[hi][ai]+=[OptimalVels]
        print(np.array(lookup))
        np.save('lookup.npy',lookup)
        print("Lookup:")
