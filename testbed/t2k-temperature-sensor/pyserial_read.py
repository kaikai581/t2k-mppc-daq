#!/usr/bin/env python

from datetime import datetime
import argparse
import serial, sys
import time

parser = argparse.ArgumentParser(description='Command line options.')
parser.add_argument('--windows', action='store_true')
args = parser.parse_args()

if args.windows:
    port_name = 'COM1'
else:
    port_name = '/dev/ttyUSB0'

sr = serial.Serial(
    port=port_name,
    baudrate=115200,
    parity=serial.PARITY_NONE,
    bytesize=serial.EIGHTBITS,
    timeout=None
)

if not sr.isOpen():
    print('Fail to connect to RS232.')
    sys.exit()

# Issue command to start reading.
run_cmd = 'run 1\r'
sr.write(run_cmd.encode())
# Flush the buffer
rb = sr.readline().decode()

print('Enter your commands below.\r\nInsert "exit" to leave the application or carrier return to retrieve readings.')

_input=1
while 1 :
    # get keyboard input
    _input = input(">> ")

    if _input == 'exit':
        sr.close()
        exit()
    else:

        rb = sr.readline().decode()
        while 'run 1' in rb:
            rb = sr.readline().decode()
        print(datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
        print(rb)