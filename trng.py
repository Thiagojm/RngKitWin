# !/usr/bin/python

# TrueRNG Read - Simple Example
# Chris K Cockrum
# 8/21/2016
#
# Requires Python 2.7, pyserial
# On Linux - may need to be root or set /dev/tty port permissions to 666
#
# Python 2.7.xx is available here: https://www.python.org/
# Install Pyserial package with:   python -m pip install pyserial

import serial
from serial.tools import list_ports

# Size of block for each loop
blocksize = 256

# Number of loops
numloops = 10

# Create ports variable as dictionary
ports = dict()

# Call list_ports to get com port info
ports_avaiable = list(list_ports.comports())

# Set default of None for com port
rng_com_port = None

# Loop on all available ports to find TrueRNG
for temp in ports_avaiable:
    if temp[1].startswith("TrueRNG"):
        if rng_com_port == None:  # always chooses the 1st TrueRNG found
            rng_com_port = str(temp[0])


# Open/create the file random.bin in the current directory with 'write binary'
fp = open('random.bin', 'ab+')

# Print an error if we can't open the file
if fp == None:
    print('Error Opening File!')

# Try to setup and open the comport
try:
    ser = serial.Serial(port=rng_com_port, timeout=10)  # timeout set at 10 seconds in case the read fails
except:
    print('Port Not Usable!')
    print('Do you have permissions set to read ' + rng_com_port + ' ?')

# Open the serial port if it isn't open
if (ser.isOpen() == False):
    ser.open()

# Set Data Terminal Ready to start flow
ser.setDTR(True)

# This clears the receive buffer so we aren't using buffered data
ser.flushInput()

# Try to read the port and record the time before and after
try:
    x = ser.read(blocksize)  # read bytes from serial port
except:
    print('Read Failed!!!')

    # If we were able to open the file, write to disk
if fp != 0:
    fp.write(x)

# Close the serial port
ser.close()

# If the file is open then close it
if fp != 0:
    fp.close()