import filecmp
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data_utilities"))
from eng_to_csv import eng_to_csv



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

