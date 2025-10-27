import json
import csv
# import pandas as pd

def read_thrust_data(filename):
    array = []
    with open(filename, "r") as file:
        for line in csv.reader(file):
            array += [line]
    return array




