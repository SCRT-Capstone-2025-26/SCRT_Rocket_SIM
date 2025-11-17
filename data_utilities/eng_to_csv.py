import csv
from dataimport_utilities import read_eng_thrustfile

# Converts a .eng file to a .csv file
def eng_to_csv(src_filepath, dst_filepath, spec_filepath=None):
    thrust_data = read_eng_thrustfile(src_filepath)
    motor_spec = [list(thrust_data[0])] + [list(thrust_data[0].values())]
    thrust_data = [["Time (s)", "Thrust (N)"]] + thrust_data[1:]
    # write thrust csv
    with open(dst_filepath, "w") as file:
        writer = csv.writer(file)
        writer.writerows(thrust_data)
    # write motor spec csv
    if spec_filepath is not None:
        with open(spec_filepath, "w") as file:
            writer = csv.writer(file)
            writer.writerows(motor_spec)


# Example usage of functions
if __name__ == "__main__":
    src_filepath = "../sample_datasets/AeroTech_N2000W.eng"
    dst_filepath = "../data/runs/20251114_191130/input/thrust_motor.csv"
    spec_filepath = "../data/runs/20251114_191130/input/motor_spec.csv"
    eng_to_csv(src_filepath, dst_filepath, spec_filepath)