#TODO add some common sense tests to verify this function
import numpy as np
from scipy.interpolate import BSpline, make_interp_spline
import dataimport_utilities 
from dataimport_utilities import np_thrust_data
from eng_to_csv import eng_to_csv
import os


#returns the estimated amount of force at a specific point in time
def thrust_init():
#TODO: make this file a non test file.
    directory_name = "../data/runs/20251114_191130/input/"
    try:
        os.mkdir(directory_name)
    except FileExistsError:
        pass
    src_filepath = "../sample_datasets/AeroTech_N2000W.eng"
    dst_filepath = "../data/runs/20251114_191130/input/thrust_motor.csv"
    spec_filepath = "../data/runs/20251114_191130/input/motor_spec.csv"
    eng_to_csv(src_filepath, dst_filepath, spec_filepath)

    Thrust_data=np_thrust_data("../data/runs/20251114_191130/input/thrust_motor.csv")
    timesteps=Thrust_data[:,0]
    Thrust=Thrust_data[:,1]
    return make_interp_spline(timesteps, Thrust,k=5)


if __name__ == "__main__":
    thrust=thrust_init()
    print(.15,thrust(.15))
