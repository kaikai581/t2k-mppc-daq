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
    args = parser.parse_args()
    infpns = args.input_files
    
    # result containers
    mppc_lines = [common_tools.MPPCLine(infpn, args.board, args.channel, prom=50, verbose=True) for infpn in infpns]
    mppc_lines[0].show_spectrum_and_fit()
    # mppc_lines[0].show_gain_vs_pe()
    # print(mppc_lines[0].preamp_gain)
