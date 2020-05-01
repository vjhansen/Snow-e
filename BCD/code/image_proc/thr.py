# based on:
#   https://github.com/opencv/opencv/blob/3.4/samples/python/tutorial_code/ShapeDescriptors/bounding_rects_circles/

# run: python3 thr.py --input sim_lot.png 

from __future__ import print_function
import cv2 as cv
import numpy as np
import argparse
import random as rng

rng.seed(12345)

def thresh_callback(val):
    threshold = val

    # Detect edges using Canny
    canny_output = cv.Canny(src_gray, threshold, threshold * 2)

    # Find contours
    contours, _ = cv.findContours(canny_output, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # Approximate contours to polygons + get bounding rects and circles
    contours_poly = [None]*len(contours)
    boundRect = [None]*len(contours)
    centers = [None]*len(contours)
   
    for i, c in enumerate(contours):
        contours_poly[i] = cv.approxPolyDP(c, 3, True)
        boundRect[i] = cv.boundingRect(contours_poly[i])
       

    drawing = np.zeros((canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)

    # Draw polygonal contour + bonding rects + circles
    for i in range(len(contours)):
        color = (rng.randint(0,256), rng.randint(0,256), rng.randint(0,256))
        #cv.drawContours(drawing, contours_poly, i, color)
        cv.rectangle(drawing, (int(boundRect[i][0]), int(boundRect[i][1])), \
          (int(boundRect[i][0]+boundRect[i][2]), int(boundRect[i][1]+boundRect[i][3])), color, -10)
    # Show in a window
    cv.imshow('Contours', drawing)

# Load source image
parser = argparse.ArgumentParser(description='Code for Creating Bounding boxes and circles for contours tutorial.')
parser.add_argument('--input', help='Path to input image.', default='stuff.jpg')
args = parser.parse_args()

src = cv.imread(cv.samples.findFile(args.input))

if src is None:
    print('Could not open or find the image:', args.input)
    exit(0)

# Convert image to gray and blur it
src_gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
#src_gray = cv.threshold(src,127,255,cv.THRESH_BINARY)
# Create Window
source_window = 'Source'
cv.namedWindow(source_window)
cv.imshow(source_window, src)
max_thresh = 255
thresh = 100 # initial threshold
cv.createTrackbar('Canny thresh:', source_window, thresh, max_thresh, thresh_callback)
thresh_callback(thresh)

cv.waitKey()