#!/usr/bin/env python

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../utilities'))

import argparse
import common_tools
import matplotlib.pyplot as plt
import pandas as pd

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

    ax = df.plot.scatter(x='ch_id', y='breakdown_voltage', yerr='breakdown_voltage_err')
    # ax.set_xticks(df.ch_id)
    # ax.set_xticklabels(df.ch_label, rotation=90)
    plt.ylabel('breakdown voltage (V)')
    plt.xlabel(r'channel number (board$\times$32+channel)')
    plt.grid(True)
    common_tools.easy_save_to(plt, 'plots/{}/vbd_vs_ch.png'.format(meas_id))
