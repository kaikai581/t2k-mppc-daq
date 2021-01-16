#!/usr/bin/env python

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../utilities'))

import argparse
import common_tools
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_filenames', type=str, nargs='*', default=['20210112_171715_mppc_volt56.0_temp20.0.root','20210112_171859_mppc_volt57.0_temp20.0.root','20210112_172042_mppc_volt58.0_temp20.0.root','20210112_172226_mppc_volt59.0_temp20.0.root','20210112_172410_mppc_volt60.0_temp20.0.root'])
    parser.add_argument('-d', '--input_database', type=str, default='processed_data/gain_database.csv')
    parser.add_argument('-o', '--output_path', type=str, default='plots/20210112_lanl_bd1_64ch_thr220_temp20')
    args = parser.parse_args()
    gain_db_pn = args.input_database
    infns = [os.path.basename(fn) for fn in args.input_filenames]

    # load dataframe
    df = pd.read_csv(gain_db_pn)
    df = df[df.filename.isin(infns)]
    df['ch_id'] = df.board * 32 + df.channel
    df['ch_label'] = df.apply(lambda x: 'b{}c{}'.format(x['board'], x['channel']), axis=1)
    print(df.head())

    # best solution
    # ref: https://www.kite.com/python/answers/how-to-color-a-scatter-plot-by-category-using-matplotlib-in-python
    df_vols = df.groupby('bias_voltage')
    for name, vol_group in df_vols:
        plt.errorbar(vol_group['ch_id'], vol_group['gain'], yerr=vol_group['gain_err'], fmt='o', ms=3, label=name)
    plt.ylabel('total gain')
    plt.xlabel(r'channel number (board$\times$32+channel)')
    plt.grid(True)
    plt.legend()

    common_tools.easy_save_to(plt, '{}/gain_vs_ch.png'.format(args.output_path))