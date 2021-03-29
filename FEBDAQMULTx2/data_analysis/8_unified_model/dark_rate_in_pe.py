#!/usr/bin/env python
'''
This script plots the dark count rate as a function of DAC and then calibrate DAC into photoelectrons.

Input:
1. A set of led files taken with different bias voltages. Note that all files can only be triggered by one channel. If OR-32 trigger is used, all channels will have no peaks removed by the threshold.
2. A set of dark noise files. One file for one DAC value.
'''

# my own modules
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../utilities'))
import peak_numbering
import software_threshold_scan

from glob import glob
import argparse
# avoid x11 error
import matplotlib
matplotlib.use('Agg')

def assemble_calib_filenames():
    with open(args.calib_file_paths) as f:
        content = [line for line in f.readlines() if line.strip()]
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    content = [glob(os.path.join(p, '*ch{}*.root'.format(args.channel)))[0] for p in content]
    return content

def assemble_dark_rate_filenames():
    return glob(os.path.join(args.dark_rate_file_path, '*ch{}*.root'.format(args.channel)))

def get_calibration_threshold(fn):
    fn = os.path.basename(fn).rstrip('.root')
    for tmp_str in fn.split('_'):
        if 'thr' in tmp_str:
            return tmp_str.lstrip('thr').strip()

if __name__ == '__main__':
    # command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--calib_file_paths', type=str, default='calib_paths/thr205.txt')
    parser.add_argument('-b', '--board', type=int, default=1)
    parser.add_argument('-c', '--channel', type=int, default=0)
    parser.add_argument('-d', '--dark_rate_file_path', type=str, nargs='*', default='../data/root/dark/20210203_volt58_ch32-63_feb170')
    parser.add_argument('-ph', '--pcb_half', type=int, default=None)
    # It is found that using a prominence of 50 leads to instability of the peak numbering algorithm!
    parser.add_argument('-p', '--prominence', type=int, default=100)
    parser.add_argument('--output_path', type=str, default=os.path.join(os.path.dirname(__file__), 'plots', os.path.basename(__file__).rstrip('.py')))
    args = parser.parse_args()
    outpn = args.output_path
    outpn = os.path.join(outpn, 'b{}c{}'.format(args.board, args.channel))

    # construct the calibration file pathnames
    calib_fpns = assemble_calib_filenames()
    calib_thr = get_calibration_threshold(calib_fpns[0])
    dark_rate_fpns = assemble_dark_rate_filenames()

    # get the first peak number
    # instantiate the class
    my_pn = peak_numbering.fitting_algorithm(calib_fpns, args.board, args.channel, verbose=True, outpn=outpn, pcb_half=args.pcb_half, prom=args.prominence)

    # fit model to data
    my_pn.fit_peak_numbering(shift_limit=4)
    my_pn.refit_physics_parameters()

    # make diagnostic plots
    my_pn.plot_adc_vs_peak_number()
    
    # print peak numbering results
    # print(my_pn.df_3d_pts)

    my_scan = software_threshold_scan.peak_number_dataframe(dark_rate_fpns, my_pn.df_3d_pts, calib_thr=calib_thr, pcb_half=1)
    print(my_scan.df_rate_scan)
    my_scan.dac_to_adc_and_pe(outpn=outpn)
