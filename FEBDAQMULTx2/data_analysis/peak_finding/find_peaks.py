#!/usr/bin/env python

from scipy.signal import find_peaks
from matplotlib import markers
import argparse
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import sys


def find_peak(infpn, feb_id, ch):
    # retrieve the dataframe
    try:
        df = pd.read_hdf(infpn, key='mppc')
    except:
        print('Error reading file {}'.format(infpn))
        sys.exit(-2)

    # make the plot of a channel
    chvar = 'chg[{}]'.format(ch)
    # select data of the specified board
    df_1b = df[df['feb_num'] == feb_id]
    bins = np.linspace(0, 4100, 821)

    _, axs = plt.subplots(2)
    histy, bin_edges, _ = axs[0].hist(df_1b[chvar], bins=bins, histtype='step')
    peaks, _ = find_peaks(histy, prominence=300)
    axs[0].scatter(np.array(bin_edges)[peaks], np.array(histy)[peaks],
                   marker=markers.CARETDOWN, color='r', s=20)

    # prepare for output
    infn = os.path.basename(infpn)
    outfdname = os.path.join(os.path.dirname(__file__), infn)
    outfdname = os.path.join(os.path.splitext(outfdname)[0], 'single_channel')
    if not os.path.exists(outfdname):
        os.makedirs(outfdname)

    # save to file
    outfig_pn = os.path.join(outfdname, 'bd{}ch{}.png'.format(feb_id, ch))
    print('Saving output to {}'.format(outfig_pn))
    axs[0].title('board {} channel {}'.format(feb_id, ch))
    plt.show()
    # plt.savefig(outfig_pn)


def main():
    # command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_filename', type=str,
                        default='processed_data/mppc_20200817_2febs.h5')
    parser.add_argument('-b', '--board_id', type=int, default=0)
    parser.add_argument('-c', '--channel', type=int, default=0)
    args = parser.parse_args()
    infpn = args.input_filename
    board_id = args.board_id
    channel = args.channel
    # argument safeguard
    if board_id > 1 or board_id < 0:
        print('Board ID should be 0 or 1.')
        sys.exit(-1)
    if channel > 31 or channel < 0:
        print('Channel number should be between 0 and 31.')
        sys.exit(-1)

    # process a single channel
    find_peak(infpn, board_id, channel)


if __name__ == '__main__':
    main()
