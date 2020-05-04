## generate waypoints for coverage path planning from Boustrophedon Cellular Decomposition

# Snow-e
# Engineer: V. J. Hansen
# 04.05.2020

import math
import csv
import numpy as np

with open('coordinates.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
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


# height
x_s = float(x_s_coord[3])
x_e = float(x_e_coord[3])

# width
z_s = float(z_s_coord[2])
z_e = float(z_e_coord[2])

delta = 0.5

# Pattern:
# Xs, Xs, Xe, Xe, Xs, Xs, Xe, Xe
def generate_x_s(num_points):
    x_s_coord = []
    for n in range(num_points):
        x = (x_s) * (0.5 * (1 + math.cos((n*math.pi)/2) - math.sin((n*math.pi)/2)))
        x_s_coord.append(x)
    return x_s_coord

def generate_x_e(num_points):
    x_e_coord = []
    for n in range(num_points):
        x = (x_e) * (0.5 * (1 - math.cos((n*math.pi)/2) + math.sin((n*math.pi)/2)))
        x_e_coord.append(x)
    return x_e_coord


# Pattern:
# Zs, Zs, Zs+delta, Zs+delta, Zs+2*delta, Zs+2*delta, ..., Zs + n*delta = Ze

def generate_z_s(num_points):
    z_s_coord = []
    for n in range (num_points):
        z = (z_s) + delta*math.ceil(n/2)
        z_s_coord.append(z)
    return z_s_coord


target_points = 4*(int((float(z_e_coord[1])-float(z_s_coord[1])))) # same as (size_z//delta=0.5)


######OK#########
z_points = 0
z_s_p = float(z_s_coord[2])
z_e_p = float(z_e_coord[2])
while z_s_p < z_e_p:
    z_s_p  += delta
    z_points += 2
###############


a = generate_x_s(target_points)
b = generate_x_e(target_points)
c = generate_z_s(z_points)

print(np.around(a,3))
print(np.around(b,3))
print(np.around(c,3))