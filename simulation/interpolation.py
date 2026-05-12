from scipy.interpolate import RBFInterpolator
import numpy as np
import matplotlib.pyplot as plt

from equations_n_constants import air_density, mach2v, feet2meters
from utilities import read_drag_data_np

ext, mach, all_drag, alt_ft = np.array(read_drag_data_np(col_names=["Extension", "Mach", "Drag of all", "Altitude"]))

vel = mach2v(mach)
drag_p_airden = all_drag / air_density(feet2meters(alt_ft))

# This is a function (or callable)
# It's args are extension and velocity
data = np.stack((ext, vel), axis=1)
drag_p_airden_interp = RBFInterpolator(data, drag_p_airden, smoothing=10)

# The vectorize is to make it run in the plot code
@np.vectorize
def get_drag_p_airden(ext, vel):
    # I don't know why this is the shape the interp wants
    return drag_p_airden_interp(((ext, vel),))[0]


if __name__ == '__main__':
    X = np.linspace(-5, 30, 35 * 3)
    Y = np.linspace(-5, 400, 405 * 3)
    X, Y = np.meshgrid(X, Y)
    Z = get_drag_p_airden(X, Y)

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d', computed_zorder=False)

    surf = ax.plot_surface(X, Y, Z, cmap='magma', zorder=1)
    ax.scatter(ext, vel, drag_p_airden, s=1, color='lime', zorder=2)

    ax.set_xlabel('Extension')
    ax.set_ylabel('Velocity')
    ax.set_zlabel('Drag / Air Density')
    ax.set_title('Drag')

    fig.colorbar(surf, ax=ax)
    plt.show()

