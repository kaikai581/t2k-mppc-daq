#!/usr/bin/env python

import argparse
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import sys

def gain_voltage_from_dataframe(df):
    print(df)
    fn = df['filename'].iloc[0]
    print(fn)
    for substr in fn.split('_'):
        if 'volt' in substr:
            voltage = substr.lstrip('volt')
    print(voltage, df['gain'].iloc[[0]][0])
    return float(voltage), float(df['gain'].iloc[0])


def process_one_channel(infpn, datasets, bnum, cnum, prom=250, lth=0.7, rth=1.4):

    ch_id = 'b{}_ch{}'.format(bnum, cnum)
    if infpn:
        with open(infpn) as json_file:
            gains = json.load(json_file)

        # x and y points for retrieving breakdown voltage
        x_vbd = np.array(list(gains.keys())).astype(float)
        y_vbd = np.array([gains[v][ch_id] for v in gains.keys()])
    else:
        x_vbd = []
        y_vbd = []
        df = pd.read_csv('processed_data/gain_database.csv')
        for ds in datasets:
            # select rows
            df_sel = df[(df['filename'] == ds) & (df['prominence'] == prom) & (df['left_threshold'] == lth) & (df['right_threshold'] == rth) & (df['board'] == bnum) & (df['channel'] == cnum)].reset_index()
            x, y = gain_voltage_from_dataframe(df_sel)
            x_vbd.append(x)
            y_vbd.append(y)
            print('Working on {}...'.format(ds))
        x_vbd = np.array(x_vbd)
        y_vbd = np.array(y_vbd)

    # make the linear plot
    coeff, residuals, _, _, _ = np.polyfit(x_vbd, y_vbd, 1, full=True)
    xmax = max(x_vbd)*1.05
    fitx = np.linspace(0, xmax, 100)
    fity = coeff[0]*fitx + coeff[1]
    xmin = -coeff[1]/coeff[0]*.9
    ax_fit_line = plt.subplot(111)
    ax_fit_line.plot(fitx, fity, '--g', alpha=.7)
    ax_fit_line.scatter(x_vbd, y_vbd, marker='o', color='r', s=20)
    ax_fit_line.set_xlim(left=xmin, right=xmax)
    ax_fit_line.set_ylim(bottom=0)
    ax_fit_line.set_xlabel('bias voltage (V)')
    ax_fit_line.set_ylabel('total gain (ADC/PE)')
    ax_fit_line.set_title(ch_id)

    # mark the x-intercept
    xcept = -coeff[1]/coeff[0]
    arrow_ylen = (ax_fit_line.get_ylim()[1]-ax_fit_line.get_ylim()[0])*.2
    arrow_xlen = (ax_fit_line.get_xlim()[1]-ax_fit_line.get_xlim()[0])*.2
    ax_fit_line.annotate('{:.2f}V'.format(xcept), xy=(xcept, 0), xytext=(xcept-arrow_xlen, arrow_ylen),
                         arrowprops=dict(color='magenta', shrink=0.05), c='b')
    # plt.show()

    # prepare the output folder
    if infpn:
        out_dir = os.path.splitext(os.path.basename(infpn))[0]
    else:
        out_dir = datasets[0].split('_')[0]
    out_dir = os.path.join('plots', out_dir)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    outfpn = os.path.join(out_dir, '{}.png'.format(ch_id))
    # save the plot
    plt.savefig(outfpn)
    print('Saved plot {}.'.format(outfpn))
    plt.close()

    return xcept, coeff[0], residuals / (len(x_vbd) - 2)

def process_all_channels(infpn, ds):
    if ((not infpn) or (not os.path.exists(infpn))) and len(ds) == 0:
        print('Input file {} and datasets specified do not exist. Terminating...'.format(infpn))
        sys.exit(-1)
    
    # results containers
    x_vbd = []
    y_vbd = []
    y_totgain = []
    y_chi2 = []
    x_cnt = 0
    # process one channel only
    for bid in range(2):
        for cid in range(32):
            x_vbd.append(x_cnt)
            vbd, total_gain, chi2 = process_one_channel(infpn, ds, bid, cid)
            y_vbd.append(vbd)
            y_totgain.append(total_gain)
            y_chi2.append(chi2)
            x_cnt += 1
    # make summary plot
    _, axes = plt.subplots(3, figsize=(12,8))
    axes[0].scatter(x_vbd, y_vbd, marker='o', color='r', s=20)
    axes[0].set_ylim(bottom = 0, top=max(y_vbd)*1.05)
    axes[0].set_ylabel('breakdown\nvoltage (V)')
    axes[0].set_xlabel('channel ID')
    # fit a horizontal line
    avg_vbd = np.polyfit(x_vbd, y_vbd, 0)
    axes[0].axhline(avg_vbd[0], ls='--', c='magenta', alpha=.5)
    axes[0].text(28, 45, 'avg: {:.2f} V'.format(avg_vbd[0]), color='magenta')
    axes[1].scatter(x_vbd, y_totgain, marker='o', color='g', s=20)
    axes[1].set_ylim(bottom = 0, top=max(y_totgain)*1.05)
    axes[1].set_xlabel('channel ID')
    axes[1].set_ylabel('total gain/voltage\n(ADC/V/PE)')
    axes[2].scatter(x_vbd, y_chi2, marker='o', color='b', s=20)
    axes[2].set_ylim(bottom = min(y_chi2)*.5, top=max(y_chi2)*2)
    axes[2].set_xlabel('channel ID')
    axes[2].set_ylabel(r'$\chi^2$/dof')
    axes[2].set_yscale('log')
    axes[2].grid(axis='y')
    plt.tight_layout()
    
    # prepare the output folder and file name
    out_dir = os.path.splitext(os.path.basename(infpn))[0]
    out_dir = os.path.join('plots', out_dir)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    outfpn = os.path.join(out_dir, 'Vbd_vs_ch.png')
    plt.savefig(outfpn)
    plt.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    # default to the old fashioned value is default='processed_data/20201020_total_gain_peak_cleanup.txt'
    group.add_argument('-i', '--input_file', type=str, nargs='?')
    group.add_argument('-ds', '--datasets', type=str, default='20200911_180348_mppc_volt58.0_temp20.0.h5', nargs='*')
    args = parser.parse_args()
    infpn = args.input_file
    ds = args.datasets

    # fit a line on gain vs voltage and
    # infer the breakdown voltage
    process_all_channels(infpn, ds)
