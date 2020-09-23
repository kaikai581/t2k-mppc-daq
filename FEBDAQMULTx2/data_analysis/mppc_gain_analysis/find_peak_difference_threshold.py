#!/usr/bin/env python

from matplotlib import markers
from peak_cleanup import PeakCleanup
from scipy.signal import find_peaks
import argparse
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def peak_diff_ratio_one_ch(df, bid, cid):
    '''
    Given a channel, calculate the peak differences
    over the median value.
    '''
    # make the plot of a channel
    chvar = 'chg[{}]'.format(cid)
    # select data of the specified board
    df_1b = df[df['feb_num'] == bid]
    # make histogram and find peaks
    bins = np.linspace(0, 4100, 821)
    plt.figure(figsize=(12,6))
    ax1 = plt.subplot2grid((2, 3), (0, 0), colspan=2)
    histy, bin_edges, _ = ax1.hist(df_1b[chvar], bins=bins, histtype='step')
    peaks, _ = find_peaks(histy, prominence=300)
    ax1.scatter(np.array(bin_edges)[peaks], np.array(histy)[peaks],
                   marker=markers.CARETDOWN, color='r', s=20)
    ax1.set_xlabel('ADC value')
    # store the found peaks into a list
    peak_adcs = list(np.array(bin_edges)[peaks])
    if print_peak_adcs: print(peak_adcs)

    # release memory
    plt.close()

    # use my utility class to calculate
    pc = PeakCleanup(peak_adcs)

    return pc.relative_interval()
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_file', type=str, default='../data/pandas/20200911_180348_mppc_volt58.0_temp20.0.h5')
    parser.add_argument('--print_peak_adcs', action='store_true')
    args = parser.parse_args()
    infpn = args.input_file
    print_peak_adcs = args.print_peak_adcs

    # retrieve data
    df = pd.read_hdf(infpn, key='mppc')

    # process all channels of data
    # for bid in range(2):
    #     for cid in range(32):
    #         peak_diff_ratio_one_ch(df, bid, cid)
    print(peak_diff_ratio_one_ch(df, 1, 1))
