#!/usr/bin/env python

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../utilities'))

import argparse
import common_tools
import matplotlib.pyplot as plt
import pandas as pd

def plot_figure(mark_feb=False):
    fig, ax = plt.subplots()
    for df, meas_id in zip(dfs, meas_ids):
        ax.errorbar(x=df.ch_id, y=df.breakdown_voltage, yerr=df.breakdown_voltage_err, fmt='o', markersize=4, linestyle='', label=meas_id.split('_')[0])
    ax.grid(True)
    ax.set_xlabel(r'channel number (board$\times32$+channel)')
    ax.set_ylabel('breakdown voltage (V)')
    ax.set_title('FEB channel matched' if args.no_swap else 'PCB channel matched')
    ax.legend()

    # mark FEB
    outfpn = 'plots/{}_matched_{}_{}.png'.format('FEB' if args.no_swap else 'PCB', meas_id1, meas_id2)
    leftx = -0.5
    rightx = 31.5
    if mark_feb:
        ax.axvspan(leftx, rightx, facecolor='magenta', alpha=0.1)
        ax.axvspan(leftx+32, rightx+32, facecolor='blue', alpha=0.1)
        ax.text(0.25, 0.7, 'old FEB', size=15, color='purple', transform=ax.transAxes)
        ax.text(0.55, 0.7, 'returned new FEB', size=15, color='purple', transform=ax.transAxes)
        outfpn = 'plots/{}_matched_{}_{}_feb_marked.png'.format('FEB' if args.no_swap else 'PCB', meas_id1, meas_id2)
    
    # save to file
    common_tools.easy_save_to(plt, outfpn)
    plt.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d1', '--input_database1', type=str, default='processed_data/breakdown_database.csv')
    parser.add_argument('-d2', '--input_database2', type=str, default=None, help='If this is left none, all data are obtained from database1.')
    parser.add_argument('-m1', '--measurement_id1', type=str, default='20210112_lanl_bd1_64ch_thr220_temp20')
    parser.add_argument('-m2', '--measurement_id2', type=str, default='20210119_lanl_bd1_64ch_thr220_temp20_feb_swap')
    parser.add_argument('--no_swap', action='store_true', help='Don\'t swap the FEB channel numbers for the first dataset. Default: False')
    args = parser.parse_args()
    in_db_name1 = args.input_database1
    in_db_name2 = args.input_database2
    meas_id1 = args.measurement_id1
    meas_id2 = args.measurement_id2

    # load dataframes
    dfs = []
    meas_ids = [meas_id1, meas_id2]
    if in_db_name2 == None:
        for meas_id in meas_ids:
            df = pd.read_csv(in_db_name1)
            df = df[df.measurement_id == meas_id]
            if (meas_id == meas_id1) and (not args.no_swap):
                df['ch_id'] = ((df.board+1)%2) * 32 + df.channel
            else:
                df['ch_id'] = df.board * 32 + df.channel
            df['ch_label'] = df.apply(lambda x: 'b{}c{}'.format(x['board'], x['channel']), axis=1)
            dfs.append(df)
            # print(df.head())
            print(len(df))
    else:
        df1 = pd.read_csv(in_db_name1)
        df1 = df1[df1.measurement_id == meas_id1]
        df2 = pd.read_csv(in_db_name2)
        df2 = df2[df2.measurement_id == meas_id2]
        for df in [df1, df2]:
            if (df == df1) and (not args.no_swap):
                df['ch_id'] = ((df.board+1)%2) * 32 + df.channel
            else:
                df['ch_id'] = df.board * 32 + df.channel
            df['ch_label'] = df.apply(lambda x: 'b{}c{}'.format(x['board'], x['channel']), axis=1)
            dfs.append(df)
            print(len(df))

    plot_figure()
    plot_figure(mark_feb=True)
