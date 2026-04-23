# Physical Constants

GOAL_HEIGHT_METERS = 3048

# TODO get local gravity of launch site
# Currently set as ISO standard 80000 
GRAVITY = -9.80665

BODY_MASS = 15

# TODO add more decimal points
MACH_TO_METERS_SEC =343.0

METERS_TO_FEET = 3.28084

FEET_TO_METERS = 0.3048

STD_DRAG_CSV_LIST = [
        "sample_datasets/SupSonicSweep2_012826_data.csv",
        "sample_datasets/SupSonicSweep4_013026_FullData.csv",
        "sample_datasets/SupSonicSweep5_013126_FullData.csv",
        "sample_datasets/SupSonicSweep2_BEAVS_012926_FullData.csv",
    ]

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
    return 3000 if t < 4 else 0


def motor_mass(t):
    return 10


def total_mass(t):
    return BODY_MASS + motor_mass(t)

# Note, needs to operate on lists as well
def meters2feet(m):
    return m * METERS_TO_FEET