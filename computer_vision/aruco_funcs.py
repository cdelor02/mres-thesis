## Functions for ArUco marker tracking

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
    
    ## FOR VIDEO SAVING PURPOSES
    #out.write(frame)

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
            show_aruco(im, markerCorner, markerID) # uncomment to show markers in video
            rmat, _ = cv.Rodrigues(rvec)
            tvec    = tvec.reshape(3, 1)
            transf  = np.concatenate((rmat, tvec), axis = 1)
            #print("rmat", rmat)
            if markerID == 3:
                tvec_bs.append(tvec)
            if markerID == 4:
                tvec_fs.append(tvec)
            #print("tvec", tvec)
    return tvec
