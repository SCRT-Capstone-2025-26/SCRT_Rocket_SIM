import matplotlib.pyplot as plt
import time
import numpy as np
from math import *

#convenient functions
sign=lambda v:abs(v)/v if v!=0 else 0
def npmap(l, f):
    return np.array(list(map(f, list(l))))

#given a function itertate f such that f(f(f(...))) converges find that 
def iterate(f,guess,iter=20,err=0.00001):
    i=0
    fguess=f(guess)
    while(i<iter and np.linalg.norm(fguess-guess)>err):
        guess=fguess
        fguess=f(guess)
        i+=1
    if i>1:
        print(i,"iters")
    return guess
def implicit(iterable):
    return lambda f,t,dt,u: iterate(iterable(f,t,dt,u),u[-1])

