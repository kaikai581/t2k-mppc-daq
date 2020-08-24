#!/usr/bin/env python

from NESLABRTE10 import NESLABRTE10

conn = NESLABRTE10()
print(conn.set_low_temperature_limit(15))
