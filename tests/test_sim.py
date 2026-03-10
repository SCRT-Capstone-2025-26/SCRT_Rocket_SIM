from simulation import sim
import convergence as conv
import pytest


def test_run():
    sim.run(headless=True)


def test_adaptive_convergence():
    conv.conv_test(
        lambda x: max(sim.run_integrate_adaptive(5 * (0.1**x))[1]),
        5,
        conv.power_bound(-1),
    )


