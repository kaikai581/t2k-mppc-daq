#!/usr/bin/env python

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../utilities'))

import argparse
import common_tools
import matplotlib
matplotlib.use('Agg')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_files', type=str, nargs='*')
    parser.add_argument('-b', '--board', type=int, default=0)
    parser.add_argument('-c', '--channel', type=int, default=24)
    parser.add_argument('-ph', '--pcb_half', type=int, default=None)
    parser.add_argument('-p', '--prominence', type=int, default=200)
    parser.add_argument('--output_path', type=str, default=os.path.join(os.path.dirname(__file__), 'plots'))
    args = parser.parse_args()
    infpns = args.input_files
    prominence = args.prominence

    mppc_group = common_tools.MPPCLines(infpns, args.board, args.channel, prom=prominence, voltage_offset=0, pcb_half=args.pcb_half)
    mppc_group.fit_total_gain_vs_preamp_gain(outpn=args.output_path, use_fit_fun=False)
    mppc_group.save_gains('processed_data/gain_database.csv')
