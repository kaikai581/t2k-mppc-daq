#!/usr/bin/env python
'''
Make the dark count rate vs. threshold plot by concatenating multiple files.
'''

import argparse
import matplotlib
matplotlib.use('Agg')
import os
import pandas as pd
import seaborn as sns

class segmented_rate:
    def __init__(self, infpns):
        self.dfs_raw = []
        self.df_rate = pd.DataFrame()
        self.infpns = infpns

        # load all files into dataframes
        self.load_dfs(infpns)
        # calculate rates for each threshold and store to df_rate
        self.calculate_rate()
    
    def calculate_rate(self):
        '''
        Calculate rates for each threshold and store to df_rate.
        '''
        for df in self.dfs_raw:
            for thr in df.columns:
                # self.df_rate[thr] = pd.Series(df[thr].iloc[2:].mean())
                self.df_rate = self.df_rate.append({'threshold (mV)': int(thr), 'rate (Hz)': df[thr].iloc[2:].mean()}, ignore_index=True)

    def cleanup_col(self, df):
        bad_cols = [colname for colname in df.columns if not colname.isnumeric()]
        df.drop(columns=bad_cols, inplace=True)

    def load_dfs(self, infpns):
        for infpn in infpns:
            df = pd.read_csv(infpn, sep='\t', index_col=False)
            self.cleanup_col(df)
            self.dfs_raw.append(df)
    
    def plot_rate_vs_thr(self):
        '''
        Output a summary plot.
        '''
        if len(self.df_rate.columns) == 0:
            print('No rate data found.')
            return
        
        # prepare the output folder
        out_dir = 'plots'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        ax = sns.scatterplot(data=self.df_rate, x='threshold (mV)', y='rate (Hz)')
        ax.set_yscale('log')
        ax.grid('both')
        fig = ax.get_figure()
        fig.tight_layout()
        fig.savefig(f'{out_dir}/dcr_vs_thr.png')
        fig.clf()
    
    def to_csv(self):
        fns = [os.path.splitext(os.path.basename(s))[0] for s in self.infpns]
        out_dir = 'combined_data'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        out_fn = os.path.commonprefix(fns)+os.path.commonprefix([s[::-1] for s in fns])[::-1]+'.csv'
        out_pn = os.path.join(out_dir, out_fn)
        
        self.df_rate.to_csv(out_pn, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_filenames', type=str, nargs='*', default=['data/20210820_LabVIEW_dark_rate/2021-08-19-151915-B-SK-CH2.txt', 'data/20210820_LabVIEW_dark_rate/2021-08-19-152157-B-SK-CH2.txt'])
    args = parser.parse_args()
    
    my_data = segmented_rate(args.input_filenames)
    my_data.plot_rate_vs_thr()
    my_data.to_csv()
