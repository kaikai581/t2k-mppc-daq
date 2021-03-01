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
    parser.add_argument('-i', '--input_files', type=str, nargs='*', default='../data/root/dark/20210203_volt58_ch32-63_feb170/20210203_171439_dark_rate_feb0_ch1_thr*.root')
    parser.add_argument('-l', '--led_file', type=str, default='../data/root/led/20210203_102342_lanl_bd1_ch32-63_thr220_temp20_feb170/20210203_130526_mppc_volt58.0_thr220_gain52_temp19.9.root')
    args = parser.parse_args()

    # my_scan = software_threshold_scan.adc_scan(args.input_files, args.led_file, pcb_half=1)
    infpns = '../data/root/dark/20210204_volt58_ch0-31_feb170/20210204_160254_dark_rate_feb0_ch0_thr*.root'
    led_fpn = '../data/root/led/20210225_171514_lanl_bd1_ch0-31_thr244_gain52_temp20_trig0_feb170/20210225_172920_mppc_volt58.0_thr244_gain52_temp20.0.root'
    my_scan = software_threshold_scan.adc_scan(infpns, led_fpn, pcb_half=0)

    
    # make sure output directory exists
    outdir = 'plots'
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    
    my_scan.plot_rate_and_diff_rate_vs_dac()
    # for this particular combination, the first peak is like 3
    my_scan.dac_to_adc_and_pe(force_first_peak_number=3)