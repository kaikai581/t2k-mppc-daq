#!/usr/bin/env python

import argparse
import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns
import sys

def gain_one_dataset(ds, bid, prom, lth, rth):
    # load database into a dataframe
    infpn = os.path.join(os.path.dirname(__file__), '../processed_data/gain_database.csv')
    try:
        df = pd.read_csv(infpn)
    except:
        e = sys.exc_info()[0]
        print('Error: {}'.format(e))
        sys.exit(0)
    
    # select rows
    df = df[(df['filename'] == ds) & (df['prominence'] == prom) & (df['left_threshold'] == lth) & (df['right_threshold'] == rth)]
    if bid > 0:
        df = df[df['board'] == bid]
    df['channel ID'] = df['channel'] + 32*df['board']
    df['good fit'] = ((df['r2'] < 1) & (df['r2'] > 0.99))
    
    # REF: https://stackoverflow.com/questions/53670308/use-seaborn-to-plot-1d-time-series-as-a-line-with-marginal-histogram-along-y-axi
    # make seaborn plots
    # grid = sns.JointGrid(data=df, x='channel ID', y='gain', hue='good fit', ratio=3)
    # grid.plot_joint(sns.scatterplot)
    # plt.sca(grid.ax_marg_y)
    # sns.distplot(grid.y, kde=False, vertical=True)
    # grid.fig.set_size_inches(10,6)
    # grid.ax_marg_x.remove()
    # grid.ax_joint.spines['top'].set_visible(True)

    df_good = df[(df['r2'] < 1) & (df['r2'] > 0.99)]
    df_doubt = df[(df['r2'] == 1) | (df['r2'] < 0.99)]
    # ax1 = df_good.plot.scatter(x='channel ID',y='gain')
    # df_doubt.plot.scatter(x='channel ID',y='gain', ax=ax1, c='r')
    # print(df_good)


    # convention implementation
    _, (ax, axhist) = plt.subplots(ncols=2, sharey=True,
                                 gridspec_kw={"width_ratios" : [3,1], "wspace" : 0})
    ax.scatter(df_good['channel ID'], df_good['gain'], marker='o', c='g', label='good linear fit')
    ax.scatter(df_doubt['channel ID'], df_doubt['gain'], marker='x', c='r', label='bad linear fit')
    axhist.hist(df['gain'], bins='auto', ec='g', orientation="horizontal", histtype='step')
    axhist.tick_params(axis="y", left=False)

    ax.set_xlabel('channel ID')
    ax.set_ylabel('total gain (ADC/PE)')
    ax.legend()
    ax.set_title('bias voltage: {} V'.format(get_voltage_from_filename(ds)))
    ax.set_ylim(top=100, bottom=20)
    ax.grid(axis='y')
    axhist.grid(axis='y')
    plt.tight_layout()

    # save to disk
    out_dir = 'plots'
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    plt.savefig(os.path.join(out_dir, os.path.basename(ds).rstrip('h5')+'png'))

def get_voltage_from_filename(fn):
    bias_volt = -1
    for tmpstr in fn.split('_'):
        if 'volt' in tmpstr:
            bias_volt = tmpstr.lstrip('volt')
    return bias_volt

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-ds', '--dataset', type=str, default='20200911_180348_mppc_volt58.0_temp20.0.h5')
    parser.add_argument('-b', '--board', type=int, default=-1)
    parser.add_argument('-p', '--prominence', type=int, default=250)
    parser.add_argument('-l', '--left_threshold', type=float, default=0.7)
    parser.add_argument('-r', '--right_threshold', type=float, default=1.23)
    args = parser.parse_args()
    
    # plot one dataset
    gain_one_dataset(args.dataset, args.board, args.prominence, args.left_threshold, args.right_threshold)