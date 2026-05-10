from scipy.interpolate import LinearNDInterpolator
import numpy as np
import matplotlib.pyplot as plt

from equations_n_constants import air_density, mach2v
from utilities import read_drag_data_np

ext, mach, all_drag, alt = np.array(read_drag_data_np(col_names=["Extension", "Mach", "Drag of all", "Altitude"]))

vel = mach2v(mach)
drag_p_airden = all_drag / air_density(alt)

# This is a function (or callable)
# It's args are extension and velocity
drag_p_airden_interp = LinearNDInterpolator(np.stack((ext, vel), axis=1), drag_p_airden)

min_vel = np.min(vel)
min_drag_p_airden = np.min(drag_p_airden)
max_vel = np.max(vel)
max_drag_p_airden = np.max(drag_p_airden)

# ext must be a in the range of exts
@np.vectorize
def get_drag_p_airden(ext, vel):
    # If the velocity is small or big enough to where we don't have data I just do this
    #  there is probably a better way maybe a linear interpolation would be better
    if vel < min_vel:
        return min_drag_p_airden
    if vel > max_vel:
        return max_drag_p_airden

    return drag_p_airden_interp(ext, vel)


if __name__ == '__main__':
    X = np.linspace(-5, 30, 200)
    Y = np.linspace(-5, 400, 1000)
    X, Y = np.meshgrid(X, Y)
    Z = get_drag_p_airden(X, Y)
    plt.pcolormesh(X, Y, Z, shading='auto')
    plt.legend()
    plt.colorbar()
    plt.show()

