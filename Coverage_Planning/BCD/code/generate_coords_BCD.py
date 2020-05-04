## generate waypoints for coverage path planning from Boustrophedon Cellular Decomposition

# Snow-e
# Engineer: V. J. Hansen
# 04.05.2020

import math
import csv

with open('coordinates.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    x_s_coord = []
    x_e_coord = []
    z_s_coord = []
    z_e_coord = []
    for row in readCSV:
        z_start = row[5]
        z_end = row[6]
        x_start = row[7]
        x_end = row[8]
        z_s_coord.append(z_start)
        z_e_coord.append(z_end)
        x_s_coord.append(x_start)
        x_e_coord.append(x_end)

#print(z_s_coord[0],z_s_coord[1],z_s_coord[2],z_s_coord[3],z_s_coord[4])
#print(z_e_coord[0],z_e_coord[1],z_e_coord[2],z_e_coord[3],z_e_coord[4])

#print(x_s_coord[0],x_s_coord[1],x_s_coord[2],x_s_coord[3],x_s_coord[4])
#print(x_e_coord[0],x_e_coord[1],x_e_coord[2],x_e_coord[3],x_e_coord[4])


size_x = abs(float(x_e_coord[2])-float(x_s_coord[2])) # height
size_z = abs(float(z_s_coord[2])-float(z_e_coord[2])) # width
print(size_x)
print(size_z)
#size_x = 10  
#size_z = 20  
delta = 0.5


# Pattern:
# Xs, Xs, Xe, Xe, Xs, Xs, Xe, Xe

def generate_x(num_points):
    x_coord = []
    for n in range(num_points):
        x = (-size_x/2.0) * ((1 + 3*n + n**2 + 2*(n**3)) - 4*(math.floor(0.25 * (2 + 3*n + (n**2) + 2*(n**3)))))
        x_coord.append(x)
    return x_coord


# Pattern:
# Zs, Zs, Zs+delta, Zs+delta, Zs+2*delta, Zs+2*delta, ..., Zs + n*delta = Ze

def generate_z(num_points):
    z_coord = []
    for n in range (num_points):
        z = (-size_z/2.0) + delta*math.ceil(n/2)
        z_coord.append(z)
    return z_coord

target_points = 4*(int(size_z)) # same as 2*(size_z//delta=0.5)
a = generate_x(target_points)
b = generate_z(target_points)

print(a)
print(b)