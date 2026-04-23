import os
import csv
import numpy as np
from scipy.interpolate import make_interp_spline

_base_path = os.path.join(os.path.dirname(__file__))

# Physical Constants

GOAL_HEIGHT_METERS = 3048

# Choose gravity variables by launch location

# ISO standard 80000 for gravity
# GRAVITY = -9.80665
# Mean radius of earth in km
# LATITUDE = 0
# radius_r = 6371.00877

# Local gravity predicted at OROC Brothers Oregon
# 43.800050, -120.650027. 1380.09 meters
# Local gravity at OROC launch site
LATITUDE = 43.800050
GRAVITY = -9.80085
# Radius of earth in km at OROC Launch site latitude at sea level
radius_r = 6367.937

# Local gravity predicted at IREC Launch Site, Reeves County Texas
# 31.031080, -103.549876. 890.45 meters
# LATITUDE = 31.031080
# Local gravity at IREC launch site
# GRAVITY = -9.79131
# Radius of earth in km at IREC launch site
# radius_r = 6372.489

# Based on Somigliana equation
def _local_gravity_at_lat(lat):
    return -9.7803253359*((1+(0.001931851353*(np.sin(lat*(np.pi/180))**2)))/
                         np.sqrt(1-(0.00669437999013*(np.sin(lat*(np.pi/180))**2))))

# Calculates gravity given a specific height
def gravity_at_alt(h):
    
    return _local_gravity_at_lat(LATITUDE) * ((radius_r/(radius_r+(h/1000)))**2)

BODY_MASS = 34.0194

# Should be highest useful precision
MACH_TO_METERS_SEC = 340.29

METERS_TO_FEET = 3.28084

FEET_TO_METERS = 0.3048

# Current motor burnout at 4.455 seconds
STD_THRUST_CSV = os.path.join(_base_path, "..", "data", "motor_data", "N3300R", "N3300R_thrust.csv")

# Thrust burnout of the current motor in seconds
THRUST_BURNOUT = 4.5

# returns the estimated amount of force at a specific point in time
def _thrust_init(thrust_filepath=STD_THRUST_CSV):
    thrust_data = []
    with open(STD_THRUST_CSV, "r") as file:
        for line in csv.reader(file):
            thrust_data += [line]
    thrust_data = np.array([[float(x) for x in y] for y in thrust_data[1:]])
    timesteps = thrust_data[:, 0]
    thrust = thrust_data[:, 1]
    return make_interp_spline(timesteps, thrust, k=5)

# thrust_fn = None # turned to _thrust_init(STD_THRUST_CSV) when thrust(t) called
thrust_fn = _thrust_init(STD_THRUST_CSV)


EXTS = [i*25./15. for i in range(16)]

STD_DRAG_CSV_LIST = [
        "data/drag_data/Bababooey_Fulldata.csv",
        "data/drag_data/DataCollSweep1_Fulldata_042026.csv"
    ]
# Bababooey_Fulldata.csv
# DataCollSweep1_Fulldata_042026.csv
# FullScale_NoCameraTransonicSweep2_041726.csv
# FullScaleV9_NoCameraTransonicSweep1_041626.csv
# FullScaleV9_NoCameraTransonicSweep1_041826.csv
# FullScaleV9_NoCameraTransonicSweep1_042026.csv

# _drag_data_path = os.path.join(_base_path, "..", "data", "drag_data")
# STD_DRAG_CSV_LIST = [
#         os.path.join(_drag_data_path, "Bababooey_Fulldata.csv"),
#         os.path.join(_drag_data_path, "DataCollSweep1_Fulldata_042026.csv"),
#         # os.path.join(_drag_data_path, "FullScale_NoCameraTransonicSweep2_041726.csv"),
#         os.path.join(_drag_data_path, "FullScaleV9_NoCameraTransonicSweep1_041626.csv"),
#         # os.path.join(_drag_data_path, "FullScaleV9_NoCameraTransonicSweep1_041826.csv"),
#         # os.path.join(_drag_data_path, "FullScaleV9_NoCameraTransonicSweep1_042026.csv"),
#     ]

STD_DRAG_COL_NAMES = ["Extension", "Mach", "Drag Coeff"]

# Equations

# TODO consider local conditions
def air_density(h):
    return 1.2 * 0.99988**h


def mach2v(v):
    return MACH_TO_METERS_SEC * v


def v2mach(mach):
    return mach / MACH_TO_METERS_SEC


def thrust(t):
    # return 3000 if t < 4 else 0
    if t < THRUST_BURNOUT+1:
        return max(thrust_fn(t), 0)
    else:
        # Shouldn't be called, but just in case
        return 0


def motor_mass(t):
    return 10


def total_mass(t):
    return BODY_MASS + motor_mass(t)

# Note, needs to operate on lists as well
def meters2feet(m):
    return m * METERS_TO_FEET
