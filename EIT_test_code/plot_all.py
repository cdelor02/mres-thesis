# command line args: python plot_all.py filename_here
# [--e for only electrodes, otherwise all] [hidex to hide x axis labels,
# otherwise a]

# https://cmdlinetips.com/2019/10/how-to-make-a-plot-with-two-different-y-axis-in-python-with-matplotlib/
# https://stackoverflow.com/questions/15575466/how-do-you-improve-matplotlib-image-quality
# http://jonathansoma.com/lede/algorithms-2017/classes/fuzziness-matplotlib/understand-df-plot-in-pandas/
# https://www.kite.com/python/answers/how-to-plot-a-line-of-best-fit-in-python

#https://dfrieds.com/data-visualizations/style-plots-python-matplotlib.html
from   matplotlib.colors import LinearSegmentedColormap
#import butter
import matplotlib.pyplot as plt
from   scipy import signal
import seaborn as sns
import pandas as pd
import numpy  as np
import sys 

# Arduino parameters
baudrate           = 115200
spool_circum         = 31.4 #mm
stepsPerRevolution = 200
stepsPer1mm        = 1 / (spool_circum/stepsPerRevolution)

## Converting between steps and millimetres
def stepToDist(num_steps):
    return num_steps / stepsPer1mm

def distToStep(dist):
    return dist * stepsPer1mm

def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def butter_highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y

filename    = sys.argv[1]
filenamelen = len(filename)
plottype    = sys.argv[2]
xaxisbool   = sys.argv[3]

fs = 40 #sampling frequency on the DAQ

nem  = []
cols = []

if plottype == "--e":
	nem  = ["a0", "B", "C", "D", "a1", "F", "G", "H", "a2"]#["3", "B", "C", "D", "2", "F", "G", "H", "1"]
	cols = ["a0", "a1", "a2"]
else:
	nem  = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
	cols = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]


data = pd.read_csv(filename, sep='\t', lineterminator='\n', skiprows=1, names=nem)

# Plot change in voltage (so subtract initial value from all values)
#if df.shape[1] > 1:
df = data - data[:1].values.squeeze()
df[df < 0] = 0


# hide X axis labels, b/c the time stuff doesn't really matter
if xaxisbool == "hidex":
	x_axis = ax.axes.get_xaxis()
	x_axis.set_visible(False)


# Plot peaks
#for i in range(len(cols)):
#	mx[i] = np.argmax(df[cols[i]])
#	my[i] = df[cols[i]][mx[i]]
#	plt.plot(mx[i], my[i], 'r+')

### !! create time X axis scale using freq
timesc = np.linspace(0, len(df)/fs, len(df))

fig = plt.figure()
plt.plot(timesc, df[["a2", "a0", "a1"]], linewidth=3)
plt.legend([df.columns[0], df.columns[4], df.columns[8]], 
		   bbox_to_anchor=(1.0, 1.0), loc='best', prop={'size': 22})
#fig.suptitle(filename[3:-4], fontsize=20)
plt.xlabel('Time (s)', fontsize=22)
plt.ylabel('Voltage change (V)', fontsize=22)
plt.tick_params(labelsize=17)
#plt.subplots_adjust(right=0.874, left=0.083)
plt.show()


######## LOOKUP TABLE PLOTTING
#lookup_table = pd.read_csv('bending_angle_lookup_table-2021-09-08.csv', 
#						   sep=',', lineterminator='\n', 
#						   names=["angles", "a0", "a1", "a2"])

#std_dev_table = pd.read_csv('bending_angle_standard_devs-2021-09-08.csv',
#							sep=',', lineterminator='\n',
#							names=["angles", "a0", "a1", "a2"])

#new_lookup_table = lookup_table.copy()

#new_lookup_table[["a0", "a1", "a2"]] = lookup_table[["a0", "a1", "a2"]].values - lookup_table[["a0", "a1", "a2"]].iloc[0].values


##eit_data = df[["a0", "a1", "a2"]]
##eit_data.plot()


#timesc = np.linspace(0, len(data)/fs, len(data))

#plt.plot(timesc, df[["a1", "a2"]])
#plt.plot(new_lookup_table[["angles"]], new_lookup_table[["a1", "a2"]])
#plt.title('does this one work?')
#plt.show()




############## PLOTTING WEIGHT VS NO WEIGHT EIT DATA

#withweightfilename = '../data/copper_wire_actuator_35fast_chamber_vertical_actuator_experiments-2021-09-06/copper_wire_actuator_35fast_chamber_100g_weight_lift_110_steps_eit.txt'

#weight_data = pd.read_csv(withweightfilename, sep='\t', lineterminator='\n', skiprows=1, names=nem)
## wrong size
#weight_timesc= np.linspace(0, len(weight_data)/fs, len(weight_data))


#weight_data         = weight_data[["a0", "a1", "a2"]]
#weight_data.columns = ["wa0", "wa1", "wa2"]
#noweight_data       = data[["a0", "a1", "a2"]]

#plt.plot(timesc, noweight_data[["a0"]], 'b', label='a0', linewidth=3)
#plt.plot(timesc, noweight_data[["a1"]], color='orange', label='a1', linewidth=3)
#plt.plot(timesc, noweight_data[["a2"]], 'g', label='a2', linewidth=3)

#plt.plot(weight_timesc, weight_data[["wa0"]], 'b--', label='wa0', linewidth=3)
#plt.plot(weight_timesc, weight_data[["wa1"]], '--', color='orange', label='wa1', linewidth=3)
#plt.plot(weight_timesc, weight_data[["wa2"]], 'g--', label='wa2', linewidth=3)

#plt.legend(loc='best',           prop={'size': 22})
#plt.xlabel('Time (s)',           fontsize=22)
#plt.ylabel('Voltage change (V)', fontsize=22)
#plt.tick_params(labelsize=17)
#plt.show()


#fig, (ax0, ax1, ax2) = plt.subplots(3)#, figsize=(5,6), dpi=400)
##fig.suptitle('Standard deviation by iteration for each joint', fontsize=22)
#ax0.plot(timesc, noweight_data[["a0"]], 'b', markersize=10, label='a0')
#ax0.plot(weight_timesc, weight_data[["wa0"]], 'b--', markersize=10, label='wa0')
#ax0.set_title('No weight (a0) vs weight (wa0)', fontsize=18)
#ax0.tick_params(labelsize=19)
#ax0.legend(loc='best', prop={'size': 15})

#ax1.plot(timesc, noweight_data[["a1"]], color='orange', markersize=10, label='a1')
#ax1.plot(weight_timesc, weight_data[["wa1"]], '--', color='orange', markersize=10, label='wa1')
#ax1.set_title('No weight (a1) vs weight (wa1)', fontsize=18)
#ax1.tick_params(labelsize=19)
#ax1.legend(loc='best', prop={'size': 15})

#ax2.plot(timesc, noweight_data[["a2"]], 'g', markersize=10, label='a2')
#ax2.plot(timesc, noweight_data[["a1"]], 'g--', markersize=10, label='wa2')
#ax2.set_title('No weight (a2) vs weight (wa2)', fontsize=18)
#ax2.tick_params(labelsize=19)
#ax2.legend(loc='center right', prop={'size': 15})

#fig.supxlabel('Time (s)', fontsize=22)
#fig.supylabel('Voltage change (V)', fontsize=22)

#fig.tight_layout()
#plt.show()





exit()





# some sorting
#idx0 = np.argsort(df[["a0"]][110:len(df)-1].values)
from scipy.signal import find_peaks

#mx = df[["a1"]].max()
#mx = mx * .75
#peaks, _ = find_peaks(np.squeeze(df[["a1"]]).values, height=.08, distance=100)
#plt.plot(timesc, df[["a1"]])
#plt.plot(timesc[peaks], df[["a2"]].values[peaks])
#plt.title('finding peaks in EIT data (a1)')
#plt.show()

#height=.04 for a2 in 

#df[["a1"]].max()


# filtering attempts
#filt_df = butter_highpass_filter(np.squeeze(df[["a0"]]), .1, fs)

#plt.plot(timesc, filt_df)
#plt.title('filtered a0 df')
#plt.show()

############### ***** NEED TO DO SOME FILTERING ON THESE CHANNELS (a1 at least)


l = timesc[0]
r = timesc[len(timesc)-1]

plt.plot(timesc, df[["a2"]])

#plt.gca().set_color_cycle(['red', 'green', 'blue', 'cyan', 'magenta', 'yellow', 'black', 'sienna'])
#plt.gca().set_prop_cycle(plt.cycler('color', plt.cm.jet(np.linspace(0, 1, len(lookup_table)*10 ))))

colors = ['red', 'green', 'blue', 'cyan', 'magenta', 'yellow', 'black', 'sienna']

#for a in range(len(lookup_table)):
plt.hlines(lookup_table[["a2"]], l, r, colors)

angles = lookup_table[["angles"]].values
plt.title('EIT data (joint a2)')
plt.legend(angles, loc='upper left')
plt.show()




#plot all and plot all lookup table values (by joint, a0-2)
#figa, (ax0, ax1, ax2) = plt.subplots(3)
#figa.suptitle('lookup table values plotted with respective joints')

#ax0.plot(data[["a0"]])
#ax0.set_title("a0")

#l, r = ax0.get_xlim()

#ax0.hlines(lookup_table[["a0"]], l+200, r+200, colors)

#ax1.plot(data[["a1"]])
#ax1.set_title("a1")
##l, r = plt.xlim()
#ax1.hlines(lookup_table[["a1"]], l+200, r+200, colors)

#ax2.plot(data[["a2"]])
#ax2.set_title("a2")
##l, r = plt.xlim()
#ax2.hlines(lookup_table[["a2"]], l+200, r+200, colors)

#plt.subplots_adjust(bottom=1.1, top=1.2)
#plt.show()



exit()


##### PLOT THE JOINT ANGLE MEASUREMENT DATA FROM 25/08/2021
#eit_data_a0 = pd.read_csv("../data/joint_angle_measurements-2021-08-24/joint_a0_angle_measurement.txt",
#						  sep='\t', lineterminator='\n', skiprows=1)

#eit_data_a1 = pd.read_csv("../data/joint_angle_measurements-2021-08-24/joint_a1_angle_measurement.txt",
#						  sep='\t', lineterminator='\n', skiprows=1)

#eit_data_a2 = pd.read_csv("../data/joint_angle_measurements-2021-08-24/joint_a2_angle_measurement.txt",
#						  sep='\t', lineterminator='\n', skiprows=1)

#eit_data_a0.columns = ["a", "b", "c"] #a
#eit_data_a1.columns = ["a", "b", "c"] #b
#eit_data_a2.columns = ["a", "b", "c"] #c

#eit_data_a2 = eit_data_a2[0:3040]

#eit_data_a0["a"].plot(); eit_data_a1["b"].plot(); eit_data_a2["c"].plot(); plt.title('a0-2 angle measuremtnts (2021-08-24)'); plt.show()

# CAN"T REALLY DO THIS CAUSE THEY"RE DIFFERENT SIZES
#eit_data_j = pd.concat([eit_data_a0["a"], eit_data_a1["b"], eit_data_a2["c"]], 
#					   axis=1)



# Find smallest change peaks/troughs
#xmax = np.argmin(df[col])
#ymax = df[col][xmax]
#plt.plot(xmax, ymax, 'r+')
#plt.annotate("Point 1", (1, 4))

#plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')


# Heat/colour map plot of electrode data
#sns.heatmap(df[["1", "2", "3"]][120:450].T, cmap ='RdYlGn')#, linewidths =
#0.0, annot = True)



# Create approximate of cablelengths (for incremental data)
#cablelens = np.zeros(len(df))
#cablelens = np.zeros(len(df[120:430]))
#cablelens[0:140] = 0
#cablelens[180:220] = 5
#cablelens[260:296] = 10
#cablelens[330:364] = 15
#cablelens[383:430] = 20

#cablelens[0:179] = np.linspace(0.0, 5.0, 179)
#cablelens[179] = 5.0

#cablelens[220:259] = np.linspace(5.0, 10.0, len(cablelens[220:259]))
#cablelens[259] = 10.0

#cablelens[296:330] = np.linspace(10.0, 15.0, len(cablelens[296:330]))

#cablelens[364:383] = np.linspace(15.0, 20.0, len(cablelens[364:383]))


#m, b = np.polyfit(cablelens, df[["1", "2", "3"]], 1)
#plt.plot(cablelens[120:430], df[["1"]][120:430])
#plt.tight_layout()
#plt.show()


eit_data  = df
stepfile = '../data/copper_actuator_test_fixed-2021-08-09/copper_actuator_test_fixed_2021-08-09.csv'
step_data = pd.read_csv(stepfile, sep='\t', lineterminator='\n')

#ss_data = s_data.iloc[::2]
#ss_data.reset_index()

## code for plotting eit data vs stepper data on the same plot, 2 diff y axes
plt.rcParams.update({'font.size': 17})
eit_data_trunc = eit_data[["a0", "a1", "a2"]][:-4]
steps_in_mm    = stepToDist(step_data)
steps_in_mm    = steps_in_mm[0:len(steps_in_mm):2]

eit_data_trunc = eit_data_trunc[6:] #remove some values to make plotting better

### !! create time X axis scale using freq
timesc = np.linspace(0, len(eit_data_trunc)/fs, len(eit_data_trunc))

figuresavename = "from_copper_actuator_test_fixed-EIT_vs_cable_pull_data--5_iterations_bigger_font"
fig, ax = plt.subplots()
ax.plot(eit_data_trunc, linewidth=4)#, color=["g", "c", "m"])#'r')
ax.set_xlabel("Time (s)", fontsize=20)
ax.set_ylabel("EIT (V)",  fontsize=20)
#increment  = eit_data_trunc["1"][np.argmax(eit_data_trunc["1"])] / 4
#ax.set_ylim([increment,   
#			 eit_data_trunc["1"][np.argmax(eit_data_trunc["1"])]+increment])
ax.set_ylim([0.98, 1.17])
#ax.legend(loc='upper left')
xticks(timesc)

ax2 = ax.twinx()
ax2.plot(steps_in_mm, 'b', linewidth=4)
ax2.set_ylabel("Cable length (mm)", color="blue", fontsize=18)
plt.legend(eit_data_trunc.columns)
plt.title(figuresavename, fontsize=20)
plt.show()

fig.savefig(figuresavename + "_2.jpg", format='jpeg', dpi=600, bbox_inches='tight')
