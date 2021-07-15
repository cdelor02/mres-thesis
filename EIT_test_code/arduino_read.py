# python serial reading of values from arduino

#https://stackoverflow.com/questions/34009653/convert-bytes-to-int
#https://stackoverflow.com/questions/49566331/pyserial-how-to-continuously-read-and-parse
#https://stackoverflow.com/questions/19908167/reading-serial-data-in-realtime-in-python

import serial
import time
import sys 
from serial_ports import serial_ports

res = serial_ports()

if len(sys.argv) > 2:
    device = sys.stdin.read()
else:
    device = res[0] # or 'COM5'
                    # not sure if this will always 
                    # select the *correct* port

baudrate           = 9600
spool_diam         = 31.4
stepsPerRevolution = 200
stepsPer1mm        = 1 / (spool_diam/stepsPerRevolution)


arduino_port = serial.Serial(device, baudrate=baudrate, 
                             parity=serial.PARITY_NONE,
                             stopbits=serial.STOPBITS_ONE,
                             bytesize=serial.EIGHTBITS,
                             rtscts=False,dsrdtr=False,
                             xonxoff=False,timeout=None)


## Checking byte-ness
#type(int.from_bytes(a.to_bytes(1, byteorder='little'), byteorder='little'))
#bytes(reply, encoding='utf-8')


arduino_port.reset_input_buffer()
arduino_port.reset_output_buffer()
arduino_port.flush()

while(True):
    #val = input()
    #arduino_port.write(bytes(val, encoding='utf-8'))
    #arduino_port.flush()
    
    #time.sleep(0.5)
    if (arduino_port.inWaiting() > 0):
    # find out how to make it wait for data
    # make sure  buffers dont get overwhelmeds
    # something that listens in the background
        reply = arduino_port.readline(arduino_port.inWaiting()).strip()#(arduino_port.inWaiting())#.strip()
        #arduino_port.reset_input_buffer()
        reply = reply.decode('utf-8')#'ascii', errors='ignore')
        print("reply:", reply)
    time.sleep(0.01)

exit()


#while True:
#    try:
#        #print('waiting for read')
#        temp = arduino_port.readline().strip().decode('ascii')
#        print (str(temp))
#    except: UnicodeDecodeError


## Converting between steps and millimetres
def stepToDist(num_steps):
    return num_steps / stepsPer1mm

def distToStep(dist):
    return dist * stepsPer1mm