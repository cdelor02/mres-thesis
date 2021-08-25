import pandas as pd
import numpy as np
import cv2 as cv

params_dir = "camera_calibration_attempt-2021-08-20"

cam_mat = pd.read_csv(params_dir + "/cameraparams-intrinsic_parameters.csv",
                      sep='\t', lineterminator='\n')

#intrinsics = cam_mat.iloc[5:7, :][0]
intrinsics = np.array([[518.1574, 0,        0],
                       [0,        518.8407, 0],
                       [308.5504, 275.0961, 1]])

# radial distortion [_,_], then tangential [_,_], then estimated tangential?
distortion = np.array([0.0271, 0.0039, 0, 0, 0])


ARUCO_LENGTH_MM = 7.0
CAMERA_MATRIX   = intrinsics # TODO: change or make sure i'm correct
DIST_COEFF      = distortion #np.array([k1, k2, k3, k4])  # TODO: change

DICT  = cv.aruco.Dictionary_get(0)
PARAM = cv.aruco.DetectorParameters_create()


def show_aruco(frame, markerCorner, markerID):
    # extract the marker corners (which are always returned in
    # top-left, top-right, bottom-right, and bottom-left order)
    corners = markerCorner.reshape((4, 2))
    (topLeft, topRight, bottomRight, bottomLeft) = corners

    # convert each of the (x, y)-coordinate pairs to integers
    topRight    = (int(topRight[0]),    int(topRight[1]))
    bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
    bottomLeft  = (int(bottomLeft[0]),  int(bottomLeft[1]))
    topLeft     = (int(topLeft[0]),     int(topLeft[1]))

    # draw the bounding box of the ArUCo detection
    cv.line(frame, topLeft,     topRight,    (0, 255, 0), 2)
    cv.line(frame, topRight,    bottomRight, (0, 255, 0), 2)
    cv.line(frame, bottomRight, bottomLeft,  (0, 255, 0), 2)
    cv.line(frame, bottomLeft,  topLeft,     (0, 255, 0), 2)

    # compute and draw the center (x, y)-coordinates of the ArUco marker
    cX = int((topLeft[0] + bottomRight[0]) / 2.0)
    cY = int((topLeft[1] + bottomRight[1]) / 2.0)
    cv.circle(frame, (cX, cY), 4, (0, 0, 255), -1)

    # draw the ArUco marker ID on the image
    cv.putText(frame, str(markerID),
               (topLeft[0], topLeft[1] - 15), 
               cv.FONT_HERSHEY_SIMPLEX,
               0.5, (0, 255, 0), 2)

    frame = cv.aruco.drawAxis(frame, CAMERA_MATRIX, DIST_COEFF, rvec, tvec, 0.01)
    cv.imshow("ArUco", frame)
    cv.waitKey(1)
    # quit on ESC button
    #if cv.waitKey(1) & 0xFF == 27:  # Esc pressed
    #    break


def get_aruco_pose(im):
    global rvec, tvec
    corners, ids, rejectedCandidates = cv.aruco.detectMarkers(im, 
                                                              DICT, 
                                                              parameters=PARAM)
    transf = None
    if len(corners) > 0:
        # flatten the ArUco IDs list
        ids = ids.flatten()
        # loop over the detected ArUCo corners
        for (markerCorner, markerID) in zip(corners, ids):
            #if markerID == 0:   # TODO: change, you have ids from 0 to 4
                # Get pose
            rvec, tvec, _ = cv.aruco.estimatePoseSingleMarkers(markerCorner, 
                                                                ARUCO_LENGTH_MM, 
                                                                CAMERA_MATRIX, 
                                                                DIST_COEFF)
            # Draw aruco
            show_aruco(im, markerCorner, markerID) # TODO: uncomment
            rmat, _ = cv.Rodrigues(rvec)
            tvec    = tvec.reshape(3, 1)
            transf  = np.concatenate((rmat, tvec), axis = 1)
    return transf




# 'main', where we open the video feed and start tracking the specified marker(s)

cap = cv.VideoCapture(0)

while(True):
    success, frame = cap.read()

    # ArUco tracking
    tf = get_aruco_pose(frame)
    #print(tf)


cap.release()