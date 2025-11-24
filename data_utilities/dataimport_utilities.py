import csv
import dataclasses

def read_thrust_data(filename):
    array = []
    with open(filename, "r") as file:
        for line in csv.reader(file):
            array += [line]
    return array

def read_eng_thrustfile(filename):
    array = []
    with open(filename, "r") as file:
        is_header = 1
        for line in file:
            if ";" in line:
                continue
            if is_header:
                is_header = 0
                header_values = line.strip().split(" ")
                if len(header_values) < 7:
                    return -1
                header_line = {"motor_name":header_values[0],
                               "diameter":header_values[1],
                               "length":header_values[2],
                               "delays":header_values[3],
                               "prop_weight":header_values[4],
                               "tot_weight":header_values[5],
                               "manufacturer":header_values[6]}
                array += [header_line]
            else:
                array += [line.strip().split(" ")]
    return array


@dataclasses.dataclass
class DragPoint:
    # degrees from horizontal (ccw)
    angle_of_attack: float

    # TODO: add vertical component of velocity
    # m/s
    ship_velocity_x: float

    # drag coefficient
    drag: float

    # TODO: wind speed and temperature
    

def read_drag_data(filename):
    points = []

    with open(filename, "r") as file:
        for line in csv.reader(file):
            point = DragPoint(
                angle_of_attack=line[0],
                ship_velocity_x=line[1],
                drag=line[2]
            )
            points.append(point)

    return points
    

if __name__ == "__main__":
    print(read_eng_thrustfile("/sample_datasets/AeroTech_N2000W.eng"))




