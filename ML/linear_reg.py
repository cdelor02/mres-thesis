# Closed-loop control for EIT actuator project
# by Charlie DeLorey

# Linear regression tutorial
# https://towardsdatascience.com/simple-machine-learning-model-in-python-in-5-lines-of-code-fe03d72e78c6

from   __future__ import print_function
from   sklearn.model_selection import train_test_split
from   sklearn.metrics import mean_squared_error, r2_score
from   sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from   random import randint
from   scipy import signal
from   scipy import stats
import pandas as pd
import numpy as np
import argparse
import time
import sys
import cv2



# Arduino parameters
baudrate           = 115200
spool_circum       = 31.4 #mm
stepsPerRevolution = 200
stepsPer1mm        = 1 / (spool_circum/stepsPerRevolution)

fs = 40

## Converting between steps and millimetres
def stepToDist(num_steps):
    return num_steps / stepsPer1mm

def distToStep(dist):
    return dist * stepsPer1mm

## Generate dataset
#from random import randint
#TRAIN_SET_LIMIT = 1000
#TRAIN_SET_COUNT = 100

#TRAIN_INPUT = list()
#TRAIN_OUTPUT = list()
#for i in range(TRAIN_SET_COUNT):
#    a = randint(0, TRAIN_SET_LIMIT)
#    b = randint(0, TRAIN_SET_LIMIT)
#    c = randint(0, TRAIN_SET_LIMIT)
#    op = a + (2*b) + (3*c)
#    TRAIN_INPUT.append([a, b, c])
#    TRAIN_OUTPUT.append(op)

step_data = pd.read_csv("../data/copper_wire_actuator_500_samples_40Hz-2021-08-17/copper_wire_actuator_500_samples_40Hz-2021-08-17_0.csv",
                          sep='\t', lineterminator='\n', skiprows=1, names=["steps"])
eit_data  = pd.read_csv("../data/copper_wire_actuator_500_samples_40Hz-2021-08-17/copper_wire_actuator_500_samples_40Hz.txt", 
                      sep='\t', lineterminator='\n', skiprows=1, 
                      names=["a0", "B", "C", "D", "a1", "F", "G", "H", "a2"])
eit_data = eit_data[["a0", "a1", "a2"]]

point_data = pd.read_csv("../data/actuator_experiments_fixed_a0-2021-09-10/actuator_10_iterations_experiments_8_data_for_matlab_2.csv",
                         sep='\t', lineterminator='\n', names=["a0", "a1", "a2", "x", "y", "z"],
                         skiprows=1)#["X", "Y"])

#point_data.columns = ["a0", "a1", "a2", "x", "y", "z"]

#["a0", "B", "C", "D", "a1", "F", "G", "H", "a2"]

### applying high pass filter to EIT data
def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
    return b, a
def butter_highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y

eit_data_trunc = eit_data[["a0", "a1", "a2"]][:-4]

#for example
filtered_one   = butter_highpass_filter(eit_data_trunc["a0"], .1, 40)
filtered_two   = butter_highpass_filter(eit_data_trunc["a1"], .1, 40)
filtered_three = butter_highpass_filter(eit_data_trunc["a2"], .1, 40)

filtered_one   = pd.DataFrame(filtered_one) 
filtered_two   = pd.DataFrame(filtered_two)
filtered_three = pd.DataFrame(filtered_three)

eit_data_filtered = pd.concat([filtered_one, filtered_two, filtered_three], axis=1)

eit_data_filtered.columns = ["a0", "a1", "a2"]


####### I DON'T WANT TO BE FILTERING HERE, I WANT TO BE FINDING THE START OF EACH
####### ACTUATION SPIKE AND RE-NORMALISING THE PEAK FROM THERE, FOR EACH PEAK (flex
####### and relax) because the values are drifting



### !! create time X axis scale using freq
timesc = np.linspace(0, len(eit_data)/fs, len(eit_data))


plt.rcParams.update({'font.size': 14})


### **Converting from regular opencv image scaling to a regular coordinate grid
point_data.columns = ["X", "Y"]
c   = [30, point_data["Y"][0]]
adj = point_data["X"] - c[0]
opp = c[1] - point_data["Y"]
# can try plotting these to see how they compare to the plotting below
plt.plot(adj, opp); plt.title('Fingertip point data'); plt.show()
#         X    Y

 #If you want to plot it in the unmodified form
# https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.imshow.html
im = plt.imread("../computer_vision/figure_images.png_1538.jpg")
implot = plt.imshow(im, origin='lower')
ax = plt.plot(point_data["X"], point_data["Y"])
plt.xlabel("X", fontsize=15)
plt.ylabel("Y", fontsize=15)
plt.title("OpenCV tracking data", fontsize=15)
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()

## ***POINT_DATA is the plotting in the normal OpenCV image format
##  **ADJ (X axis) and OPP (Y axis) is the lengths of each side of the 

# computing right triangles from points
valid_points = np.where(adj > 0)[0]
valid_adj = adj[valid_points]
valid_opp = opp[valid_points]
thetas = np.arctan(valid_opp / valid_adj)
    ##--> maybe used np.arctan2() instead?
thetas = np.degrees(thetas)
#np.savetxt("copper_wire_actuator_500_samples_40Hz_thetas-2021-08-17.csv", 
#           thetas, fmt="%1.3f", delimiter=",")


theta_data = pd.read_csv("../data/copper_wire_actuator_500_samples_40Hz-2021-08-17/copper_wire_actuator_500_samples_40Hz_thetas-2021-08-17.csv",
                         sep='\t', lineterminator='\n', names=["ts"])

#plt.plot(theta_data)
#plt.xlabel("Time (samples)", fontsize=18)
#plt.ylabel("Angle (degrees)", fontsize=18)
#plt.title("Angle values between baseline and tracked point", fontsize=20)
#plt.show()


#removal of large spikes, as per this tutorial
# https://becominghuman.ai/linear-regression-in-python-with-pandas-scikit-learn-72574a2ec1a5
std_dev = 3
step_data = step_data[(np.abs(stats.zscore(step_data)) < float(std_dev)).all(axis=1)]
#????????

theta_data = pd.DataFrame(theta_data)
# input data: | eit joint 0 | eit joint 1 | eit joint 2 |
concat_data = pd.concat([eit_data_trunc["a0"],
                         eit_data_trunc["a1"],
                         eit_data_trunc["a2"]],
                         axis=1)

X_train = concat_data.head(300)
X_test  = concat_data.head(len(eit_data_trunc["a0"])-300)

y_train = point_data[["X"]].head(300)
y_test  = point_data[["X"]].head(len(eit_data_trunc)-300)


plt.plot(point_data[["X"]], 'r')
plt.plot(point_data[["Y"]], 'g')
plt.title('Point data X and Y values')
plt.gca().invert_yaxis()
plt.legend(['X', 'Y'])
plt.show()

#x_train, x_test, y_train, y_test = train_test_split(concat_data, point_data, test_size=0.2, )

TRAIN_INPUT  = concat_data#step_data.iloc[0:len(theta_data),0]
TRAIN_OUTPUT = point_data[["X"]]#eit_data.iloc[:,0]

## The learning begins
predictor = LinearRegression()#n_jobs=-1)
predictor.fit(X_train, y_train)#X=TRAIN_INPUT, y=TRAIN_OUTPUT)

#index [346]
#X_TEST = [[25, 0.261, 0.2593, 0.36]]
outcome = predictor.predict(X_test)#X=X_TEST)
coefficients = predictor.coef_

print('(mean) outcome : {}\nCoefficients : {}'.format(np.mean(outcome), coefficients))
# https://scikit-learn.org/stable/auto_examples/linear_model/plot_ols.html
print('Mean squared error: %.2f' % mean_squared_error(y_test, outcome))
print('Coefficient of determination (r2 score): %.2f' % r2_score(y_test, outcome))

# Plot outputs

y_tests = pd.concat([y_test, y_test, y_test], axis=1)

plt.scatter(X_test, y_tests,  color='black')
plt.plot(X_test, outcome, color='blue', linewidth=3)

plt.xticks(())
plt.yticks(())
plt.title("Linear regression test --> a bunch of nonsense")
plt.legend()

plt.show()






##### try multi-task lasso, doing learning on the x coord and the y coord separately