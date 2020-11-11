#!/usr/bin/env python

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../utilities'))

import argparse
import common_tools

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_files', type=str, nargs='*')
    parser.add_argument('-b', '--board', type=int, default=0)
    parser.add_argument('-c', '--channel', type=int, default=24)
    parser.add_argument('--output_path', type=str, default=os.path.join(os.path.dirname(__file__), 'plots'))
    args = parser.parse_args()
    infpns = args.input_files

    # result containers
    mppc_group = common_tools.MPPCLines(infpns, args.board, args.channel, prom=200)
    mppc_group.fit_total_gain_vs_bias_voltage(args.output_path, False)
