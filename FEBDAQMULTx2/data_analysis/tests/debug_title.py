#!/usr/bin/env python
'''
With some particular input files, all plots generated have -1 at temperature, preamp gain, and bias regulation in the title.
This unit test script is to debug this issue.

Shih-Kai Lin in Feb, 2021.
'''
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../utilities'))
import common_tools
import argparse

import matplotlib
matplotlib.use('Agg')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_file', type=str, default='../data/root/led/20210209_145843_lanl_bd1_ch0-31_thr220_temp20_feb170/20210209_174022_mppc_volt58.0_thr220_gain52_temp19.9.root')
    # With the above default filename, only board 1 exists.
    parser.add_argument('-b', '--board', type=int, default=1)
    parser.add_argument('-c', '--channel', type=int, default=24)
    parser.add_argument('-ph', '--pcb_half', type=int, default=0)
    args = parser.parse_args()

    mline = common_tools.MPPCLine(args.input_file, args.board, args.channel, verbose=True, pcb_half=args.pcb_half)
    print(mline.get_parameter_string())
    print('Number of FEBs involved in this dataset:', mline.get_nboards())