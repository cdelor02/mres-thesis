import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys 

filename = sys.argv[1] #'actuator_tube.txt'
filenamelen = len(filename)

col = sys.argv[2]

df = pd.read_csv(filename, sep='\t', lineterminator='\n', skiprows=1, 
	names=["A", "B", "C", "D"])

print(df)

#plt.figure();

ax = df[[col]].plot(title=filename, xlabel="X", ylabel="Y (mV)", rot=30)

#df[['B', 'C']].plot()
plt.legend(loc='best')

ax.set_title(filename[2:filenamelen])
ax.set_xlabel('Time')
ax.set_ylabel('Voltage (mV)')

# Find smallest change peaks/troughs

#xmax = np.argmin(df[col])
#ymax = df[col][xmax]
#plt.plot(xmax, ymax, 'r+')

#plt.annotate("Point 1", (1, 4))


#plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')

plt.show()