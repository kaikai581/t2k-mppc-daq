#!/usr/bin/env python

from datetime import datetime
from T2KTEMPSENSOR import T2KTEMPSENSOR

dev = T2KTEMPSENSOR()
# print(datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
print(dev.query_temperature())
