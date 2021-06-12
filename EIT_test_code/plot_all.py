# command line args: python plot_all.py filename_here 
# [--e for only electrodes, otherwise all] [hidex to hide x axis labels, otherwise a]

# https://cmdlinetips.com/2019/10/how-to-make-a-plot-with-two-different-y-axis-in-python-with-matplotlib/
# https://stackoverflow.com/questions/15575466/how-do-you-improve-matplotlib-image-quality
# http://jonathansoma.com/lede/algorithms-2017/classes/fuzziness-matplotlib/understand-df-plot-in-pandas/
# 

from   matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy  as np
import sys 

filename    = sys.argv[1]
filenamelen = len(filename)
plottype    = sys.argv[2]
xaxisbool   = sys.argv[3]

nem  = []
cols = []

if plottype == "--e":
	nem  = ["3", "B", "C", "D", "2", "F", "G", "H", "1"]
	cols = ["1", "2", "3"]
else:
	nem  = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
	cols = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]


df = pd.read_csv(filename, sep='\t', lineterminator='\n', skiprows=1, names=nem)

#xs = np.linspace(0.0, 
#	int((len(df[["B"]]) * 0.02)), 
#	0.02)


# Plot change in voltage (so subtract initial value from all values)
df = df - df[:1].values.squeeze()
df[df < 0] = 0


ax = df[cols][120:450].plot(xlabel="X", ylabel="Y (mV)", linewidth=4, fontsize=15)
#title=filename, 

plt.legend(bbox_to_anchor=(1.0, 1.0), loc='upper left')

# hide X axis labels, b/c the time stuff doesn't really matter
if xaxisbool == "hidex":
	x_axis = ax.axes.get_xaxis()
	x_axis.set_visible(False)


mx = np.zeros(3)
my = np.zeros(3)

# Plot peaks
#for i in range(len(cols)):
#	mx[i] = np.argmax(df[cols[i]])
#	my[i] = df[cols[i]][mx[i]]
#	plt.plot(mx[i], my[i], 'r+')

#ax.set_title(filename[2:filenamelen])
ax.set_xlabel('Time', fontsize=15)
ax.set_ylabel('Change in voltage (mV)', fontsize=15)


# Find smallest change peaks/troughs
#xmax = np.argmin(df[col])
#ymax = df[col][xmax]
#plt.plot(xmax, ymax, 'r+')
#plt.annotate("Point 1", (1, 4))

#plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')


# Heat/colour map plot of electrode data
#sns.heatmap(df[["1", "2", "3"]][120:450].T, cmap ='RdYlGn')#, linewidths = 0.0, annot = True)



plt.tight_layout()
plt.show()