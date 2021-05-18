#!/usr/bin/env python
'''
This script fit the breakdown voltage with the autocorrelation method.
'''

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../utilities'))

import argparse
import autocorrelation_gain
import matplotlib
matplotlib.use('Agg')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_files', type=str, nargs='*')
    parser.add_argument('-c', '--channel', type=int, default=None, help='Channel run through. Default to run through all.')
    parser.add_argument('-d', '--db_filepathname', type=str, default='processed_data/breakdown_autocorrelation.csv', help='Breakdown voltage output file pathname.')
    parser.add_argument('-n', '--nbins', type=int, default=4100)
    parser.add_argument('-ph', '--pcb_half', type=int, default=0)
    parser.add_argument('-p', '--prominence_fraction', type=int, default=0.001, help='Peak prominence fraction of the magnitude of the largest peak in the autocorrelation plot.')
    parser.add_argument('--output_path', type=str, default=os.path.join(os.path.dirname(__file__), 'plots'))
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()
    infpns = args.input_files
    prom_frac = args.prominence_fraction
    ch = args.channel
    db_filepathname = args.db_filepathname

    # use the MPPCLines class to fit the breakdown voltage
    my_breakdowns = autocorrelation_gain.MPPCLines(infpns, verbose=args.verbose)
    if not ch is None:
        my_breakdowns.fit_total_gain_vs_bias_voltage(ch, nbins=args.nbins, prom_frac=prom_frac, outpn=args.output_path)
        my_breakdowns.save_breakdowns(db_filepathname, ch)
    else:
        for ch in range(64):
            my_breakdowns.fit_total_gain_vs_bias_voltage(ch, nbins=args.nbins, prom_frac=prom_frac, outpn=args.output_path)
            my_breakdowns.save_breakdowns(db_filepathname, ch)