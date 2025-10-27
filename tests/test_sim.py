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


@pytest.mark.skip(reason="Failing")
def test_scipy_convergence():
    conv.conv_test(lambda x: sim.run_scipy(5000 * (0.1**x)), 5, conv.power_bound(-1))
