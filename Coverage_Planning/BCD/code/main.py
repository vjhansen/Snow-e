# Apply Boustrophedon Cellular Decomposition to a map
# V. J. Hansen
# Version 0.1 - 01.05.2020

# need to extract waypoints from the generated cells.

# based on:
# https://github.com/samialperen/boustrophedon_cellular_decomposition
##################################################
from matplotlib import pyplot as plt
import bcd  # Boustrophedon Cellular decomposition 
import cv2

##################################################
# Depth-first Search Algorithm
def dfs(cleaned, graph, node):
    if node not in cleaned:
        cleaned.append(node)
        for neighbour in graph[node]:
            dfs(cleaned, graph, neighbour)

##################################################
# Breadth First Search Algorithm
# visits all the nodes of a graph (connected component) using BFS
def bfs(cleaned, graph, start):
    # keep track of nodes to be checked
    queue = [start]
    # keep looping until there are nodes still to be checked
    while queue:
        # pop shallowest node (first node) from queue
        node = queue.pop(0)
        if node not in cleaned:
            # add node to list of checked nodes
            cleaned.append(node)
            neighbours = graph[node]
            # add neighbours of node to queue
            for neighbour in neighbours:
                queue.append(neighbour)

##################################################
    """
        Input: cells_to_visit --> It contains the order of cells to visit
        Input: cell_boundaries --> It contains y coordinates of each cell
            x coordinates will be calculated in this function based on cell number 
            since first cell starts from the left and moves towards right
        Input: Nonneighbors --> This shows cels which are separated by the objects, so these cells should have the same x coordinates.
        Output: cells_x_coordinates --> x coordinates of each cell
    """
def calculate_x_coordinates(x_size, y_size, cells_to_visit, cell_boundaries, nonneighbors):
    total_cell_number = len(cells_to_visit)
    # Find the total length of the axises
    size_x = x_size
    size_y = y_size
    
    # Calculate x coordinates of each cell
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
    return cells_x_coordinates

##################################################
if __name__ == '__main__':
    # Read the original data
    # image: Export as -> Check Transparent Background and Selection Only -> Export
    original_map = bcd.cv2.imread("../data/map5.png")
    
    # Show the original data
    fig1 = plt.figure()
    plt.imshow(original_map)
    plt.title("Original Map Image")
    
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

    ############ Add cost using distance between center of mass of cells
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
    
    x_length = original_map.shape[1]
    y_length = original_map.shape[0]
    x_coordinates = calculate_x_coordinates(x_length, y_length, cell_numbers, cell_boundaries, non_neighboor_cell_numbers)
    y_coordinates = cell_boundaries
    mean_x_coordinates = {}
    mean_y_coordinates = {}

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
