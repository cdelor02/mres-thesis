
import numpy as np
import cv2 as cv
import argparse

# get marker number from command line arg
parser = argparse.ArgumentParser(description='Script for creating ArUco tracking markers')
parser.add_argument('id', type=int, help='Marker ID (integer)')
args       = parser.parse_args()
id   = args.id

# load predefined dictionary
dictionary = cv.aruco.Dictionary_get(0)

# generate marker
PIXEL_SIZE = 500
MARKER_ID = id
markerImage = np.zeros((PIXEL_SIZE, PIXEL_SIZE), dtype=np.uint8)
markerImage = cv.aruco.drawMarker(dictionary, MARKER_ID, PIXEL_SIZE, markerImage, 1);
cv.imwrite("marker{}.png".format(MARKER_ID), markerImage);


