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
# Mean radius of earth in m
# LATITUDE = 0
# radius_r = 6371.00877 * 1000

# Local gravity predicted at OROC Brothers Oregon
# 43.800050, -120.650027. 1380.09 meters
# Local gravity at OROC launch site
LATITUDE = 43.800050
GRAVITY = -9.80085
GROUND_HEIGHT = 1380.09
# Radius of earth in m at OROC Launch site latitude at sea level
radius_r = 6367.937 * 1000

# Local gravity predicted at IREC Launch Site, Reeves County Texas
# 31.031080, -103.549876. 890.45 meters
# LATITUDE = 31.031080
# Local gravity at IREC launch site
# GRAVITY = -9.79131
# Radius of earth in m at IREC launch site
# radius_r = 6372.489 * 1000

# Based on Somigliana equation
def _local_gravity_at_lat(lat):
    return -9.7803253359*((1+(0.001931851353*(np.sin(lat*(np.pi/180))**2)))/
                         np.sqrt(1-(0.00669437999013*(np.sin(lat*(np.pi/180))**2))))

# Calculates gravity given a specific height
def gravity_at_alt(h):
    # Sanity check to ensure height is given in meters
    if h > 8000:
        raise ValueError("Height beyond expected value. Height should be in meters.")
    return _local_gravity_at_lat(LATITUDE) * ((radius_r/(radius_r+h+GROUND_HEIGHT))**2)


# Burnable propellant mass
PROP_MASS = 7.512
BODY_MASS = 34.0194-PROP_MASS

# Based on settings used in the sim because it varies by conditions
MACH_TO_METERS_SEC = 335.4162

METERS_TO_FEET = 3.28084

FEET_TO_METERS = 0.3048

STD_THRUST_CSV = os.path.join(_base_path, "data", "motor_data", "N3300R", "N3300R_thrust.csv")

# Thrust burnout of the current motor in seconds
# Current motor burnout at 4.455 to 4.519 seconds
THRUST_BURNOUT = 4.52

# The height below which the angle can't change
# It is made up because I don't care
RAIL_HEIGHT = 30


# returns the estimated amount of force at a specific point in time
def _thrust_init(thrust_filepath=STD_THRUST_CSV):
    thrust_data = []
    with open(thrust_filepath, "r") as file:
        for line in csv.reader(file):
            thrust_data += [line]
    thrust_data = np.array([[float(x) for x in y] for y in thrust_data[1:]])
    timesteps = thrust_data[:, 0]
    thrust = thrust_data[:, 1]
    return make_interp_spline(timesteps, thrust, k=5)


# thrust_fn = None # turned to _thrust_init(STD_THRUST_CSV) when thrust(t) called
thrust_fn = _thrust_init(STD_THRUST_CSV)

EXTS = [i*25./15. for i in range(16)]

_drag_data_path = os.path.join(_base_path, "data", "drag_data")
STD_DRAG_CSV_LIST = [
        os.path.join(_drag_data_path, "Bababooey_Fulldata.csv"),
        os.path.join(_drag_data_path, "DataCollSweep1_Fulldata_042026.csv"),
    ]


# _drag_data_path = os.path.join(_base_path, "..", "data", "drag_data")
# STD_DRAG_CSV_LIST = [
#         os.path.join(_drag_data_path, "Bababooey_Fulldata.csv"),
#         os.path.join(_drag_data_path, "DataCollSweep1_Fulldata_042026.csv"),
#         # os.path.join(_drag_data_path, "FullScale_NoCameraTransonicSweep2_041726.csv"),
#         os.path.join(_drag_data_path, "FullScaleV9_NoCameraTransonicSweep1_041626.csv"),
#         # os.path.join(_drag_data_path, "FullScaleV9_NoCameraTransonicSweep1_041826.csv"),
#         # os.path.join(_drag_data_path, "FullScaleV9_NoCameraTransonicSweep1_042026.csv"),
#     ]

STD_DRAG_COL_NAMES = ("Extension", "Mach", "Drag Coeff")

# Equations


# Low humidity, so use standard model that assumes dry air
# Takes in h in meters above ground level. Uses a set ground level temperature and pressure 
# WILL BE VERY WRONG IF HEIGHT ABOVE SEA LEVEL IS PASSED FOR h!
#   (probably some, but not much difference for different days and launch sites)
# Note this is excessive detail. If it's too costly time wise, we should revert
# to: return 1.2 * 0.99988**(h+GROUND_HEIGHT)
def air_density(h):
    p_0 = 1.05365 # kg/m^3, ground level air density (currently for 1380.09m & 51deg F)
    t_0 = 283.706 # K,  ground level air temperature (std is 273.15)
    t_lapse = 0.00649 # K/m, usual change in temperature per meter
    g = -GRAVITY # m/s^2 force of gravity (positive)
    m = 0.0289652 # kg/mol, molar mass of dry air
    r = 8.31446261815342 # J/(mol*K), Gas constant 
    p = p_0 * ((1 - (t_lapse * h)/(t_0))**(((g*m)/(r*t_lapse))-1))
    return p


def mach2v(v):
    return MACH_TO_METERS_SEC * v


def v2mach(mach):
    return mach / MACH_TO_METERS_SEC


def thrust(t):
    if t < THRUST_BURNOUT:
        return max(thrust_fn(t), 0)
    else:
        # Shouldn't be called, but just in case
        return 0


def prop_mass(t):
    if t <= THRUST_BURNOUT:
        # Assumes linear burning, which almost but not completely correct
        return PROP_MASS*(1-(t/THRUST_BURNOUT))
    else:
        return 0
    

def total_mass(t):
    return BODY_MASS + prop_mass(t)


# Note, needs to operate on lists as well
def meters2feet(m):
    return m * METERS_TO_FEET

def feet2meters(m):
    return m * FEET_TO_METERS

