#!/usr/bin/python
#
# Copyright 2018 BIG VISION LLC ALL RIGHTS RESERVED
# 

#https://github.com/spmallick/learnopencv/blob/master/MultiObjectTracker/multiTracker.py
#https://learnopencv.com/multitracker-multiple-object-tracking-using-opencv-c-python/

# need to use .legacy for creating the trackers in createTrackerByName
#https://stackoverflow.com/questions/65967096/multi-object-tracking-expected-ptrcvlegacytracker-for-argument-newtrack

# saving video
# https://stackoverflow.com/questions/30103077/what-is-the-codec-for-mp4-videos-in-python-opencv

from __future__ import print_function
import matplotlib.pyplot as plt
from datetime import datetime
from random import randint
import pandas as pd
import numpy as np
import argparse
import math
import time
import sys
import cv2
import os


# Some command line argument parsing for usability
parser = argparse.ArgumentParser(description='MRes project optical tracking \
                                              for actuator ground truth \
                                              measurements.')
parser.add_argument('image', type=str, help='path to image/video file, or 0 for live camera')
parser.add_argument('filename', type=str, help='file in which to save the new video')
args      = parser.parse_args()
image     = args.image
filename  = args.filename
directory = "./opencv_videos"

filename = filename[:-4] # remove filetype


trackerTypes = ['BOOSTING',   'MIL',    'KCF',   'TLD', 
                'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']

dist_btwn_joint_centres = 105.48     #11 / 25.4 # these are in inches,
                                     # I have to use pixels for now

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


## NOT SURE THIS BELONGS HERE 
# Calculate distance between two points
def calculateDistance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


if __name__ == '__main__':

  #print("Default tracking algoritm is CSRT \n"
  #      "Available tracking algorithms are:\n")
  #for t in trackerTypes:
  #    print(t)      

    trackerType = "CSRT" # i tried KCF but it threw the points into the
                         # top left corner frequently

  # Set video to load
    #videoPath = "slow_traffic_small.mp4"#"videos/chaplin.mp4"
    if image == '0':
        cap = cv2.VideoCapture(0)
    else:
        videoPath = directory + "/" + image#"./opencv_videos/" + image#r_and_b_markers_actuator_footage.mp4"#filetypetest_trimmed.mp4"
        cap = cv2.VideoCapture(videoPath)
  # Create a video capture object to read videos
    #if image == '0' or '1':
    #    cap = cv2.VideoCapture(int(image))#videoPath)
    #else:
    

    frame_width  = int(cap.get(3))
    frame_height = int(cap.get(4))

    # Define the codec and create VideoWriter object. The output is 'filename'.
    out = cv2.VideoWriter("tracked_" + filename + ".mp4",
                          cv2.VideoWriter_fourcc(*'mp4v'), #'M','J','P','G'), 
                          10, (frame_width, frame_height))



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
    print("Saving first frame as firstframe.jpg")
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

print(len(bboxes), "regions selected")

  # Process video and track objects
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break
    
    # UNCOMMENT IF YOU WANT TO SAVE JUST THE UNMODIFIED VIDEO
    out.write(frame)

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
        #cv2.circle(frame, (x,y), radius=6, color=colors[i], thickness=-1)
        cv2.rectangle(frame, (x-3,y+3), (x+3,y-3), colors[i], 2, 1)
        #print("x", x, "- type x:", type(x))
        #print("y", y, "- type y:", type(y))

    # save coordinates into lists
        xs.append(x)
        ys.append(y)
    
    # draw lines between each detected point
    #for i in range(len(ys) - 1):
    #    x0,y0 = xs[i], ys[i]
    #    x1,y1 = xs[i+1], ys[i+1]
    #    cv2.line(frame, (x0, y0), (x1, y1), color=colors[i], thickness=2)

    #    # find midpoint between each line
    #    d = calculateDistance(x0, y0, x1, y1)
    #    #print("Dist:", d, "pixels")
    #    if d == 0:
    #        print("BAD")
    #        exit(1)

        ## dist_btwn... SHOULD BE BIGGER CAUSE IT SHOULD BE IN PIXELS NOT MM
        #theta = math.asin(d / (dist_btwn_joint_centres))
        #print("d", d, "theta", theta)

    xss.append(xs)
    yss.append(ys)
    xs = []
    ys = []
    # show frame
    cv2.imshow('MultiTracker', frame)

    # UNCOMMENT IF YOU WANT TO SAVE VIDEO WITH CV drawing
    #out.write(frame)

    # quit on ESC button
    if cv2.waitKey(1) & 0xFF == 27:  # Esc pressed
        break

out.release()


## Get current date for concatenation to datafile (for bookkeeping)
today     = datetime.now()
todaydate = today.strftime("%Y-%m-%d")

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

incr = 0
savename = filename + "_points-" + todaydate
while os.path.exists(savename+".csv"):
    incr += 1

np.savetxt(savename + "_" + str(incr) + ".csv", coords, fmt="%d", delimiter=",")#, lineterminator='\n')

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
plt.savefig(savename + "firstframe_tracking.jpg", dpi=600)

#### ****issue with the plotting is that the Y axis starts at 0 from the 
#### top left, not the bottom left. so, i have to adjust it by the height
#### of the image (from above, get it like this: im.shape[0])
#### for example, to get correct value is z = im.shape[0] - desired height

#read in data
#df = pd.read_csv(csv_name)
#pts = pd.read_csv("../computer_vision/copper_actuator_test_fixed_points-2021-08-09_0.csv", 
#                      names=["X", "Y"])

### **Converting from regular opencv image scaling to a regular coordinate grid
#c = [30, d["Y"][0]]
#adj = d["X"] - c[0]
#opp = c[1] - d["Y"]
## can try plotting these to see how they compare to the plotting below
#plt.plot(adj, opp); plt.show()


## If you want to plot it in the unmodified form
#im = plt.imread("../computer_vision/firstframe.jpg")
#implot = plt.imshow(im)
#ax = plt.plot(d["X"], d["Y"])
#plt.xlabel("X", fontsize=15)
#plt.ylabel("Y", fontsize=15)
#plt.title("OpenCV tracking data", fontsize=15)
#plt.tight_layout()
#plt.show()


### computing right triangles from points
#valid_points = np.where(adj > 0)[0]
#valid_adj = adj[valid_points]
#valid_opp = opp[valid_points]
#thetas = np.arctan(valid_opp / valid_adj)
#    ##--> maybe used np.arctan2() instead?
#thetas = np.degrees(thetas)
#np.savetxt("copper_actuator_test_fixed-thetas-2021-08-09.csv", 
#           thetas, fmt="%1.3f", delimiter=",")



