#!/usr/bin/env python
'''
This script is to test the implementation of the new peak numbering algorithm utilizing the full functional form between ADC, bias voltage, and photoelectron.
'''

# my own modules
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../utilities'))
import peak_numbering

# redirect output engine to avoid x11 errors
import matplotlib
matplotlib.use('Agg')

import argparse

if __name__ == '__main__':
    # command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_files', type=str, nargs='*', default='/cshare/vol2/users/shihkai/data/mppc/root/led/20210225_171514_lanl_bd1_ch0-31_thr244_gain52_temp20_trig0_feb170/*.root')
    parser.add_argument('-b', '--board', type=int, default=1)
    parser.add_argument('-c', '--channel', type=int, default=0)
    parser.add_argument('-ph', '--pcb_half', type=int, default=None)
    parser.add_argument('-p', '--prominence', type=int, default=100)
    parser.add_argument('--output_path', type=str, default=os.path.join(os.path.dirname(__file__), 'plots', os.path.basename(__file__).rstrip('.py')))
    args = parser.parse_args()

    outpn = args.output_path
    outpn = os.path.join(outpn, 'b{}c{}'.format(args.board, args.channel))

    # instantiate the class
    my_pn = peak_numbering.fitting_algorithm(args.input_files, args.board, args.channel, verbose=True, outpn=outpn, pcb_half=args.pcb_half, prom=args.prominence)

    # fit model to data
    my_pn.fit_peak_numbering(shift_limit=4)
    my_pn.refit_physics_parameters()

    # make plots
    my_pn.plot_gamma_spread()
    my_pn.plot_adc_vs_peak_number()
    my_pn.plot_breakdown_voltage_comparison()