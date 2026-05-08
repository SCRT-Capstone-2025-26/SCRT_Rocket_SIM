import csv
import numpy as np
from equations_n_constants import STD_DRAG_COL_NAMES, STD_DRAG_CSV_LIST

# convenient functions

""" Returns the sign of a numeric value
Input: numeric value
Output: -1, 1, or 0 depending on the sign of the value
"""
def sign(v):
    return abs(v) / v if v != 0 else 0


def npmap(arr, func):
    return np.array(list(map(func, list(arr))))


# given a function itertate f such that f(f(f(...))) converges find that
def iterate(f, guess, iter=20, err=0.00001, verbose=False):
    i = 0
    fguess = f(guess)
    while i < iter and np.linalg.norm(fguess - guess) > err:
        guess = fguess
        fguess = f(guess)
        i += 1
    if i > 1 and verbose:
        print("iteration: " + str(i))
    return guess


def implicit(iterable):
    return lambda f, t, dt, u: iterate(iterable(f, t, dt, u), u[-1])

def read_thrust_data(filename):
    array = []
    with open(filename, "r") as file:
        for line in csv.reader(file):
            array += [line]
    return array


def np_thrust_data(filename):
    return np.array([[float(x) for x in y] for y in read_thrust_data(filename)[1:]])

# Input:
#     csv_list: a list of csv filepath strings.
#     VarNames: a list of substrings in the headers you want data from
#         Default values of ['Extension','Mach','Drag Coeff']

def read_csv_to_list_of_lists(filename):
    """Reads a CSV file and returns its content as a list of lists. (Specifically as Strings)"""
    data = []
    with open(filename, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        data = list(reader)
    return data

def find_index(word, csv_data):
    # Finds the index of a specific substring in the header
    # in the list of lists created by the
    # read_csv_to_list_of_lists function
    for i in range(len(csv_data[0])):
        if word in csv_data[0, i] and csv_data[1, i] != "null":
            # print(csv_data[1,i])
            return i

def read_drag_data_np(
    csv_files=STD_DRAG_CSV_LIST,
    col_names=STD_DRAG_COL_NAMES,
):  # list of substrings in the headers for which you want data
    import numpy as np

    # initialize a list for each Variable
    vars = [[] for i in range(len(col_names))] 
    for csv_item in csv_files:
        # get list version of each CSV as a numpy array
        csv_data = np.array(read_csv_to_list_of_lists(csv_item)) 
         # adds each variable into it's specific list
        for vari in range(len(vars)):
            vars[vari] += [
                float(csv_data[:, find_index(col_names[vari], csv_data)][i + 1])
                for i in range(len(csv_data) - 1)
            ]
    for vari in range(len(vars)):
        vars[vari] = np.array(vars[vari])
    # print(Vars)
    return vars
