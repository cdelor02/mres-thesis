# command line args: python plot_all.py filename_here
# [--e for only electrodes, otherwise all] [hidex to hide x axis labels,
# otherwise a]

# https://cmdlinetips.com/2019/10/how-to-make-a-plot-with-two-different-y-axis-in-python-with-matplotlib/
# https://stackoverflow.com/questions/15575466/how-do-you-improve-matplotlib-image-quality
# http://jonathansoma.com/lede/algorithms-2017/classes/fuzziness-matplotlib/understand-df-plot-in-pandas/
# https://www.kite.com/python/answers/how-to-plot-a-line-of-best-fit-in-python
from   matplotlib.colors import LinearSegmentedColormap

import sys
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as ani


def get_data(table,rownum,title):
    data = pd.DataFrame(table.loc[rownum][2:]).astype(float)
    data.columns = {title}
    return data

def animate(i):
    data = df.iloc[:int(i+1)] #select data range
    p = sns.lineplot(x=data.index, y=data[title], data=data, color="r")
    p.tick_params(labelsize=17)
    plt.setp(p.lines,linewidth=7)

Writer = ani.writers['ffmpeg']
videowriter = Writer(fps=20, metadata=dict(artist='Me'), bitrate=1800)


filename    = sys.argv[1]
filenamelen = len(filename)
plottype    = sys.argv[2]
xaxisbool   = sys.argv[3]

fs = 40 #sampling frequency on the DAQ

nem  = []
cols = []

if plottype == "--e":
	nem  = ["a0", "B", "C", "D", "a1", "F", "G", "H", "a2"]
	cols = ["a0", "a1", "a2"]
else:
	nem  = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
	cols = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]


df = pd.read_csv(filename, sep='\t', lineterminator='\n', skiprows=1, names=nem)


# Plot change in voltage (so subtract initial value from all values)
#if df.shape[1] > 1:
df = df - df[:1].values.squeeze()
df[df < 0] = 0

timesc = np.linspace(0, len(df)/fs, len(df))

fig = plt.figure(figsize=(10,6))
plt.xlabel('Time (s)', fontsize=15)
plt.ylabel('Voltage change (V)', fontsize=15)
#plt.plot(timesc, df[cols])
#plt.legend(df.columns, bbox_to_anchor=(1.0, 1.0), loc='upper left')
#plt.title(filename[3:-4], fontsize=18)

# hide X axis labels, b/c the time stuff doesn't really matter
if xaxisbool == "hidex":
	x_axis = ax.axes.get_xaxis()
	x_axis.set_visible(False)

#fig.suptitle(filename)
plt.xlabel('Time (s)', fontsize=15)
plt.ylabel('Voltage change (V)', fontsize=15)
#plt.show()

color    = ['red', 'green', 'blue', 'orange']
eit_data = df[["a0", "a1", "a2"]]


small_eit_data = eit_data.values[0:len(eit_data):5]
small_timesc   = timesc[0:len(timesc):5]

## PLAY VIDEO AT AROUND 1.5x SPEED!!!

def animate(i=int):
    plt.legend(eit_data.columns, bbox_to_anchor=(1.0, 1.0), loc='upper left')
    p = plt.plot(small_timesc[:i], small_eit_data[:i]) #note it only returns the dataset, up to the point i
    for i in range(0,3):
        p[i].set_color(color[i]) #set the colour of each curve

#https://towardsdatascience.com/learn-how-to-create-animated-graphs-in-python-fce780421afe

animator = ani.FuncAnimation(fig, animate, interval = 100)#25)
# at 40 Hz, it would be 25ms interval between frames for each datapoint
# I want to speed it up considerably, to match the video

plt.show()

animator.save(r'C:\Users\Charlie\Downloads\EIT_animation.mp4', writer=writer)
