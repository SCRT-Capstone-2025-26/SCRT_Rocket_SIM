import matplotlib.pyplot as plt

from numpy import sin, cos, pi
import numpy as np
import scipy
import os

from integration import scipyintegrate
from interpolation import drag_p_airden_fn
from equations_n_constants import air_density, thrust, total_mass, mach2v, v2mach, GRAVITY, GOAL_HEIGHT_METERS

##################CD is actually just drag rn

# physical constants and simple equations imported from data_utilities.equations_n_constants
# TODO add comments

class Sim():
    def __init__(self):
        self.dragdata = []
        self.exts = [0, 5, 15, 30]
        self.drag_p_airden = [drag_p_airden_fn(ext) for ext in self.exts]

    def get_exts(self):
        return self.exts


    def drag(self, h, v, theta, exti, t):
        # If the angle is too big we have to retract the blades
        if t < 4 or theta * 180 / pi > 20:
            exti = 0
        next_dragdata = air_density(h) * self.drag_p_airden[exti](v2mach(v))
        self.dragdata += [next_dragdata]
        return next_dragdata


    # acceleration=-(A*rho*Cd*v^2+thrust)/m+g
    # TODO add derivation documentation
    def accel(self, t, u, exti):
        h, v, theta = u
        # TODO np.cos(theta)*GRAVITY is correct, whiteboarded work needs to be documented.
        return ((-self.drag(h, v, theta, exti, t) + thrust(t)) / total_mass(t)) + np.cos(theta)*GRAVITY
    
    
    # FDS bs
    # the derivative of the state space
    # forcing function f for finite difference scheme accountign for extention
    def f_w_ext(self, t, u, exti): 
        # this is a numerical trick to make sure that the code doesn't break at t=0
        backward_euler_dt = 0.005
        acceleration = self.accel(t, u, exti)
        return np.array(
            [
                u[1] * cos(u[2]),  # Change in Height
                acceleration,  # Change in Velocity
                # acceleration term is to avoid divides by zero
                -GRAVITY * sin(u[2]) / (u[1] + acceleration*backward_euler_dt),  # Change in Zenith
            ]
        )


    def run_scipy(
        self,
        dt = 0.05,
        exti = 3,
        t = 200,
        t0 = 0,
        u0 = np.array([0, 0]),  # u[0]=height u[1]=velocity
    ):
        # Forcing function needed for scipu RK45
        def f(t, u):
            return self.f_w_ext(t, u, exti)
            
        return scipyintegrate(u0, scipy.integrate.RK45, f, t, dt, t0=t0)


    def apogee(self, exti, u0, t, t0, dt=0.05):
        f, time = self.run_scipy(dt=dt, exti=exti, t=t, t0=t0, u0=u0)
        return np.max(f[:, 0])


    def runsweep(self, headless=False, exti=[3], u0=[np.array([0, 0, 1 / 15])], t0=[4]):
        # initial conditions
        t=200
        dt = 0.05

        # run code
        u=[[] for i in range(len(exti))]
        time=[[] for i in range(len(exti))]
        for i in range(len(exti)):
            u[i], time[i] = self.run_scipy(dt=dt, exti=exti[i], t=t, u0=u0[i], t0=t0[i])

        if not headless:
            # plotting
            fig, (ax1_h, ax2_v, ax3_angle,axti) = plt.subplots(1,4)
            for i in range(len(exti)):
                ax1_h.plot(time[i], u[i][:, 0], label=f"ext={self.exts[exti[i]]}, angle={u0[i][2]*180/pi:.2f}")

                ax2_v.plot(time[i], u[i][:, 1], label=f"ext={self.exts[exti[i]]} angle={u0[i][2]*180/pi:.2f}")
                ax3_angle.plot(time[i], u[i][:, 2] * 180/pi, label=f"ext={self.exts[exti[i]]} angle={u0[i][2]*180/pi:.2f}")
                axti.plot(time[i], np.array([0 if (time[i][t] < 4 or u[i][t,2] * 180 / pi > 20) else self.exts[exti[i]] for t in range(len(time[i]))]), label=f"ext={self.exts[exti[i]]} angle={u0[i][2]*180/pi:.2f}")
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


    def run(self, headless=False, exti=3, u0=np.array([0, 0, 1 / 15]), t0=4):
        # initial conditions
        # T=200
        dt = 0.05

        # run code
        u, time = self.run_scipy(dt, u0=u0, exti=exti, t0=t0)

        if not headless:
            # plotting
            fig, (ax1_h, ax2_v, ax3_angle) = plt.subplots(1,3)
            ax1_h.plot(time, u[:, 0], label=f"ext={self.exts[exti]}, angle={u0[2]:.2f}")
            ax1_h.plot(time, np.full(len(time), GOAL_HEIGHT_METERS), label="Goal height")
            ax1_h.legend()
            ax1_h.set_xlabel("time (s)")
            ax1_h.set_ylabel("Height(m)")
            ax1_h.set_title("Flight Altitude Graph")

            ax2_v.plot(time, u[:, 1], label=f"ext={self.exts[exti]} angle={u0[2]:.2f}")
            ax2_v.legend()
            ax2_v.set_xlabel("time (s)")
            ax2_v.set_ylabel("velocity(m/s)")
            ax2_v.set_title("Flight Velocity Graph")

            ax3_angle.plot(time, u[:, 2], label=f"ext={self.exts[exti]} angle={u0[2]:.2f}")
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


    def eval(self, v,h,a,exti):
        u0=np.array([h,mach2v(v),a])
        return self.apogee(exti,u0,200,t0=4)-GOAL_HEIGHT_METERS

    def binary_search(self, h,a,exti):
        va=0
        vb=1.1
        # If we are always overshooting then our best velocity is 0
        if (self.eval(va,h,a,exti))>0:
            return 0
        # If we are always undershooting then our best velocity is maximum
        if (self.eval(vb,h,a,exti))<0:
            return 1.2
        while(vb-va>Tol):
            mid_v=(va+vb)/2
            apogee_mid=self.eval(mid_v,h,a,exti)
            # print(exti,apogee_mid)
            if apogee_mid<0:
                va=mid_v
            else:
                vb=mid_v
        return mid_v


    def lookup_table(self, angles, heights, save=False, verbose=True):
        lookup=[[[] for ai in angles] for hi in heights]
        for hi in range(len(heights)):
            for ai in range(len(angles)):
                optimal_vel_list=[]#optimal velocity given a specfic height to switch beavs extension
                for exti in range(len(self.exts)):
                    h=heights[hi]
                    a=angles[ai]
                    optimal_vel_list+=[self.binary_search(h, a, exti)]
                if verbose:
                    print(f"Height:{heights[hi]} Angle:{angles[ai]:.3f} vel diff:{100*(max(optimal_vel_list)-min(optimal_vel_list))/min(optimal_vel_list):.3f}%")
                    # print([float(self.eval(v, h, a, exti)) for v,exti in zip(optimal_vel_list,[0,1,2,3])])
                    # print(optimal_vel_list)
                    # print()
                lookup[hi][ai] += optimal_vel_list
        if save:
            base_path = os.path.join(os.path.dirname(__file__), "..", "tables")

            if os.path.isfile(base_path):
                # Prints a stylized error message.
                raise FileExistsError("\n__________________________________________________\n__________________¶¶¶¶¶¶¶¶¶¶¶¶¶¶__________________\n______________¶¶¶¶_____________¶¶¶¶¶______________\n___________¶¶¶_____________________¶¶¶¶___________\n________¶¶¶¶__________________________¶¶¶_________\n_______¶¶_______________________________¶¶¶_______\n______¶¶__________________________________¶¶______\n____¶¶_____________________________________¶¶_____\n____¶________________________________________¶____\n___¶¶________________________________________¶¶___\n__¶¶_____________¶¶¶__________________________¶___\n___¶___________¶¶_____________________________¶¶__\n___¶___________¶________________¶¶¶___________¶¶__\n___¶_____¶¶_¶¶_¶¶¶¶¶_¶____________¶¶¶__________¶__\n___¶_________¶___¶¶¶¶¶¶¶¶¶¶¶¶______¶¶¶_________¶__\n___¶¶______¶¶¶¶___¶¶¶¶¶¶¶¶¶¶¶¶¶¶____¶¶¶_¶¶____¶¶¶_\n___¶¶____¶¶¶¶¶¶___¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶__¶¶¶¶¶¶¶¶__¶¶__\n___¶____¶¶¶¶¶¶¶____¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶__¶¶¶¶¶¶¶¶¶¶¶___\n__¶¶___¶¶¶¶¶¶¶¶____¶¶¶¶¶¶¶¶¶¶¶¶¶¶__¶¶¶¶¶¶¶¶¶¶¶¶___\n____¶¶¶¶¶¶¶¶¶¶______¶¶¶¶¶¶¶¶¶¶¶¶¶__¶¶¶¶¶¶¶¶¶¶¶____\n______¶¶¶¶¶¶¶___¶¶_____¶¶¶¶¶¶¶¶¶____¶¶¶¶¶¶¶¶¶¶____\n______¶__¶¶¶____¶¶¶___________________¶¶¶¶¶¶¶_____\n_____¶¶________¶¶¶¶¶¶__¶________________¶¶¶_______\n_____¶¶______¶¶¶____¶¶¶¶______________¶¶¶¶________\n______¶¶______¶_______¶¶_________¶¶¶¶¶¶¶¶¶________\n_______¶¶¶¶¶_______________¶_¶¶¶¶¶¶¶¶¶¶¶¶¶________\n___________¶¶¶____¶¶¶¶_¶¶_¶¶¶___¶¶¶¶¶___¶¶________\n____________¶¶¶¶¶_¶__¶¶_¶_¶_¶____¶¶_____¶_________\n_____________¶_____________¶¶_____¶_____¶_________\n______________¶¶¶¶¶_¶¶¶¶¶¶________¶¶____¶_________\n____________________¶¶¶¶¶¶_________¶____¶_________\n_____________________¶¶_¶¶_________¶¶___¶¶________\n______________________¶¶¶¶¶_________¶____¶________\n___Why_is_tables_a_____¶¶¶¶¶_______¶¶____¶¶_______\n___file_it_should_be___¶¶¶¶¶______¶_¶_____¶_______\n___a_directory_to______¶_¶¶¶_____¶__¶¶____¶_______\n___hold_all_the________¶¶¶¶¶____¶¶__¶¶___¶________\n___tables!!____________¶¶¶¶¶__¶¶¶__¶¶___¶_________\n________________________¶¶¶¶¶¶¶__¶¶¶___¶¶_________\n_________________________¶¶_____¶¶¶____¶__________\n____________________________¶¶¶¶______¶___________\n______________________________¶¶_____¶¶___________\n_______________________________¶¶¶¶¶¶¶____________\n__________________________________________________")
            if not os.path.exists("tables"):
                os.mkdir(base_path)

            np.save(os.path.join(base_path, "angles.npy"), angles)
            np.save(os.path.join(base_path, "heights.npy"), heights)
            np.save(os.path.join(base_path, "exts.npy"), self.exts)
            np.save(os.path.join(base_path, "lookup.npy"), lookup)

        return lookup


if __name__ == "__main__":
        sim = Sim()
        sim.runsweep(exti=[3,3], u0=[np.array([0, 0, 20 * pi / 180]),np.array([0, 0, 0])], t0=[0,0])
        plt.show()
        sim.runsweep(exti=[0,3], u0=[np.array([0, 0, 0]),np.array([0, 0, 0])], t0=[0,0])
        plt.show()
        heights=[200*i+800 for i in range(11)]
        angles=[pi/180*i**2 for i in range(4)]
        Tol=0.001 
        print("Angles:",angles)
        print("Heights:",heights)
        print("Exts:",sim.get_exts())
        lookup=sim.lookup_table(angles, heights, save=False)
        print("Lookup:")
        print(np.array(lookup))
        
