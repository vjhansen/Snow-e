# based on:
# https://github.com/samialperen/boustrophedon_cellular_decomposition
#-----------------------------------------------
# Apply Boustrophedon Cellular Decomposition to a map
# Engineer(s): V. J. Hansen
# Version 0.4.0
# Data: 12.05.2020

#-----------------------------------------------
from matplotlib import pyplot as plt
import bcd  # Boustrophedon Cellular decomposition
import cv2, csv
import numpy as np
#-----------------------------------------------
"""
    Input: cells_to_visit --> the order of cells to visit
    Input: cell_boundaries --> y-coordinates of each cell
        x-coordinates will be calculated in this function based on cell number
        since first cell starts from the left and moves towards right
    Input: Nonneighbors --> This shows cells which are separated by the objects, so these cells should have the same x-coordinates.
"""
def calculate_x_coordinates(x_size, y_size, cells_to_visit, cell_boundaries, nonneighbors):
    total_cell_number = len(cells_to_visit)
    # Find the total length of the axises
    size_x = x_size
    size_y = y_size
    # Calculate x-coordinates of each cell
    cells_x_coordinates = {}
    width_accum_prev = 0
    cell_idx = 1
    while cell_idx <= total_cell_number:
        for subneighbor in nonneighbors:
            if subneighbor[0] == cell_idx: #current_cell, i.e. cell_idx is divided by the object(s)
                separated_cell_number = len(subneighbor) #contains how many cells are in the same vertical line
                width_current_cell = len(cell_boundaries[cell_idx])
                for j in range(separated_cell_number):
                    # All cells separated by the object(s) in this vertical line have same x coordinates
                    cells_x_coordinates[cell_idx+j] = list(range(width_accum_prev, width_current_cell+width_accum_prev))
                width_accum_prev += width_current_cell
                cell_idx = cell_idx + separated_cell_number
                break
        #current cell is not separated by any object(s)
        width_current_cell = len(cell_boundaries[cell_idx])
        cells_x_coordinates[cell_idx] = list(range(width_accum_prev, width_current_cell+width_accum_prev))
        width_accum_prev += width_current_cell
        cell_idx = cell_idx + 1
    return cells_x_coordinates # Output: cells_x_coordinates --> x-coordinates of each cell

#-----------------------------------------------
if __name__ == '__main__':
    # image: Export as -> Check Transparent Background and Selection Only -> Export
    original_map = bcd.cv2.imread("files/new_map.png")

    # We need binary image - 1's represents free space while 0's represents objects/walls
    if len(original_map.shape) > 2:
        print("Map image is converted to binary")
        single_channel_map = original_map[:, :, 0]
        _, binary_map = bcd.cv2.threshold(single_channel_map, 127, 1, bcd.cv2.THRESH_BINARY)

    # Call The Boustrophedon Cellular Decomposition function
    bcd_out_im, bcd_out_cells, cell_numbers, cell_boundaries, non_neighboor_cell_numbers = bcd.bcd(binary_map)
    # Show the decomposed cells on top of original map
    bcd.display_separate_map(bcd_out_im, bcd_out_cells)
    plt.show(block=False)

    # Add cost using distance between center of mass of cells
    def mean(input_list):
        output_mean = sum(input_list)/len(input_list)
        return output_mean

    def mean_double_list(input_double_list):
        length = len(input_double_list)
        total = 0
        for i in range(length):
            total += mean(input_double_list[i])
        output_mean = total/length
        return output_mean

    def mean_d_double_list(input_double_list):
        length = len(input_double_list)
        total = 0
        for i in range(length):
            total += mean(input_double_list[i][0])
        output_mean = total/length
        return output_mean
#-----------------------------------------------
    x_length = original_map.shape[1]
    y_length = original_map.shape[0]
    x_coordinates = calculate_x_coordinates(x_length, y_length, cell_numbers, cell_boundaries, non_neighboor_cell_numbers)
    y_coordinates = cell_boundaries
    mean_x_coordinates = {}
    mean_y_coordinates = {}

    # field names
    fields = ['Cell', 'Z_start', 'Z_end', 'X_start', 'X_end']

    # X is the length of the parking lot, which is 10 meters
    X_max = 5   # [m], these will be related to y_coordinates of image
    X_min = -5  # [m], these will be related to y_coordinates of image

    # Z is the width of the parking lot, which is 20 meters
    Z_max = 10   # [m], these will be related to x_coordinates of image
    Z_min = -10  # [m], these will be related to x_coordinates of image


    #gps = ((gps_max-gps_min)/(px_max-px_min))*(px-px_min)+gps_min

    # the values for Z will have to be divided into segments of equal size.
    filename = "files/BCD_coordinates.csv"
    # writing to csv file
    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)
        for i in range(len(x_coordinates)):
            # data rows of csv file   # first, middle and last y_coordinates are special (4D)
            cell_idx = i+1
            if ( (cell_idx == 1) | (cell_idx == len(x_coordinates)) | (cell_idx == ((len(x_coordinates)+1)/2)) ):
                rows = [[   cell_numbers[i],
                            ((Z_max-Z_min)/(x_length))*(x_coordinates[cell_idx][0])+Z_min,
                            ((Z_max-Z_min)/(x_length))*(x_coordinates[cell_idx][len(x_coordinates[cell_idx])-1])+Z_min,
                            ((X_max-X_min)/(y_length))*(y_coordinates[cell_idx][0][0][0])+X_min,
                            ((X_max-X_min)/(y_length))*(y_coordinates[cell_idx][0][0][1])+X_min ] ]
            elif ( (cell_idx != 1) | (cell_idx != len(x_coordinates)) ):
                rows = [ [  cell_numbers[i],
                            ((Z_max-Z_min)/(x_length))*(x_coordinates[cell_idx][0])+Z_min,
                            ((Z_max-Z_min)/(x_length))*(x_coordinates[cell_idx][len(x_coordinates[cell_idx])-1])+Z_min,
                            ((X_max-X_min)/(y_length))*(y_coordinates[cell_idx][0][0])+X_min,
                            ((X_max-X_min)/(y_length))*(y_coordinates[cell_idx][0][1])+X_min ] ]
            csvwriter.writerows(rows) # writing the data rows
    for i in range(len(x_coordinates)):
        cell_idx = i+1 #i starts from zero, but cell numbers start from 1
        mean_x_coordinates[cell_idx] = mean(x_coordinates[cell_idx])
        if type(y_coordinates[cell_idx][0]) is list:
            mean_y_coordinates[cell_idx] = mean_d_double_list(y_coordinates[cell_idx])
        else:
            mean_y_coordinates[cell_idx] = mean_double_list(y_coordinates[cell_idx])
    plt.waitforbuttonpress(1)
    input("Press any key to close all figures.")
    plt.close("all")
