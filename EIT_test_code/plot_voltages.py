import matplotlib.pyplot as plt
import pandas as pd
import sys 

filename = sys.argv[1] #'actuator_tube.txt'

df = pd.read_csv(filename, sep='\t', lineterminator='\n', skiprows=1, 
	names=["A", "B", "C", "D"])

#print(df[['B', 'C']])

print(df)

ax = df[['B']].plot()#df[['B', 'C']].plot()
plt.legend(loc='best')

ax.set_title(filename)
ax.set_xlabel('X')
ax.set_ylabel('Y (mV)')

df[['B']].plot(title=filename, xlabel="X", ylabel="Y (mV)", rot=30)

#plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')

plt.show()