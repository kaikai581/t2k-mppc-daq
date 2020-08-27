#!/usr/bin/env python

import os
# Load event classes
# Ref: https://root-forum.cern.ch/t/wrapping-root-classes-for-python/21845/2
# Load the library and include the header file
from ROOT import gInterpreter, gSystem
gInterpreter.ProcessLine('#include "{}"'.format(os.path.join(os.path.expandvars('$DT5702_PATH'), 'FEBDTP_LinkDef.h')))
gSystem.Load(os.path.expandvars('$DT5702_PATH/libFEBDTP'))

import ROOT
dev = ROOT.FEBDTP('enp0s31f6')
dev.ScanClients()
# dev.Init_FEBDTP_pkt()
dev.Print_gpkt(0)