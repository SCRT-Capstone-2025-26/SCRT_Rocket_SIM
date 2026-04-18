import matplotlib.pyplot as plt

from numpy import sin, cos, pi
import numpy as np
from integration import scipyintegrate
# from data_utilities.dataimport_utilities import np_thrust_data,read_drag_data_np

from data_utilities.interpolation import drag_p_airden_fn
from data_utilities.equations_n_constants import air_density, thrust, total_mass, mach2v, v2mach, GRAVITY, GOAL_HEIGHT_METERS
import scipy

import os

##################CD is actually just drag rn

# TODO make class or something to get rid of usign a global object
Dragdata = []


# physical constants and simple equations imported from data_utilities.equations_n_constants



Exts = [0, 5, 15, 30]
drag_p_airden = [drag_p_airden_fn(ext) for ext in Exts]


def drag(h, v, theta, exti, t):
    if t < 4 or theta * 180 / pi > 20:
        exti = 0
    # TODO make cleaner, perhaps a class
    next_dragdata = air_density(h) * drag_p_airden[exti](v2mach(v))
    global Dragdata
    Dragdata += [next_dragdata]
    return next_dragdata


# acceleration=-(A*rho*Cd*v^2+thrust)/m+g
# TODO add derivation documentation
def accel(t, u, exti):
    h, v, theta = u
    # TODO np.cos(theta)*GRAVITY is a good approximation needs to be fixed
    return (-drag(h, v, theta, exti, t) + thrust(t)) / total_mass(t) + np.cos(theta)*GRAVITY


# FDS bs
# the derivative of the state space
# forcing function f for finite difference scheme accountign for extention
def f_w_ext(t, u, exti): 
    acceleration = accel(t, u, exti)
    return np.array(
        [
            u[1] * cos(u[2]),  # Change in Height
            acceleration,  # Change in Velocity
            -GRAVITY * sin(u[2]) / (u[1] + acceleration),  # Change in Zenith
        ]
    )


def run_scipy(
    dt = 0.05,
    exti = 3,
    t = 200,
    t0 = 0,
    u0 = np.array([0, 0]),  # u[0]=height u[1]=velocity
):
    t = 200
    def f(t, u):
        return f_w_ext(t, u, exti)
        
    return scipyintegrate(u0, scipy.integrate.RK45, f, t, dt, t0=t0)


def apogee(exti, u0, t, t0, dt=0.05):

    f, time = run_scipy(dt=dt, exti=exti, t=t, t0=t0, u0=u0)
    return np.max(f[:, 0])


def runsweep(headless=False, exti=[3], u0=[np.array([0, 0, 1 / 15])], t0=[4]):
    # initial conditions
    t=200
    dt = 0.05

    # run code
    u=[[] for i in range(len(exti))]
    time=[[] for i in range(len(exti))]
    for i in range(len(exti)):
        u[i], time[i] = run_scipy(dt=dt, exti=exti[i], t=t, u0=u0[i], t0=t0[i])

    if not headless:
        # plotting
        fig, (ax1_h, ax2_v, ax3_angle) = plt.subplots(1,3)
        for i in range(len(exti)):
            ax1_h.plot(time[i], u[i][:, 0], label=f"ext={Exts[exti[i]]}, angle={u0[i][2]:.2f}")
            ax1_h.plot(time[i], np.full(len(time[i]), GOAL_HEIGHT_METERS), label="Goal height")

            ax2_v.plot(time[i], u[i][:, 1], label=f"ext={Exts[exti[i]]} angle={u0[i][2]:.2f}")

            ax3_angle.plot(time[i], u[i][:, 2], label=f"ext={Exts[exti[i]]} angle={u0[i][2]:.2f}")
        ax1_h.legend()
        ax1_h.set_xlabel("time (s)")
        ax1_h.set_ylabel("Height(m)")
        ax1_h.set_title("Flight Altitude Graph")
        ax2_v.legend()
        ax2_v.set_xlabel("time (s)")
        ax2_v.set_ylabel("velocity(m/s)")
        ax2_v.set_title("Flight Velocity Graph")
        ax3_angle.legend()
        ax3_angle.set_xlabel("time (s)")
        ax3_angle.set_ylabel("radians")
        ax3_angle.set_title("Flight Angle Graph")
        plt.get_current_fig_manager().full_screen_toggle()
        fig.show()


def run(headless=False, exti=3, u0=np.array([0, 0, 1 / 15]), t0=4):
    # initial conditions
    # T=200
    dt = 0.05

    # run code
    u, time = run_scipy(dt, u0=u0, exti=exti, t0=t0)

    if not headless:
        # plotting
        fig, (ax1_h, ax2_v, ax3_angle) = plt.subplots(1,3)
        ax1_h.plot(time, u[:, 0], label=f"ext={Exts[exti]}, angle={u0[2]:.2f}")
        ax1_h.plot(time, np.full(len(time), GOAL_HEIGHT_METERS), label="Goal height")
        ax1_h.legend()
        ax1_h.set_xlabel("time (s)")
        ax1_h.set_ylabel("Height(m)")
        ax1_h.set_title("Flight Altitude Graph")

        ax2_v.plot(time, u[:, 1], label=f"ext={Exts[exti]} angle={u0[2]:.2f}")
        ax2_v.legend()
        ax2_v.set_xlabel("time (s)")
        ax2_v.set_ylabel("velocity(m/s)")
        ax2_v.set_title("Flight Velocity Graph")

        ax3_angle.plot(time, u[:, 2], label=f"ext={Exts[exti]} angle={u0[2]:.2f}")
        ax3_angle.legend()
        ax3_angle.set_xlabel("time (s)")
        ax3_angle.set_ylabel("radians")
        ax3_angle.set_title("Flight Angle Graph")
        # plt.tight_layout()

        # # plt.plot(Time,U[:,0],label="Height")
        # # plt.plot(Time,U[:,1],label="Velocity")
        # plt.legend()
        # plt.xlabel("time (s)")
        # # plt.ylabel("velocity(m/s)/Height(m)")
        # # plt.show()
        # # plt.plot(np.array(Dragdata),label="Dragdata")
        # # plt.show()
        fig.show()


def eval(maxheight,currheight):
    return abs(maxheight-GOAL_HEIGHT_METERS)


def lookup_table(angles, heights, verbose=True):
    lookup=[[[] for ai in angles] for hi in heights]
    for hi in range(len(heights)):
        for ai in range(len(angles)):
            optimal_vel_list=[]#optimal velocity given a specfic height to switch beavs extension
            for exti in range(len(Exts)):
                va=0
                vb=1.1
                u0=np.array([heights[hi],mach2v([va])[0],angles[ai]])
                apogee_a=abs(apogee(exti,u0,200,t0=4)-GOAL_HEIGHT_METERS)
                u0=np.array([heights[hi],mach2v([vb])[0],angles[ai]])
                apogee_b=abs(apogee(exti,u0,200,t0=4)-GOAL_HEIGHT_METERS)
                while(vb-va>Tol):
                    mid_v=(va+vb)/2
                    # print(mid_v,va,vb)
                    u0=np.array([heights[hi],mach2v([mid_v])[0],angles[ai]])
                    # TODO fix. Consider apogee_mid > apogee_a > apogee_b
                    """I am not convinced this algorithm works for finding the min. 
                    If f(x) = |x + 0.99|x|| and a = -10 and b = 2 then f(-10) = 0.1 and 
                    f(1) = 3.98 so b becomes (a + b) / 2 = -4 and since min f(x) is 
                    when x = 0 this finds the wrong result"""

                    apogee_mid=eval(apogee(exti,u0,200,t0=4),heights[hi])
                    if apogee_a>apogee_b:
                        # print('a has more error')
                        va=mid_v
                        apogee_a=apogee_mid
                    else:
                        # print('b has more error')
                        vb=mid_v
                        apogee_b=apogee_mid
                optimal_vel_list+=[mid_v]
            if verbose:
                print(f"Height:{heights[hi]} Angle:{angles[ai]:.3f} vel diff:{100*(max(optimal_vel_list)-min(optimal_vel_list))/min(optimal_vel_list):.3f}%")
            lookup[hi][ai] += optimal_vel_list
    return lookup


if __name__ == "__main__":
        runsweep(exti=[3,3], u0=[np.array([0, 0, 20 * pi / 180]),np.array([0, 0, 0])], t0=[0,0])
        plt.show()
        runsweep(exti=[0,3], u0=[np.array([0, 0, 0]),np.array([0, 0, 0])], t0=[0,0])
        plt.show()
        heights=[200*i+800 for i in range(11)]
        angles=[pi/180*i**2 for i in range(4)]
        Tol=0.001 
        print("Angles:",angles)
        print("Heights:",heights)
        print("Exts:",Exts)
        lookup=lookup_table(angles, heights)
        print("Lookup:")
        print(np.array(lookup))
        np.save('lookup.npy',lookup)

        if os.path.isfile("tables"):
            raise FileExistsError("\n__________________________________________________\n__________________¶¶¶¶¶¶¶¶¶¶¶¶¶¶__________________\n______________¶¶¶¶_____________¶¶¶¶¶______________\n___________¶¶¶_____________________¶¶¶¶___________\n________¶¶¶¶__________________________¶¶¶_________\n_______¶¶_______________________________¶¶¶_______\n______¶¶__________________________________¶¶______\n____¶¶_____________________________________¶¶_____\n____¶________________________________________¶____\n___¶¶________________________________________¶¶___\n__¶¶_____________¶¶¶__________________________¶___\n___¶___________¶¶_____________________________¶¶__\n___¶___________¶________________¶¶¶___________¶¶__\n___¶_____¶¶_¶¶_¶¶¶¶¶_¶____________¶¶¶__________¶__\n___¶_________¶___¶¶¶¶¶¶¶¶¶¶¶¶______¶¶¶_________¶__\n___¶¶______¶¶¶¶___¶¶¶¶¶¶¶¶¶¶¶¶¶¶____¶¶¶_¶¶____¶¶¶_\n___¶¶____¶¶¶¶¶¶___¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶__¶¶¶¶¶¶¶¶__¶¶__\n___¶____¶¶¶¶¶¶¶____¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶__¶¶¶¶¶¶¶¶¶¶¶___\n__¶¶___¶¶¶¶¶¶¶¶____¶¶¶¶¶¶¶¶¶¶¶¶¶¶__¶¶¶¶¶¶¶¶¶¶¶¶___\n____¶¶¶¶¶¶¶¶¶¶______¶¶¶¶¶¶¶¶¶¶¶¶¶__¶¶¶¶¶¶¶¶¶¶¶____\n______¶¶¶¶¶¶¶___¶¶_____¶¶¶¶¶¶¶¶¶____¶¶¶¶¶¶¶¶¶¶____\n______¶__¶¶¶____¶¶¶___________________¶¶¶¶¶¶¶_____\n_____¶¶________¶¶¶¶¶¶__¶________________¶¶¶_______\n_____¶¶______¶¶¶____¶¶¶¶______________¶¶¶¶________\n______¶¶______¶_______¶¶_________¶¶¶¶¶¶¶¶¶________\n_______¶¶¶¶¶_______________¶_¶¶¶¶¶¶¶¶¶¶¶¶¶________\n___________¶¶¶____¶¶¶¶_¶¶_¶¶¶___¶¶¶¶¶___¶¶________\n____________¶¶¶¶¶_¶__¶¶_¶_¶_¶____¶¶_____¶_________\n_____________¶_____________¶¶_____¶_____¶_________\n______________¶¶¶¶¶_¶¶¶¶¶¶________¶¶____¶_________\n____________________¶¶¶¶¶¶_________¶____¶_________\n_____________________¶¶_¶¶_________¶¶___¶¶________\n______________________¶¶¶¶¶_________¶____¶________\n___Why_is_tables_a_____¶¶¶¶¶_______¶¶____¶¶_______\n___file_it_should_be___¶¶¶¶¶______¶_¶_____¶_______\n___a_directory_to______¶_¶¶¶_____¶__¶¶____¶_______\n___hold_all_the________¶¶¶¶¶____¶¶__¶¶___¶________\n___tables!!____________¶¶¶¶¶__¶¶¶__¶¶___¶_________\n________________________¶¶¶¶¶¶¶__¶¶¶___¶¶_________\n_________________________¶¶_____¶¶¶____¶__________\n____________________________¶¶¶¶______¶___________\n______________________________¶¶_____¶¶___________\n_______________________________¶¶¶¶¶¶¶____________\n__________________________________________________")
        if not os.path.exists("tables"):
            os.mkdir("tables")

        np.save("tables/angles.npy", angles)
        np.save("tables/heights.npy", heights)
        np.save("tables/exts.npy", Exts)
        np.save("tables/lookup.npy", lookup)
