# - Create binary map from image
## python3 image_to_binary_map.py --image sim_lot.png

'''
Based on:
    https://stackoverflow.com/questions/50234485/drawing-rectangle-in-opencv-python/50235566
    https://stackoverflow.com/questions/50368683/set-white-color-outside-boundingbox-python-opencv
'''
# Engineer(s): V. J. Hansen
# Version: 1.4
# Date: 26.05.2020

import cv2, argparse, os
import numpy as np

# - initialize the list of reference point
ref_point = []

def shape_selection(event, x, y, flags, param):
    # grab references to the global variables
    global ref_point, crop

    # left mouse button clicked, record the starting (x, y)-coordinates and indicate that cropping is being performed
    if event == cv2.EVENT_LBUTTONDOWN:
        ref_point = [(x, y)]

    # left mouse button released
    elif event == cv2.EVENT_LBUTTONUP:
        # record the ending (x, y)-coordinates and indicate that the cropping operation is finished
        ref_point.append((x, y))
        # draw a rectangle around the region of interest (roi)
        x1, y1 = ref_point[0]
        x2, y2 = ref_point[1]
        roi = image[y1:y2, x1:x2]
        cv2.rectangle(image, ref_point[0], ref_point[1], (0, 0, 0), -10)
        white_bg[y1:y2, x1:x2] = roi
        cv2.imshow("image", image)

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="Path to the image")
args = vars(ap.parse_args())

# load image, clone it, and initialize mouse callback function
image = cv2.imread(args["image"])
white_bg = 255*np.ones_like(image)
clone = image.copy()
clonew_bg = white_bg.copy()
cv2.namedWindow("image", cv2.WINDOW_NORMAL)
cv2.setMouseCallback("image", shape_selection)
cwd = os.getcwd()
print("Drag a rectangle to cover the obstacle(s)")
print("Press 'r' to reset")
print("Press 'v' to view binary map")
print("Press 'q' to save image and quit")

# keep looping until 'q' is pressed
while True:
    # display image and wait for a keypress
    cv2.imshow("image", image)
    key = cv2.waitKey(1) & 0xFF

    # press 'r' to reset the window
    if key == ord("r"):
        image = clone.copy()
        white_bg = clonew_bg.copy()
    # press 'v' to view binary map
    if key == ord("v"):
        cv2.namedWindow("binary map", cv2.WINDOW_NORMAL)
        cv2.imshow('binary map', white_bg)
    # press 'q' to quit
    elif key == ord("q"):
        resized_img = cv2.resize(white_bg, (251, 221)) # resize image
        # add black border to resized image (the border is needed for the BCD to set the boundary of our area)
        bordersize = 1
        border = cv2.copyMakeBorder(
                        resized_img,
                        top = bordersize,
                        bottom = bordersize,
                        left = bordersize,
                        right = bordersize,
                        borderType = cv2.BORDER_CONSTANT,
                        value = [0,0,0] # black color
        )
        cv2.imwrite("new_map.png", border)
        print('Successfully saved')
        # could launch main_BCD.py from here
        break
cv2.destroyAllWindows()
