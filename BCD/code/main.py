
# https://github.com/samialperen/boustrophedon_cellular_decomposition

import bcd  # The Boustrophedon Cellular decomposition
import dfs  # The Depth-first Search Algorithm
import bfs  # The Breadth First Search Algorithm
import move_boustrophedon # Uses output of bcd cells in order to move the robot
import cv2

if __name__ == '__main__':
    # Read the original data
    # image: Export as -> Check Transparent Background and Selection Only -> Export
    original_map = bcd.cv2.imread("../data/one.png")
    
    # Show the original data
    fig1 = move_boustrophedon.plt.figure()
    move_boustrophedon.plt.imshow(original_map)
    move_boustrophedon.plt.title("Original Map Image")
    
    # We need binary image
    # 1's represents free space while 0's represents objects/walls
    if len(original_map.shape) > 2:
        print("Map image is converted to binary")
        single_channel_map = original_map[:, :, 0]
        _, binary_map = bcd.cv2.threshold(single_channel_map, 127, 1, bcd.cv2.THRESH_BINARY)

    # Call The Boustrophedon Cellular Decomposition function
    bcd_out_im, bcd_out_cells, cell_numbers, cell_boundaries, non_neighboor_cell_numbers = bcd.bcd(binary_map)
    # Show the decomposed cells on top of original map
    bcd.display_separate_map(bcd_out_im, bcd_out_cells)
    move_boustrophedon.plt.show(block=False)

    ############ Add cost using distance between center of mass of cells
    # Small function to calculate mean --> no need to use numpy or statistics module
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
    x_coordinates = move_boustrophedon.calculate_x_coordinates(x_length, y_length, \
                    cell_numbers, cell_boundaries, non_neighboor_cell_numbers)
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
 
    # Just for convenience, show each plot at the same time at different plots
    move_boustrophedon.plt.waitforbuttonpress(1)
    input("Please press any key to close all figures.")
    move_boustrophedon.plt.close("all")
