import matplotlib.pyplot as plt
import time
import numpy as np
from math import *
from utilities import *

def Butcher_Tableaux(a,c,b,N=20,Err=.00001):
    k=[0 for i in range(len(a))]
    csum=[0 for i in range(len(a))]
    print(len(a),"len(a)")
    for i in range(len(a)):
        print(i)
        if sum(a[i][i+1:])!=0 :
            raise Exception("tableaux a has values above the diagonal")
        print([[j,a[i][j]] for j in range(i)])
        csum[i]=lambda f,t,dt,u,asum=csum[i-1]:sum([a[i][j]*k[j](f,t,dt,u,asum) for j in range(i)])
        if a[i][i]!=0:#check if implicit
            k[i]=lambda f,t,dt,u,asum=csum[i]: iterate(lambda un:f(t+c[i]*dt,u[-1]
                +dt*(asum(f,t+c[i]*dt,dt,u)+a[i][i]*un)),f(t,u[-1]))
        else:#it's explicit :)
            k[i]=lambda f,t,dt,u,asum=csum[i]: f(t+c[i]*dt,u[-1]+dt*asum(f,t,dt,u))
    return lambda f,t,dt,u:(u[-1]
            +dt*sum([b[j]*k[j](f,t,dt,u) for j in range(len(b))]))

def Butcher_Table(a,b,c):
    def k (f,t,dt,u,i):
        if i>=0:
            asum=np.array([0.,0.])
            for j in range(i):
                print(a[i][j],"aij")
                asum+=a[i][j]*k(f,t,dt,u,j)
            print(asum,"asum")
            if a[i][i]!=0:
                return iterate(lambda un:f(t+c[i]*dt,u[-1]
                    +dt*(asum+a[i][i]*un)),f(t+c[i]*dt,u[-1]))
            else:
                return f(t+c[i],u[-1]+dt*asum)
        else:
            return f(t+c[i]*dt,u[-1])
    return lambda f,t,dt,u:(u[-1]
            +dt*sum([b[j]*k(f,t,dt,u,j) for j in range(len(b))]))

def Butcher_Table2(a,b,c):
    def calc(f,t,dt,u):
        k=[]
        for i in range(len(c)):
            asum=np.array([0.,0.])
            for j in range(i):
                asum+=a[i][j]*k[j]
            k+=[f(t+c[i]*dt,u[-1]+asum*dt)]
            if a[i][i]!=0:
                k[-1]=iterate(lambda un:f(t+c[i]*dt,u[-1]
                        +dt*(asum+a[i][i]*un)),k[-1])
        bsum=np.array([0.,0.])
        for j in range(len(b)):
            bsum+=b[j]*k[j]
        return u[-1]+dt*bsum
    return calc

