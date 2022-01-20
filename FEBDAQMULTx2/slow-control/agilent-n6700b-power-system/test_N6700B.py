#!/usr/bin/env python

from N6700B import N6700B
import time

# dev = N6700B('169.254.130.161') # default ip, changed since connected to the switch
dev = N6700B('192.168.0.201')
dev.set_voltage(4, 5)
dev.power_on(4)
print(dev.query_voltage(4))
time.sleep(10)
dev.power_off(4)
