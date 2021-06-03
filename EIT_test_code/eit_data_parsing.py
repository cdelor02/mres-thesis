# data parsing and cleaning

import pandas as pd
import sys

filename = sys.argv[1]

df = pd.read_csv(filename, sep='\t', lineterminator='\n', skiprows=1, 
	names=["A", "B", "C", "D"])

new_df = df[["A"]]

new_df.to_csv(filename[:-4]+'_parsed'+'.txt', sep='\t', line_terminator='\n', float_format='%.6f')