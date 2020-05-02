# Create binary map from image

# V. J. Hansen
# 02.05.2020

# https://stackoverflow.com/questions/50234485/drawing-rectangle-in-opencv-python/50235566
# https://stackoverflow.com/questions/50368683/set-white-color-outside-boundingbox-python-opencv

## python3 image_to_binary_map.py --image sim_lot.png

import cv2
import argparse
import os
import numpy as np


# initialize the list of reference point
ref_point = []

def shape_selection(event, x, y, flags, param):
    # grab references to the global variables
    global ref_point, crop

    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being performed
    if event == cv2.EVENT_LBUTTONDOWN:
        ref_point = [(x, y)]

    # check to see if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP:
        # record the ending (x, y) coordinates and indicate that
        # the cropping operation is finished
        ref_point.append((x, y))

        # draw a rectangle around the region of interest
        x1, y1 = ref_point[0]
        x2, y2 = ref_point[1]
        roi = image[y1:y2, x1:x2]
        cv2.rectangle(image, ref_point[0], ref_point[1], (0, 0, 0), -10)
        white_bg[y1:y2, x1:x2] = roi
        cv2.imshow("image", image)

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="Path to the image")
args = vars(ap.parse_args())

# load the image, clone it, and setup the mouse callback function
image = cv2.imread(args["image"])
white_bg = 255*np.ones_like(image)
clone = image.copy()
cv2.namedWindow("image")
cv2.setMouseCallback("image", shape_selection)

cwd = os.getcwd()
print("Drag a rectangle to cover the obstacles")
print("Press 'r' to reset")
print("Press 'v' to view binary map")
print("Press 'q' to save image and quit")

# keep looping until the 'q' key is pressed
while True:
    # display the image and wait for a keypress
    cv2.imshow("image", image)
    
    key = cv2.waitKey(1) & 0xFF

    # press 'r' to reset the window
    if key == ord("r"):
        image = clone.copy()

    if key == ord("v"):
        cv2.imshow('binary map', white_bg)

    # press 'q' to quit
    elif key == ord("q"):
        resized_img = cv2.resize(white_bg, (251,221))
        bordersize = 1
        border = cv2.copyMakeBorder(
                        resized_img,
                        top=bordersize,
                        bottom=bordersize,
                        left=bordersize,
                        right=bordersize,
                        borderType=cv2.BORDER_CONSTANT,
                        value=[0,0,0] # black
        )
        cv2.imwrite("new_map.png", border)
        print('Successfully saved') 
        break
cv2.destroyAllWindows() 
