#!/usr/bin/env python

import argparse
from NESLABRTE10 import NESLABRTE10

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--start', action='store_true')
args = parser.parse_args()

conn = NESLABRTE10()

print(conn.read_low_temperature_limit())

cmd = conn.set_low_temperature_limit(15)
print(cmd)
print(hex(conn.checksum(b'\xca\x00\x01\x20\x00')))
print(hex(conn.checksum(b'\xca\x00\x01\x20\x03\x11\x02\x71')))
print(hex(conn.checksum(b'\xcc\x00\x03\xf0\x02\x01\x2c')))
print(hex(conn.checksum(b'\xcc\x00\x03\xf0\x03\x11\x01\x2c')))
print(hex(conn.checksum(b'\xca\x00\x01p\x03\x11\x01r')))

print('Set point:', conn.read_setpoint())
print('Setting to:', conn.set_setpoint(21))
print('Set point:', conn.read_setpoint())
print('Internal temperature:', conn.read_internal_temperature())

# start the unit
if args.start:
    print('Turn on!\nResponse from the circulator:', conn.set_on_array())
    input('Press enter to stop the circulator.')
    print('Turn off!\nResponse from the circulator:', conn.set_off_array())
