## generate waypoints for coverage path planning from Boustrophedon Cellular Decomposition

# Snow-e
# Engineer: V. J. Hansen
# 03.05.2020

import math
import csv

size_x = 10  # height
size_z = 20  # width
delta = 0.5

num_points = 10

def generate_x(num_points):
    x = {}
    for n in range(num_points):
        x[n] = (-size_x/2.0) * ((1 + 3*n + n**2 + 2*(n**3)) - 4*(math.floor(0.25 * (2 + 3*n + (n**2) + 2*(n**3)))))
    return x


def generate_z(num_points):
    z = {}
    for n in range (num_points):
        z[n] = (-size_z/2.0) + delta*math.ceil(n/2)
    return z


target_points = 4*(size_z) # same as 2*(size_z//delta)
a = generate_x(target_points)
b = generate_z(target_points)


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

print(z_s_coord[0])
print(z_e_coord[0])


print(x_s_coord[0])
print(x_e_coord[0])
