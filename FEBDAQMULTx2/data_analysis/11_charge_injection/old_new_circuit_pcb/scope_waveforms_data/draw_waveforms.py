#!/usr/bin/env python
'''
Compare the waveforms taken by the MSO5240 scope.
'''

import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns
import sys

class ScopeWaveform:
    def __init__(self, infpn, id_name=None):
        columns = ['info_name', 'value', 'units', 'time', 'waveform_value']
        self.df = pd.read_csv(infpn, names=columns)

        # add the name of the waveform and the partial sum of the waveform to data
        self.df['waveform_id'] = id_name
        self.df['waveform_partial_sum'] = self.df.waveform_value.cumsum()

        # get the max amplitude and its index
        self.maxamp, self.maxampidx = self.get_max_amp_and_idx()
    
    def get_max_amp_and_idx(self):
        return self.df.waveform_value.max(), self.df.waveform_value.argmax()

class ScopeWaveforms:
    def __init__(self, infpns):
        self.dfs = []
        for infpn in infpns:
            self.dfs.append(ScopeWaveform(infpn).df)

class TwoWaveforms:
    def __init__(self, wf1, wf2):
        self.wf1 = wf1
        self.wf2 = wf2
        self.df_all = pd.concat([wf1.df, wf2.df])
    
    def plot_waveforms_and_partial_sums(self):
        out_dir = 'plots'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        
        fig, axes = plt.subplots(2, 1, sharex=True)
        sns.scatterplot(data=self.df_all, x='time', y='waveform_value', hue='waveform_id', s=8, ax=axes[0])
        axes[0].set_ylabel('pulse height (mV)')
        axes[0].grid()
        sns.scatterplot(data=self.df_all, x='time', y='waveform_partial_sum', hue='waveform_id', s=8, ax=axes[1])
        axes[1].set_ylabel('partial sum (mV)')
        axes[1].set_xlabel('time')
        axes[1].grid()
        fig.tight_layout()
        fig.savefig(f'{out_dir}/pulse_height_comparison.jpg')
        fig.clf()

def make_plot(df, t_range=[-sys.maxsize, sys.maxsize]):
    out_dir = 'plots'
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    if t_range[1] == sys.maxsize:
        g = sns.scatterplot(data=df, x='time', y='pulse height (mV)', hue='circuit')
        g.figure.tight_layout()
        g.figure.savefig(f'{out_dir}/pulse_height_comparison.jpg')
        g.figure.clf()
    else:
        g = sns.scatterplot(data=df[(df.time >= t_range[0]) & (df.time <= t_range[1])], x='time', y='pulse height (mV)', hue='circuit')
        g.figure.tight_layout()
        g.figure.savefig(f'{out_dir}/pulse_height_comparison_t{t_range[0]:.2e}_{t_range[1]:.2e}.jpg')
        g.figure.clf()

if __name__ == '__main__':
    # infpns = ['scope_waveforms_data/old_pcb_50ohm_140131_130100000.csv', 'scope_waveforms_data/new_pcb_50ohm_140131_130100000.csv']
    # my_wfms = ScopeWaveforms(infpns)
    # print(my_wfms.dfs[0])

    old_wf = ScopeWaveform('old_pcb_50ohm_140131_130100000.csv')
    new_wf = ScopeWaveform('new_pcb_50ohm_140131_130100000.csv')
    print(old_wf.df)
    print(new_wf.df)
    df = pd.merge(old_wf.df[['time', 'waveform_value']],
                  new_wf.df[['time', 'waveform_value']],
                  on='time', how='outer', indicator=True)
    df = df.rename(columns={'waveform_value_x': 'old: breadboard + T', 'waveform_value_y': 'new: PCB + dual output'})[['time', 'old: breadboard + T', 'new: PCB + dual output']]
    df = df.melt('time', var_name='circuit', value_name='pulse height (mV)')
    print(df)

    make_plot(df)
    make_plot(df, [-.2e-7, .5e-7])