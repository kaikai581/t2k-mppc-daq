#!/usr/bin/env python

import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_files', type=str, nargs='*')
    parser.add_argument('-p', '--prominence', type=int, default=200)
    args = parser.parse_args()
    infpns = args.input_files
    prominence = args.prominence

    for board in [0, 1]:
        for ch in range(32):
            outpn = os.path.dirname(infpns[0]).split('/')[-1]
            outpn = os.path.join('plots', outpn, 'b{}c{}'.format(board, ch))
            cmd = './v2_plot_totalgain_vs_bias_for_breakdown.py -i {} -b {} -c {} -p {} --output_path {}'.format(' '.join(infpns), board, ch, prominence, outpn)
            os.system(cmd)