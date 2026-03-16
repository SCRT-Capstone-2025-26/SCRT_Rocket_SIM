import matplotlib.pyplot as plt

from numpy import sin, cos, pi
import numpy as np
from integration import scipyintegrate
# from data_utilities.dataimport_utilities import np_thrust_data,read_drag_data_np

from data_utilities.interpolation import cd_init
import scipy

##################CD is actually just drag rn

Dragdata = []


# physical constants


def air_density(h):
    return 1.2 * 0.99988**h


def thrust(t):
    return 3000 if t < 4 else 0


g = -10
body_mass = 15


def motor_mass(t):
    return 10


def total_mass(t):
    return body_mass + motor_mass(t)


Exts = [0, 5, 15, 30]
Cd = [cd_init(ext) for ext in Exts]


def drag(h, v, theta, exti, t):
    if t < 4 or theta * 180 / pi > 20:
        exti = 0
    global Dragdata
    Dragdata += [air_density(h) * Cd[exti](v / 343)]
    return air_density(h) * Cd[exti](v / 343)


# acceleration=-(A*rho*Cd*v^2+thrust)/m+g
def accel(t, u, exti):
    h, v, theta = u
    return (-drag(h, v, theta, exti, t) + thrust(t)) / total_mass(t) + g


# FDS bs
def f_w_ext(t, u, exti):  # the derivative of the state space
    acceleration = accel(t, u, exti)
    return np.array(
        [
            u[1] * cos(u[2]),  # Change in Height
            acceleration,  # Change in Velocity
            -g * sin(u[2]) / (u[1] + acceleration),  # Change in Zenith
        ]
    )


def run_scipy(
    dt,
    exti=3,
    t0=0,
    u0=np.array([0, 0]),  # u[0]=height u[1]=velocity
):
    t = 200
    dt = 0.05

    def f(t, u):
        return f_w_ext(t, u, exti)

    return scipyintegrate(u0, scipy.integrate.RK45, f, t, dt, t0=t0)


def apogee(exti, u0, t, t0, dt=0.0005):

    f, time = run_scipy(dt, exti=exti, t0=t0, u0=u0)
    return np.max(f[:, 0])


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
        ax1_h.plot(time, [10000 * 0.3048 for t in time], label="Goal height")
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
    return abs(maxheight-10000/3.3)


def lookup_table(angles,heights):
    lookup=[[[] for ai in angles] for hi in heights]
    for hi in range(len(heights)):
        for ai in range(len(angles)):
            optimal_vel_list=[]#optimal velocity given a specfic height to switch beavs extension
            for exti in range(len(Exts)):
                va=0
                vb=1.1
                u0=np.array([heights[hi],mach2v([va])[0],angles[ai]])
                apogee_a=abs(apogee(exti,u0,200,t0=4)-10000/3.3)
                u0=np.array([heights[hi],mach2v([vb])[0],angles[ai]])
                apogee_b=abs(apogee(exti,u0,200,t0=4)-10000/3.3)
                while(vb-va>Tol):
                    mid_v=(va+vb)/2
                    # print(mid_v,va,vb)
                    u0=np.array([heights[hi],mach2v([mid_v])[0],angles[ai]])
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
            print(f"Height:{heights[hi]} Angle:{angles[ai]:.3f} vel diff:{100*(max(optimal_vel_list)-min(optimal_vel_list))/min(optimal_vel_list):.3f}%")
            lookup[hi][ai]+=[optimal_vel_list]
    return lookup

def mach2v(v):
    # TODO add more decimal points
    return [343.0 * v for v in v]


if __name__ == "__main__":
        run(exti=3, u0=np.array([0, 0, 20 * pi / 180]), t0=0)
        run(exti=3, u0=np.array([0, 0, 0]), t0=0)
        plt.show()
        run(exti=3, u0=np.array([0, 0, 5 * pi / 180]), t0=0)
        run(exti=0, u0=np.array([0, 0, 5 * pi / 180]), t0=0)
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
