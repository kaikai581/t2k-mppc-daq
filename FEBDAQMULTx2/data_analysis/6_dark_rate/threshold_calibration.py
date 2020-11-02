#!/usr/bin/env python

# Quick and dirty script. Should revisit later.
# First, with FEB0 preamp gain 55 bias voltage 60V,
# here are the peak ADCs from Wojciech's algorithm
# implemented in 4_mppc_gain_analysis folder.
mapped_peak_adcs = [156.48, 265.0, 350.0, 430.0, 515.0, 600.0]

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../4_mppc_gain_analysis/wojciech_intersection'))
from best_isep import MPPCLine
import argparse
import matplotlib.pyplot as plt

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_files', type=str, default=['../data/root/20201030_thr_scan_with_led_volt60_temp22.8/20201030_124749_dark_rate_feb0_ch24_thr250.0.root'], nargs='*')
    parser.add_argument('-b', '--board_id', type=int, default=0)
    parser.add_argument('-c', '--channel', type=int, default=24)
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()
    infpns = args.input_files
    board_id = args.board_id
    channel = args.channel
    verbose = args.verbose

    # load line from file
    mppc_lines = []
    for infpn in infpns:
        mppc_line = MPPCLine(infpn, board_id, channel, verbose)
        if len(mppc_line.peaks) > 1:
            mppc_lines.append(mppc_line)

    # mppc_line.show_spectrum()
    for mppc_line in mppc_lines:
        mppc_line.shift_and_match(mapped_peak_adcs)
        # print(mppc_line.get_threshold_from_metadata())
        mppc_line.show_spectrum(os.path.join(os.path.dirname(__file__), 'plots/dac{}.png'.format(mppc_line.get_threshold_from_metadata())))
    
    x = [mppc_line.get_threshold_from_metadata() for mppc_line in mppc_lines]
    y = [float(mppc_line.points[0].x) for mppc_line in mppc_lines]
    plt.scatter(x, y)
    plt.ylim(bottom=0)
    plt.xlabel('DAC value')
    plt.ylabel('first peak number')
    plt.savefig('plots/peak_number_vs_dac.png')