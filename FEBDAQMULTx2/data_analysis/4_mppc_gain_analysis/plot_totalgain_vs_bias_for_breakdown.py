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
    parser.add_argument('--voltage_offset', type=float, default=0)
    parser.add_argument('--output_path', type=str, default=os.path.join(os.path.dirname(__file__), 'plots'))
    args = parser.parse_args()
    infpns = args.input_files
    voltage_offset = args.voltage_offset

    # result containers for vanila Vset as Vbias
    if voltage_offset == 0:
        mppc_group = common_tools.MPPCLines(infpns, args.board, args.channel, prom=200, voltage_offset=0)
        mppc_group.fit_total_gain_vs_bias_voltage(outpn=args.output_path, use_fit_fun=False, vset=False)
    # plot Vbias as Vset-voltage_offset
    else:
        mppc_group = common_tools.MPPCLines(infpns, args.board, args.channel, prom=200, voltage_offset=0)
        mppc_group.fit_total_gain_vs_bias_voltage(outpn=args.output_path, use_fit_fun=False, vset=True)
        mppc_group = common_tools.MPPCLines(infpns, args.board, args.channel, prom=200, voltage_offset=voltage_offset)
        mppc_group.fit_total_gain_vs_bias_voltage(outpn=args.output_path, use_fit_fun=False, vset=False)

