#!/usr/bin/env python

import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--fit_spectrum_shape', action='store_true')
    parser.add_argument('-d','--data_id', type=str, default="")
    parser.add_argument('-i', '--input_files', type=str, nargs='*')
    parser.add_argument('-p', '--prominence', type=int, default=200)
    parser.add_argument('--remove_first_peak', action='store_true')
    args = parser.parse_args()
    infpns = args.input_files
    data_id = args.data_id
    prominence = args.prominence

    print("Data Directory: {}".format(infpns))
    print("Board Id: {}".format(data_id))

    for board in [0, 1]:
        for ch in range(32):
            outpn = os.path.dirname(infpns[0]).split('/')[-1]
            outpn = os.path.join('plots', outpn, 'b{}c{}'.format(board, ch))
            if not data_id:
                data_id = os.path.dirname(infpns[0]).split('/')[-2]

            cmd = './v2_plot_totalgain_vs_bias_for_breakdown.py -i {} -b {} -c {} -p {} --output_path {}'.format(' '.join(infpns), board, ch, prominence, outpn)
            if args.fit_spectrum_shape:
                cmd += ' --fit_spectrum_shape'
            if args.remove_first_peak:
                cmd += ' --remove_first_peak'
            os.system(cmd)
