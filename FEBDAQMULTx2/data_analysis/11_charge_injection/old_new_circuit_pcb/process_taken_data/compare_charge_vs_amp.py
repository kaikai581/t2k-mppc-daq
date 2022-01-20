#!/usr/bin/env python
'''
This script comapres conversion factors obtained by amplitude and charge methods.
'''

import argparse

# redirect output figures
import matplotlib
matplotlib.use('Agg')

import os
import pandas as pd
import seaborn as sns

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_filename', default='processed_data/20211116_charge_injection_feb12808_gain56.csv')
    parser.add_argument('-o', '--output_file_pathname', type=str, default='plots/charge_amp_comparison.png')
    args = parser.parse_args()

    df = pd.read_csv(args.input_filename, index_col=None)
    amp = df.scope_amplitude.unique()[0]
    df_sel = df[(df.scope_amplitude == amp) & (df.method == 'mpv')]
    
    g = sns.scatterplot(data=df_sel, x='trigger_channel', y='conversion_factor')
    g = sns.scatterplot(data=df_sel, x='trigger_channel', y='conversion_factor_from_charge')
    g.figure.savefig(args.output_file_pathname)
