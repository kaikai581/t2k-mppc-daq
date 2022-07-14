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
    parser.add_argument('-d','--data_id',type=str)
    parser.add_argument('-c', '--channel', type=int, default=24)
    parser.add_argument('--fit_spectrum_shape', action='store_true')
    parser.add_argument('-ph', '--pcb_half', type=int, default=None)
    parser.add_argument('-p', '--prominence', type=int, default=200)
    parser.add_argument('--voltage_offset', type=float, default=0)
    parser.add_argument('--output_path', type=str, default=os.path.join(os.path.dirname(__file__), 'plots'))
    parser.add_argument('--remove_first_peak', action='store_true')
    args = parser.parse_args()
    infpns = args.input_files
    prominence = args.prominence
    voltage_offset = args.voltage_offset
    data_id = args.data_id

    # result containers for vanila Vset as Vbias
    if voltage_offset == 0:
        mppc_group = common_tools.MPPCLines(infpns, args.board, args.channel, prom=prominence, voltage_offset=0, verbose=False,pcb_half=args.pcb_half, exclude_first_peak=args.remove_first_peak)
        mppc_group.fit_total_gain_vs_bias_voltage(outpn=args.output_path, use_fit_fun=args.fit_spectrum_shape, vset=False, remove_outliers=True)
        if not args.fit_spectrum_shape:
            out_db_fn = 'processed_data/breakdown_database_{}.csv'.format(data_id)
            out_gain_db_fn = 'processed_data/gain_database_{}.csv'.format(data_id)
        else:
            out_db_fn = 'processed_data/breakdown_database_fit_spec_shape_{}.csv'.format(data_id)
            out_gain_db_fn = 'processed_data/gain_database_fit_spec_shape_{}.csv'.format(data_id)
        mppc_group.save_gains(out_gain_db_fn)
        mppc_group.save_breakdowns(out_db_fn)
    # plot Vbias as Vset-voltage_offset
    else:
        mppc_group = common_tools.MPPCLines(infpns, args.board, args.channel, prom=prominence, voltage_offset=0, pcb_half=args.pcb_half)
        mppc_group.fit_total_gain_vs_bias_voltage(outpn=args.output_path, use_fit_fun=args.fit_spectrum_shape, vset=True)
        mppc_group = common_tools.MPPCLines(infpns, args.board, args.channel, prom=prominence, voltage_offset=voltage_offset)
        mppc_group.fit_total_gain_vs_bias_voltage(outpn=args.output_path, use_fit_fun=args.fit_spectrum_shape, vset=False)
