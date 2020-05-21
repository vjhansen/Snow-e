# based on: https://github.com/samialperen/boustrophedon_cellular_decomposition
'''
    - Apply Boustrophedon Cellular Decomposition to a map
    - Engineer(s): V. J. Hansen
    - Version 0.9.5
    - Data: 21.05.2020
'''

from typing import Tuple, List
from matplotlib import pyplot as plt
import csv, os, random, itertools
import cv2
import argparse
import numpy as np
#-------------------------------------
Slice = List[Tuple[int, int]] # vertical line segment
#-------------------------------------
def calc_connectivity(slice: np.ndarray) -> Tuple[int, Slice]:
    """ Calculates the connectivity of a slice and returns the connected area of ​​the slice.
    Args:       slice: rows. A slice of map.
    Returns:    The connectivity number and connectivity parts.
                connectivity --> total number of connected parts """
    connectivity = last_data = 0
    open_part = False
    connective_parts = []
    for i, data in enumerate(slice):
        if (last_data == 0 and data == 1):
            open_part = True
            start_point = i
        elif (last_data == 1 and data == 0 and open_part):
            open_part = False
            connectivity += 1
            end_point = i
            connective_parts.append((start_point, end_point))
        last_data = data
    return connectivity, connective_parts
#-------------------------------------
def get_adjacency_matrix(parts_left: Slice, parts_right: Slice) -> np.ndarray:
    """ Get adjacency matrix of 2 neighborhood slices.
    Args: slice_left: left slice, slice_right: right slice """
    adjacency_matrix = np.zeros( [len(parts_left), len(parts_right)] )
    for l, lparts in enumerate(parts_left):
        for r, rparts in enumerate(parts_right):
            if (min(lparts[1], rparts[1]) - max(lparts[0], rparts[0]) > 0):
                adjacency_matrix[l, r] = 1
    return adjacency_matrix # - [L, R] Adjacency matrix.
#-------------------------------------
def remove_duplicates(in_list):
    """ This function removes duplicates in the input list, where input list is composed of unhashable elements """
    out_list = []
    in_list.sort()
    out_list = list(in_list for in_list, _ in itertools.groupby(in_list))
    return out_list
#------------------------------------
def bcd(erode_img: np.ndarray) -> Tuple[np.ndarray, int]:
    """ Boustrophedon Cellular Decomposition
    Args:   erode_img: [H, W], eroded map. pixel value 0 = obstacles, 1 = free space.
    Returns:
        [H, W], separated map.
        crrnt_cell and seperate_img is for display purposes --> which is used to show
        decomposed cells into a separate figure
        all_cell_nums --> contains all cell index numbers
        cell_bounds   --> contains all cell boundary coordinates (only y-coordinate)
        non_nbr_cells --> contains cell index numbers of non_nbr_cells, i.e. cells which are separated by obstacles
    """
    last_connectivity = 0
    last_connectivity_parts = crrnt_cells = non_nbr_cells = []
    crrnt_cell = 1
    separate_img = np.copy(erode_img)
    cell_bounds = {}
    for col in range(erode_img.shape[1]):
        crrnt_slice = erode_img[:, col]

        connectivity, connective_parts = calc_connectivity(crrnt_slice)
        if (last_connectivity == 0):
            crrnt_cells = []
            for i in range(connectivity): # - Slice intersects with the object for the first time
                crrnt_cells.append(crrnt_cell)
                crrnt_cell += 1     # - Creating different cells on the same column which are seperated by the objects
        elif (connectivity == 0):
            crrnt_cells = []
            continue
        else:
            adj_matrix = get_adjacency_matrix(last_connectivity_parts, connective_parts)
            new_cells = [0] * len(connective_parts)
            for i in range(adj_matrix.shape[0]):
                if (np.sum(adj_matrix[i, :]) == 1):
                    new_cells[np.argwhere(adj_matrix[i, :])[0][0]] = crrnt_cells[i]
                # - If a previous part is connected to multiple parts this time, it means that IN has occurred.
                elif (np.sum(adj_matrix[i, :]) > 1): # left slice is connected to more than one part of right slice
                    for idx in np.argwhere(adj_matrix[i, :]):
                        new_cells[idx[0]] = crrnt_cell
                        crrnt_cell = crrnt_cell+1
            for i in range(adj_matrix.shape[1]):
                # - If a part of this time is connected to the last multiple parts, it means that OUT has occurred.
                if (np.sum(adj_matrix[:, i]) > 1): # right slice is connected to more than one part of left slice
                    new_cells[i] = crrnt_cell
                    crrnt_cell = crrnt_cell+1
                # - If this part of the part does not communicate with any part of the last time, it means that it happened in
                elif (np.sum(adj_matrix[:, i]) == 0):
                    new_cells[i] = crrnt_cell
                    crrnt_cell = crrnt_cell+1
            crrnt_cells = new_cells

        # - Draw the partition information on the map.
        for cell, slice in zip(crrnt_cells, connective_parts):
            separate_img[slice[0]:slice[1], col] = cell
        last_connectivity = connectivity
        last_connectivity_parts = connective_parts
        if (len(crrnt_cells) == 1):     # - no object in this cell
            cell_index = crrnt_cell-1  # - cell index starts from 1
            cell_bounds.setdefault(cell_index,[])
            cell_bounds[cell_index].append(connective_parts)
        elif (len(crrnt_cells) > 1):    # - Cells separated by the object
            # - Cells separated by the objects are not neighbors to each other
            non_nbr_cells.append(crrnt_cells)
            # - non_nbr_cells will contain many duplicate values
            # we get rid of duplicates at the end in this logic, all other cells must be neighbors to each other
            # if their cell number are adjacent to each other, like cell 1 is neighbor to cell 2
            for i in range(len(crrnt_cells)):
                cell_index = crrnt_cells[i]
                # - connective_parts and crrnt_cells contain more than one cell which are separated by the object
                # - We are iterating with the loop to reach all cells
                cell_bounds.setdefault(cell_index,[])
                cell_bounds[cell_index].append(connective_parts[i])
    # - Cell 1 is the left most cell, and cell n is the right most cell, where n is the total cell number
    all_cell_nums = cell_bounds.keys()
    non_nbr_cells = remove_duplicates(non_nbr_cells)
    return separate_img, crrnt_cell, list(all_cell_nums), cell_bounds, non_nbr_cells
#-------------------------------------
def disp_separate_map(separate_map, cells):
    disp_img = np.empty([*separate_map.shape, 3], dtype=np.uint8)
    random_colors = np.random.randint(0, 255, [cells, 3])
    for cell_id in range(1, cells):
        disp_img[separate_map == cell_id, :] = random_colors[cell_id, :]
    fig_new = plt.figure()
    plt.imshow(disp_img)

""" Input: cells_to_visit   --> the order of cells to visit
    Input: cell_bounds      --> y-coordinates of each cell
        x-coordinates will be calculated in this function based on cell number, since the 1st cell starts from the left and moves towards the right.
    Input: Nonneighbors --> This shows cells which are separated by the objects,
                            so these cells should have the same x-coordinates.
"""
def calculate_x_coords(x_size, y_size, cells_to_visit, cell_bounds, non_nbrs):
    total_cell_number = len(cells_to_visit)
    # - Find the total length of the axises
    size_x = x_size
    size_y = y_size
    # - Calculate x-coordinates of each cell
    cells_x_coords = {}
    width_accum_prev = 0
    cell_idx = 1
    while (cell_idx <= total_cell_number):
        for sub_nbr in non_nbrs:
            if (sub_nbr[0] == cell_idx): # - crrnt_cell, i.e. cell_idx is divided by the object(s)
                separated_cell_number = len(sub_nbr) # - Contains how many cells are in the same vertical line
                width_crrnt_cell = len(cell_bounds[cell_idx])
                for j in range(separated_cell_number):
                    # - All cells separated by the object(s) in this vertical line have same x coordinates
                    cells_x_coords[cell_idx+j] = list(range(width_accum_prev, width_crrnt_cell+width_accum_prev))
                width_accum_prev += width_crrnt_cell
                cell_idx = cell_idx + separated_cell_number
                break
        # - Current cell is not separated by any object(s)
        width_crrnt_cell = len(cell_bounds[cell_idx])
        cells_x_coords[cell_idx] = list(range(width_accum_prev, width_crrnt_cell+width_accum_prev))
        width_accum_prev += width_crrnt_cell
        cell_idx = cell_idx + 1
    return cells_x_coords # - Output: x-coordinates of each cell

#-----------------------------------------------
if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", help="Path to the image")
    ap.add_argument('X', type=int, default=10, help="Height [m] of parking lot")
    ap.add_argument('Z', type=int, default=20, help="Width [m] of parking lot")
    ap.add_argument('delta', type=float, default=0.5, help="Side step [m]")
    args = ap.parse_args()

    original_map = cv2.imread(args.image)
    # - We need a binary image: 1 represents free space, 0 represents objects/walls
    if (len(original_map.shape) > 2):
        print("Map image is converted to binary")
        single_ch_map = original_map[:, :, 0]
        _, binary_map = cv2.threshold(single_ch_map, 127, 1, cv2.THRESH_BINARY)
    # - Call Boustrophedon Cellular Decomposition function
    bcd_out_im, bcd_out_cells, cell_nums, cell_bounds, non_nbr_cell_nums = bcd(binary_map)
    # - Show the decomposed cells on top of original map
    disp_separate_map(bcd_out_im, bcd_out_cells)
    plt.show(block=False)
    print("Cells: ", cell_nums)
    print("Non-neighbor cells: ", non_nbr_cell_nums)

#-----------------------------------------------
    x_length = original_map.shape[1]
    y_length = original_map.shape[0]
    x_coords = calculate_x_coords(x_length, y_length, cell_nums, cell_bounds, non_nbr_cell_nums)
    y_coords = cell_bounds

    # - X is the Height of the parking lot
    X_max = (args.X-0.1)/2   # [m], these will be related to y_coords of image
    X_min = (-args.X+0.1)/2  # [m], these will be related to y_coords of image

    # - Z is the width of the parking lot
    Z_max = (args.Z-0.1)/2   # [m], these will be related to x_coords of image
    Z_min = (-args.Z+0.1)/2 # [m], these will be related to x_coords of image
    # gps = ((gps_max-gps_min)/(px_max-px_min))*(px-px_min)+gps_min
    px_min = 1

    fields = ['Cell', 'Z_start', 'Z_end', 'X_start', 'X_end']
    filename = "BCD_coordinates.csv"
    # - Writing to .csv-file
    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)
        for i in range(len(x_coords)):
            # - data rows of csv file
            cell_idx = i+1
            # - first, middle and last y_coords are 4D
            if (len(x_coords) > 3):
                if ( (cell_idx == 1) | (cell_idx == len(x_coords)) | (cell_idx == ((len(x_coords)+1)/2)) ):
                    px_zs = x_coords[cell_idx][0]
                    px_ze = x_coords[cell_idx][-1]
                    px_xs = y_coords[cell_idx][0][0][1]
                    px_xe = y_coords[cell_idx][0][0][0]
                    rows = [[   cell_nums[i],
                                ((Z_max-Z_min)/(x_length-px_min)) * (px_zs-px_min)+Z_min,
                                ((Z_max-Z_min)/(x_length-px_min)) * (px_ze-px_min)+Z_min,
                                # - the y-axis is inverted, i.e. goes from y_length (bottom) to 0 (top)
                                ((X_max-X_min)/(px_min-y_length)) * (px_xs-px_min)+X_max,
                                ((X_max-X_min)/(px_min-y_length)) * (px_xe-px_min)+X_max ] ]
                elif ( (cell_idx != 1) | (cell_idx != len(x_coords)) ):
                    px_zs = x_coords[cell_idx][0]
                    px_ze = x_coords[cell_idx][-1]
                    px_xs = y_coords[cell_idx][0][1]
                    px_xe = y_coords[cell_idx][0][0]
                    rows = [ [  cell_nums[i],
                                ((Z_max-Z_min)/(x_length-px_min)) * (px_zs-px_min)+Z_min,
                                ((Z_max-Z_min)/(x_length-px_min)) * (px_ze-px_min)+Z_min,
                                ((X_max-X_min)/(px_min-y_length)) * (px_xs+px_min)+X_max,
                                ((X_max-X_min)/(px_min-y_length)) * (px_xe+px_min)+X_max ] ]
                csvwriter.writerows(rows)
            elif (len(x_coords) < 3):
                if ((cell_idx != len(x_coords))):
                    px_zs = x_coords[cell_idx][0]
                    px_ze = x_coords[cell_idx][-1]
                    px_xs = y_coords[cell_idx][0][1]
                    px_xe = y_coords[cell_idx][0][0]
                    rows = [[   cell_nums[i],
                                ((Z_max-Z_min)/(x_length-px_min)) * (px_zs-px_min)+Z_min,
                                ((Z_max-Z_min)/(x_length-px_min)) * (px_ze-px_min)+Z_min,
                                # - the y-axis is inverted, i.e. goes from y_length (bottom) to 0 (top)
                                ((X_max-X_min)/(px_min-y_length)) * (px_xs-px_min)+X_max,
                                ((X_max-X_min)/(px_min-y_length)) * (px_xe-px_min)+X_max ] ]
                else:
                    px_zs = x_coords[cell_idx][0]
                    px_ze = x_coords[cell_idx][-1]
                    px_xs = y_coords[cell_idx][0][0][1]
                    px_xe = y_coords[cell_idx][0][0][0]
                    rows = [[   cell_nums[i],
                                ((Z_max-Z_min)/(x_length-px_min)) * (px_zs-px_min)+Z_min,
                                ((Z_max-Z_min)/(x_length-px_min)) * (px_ze-px_min)+Z_min,
                                # - the y-axis is inverted, i.e. goes from y_length (bottom) to 0 (top)
                                ((X_max-X_min)/(px_min-y_length)) * (px_xs-px_min)+X_max,
                                ((X_max-X_min)/(px_min-y_length)) * (px_xe-px_min)+X_max ] ]
                csvwriter.writerows(rows)
    plt.waitforbuttonpress(1)
    input("Press any key to close all figures.")
    plt.close("all")
    os.system("python3 generate_coords_BCD.py "+ str(args.delta)) # run generate_coords_BCD.py
