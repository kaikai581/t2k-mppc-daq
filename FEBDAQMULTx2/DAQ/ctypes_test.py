#!/usr/bin/env python

from ctypes import *

lib = './FEBDAQMULT_C.so'
dll = cdll.LoadLibrary(lib)
dll.SelectBoard.argtypes=[c_int]
dll.SelectBoard(c_int(10))