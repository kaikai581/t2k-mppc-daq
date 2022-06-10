#!/usr/bin/env python

import argparse
import matplotlib.pyplot as plt
import numpy as np
import os, sys
import uproot
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../utilities'))
import common_tools

def board_trigger_rate(df, feb_id):

    # select data of the specified board
    df_1b = df[df['feb_num'] == feb_id]

    # get maximum and minimum time stamps
    ntrigs = len(df_1b)
    ts0_min = df_1b['ts0'].min()
    ts0_max = df_1b['ts0'].max()
    rate0 = ntrigs/(ts0_max-ts0_min)
    ts1_min = df_1b['ts1'].min()
    ts1_max = df_1b['ts1'].max()
    rate1 = ntrigs/(ts1_max-ts1_min)
    print('board {}: rate0 {:.2e} rate1 {:.2e}'.format(feb_id, rate0, rate1))
    print('max time0: {}\nmin time0: {}'.format(ts0_max, ts0_min))
    print('max time1: {}\nmin time1: {}'.format(ts1_max, ts1_min))

def plot_32_channels(df, feb_id, plot_linear):

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
        if not plot_linear:
            cur_ax.set_yscale('log')
        cur_ax.text(0.7, 0.6,'FEB {} ch {}'.format(feb_id, ch), ha='center',
                    va='center', transform=cur_ax.transAxes, color='r')
    
    plt.tight_layout()

    # save to file
    outfdname = os.path.join(os.path.dirname(__file__), infn)
    outfdname = os.path.join(os.path.splitext(outfdname)[0], 'all_channels')
    if not os.path.exists(outfdname):
        os.makedirs(outfdname)
    outfig_pn = os.path.join(outfdname, 'board{}{}.png'.format(feb_id, '_linear' if plot_linear else ''))
    print('Saving output to {}'.format(outfig_pn))
    plt.savefig(outfig_pn)

def single_channel_plot(df, feb_id, ch):
    # argument safeguard
    chvar = 'chg[{}]'.format(ch)
    if not chvar in df.columns:
        print('Channel {} has no data!'.format(ch))
        sys.exit(-1)
    
    # select data of the specified board
    df_1b = df[df['feb_num'] == feb_id]
    bins = np.linspace(0, 4100, 821)
    df_1b[chvar].plot.hist(bins=bins, histtype='step')
    
    # prepare for output
    outfdname = os.path.join(os.path.dirname(__file__), infn)
    outfdname = os.path.join(os.path.splitext(outfdname)[0], 'single_channel')
    if not os.path.exists(outfdname):
        os.makedirs(outfdname)
    
    # save to file
    outfig_pn = os.path.join(outfdname, 'bd{}ch{}.png'.format(feb_id, ch))
    print('Saving output to {}'.format(outfig_pn))
    plt.title('board {} channel {}'.format(feb_id, ch))
    plt.ylabel('Count')
    plt.xlabel('ADC')
    plt.savefig(outfig_pn)

def main():
    # command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_filename', type=str,
           default='mppc_20200728.root')
    parser.add_argument('-b', '--board_id', type=int, default=0)
    parser.add_argument('-c', '--channel', type=int, default=0)
    parser.add_argument('-l', '--linear', action='store_true', help='Make all plots in linear scale.')
    args = parser.parse_args()
    global infpn
    infpn = args.input_filename
    board_id = args.board_id
    channel = args.channel
    linear_plots = args.linear

    # read data with uproot
    global infn
    infn = os.path.basename(infpn)
    infpn = os.path.join(os.path.dirname(__file__), '../data/root', infn)
    tr = uproot.open(infpn)['mppc']
    if common_tools.get_uproot_version() == 3:
        df = tr.pandas.df()
    elif common_tools.get_uproot_version() == 4:
        df = tr.arrays(library='pd')
    else:
        print('Only uproot3 and uproot4 are implemented!')
        sys.exit(-1)
    # add a row for FEB board ID according to the mac5 value
    mac5s = list(df.mac5.unique())
    df['feb_num'] = df['mac5'].apply(lambda x: mac5s.index(x))
    # argument safeguard
    if not board_id in df.feb_num.unique():
        print('Board ID {} does not exist.'.format(board_id))
        sys.exit(-1)
    
    if channel >= 0:
        single_channel_plot(df, board_id, channel)
    else:
        plot_32_channels(df, board_id, linear_plots)
        board_trigger_rate(df, board_id)

if __name__ == '__main__':
    main()
