#!/usr/bin/python
#
# Copyright 2018 BIG VISION LLC ALL RIGHTS RESERVED
# 

#https://github.com/spmallick/learnopencv/blob/master/MultiObjectTracker/multiTracker.py
#https://learnopencv.com/multitracker-multiple-object-tracking-using-opencv-c-python/

# need to use .legacy for creating the trackers in createTrackerByName
#https://stackoverflow.com/questions/65967096/multi-object-tracking-expected-ptrcvlegacytracker-for-argument-newtrack

from __future__ import print_function
import matplotlib.pyplot as plt
from random import randint
import pandas as pd
import numpy as np
import time
import sys
import cv2



trackerTypes = ['BOOSTING',   'MIL',    'KCF',   'TLD', 
                'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']

def createTrackerByName(trackerType):
# Create a tracker based on tracker name
    if trackerType == trackerTypes[0]:
        tracker = cv2.legacy.TrackerBoosting_create()
    elif trackerType == trackerTypes[1]: 
        tracker = cv2.legacy.TrackerMIL_create()
    elif trackerType == trackerTypes[2]:
        tracker = cv2.legacy.TrackerKCF_create()
    elif trackerType == trackerTypes[3]:
        tracker = cv2.legacy.TrackerTLD_create()
    elif trackerType == trackerTypes[4]:
        tracker = cv2.legacy.TrackerMedianFlow_create()
    elif trackerType == trackerTypes[5]:
        tracker = cv2.legacy.TrackerGOTURN_create()
    elif trackerType == trackerTypes[6]:
        tracker = cv2.legacy.TrackerMOSSE_create()
    elif trackerType == trackerTypes[7]:
        tracker = cv2.legacy.TrackerCSRT_create()
    else:
        tracker = None
        print('Incorrect tracker name')
        print('Available trackers are:')
        for t in trackerTypes:
            print(t)
    
    return tracker

if __name__ == '__main__':

  #print("Default tracking algoritm is CSRT \n"
  #      "Available tracking algorithms are:\n")
  #for t in trackerTypes:
  #    print(t)      

    trackerType = "CSRT" # i tried KCF but it threw the points into the
                         # top left corner frequently

  # Set video to load
    videoPath = "slow_traffic_small.mp4"#"videos/chaplin.mp4"
  
  # Create a video capture object to read videos
    cap = cv2.VideoCapture(0)#videoPath)
 
  # Read first frame
    success, frame = cap.read()
  # quit if unable to read the video file
    if not success:
        print('Failed to read video')
        sys.exit(1)

  ## Select boxes
    bboxes = []
    colors = [] 

    ## Save the first frame for plotting later on!
    cv2.imwrite("firstframe.jpg", frame)


  # Alert user to set the scene, as the objects must be selected from first frame
    print("3s to selection, get ready!")
    time.sleep(3.0)

  # OpenCV's selectROI function doesn't work for selecting multiple objects in Python
  # So we will call this function in a loop till we are done selecting all objects
while True:
    # draw bounding boxes over objects
    # selectROI's default behaviour is to draw box starting from the center
    # when fromCenter is set to false, you can draw box starting from top left corner
    bbox = cv2.selectROI('MultiTracker', frame)
    bboxes.append(bbox)
    colors.append((randint(64, 255), randint(64, 255), randint(64, 255)))
    print("Press q to quit selecting boxes and start tracking")
    print("Press any other key to select next object")
    k = cv2.waitKey(0) & 0xFF
    if (k == 113):  # q is pressed
        break
  
    print('Selected bounding boxes {}'.format(bboxes))

  ## Initialize MultiTracker
  # There are two ways you can initialize multitracker
  # 1. tracker = cv2.MultiTracker("CSRT")
  # All the trackers added to this multitracker
  # will use CSRT algorithm as default
  # 2. tracker = cv2.MultiTracker()
  # No default algorithm specified

  # Initialize MultiTracker with tracking algo
  # Specify tracker type
  
  # Create MultiTracker object
    multiTracker = cv2.legacy.MultiTracker_create()

  # Initialize MultiTracker 
    for bbox in bboxes:
        a = createTrackerByName(trackerType)
        multiTracker.add(a, frame, bbox)#createTrackerByName(trackerType), frame, bbox)

    # Create containers for final coordinate data
xss = []
yss = []
xs  = []
ys  = []


  # Process video and track objects
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break
    
    # get updated location of objects in subsequent frames
    success, boxes = multiTracker.update(frame)

    # draw tracked objects
    ## --> draw point: https://stackoverflow.com/questions/49799057/how-to-draw-a-point-in-an-image-using-given-co-ordinate-with-python-opencv

    for i, newbox in enumerate(boxes):
      #print("i:", i)
        p1 = (int(newbox[0]), int(newbox[1]))
        p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
        #cv2.rectangle(frame, p1, p2, colors[i], 2, 1)
      
        x = int((p1[0] + p2[0]) / 2)
        y = int((p1[1] + p2[1]) / 2)
        cv2.circle(frame, (x,y), radius=6, color=colors[i], thickness=-1)
        #print("x", x, "- type x:", type(x))
        #print("y", y, "- type y:", type(y))

    # save coordinates into lists
        xs.append(x)
        ys.append(y)

    #cv2.line()
    
    xss.append(xs)
    yss.append(ys)
    xs = []
    ys = []
    # show frame
    cv2.imshow('MultiTracker', frame)


    # quit on ESC button
    if cv2.waitKey(1) & 0xFF == 27:  # Esc pressed
        break


  ## Format into arrays and save the data
  ### --> NEED TO MAKE THIS FORMAT MORE CONVIENENT, ZIP THE VALUES
nxss = np.array(xss)
nyss = np.array(yss)

#for i in range(len(nxss[0])):
#    if i == 0:
#        coords[:,i] = nxss[:,i]
#    else:
#        coords[:,i+i] = nxss[:,i]

#for i in range(0, len(nxss[0])*2, 2):
#    coords[:,i] = nxss[:,i]

coords = np.zeros(shape=(len(nxss), len(nxss[0])*2))

coords[:,0::2] = nxss
coords[:,1::2] = nyss

#np.savetxt("nxss.csv", nxss, fmt="%d", delimiter=",")
#np.savetxt("nyss.csv", nyss, fmt="%d", delimiter=",")

#np.savetxt("coords1.csv", coords, fmt="%d", delimiter=",")

#df = pd.DataFrame(xs, columns=["x", "y"])


## Plot the tracked points
im = plt.imread("firstframe.jpg")
implot = plt.imshow(im)
ax = plt.plot(coords[:,0::2], coords[:,1::2])
plt.xlabel("X", fontsize=15)
plt.ylabel("Y", fontsize=15)
plt.title("Path of tracked points overlaid on first frame", fontsize=15)
plt.tight_layout()
plt.show()

