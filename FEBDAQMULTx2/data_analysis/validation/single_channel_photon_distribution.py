#!/usr/bin/env python

import argparse
import matplotlib.pyplot as plt
import numpy as np
import os, sys
import uproot

def plot_32_channels(df, feb_id):
    # argument safeguard
    if not feb_id in df.feb_num.unique():
        print('Board ID does not exist.')
        sys.exit(-1)
    
    # select data of the specified board
    df_1b = df[df['feb_num'] == feb_id]
    bins = np.linspace(0, 4100, 821)

    # get number of channels in data
    chs = [int(col[4:-1]) for col in df.columns if 'chg' in col]

    # prepare the canvases
    _, axs = plt.subplots(8, 4, figsize=(16,16))

    # loop and plot all channels
    for ch in chs:
        cur_ax = axs[ch//4, ch%4]
        cur_ax.tick_params(axis='x', labelsize=7)
        cur_ax.tick_params(axis='y', labelsize=7)
        chvar = 'chg[{}]'.format(ch)
        df_1b[chvar].plot.hist(bins=bins, histtype='step', ax=cur_ax)
        cur_ax.set_xlabel('ADC')
        cur_ax.set_ylabel('')
        cur_ax.set_yscale('log')
        cur_ax.text(0.7, 0.6,'FEB {} ch {}'.format(feb_id, ch), ha='center', va='center', transform=cur_ax.transAxes, color='r')
    
    plt.tight_layout()

    # save to file
    outfdname = os.path.join(os.path.splitext(infpn)[0], 'all_channels')
    if not os.path.exists(outfdname):
        os.makedirs(outfdname)
    plt.savefig(os.path.join(outfdname, 'board{}.png'.format(feb_id)))

def single_channel_plot(df, feb_id, ch):
    # argument safeguard
    if not feb_id in df.feb_num.unique():
        print('Board ID does not exist.')
        sys.exit(-1)
    chvar = 'chg[{}]'.format(ch)
    if not chvar in df.columns:
        print('Channel {} has no data!'.format(ch))
        sys.exit(-1)
    
    # select data of the specified board
    df_1b = df[df['feb_num'] == feb_id]
    bins = np.linspace(0, 4100, 821)
    df_1b[chvar].plot.hist(bins=bins, histtype='step')
    
    # prepare for output
    outfdname = os.path.join(os.path.splitext(infpn)[0], 'single_channel')
    if not os.path.exists(outfdname):
        os.makedirs(outfdname)
    
    # save to file
    plt.title('board {} channel {}'.format(feb_id, ch))
    plt.savefig(os.path.join(outfdname, 'bd{}ch{}.png'.format(feb_id, ch)))

def main():
    # command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_filename', type=str,
           default='mppc_20200728.root')
    parser.add_argument('-b', '--board_id', type=int, default=0)
    parser.add_argument('-c', '--channel', type=int, default=0)
    args = parser.parse_args()
    global infpn
    infpn = args.input_filename
    board_id = args.board_id
    channel = args.channel

    # read data with uproot
    tr = uproot.open(infpn)['mppc']
    df = tr.pandas.df()
    # add a row for FEB board ID according to the mac5 value
    mac5s = list(df.mac5.unique())
    df['feb_num'] = df['mac5'].apply(lambda x: mac5s.index(x))
    
    if channel >= 0:
        single_channel_plot(df, board_id, channel)
    else:
        plot_32_channels(df, board_id)

if __name__ == '__main__':
    main()
