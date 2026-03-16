import numpy as np
# Physical Constants

# TODO get local gravity of launch site
# Currently set as ISO standard 80000 
GRAVITY = -9.80665

BODY_MASS = 15

# TODO add more decimal points
MACH_TO_METERS_SEC =343.0

# Equations

def air_density(h):
    return 1.2 * 0.99988**h


def mach2v(v):
    return MACH_TO_METERS_SEC * np.array(v)


def thrust(t):
    return 3000 if t < 4 else 0


def motor_mass(t):
    return 10


def total_mass(t):
    return BODY_MASS + motor_mass(t)