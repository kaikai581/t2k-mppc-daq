#!/usr/bin/env python

import argparse
import os
import matplotlib
matplotlib.use('Agg')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--board', type=int, default=0)
    parser.add_argument('-i', '--input_files', type=str, nargs='*')
    parser.add_argument('-p', '--prominence', type=int, default=200)
    parser.add_argument('-ph', '--pcb_half', type=int, default=None)
    args = parser.parse_args()
    board = args.board
    infpns = args.input_files
    prominence = args.prominence

    for ch in range(32):
        outpn = os.path.dirname(infpns[0]).split('/')[-1]
        # get the gain value string
        gain = 'gain0'
        for tmpstr in os.path.basename(infpns[0]).split('_'):
            if 'gain' in tmpstr:
                gain = tmpstr
                break
        outpn = os.path.join('plots', outpn, gain, 'b{}c{}'.format(board, ch))
        cmd = './v2_plot_totalgain_vs_bias_for_breakdown.py -i {} -b {} -c {} -p {} --output_path {} --pcb_half {}'.format(' '.join(infpns), board, ch, prominence, outpn, args.pcb_half)
        os.system(cmd)
