#!/usr/bin/env python

from datetime import datetime
from MPPCTEMPSENSOR import MPPCTEMPSENSOR

dev = MPPCTEMPSENSOR()
# print(datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
print(dev.query_temperature())
