"""
Create binary map from image
python3 image_to_binary_map.py --image sim_lot.png
"""


import argparse
import os
import cv2
import numpy as np

REF_POINT = []


def shape_selection(event, x_pos, y_pos):
    """
    Select obstacle
    """
    # - initialize the list of reference point
    global REF_POINT
    # left mouse button clicked, record the starting (x, y)-coordinates
    if event == cv2.EVENT_LBUTTONDOWN:
        REF_POINT = [(x_pos, y_pos)]

    # left mouse button released
    elif event == cv2.EVENT_LBUTTONUP:
        # record the ending (x, y)-coordinates
        REF_POINT.append((x_pos, y_pos))
        # draw a rectangle around the region of interest (roi)
        x_1, y_1 = REF_POINT[0]
        x_2, y_2 = REF_POINT[1]
        roi = image[y_1:y_2, x_1:x_2]
        cv2.rectangle(image, REF_POINT[0], REF_POINT[1], (0, 0, 0), -10)
        white_bg[y_1:y_2, x_1:x_2] = roi
        cv2.imshow("image", image)


ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="Path to the image")
args = vars(ap.parse_args())

# load image and white background
image = cv2.imread(args["image"])
white_bg = 255 * np.ones_like(image)

# clone image
clone = image.copy()
clonew_bg = white_bg.copy()
cv2.namedWindow("image", cv2.WINDOW_NORMAL)

# initialize mouse callback function
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
        cv2.imshow("binary map", white_bg)
    # press 'q' to quit
    elif key == ord("q"):
        resized_img = cv2.resize(white_bg, (251, 221))  # resize image
        # add black border to resized image
        # (the border is needed for the BCD to set the boundary of our area)
        BORDER_SZ = 1
        border = cv2.copyMakeBorder(
            resized_img,
            top=BORDER_SZ,
            bottom=BORDER_SZ,
            left=BORDER_SZ,
            right=BORDER_SZ,
            borderType=cv2.BORDER_CONSTANT,
            value=[0, 0, 0],  # black color
        )
        cv2.imwrite("new_map.png", border)
        print("Successfully saved")
        break
cv2.destroyAllWindows()
