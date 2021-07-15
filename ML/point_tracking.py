# OpenCV script for soft robot actuator trained on EIT voltage data

#https://stackoverflow.com/questions/31460267/python-opencv-color-tracking
#https://www.pyimagesearch.com/2016/02/01/opencv-center-of-contour/
#https://learnopencv.com/find-center-of-blob-centroid-using-opencv-cpp-python/
#https://answers.opencv.org/question/223919/unable-to-find-and-draw-biggest-contour/

#measurement on object
#https://gist.github.com/benmarwick/2b250d8ef3dbe36f817fbe2bf14aaa55

# optical flow tutorial example
# https://docs.opencv.org/master/d4/dee/tutorial_optical_flow.html

import numpy as np
import argparse
import imutils
import time
import cv2
import sys

refPt = []

## Function for getting mouse click on OpenCV camera window
#click event function
# RETURNS A TUPLE ([np array], string)
def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        font  = cv2.FONT_HERSHEY_SIMPLEX
        strang = str(x) + ", " + str(y)
        cv2.putText(frame, strang, (x,y), font, 0.5, (255,255,0), 2)
        cv2.imshow("image", old_frame)

    if event == cv2.EVENT_RBUTTONDOWN:
        blue   = img[y, x, 0]
        green  = img[y, x, 1]
        red    = img[y, x, 2]
        font   = cv2.FONT_HERSHEY_SIMPLEX
        strang = str(blue) + ", " + str(green) + "," + str(red)
        cv2.putText(frame, strang, (x,y), font, 0.5, (0,255,255), 2)
        cv2.imshow("image", old_frame)

    #return np.array([x,y], dtype=np.float32), strang



# Some command line argument parsing for usability
parser = argparse.ArgumentParser(description='MRes project optical tracking \
                                              for actuator ground truth \
                                              measurements.')
parser.add_argument('image', type=str, help='path to image/video file, or [live] for live camera')
parser.add_argument('mode',  type=str, help='choose method: optical flow [optical] or contour thresholding [contour]')
args = parser.parse_args()
mode = args.mode

## Recording camera feed
#fourcc = cv2.VideoWriter_fourcc(*'MP4V')
#out = cv2.VideoWriter('output1' + '.mp4', fourcc, 20.0, (640,480))

# TODO: if external webcam available, use that
if args.image == 'live':
    cap = cv2.VideoCapture(0)
else:
    cap = cv2.VideoCapture(args.image)


if mode == 'optical':

    # params for ShiTomasi corner detection
    feature_params = dict( maxCorners   = 50,
                           qualityLevel = 0.3,
                           minDistance  = 7,
                           blockSize    = 7)

    # params for Lucas Kanade optical flow
    lk_params = dict( winSize  = (15, 15),
                      maxLevel = 2,
                      criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    # Create some random colors
    color = np.random.randint(0, 255, (100, 3))

    # Take first frame and find corners in it
    #ret, old_frame = cap.read()
    #cv2.setMouseCallback("old_frame", click_event)
    #cv2.imshow("old_frame - select shape", old_frame)

    ret, old_frame = cap.read()
    old_grey       = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)


    while(len(refPt) < 1):
        ret, frame = cap.read()
        cv2.setMouseCallback("frame", click_event)
        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    #time.sleep(4.0)
    print(refPt)
    
    p0 = refPt[0]


    #p0             = cv2.goodFeaturesToTrack(old_grey, mask=None,  # WANT TO REPLACE THIS
    #                                         **feature_params)


    # use color to find desired initial point, which is then
    # given to the while loop below to do optical flow tracking
    hsv = cv2.cvtColor(old_frame, cv2.COLOR_BGR2HSV)

    # HSV in OpenCV is tricky because of variable size:
    # H is in [0, 180] and S,V are in [0,255]. 
    # Typically H is in range [0,360] (the full circle), 
    # but to fit in a byte (256 different values) 
    # it's value is halved.

    # define range of color in HSV
    sensitivity = 11 # lower value means more specific
        # --> should be at least 15
    red_ranges = np.array([[0,               0,   100],                 # lower target 0
                           [sensitivity,     255, 255],     # upper target 0
                           [180-sensitivity, 100, 100], # lower target 1
                           [180,             255, 255]])            # upper target 1
    # red H value is 0

    #blue = np.array([[240, 100, 100],           # lower target 0
    #               [sensitivity, 255, 255],     # upper target 0
    #               [180-sensitivity, 100, 100], # lower target 1
    #               [180, 255, 255]])            # upper target 1

    # Red upper and lower ranges
    #lower_target_0 = np.array([0, 0, 100])
    #upper_target_0 = np.array([sensitivity, 255, 255])
    #lower_target_1 = np.array([180 - sensitivity, 100, 100])
    #upper_target_1 = np.array([180, 255, 255])

    mask_0 = cv2.inRange(hsv, red_ranges[0], red_ranges[1]);
    mask_1 = cv2.inRange(hsv, red_ranges[2], red_ranges[3]);

    # Threshold the HSV image to get only desired colors
    mask = cv2.bitwise_or(mask_0, mask_1)

    # Bitwise-AND mask and original image
    old_output = cv2.bitwise_and(old_frame, old_frame, mask=mask)
    
    ## Contours 
    #imgrey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ##thresh = cv2.threshold(imgrey, 127, 255, 0)
    #blurred = cv2.GaussianBlur(imgrey, (5,5), 0)
    #thresh  = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
    #contours = cv2.findContours(frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    ##cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)    
    ##op = cv2.drawContours(frame, contours, -1, (0,255,0),3)
 
    #contours = imutils.grab_contours(contours)
 
    old_grey    = cv2.cvtColor(old_output, cv2.COLOR_BGR2GRAY)
    blurred     = cv2.GaussianBlur(old_grey, (5, 5), 0)
    thresh      = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]

    # find contours in the thresholded image
        #--> use mask or output instead of thresh.copy() as first param
    cnts = cv2.findContours(old_output[:,:,1], cv2.RETR_EXTERNAL, 1)
    #cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    desired_cnt = min(cnts, key=cv2.contourArea)
        #x,y,w,h = cv2.boundingRect(desired_cnt)
        #cv2.rectangle(output, (x, y), (x+w, y+h), (0, 255, 0), 2)
        #cv2.circle(output, (int(np.floor(x+w/2)), 
        #                    int(np.floor(y+h/2))), 
        #           10, (255,0,0), 2)

    #p0 = np.array(desired_cnt[0], dtype=np.float32)

    while(True):
        ret,frame  = cap.read()
        frame_grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # calculate optical flow
        p1, st, err = cv2.calcOpticalFlowPyrLK(old_grey, frame_grey, 
                                               p0, None, **lk_params)

        if p1 is not None:
            good_new = p1[st==1]
            good_old = p0[st==1]

        # draw the tracks
        for i,(new,old) in enumerate(zip(good_new, good_old)):
            a,b   = new.ravel()
            c,d   = old.ravel()
            mask  = cv2.line(mask,   (int(a),int(b)),(int(c),int(d)), color[i].tolist(), 2)
            frame = cv2.circle(frame,(int(a),int(b)),5,color[i].tolist(),-1)
        img = cv2.add(frame, mask)
        cv2.imshow('Optical flow - hit q to exit', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Now update the previous frame and previous points
    old_grey = frame_grey.copy()
    p0       = good_new.reshape(-1,1,2)



if mode == 'contour':
    while(True):
        ret, frame = cap.read()
        hsv        = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # HSV in OpenCV is tricky because of variable size:
        # H is in [0, 180] and S,V are in [0,255]. 
        # Typically H is in range [0,360] (the full circle), 
        # but to fit in a byte (256 different values) 
        # it's value is halved.

        # H values in OpenCV for different colours
        red = 0; green = 60; blue = 120; yellow = 30

        # define range of color in HSV
        sensitivity = 11 # lower value means more specific
            # --> should be at least 15
        red_ranges = np.array([[0,               0,   100],                # lower target 0
                               [sensitivity,     255, 255],     # upper target 0
                               [180-sensitivity, 100, 100], # lower target 1
                               [180,             255, 255]])            # upper target 1
        # red H value is 0

        blue_ranges = np.array([[blue,             110, 110],              # lower target 0
                                [blue-sensitivity, 255, 255],  # upper target 0
                                [180-sensitivity,  100, 100],   # lower target 1
                                [blue+sensitivity, 255, 255]]) # upper target 1
    
        blue_r = np.array([[blue-sensitivity, 100, 100],
                           [blue+sensitivity, 255, 255]])

        #blue = np.array([[240, 100, 100],           # lower target 0
        #               [sensitivity, 255, 255],     # upper target 0
        #               [180-sensitivity, 100, 100], # lower target 1
        #               [180, 255, 255]])            # upper target 1

        lower_target_0 = np.array([0,                 0,   100])
        upper_target_0 = np.array([sensitivity,       255, 255])
        lower_target_1 = np.array([180 - sensitivity, 100, 100])
        upper_target_1 = np.array([180,               255, 255])

        mask_0 = cv2.inRange(hsv, lower_target_0, upper_target_0);
        mask_1 = cv2.inRange(hsv, lower_target_1, upper_target_1);

        #mask_0 = cv2.inRange(hsv, blue[0], blue[1])
        #mask_1 = cv2.inRange(hsv, blue[2], blue[3])

        # Threshold the HSV image to get only desired colors
        mask = cv2.bitwise_or(mask_0, mask_1)

        blue_mask = cv2.inRange(hsv, blue_r[0], blue_r[1])

        # Bitwise-AND mask and original image
        output = cv2.bitwise_and(frame, frame, mask=mask)
    
        ## Contours 
        #imgrey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ##thresh = cv2.threshold(imgrey, 127, 255, 0)
        #blurred = cv2.GaussianBlur(imgrey, (5,5), 0)
        #thresh  = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
        #contours = cv2.findContours(frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        ##cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)    
        ##op = cv2.drawContours(frame, contours, -1, (0,255,0),3)
 
        #contours = imutils.grab_contours(contours)
 
        gray    = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh  = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]

        # find contours in the thresholded image
            #--> use mask or output instead of thresh.copy()
        cnts = cv2.findContours(output[:,:,1], cv2.RETR_EXTERNAL, 1)
        #cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        # loop over the contours
        #for c in cnts:
        ## compute the center of the contour
        #    M = cv2.moments(c)
        #    if M["m00"] != 0:
        #        cX = int(M["m10"] / M["m00"])
        #        cY = int(M["m01"] / M["m00"])
        #    else:
        #        cX, cY = 0, 0
        #    # draw the contour and center of the shape on the image
        #    cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
        #    cv2.circle(frame, (cX, cY), 7, (255, 255, 255), -1)
        #    cv2.putText(frame, "center", (cX - 20, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
        c       = max(cnts, key=cv2.contourArea)
        
        # Find then draw a bounding rectangle around contour
        x,y,w,h = cv2.boundingRect(c)
        cv2.rectangle(output, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # Mark centrepoint with circle
        cv2.circle(output, (int(np.floor(x+w/2)), 
                            int(np.floor(y+h/2))), 
                   10, (255,0,0), 2)

        #cv2.putText(output, "center", (x - 20, y - 20), 
        #            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)


        # Show the image
        #cv2.imshow("frame", frame)
        #out.write(output)
        cv2.imshow("Contour output - hit q to exit", output)
    
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    #out.release()
    cap.release()
    cv2.destroyAllWindows()


#    for c in contours:
#    # compute the center of the contour
#        M = cv2.moments(c)
#        cX = int(M["m10"] / M["m00"])
#        cY = int(M["m01"] / M["m00"])
#        # draw the center of the shape on the image
#        cv2.circle(mask, (cX, cY), 7, (0, 0, 255), -1)


#	    # draw the contour and center of the shape on the image
#        cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
#        cv2.circle(frame, (cX, cY), 7, (255, 255, 255), -1)
#        cv2.putText(frame, "center", (cX - 20, cY - 20),
#        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)


#    # show the image
#    #cv2.imshow('frame - hit q to exit!', frame) #regular video feed
#    #cv2.imshow('contours - hit q to exit!', op)
#    cv2.imshow('mask - hit q to exit!', mask)
#    cv2.imshow('Output - hit q to exit!', output)

#    if cv2.waitKey(1) & 0xFF == ord('q'):
#        break

#cap.release()
#cv2.destroyAllWindows()


#class ColorTracker:

#    def __init__(self):
#        cv2.NamedWindow( color_tracker_window, 1 )
#        self.capture = cv2.CaptureFromCAM(0)

#    def run(self):
#        while True:
#            img = cv2.QueryFrame( self.capture )

#            #blur the source image to reduce color noise
#            cv2.Smooth(img, img, cv2.CV_BLUR, 3);

#            #convert the image to hsv(Hue, Saturation, Value) so its
#            #easier to determine the color to track(hue)
#            hsv_img = cv2.CreateImage(cv.GetSize(img), 8, 3)
#            cv2.CvtColor(img, hsv_img, cv2.CV_BGR2HSV)

#            #limit all pixels that don't match our criteria, in this case we are
#            #looking for purple but if you want you can adjust the first value in
#            #both turples which is the hue range(120,140).  OpenCV uses 0-180 as
#            #a hue range for the HSV color model
#            thresholded_img =  cv2.CreateImage(cv2.GetSize(hsv_img), 8, 1)
#            cv2.InRangeS(hsv_img, (120, 80, 80), (140, 255, 255), thresholded_img)

#            #determine the objects moments and check that the area is large
#            #enough to be our object
#            moments = cv2.Moments(thresholded_img, 0)
#            area = cv2.GetCentralMoment(moments, 0, 0)

#            #there can be noise in the video so ignore objects with small areas
#            if(area > 100000):
#                #determine the x and y coordinates of the center of the object
#                #we are tracking by dividing the 1, 0 and 0, 1 moments by the area
#                x = cv2.GetSpatialMoment(moments, 1, 0)/area
#                y = cv2.GetSpatialMoment(moments, 0, 1)/area

#                #print 'x\: ' + str(x) + ' y\: ' + str(y) + ' area\: ' + str(area)

#                #create an overlay to mark the center of the tracked object
#                overlay = cv2.CreateImage(cv2.GetSize(img), 8, 3)

#                cv2.Circle(overlay, (x, y), 2, (255, 255, 255), 20)
#                cv2.Add(img, overlay, img)
#                #add the thresholded image back to the img so we can see what was
#                #left after it was applied
#                cv2.Merge(thresholded_img, None, None, None, img)

#            #display the image
#            cv2.ShowImage(color_tracker_window, img)

#            if cv2.WaitKey(10) == 27:
#                break

#if __name__=="__main__":
#    color_tracker = ColorTracker()
#    color_tracker.run()



#(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

#if __name__ == '__main__' :
#    # Set up tracker.
#    # Instead of MIL, you can also use
#    tracker_types = ['BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']
#    tracker_type = tracker_types[2]

#    if int(minor_ver) < 3:
#        tracker = cv2.Tracker_create(tracker_type)
#    else:
#        if tracker_type == 'BOOSTING':
#            tracker = cv2.TrackerBoosting_create()
#        if tracker_type == 'MIL':
#            tracker = cv2.TrackerMIL_create()
#        if tracker_type == 'KCF':
#            tracker = cv2.TrackerKCF_create()
#        if tracker_type == 'TLD':
#            tracker = cv2.TrackerTLD_create()
#        if tracker_type == 'MEDIANFLOW':
#            tracker = cv2.TrackerMedianFlow_create()
#        if tracker_type == 'GOTURN':
#            tracker = cv2.TrackerGOTURN_create()
#        if tracker_type == 'MOSSE':
#            tracker = cv2.TrackerMOSSE_create()
#        if tracker_type == "CSRT":
#            tracker = cv2.TrackerCSRT_create()

#    # Get video (from built-in camera)
#    video = cv2.VideoCapture(0)
#    video.set(3,640) # set Width
#    video.set(4,480) # set Height

#    # Exit if video not opened.
#    #if not video.isOpened():
#    #    print "Could not open video"
#    #    sys.exit()

#    # Read first frame.
#    ok, frame = video.read()

#    if not ok:
#        print('Cannot read video file')
#        sys.exit()

#    # Define an initial bounding box
#    bbox = (287, 23, 86, 320)

#    # Uncomment the line below to select a different bounding box
#    #bbox = cv2.selectROI(frame, False)

#    # Initialize tracker with first frame and bounding box
#    ok = tracker.init(frame, bbox)

#    while True:
#        # Read a new frame
#        ok, frame = video.read()
#        if not ok:
#            break

#        # Start timer
#        timer = cv2.getTickCount()
#        # Update tracker
#        ok, bbox = tracker.update(frame)
#        # Calculate Frames per second (FPS)
#        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);

#        # Draw bounding box
#        if ok:
#            # Tracking success
#            p1 = (int(bbox[0]), int(bbox[1]))
#            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
#            cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)
#        else :
#            # Tracking failure
#            cv2.putText(frame, "Tracking failure detected", (100,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)

#        # Display tracker type on frame
#        cv2.putText(frame, tracker_type + " Tracker", (100,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2);

#        # Display FPS on frame
#        cv2.putText(frame, "FPS : " + str(int(fps)), (100,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50), 2);

#        # Display result
#        cv2.imshow("Tracking", frame)

#        # Exit if ESC pressed
#        k = cv2.waitKey(1) & 0xff
#        if k == 27 : break

