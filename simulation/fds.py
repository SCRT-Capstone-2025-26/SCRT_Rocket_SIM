from utilities import iterate
from simulation.butcher_table import butcher_table_2


def heun(f, t, dt, u):  # forward euler FDS
    return u[-1] + dt * (f(t, u[-1]) + f(t + dt, u[-1] + dt * f(t, u[-1]))) / 2


def fe_fds(f, t, dt, u):  # forward euler FDS
    return u[-1] + dt * f(t, u[-1])


def be_fds(f, t, dt, u):  # Backward Euler
    return iterate(lambda un: u[-1] + dt * f(t + dt, un), u[-1])


def trap_fds(f, t, dt, u):  # trapezoidal FDS
    return iterate(lambda un: u[-1] + dt * (f(t + dt, un) + f(t, u[-1])) / 2, u[-1])


RK4 = butcher_table_2(
    [[0, 0, 0, 0], [1 / 3, 0, 0, 0], [-1 / 3, 1, 0, 0], [1, -1, 1, 0]],
    [0, 1 / 3, 2 / 3, 1],
    [1 / 8, 3 / 8, 3 / 8, 1 / 8],
)
RK1 = butcher_table_2([[1]], [1], [1])
RKtrap = butcher_table_2([[0, 0], [1 / 2, 1 / 2]], [0, 1], [0.5, 0.5])
RKheun = butcher_table_2([[0, 0], [1, 0]], [0, 1], [0.5, 0.5])
