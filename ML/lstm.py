# lstm.py
## experiment with LSTM (long short term memory) on actuator data
## by Charlie DeLorey

#https://machinelearningmastery.com/time-series-prediction-lstm-recurrent-neural-networks-python-keras/

#https://medium.com/@nutanbhogendrasharma/simple-sequence-prediction-with-lstm-69ff0f4d57cd

# this one seems followable
#https://stackabuse.com/time-series-analysis-with-lstm-using-pythons-keras-library/

from __future__ import print_function
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from keras.callbacks import EarlyStopping
from keras.models import Sequential
from keras.layers import Dropout
import matplotlib.pyplot as plt
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import *
import pandas as pd
import numpy as np
import argparse
import keras
import math 
import time
import sys
import cv2

print("hi")




