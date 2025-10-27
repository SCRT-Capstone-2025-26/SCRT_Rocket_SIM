import matplotlib.pyplot as plt
import time
import numpy as np
from math import *
from utilities import *
from Butcher_Table import *
from scipy import integrate as inte




def Heun(f,t,dt,u):#forward euler FDS
    return u[-1]+dt*(f(t,u[-1])+f(t+dt,u[-1]+dt*f(t,u[-1])))/2
def FE(f,t,dt,u):#forward euler FDS
    return u[-1]+dt*f(t,u[-1])
def BE(f,t,dt,u):#Backward Euler
    return iterate(lambda un:u[-1]+dt*f(t+dt,un),u[-1])
def Trap(f,t,dt,u):#trapezoidal FDS
    return iterate(lambda un:u[-1]+dt*(f(t+dt,un)+f(t,u[-1]))/2,u[-1])
RK4=Butcher_Table2([[0   , 0,0,0],\
                   [ 1/3, 0,0,0],\
                   [-1/3, 1,0,0],\
                   [1   ,-1,1,0]],[0,1/3,2/3,1],[1/8,3/8,3/8,1/8])
RK1=Butcher_Table2([[1]],[1],[1])
RKtrap=Butcher_Table2([[0  ,0  ],\
                      [1/2,1/2]],[0,1],[0.5,0.5])
RKheun=Butcher_Table2([[0  ,0  ],\
                      [1,0]],[0,1],[0.5,0.5])
