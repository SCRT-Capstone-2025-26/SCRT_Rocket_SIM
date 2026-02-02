#TODO add some common sense tests to verify this function
from scipy.interpolate import  make_interp_spline
from dataimport_utilities import np_thrust_data,read_drag_data_np
from eng_to_csv import eng_to_csv
import os

import numpy as np
import matplotlib.pyplot as plt
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


def pointwise_interp():
# #TODO: use something that is actually Cd data
#     directory_name = "../data/runs/20251114_191130/input/"
#     try:
#         os.mkdir(directory_name)
#     except FileExistsError:
#         pass
#     src_filepath = "../sample_datasets/AeroTech_N2000W.eng"
#     dst_filepath = "../data/runs/20251114_191130/input/thrust_motor.csv"
#     spec_filepath = "../data/runs/20251114_191130/input/motor_spec.csv"
#     eng_to_csv(src_filepath, dst_filepath, spec_filepath)
#
#     Thrust_data=np_thrust_data("../data/runs/20251114_191130/input/thrust_motor.csv")
#     timesteps=Thrust_data[:,0]
#     Thrust=Thrust_data[:,1]
#     data=[[[Thrust[i]*Thrust[j],timesteps[i],timesteps[j]] for j in range(len(Thrust))] for i in range(len(Thrust))]
#     data=np.array(data)
#     #TODO replace everything above with real data
    
    [ext,mach,Cd]=read_drag_data_np()
    data=[[Cd[i],ext[i],mach[i]] for i in range(len(Cd))]
    # data=[[1,1,1],[2,2,2],[3,1,2],[4,2,3],[5,1,3],[6,2,1]]
    data=sorted(data, key=lambda tup: tup[1])
    data=sorted(data, key=lambda tup: tup[2])
    length=1
    while data[length][2]==data[0][2]:
        length+=1
    data=np.array(data).reshape((len(data)//length,length,3))
    print(data,length)
    # print(data[:,0,1])

    #CAUTION: DOES NOT WORK:
    firstinterps=[make_interp_spline(data[i,:,2], data[i,:,0],k=5) for i in range(len(data))]
    def secondinterp(x,y):
        xsteps=data[:,0,1]
        z=[f(y) for f in firstinterps]
        return make_interp_spline(xsteps,z)(x)
    return secondinterp
def laplacian(Z,dx):
    return np.array([[(4*Z[i+1][j+1]-Z[i+2][j+1]-Z[i+1][j+2]-Z[i][j+1]-Z[i+1][j])*dx for j in range(len(Z[0])-2)] for i in range(len(Z)-2)])



if __name__ == "__main__":
    thrust=thrust_init()
    thrust2=pointwise_interp()
    N=200
    a,b=0,7
    x = np.linspace(a, b, N)
    y = np.linspace(a, b, N)
    X, Y = np.meshgrid(x, y)
    Z =np.array([[thrust2(X[i][j],Y[i][j]) for j in range(len(X[0]))] for i in range(len(X))])
    x = np.linspace(a, b, N-2)
    y = np.linspace(a, b, N-2)
    X2, Y2 = np.meshgrid(x, y)
    Z2 =laplacian(Z,(b-a)/N)
    fig = plt.figure(figsize=(10, 8))
    ax = plt.axes(projection='3d')
    ax.plot_surface(X, Y, Z, cmap='cool', alpha=0.8)
    # ax.plot_surface(X, Y, Z2, cmap='cool', alpha=0.8)

    ax.set_title('Thrust^2')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')

    plt.show()

    fig = plt.figure(figsize=(10, 8))
    ax = plt.axes(projection='3d')
    ax.plot_surface(X2, Y2, Z2, cmap='cool', alpha=0.8)

    ax.set_title('laplacian')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')

  plt.show()
    thrust=thrust_init()
    print(.15,thrust(.15))
