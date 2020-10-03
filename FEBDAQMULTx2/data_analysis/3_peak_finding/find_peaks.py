#!/usr/bin/env python

from scipy.signal import find_peaks
from matplotlib import markers
from operator import itemgetter
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
    # make histogram and find peaks
    bins = np.linspace(0, 4100, 821)
    _, axs = plt.subplots(2)
    histy, bin_edges, _ = axs[0].hist(df_1b[chvar], bins=bins, histtype='step')
    peaks, _ = find_peaks(histy, prominence=300)
    axs[0].scatter(np.array(bin_edges)[peaks], np.array(histy)[peaks],
                   marker=markers.CARETDOWN, color='r', s=20)
    axs[0].set_xlabel('ADC value')

    # make the linear plot
    # try 2 ADC to n_photo map
    ped_idx = min(enumerate(np.array(bin_edges)[peaks]), key=itemgetter(1))[0]
    peaks_no_ped = [peaks[i] for i in range(len(peaks)) if i != ped_idx]
    x_trys = []
    y_trys = []
    coeff = []
    for i in range(2):
        x_try = np.linspace(1+i, len(peaks_no_ped)+i, len(peaks_no_ped))
        y_try = sorted(np.array(bin_edges)[peaks_no_ped])
        x_trys.append(x_try)
        y_trys.append(y_try)
        coeff.append(np.polyfit(x_try, y_try, 1))
    # choose the one with smaller absolute intersection
    intersecs = [np.abs(c[1]) for c in coeff]
    correct_idx = min(enumerate(intersecs), key=itemgetter(1))[0]
    x_try = x_trys[correct_idx]
    y_try = y_trys[correct_idx]
    fitx = np.linspace(0, x_try[-1], 100)
    fity = coeff[correct_idx][0]*fitx + coeff[correct_idx][1]
    axs[1].plot(fitx, fity, '--g', alpha=.7)
    axs[1].scatter(x_try, y_try, marker='o', color='r', s=20)
    axs[1].set_xlim(left=0)
    axs[1].set_ylim(bottom=0)
    axs[1].set_xlabel('number of photons')
    axs[1].set_ylabel('ADC value')

    # prepare for output
    infn = os.path.basename(infpn)
    outfdname = os.path.join(os.path.dirname(__file__), infn)
    outfdname = os.path.join(os.path.splitext(outfdname)[0], 'single_channel')
    if not os.path.exists(outfdname):
        os.makedirs(outfdname)

    # save to file
    outfig_pn = os.path.join(outfdname, 'bd{}ch{}.png'.format(feb_id, ch))
    print('Saving output to {}'.format(outfig_pn))
    axs[0].set_title('board {} channel {}'.format(feb_id, ch))
    plt.tight_layout()
    plt.savefig(outfig_pn)


def plot_32_channels(infpn, feb_id):
    # retrieve the dataframe
    try:
        df = pd.read_hdf(infpn, key='mppc')
    except:
        print('Error reading file {}'.format(infpn))
        sys.exit(-2)
    
    # select data of the specified board
    df_1b = df[df['feb_num'] == feb_id]
    bins = np.linspace(0, 4100, 821)

    # get number of channels in data
    chs = [int(col[4:-1]) for col in df.columns if 'chg' in col]

    # prepare the canvases
    _, axs = plt.subplots(8, 4, figsize=(24,16))

    # loop and plot all channels
    for ch in chs:
        cur_ax = axs[ch//4, ch%4]
        cur_ax.tick_params(axis='x', labelsize=7)
        cur_ax.tick_params(axis='y', labelsize=7)
        chvar = 'chg[{}]'.format(ch)
        df_1b[chvar].plot.hist(bins=bins, histtype='step', ax=cur_ax)
        cur_ax.set_xlabel('ADC')
        cur_ax.set_ylabel('')
        # cur_ax.set_yscale('log')
        cur_ax.text(0.7, 0.6,'FEB {} ch {}'.format(feb_id, ch), ha='center',
                    va='center', transform=cur_ax.transAxes, color='r')
    
    plt.tight_layout()

    # save to file
    infn = os.path.basename(infpn)
    outfdname = os.path.join(os.path.dirname(__file__), infn)
    outfdname = os.path.join(os.path.splitext(outfdname)[0], 'all_channels')
    if not os.path.exists(outfdname):
        os.makedirs(outfdname)
    outfig_pn = os.path.join(outfdname, 'board{}.png'.format(feb_id))
    print('Saving output to {}'.format(outfig_pn))
    plt.savefig(outfig_pn)

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
    if channel > 31:
        print('Channel number should be between 0 and 31. Use a negative number to plot all channels')
        sys.exit(-1)

    # process a single channel
    if channel >= 0:
        find_peak(infpn, board_id, channel)
    else:
        plot_32_channels(infpn, board_id)


if __name__ == '__main__':
    main()
