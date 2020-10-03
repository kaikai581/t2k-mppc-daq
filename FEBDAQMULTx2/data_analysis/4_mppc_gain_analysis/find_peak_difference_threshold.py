#!/usr/bin/env python

from matplotlib import markers
from peak_cleanup import PeakCleanup
from scipy.signal import find_peaks
import argparse
import matplotlib.pyplot as plt
import numpy as np
import os
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

    # accumulate all channels of data
    # by looking at the resulting histogram, choose passing interval (0.95, 1.05)
    xmax_cut = 1.2
    xmin_cut = 0.8
    relative_intervals = []
    revisit_channels = dict()
    for bid in range(2):
        for cid in range(32):
            ch_id = (bid, cid)
            cur_ri = peak_diff_ratio_one_ch(df, bid, cid)
            relative_intervals = relative_intervals + cur_ri
            for ri in cur_ri:
                if ri > xmax_cut or ri < xmin_cut:
                    if not ch_id in revisit_channels.keys():
                        revisit_channels[ch_id] = []
                    revisit_channels[ch_id].append(ri)
    plt.hist(relative_intervals, bins=75)
    plt.xlabel('adjacent peak ADC difference/median adjacent peak ADC differences')
    plt.axvline(x=xmax_cut, c='g', alpha=.75, linestyle='--')
    plt.axvline(x=xmin_cut, c='g', alpha=.75, linestyle='--')
    print(revisit_channels)
    # print(peak_diff_ratio_one_ch(df, 1, 1))

    # prepare output file pathname
    out_dir = os.path.join('plots', os.path.basename(infpn).rstrip('.h5'), 'relative_intervals')
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    outfpn = os.path.join(out_dir, 'all_channels_combined.png')
    # save fig to file
    plt.savefig(outfpn)
