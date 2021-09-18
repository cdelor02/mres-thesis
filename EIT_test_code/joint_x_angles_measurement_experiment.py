# processing joint angle measurement data

from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
from scipy import signal
import pandas as pd
import numpy as np
import glob

fs = 40

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


#a0_0_deg = pd.read_csv("../data/joint_angle_measurements_individual-2021-08-25/a0_measurements/a0_0_deg.txt",
#                       sep='\t', lineterminator='\n', skiprows=1)

# first time doing this experiment
overall_dir = "../data/bend_angle_measurements_all_in_one_day-2021-09-03"

# second time
#overall_dir = "../data/bend_angle_measurements_one_day-2021-09-05"


# third time
#overall_dir = "../data/bend_angle_measurements-2021-09-07"


# fourth time
#overall_dir = "../data/35fast_actuator_bend_angle_measurements-2021-09-08"

a0_dir = overall_dir + "/a0/"
a1_dir = overall_dir + "/a1/"
a2_dir = overall_dir + "/a2/"

nem  = ["3", "B", "C", "D", "2", "F", "G", "H", "1"]
# so I think it'd be better to use the channel names instead of just
# numbers, so if I'm not mistaken:
# 3 is a0 (closest to the fingertip)
# 2 is a1 (middle joint)
# 1 is a2 (closest to the actuator mount)
#                  |
#                  V
better_nem  = ["a0", "B", "C", "D", "a1", "F", "G", "H", "a2"]


###### SINCE THERE ARE MULTIPLE FILES FOR EACH ANGLE, I SHOULD PARALLELISE THIS
###### TO BE ABLE TO READ FROM ALL FILES, BUT IN A LOOP OR SOMETHING SIMILAR


#### put all files from a0, a1, a2 into separate lists

a0_all = []
a1_all = []
a2_all = []

a0_files = glob.glob(a0_dir + "*.txt")
a1_files = glob.glob(a1_dir + "*.txt")
a2_files = glob.glob(a2_dir + "*.txt")

print("Getting a0 files")
for f in a0_files:
    txt0 = pd.read_csv(f, sep='\t', lineterminator='\n', skiprows=1)
    txt0.columns = better_nem
    a0_all.append(txt0)

print("Getting a1 files")
for f in a1_files:
    txt1 = pd.read_csv(f, sep='\t', lineterminator='\n', skiprows=1)
    txt1.columns = better_nem
    a1_all.append(txt1)

print("Getting a2 files")
for f in a2_files:
    txt2 = pd.read_csv(f, sep='\t', lineterminator='\n', skiprows=1)
    txt2.columns = better_nem
    a2_all.append(txt2)


   
# Get desired channel values
# Also get mean values from sets of 5 for each angle

a0_raw_means = []
a1_raw_means = []
a2_raw_means = []

a0_raw_stddev = []
a1_raw_stddev = []
a2_raw_stddev = []

for i in range(len(a0_all)):
    a0_all[i] = a0_all[i][["a0", "a1", "a2"]]
    a0_raw_means.append(np.mean(a0_all[i][["a0"]]))
    a0_raw_stddev.append(np.std(a0_all[i][["a0"]]))

for i in range(len(a1_all)):
    a1_all[i] = a1_all[i][["a0", "a1", "a2"]]
    a1_raw_means.append(np.mean(a1_all[i][["a1"]]))
    a1_raw_stddev.append(np.std(a1_all[i][["a1"]]))

for i in range(len(a2_all)):
    a2_all[i] = a2_all[i][["a0", "a1", "a2"]]
    a2_raw_means.append(np.mean(a2_all[i][["a2"]]))
    a2_raw_stddev.append(np.std(a2_all[i][["a2"]]))


####################### USE THIS CODE FOR 03/09/2021 DATA ONLY

all_0_deg = [a0_raw_means[0], a0_raw_means[1], a1_raw_means[0], a1_raw_means[1]]

# a0:
a00 = [ a0_all[0][["a0"]], a0_all[1][["a0"]], 
        a1_all[0][["a0"]], a1_all[1][["a0"]] ]

a0_0_m = np.mean(np.mean(a00))

a0_means  = []
a0_stddev = []
a0_means.append(a0_0_m)                         #  0 deg
a0_means.append(np.mean(a0_raw_means[2:7]))     # 10 deg
a0_means.append(np.mean(a0_raw_means[7:12]))    # 20 deg
a0_means.append(np.mean(a0_raw_means[12:17]))   # 30 deg
a0_means.append(np.mean(a0_raw_means[17:22]))   # 40 deg
a0_means.append(np.mean(a0_raw_means[22:27]))   # 50 deg
a0_means.append(np.mean(a0_raw_means[27:32]))   # 60 deg
a0_means.append(np.mean(a0_raw_means[32:37]))   # 70 deg

a0_stddev.append(np.std(a00))                   #  0 deg
a0_stddev.append(np.mean(a0_raw_stddev[2:7]))   # 10 deg
a0_stddev.append(np.mean(a0_raw_stddev[7:12]))  # 20 deg
a0_stddev.append(np.mean(a0_raw_stddev[12:17])) # 30 deg
a0_stddev.append(np.mean(a0_raw_stddev[17:22])) # 40 deg
a0_stddev.append(np.mean(a0_raw_stddev[22:27])) # 50 deg
a0_stddev.append(np.mean(a0_raw_stddev[27:32])) # 60 deg
a0_stddev.append(np.mean(a0_raw_stddev[32:37])) # 70 deg

## a1:
a10 = [ a0_all[0][["a1"]], a0_all[1][["a1"]], 
        a1_all[0][["a1"]], a1_all[1][["a1"]] ]
a1_0_m = np.mean(np.mean(a10))

a1_means  = []
a1_stddev = []
a1_means.append(a1_0_m)                         #  0 deg --> i suspect this is wrong anyway
a1_means.append(np.mean(a1_raw_means[2:6]))     # 10 deg 
a1_means.append(np.mean(a1_raw_means[6:11]))    # 20 deg
a1_means.append(np.mean(a1_raw_means[11:16]))   # 30 deg
a1_means.append(np.mean(a1_raw_means[16:21]))   # 40 deg
a1_means.append(np.mean(a1_raw_means[21:26]))   # 50 deg
a1_means.append(np.mean(a1_raw_means[26:31]))   # 60 deg
a1_means.append(np.mean(a1_raw_means[31:36]))   # 70 deg

a1_stddev.append(np.std(a10))                    #  0 deg
a1_stddev.append(np.mean(a1_raw_stddev[2:6]))   # 10 deg
a1_stddev.append(np.mean(a1_raw_stddev[6:11]))  # 20 deg
a1_stddev.append(np.mean(a1_raw_stddev[11:16])) # 30 deg
a1_stddev.append(np.mean(a1_raw_stddev[16:21])) # 40 deg
a1_stddev.append(np.mean(a1_raw_stddev[21:26])) # 50 deg
a1_stddev.append(np.mean(a1_raw_stddev[26:31])) # 60 deg
a1_stddev.append(np.mean(a1_raw_stddev[31:36])) # 70 deg


## a2:
a20 = [ a0_all[0][["a2"]], a0_all[1][["a2"]], 
        a1_all[0][["a2"]], a1_all[1][["a2"]] ]
a2_0_m = np.mean(np.mean(a20))

a2_means  = []
a2_stddev = []
a2_means.append(a2_0_m)                         #  0 deg 
a2_means.append(np.mean(a2_raw_means[:5]))      # 10 deg
a2_means.append(np.mean(a2_raw_means[5:10]))    # 20 deg
a2_means.append(np.mean(a2_raw_means[10:15]))   # 30 deg
a2_means.append(np.mean(a2_raw_means[15:20]))   # 40 deg
a2_means.append(np.mean(a2_raw_means[20:25]))   # 50 deg
a2_means.append(np.mean(a2_raw_means[25:30]))   # 60 deg
a2_means.append(np.mean(a2_raw_means[30:35]))   # 70 deg

a2_stddev.append(np.std(a20))                        #  0 deg
a2_stddev.append(np.mean(a2_raw_stddev[:5]))    # 10 deg
a2_stddev.append(np.mean(a2_raw_stddev[5:11]))  # 20 deg
a2_stddev.append(np.mean(a2_raw_stddev[10:15])) # 30 deg
a2_stddev.append(np.mean(a2_raw_stddev[15:20])) # 40 deg
a2_stddev.append(np.mean(a2_raw_stddev[20:25])) # 50 deg
a2_stddev.append(np.mean(a2_raw_stddev[25:30])) # 60 deg
a2_stddev.append(np.mean(a2_raw_stddev[30:35])) # 70 deg
####################################################

angles = [0, 10, 20, 30, 40, 50, 60, 70]

###### VALUES FROM 05/09/2021 AND BEYOND
#a0_means = []
#a1_means = []
#a2_means = []

#ind = list(range(0, len(a0_raw_means), 5))

#for i in ind:
#    a0_means.append(np.mean(a0_raw_means[i:i+4]))
#    a1_means.append(np.mean(a1_raw_means[i:i+4]))
#    a2_means.append(np.mean(a2_raw_means[i:i+4]))


#a0_stddev = []
#a1_stddev = []
#a2_stddev = []

#for i in ind:
#    a0_stddev.append(np.mean(a0_raw_stddev[i:i+4]))
#    a1_stddev.append(np.mean(a1_raw_stddev[i:i+4]))
#    a2_stddev.append(np.mean(a2_raw_stddev[i:i+4]))



anglesvec    = np.array([ angles ]).T
#a0_voltsvec  = np.array([a0_means]).T
#a1_voltsvec  = np.array([a1_means]).T
#a2_voltsvec  = np.array([a2_means]).T
#lookup_table = np.column_stack((anglesvec,   a0_voltsvec, 
#                                a1_voltsvec, a2_voltsvec))
##np.savetxt('bending_angle_lookup_table-2021-09-08.csv', lookup_table, 
##delimiter=',', fmt='%1.8f')


# plotting standard deviation results
factor = 10**2

a0_devvec = np.array([ [i * factor for i in a0_stddev] ]).T
a1_devvec = np.array([ [i * factor for i in a1_stddev] ]).T
a2_devvec = np.array([ [i * factor for i in a2_stddev] ]).T


# PLOTTING

# Angles (X) against mean voltages (Y)
angles = [0, 10, 20, 30, 40, 50, 60, 70]
plt.rcParams.update({'font.size': 18})
plt.plot(angles, a0_means, 'bo-', markersize=10)
plt.plot(angles, a1_means, 'o-', color='orange', markersize=10)
plt.plot(angles, a2_means, 'go-', markersize=10)
plt.legend(["a0", "a1", "a2"], loc='best', prop={'size': 15})
plt.xlabel("Bending angle ($^\circ$)", fontsize=22)
plt.ylabel("Voltage (V)", fontsize=22)
plt.tick_params(labelsize=19)
plt.xticks(angles)
plt.show()

# Angles (X) against mean standard deviations (Y)
plt.rcParams.update({'font.size': 18})
plt.plot(angles, a0_devvec, 'b^-', markersize=10)
plt.plot(angles, a1_devvec, 'o-', color='orange', markersize=10)
plt.plot(angles, a2_devvec, 'gx-', markersize=10)
plt.xlabel("Bending angle ($^\circ$)", fontsize=22)
plt.ylabel("Mean standard deviation (V) (x" + str(factor) + ')', fontsize=22)
#plt.title('Bending angle standard deviation values (y axis factor ' + str(factor) + 'x) : ' + overall_dir[-10:], fontsize=24)
plt.legend(["a0", "a1", "a2"], loc='best', prop={'size': 15})
plt.tick_params(labelsize=19)
plt.xticks(angles)
plt.show()

standard_devs = np.column_stack((anglesvec, a0_devvec, a1_devvec, a2_devvec))

#np.savetxt('bending_angle_standard_devs-2021-09-08.csv', 
#           standard_devs, delimiter=',', fmt='%1.8f')


exit()

