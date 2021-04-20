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
    parser.add_argument('-i', '--input_filenames', type=str, nargs='*', default=['20210112_171715_mppc_volt56.0_temp20.0.root','20210112_171859_mppc_volt57.0_temp20.0.root','20210112_172042_mppc_volt58.0_temp20.0.root','20210112_172226_mppc_volt59.0_temp20.0.root','20210112_172410_mppc_volt60.0_temp20.0.root'])
    parser.add_argument('-d', '--input_database', type=str, default='processed_data/gain_database.csv')
    parser.add_argument('-o', '--output_path', type=str, default='plots/20210112_lanl_bd1_64ch_thr220_temp20')
    parser.add_argument('-p', '--prominence', type=int, default=75)
    parser.add_argument('--color_feb', action='store_true')
    args = parser.parse_args()
    gain_db_pn = args.input_database
    infns = [os.path.basename(fn) for fn in args.input_filenames]

    # load dataframe
    df = pd.read_csv(gain_db_pn)
    df = df[df.filename.isin(infns)]
    df = df[df.prominence == args.prominence]
    if df.pcb_half.isnull().values.any(): # if any row of the pcb_half is NaN, use board id
        df['ch_id'] = df.board * 32 + df.channel
    else:
        df['ch_id'] = df.pcb_half * 32 + df.channel
    df['ch_label'] = df.apply(lambda x: 'b{}c{}'.format(x['board'], x['channel']), axis=1)
    print(df.head())

    # best solution
    # ref: https://www.kite.com/python/answers/how-to-color-a-scatter-plot-by-category-using-matplotlib-in-python
    df_vols = df.groupby('bias_voltage')
    fig, ax = plt.subplots()
    for name, vol_group in df_vols:
        ax.errorbar(vol_group['ch_id'], vol_group['gain'], yerr=vol_group['gain_err'], fmt='o', ms=3, label=round(name, 4))
    ax.set_ylabel('total gain')
    ax.set_xlabel(r'channel number (board$\times$32+channel)')
    ax.grid(True)
    ax.legend(bbox_to_anchor=(1.04,1))
    fig.tight_layout()

    # get preamp gain
    gain = 'gain0'
    for tmpstr in os.path.basename(infns[0]).split('_'):
        if 'gain' in tmpstr:
            gain = tmpstr
            break

    # color the canvas
    outfpn = '{}/gain_vs_ch_{}.png'.format(args.output_path, gain)
    if args.color_feb:
        leftx = -0.5
        rightx = 31.5
        ax.axvspan(leftx, rightx, facecolor='magenta', alpha=0.1)
        ax.axvspan(leftx+32, rightx+32, facecolor='blue', alpha=0.1)
        ax.text(0.25, 0.9, 'old FEB', size=15, color='magenta', transform=ax.transAxes)
        ax.text(0.55, 0.9, 'returned new FEB', size=15, color='blue', transform=ax.transAxes)
        outfpn = '{}/gain_vs_ch_{}_color_feb.png'.format(args.output_path, gain)

    common_tools.easy_save_to(plt, outfpn)
    print('Output figure to', outfpn)
