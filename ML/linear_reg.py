# Closed-loop control for EIT actuator project
# by Charlie DeLorey

# Linear regression tutorial
# https://towardsdatascience.com/simple-machine-learning-model-in-python-in-5-lines-of-code-fe03d72e78c6

from __future__ import print_function
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from random import randint
from scipy import stats
import pandas as pd
import numpy as np
import argparse
import time
import sys
import cv2


## Generate dataset
#from random import randint
#TRAIN_SET_LIMIT = 1000
#TRAIN_SET_COUNT = 100

#TRAIN_INPUT = list()
#TRAIN_OUTPUT = list()
#for i in range(TRAIN_SET_COUNT):
#    a = randint(0, TRAIN_SET_LIMIT)
#    b = randint(0, TRAIN_SET_LIMIT)
#    c = randint(0, TRAIN_SET_LIMIT)
#    op = a + (2*b) + (3*c)
#    TRAIN_INPUT.append([a, b, c])
#    TRAIN_OUTPUT.append(op)

step_data = pd.read_csv("../EIT_test_code/stepper_values/copper_actuator_test_fixed_2021-08-09.csv",
                          sep='\t', lineterminator='\n', skiprows=1, names=["steps"])
eit_data  = pd.read_csv("../EIT_test_code/copper_actuator_test_fixed.txt", 
                      sep='\t', lineterminator='\n', skiprows=1, 
                      names=["3", "B", "C", "D", "2", "F", "G", "H", "1"])
eit_data = eit_data[["1", "2", "3"]]

theta_data = pd.read_csv("../computer_vision/copper_actuator_test_fixed-thetas-2021-08-09.csv",
                         sep='\t', lineterminator='\n', names=["ts"])

#removal of large spikes, as per this tutorial
# https://becominghuman.ai/linear-regression-in-python-with-pandas-scikit-learn-72574a2ec1a5
std_dev = 3
step_data = step_data[(np.abs(stats.zscore(step_data)) < float(std_dev)).all(axis=1)]
#????????

theta_data = pd.DataFrame(theta_data)
# input data: step data | eit joint 1 | eit joint 1 | eit joint 3 |
concat_data = pd.concat([step_data.iloc[0:len(theta_data), 0],
                                  eit_data["1"].iloc[0:len(theta_data)],
                                  eit_data["2"].iloc[0:len(theta_data)],
                                  eit_data["3"].iloc[0:len(theta_data)]],
                                  axis=1)

X_train = concat_data["steps"].head(30)
X_test  = concat_data["steps"].head(len(theta_data)-30)

y_train = theta_data.head(30)
y_test  = theta_data.head(len(theta_data)-30)


TRAIN_INPUT  = concat_data#step_data.iloc[0:len(theta_data),0]
TRAIN_OUTPUT = theta_data#eit_data.iloc[:,0]

## The learning begins
predictor = LinearRegression()#n_jobs=-1)
predictor.fit(X_train, y_train)#X=TRAIN_INPUT, y=TRAIN_OUTPUT)

#index [346]
#X_TEST = [[25, 0.261, 0.2593, 0.36]]
outcome = predictor.predict(X_test)#X=X_TEST)
coefficients = predictor.coef_

print('Outcome : {}\nCoefficients : {}'.format(outcome, coefficients))
# https://scikit-learn.org/stable/auto_examples/linear_model/plot_ols.html
print('Mean squared error: %.2f' % mean_squared_error(y_test, outcome))
print('Coefficient of determination: %.2f' % r2_score(y_test, outcome))

# Plot outputs
plt.scatter(X_test, y_test,  color='black')
plt.plot(X_test, outcome, color='blue', linewidth=3)

plt.xticks(())
plt.yticks(())
plt.title("Linear regression test: only steps as training feature")

plt.show()