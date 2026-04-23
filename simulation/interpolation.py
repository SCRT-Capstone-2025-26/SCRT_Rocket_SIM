# TODO add some common sense tests to verify this function
from scipy.interpolate import make_interp_spline
from scipy.ndimage import convolve
from utilities import np_thrust_data, read_drag_data_np
from equations_n_constants import air_density, meters2feet, STD_THRUST_CSV

import numpy as np
import matplotlib.pyplot as plt


# returns the estimated amount of force at a specific point in time
def thrust_init(thrust_filepath=STD_THRUST_CSV):
    thrust_data = np_thrust_data(thrust_filepath)
    timesteps = thrust_data[:, 0]
    thrust = thrust_data[:, 1]
    return make_interp_spline(timesteps, thrust, k=5)


# finds all the drag data with the extension fixed extension
def find_drag_from_exti(drag_data, fixed_ext, exti=0, err=0.0001):
    good_data = [[] for j in range(len(drag_data))]
    for i in range(len(drag_data[exti])):
        if np.abs(drag_data[exti][i] - fixed_ext) < err:
            for j in range(len(good_data)):
                good_data[j] += [drag_data[j][i]]
    return good_data

#this takes in np arrays with multiple entries and concatenates them
def pointwise_concatenate_np(dragdata1,dragdata2):
    return np.array([np.array(list(dragdata1[i])+list(dragdata2[i])) for i in range(len(dragdata1))])


#removes duplicates from the first collumn of the data
def remove_repeats(sorted_drag_data):
    data=sorted_drag_data
    i=0
    print(len(data[0,:]))
    while i < len(data[0,:])-1:
        if data[0,i]==data[0,i+1]:
            data=pointwise_concatenate_np(data[:,:i+1], data[:,i+2:])
            print(data[0,i],data[0,i+1])
        i+=1
    return data



def drag_p_airden_fn(fixed_ext):
    drag_data = np.array(
        find_drag_from_exti(
            read_drag_data_np(
                col_names=["Extension", "Mach", "Drag of all", "Altitude"]
            ),
            fixed_ext,
        )[1:]
    )
    sort_indices = np.argsort(drag_data[0, :])
    drag_data = drag_data[:, sort_indices]
    drag_data=remove_repeats(drag_data)

    machsteps = drag_data[0, :]
    drag = drag_data[1, :] / air_density(meters2feet(drag_data[2, :]))
    return make_interp_spline(machsteps, drag, k=1)


def laplacian(z, dx):
    kernel = np.array([[ 0, -1,  0],
                       [-1,  4, -1],
                       [ 0, -1,  0]])
    
    # TODO choose better mode to relfect intended behavior
    return convolve(z, kernel, mode='nearest') * dx


if __name__ == "__main__":
    Exts = [0, 5, 15, 30]
    Cd = [drag_p_airden_fn(ext) for ext in Exts]
    X = np.linspace(0, 1, 1000)
    for j in range(4):
        plt.plot(X, np.array([Cd[j](x) for x in X]))
    plt.show()
