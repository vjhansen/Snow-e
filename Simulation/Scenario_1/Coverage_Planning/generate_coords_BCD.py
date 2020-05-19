'''
Generate waypoints for coverage path planning
    from Boustrophedon Cellular Decomposition (BCD)
'''
# Snow-e
# Engineer(s): V. J. Hansen
# 17.05.2020
# V 1.1

#-----------------------------------------------
import math, csv
import numpy as np

with open('files/BCD_coordinates.csv') as csvread_file:
    readCSV = csv.reader(csvread_file, delimiter=',')
    x_s_coord = []
    x_e_coord = []
    z_s_coord = []
    z_e_coord = []
    for row in readCSV:
        z_start = row[1]
        z_end   = row[2]
        x_start = row[3]
        x_end   = row[4]
        z_s_coord.append(z_start)
        z_e_coord.append(z_end)
        x_s_coord.append(x_start)
        x_e_coord.append(x_end)


def init_x_s(cell):
    x_s = float(x_s_coord[cell])
    return x_s

def init_x_e(cell):
    x_e = float(x_e_coord[cell])
    return x_e

def init_z_s(cell):
    z_s = float(z_s_coord[cell])
    return z_s

def init_z_e(cell):
    z_e = float(z_e_coord[cell])
    return z_e

# Pattern:
# 0, 0, Xs, Xs, 0, 0, Xs, Xs
def generate_x_s(cell):
    x_s_coord = []
    x_s = init_x_s(cell)
    num_points = 5*(int((float(z_e_coord[cell])-float(z_s_coord[cell]))))
    for n in range(num_points):
        x = (x_s) * (0.5 * (1 + math.cos((n*math.pi)/2) - math.sin((n*math.pi)/2)))
        x = round(x, 1)
        x_s_coord.append(x)
    return x_s_coord

# Pattern:
# Xe, Xe, 0, 0, Xe, Xe, 0, 0
def generate_x_e(cell):
    x_e_coord = []
    x_e = init_x_e(cell)
    num_points = 5*(int((float(z_e_coord[cell])-float(z_s_coord[cell])))) # 5*20 = 100 points
    for n in range(num_points):
        x = (x_e) * (0.5 * (1 - math.cos((n*math.pi)/2) + math.sin((n*math.pi)/2)))
        x = round(x, 1)
        x_e_coord.append(x)
    return x_e_coord

# Pattern:
# Xs, Xs, Xe, Xe, Xs, Xs, Xe, Xe
def final_x(cell):
    final_x_coord = []
    x_s = generate_x_s(cell)
    x_e = generate_x_e(cell)
    for n in range(len(x_s)):
        if (x_s[n] != 0): # problem if x-coordinate == 0
            x = x_s[n]
        elif (x_e[n] != 0):
            x = x_e[n]
        final_x_coord.append(x)
    res = ", ".join(repr(e) for e in final_x_coord)
    return res

# Pattern:
# Zs, Zs, Zs+delta, Zs+delta, Zs+2*delta, Zs+2*delta, ..., Zs + n*delta = Ze
# delta is the incremental change in eastern direction after each iteration,
def generate_z_s(cell, delta):
    z_s_coord = []
    z_s = z_s_p = init_z_s(cell)
    z_e = init_z_e(cell)
    num_points = 0
    while (z_s_p <= z_e):
        z_s_p += delta
        num_points += 2
    for n in range (num_points): # (num_points-1) to ensure that the snow blower doesn't get too close to obstacles
        z = (z_s) + delta*math.ceil(n/2)
        z = round(z, 1)
        z_s_coord.append(z)
    res = ", ".join(repr(e) for e in z_s_coord)
    return res
#-----------------------------------------------

num_cells = len(x_s_coord)-1
x_filename = "files/x_waypoints.txt"
z_filename = "files/z_waypoints.txt"

with open(z_filename, 'w') as zf:
    for x in range(num_cells):
        cell_idx = x+1
        rows = generate_z_s(cell_idx, 0.3)
        zf.write(rows)
        zf.write("\n")

with open(x_filename, 'w') as xf:
    for n in range(num_cells):
        cell_idx = n+1
        rows = final_x(cell_idx)
        xf.write(rows)
        xf.write("\n")
print("Waypoints Created!")
