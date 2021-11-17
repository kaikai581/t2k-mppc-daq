#!/usr/bin/env python
'''
This script takes multiple csv files as input and compares the conversion factor.
'''

import argparse

# redirect output figures
import matplotlib
matplotlib.use('Agg')

import os
import pandas as pd
import seaborn as sns

class calibration_comparison:
    def __init__(self, infpns):
        self.infpns = infpns
        self.dfs = []
        self.df = None

        # fills the dfs and df attibutes
        self.load_files()
    
    def load_files(self):
        for infpn in self.infpns:
            df = pd.read_csv(infpn, index_col=None)
            df['dataset & processing'] = os.path.splitext(os.path.basename(infpn))[0]
            self.dfs.append(df)
        self.df = pd.concat(self.dfs)
    
    def make_plot(self, outfpn):
        # make sure the output folder exists
        out_dir = os.path.dirname(outfpn)
        if not out_dir: out_dir = 'plots'
        out_fn = os.path.basename(outfpn)
        out_fpn = os.path.join(out_dir, out_fn)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        ax = sns.scatterplot(data=self.df, x='trigger_channel', y='conversion_factor', hue='dataset & processing')
        ax.set_xlabel('FEB channel')
        ax.set_ylabel('conversion factor (electrons/ADC)')
        ax.figure.savefig(out_fpn)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_filenames', nargs='*', default=['processed_data/20210413_breadboard_with_t_feb428_mpv.csv', 'processed_data/20210625_new_pcb_without_t_feb428_gauss.csv', 'processed_data/20210625_new_pcb_without_t_feb428_mpv.csv'])
    parser.add_argument('-o', '--output_file_pathname', type=str, default='plots/output.png')
    args = parser.parse_args()

    my_comparison = calibration_comparison(args.input_filenames)
    my_comparison.make_plot(args.output_file_pathname)
