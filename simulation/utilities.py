import numpy as np

# convenient functions
""" Returns the sign of a numeric value
Input: numeric value
Output: -1, 1, or 0 depending on the sign of the value
"""


def sign(v):
    return abs(v) / v if v != 0 else 0


def npmap(arr, func):
    return np.array(list(map(func, list(arr))))


# given a function itertate f such that f(f(f(...))) converges find that
def iterate(f, guess, iter=20, err=0.00001, verbose=False):
    i = 0
    fguess = f(guess)
    while i < iter and np.linalg.norm(fguess - guess) > err:
        guess = fguess
        fguess = f(guess)
        i += 1
    if i > 1 and verbose:
        print("iteration: " + str(i))
    return guess


def implicit(iterable):
    return lambda f, t, dt, u: iterate(iterable(f, t, dt, u), u[-1])
