#!/usr/bin/env python

import argparse
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def main(args):
    in_files = args.input_files
    dfs = [pd.read_hdf(infpn, key='mppc') for infpn in in_files]
    legs = args.legends

    # make the plot of a channel
    chvar = 'chg[{}]'.format(args.channel)

    _, axs = plt.subplots(1)
    for i in range(3):
        df = dfs[i]
        df_1b = df[df['feb_num'] == args.board_id]
        bins = np.linspace(0, 4100, 821)
        histy, bin_edges, _ = axs.hist(df_1b[chvar], bins=bins, histtype='step', label=legs[i], density=True)
    axs.set_title('board {} channel {}'.format(args.board_id, args.channel))
    axs.legend()
    plt.savefig('b{}_ch{}.jpg'.format(args.board_id, args.channel))



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input_files', nargs='*', help='Provide a list of input files', default=['../data/pandas/mppc_20200901_gain45.h5', '../data/pandas/mppc_20200901_gain50.h5', '../data/pandas/mppc_20200901_gain55.h5'])
    parser.add_argument('-l','--legends', nargs='*', help='Provide a list of legend labels', default=['gain 45', 'gain 50', 'gain 55'])
    parser.add_argument('-b', '--board_id', type=int, default=0)
    parser.add_argument('-c', '--channel', type=int, default=5)
    args = parser.parse_args()
    # print(args)
    main(args)