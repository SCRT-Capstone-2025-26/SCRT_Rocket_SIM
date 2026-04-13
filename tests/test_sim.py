from simulation import sim


def test_run():
    simulator = sim.Sim()
    simulator.run(headless=True)
