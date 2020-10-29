#!/usr/bin/env python

import argparse
import matplotlib.pyplot as plt
import os
import uproot

def make_plot(infpn):
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
    for infpn in infpns:
        make_plot(infpn)
