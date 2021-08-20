# Closed-loop control for EIT actuator project
# by Charlie DeLorey

# Linear regression tutorial
# https://towardsdatascience.com/simple-machine-learning-model-in-python-in-5-lines-of-code-fe03d72e78c6

from __future__ import print_function
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from random import randint
from scipy import stats
import pandas as pd
import numpy as np
import argparse
import time
import sys
import cv2

from scipy import signal

# Arduino parameters
baudrate           = 115200
spool_diam         = 31.4 #mm
stepsPerRevolution = 200
stepsPer1mm        = 1 / (spool_diam/stepsPerRevolution)

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
                      names=["3", "B", "C", "D", "2", "F", "G", "H", "1"])
eit_data = eit_data[["1", "2", "3"]]

point_data = pd.read_csv("../data/copper_wire_actuator_500_samples_40Hz-2021-08-17/copper_wire_actuator_500_samples_40Hz_points-2021-08-17_0.csv",
                         lineterminator='\n')#sep='\t', lineterminator='\n', names=["X", "Y"])



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

eit_data_trunc = eit_data[["1", "2", "3"]][:-4]

#for example
filtered_one   = butter_highpass_filter(eit_data_trunc["1"], .1, 40)
filtered_two   = butter_highpass_filter(eit_data_trunc["2"], .1, 40)
filtered_three = butter_highpass_filter(eit_data_trunc["3"], .1, 40)

filtered_one = pd.DataFrame(filtered_one); filtered_two = pd.DataFrame(filtered_two);
filtered_three = pd.DataFrame(filtered_three);

eit_data_filtered = pd.concat([filtered_one, filtered_two, filtered_three], axis=1)

eit_data_filtered.columns = ["1", "2", "3"]


plt.rcParams.update({'font.size': 14})


### **Converting from regular opencv image scaling to a regular coordinate grid
point_data.columns = ["X", "Y"]
c   = [30, point_data["Y"][0]]
adj = point_data["X"] - c[0]
opp = c[1] - point_data["Y"]
# can try plotting these to see how they compare to the plotting below
plt.plot(adj, opp); plt.show()


 #If you want to plot it in the unmodified form
im = plt.imread("../computer_vision/firstframe.jpg")
implot = plt.imshow(im)
ax = plt.plot(point_data["X"], point_data["Y"])
plt.xlabel("X", fontsize=15)
plt.ylabel("Y", fontsize=15)
plt.title("OpenCV tracking data", fontsize=15)
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
# input data: step data | eit joint 1 | eit joint 1 | eit joint 3 |
#concat_data = pd.concat([step_data.iloc[0:len(theta_data), 0],
#                                  eit_data_filtered["1"].iloc[0:len(theta_data)],
#                                  eit_data_filtered["2"].iloc[0:len(theta_data)],
#                                  eit_data_filtered["3"].iloc[0:len(theta_data)]],
#                                  axis=1)

concat_data = pd.concat([eit_data_filtered["1"],
                         eit_data_filtered["2"],
                         eit_data_filtered["3"]],
                         axis=1)


X_train = concat_data.head(300)
X_test  = concat_data.head(len(eit_data_filtered["1"])-300)

y_train = theta_data.head(300)
y_test  = theta_data.head(len(eit_data_filtered)-300)


TRAIN_INPUT  = concat_data#step_data.iloc[0:len(theta_data),0]
TRAIN_OUTPUT = theta_data#eit_data.iloc[:,0]

## The learning begins
predictor = LinearRegression()#n_jobs=-1)
predictor.fit(X_train, y_train)#X=TRAIN_INPUT, y=TRAIN_OUTPUT)

#index [346]
#X_TEST = [[25, 0.261, 0.2593, 0.36]]
outcome = predictor.predict(X_test)#X=X_TEST)
coefficients = predictor.coef_

print('(mean) Outcome : {}\nCoefficients : {}'.format(np.mean(outcome), coefficients))
# https://scikit-learn.org/stable/auto_examples/linear_model/plot_ols.html
print('Mean squared error: %.2f' % mean_squared_error(y_test, outcome))
print('Coefficient of determination: %.2f' % r2_score(y_test, outcome))

# Plot outputs

y_tests = pd.concat([y_test, y_test, y_test, y_test], axis=1)

plt.scatter(X_test, y_tests,  color='black')
plt.plot(X_test, outcome, color='blue', linewidth=3)

plt.xticks(())
plt.yticks(())
plt.title("Linear regression test --> a bunch of nonsense")

plt.show()