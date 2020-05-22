# based on:
# https://github.com/samialperen/boustrophedon_cellular_decomposition
#-----------------------------------------------
# Apply Boustrophedon Cellular Decomposition to a map
# Engineer(s): V. J. Hansen
# Version 0.9.1
# Data: 14.05.2020

#-----------------------------------------------
from matplotlib import pyplot as plt
from typing import Tuple, List
import csv, os, random, itertools
import cv2
import numpy as np
#-----------------------------------------------

Slice = List[Tuple[int, int]]

#-------------------------------------
def calc_connectivity(slice: np.ndarray) -> Tuple[int, Slice]:
    """ Calculates the connectivity of a slice and returns the connected area of ​​the slice.
    Args:       slice: rows. A slice of map.

    Returns:    The connectivity number and connectivity parts.
                connectivity --> total number of connected parts """
    connectivity = 0
    last_data = 0
    open_part = False
    connective_parts = []
    for i, data in enumerate(slice):
        if last_data == 0 and data == 1:
            open_part = True
            start_point = i
        elif last_data == 1 and data == 0 and open_part:
            open_part = False
            connectivity += 1
            end_point = i
            connective_parts.append((start_point, end_point))
        last_data = data
    return connectivity, connective_parts

#-------------------------------------
def get_adjacency_matrix(parts_left: Slice, parts_right: Slice) -> np.ndarray:
    """ Get adjacency matrix of 2 neighborhood slices.
    Args:       slice_left: left slice, slice_right: right slice """
    adjacency_matrix = np.zeros( [len(parts_left), len(parts_right)] )
    for l, lparts in enumerate(parts_left):
        for r, rparts in enumerate(parts_right):
            if min(lparts[1], rparts[1]) - max(lparts[0], rparts[0]) > 0:
                adjacency_matrix[l, r] = 1
    return adjacency_matrix     # [L, R] Adjacency matrix.

#-------------------------------------
def remove_duplicates(in_list):
    """ This function removes duplicates in the input list, where
        input list is composed of unhashable elements """
    out_list = []
    in_list.sort()
    out_list = list(in_list for in_list, _ in itertools.groupby(in_list))
    return out_list

#-------------------------------------
def bcd(erode_img: np.ndarray) -> Tuple[np.ndarray, int]:
    """ Boustrophedon Cellular Decomposition
    Args:   erode_img: [H, W], eroded map. pixel value 0 represents obstacles, 1 = free space.
    Returns:
        [H, W], separated map. pixel value 0 represents obstacles for its cell number.
        current_cell and seperate_img is for display purposes --> which is used to show
        decomposed cells into a separate figure
        all_cell_numbers --> contains all cell index numbers
        cell_boundaries --> contains all cell boundary coordinates (only y coordinate)
        non_neighboor_cells --> contains cell index numbers of non_neighboor_cells, i.e.
        cells which are separated by the objects """
    last_connectivity = 0
    last_connectivity_parts = []
    current_cell = 1
    current_cells = []
    separate_img = np.copy(erode_img)
    cell_boundaries = {}
    non_neighboor_cells = []

    for col in range(erode_img.shape[1]):
        current_slice = erode_img[:, col]
        connectivity, connective_parts = calc_connectivity(current_slice)
        if last_connectivity == 0:
            current_cells = []
            for i in range(connectivity): #slice intersects with the object for the first time
                current_cells.append(current_cell)
                current_cell += 1 # we are creating different cells on the same column which are seperated by the objects
        elif connectivity == 0:
            current_cells = []
            continue
        else:
            adj_matrix = get_adjacency_matrix(last_connectivity_parts, connective_parts)
            new_cells = [0] * len(connective_parts)
            for i in range(adj_matrix.shape[0]):
                if np.sum(adj_matrix[i, :]) == 1:
                    new_cells[np.argwhere(adj_matrix[i, :])[0][0]] = current_cells[i]
                # If a previous part is connected to multiple parts this time, it means that IN has occurred.
                elif np.sum(adj_matrix[i, :]) > 1: #left slice is connected to more than one part of right slice
                    for idx in np.argwhere(adj_matrix[i, :]):
                        new_cells[idx[0]] = current_cell
                        current_cell = current_cell + 1
            for i in range(adj_matrix.shape[1]):
                # If a part of this time is connected to the last multiple parts, it means that OUT has occurred.
                if np.sum(adj_matrix[:, i]) > 1: #right slice is connected to more than one part of left slice
                    new_cells[i] = current_cell
                    current_cell = current_cell + 1
                # If this part of the part does not communicate with any part of the last time, it means that it happened in
                elif np.sum(adj_matrix[:, i]) == 0:
                    new_cells[i] = current_cell
                    current_cell = current_cell + 1
            current_cells = new_cells
        # Draw the partition information on the map.
        for cell, slice in zip(current_cells, connective_parts):
            separate_img[slice[0]:slice[1], col] = cell
        last_connectivity = connectivity
        last_connectivity_parts = connective_parts
        if len(current_cells) == 1: #no object in this cell
            cell_index = current_cell -1  # cell index starts from 1
            cell_boundaries.setdefault(cell_index,[])
            cell_boundaries[cell_index].append(connective_parts)
        elif len(current_cells) > 1: #cells separated by the object
            # cells separated by the objects are not neighbor to each other
            non_neighboor_cells.append(current_cells)
            # non_neighboor_cells will contain many duplicate values, but we
            # will get rid of duplicates at the end in this logic, all other cells must be neighboor to each other
            # if their cell number are adjacent to each other like cell1 is neighboor to cell2
            for i in range(len(current_cells)):
                cell_index = current_cells[i]
                # connective_parts and current_cells contain more than one
                # cell info which are separated by the object, so we are iterating
                # with the for loop to reach all the cells
                cell_boundaries.setdefault(cell_index,[])
                cell_boundaries[cell_index].append(connective_parts[i])
    # Cell 1 is the left most cell and cell n is the right most cell, where n is the total cell number
    all_cell_numbers = cell_boundaries.keys()
    non_neighboor_cells = remove_duplicates(non_neighboor_cells)
    return separate_img, current_cell, list(all_cell_numbers), cell_boundaries, non_neighboor_cells

#-------------------------------------
def display_separate_map(separate_map, cells):
    display_img = np.empty([*separate_map.shape, 3], dtype=np.uint8)
    random_colors = np.random.randint(0, 255, [cells, 3])
    for cell_id in range(1, cells):
        display_img[separate_map == cell_id, :] = random_colors[cell_id, :]
    fig_new = plt.figure()
    plt.imshow(display_img)

"""
    Input: cells_to_visit --> the order of cells to visit
    Input: cell_boundaries --> y-coordinates of each cell
        x-coordinates will be calculated in this function based on cell number
        since 1st cell starts from the left and moves towards right
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
    return cells_x_coordinates # Output: x-coordinates of each cell

#-----------------------------------------------
if __name__ == '__main__':
    original_map = cv2.imread("files/new_map.png")

    # We need a binary image - 1 represents free space, 0 represents objects/walls
    if len(original_map.shape) > 2:
        print("Map image is converted to binary")
        single_channel_map = original_map[:, :, 0]
        _, binary_map = cv2.threshold(single_channel_map, 127, 1, cv2.THRESH_BINARY)

    # Call Boustrophedon Cellular Decomposition function
    bcd_out_im, bcd_out_cells, cell_numbers, cell_boundaries, non_neighboor_cell_numbers = bcd(binary_map)
    # Show the decomposed cells on top of original map
    display_separate_map(bcd_out_im, bcd_out_cells)
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
    X_max = 4.5   # [m], these will be related to y_coordinates of image
    X_min = -4.5 # [m], these will be related to y_coordinates of image

    # Z is the width of the parking lot, which is 20 meters
    Z_max = 9.5   # [m], these will be related to x_coordinates of image
    Z_min = -9.5  # [m], these will be related to x_coordinates of image

    #gps = ((gps_max-gps_min)/(px_max-px_min))*(px-px_min)+gps_min

    # the values for Z will have to be divided into segments of equal size.
    filename = "files/BCD_coordinates.csv"
    # writing to csv file
    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)
        for i in range(len(x_coordinates)):
            # data rows of csv file   # first, middle and last y_coordinates are 4D
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
    os.system("python3 generate_coords_BCD.py")
