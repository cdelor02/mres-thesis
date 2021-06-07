import matplotlib.pyplot as plt
import pandas as pd
import numpy  as np
import sys 

filename    = sys.argv[1]
filenamelen = len(filename)
plottype    = sys.argv[2]

nem  = []
cols = []

if plottype == "--e":
	nem  = ["3", "B", "C", "D", "2", "F", "G", "H", "1"]
	cols = ["1", "2", "3"]
else:
	nem  = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
	cols = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]


df = pd.read_csv(filename, sep='\t', lineterminator='\n', skiprows=1, names=nem)

print(df)

#plt.figure();


ax = df[cols].plot(title=filename, xlabel="X", ylabel="Y (mV)")#, rot=30)

plt.legend(bbox_to_anchor=(1.0, 1.0), loc='upper left')#loc='upper left')#best')

ax.set_title(filename[2:filenamelen])
ax.set_xlabel('Time')
ax.set_ylabel('Voltage (mV)')


# Find smallest change peaks/troughs
#xmax = np.argmin(df[col])
#ymax = df[col][xmax]
#plt.plot(xmax, ymax, 'r+')

#plt.annotate("Point 1", (1, 4))

#plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')

plt.tight_layout()
plt.show()