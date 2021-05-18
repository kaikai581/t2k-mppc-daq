#!/usr/bin/env python

# my own modules
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../utilities'))
import autocorrelation_gain

# redirect output engine to avoid x11 errors
import matplotlib
matplotlib.use('Agg')

if __name__ == '__main__':
    test_file = '../data/root/led/20210202_132916_lanl_bd1_ch0-31_thr220_temp20_feb170/20210202_190253_mppc_volt57.0_thr220_gain57_temp19.9.root'
    one_file = autocorrelation_gain.MPPCLine(test_file)
    one_file.gain_from_autocorrelation(nbins=4100)