#!/usr/bin/env python

import argparse
import glob
import matplotlib.pyplot as plt
import os
import uproot

def easy_savefig(plt, outfpn=None):
    if outfpn:
        outp = os.path.dirname(outfpn)
        if not os.path.exists(outp):
            os.makedirs(outp)
        plt.savefig(outfpn)
    plt.close()

def make_plot_from_raw(flist, label):
    # load data trees one by one
    x_dac = []
    y_rate = []
    for f in flist:
        tr = uproot.open(f)['mppc']
        df = tr.pandas.df()
        rate = len(df)/(df['ns_epoch'].max()-df['ns_epoch'].min())*1e9
        y_rate.append(rate)
        
        tr_metadata = uproot.open(f)['metadata']
        df_metadata = tr_metadata.pandas.df()

        x_dac.append(df_metadata[df_metadata.isTrigger == True]['DAC'].iloc[0])
    board = df_metadata[df_metadata.isTrigger == True]['board'].iloc[0]
    channel = df_metadata[df_metadata.isTrigger == True]['channel'].iloc[0]

    # plt.plot(x_dac, y_rate, marker='o', markerfacecolor='None', linestyle='None')
    plt.plot(x_dac, y_rate, marker='o', markersize=5, linestyle='None', label=label)
    plt.ylabel('rate (Hz)')
    plt.xlabel('DAC')
    plt.yscale('log')
    plt.title('FEB{} ch{}'.format(board, channel))
    plt.grid(axis='both')

def make_plot_from_summary(infpn, axis=None):
    # load the tree
    tr = uproot.open(infpn)['tr_rate']
    df = tr.pandas.df()
    
    # plot dark rate vs. threshold
    if axis:
        ax = df.plot(x='DAC', y='meanRate_sw', marker='o', fillstyle='none', label='software', ax=axis)
    else:
        ax = df.plot(x='DAC', y='meanRate_sw', marker='o', fillstyle='none', label='software')
    df.plot(x='DAC', y='meanRate', marker='*', ax=ax, label='hardware')
    plt.yscale('log')
    plt.grid(axis='y')
    plt.ylabel('rate (Hz)')
    plt.title('b{} ch{}'.format(df['board'].iloc[0], df['channel'].iloc[0]))

    return ax

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i1', '--input_files1', nargs='*', default=glob.glob('../data/root/20201208_dark_rate_scan_feb0_ch24/*.root'), type=str)
    parser.add_argument('-i2', '--input_files2', nargs='*', default=glob.glob('../data/root/20210108_dark_rate_scan_feb0_ch24/*.root'), type=str)
    args = parser.parse_args()
    infpns1 = args.input_files1
    infpns2 = args.input_files2
    
    # loop through all input files
    raw_filelist1 = []
    raw_filelist2 = []
    for infpn in infpns1:
        if 'summary' in infpn:
            ax = make_plot_from_summary(infpn)
        else:
            raw_filelist1.append(infpn)
    for infpn in infpns2:
        if 'summary' in infpn:
            make_plot_from_summary(infpn, ax)
            easy_savefig(plt, 'plots/compare_dark_rates_from_summary.png')
        else:
            raw_filelist2.append(infpn)
    
    # if raw file list1 or raw file list2 is not empty, process them
    if raw_filelist1 and raw_filelist2:
        make_plot_from_raw(raw_filelist1, label=os.path.basename(raw_filelist1[0]).split('_')[0])
        make_plot_from_raw(raw_filelist2, label=os.path.basename(raw_filelist2[0]).split('_')[0])
        plt.legend()
        easy_savefig(plt, 'plots/compare_dark_rates_from_raw.png')
