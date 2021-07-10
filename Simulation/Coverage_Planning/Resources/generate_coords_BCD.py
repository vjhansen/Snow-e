"""
Generate way-points for coverage path planning
    from Boustrophedon Cellular Decomposition (BCD)
"""

import math
import csv
import argparse

with open("BCD_coordinates.csv") as csvread_file:
    readCSV = csv.reader(csvread_file, delimiter=",")
    x_b_coord = []
    x_t_coord = []
    z_s_coord = []
    z_e_coord = []
    for row in readCSV:
        z_start = row[1]
        z_end = row[2]
        X_start = row[3]
        X_end = row[4]
        z_s_coord.append(z_start)
        z_e_coord.append(z_end)
        x_b_coord.append(X_start)
        x_t_coord.append(X_end)


def init_x_b(cell):
    x_b = float(x_b_coord[cell])
    return x_b


def init_x_t(cell):
    x_t = float(x_t_coord[cell])
    return x_t


def init_z_s(cell):
    z_s = float(z_s_coord[cell])
    return z_s


def init_z_e(cell):
    z_e = float(z_e_coord[cell])
    return z_e


def generate_num_points(cell):
    z_s = init_z_s(cell)
    z_e = init_z_e(cell)
    num_points = 0
    while z_s <= z_e:
        z_s += args.delta
        num_points += 2
    return num_points


def generate_x_b(cell):
    """
    Pattern:
    0, 0, Xb, Xb, 0, 0, Xb, Xb
    """
    x_b_coord = []
    x_b = init_x_b(cell)
    num_points = generate_num_points(cell)
    for n in range(num_points):
        x = (x_b) * (
            0.5 * (1+math.cos((n*math.pi)/2) - math.sin((n*math.pi)/2))
        )
        x = round(x, 1)
        x_b_coord.append(x)
    return x_b_coord


def generate_x_t(cell):
    """
    Pattern:
    Xt, Xt, 0, 0, Xt, Xt, 0, 0
    """
    x_t_coord = []
    x_t = init_x_t(cell)
    num_points = generate_num_points(cell)
    for n in range(num_points):
        x = (x_t) * (
            0.5 * (1-math.cos((n*math.pi)/2) + math.sin((n*math.pi)/2))
        )
        x = round(x, 1)
        x_t_coord.append(x)
    return x_t_coord


def generate_x(cell):
    """
    Pattern:
    Xb, Xb, Xt, Xt, Xb, Xb, Xt, Xt
    """
    final_x_coord = []
    x_b = generate_x_b(cell)
    x_t = generate_x_t(cell)
    for n in range(len(x_b)):
        if x_b[n] != 0:  # problem if x-coordinate == 0
            x = x_b[n]
        elif x_t[n] != 0:
            x = x_t[n]
        final_x_coord.append(x)
    res = ", ".join(repr(e) for e in final_x_coord)
    return res


def generate_z_s(cell, delta):
    """
    Pattern:
    Zs, Zs, Zs+delta, Zs+delta, ..., Zs + n*delta = Ze
    delta is the incremental change in eastern direction after each iteration
    """
    z_s_coord = []
    z_s = init_z_s(cell)
    z_e = init_z_e(cell)
    num_points = generate_num_points(cell)
    for n in range(num_points):
        z = (z_s) + delta * math.ceil(n / 2)
        z = min(z, z_e)  # used to prevent Z-values going out of bounds.
        z = round(z, 1)
        z_s_coord.append(z)
    res = ", ".join(repr(e) for e in z_s_coord)
    return res


# -----------------------------------------------
NUM_CELLS = len(x_b_coord) - 1
X_FILENAME = "x_waypoints.txt"
Z_FILENAME = "z_waypoints.txt"

ap = argparse.ArgumentParser()
ap.add_argument("delta", type=float, default=0.5, help="Side step")
args = ap.parse_args()

with open(Z_FILENAME, "w") as zf:
    for i in range(NUM_CELLS):
        cell_idx = i + 1
        ROWS = generate_z_s(cell_idx, args.delta)
        zf.write(ROWS)
        zf.write("\n")

with open(X_FILENAME, "w") as xf:
    for n in range(NUM_CELLS):
        cell_idx = n + 1
        ROWS = generate_x(cell_idx)
        xf.write(ROWS)
        xf.write("\n")
print("Waypoints Created!")
