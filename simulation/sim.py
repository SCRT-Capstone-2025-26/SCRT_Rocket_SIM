import matplotlib.pyplot as plt

from numpy import sin, cos, pi
import numpy as np
from integration import scipyintegrate
# from data_utilities.dataimport_utilities import np_thrust_data,read_drag_data_np

from data_utilities.interpolation import drag_p_airden_fn
from data_utilities.equations_n_constants import air_density, thrust, total_mass, mach2v, v2mach, GRAVITY, GOAL_HEIGHT_METERS
import scipy

##################CD is actually just drag rn

# TODO make class or something to get rid of usign a global object
Dragdata = []


# physical constants and simple equations imported from data_utilities.equations_n_constants



Exts = [0, 5, 15, 30]
drag_p_airden = [drag_p_airden_fn(ext) for ext in Exts]


def drag(h, v, theta, exti, t):

    if t < 4 or theta * 180 / pi > 25:
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
    return (-drag(h, v, theta, exti, t) + thrust(t)) / total_mass(t) + GRAVITY*cos(theta)


# FDS bs
# the derivative of the state space
# forcing function f for finite difference scheme accountign for extention
def f_w_ext(t, u, exti): 
    # this is a numerical trick to make sure that the code doesn't break at t=0
    backward_euler_dt = 0.005
    acceleration = accel(t, u, exti)
    return np.array(
        [
            u[1] * cos(u[2]),  # Change in Height
            acceleration,  # Change in Velocity
            # acceleration term is to avoid divides by zero
            -GRAVITY * sin(u[2]) / (u[1] + acceleration*backward_euler_dt),  # Change in Zenith
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
        fig, (ax1_h, ax2_v, ax3_angle,axti) = plt.subplots(1,4)
        for i in range(len(exti)):
            ax1_h.plot(time[i], u[i][:, 0], label=f"ext={Exts[exti[i]]}, angle={u0[i][2]*180/pi:.2f}")

            ax2_v.plot(time[i], u[i][:, 1], label=f"ext={Exts[exti[i]]} angle={u0[i][2]*180/pi:.2f}")
            ax3_angle.plot(time[i], u[i][:, 2] * 180/pi, label=f"ext={Exts[exti[i]]} angle={u0[i][2]*180/pi:.2f}")
            axti.plot(time[i], np.array([0 if (time[i][t] < 4 or u[i][t,2] * 180 / pi > 20) else Exts[exti[i]] for t in range(len(time[i]))]), label=f"ext={Exts[exti[i]]} angle={u0[i][2]*180/pi:.2f}")
        ax1_h.plot(time[i], np.full(len(time[i]), GOAL_HEIGHT_METERS), label="Goal height")
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
        ax3_angle.set_ylabel("degrees")
        ax3_angle.set_title("Flight Angle Graph")
        axti.legend()
        axti.set_xlabel("time (s)")
        axti.set_ylabel("mm")
        axti.set_title( "Extension")
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


def eval(v,hi,ai,exti):
    u0=np.array([heights[hi],mach2v([vb])[0],angles[ai]])
    return apogee(exti,u0,200,t0=4)-GOAL_HEIGHT_METERS

def lookup_table(angles, heights, verbose=True):
    lookup=[[[] for ai in angles] for hi in heights]
    for hi in range(len(heights)):
        for ai in range(len(angles)):
            optimal_vel_list=[]#optimal velocity given a specfic height to switch beavs extension
            for exti in range(len(Exts)):
                va=0
                vb=1.1
                apogee_a=eval(va,hi,ai,exti)
                apogee_b=eval(vb,hi,ai,exti)
                # If we are always overshooting then our best velocity is 0
                if (apogee_a)>0:
                    return 0
                # If we are always undershooting then our best velocity is maximum
                if (apogee_b)<0:
                    return 2
                while(vb-va>Tol):
                    mid_v=(va+vb)/2
                    apogee_mid=eval(mid_v,hi,ai,exti)
                    if apogee_mid>0:
                        va=mid_v
                    else:
                        vb=mid_v
                optimal_vel_list+=[mid_v]
            if verbose:
                print(f"Height:{heights[hi]} Angle:{angles[ai]:.3f} vel diff:{100*(max(optimal_vel_list)-min(optimal_vel_list))/min(optimal_vel_list):.3f}%")
            lookup[hi][ai] += optimal_vel_list
    return lookup


if __name__ == "__main__":
        runsweep(exti=[3 for i in range(15)], 
                 u0=[np.array([0, 0, i * pi / 180]) for i in range(15)],
                                      t0=[0 for i in range(15)])
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
