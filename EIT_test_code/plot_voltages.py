import matplotlib.pyplot as plt
import pandas as pd

filename = 'test.txt'

df = pd.read_csv(filename, sep='\t', lineterminator='\n', skiprows=1, 
	names=["A", "B", "C", "D"])

#print(df[['B', 'C']])

ax = df[['B', 'C']].plot()
plt.legend(loc='best')

ax.set_title(filename)
ax.set_xlabel('Samples')
ax.set_ylabel('Voltage (mV)')
plt.show()