#!/usr/bin/env python

from N6700B import N6700B
import time

dev = N6700B('169.254.130.161')
dev.set_voltage(4, 5)
dev.power_on(4)
time.sleep(10)
dev.power_off(4)