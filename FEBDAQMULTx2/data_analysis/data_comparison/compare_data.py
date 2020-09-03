#!/usr/bin/env python

import argparse
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def main(args):
    in_files = ['../data/pandas/mppc_20200901_gain45.h5', '../data/pandas/mppc_20200901_gain50.h5', '../data/pandas/mppc_20200901_gain55.h5']
    dfs = [pd.read_hdf(infpn, key='mppc') for infpn in in_files]
    gains = ['45', '50', '55']

    # make the plot of a channel
    chvar = 'chg[{}]'.format(args.channel)

    _, axs = plt.subplots(1)
    for i in range(3):
        df = dfs[i]
        df_1b = df[df['feb_num'] == args.board_id]
        bins = np.linspace(0, 4100, 821)
        histy, bin_edges, _ = axs.hist(df_1b[chvar], bins=bins, histtype='step', label='gain {}'.format(gains[i]))
    axs.set_title('board {} channel {}'.format(args.board_id, args.channel))
    axs.legend()
    plt.savefig('b{}_ch{}.jpg'.format(args.board_id, args.channel))



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument('-i','--input_files', action='append', help='Provide a list of input files')
    # args = parser.parse_args()._get_kwargs()
    # print(args)
    parser.add_argument('-b', '--board_id', type=int, default=0)
    parser.add_argument('-c', '--channel', type=int, default=5)
    args = parser.parse_args()
    main(args)