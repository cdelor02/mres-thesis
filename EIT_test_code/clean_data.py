## EIT data cleaning
# https://stackoverflow.com/questions/20618804/how-to-smooth-a-curve-in-the-right-way
# uses a Savitzky-Golar filter as described above

from __future__ import print_function

from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
from datetime import datetime
from random import randint
import pandas as pd
import numpy as np
import argparse
import math
import time
import sys
import cv2
import os

# Some command line argument parsing for usability
parser = argparse.ArgumentParser(description='Data cleaning for EIT')
parser.add_argument('filename', type=str, help='source file')
parser.add_argument('windowlength', type=int, help='must be shorter than data')
parser.add_argument('polynomial', type=int, help='must be less than window length')
args       = parser.parse_args()
filename   = args.filename
window_len = args.windowlength
polyord    = args.polynomial
directory  = "./EIT_test_code"


eit_data = pd.read_csv(filename,#directory + filename,
                                sep='\t', lineterminator='\n',
                                skiprows=1)

cleaned_data = eit_data

for i in range (eit_data.shape[1]):
    cleaned_data.iloc[:,i] = savgol_filter(eit_data.iloc[:,i],
                                           window_len, polyord)

filetype = filename[5:]
filename = filename[:-4]

np.savetxt(filename + "_cleaned" + filetype,#directory + filename + "_cleaned" + filetype, 
           cleaned_data, delimiter=",")