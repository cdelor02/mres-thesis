# contour tracking
# https://docs.opencv.org/3.4/da/d97/tutorial_threshold_inRange.html

from __future__ import print_function
import cv2
import argparse
import numpy as np
import imutils


## Read
#img = cv2.imread("firstframe.jpg")

### convert to hsv
#hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

### mask of green (36,25,25) ~ (86, 255,255)
## mask = cv2.inRange(hsv, (36, 25, 25), (86, 255,255))
#mask = cv2.inRange(hsv, (0, 140, 100), (180, 255,255)) # changed to red

### slice the green
#imask = mask > 0
#red = np.zeros_like(img, np.uint8)
#red[imask] = img[imask]

### save 
#cv2.imwrite("red.png", red)

#cv2.imshow("red", red)
#cv2.waitKey(0)


# Read image
#im = cv2.imread("firstimage.png", cv2.IMREAD_GRAYSCALE)
im = cv2.imread("imcap_187.jpg")

gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

blurred = cv2.GaussianBlur(gray, (5,5),0)

thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]

#    ## convert to hsv
hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)

#    ## mask of green (36,25,25) ~ (86, 255,255)
#    # mask = cv2.inRange(hsv, (36, 25, 25), (86, 255,255))
mask = cv2.inRange(hsv, (0, 175, 100), (180, 255,255)) # changed to red

#    ## slice the red
imask = mask > 0
red = np.zeros_like(im, np.uint8)
red[imask] = im[imask]

greyscale_red = cv2.cvtColor(red, cv2.COLOR_BGR2GRAY)

while True:
    #cv2.imshow("red", red)
    cv2.imshow("mask", mask)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cnts = cv2.findContours(greyscale_red, cv2.RETR_EXTERNAL, 1)
#                        cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)

# Traverse the contour set
for c in cnts:
    # Calculate the image moment of the contour area. In computer vision and image processing, image moments are usually used to characterize the shape of objects in an image. These moments capture the basic statistical properties of the shape, including the area of ​​the object, the center of mass (that is, the object's center (x, y) coordinates), direction, and other desired characteristics.
    M = cv2.moments(c)
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    # Draw contour and center on the image
    cv2.drawContours(im, [c], -1, (0, 255, 0), 2)
    cv2.circle(im, (cX, cY), 7, (255, 255, 255), -1)
    cv2.putText(im, "center", (cX - 20, cY - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    # Display image
    cv2.imshow("Image", im)
    cv2.waitKey(0)






####################################################################

# Set up the detector with default parameters.
#params = cv2.SimpleBlobDetector_Params()
## Change thresholds
#params.minThreshold = 10;    # the graylevel of images
#params.maxThreshold = 200;

#params.filterByColor = True
#params.blobColor = 255

## Filter by Area
#params.filterByArea = True
#params.minArea = 300

#detector = cv2.SimpleBlobDetector_create(params)

## Detect blobs
#keypoints = detector.detect(im)

##print(keypoints)

## Draw detected blobs as red circles.
## cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
##im_with_keypoints = cv2.drawKeypoints(im, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
#im_with_keypoints = cv2.drawKeypoints(im, 
#                                      keypoints, 
#                                      np.array([]), 
#                                     (0,0,255), 
#                                      cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

#cv2.imshow("Keypoints", im_with_keypoints)
#cv2.waitKey(0)




#################################################################

#cap = cv2.VideoCapture(0)#"./opencv_videos/eit_stepper_sync_test.mp4")

#while True:
#    _,frame = cap.read()

#    ## convert to hsv
#    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

#    ## mask of green (36,25,25) ~ (86, 255,255)
#    # mask = cv2.inRange(hsv, (36, 25, 25), (86, 255,255))
#    mask = cv2.inRange(hsv, (0, 175, 100), (180, 255,255)) # changed to red

#    ## slice the green
#    imask = mask > 0
#    red = np.zeros_like(frame, np.uint8)
#    red[imask] = frame[imask]
 
#    cv2.imshow("red", red)
#    if cv2.waitKey(1) & 0xFF == ord('q'):
#        break
    
#cap.release()
#cv2.destroyAllWindows()









#################################################################

#max_value = 255
#max_value_H = 360//2
#low_H = 0
#low_S = 0
#low_V = 0
#high_H = max_value_H
#high_S = max_value
#high_V = max_value
#window_capture_name = 'Video Capture'
#window_detection_name = 'Object Detection'
#low_H_name = 'Low H'
#low_S_name = 'Low S'
#low_V_name = 'Low V'
#high_H_name = 'High H'
#high_S_name = 'High S'
#high_V_name = 'High V'


#def on_low_H_thresh_trackbar(val):
#    global low_H
#    global high_H
#    low_H = val
#    low_H = min(high_H-1, low_H)
#    cv.setTrackbarPos(low_H_name, window_detection_name, low_H)

#def on_high_H_thresh_trackbar(val):
#    global low_H
#    global high_H
#    high_H = val
#    high_H = max(high_H, low_H+1)
#    cv.setTrackbarPos(high_H_name, window_detection_name, high_H)

#def on_low_S_thresh_trackbar(val):
#    global low_S
#    global high_S
#    low_S = val
#    low_S = min(high_S-1, low_S)
#    cv.setTrackbarPos(low_S_name, window_detection_name, low_S)

#def on_high_S_thresh_trackbar(val):
#    global low_S
#    global high_S
#    high_S = val
#    high_S = max(high_S, low_S+1)
#    cv.setTrackbarPos(high_S_name, window_detection_name, high_S)

#def on_low_V_thresh_trackbar(val):
#    global low_V
#    global high_V
#    low_V = val
#    low_V = min(high_V-1, low_V)
#    cv.setTrackbarPos(low_V_name, window_detection_name, low_V)

#def on_high_V_thresh_trackbar(val):
#    global low_V
#    global high_V
#    high_V = val
#    high_V = max(high_V, low_V+1)
#    cv.setTrackbarPos(high_V_name, window_detection_name, high_V)

#parser = argparse.ArgumentParser(description='Code for Thresholding Operations using inRange tutorial.')
#parser.add_argument('--camera', help='Camera divide number.', default=0, type=int)
#args = parser.parse_args()

#cap = cv.VideoCapture(args.camera)
#cv.namedWindow(window_capture_name)
#cv.namedWindow(window_detection_name)
#cv.createTrackbar(low_H_name, window_detection_name , low_H, max_value_H, on_low_H_thresh_trackbar)
#cv.createTrackbar(high_H_name, window_detection_name , high_H, max_value_H, on_high_H_thresh_trackbar)
#cv.createTrackbar(low_S_name, window_detection_name , low_S, max_value, on_low_S_thresh_trackbar)
#cv.createTrackbar(high_S_name, window_detection_name , high_S, max_value, on_high_S_thresh_trackbar)
#cv.createTrackbar(low_V_name, window_detection_name , low_V, max_value, on_low_V_thresh_trackbar)
#cv.createTrackbar(high_V_name, window_detection_name , high_V, max_value, on_high_V_thresh_trackbar)

#while True:
    
#    ret, frame = cap.read()
#    if frame is None:
#        break
#    frame_HSV = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
#    frame_threshold = cv.inRange(frame_HSV, (low_H, low_S, low_V), (high_H, high_S, high_V))
    
    
#    cv.imshow(window_capture_name, frame)
#    cv.imshow(window_detection_name, frame_threshold)
    
#    key = cv.waitKey(30)
#    if key == ord('q') or key == 27:
#        break
