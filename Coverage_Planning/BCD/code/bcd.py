# Boustrophedon Cellular Decomposition
#--------------------------
# based on:
# https://github.com/samialperen/boustrophedon_cellular_decomposition
#--------------------------
# Engineers(s) V. J. Hansen
# Version 0.1.3 - 07.05.2020
#--------------------------

import numpy as np
from matplotlib import pyplot as plt
from typing import Tuple, List
import random, itertools, cv2

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
    Args:       slice_left: left slice, slice_right: right slice
    Returns:    [L, R] Adjacency matrix. """
    adjacency_matrix = np.zeros( [len(parts_left), len(parts_right)] )
    for l, lparts in enumerate(parts_left):
        for r, rparts in enumerate(parts_right):
            if min(lparts[1], rparts[1]) - max(lparts[0], rparts[0]) > 0:
                adjacency_matrix[l, r] = 1
    return adjacency_matrix

#-------------------------------------
def remove_duplicates(in_list):
    """ This function removes duplicates in the input list, where
        input list is composed of unhashable elements
        Example:
            in_list = [[1,2],[1,2],[2,3]]
            output = remove_duplicates(in_list)
            output --> [[1,2].[2,3]] """
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
