#!/usr/bin/env python

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../utilities'))

import argparse
import common_tools
import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_files', type=str, nargs='*')
    parser.add_argument('-b', '--board', type=int, default=0)
    parser.add_argument('-c', '--channel', type=int, default=24)
    args = parser.parse_args()
    infpns = args.input_files

    # x0 = [1.92146209e+04, 2.70747057e+01, 2.61399618e+02, 2.49084992e-01, 2.67437806e+00, 2.19167730e+00, 3.88837355e-06]
    # x0 = [9.94192213e+04, 9.30903167e+00, 2.22499208e+02, 4.58364234e-04, 2.25968104e+00, 3.02765250e+00, 4.56089578e+00]
    # x = np.linspace(0,800,800,False)
    # f = np.vectorize(common_tools.multipoisson_fit_function)
    # x0 = [8.17238186e+03, 7.04937982e+01, 1.71778575e+02, 2.67215945e-03, 1.70559594e+00, 3.92486266e-01, 2.52090931e-01]
    # y = f(x,*x0)
    # plt.plot(x,y,c='r')
    # plt.show()

    # result containers
    mppc_group = common_tools.MPPCLines(infpns, args.board, args.channel, prom=200)
    # mppc_group.fit_total_gain_vs_bias_voltage(os.path.join(os.path.dirname(__file__), 'plots'))
    # mppc_group.mppc_lines[0].adc_spectrum(adcmax=2000, savepn=os.path.join(os.path.dirname(__file__), 'plots'))
    mppc_group.fit_total_gain_vs_preamp_gain(os.path.join(os.path.dirname(__file__), 'plots/20201103_preamp_scan_with_led'), False)
