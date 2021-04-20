#!/usr/bin/env python

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../utilities'))

import argparse
import common_tools
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# redirect output to avoid x11 error
import matplotlib
matplotlib.use('Agg')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--input_database', type=str, default='processed_data/breakdown_database.csv')
    parser.add_argument('-m', '--measurement_id', type=str, default='20210112_lanl_bd1_64ch_thr220_temp20')
    args = parser.parse_args()
    in_db_name = args.input_database
    meas_id = args.measurement_id

    # load dataframe
    df = pd.read_csv(in_db_name)
    df = df[df.measurement_id == meas_id]
    df['ch_id'] = df.board * 32 + df.channel
    df['ch_label'] = df.apply(lambda x: 'b{}c{}'.format(x['board'], x['channel']), axis=1)
    print(df.head(64))

    # use dataframe to make plot
    # ax = df.plot.scatter(x='ch_id', y='breakdown_voltage', yerr='breakdown_voltage_err')
    # # ax.set_xticks(df.ch_id)
    # # ax.set_xticklabels(df.ch_label, rotation=90)
    # plt.ylabel('breakdown voltage (V)')
    # plt.xlabel(r'channel number (board$\times$32+channel)')
    # plt.grid(True)

    # use seaborn to make plot
    fig, (ax, axhist) = plt.subplots(ncols=2, sharey=True,
                                     gridspec_kw={"width_ratios" : [3,1], "wspace" : 0})
    fig.set_size_inches(10, 5)
    ax.errorbar(x=df['ch_id'], y=df['breakdown_voltage'], yerr=df['breakdown_voltage_err'], fmt='o')
    ax.grid(True)
    ax.set_ylabel('breakdown voltage (V)')
    ax.set_xlabel('PCB channel number')

    axhist.hist(df['breakdown_voltage'], bins='auto', orientation='horizontal', histtype='step')
    axhist.tick_params(axis="y", left=False)
    axhist.grid(axis='y')

    # save figure to file
    outfpn = 'plots/{}/vbd_vs_ch.png'.format(meas_id)
    common_tools.easy_save_to(plt, outfpn)
    print('Output figure to', outfpn)
