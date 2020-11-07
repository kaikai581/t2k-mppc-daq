#!/usr/bin/env python

import argparse
import matplotlib.pyplot as plt
import os
import uproot

def common_prefix(strings):
    '''
    Find the longest string that is a prefix of all the strings.
    '''
    if not strings:
        return ''
    prefix = strings[0]
    for s in strings:
        if len(s) < len(prefix):
            prefix = prefix[:len(s)]
        if not prefix:
            return ''
        for i in range(len(prefix)):
            if prefix[i] != s[i]:
                prefix = prefix[:i]
                break
    return prefix

def make_plot_from_raw(flist):
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
    plt.plot(x_dac, y_rate, marker='o', markersize=5)
    plt.ylabel('rate (Hz)')
    plt.xlabel('DAC')
    plt.yscale('log')
    plt.title('FEB{} ch{}'.format(board, channel))
    plt.grid(axis='both')

    # prepare output folder
    out_dir = 'plots'
    out_dir = os.path.join(os.path.dirname(__file__), out_dir)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    ofpn = os.path.join(out_dir, common_prefix([os.path.basename(fname) for fname in flist])+'.png')
    # plt.show()
    plt.savefig(ofpn)

def make_plot_from_summary(infpn):
    # load the tree
    tr = uproot.open(infpn)['tr_rate']
    df = tr.pandas.df()
    
    # plot dark rate vs. threshold
    ax = df.plot(x='DAC', y='meanRate_sw', marker='o', fillstyle='none', label='software')
    df.plot(x='DAC', y='meanRate', marker='*', ax=ax, label='hardware')
    plt.yscale('log')
    plt.grid(axis='y')
    plt.ylabel('rate (Hz)')
    plt.title('b{} ch{}'.format(df['board'].iloc[0], df['channel'].iloc[0]))

    # prepare the output pathname
    out_dir = 'plots'
    out_dir = os.path.join(os.path.dirname(__file__), out_dir)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    ofpn = os.path.join(out_dir, os.path.basename(infpn).rstrip('.root')+'.png')
    plt.savefig(ofpn)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_files', nargs='*', default=['../data/root/20201028_184652_dark_rate_summary.root'], type=str)
    args = parser.parse_args()
    infpns = args.input_files
    
    # loop through all input files
    raw_filelist = []
    for infpn in infpns:
        if 'summary' in infpn:
            make_plot_from_summary(infpn)
        else:
            raw_filelist.append(infpn)
    
    # if raw file list is not empty, process it
    if raw_filelist:
        make_plot_from_raw(raw_filelist)
