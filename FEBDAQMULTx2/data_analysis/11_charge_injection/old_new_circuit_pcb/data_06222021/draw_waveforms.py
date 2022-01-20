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

        # add a partial sum column
        self.waveform_partial_integral()
    
    def waveform_partial_integral(self):
        '''
        Partial sum of the waveform to study the pulse area.
        '''
        self.df['partial_integral'] = self.df.waveform_value.cumsum()

class TwoScopeWaveforms:
    def __init__(self, infpns):
        self.dfs1 = ScopeWaveform(infpns[0]).df
        self.dfs2 = ScopeWaveform(infpns[1]).df

        # find the time shift to best match the two pulses
        self.best_time_unit_shift = None
    
    def best_time_shift(self):
        '''
        Find the time shift to best match the two waveforms.
        '''
        min_diff = sys.maxsize
        min_sh = sys.maxsize
        for i in range(-100, 101):
            diff = (self.dfs1['waveform_value'][200+i:400+i] - self.dfs2['waveform_value']).sum()
            if diff < min_diff:
                min_diff = diff
                min_sh = i
        self.best_time_unit_shift = i
        return min_sh, min_diff
    
    def make_plots(self, t_range=[-sys.maxsize, sys.maxsize]):
        '''
        Plot the waveforms.
        '''
        out_dir = 'plots'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        
        if self.best_time_unit_shift != None:
            self.dfs1['waveform_value_shifted'] = self.dfs1.waveform_value.shift(periods=11)

        # melt the dataframe
        df = pd.merge(self.dfs1[['time', 'waveform_value_shifted']],
                  self.dfs2[['time', 'waveform_value']],
                  on='time', how='outer', indicator=True)
        df = df.rename(columns={'waveform_value_shifted': 'old: breadboard + T', 'waveform_value': 'new: PCB + T'})[['time', 'old: breadboard + T', 'new: PCB + T']]
        df = df.melt('time', var_name='circuit', value_name='pulse height (V)')

        # 
        g = sns.lineplot(data=df[(df.time >= t_range[0]) & (df.time <= t_range[1])], x='time', y='pulse height (V)', hue='circuit')
        g.figure.tight_layout()
        g.figure.savefig(f'{out_dir}/matched_pulse_height_comparison_t{t_range[0]:.2e}_{t_range[1]:.2e}.jpg')
        g.figure.clf()

def make_plot(df, t_range=[-sys.maxsize, sys.maxsize]):
    out_dir = 'plots'
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    if t_range[1] == sys.maxsize:
        g = sns.scatterplot(data=df, x='time', y='pulse height (V)', hue='circuit')
        g.figure.tight_layout()
        g.figure.savefig(f'{out_dir}/pulse_height_comparison.jpg')
        g.figure.clf()
    else:
        g = sns.scatterplot(data=df[(df.time >= t_range[0]) & (df.time <= t_range[1])], x='time', y='pulse height (V)', hue='circuit')
        g.figure.tight_layout()
        g.figure.savefig(f'{out_dir}/pulse_height_comparison_t{t_range[0]:.2e}_{t_range[1]:.2e}.jpg')
        g.figure.clf()

if __name__ == '__main__':
    infpns = ['old_breadboard_50ohm_140131_130100000.csv', 'new_pcb_50ohm_140131_130100001.csv']
    my_wfms = TwoScopeWaveforms(infpns)
    print(my_wfms.best_time_shift())
    my_wfms.make_plots([-.2e-7, .5e-7])

    old_wf = ScopeWaveform('old_breadboard_50ohm_140131_130100000.csv')
    new_wf = ScopeWaveform('new_pcb_50ohm_140131_130100001.csv')
    print(old_wf.df)
    print(new_wf.df)
    df = pd.merge(old_wf.df[['time', 'waveform_value']],
                  new_wf.df[['time', 'waveform_value']],
                  on='time', how='outer', indicator=True)
    df = df.rename(columns={'waveform_value_x': 'old: breadboard + T', 'waveform_value_y': 'new: PCB + T'})[['time', 'old: breadboard + T', 'new: PCB + T']]
    df = df.melt('time', var_name='circuit', value_name='pulse height (V)')
    print(df)

    make_plot(df)
    make_plot(df, [-.2e-7, .5e-7])