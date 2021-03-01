#!/usr/bin/env python

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../utilities'))

# get rid of x11 requirement
import matplotlib
matplotlib.use('Agg')

import argparse
import software_threshold_scan

if __name__ == '__main__':
    # command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_files', type=str, nargs='*', default='../data/root/dark/20210203_volt58_ch32-63_feb170/20210203_171439_dark_rate_feb0_ch0_thr*.root')
    parser.add_argument('-l', '--led_file', type=str, default='../data/root/led/20210203_102342_lanl_bd1_ch32-63_thr220_temp20_feb170/20210203_130526_mppc_volt58.0_thr220_gain52_temp19.9.root')
    args = parser.parse_args()
    infpns = args.input_files

    my_scan = software_threshold_scan.adc_scan(args.input_files, args.led_file, pcb_half=1)
    