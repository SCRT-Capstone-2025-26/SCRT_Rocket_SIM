import matplotlib.pyplot as plt
import time
import numpy as np
from math import *
from utilities import *


## TODO please make look good
def scipyintegrate(u0,scheme,f,T,dt):
    print(u0,'u0')
    u=u0
    t=[i*dt for i in range(len(u))]
    solution=scheme(lambda t0,u0:f(t0,u0) ,t[-1],u[-1],T)   
    while u[-1][0]>0:
        t+=[t[-1]+dt]
        print(u,'u')
        u+=[scheme(f,t[-1],dt,u)]
    return np.array(u),np.array(t)







#Finite Difference Scheme(FDS) integrator
def integrate(u0, scheme, f, T, dt):
    u = u0
    print(u)
    N=ceil(T/dt)
    for n in range(N):
        u+=[scheme(f,dt*n,dt,u)]
        if u[-1][0]<0:
            return u
    return u

def double_step(scheme):
    return lambda f,t,dt,u:scheme(f,t+dt/2,dt/2,u+[scheme(f,t,dt/2,u)])

def integrate_adaptive(u0, scheme, f, T, dt,batch=1,scheme2=None,tol=None):
    if tol==None:
        tol=dt/1000
    if scheme2==None:
        scheme2=double_step(scheme)
    u = [u0[0] for i in range(batch+1)]
    t = [0 for i in range(batch+1)]
    print(u)
    while t[-1]<T:
        err=np.linalg.norm(scheme(f,t[-1],dt,u)-scheme2(f,t[-1],dt,u))
        #err/=np.linalg.norm(scheme(f,t[-1],dt,u))
        if err>tol:
            #print(err,dt,t[-1])
            u=u[:-batch]
            t=t[:-batch]
            dt/=4.0
        else:
            dt*=1.1
        for i in range(batch):
            t+=[t[-1]+dt]
            u+=[scheme(f,t[-1],dt,u)]
            if u[-1][0]<0 or t[-1]>T:
                return np.array(u),np.array(t)
    return np.array(u),np.array(t)
