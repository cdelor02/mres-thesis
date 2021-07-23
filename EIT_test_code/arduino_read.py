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
import numpy as np
import argparse
import serial
import time
import sys 

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

# using external function, get serial ports currently in use
# (not sure if it will always select the Arduino one, but 
# it seems to work for now)
res = serial_ports()

if res == []:
    print("No ports found. Are you sure the Arduino is plugged in?")
    print("While you're at it, make sure the motor controller is plugged in")
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

while(True):
    if (arduino_port.inWaiting() > 0):
        reply = arduino_port.readline(arduino_port.inWaiting()).strip()#(arduino_port.inWaiting())#.strip()
        #arduino_port.reset_input_buffer()
        reply = reply.decode('utf-8')#'ascii', errors='ignore')
        print(reply)
        stepper_motor_vals = np.append(stepper_motor_vals, reply)
    time.sleep(0.01)

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
step_cpy = stepper_motor_vals.astype(int)
step_cpy = np.c_[step_cpy]

#np.savetxt("./" + directory + "/" + filename, step_cpy, #np.c_[stepper_motor_vals], 
#           fmt="%d", delimiter=",")

