from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from scipy import signal
import pandas as pd
import numpy as np
import glob


ep_dir = "../data/actuator_experiments_fixed_a0-2021-09-10/"

ep_dir = "../data/copper_wire_actuator_35fast_chamber_vertical_actuator_experiments-2021-09-06/"

ep_files = glob.glob(ep_dir + "*_eit.csv") 
## remember that i changed the filename for two files in the vertical experiments directory
## change those back!

cols  = ["a0", "a1", "a2", "x", "y", "z"]

a0_std_devs = []
a1_std_devs = []
a2_std_devs = []
a0_means    = []
a1_means    = []
a2_means    = []


indices = [    [0,370],  [370,640], 
              [640,930], [930, 1230], 
           [1230, 1520], [1520, 1810], 
           [1810, 2100], [2100, 2385], 
           [2385, 2670], [2670, 2880]]



for f in ep_files:
    dat = pd.read_csv(f, sep='\t', lineterminator='\n', skiprows=1, names=cols)

    # find max value in each joint value array
    a0_mx = dat[["a0"]].max()
    a1_mx = dat[["a1"]].max()
    a2_mx = dat[["a2"]].max()
    
    #get all 10 peaks from each
    a0_peaks, _ = find_peaks(np.squeeze(dat[["a0"]]), height=float(a0_mx - a0_mx / 6))
    a1_peaks, _ = find_peaks(np.squeeze(dat[["a1"]]), height=float(a1_mx - a1_mx / 6))
    a2_peaks, _ = find_peaks(np.squeeze(dat[["a2"]]), height=float(a2_mx - a2_mx / 6))

    #plt.plot(dat[["a0"]].values) 
    #plt.plot(a0_peaks, dat[["a0"]].values[a0_peaks], "x")
    #plt.show()

    a0_dev = []
    a1_dev = []
    a2_dev = []

    for inx in indices:
        a0_dev.append(np.mean(dat[["a0"]].values[ a0_peaks[np.where(a0_peaks > inx[0]) and 
                                                           np.where(a0_peaks < inx[1])] ]))

        a1_dev.append(np.mean(dat[["a1"]].values[ a1_peaks[np.where(a1_peaks > inx[0]) and 
                                                           np.where(a1_peaks < inx[1])] ]))

        a2_dev.append(np.mean(dat[["a2"]].values[ a2_peaks[np.where(a2_peaks > inx[0]) and 
                                                           np.where(a2_peaks < inx[1])] ]))

    a0_std_devs.append(np.std(a0_dev))
    a0_means.append(np.mean(a0_dev))
    a1_std_devs.append(np.std(a1_dev))
    a1_means.append(np.mean(a1_dev))    
    a2_std_devs.append(np.std(a2_dev))
    a2_means.append(np.mean(a2_dev))
    
    # TODO: add functionality to know how many points I'm averaging over
    # aka 
    # dat[["a0"]].values[ a0_peaks[np.where(a0_peaks > indices[1][0]) and np.where(a0_peaks < indices[1][1])]]

num_episodes = list(range(1,len(a0_std_devs)+1))

fig, (ax0, ax1, ax2) = plt.subplots(3)
#fig.suptitle('Standard deviation by iteration for each joint', fontsize=22)
ax0.plot(num_episodes, a0_std_devs, 'ro-', markersize=10)
ax0.set_title('a0', fontsize=18)
ax0.set_xticks(num_episodes)
ax0.tick_params(labelsize=19)
#ax0.legend(loc='best', prop={'size': 15})
ax1.plot(num_episodes, a1_std_devs, 'go-', markersize=10)
ax1.set_title('a1', fontsize=18)
ax1.set_xticks(num_episodes)
ax1.tick_params(labelsize=19)
#ax1.legend(loc='best', prop={'size': 15})
ax2.plot(num_episodes, a2_std_devs, 'bo-', markersize=10)
ax2.set_title('a2', fontsize=18)
ax2.set_xticks(num_episodes)
ax2.tick_params(labelsize=19)
#ax2.legend(loc='best', prop={'size': 15})
fig.supxlabel('Episode', fontsize=22)
fig.supylabel('Standard deviation (V)', fontsize=22)
#plt.legend(["a0", "a1", "a2"])
#, label='a0'

fig.tight_layout()
plt.show()


fig2 = plt.figure()
plt.plot(num_episodes, a0_means, 'r^-', markersize=10, label='a0')
plt.plot(num_episodes, a1_means, 'g^-', markersize=10, label='a1')
plt.plot(num_episodes, a2_means, 'b^-', markersize=10, label='a2')
plt.xlabel('Episodes', fontsize=22)
plt.ylabel('Mean voltages (V)', fontsize=22)
plt.legend(loc='center right', prop={'size': 18})#["a0", "a1", "a2"], loc='middle right')
plt.tick_params(labelsize=20)
plt.xticks(num_episodes)
plt.locator_params(nbins=20, axis='y')
#plt.title('a0-2 means')
plt.tight_layout()
plt.show()
#plt.errorbar(num_episodes, a0_means, a0_std_devs, linestyle='None', marker='^', c='r')
#plt.errorbar(num_episodes, a1_means, a1_std_devs, linestyle='None', marker='^', c='g')
#plt.errorbar(num_episodes, a2_means, a2_std_devs, linestyle='None', marker='^', c='b')


exit()



#a0_peaks = signal.find_peaks_cwt(np.squeeze(data[["a0"]].values), np.arange(1,10))





########## FINDING SUCH MAX PEAK VALUES FOR THE WEIGHT/NOWEIGHT DATA

weightdat = pd.read_csv(ep_dir + "copper_wire_actuator_35fast_chamber_100g_weight_lift_110_steps_eit.txt",
                        sep='\t', lineterminator='\n', skiprows=1, names=["a0", "s", "s" ,"s", "a1", "s", "s", "s", "a2"])

noweightdat = pd.read_csv(ep_dir + "copper_wire_actuator_35fast_chamber_vertical_eit.txt",
                          sep='\t', lineterminator='\n', skiprows=1, names=["a0", "s", "s" ,"s", "a1", "s", "s", "s", "a2"])

weightmaxa0 = dat[["a0"]].max()
weightmaxa1 = dat[["a1"]].max()
weightmaxa2 = dat[["a2"]].max()
weightmaxa0 = weightdat[["a0"]].max()
weightmaxa1 = weightdat[["a1"]].max()
weightmaxa2 = weightdat[["a2"]].max()
noweightmaxa2 = noweightdat[["a2"]].max()
noweightmaxa1 = noweightdat[["a1"]].max()
noweightmaxa0 = noweightdat[["a0"]].max()

w0p, _ = find_peaks(np.squeeze(weightdat[["a0"]]), 
                    height=float(weightmaxa0 - weightmaxa0 / 6))
w1p, _ = find_peaks(np.squeeze(weightdat[["a1"]]), 
                    height=float(weightmaxa1 - weightmaxa1 / 6))
w2p, _ = find_peaks(np.squeeze(weightdat[["a2"]]), 
                    height=float(weightmaxa2 - weightmaxa2 / 6))

nw0p, _ = find_peaks(np.squeeze(noweightdat[["a0"]]), 
                    height=float(noweightmaxa0 - noweightmaxa0 / 6))
nw1p, _ = find_peaks(np.squeeze(noweightdat[["a1"]]), 
                    height=float(noweightmaxa1 - noweightmaxa1 / 6))
nw2p, _ = find_peaks(np.squeeze(noweightdat[["a2"]]), 
                    height=float(noweightmaxa2 - noweightmaxa2 / 6))


plt.plot(weightdat[["a0"]], 'r'); plt.plot(weightdat[["a0"]].values[np.where(w0p < indices[0][0]) and
                                                                    np.where(w0p > indices[0][1])], 'b')
plt.show()






timesc = np.linspace(0, len(df)/40, len(df))


plt.plot(timesc, df[["a0"]], label='a0', color='b', linewidth=3)
plt.plot(timesc, df[["B"]], label='B', linewidth=3)
plt.plot(timesc, df[["C"]], label='C', linewidth=3)
plt.plot(timesc, df[["D"]], label='D', linewidth=3)
plt.plot(timesc, df[["a1"]], label='a1', color='orange', linewidth=3)
plt.plot(timesc, df[["F"]], label='F', linewidth=3)
plt.plot(timesc, df[["G"]], label='G', linewidth=3)
plt.plot(timesc, df[["H"]], label='H', linewidth=3)
plt.plot(timesc, df[["a2"]], label='a2', color='g', linewidth=3)
plt.xlabel("Time (s)", fontsize=20)
plt.ylabel("Voltage change (V)", fontsize=20)
plt.tick_params(fontsize=19)
plt.legend()
plt.show()
