#!/usr/bin/env python
'''
This is the script to compare VME data with the CAEN data.
The data source can be either from the real MPPC pulse or from a pulser.
'''

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../utilities'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../12_labview_dark_rate'))

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from dark_rate_vs_threshold import make_plot_from_raw
import argparse
import common_tools
import glob
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import uproot

class CaenMeasurement:
    def __init__(self, infpns):
        self.infpns = infpns
        self.df_rate = pd.DataFrame(columns=['threshold (DAC)', 'rate (Hz)'])
        self.load_data()
    
    def load_data(self):
        # load data from the metadata tree
        uproot_ver = common_tools.get_uproot_version()
        if uproot_ver <= 3:
            print(f'The uproot version in use is {uproot_ver}, which is not supported by this script.')
            print('Please use a newer version')
            sys.exit(-1)
        
        # load data trees one by one
        x_dac = []
        y_rate = []
        for f in self.infpns:
            tr = uproot.open(f)['mppc']
            df = tr.arrays(library='pd')
            rate = len(df)/(df['ns_epoch'].max()-df['ns_epoch'].min())*1e9
            y_rate.append(rate)
            
            tr_metadata = uproot.open(f)['metadata']
            df_metadata = tr_metadata.arrays(library='pd')

            x_dac.append(df_metadata[df_metadata.isTrigger == True]['DAC'].iloc[0])
            self.df_rate.loc[len(self.df_rate)] = [df_metadata[df_metadata.isTrigger == True]['DAC'].iloc[0], rate]
        board = df_metadata[df_metadata.isTrigger == True]['board'].iloc[0]
        channel = df_metadata[df_metadata.isTrigger == True]['channel'].iloc[0]

class VmeMeasurement:
    def __init__(self, infpns):
        self.dfs_raw = []
        self.df_rate = pd.DataFrame(columns=['threshold (mV)', 'rate (Hz)'])
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
                self.df_rate.loc[len(self.df_rate)] = [int(thr), df[thr].iloc[2:].mean()]

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

def plot_side_by_side(vme_input, caen_input):
    vme_meas = VmeMeasurement(vme_input)
    caen_meas = CaenMeasurement(caen_input)

    # find the maximum value of the y axis
    y_max = max(list(vme_meas.df_rate['rate (Hz)'])+list(caen_meas.df_rate['rate (Hz)']))
    print(y_max)
    print(vme_meas.df_rate.info())
    print(caen_meas.df_rate.info())

    fig, axes = plt.subplots(nrows=1, ncols=2)
    vme_meas.df_rate.plot.scatter(ax=axes[0], x='threshold (mV)', y='rate (Hz)', title='rate with VME')
    caen_meas.df_rate.plot.scatter(ax=axes[1], x='threshold (DAC)', y='rate (Hz)', title='rate with CAEN')
    for axis in axes:
        axis.set_ylim([100, y_max*1.05])
        axis.set_yscale('log')
        axis.grid('both')
    plt.tight_layout()
    fig.savefig('plots/vme_vs_caen.png')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--vme_input', type=str, default=['../data/labview/20220119_pulser/2022-01-19-164814-B-PULSER-CH0.txt'])
    parser.add_argument('--caen_input', type=str, nargs='*', default=glob.glob('../data/root/dark/20220128_162626_funcgen_1kHz_10mV_feb428_ch31/*.root'))
    args = parser.parse_args()

    plot_side_by_side(args.vme_input, args.caen_input)
