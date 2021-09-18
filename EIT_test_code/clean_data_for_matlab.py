## Data preparation for MATLAB machine learning
## Charlie DeLorey

from   scipy.signal import savgol_filter
import matplotlib.pyplot as plt
from   scipy import signal
import seaborn as sns
import pandas as pd
import numpy  as np
import cv2 as cv
import glob
import sys 

eitfilename    = sys.argv[1]   # _eit file
videofilename  = eitfilename[:-8] + '.mp4'

eit_data  = pd.read_csv(eitfilename, sep='\t', lineterminator='\n', 
                        skiprows=1, names=["a0", "B", "C", "D", "a1", "F", "G", "H", "a2"])

eit_data = eit_data[["a0", "a1", "a2"]]

params_dir = "../computer_vision/camera_calibration_attempt-2021-08-20"
cam_mat    = pd.read_csv(params_dir + "/cameraparams-intrinsic_parameters.csv",
                         sep='\t', lineterminator='\n')


print("Process EIT and point data into single .csv file")
print("Note: check that the video file you're using actually has ArUco markers in it!")
print("Using EIT data from: " + eitfilename)

tvec_bad_indx = []
framecount    = 0
tvec_vals     = []
tvec_bs       = []
tvec_fs       = []

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

kernel = np.ones((5,5), np.uint8)

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

    #cv.imshow("ArUco", frame)
    #cv.waitKey(1)
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
             # or 0
            if 4 not in ids: # will need to change this if using vertical actuator experiment
                tvec_bad_indx.append(framecount)
                tvec_fs.append(None)
            elif markerID == 4: # or 0
                tvec_fs.append(tvec)
            #if 3 not in ids:
            #    tvec_bad_indx.append(framecount)
            #    tvec_bs.append(None)
            if markerID == 3: # or 1
                tvec_bs.append(tvec)
    return tvec


cap = cv.VideoCapture(videofilename)

frame_width  = int(cap.get(3))
frame_height = int(cap.get(4))


print("Using mp4 file: " + videofilename)

while(True):
    success, frame = cap.read()
    framecount += 1
    #dilframe = cv.dilate(frame, kernel, iterations=1)

    if framecount == 34:
        cv.imwrite(videofilename[:-4] + '_no' + str(framecount) + '.jpg', frame)

    if framecount == 500:
        cv.imwrite(videofilename[:-4] + '_no' + str(framecount) + '.jpg', frame)

    if framecount == 4:
        cv.imwrite(videofilename[:-4] + '_no' + str(framecount) + '.jpg', frame)

    if framecount == 2300:
        cv.imwrite(videofilename[:-4] + '_no' + str(framecount) + '.jpg', frame)


    # ArUco tracking
    tf = get_aruco_pose(frame)#dilframe)
    tvec_vals.append(tf)

print("No. frames:", framecount)

cap.release()

################# THIS IS THE POINT WHERE IT JUST STOPS
print("Processing transformation vectors")

fs_vals = pd.DataFrame(index=range(len(tvec_fs)), columns=["x", "y", "z"])
bs_vals = pd.DataFrame(index=range(len(tvec_bs)), columns=["x", "y", "z"])

def nan_helper(y):
    return np.isnan(y), lambda z: z.nonzero()[0]

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
        fs_vals["x"].iloc[i] = float('nan')
        fs_vals["y"].iloc[i] = float('nan')
        fs_vals["z"].iloc[i] = float('nan')
    else:
        fs_vals["x"].iloc[i] = tvec_fs[i][0]
        fs_vals["y"].iloc[i] = tvec_fs[i][1]
        fs_vals["z"].iloc[i] = tvec_fs[i][2]

for i in range(len(tvec_bs)):
    if tvec_bs[i] is None:
        bs_vals["x"].iloc[i] = float('nan')
        bs_vals["y"].iloc[i] = float('nan')
        bs_vals["z"].iloc[i] = float('nan')
    else:
        bs_vals["x"].iloc[i] = tvec_bs[i][0]
        bs_vals["y"].iloc[i] = tvec_bs[i][1]
        bs_vals["z"].iloc[i] = tvec_bs[i][2]

#np.isnan(bs_vals[["x"]].iloc[30].values[0])

fs_vals["x"] = pd.to_numeric(fs_vals["x"], downcast="float")
fs_vals["y"] = pd.to_numeric(fs_vals["y"], downcast="float")
fs_vals["z"] = pd.to_numeric(fs_vals["z"], downcast="float")

bs_vals["x"] = pd.to_numeric(bs_vals["x"], downcast="float")
bs_vals["y"] = pd.to_numeric(bs_vals["y"], downcast="float")
bs_vals["z"] = pd.to_numeric(bs_vals["z"], downcast="float")


#### Perform linear interpolation over missing datapoints
# https://stackoverflow.com/questions/6518811/interpolate-nan-values-in-a-numpy-array
# https://docs.scipy.org/doc/scipy/reference/reference/generated/scipy.interpolate.interp1d.html#scipy.interpolate.interp1d
fixed_x = fs_vals[["x"]].values
nans, xs = nan_helper(fixed_x)
fixed_x[nans] = np.interp(xs(nans), xs(~nans), fixed_x[~nans])

fixed_y = fs_vals[["y"]].values
nans, ys = nan_helper(fixed_y)
fixed_y[nans] = np.interp(ys(nans), ys(~nans), fixed_y[~nans])

fixed_z = fs_vals[["z"]].values
nans, zs = nan_helper(fixed_z)
fixed_z[nans] = np.interp(zs(nans), xs(~nans), fixed_z[~nans])


bs_x = bs_vals[["x"]].values
nans, xs = nan_helper(bs_x)
bs_x[nans] = np.interp(xs(nans), xs(~nans), bs_x[~nans])

bs_y = bs_vals[["y"]].values
nans, ys = nan_helper(bs_y)
bs_y[nans] = np.interp(ys(nans), ys(~nans), bs_y[~nans])

bs_z = bs_vals[["z"]].values
nans, zs = nan_helper(bs_z)
bs_z[nans] = np.interp(zs(nans), xs(~nans), bs_z[~nans])


# filtering to smooth the noisy x y signals
fixed_x = savgol_filter(np.squeeze(fixed_x), 51, 3)
fixed_y = savgol_filter(np.squeeze(fixed_y), 51, 3)
fixed_z = savgol_filter(np.squeeze(fixed_z), 51, 3)



timesc = np.linspace(0, len(eit_data)/40, len(eit_data))


df = eit_data[["a0", "a1", "a2"]] - eit_data[["a0", "a1", "a2"]][:1].values.squeeze()
df[df < 0] = 0


mine = []
maxe = []
maxe.append(max(df[["a0"]].values))
mine.append(min(df[["a0"]].values))
maxe.append(max(df[["a1"]].values))
mine.append(min(df[["a1"]].values))
maxe.append(max(df[["a2"]].values))
mine.append(min(df[["a2"]].values))

newstart = 400

fig, ax = plt.subplots()
ax.plot(timesc[newstart:len(timesc)-1], df[["a0"]].values[newstart:len(timesc)-1], linewidth=4, color='b', label='a0')
ax.plot(timesc[newstart:len(timesc)-1], df[["a1"]].values[newstart:len(timesc)-1], linewidth=4, color='orange', label='a1')
ax.plot(timesc[newstart:len(timesc)-1], df[["a2"]].values[newstart:len(timesc)-1], linewidth=4, color='g', label='a2')#, color=["g", "c", "m"])#'r')
ax.set_xlabel("Time (s)", fontsize=20)
ax.set_ylabel("Voltage change (V)",  fontsize=20)
ax.set_ylim([min(mine)-0.01, max(maxe)+0.1])
ax.set_xlim([7, 80])
ax.legend(loc='center left')

offs = fixed_x.shape[0] - df.shape[0]

ax2 = ax.twinx()
ax2.plot(timesc, fixed_x[offs-1:len(fixed_x)-1], 'r--', label='x')
ax2.plot(timesc, fixed_y[offs-1:len(fixed_y)-1], 'k--', label='y')
ax2.set_ylabel("Tracked marker coordinates (pixels)", fontsize=18)
ax2.legend(loc='upper right', bbox_to_anchor=(1, 0.7))
#plt.title('works?', fontsize=20)
plt.show()

#[offs-1:len(timesc)-1]

basept = np.array([np.mean(bs_x), np.mean(bs_y), np.mean(bs_z)])
bspt   = pd.DataFrame(basept)#, columns=["x" ,"y", "z"])
#bspt.to_csv(eitfilename[:-8] + '_meanbasepoint.csv', sep='\t')

#for i in range(len(tvec_fs)):
#    tvec_fs[i] = tvec_fs[i].reshape((1,3))


#for i in range(len(tvec_bs)):
#    tvec_bs[i] = tvec_bs[i].reshape((1,3))

#tvec_fs = np.squeeze(tvec_fs)
#tvec_bs = np.squeeze(tvec_bs)

#tv_fs = pd.DataFrame(tvec_fs, columns=["x", "y", "z"])
#tv_bs = pd.DataFrame(tvec_bs, columns=["x", "y", "z"])

#eit_data = eit_data.assign(x=pd.Series(np.squeeze(tv_fs[["x"]].values)))
#eit_data = eit_data.assign(y=pd.Series(np.squeeze(tv_fs[["y"]].values)))
#eit_data = eit_data.assign(z=pd.Series(np.squeeze(tv_fs[["z"]].values)))

eit_data = eit_data.assign(x=pd.Series(np.squeeze(fixed_x)))
eit_data = eit_data.assign(y=pd.Series(np.squeeze(fixed_y)))
eit_data = eit_data.assign(z=pd.Series(np.squeeze(fixed_z)))


# save the new file
eit_data.to_csv(eitfilename[:-8] + '_data_for_matlab_2.csv', sep='\t')

