'''
Generate waypoints for coverage path planning
    from Boustrophedon Cellular Decomposition (BCD)
'''
# Snow-e
# Engineer(s): V. J. Hansen
# 28.05.2020
# V 1.4.1

#-----------------------------------------------
import math, csv
import numpy as np
import argparse

with open('BCD_coordinates.csv') as csvread_file:
    readCSV = csv.reader(csvread_file, delimiter=',')
    X_b_coord = []
    X_t_coord = []
    z_s_coord = []
    z_e_coord = []
    for row in readCSV:
        z_start = row[1]
        z_end   = row[2]
        X_start = row[3]
        X_end   = row[4]
        z_s_coord.append(z_start)
        z_e_coord.append(z_end)
        X_b_coord.append(X_start)
        X_t_coord.append(X_end)

def init_X_b(cell):
    X_b = float(X_b_coord[cell])
    return X_b

def init_X_t(cell):
    X_t = float(X_t_coord[cell])
    return X_t

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
    while (z_s <= z_e):
        z_s += args.delta
        num_points += 2
    return num_points

# Pattern:
# 0, 0, Xb, Xb, 0, 0, Xb, Xb
def generate_X_b(cell):
    X_b_coord = []
    X_b = init_X_b(cell)
    num_points = generate_num_points(cell)
    for n in range(num_points):
        x = (X_b) * (0.5 * (1 + math.cos((n*math.pi)/2) - math.sin((n*math.pi)/2)))
        x = round(x, 1)
        X_b_coord.append(x)
    return X_b_coord

# Pattern:
# Xt, Xt, 0, 0, Xt, Xt, 0, 0
def generate_X_t(cell):
    X_t_coord = []
    X_t = init_X_t(cell)
    num_points = generate_num_points(cell)
    for n in range(num_points):
        x = (X_t) * (0.5 * (1 - math.cos((n*math.pi)/2) + math.sin((n*math.pi)/2)))
        x = round(x, 1)
        X_t_coord.append(x)
    return X_t_coord

# Pattern:
# Xb, Xb, Xt, Xt, Xb, Xb, Xt, Xt
def generate_X(cell):
    final_x_coord = []
    X_b = generate_X_b(cell)
    X_t = generate_X_t(cell)
    for n in range(len(X_b)):
        if (X_b[n] != 0): # problem if x-coordinate == 0
            x = X_b[n]
        elif (X_t[n] != 0):
            x = X_t[n]
        final_x_coord.append(x)
    res = ", ".join(repr(e) for e in final_x_coord)
    return res

# Pattern:
# Zs, Zs, Zs+delta, Zs+delta, Zs+2*delta, Zs+2*delta, ..., Zs + n*delta = Ze
# delta is the incremental change in eastern direction after each iteration
def generate_z_s(cell, delta):
    z_s_coord = []
    z_s = init_z_s(cell)
    z_e = init_z_e(cell)
    num_points = generate_num_points(cell)
    for n in range (num_points):
        z = (z_s) + delta*math.ceil(n/2)
        if (z >= z_e): # used to prevent Z-values going out of bounds because of delta.
            z = z_e
        z = round(z, 1)
        z_s_coord.append(z)
    res = ", ".join(repr(e) for e in z_s_coord)
    return res
#-----------------------------------------------
num_cells = len(X_b_coord)-1
x_filename = "x_waypoints.txt"
z_filename = "z_waypoints.txt"

ap = argparse.ArgumentParser()
ap.add_argument('delta', type=float, default=0.5, help="Side step")
args = ap.parse_args()

with open(z_filename, 'w') as zf:
    for i in range(num_cells):
        cell_idx = i+1
        rows = generate_z_s(cell_idx, args.delta)
        zf.write(rows)
        zf.write("\n")

with open(x_filename, 'w') as xf:
    for n in range(num_cells):
        cell_idx = n+1
        rows = generate_X(cell_idx)
        xf.write(rows)
        xf.write("\n")
print("Waypoints Created!")
