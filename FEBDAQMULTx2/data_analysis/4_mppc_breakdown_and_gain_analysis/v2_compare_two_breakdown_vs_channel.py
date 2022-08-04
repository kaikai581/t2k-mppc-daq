#!/usr/bin/env python
feb_sys = {'feb1': '136', 'feb2': '428', 'feb3': '12808', 'feb4': '13294'}
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../utilities'))

import argparse
import common_tools
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import chi2_contingency
import numpy as np

def get_dac_offset(feb_sns):
    df_dac_offset = pd.read_csv(f'processed_data/dac_offset_feb{feb_sns[0]}.csv')
    df_dac_offset2 = pd.read_csv(f'processed_data/dac_offset_feb{feb_sns[1]}.csv')
    df_dac_offset_ret = pd.DataFrame(columns=['ch_id', 'dac_offset'])
    df_dac_offset_ret['ch_id'] = [i for i in range(len(df_dac_offset) + len(df_dac_offset2))]
    df_dac_offset_ret['dac_offset'] = list(df_dac_offset['DAC offset (V)']) + list(df_dac_offset2['DAC offset (V)'])
    return df_dac_offset_ret

def plot_figure(title, legend, mark_feb=False, dac_offset=True):
    fig, ax = plt.subplots()
    for df, meas_id in zip(dfs, meas_ids):
        if dac_offset:
            ax.errorbar(x=df.ch_id, y=df.corrected_breakdown_voltage, yerr=df.breakdown_voltage_err, fmt='o', markersize=3,
                        linestyle='', label=meas_id.split('_')[0])
        else:
            ax.errorbar(x=df.ch_id, y=df.breakdown_voltage, yerr=df.breakdown_voltage_err, fmt='o', markersize=3,
                        linestyle='', label=meas_id.split('_')[0])
    ax.grid(True)
    ax.set_xlabel(r'channel number')
    ax.set_ylabel('breakdown voltage (V)')
    ax.set_ylim([50, 53])
    if dac_offset:
        ax.set_title(title+' dac_corrected')
    else:
        ax.set_title(title)
    ax.legend(legend)

    # mark FEB
    outfpn = 'plots/{}_matched_{}_{}.png'.format('FEB' if args.no_swap else 'PCB', meas_id1, meas_id2)
    leftx = -0.5
    rightx = 31.5
    if mark_feb:
        ax.axvspan(leftx, rightx, facecolor='magenta', alpha=0.1)
        ax.axvspan(leftx+32, rightx+32, facecolor='blue', alpha=0.1)
        ax.text(0.25, 0.7, 'FEB1', size=15, color='purple', transform=ax.transAxes)
        ax.text(0.55, 0.7, 'FEB2', size=15, color='purple', transform=ax.transAxes)
        outfpn = 'plots/{}_matched_{}_{}_feb_marked.png'.format('FEB' if args.no_swap else 'PCB', meas_id1, meas_id2)
    
    # save to file
    common_tools.easy_save_to(plt, outfpn)
    plt.close()

def plot_distributions(title, legend, dac_offset=True):
    plt.style.use('bmh')
    fig, ax = plt.subplots()
    for df, meas_id in zip(dfs, meas_ids):
        if dac_offset:
            ax.hist(df.corrected_breakdown_voltage, histtype='stepfilled', bins = 12, range=(50, 53),alpha=0.6, density=False)
        else:
            ax.hist(df.breakdown_voltage, histtype='stepfilled', alpha=0.6, density = False)

    ax.grid(True)
    ax.set_xlabel('breakdown voltage (V)')
    ax.legend(legend)

    if dac_offset:
        ax.set_title(title + ' dac_corrected')
        outfpn = 'plots/compare_distribution_{}_matched_{}_{}_dac_offset.png'.format('FEB' if args.no_swap else 'PCB',
                                                                                     meas_id1, meas_id2)
    else:
        ax.set_title(title)
        outfpn = 'plots/compare_distribution_{}_matched_{}_{}.png'.format('FEB' if args.no_swap else 'PCB', meas_id1,
                                                                          meas_id2)
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
            #df = df[df.measurement_id == meas_id]
            if (meas_id == meas_id1) and (not args.no_swap):
                df['ch_id'] = ((df.board+1)%2) * 32 + df.channel
            else:
                df['ch_id'] = df.board * 32 + df.channel
            df['ch_label'] = df.apply(lambda x: 'b{}c{}'.format(x['board'], x['channel']), axis=1)
            dfs.append(df)
            df.as_matrix()
            # print(df.head())
            print(len(df))
    else:
        df1 = pd.read_csv(in_db_name1)
        #df1 = df1[df1.measurement_id == meas_id1]
        df2 = pd.read_csv(in_db_name2)
        #df2 = df2[df2.measurement_id == meas_id2]
        df1_febs = [feb_sys['feb3'], feb_sys['feb4']]
        df2_febs = [feb_sys['feb3'], feb_sys['feb4']]
        for df, febs in zip([df1, df2], [df1_febs, df2_febs]):
            if (df.equals(df1)) and (not args.no_swap):
                df['ch_id'] = ((df.board+1)%2) * 32 + df.channel
            else:
                df['ch_id'] = df.board * 32 + df.channel
            df['ch_label'] = df.apply(lambda x: 'b{}c{}'.format(x['board'], x['channel']), axis=1)
            offsets = get_dac_offset(febs)
            df = pd.merge(df, offsets, how='left', on='ch_id')
            df['corrected_breakdown_voltage'] = df['breakdown_voltage']+df['dac_offset']
            dfs.append(df)
            print(len(df))

    ttl = 'SN8 Breakdown voltages with swapped SAMTEC Cables'
    leg = ['Control', 'FEB3=Bottom Half, FEB4=Top half']
    plot_figure(title = ttl,
                legend=leg, dac_offset=True)
    plot_figure(mark_feb=True, title = ttl,
                legend=leg, dac_offset=True)
    plot_distributions(title = ttl,
                       legend=leg, dac_offset=True)


