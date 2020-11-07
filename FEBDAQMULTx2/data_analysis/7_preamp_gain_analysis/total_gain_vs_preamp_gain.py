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
    
    # result containers
    # mppc_group = common_tools.MPPCLines(infpns, args.board, args.channel, prom=200)
    # print(mppc_group.mppc_lines[0].bias_voltage, mppc_group.mppc_lines[0].temperature)
    # mppc_group.mppc_lines[0].show_spectrum_and_fit()

    x = np.linspace(0,200,200,False)
    f = np.vectorize(common_tools.multipoisson_fit_function)
    y = f(x,1000,10,10,0.2,3,0.05,0.5)
    plt.plot(x,y,c='r')
    plt.show()
