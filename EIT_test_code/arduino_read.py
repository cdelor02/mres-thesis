# python serial reading of values from arduino

import serial
import sys 

if len(sys.argv) > 2:
    device = sys.stdin.read()
else:
    device = 'COM5'

baudrate = 9600

arduino_port = serial.Serial(device, baudrate=baudrate, 
                             parity=serial.PARITY_NONE,
                             stopbits=serial.STOPBITS_ONE,
                             bytesize=serial.EIGHTBITS,
                             rtscts=False,dsrdtr=False,
                             xonxoff=False,timeout=0)

while(True):
    line = arduino_port.readline()
    print(line.strip().decode('ascii'))#.decode('utf-8'))


#while True:
#    try:
#        #print('waiting for read')
#        temp = arduino_port.readline().strip().decode('ascii')
#        print (str(temp))
#    except: UnicodeDecodeError

