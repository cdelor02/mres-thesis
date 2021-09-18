# Python serial reading of values from arduino
# Charlie DeLorey

#https://stackoverflow.com/questions/34009653/convert-bytes-to-int
#https://stackoverflow.com/questions/49566331/pyserial-how-to-continuously-read-and-parse
#https://stackoverflow.com/questions/19908167/reading-serial-data-in-realtime-in-python


"""
TODO/things to be aware of:

- find out how to make it wait for data
- make sure  buffers dont get overwhelmed 
    --> something that listens in the background?
"""

from serial_ports import serial_ports
from datetime import datetime
import numpy as np
import argparse
import serial
import time
import sys 
import os

# Some command line argument parsing for usability
parser = argparse.ArgumentParser(description='MRes project Arduino serial \
                                              reading script')
parser.add_argument('filename', type=str, help='destination filename \
                                                for saved stepper motor vals \
                                                (include the filetype suffix!)')
#parser.add_argument('prt',  type=str, help='COM port')
args      = parser.parse_args()
filename  = args.filename
directory = "stepper_values" # hardcoded for now
filename  = filename[:-4]

# using external function, get serial ports currently in use
# (not sure if it will always select the Arduino one, but 
# it seems to work for now)
res = serial_ports()

if res == []:
    print("No ports found. Are you sure the Arduino is plugged in?")
    print("While you're at it, make sure the motor controller is plugged in!")
    exit(1)

if len(sys.argv) > 2:
    device = sys.stdin.read()
elif len(res) != 0:
    device = res[0]
else:
    device = "COM5"


# Arduino parameters
baudrate           = 115200
spool_diam         = 31.4 #mm
stepsPerRevolution = 200
stepsPer1mm        = 1 / (spool_diam/stepsPerRevolution)

## Converting between steps and millimetres
def stepToDist(num_steps):
    return num_steps / stepsPer1mm

def distToStep(dist):
    return dist * stepsPer1mm


arduino_port = serial.Serial(device, baudrate=baudrate, 
                             parity=serial.PARITY_NONE,
                             stopbits=serial.STOPBITS_ONE,
                             bytesize=serial.EIGHTBITS,
                             rtscts=False,dsrdtr=False,
                             xonxoff=False,timeout=None)


## Checking byte-ness; not currently necessary but kept for posterity
#type(int.from_bytes(a.to_bytes(1, byteorder='little'), byteorder='little'))
#bytes(reply, encoding='utf-8')

# clean out Arduino serial buffers
arduino_port.reset_output_buffer()
arduino_port.reset_input_buffer()
arduino_port.flush()

# numpy array to store stepper motor values
stepper_motor_vals = np.array([])


## Commence handshake
#respo = arduino_port.readline(arduino_port.inWaiting()).strip()
#print("first respo:", respo)
#arduino_port.write(b'-1')
#arduino_port.flush()
#respo = 0
##time.sleep(1)

#respo = arduino_port.readline(arduino_port.inWaiting()).strip()
#respo = respo.decode('utf-8')
#if respo == '':
#    respo = 0 
#else: 
#    respo = int(respo)

#print("response:", respo)


## clean out Arduino serial buffers
#arduino_port.reset_output_buffer()
#arduino_port.reset_input_buffer()
#arduino_port.flush()

#print("ending")

while(True):
    if (arduino_port.inWaiting() > 0):
        reply = arduino_port.readline(arduino_port.inWaiting()).strip()#(arduino_port.inWaiting())#.strip()
        #arduino_port.reset_input_buffer()
        reply = reply.decode('utf-8')#'ascii', errors='ignore')
        #print(reply)
        if reply == "-1":
            break
        stepper_motor_vals = np.append(stepper_motor_vals, reply)
    #time.sleep(0.02)

#exit()

# try-except example, in case this makes more sense to use down the road
#while True:
#    try:
#        #print('waiting for read')
#        temp = arduino_port.readline().strip().decode('ascii')
#        print (str(temp))
#    except: UnicodeDecodeError

# postprocessing of stepper values into a .csv file
#stepper_motor_vals = stepper_motor_vals.astype(int) # I hope this is the right int

##** there's an issue with some of the datapoints, so I just
##   replace them with the previous value

empties = np.where(stepper_motor_vals == '')
for em in empties:
    stepper_motor_vals[em] = stepper_motor_vals[em-1]

step_cpy = stepper_motor_vals.astype(int)
step_cpy = np.c_[step_cpy]

## Get current date for concatenation to datafile (for bookkeeping)
today     = datetime.now()
todaydate = today.strftime("%Y-%m-%d")

########## THIS DOESN'T WORK
incr = 0
savename = directory + "/" + filename + "-" + todaydate# + ".csv"
while os.path.exists(savename + ".csv"):
    print("Checking for file", incr)
    incr += 1

savename = savename + "_" + str(incr) + ".csv"
print("Saving data to ", savename)

# https://stackoverflow.com/questions/24106575/numpy-savetxt-to-csv-with-integer-integer-string
np.savetxt("./" + savename, step_cpy, fmt="%d", delimiter=",")

#https://stackoverflow.com/questions/19609631/python-changing-row-index-of-pandas-data-frame
#stepper_data = pd.read_csv(stepper filehere,...)
#eit_data = pd.read_csv(eit filehere,...)
#s_data.index=range(s_data.shape[0])
#e_data = eit_data[["1", "2", "3"]]
