import filecmp
import os
from data_utilities.eng_to_csv import eng_to_csv
from data_utilities.dataimport_utilities import read_thrust_data

# test dependent on thrust_sample.csv not changing
def test_read_thrust_data():
    thrust_src = os.path.join(os.path.dirname(__file__), "..", "sample_datasets", "thrust_sample.csv")
    thrust_data = read_thrust_data(thrust_src)
    assert thrust_data[0][0] == "Time (s)"
    assert thrust_data[0][1] == "Thrust (N)"
    assert thrust_data[11][0] == "10"

# test dependent on AeroTech_N2000W.eng not changing
def test_read_eng_thrustfile():
    eng_src = os.path.join(os.path.dirname(__file__), "..", "sample_datasets", "AeroTech_N2000W.eng")
    eng_data = read_thrust_data(eng_src)
    assert eng_data[0]["motor_name"] == "N2000W"
    assert eng_data[1][0] == "0.146"

def test_eng_to_csv():
    eng_src = os.path.join(os.path.dirname(__file__), "..", "sample_datasets", "AeroTech_N2000W.eng")

    spec_true = os.path.join(os.path.dirname(__file__), "..", "sample_datasets", "motor_spec.csv")
    spec_created = os.path.join(os.path.dirname(__file__), "..", "sample_datasets", "motor_spec_test.csv")

    thrust_true = os.path.join(os.path.dirname(__file__), "..", "sample_datasets", "thrust_motor.csv")
    thrust_created = os.path.join(os.path.dirname(__file__), "..", "sample_datasets", "thrust_motor_test.csv")
    eng_to_csv(eng_src, thrust_created, spec_created)

    assert(filecmp.cmp(spec_true, spec_created, shallow=False))
    assert(filecmp.cmp(thrust_true, thrust_created, shallow=False))

    if os.path.exists(spec_created):
        os.remove(spec_created)
    if os.path.exists(thrust_created):
        os.remove(thrust_created)

