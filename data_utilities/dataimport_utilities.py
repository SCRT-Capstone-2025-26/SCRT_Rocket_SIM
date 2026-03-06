import csv
import numpy as np
import dataclasses

def read_thrust_data(filename):
    array = []
    with open(filename, "r") as file:
        for line in csv.reader(file):
            array += [line]
    return array

def np_thrust_data(filename):
    return np.array([[float(x) for x in y] for y in read_thrust_data(filename)[1:]])

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

class DragPoint:#TODO:make this reflect actual CSVs
    # degrees from horizontal (ccw)
    angle_of_attack: float

    # TODO: add vertical component of velocity
    # m/s
    ship_velocity_x: float

    # drag coefficient
    drag: float

    # TODO: wind speed and temperature
    
def read_csv_to_list_of_lists(filename):
    """Reads a CSV file and returns its content as a list of lists. (Specifically as Strings)"""
    data = []
    with open(filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        data = list(reader)
    return data

def find_index(word,csv_data):
    # Finds the index of a specific substring in the header
    # in the list of lists created by the 
    # read_csv_to_list_of_lists function
    for i in range(len(csv_data[0])):
        if word in csv_data[0,i] and csv_data[1,i]!='null':
            # print(csv_data[1,i])
            return i


        

# Input: 
#     CSVs: a list of csv filepath strings.
#     VarNames: a list of substrings in the headers you want data from
#         Default values of ['Extension','Mach','Drag Coeff']
def read_drag_data_np(CSVs = [
'sample_datasets/SupSonicSweep2_012826_data.csv',
'sample_datasets/SupSonicSweep4_013026_FullData.csv',
'sample_datasets/SupSonicSweep5_013126_FullData.csv',
'sample_datasets/SupSonicSweep2_BEAVS_012926_FullData.csv'],
# 'sample_datasets/SupSonicSweep7_SATurb_020426_FullData.csv',
# 'sample_datasets/SupSonicSweep8_SATurb_020526_FullData.csv'],
              # 'sample_datasets/SupSonicSweep5_013126_FullData.csv',    
              # 'sample_datasets/SupSonicSweep2_BEAVS_012926_FullData.csv', 
              # 'sample_datasets/SupSonicSweep4_013026_FullData.csv',
              # 'sample_datasets/SupSonicSweep4_013026_FullData.csv'],
              # '../sample_datasets/SimNoaMaxStyle.csv'],

              # '../sample_datasets/NoaExt1DCdMach.csv'], # list of CSVs to be used
        VarNames=['Extension','Mach','Drag Coeff']): # list of substrings in the headers for which you want data
    import numpy as np
    Vars=[[] for i in range(len(VarNames))] # initialize a list for each Variable
    for CSV in CSVs: 
        csv_data = np.array(read_csv_to_list_of_lists(CSV)) # get list version of each CSV as a numpy array
        for vari in range(len(Vars)): # adds each variable into it's specific list
            Vars[vari]+=[float(csv_data[:, find_index(VarNames[vari], csv_data)][i+1]) for i in range(len(csv_data)-1)]
    for vari in range(len(Vars)):
        Vars[vari]=np.array(Vars[vari])
    #print(Vars)
    return Vars

def plot2d(Vars,VarNames=['Extension','Mach','Drag Coeff']):
        import matplotlib.pyplot as plt
        import numpy as np
        xs =Vars[0]
        ys =Vars[1]
        zs =Vars[2]
# 2. Create a figure and a 3D axes object
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(projection='3d') # or fig.add_subplot(111, projection='3d')
# 3. Plot the data
        ax.scatter(xs, ys, zs, c=zs, cmap='viridis', marker='o') # 'c' for color mapping, 'cmap' for color map
# 4. Add labels and a title
        ax.set_xlabel(VarNames[0])
        ax.set_ylabel(VarNames[1])
        ax.set_zlabel(VarNames[2])
# 5. Display the plot
        plt.show()


  
def read_drag_data(filename):
    points=[]
    line=read_drag_data_np(CSVs=[filename],
                           VarNames=['Extension','Mach','Drag Coeff']) 
    #TODO: changes VarNames to match the lines in DragPoint
    for i in range(len(line[1])):
        point = DragPoint(
            angle=line[0][i],
            wind_speed=line[1][i],
            temperature=line[2][i],
            ship_speed=line[3][i],
            drag=line[4][i]
        )
        points.append(point)
    return points

if __name__ == "__main__":
    print(read_eng_thrustfile("../sample_datasets/AeroTech_N2000W.eng"))
    plot2d(read_drag_data_np())
    plot2d(read_drag_data_np(VarNames=['Extension','Mach','Drag of all']))
    # ext,mach,cd=read_drag_data_np()
    # ext2,cd2=read_drag_data_np(CSVs=['../sample_datasets/SimNoaExtDragCd.csv'],VarNames=['Extension','Drag Coeff'])
    # mach=np.array(list(mach)+[0.75 for i in range(len(ext2))])
    # plot2d([np.array(list(ext)+list(ext2)),mach,np.array(list(cd)+list(cd2))])
