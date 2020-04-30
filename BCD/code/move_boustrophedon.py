from matplotlib import pyplot as plt
from random import randint


def calculate_x_coordinates(x_size, y_size, cells_to_visit, cell_boundaries, nonneighbors):
    """
        Input: cells_to_visit --> It contains the order of cells to visit
        Input: cell_boundaries --> It contains y coordinates of each cell
            x coordinates will be calculated in this function based on 
            cell number since first cell starts from the left and moves towards
            right
        Input: Nonneighbors --> This shows cels which are separated by the objects
                ,so these cells should have the same x coordinates!
        Output: cells_x_coordinates --> x coordinates of each cell
    """
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