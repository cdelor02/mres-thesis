import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import argparse
import cv2 as cv

params_dir = "camera_calibration_attempt-2021-08-20"
cam_mat    = pd.read_csv(params_dir + "/cameraparams-intrinsic_parameters.csv",
                         sep='\t', lineterminator='\n')

tvec_vals = []
tvec_bs   = []
tvec_fs   = []
tvec_bad_indx = []
framecount = 0

#intrinsics = cam_mat.iloc[5:7, :][0]
intrinsics = np.array([[518.1574, 0,        0],
                       [0,        518.8407, 0],
                       [308.5504, 275.0961, 1]])

# radial distortion [_,_], then tangential [_,_], then estimated tangential?
distortion = np.array([0.0271, 0.0039, 0, 0, 0])


ARUCO_LENGTH_MM = 7.0
CAMERA_MATRIX   = intrinsics # TODO: change or make sure i'm correct
DIST_COEFF      = distortion

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

    # write frame number 
    cv.putText(frame, str(framecount), (10, 10), cv.FONT_HERSHEY_SIMPLEX,
               0.5, (0, 0, 255), 2)

    frame = cv.aruco.drawAxis(frame, CAMERA_MATRIX, DIST_COEFF, rvec, tvec, 0.01)
    
    ## FOR VIDEO SAVING PURPOSES
    #out.write(frame)

    cv.imshow("ArUco", frame)
    cv.waitKey(1) # trying to delay
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
        print(ids)
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
            if 4 not in ids:
                tvec_bad_indx.append(framecount)
                tvec_fs.append(None)
            elif markerID == 4:
                tvec_fs.append(tvec)
            if 4 not in ids:
                tvec_bad_indx.append(framecount)
                tvec_bs.append(None)
            elif markerID == 3:
                tvec_bs.append(tvec)
            #print("tvec", tvec)
    return tvec



# 'main', where we open the video feed and start tracking the specified marker(s)
directory = '../data/10_iterations_10_experiments_done_on-2021-09-01/'
filename  = '../data/10_iterations_10_experiments_done_on-2021-09-01/copper_wire_actuator_35fast_chamber_5minmax_10_iterations_3-2021-09-01.mp4'

#filename = './opencv_videos/copper_wire_actuator_35fast_chamber_5minmax_10_iterations_13-2021-09-05.mp4'

#filename = '../data/copper_wire_actuator_35fast_chamber_vertical_actuator_experiments-2021-09-06/copper_wire_actuator_35fast_chamber_100g_weight_lift_110_steps-2021-09-06.mp4'

#filename = './opencv_videos/eit_chamber_glove_test_6_aruco_markers-21-09-06.mp4'

filename = '../data/actuator_experiments_fixed_a0-2021-09-10/actuator_10_iterations_experiments_12.mp4'

cap = cv.VideoCapture(filename)

# Default resolutions of the frame are obtained.The default resolutions are system dependent.
# We convert the resolutions from float to integer.
frame_width  = int(cap.get(3))
frame_height = int(cap.get(4))

# Define the codec and create VideoWriter object. The output is 'filename'.
#out = cv.VideoWriter(filename[:-4] + '-aruco_tracking' + '.mp4', cv.VideoWriter_fourcc(*'mp4v'), 
#                     40, (frame_width, frame_height))

print("ArUco : commencing recording...")
print("Recording from: " + filename)

while(True):
    success, frame = cap.read()
    framecount += 1
    # ArUco tracking
    tf = get_aruco_pose(frame)
    tvec_vals.append(tf)


cap.release()
#out.release()
print('framecount: ', framecount)


cv.destroyAllWindows()


for i in range(len(tvec_vals)):
    tvec_vals[i] = tvec_vals[i].reshape((1,3))

tvec_vals = np.squeeze(tvec_vals)
tv        = pd.DataFrame(tvec_vals, columns=["x", "y", "z"])

fs_vals = pd.DataFrame(index=range(len(tvec_vals)), columns=["x", "y", "z"])

for i in range(len(tvec_bs)):
    if tvec_bs[i] is not None:
        tvec_bs[i] = tvec_bs[i].reshape((1,3))

for i in range(len(tvec_fs)):
    if tvec_fs[i] is not None:
        tvec_fs[i] = np.squeeze(tvec_fs[i])

for i in range(len(tvec_fs)):
    if tvec_fs[i] is not None:
        tvec_fs[i] = np.squeeze(tvec_fs[i])

for i in range(len(tvec_bs)):
    if tvec_bs[i] is not None:
        tvec_bs[i] = np.squeeze(tvec_bs[i])

for i in range(len(tvec_fs)):
    if tvec_fs[i] is None:
        fs_vals["x"].iloc[i] = None
        fs_vals["y"].iloc[i] = None
        fs_vals["z"].iloc[i] = None
    else:
        fs_vals["x"].iloc[i] = tvec_fs[i][0]
        fs_vals["y"].iloc[i] = tvec_fs[i][1]
        fs_vals["z"].iloc[i] = tvec_fs[i][2]




tv_fs = pd.DataFrame(tvec_fs, columns=["x", "y", "z"])
tv_bs = pd.DataFrame(tvec_bs, columns=["x", "y", "z"])

# Plot the base values (tv_bs) and the fingertip values (tv_fs)
plt.scatter(tv_fs[["x"]], tv_fs[["y"]])
plt.scatter(tv_bs[["x"]], tv_bs[["y"]])
centr = [np.mean(tv_bs[["x"]]), np.mean(tv_bs[["y"]])]
plt.plot(centr, 'ro')
plt.legend(['Fingertip points', 'Base points'])
#plt.plot(centr, [tv_fs[["x"]], tv_fs[["y"]]], 'k-')
plt.gca().invert_yaxis()
plt.show()

# normalise by the first value
tv[["x", "y", "z"]].values = tv[["x", "y", "z"]].values - tv[["x", "y", "z"]].iloc[0]

tv_xy   = tv[["x", "y"]]
goodpts = tv[["x"]] > 25

#plotting
fig=plt.figure()
ax = fig.add_subplot(projection='3d')
ax.scatter(tv[["x"]],tv[["y"]],tv[["z"]])
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
plt.gca().invert_yaxis()
plt.show()


#half = int([0:len(tv)/2])

#### SAVING MARKER TVEC


## saving it together with it's EIT data
#data = pd.read_csv()

data = data.assign(x=pd.Series(np.squeeze(tv_fs[["x"]].values)))
data = data.assign(y=pd.Series(np.squeeze(tv_fs[["y"]].values)))
data = data.assign(z=pd.Series(np.squeeze(tv_fs[["z"]].values)))