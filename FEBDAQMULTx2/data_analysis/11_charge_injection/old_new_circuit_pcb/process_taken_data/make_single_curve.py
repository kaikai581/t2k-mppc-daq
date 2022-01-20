#!/usr/bin/env python
'''
This script takes a single csv file as input plot the conversion factors channel by channel.
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
    parser.add_argument('-a', '--scope_amplitude', help='Pulse amplitude observed on the scope in mV', type=float, default=50)
    parser.add_argument('-i', '--input_filename', default='processed_data/20211116_charge_injection_feb12808_gain56.csv')
    parser.add_argument('-o', '--output_file_pathname', type=str, default='plots/output_one_curve.png')
    args = parser.parse_args()

    df = pd.read_csv(args.input_filename, index_col=None)
    df_sel = df[(df.scope_amplitude == args.scope_amplitude) & (df.method == 'gauss')]
    
    g = sns.scatterplot(data=df_sel, x='trigger_channel', y='conversion_factor')
    g.figure.savefig(args.output_file_pathname)