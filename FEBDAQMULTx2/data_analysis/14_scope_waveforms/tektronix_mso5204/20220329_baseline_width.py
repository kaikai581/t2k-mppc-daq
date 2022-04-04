#!/usr/bin/env python

from glob import glob
from pathlib import Path
from scipy.stats import expon
from statistics import mean, stdev
from waveform_tools import ScopeWaveform
import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns
import sys
sys.dont_write_bytecode=True

class BaselineWidth:
    def __init__(self, infpns, amp_per_pe, dataset_name):
        self.infpns = infpns
        self.amp_per_pe = amp_per_pe
        self.dataset_name = dataset_name
        self.df = None

        # load data into a dataframe
        self.load_data()
        # add a column for the dataset name
        self.df['dataset_name'] = dataset_name
        self.df['waveform voltage / voltage per p.e.'] = self.df.waveform_value/amp_per_pe
    
    def load_data(self):
        dfs = []
        for infpn in self.infpns:
            dfs.append(ScopeWaveform(infpn).df)
        self.df = pd.concat(dfs)

if __name__ == '__main__':
    # compare baseline width
    baseline_0321 = BaselineWidth(glob('20220321_data_58V/*.csv'), 11, '0321_58V_VME')
    baseline_0329_same = BaselineWidth(glob('20220329_rate_waveform_57V_amp_in_box_25C/*.csv'), 14, '0329_57V_preamp_same_box')
    baseline_0329_diff = BaselineWidth(glob('20220329_rate_waveform_57V_amp_diff_box_25C/*.csv'), 8.8, '0329_57V_preamp_diff_box')

    df_grand = pd.concat([baseline_0321.df, baseline_0329_same.df, baseline_0329_diff.df])
    out_fpn = 'plots/baseline_comparison.png'
    g = sns.histplot(data=df_grand, x='waveform voltage / voltage per p.e.', hue='dataset_name')
    g.figure.savefig(out_fpn)
