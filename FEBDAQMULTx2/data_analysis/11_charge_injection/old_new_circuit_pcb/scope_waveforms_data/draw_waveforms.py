#!/usr/bin/env python
'''
Compare the waveforms taken by the MSO5240 scope.
'''

import os
import pandas as pd
import seaborn as sns
import sys

class ScopeWaveform:
    def __init__(self, infpn):
        columns = ['info_name', 'value', 'units', 'time', 'waveform_value']
        self.df = pd.read_csv(infpn, names=columns)

class ScopeWaveforms:
    def __init__(self, infpns):
        self.dfs = []
        for infpn in infpns:
            self.dfs.append(ScopeWaveform(infpn).df)

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