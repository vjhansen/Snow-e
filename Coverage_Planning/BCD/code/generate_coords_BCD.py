## generate waypoints for coverage path planning from Boustrophedon Cellular Decomposition

# Snow-e
# Engineer: V. J. Hansen
# 07.05.2020
# V 0.7

#-----------------------------------------------
import math, csv
import numpy as np

with open('BCD_coordinates.csv') as csvread_file:
    readCSV = csv.reader(csvread_file, delimiter=',')
    x_s_coord = []
    x_e_coord = []
    z_s_coord = []
    z_e_coord = []
    for row in readCSV:
        z_start = row[5]
        z_end   = row[6]
        x_start = row[7]
        x_end   = row[8]
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
# Xs, Xs, Xe, Xe, Xs, Xs, Xe, Xe
def generate_x_s(cell):
    x_s_coord = []
    x_s = init_x_s(cell)
    num_points = 4*(int((float(z_e_coord[cell])-float(z_s_coord[cell]))))
    for n in range(num_points):
        x = (x_s) * (0.5 * (1 + math.cos((n*math.pi)/2) - math.sin((n*math.pi)/2)))
        x = round(x, 1)
        x_s_coord.append(x)
    return x_s_coord

def generate_x_e(cell):
    x_e_coord = []
    x_e = init_x_e(cell)
    num_points = 4*(int((float(z_e_coord[cell])-float(z_s_coord[cell]))))
    for n in range(num_points):
        x = (x_e) * (0.5 * (1 - math.cos((n*math.pi)/2) + math.sin((n*math.pi)/2)))
        x = round(x, 1)
        x_e_coord.append(x)
    return x_e_coord


# Pattern:
# Zs, Zs, Zs+delta, Zs+delta, Zs+2*delta, Zs+2*delta, ..., Zs + n*delta = Ze
# delta is the incremental change in eastern direction after each iteration,
def generate_z_s(cell, delta):
    z_s_coord = []
    z_s = z_s_p = init_z_s(cell)
    z_e = init_z_e(cell)
    num_points = 0
    while z_s_p < z_e:
        z_s_p += delta
        num_points += 2
    for n in range (num_points-1): # (num_points-1) to ensure that the snow blower doesn't get too close to obstacles
        z = (z_s) + delta*math.ceil(n/2)
        z = round(z, 1)
        z_s_coord.append(z)
    return z_s_coord
#-----------------------------------------------

num_cells = len(x_s_coord)-1

fields = ['Cell', 'Z', 'X_start[m]', 'X_end[m]']  
filename = "waypoints.csv"

with open(filename, 'w') as csvwrite_file:
    csvwriter = csv.writer(csvwrite_file)
    csvwriter.writerow(fields)
    for x in range(num_cells):
        cell_idx = x+1
        rows = [[cell_idx, generate_z_s(cell_idx, 0.5), generate_x_s(cell_idx), generate_x_e(cell_idx)]]
        csvwriter.writerows(rows)
