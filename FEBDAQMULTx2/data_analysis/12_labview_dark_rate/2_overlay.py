#!/usr/bin/env python
'''
Overlay multiple DCR vs. threshold plots.
'''

import argparse
import matplotlib
matplotlib.use('Agg')
import numpy as np
import os
import pandas as pd
import seaborn as sns

class overlay:
    def __init__(self, infpns, config_list=[]):
        self.infpns = infpns

        self.df = self.load_join(config_list)
    
    def load_join(self, config_list):
        '''
        Load CSV files and join them on threshold values.
        '''

        # overwrite the config list
        self.config_list = [f'rate (Hz) {i}' for i in range(1, len(self.infpns)+1)]
        for i in range(len(config_list)):
            if i < len(self.config_list):
                self.config_list[i] = config_list[i]
        
        df = pd.read_csv(self.infpns[0])
        df[self.config_list[0]] = np.log10(df['rate (Hz)'])
        df.drop(columns='rate (Hz)', inplace=True)

        for i in range(1, len(self.infpns)):
            df1 = pd.read_csv(self.infpns[i])
            df1[self.config_list[i]] = np.log10(df1['rate (Hz)'])
            df1.drop(columns='rate (Hz)', inplace=True)
            df = pd.merge(df, df1, how='outer', on='threshold (mV)')

        return df
    
    def overlay_plot(self):
        '''
        To solve the grid line problem, see here:
        https://stackoverflow.com/questions/65029406/how-to-add-vertical-gridlines-in-seaborn-catplot-with-multiple-column-plots
        '''
        df = self.df.melt('threshold (mV)', value_name='rate (Hz)', var_name='config')
        # sns.set_style({'axes.grid' : True})
        g = sns.factorplot(x='threshold (mV)', y='rate (Hz)', hue='config', data=df)
        g.set_xticklabels(step=10)
        g.set_ylabels(r'$log_{10}(rate/Hz)$')
        for ax in g.axes.flat:
            ax.grid(True, axis='both')
        g.savefig('plots/overlay.png')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_filenames', type=str, nargs='*', default=['combined_data/2021-08-19-15-B-SK-CH2.csv', 'combined_data/2021-08-24-18-B-SK-CH2.csv'])
    parser.add_argument('-c', '--config_desc', type=str, nargs='*', default=['1 filter', '2 filters'])
    args = parser.parse_args()
    
    my_overlay = overlay(args.input_filenames, args.config_desc)
    # print(my_overlay.df.columns)
    my_overlay.overlay_plot()
