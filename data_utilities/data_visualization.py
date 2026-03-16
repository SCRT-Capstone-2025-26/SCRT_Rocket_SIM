import matplotlib.pyplot as plt


# Plots a 2d data in a 3D graph
# Input:
#     Vars: 2D list with 3 arrays in the first dimension for the 3 data axis
#     VarNames: Names of the 3 axis for the graph axis labels.
#         Default values of ['Extension','Mach','Drag Coeff']
def plot2d_surf(vars, var_names=["Extension", "Mach", "Drag Coeff"]):
    xs = vars[0]
    ys = vars[1]
    zs = vars[2]
    # 2. Create a figure and a 3D axes object
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(projection="3d")  # or fig.add_subplot(111, projection='3d')
    # 3. Plot the data
    ax.scatter(
        xs, ys, zs, c=zs, cmap="viridis", marker="o"
    )  # 'c' for color mapping, 'cmap' for color map
    # 4. Add labels and a title
    ax.set_xlabel(var_names[0])
    ax.set_ylabel(var_names[1])
    ax.set_zlabel(var_names[2])
    # 5. Display the plot
    plt.show()


if __name__ == "__main__":
    from dataimport_utilities import read_drag_data_np

    plot2d_surf(read_drag_data_np())
    plot2d_surf(read_drag_data_np(col_names=["Extension", "Mach", "Drag of all"]))
    # ext,mach,cd=read_drag_data_np()
    # ext2,cd2=read_drag_data_np(CSVs=['../sample_datasets/SimNoaExtDragCd.csv'],VarNames=['Extension','Drag Coeff'])
    # mach=np.array(list(mach)+[0.75 for i in range(len(ext2))])
    # plot2d([np.array(list(ext)+list(ext2)),mach,np.array(list(cd)+list(cd2))])
