#!/usr/bin/env python
'''
This script takes the exported data from the QUCS simulations and manipulates them.
'''

from pathlib import Path
import argparse
import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns
import sys

class SimCurves:
    def __init__(self, infpns=None):
        self.infpns = infpns
        self.df = None
        self.df_charge = None

        if not self.infpns is None:
            self.load_data()
    
    def add_capacitor_charge(self, probe_name, C=100e-12):
        df_v = self.df[self.df.probe==probe_name].copy()
        df_c = pd.DataFrame()
        df_c['time (s)'] = df_v['time (s)']
        df_c['charge (C)'] = df_v['voltage (V)']*C
        df_c['probe'] = 'capacitor_charge'
        if self.df_charge is None:
            self.df_charge = df_c
        else:
            self.df_charge = pd.concat([self.df_charge, df_c], axis=0, ignore_index=True)

    def add_cumulative_sum(self, curve_name):
        df_curve = self.df[self.df.probe==curve_name].copy()
        df_curve['voltage (V)'] = df_curve['voltage (V)'].cumsum()
        df_curve['probe'] = df_curve['probe'] + '_integral'
        self.df = pd.concat([self.df, df_curve], axis=0, ignore_index=True)

    def add_curve(self, infpn, curve_name=None):
        col_names = ['time (s)', 'voltage (V)', 'voltage2 (V)']
        if curve_name is None:
            curve_name = Path(infpn).stem
        if self.df is None:
            self.df = pd.read_csv(infpn, delimiter=';', names=col_names, skiprows=1)
            self.df['probe'] = curve_name
        else:
            df = pd.read_csv(infpn, delimiter=';', names=col_names, skiprows=1)
            df['probe'] = curve_name
            self.df = pd.concat([self.df, df], axis=0, ignore_index=True)
        
        # after adding the curve, also add it's cumulative sum
        self.add_cumulative_sum(curve_name)
    
    def add_output_charge(self, probe_name, R=50):
        df_v = self.df[self.df.probe==probe_name].copy()
        df_c = pd.DataFrame()
        df_c['time (s)'] = df_v['time (s)']
        dt = df_v['time (s)'].diff().iloc[1]
        df_c['charge (C)'] = df_v['voltage (V)'].cumsum()/R*dt
        df_c['probe'] = 'output_charge'
        if self.df_charge is None:
            self.df_charge = df_c
        else:
            self.df_charge = pd.concat([self.df_charge, df_c], axis=0, ignore_index=True)
    
    def get_probe_dict(self):
        probes = self.df.probe.unique()
        return {i: p for i, p in enumerate(probes)}

    def load_data(self):
        for infpn in self.infpns:
            self.add_curve(infpn)
    
    def make_charge_plot(self, probe_names):
        plt.clf()
        df = self.df_charge[self.df_charge.probe.isin(probe_names)]

        # make sure plots can be saved
        out_dir = 'plots'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        
        out_fn = '_'.join(probe_names)+'.png'
        out_fpn = os.path.join(out_dir, out_fn)
                
        # plot selected curves
        g = sns.scatterplot(data=df, x='time (s)', y='charge (C)', hue='probe', style='probe')
        g.figure.savefig(out_fpn)

    def make_voltage_plot(self, probe_names):
        plt.clf()
        df = self.df[self.df.probe.isin(probe_names)]

        # make sure plots can be saved
        out_dir = 'plots'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        
        out_fn = '_'.join(probe_names)+'.png'
        out_fpn = os.path.join(out_dir, out_fn)
                
        # plot selected curves
        g = sns.scatterplot(data=df, x='time (s)', y='voltage (V)', hue='probe')
        g.figure.savefig(out_fpn)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_pathnames', nargs='*', default=['data/output_voltage.csv'])
    args = parser.parse_args()

    # create instance with specified input files
    my_sim_curves = SimCurves(args.input_pathnames)
    my_sim_curves.add_capacitor_charge('capacitor_voltage')
    my_sim_curves.add_output_charge('output_voltage')

    # # command line query to select curves to plot
    # probe_dict = my_sim_curves.get_probe_dict()
    # print('Select curves to plot:')
    # print('\n'.join(f'{k}: {v}' for k, v in probe_dict.items()))
    # try:
    #     selected_keys = list(map(int, input().split()))
    # except:
    #     print('Selection error... Aborting...')
    #     sys.exit(-1)
    
    # # get the selected curve names
    # try:
    #     selected_probes = [probe_dict[k] for k in selected_keys]
    # except:
    #     print('Selection error... Aborting...')
    #     sys.exit(-1)
    
    # make the plot
    my_sim_curves.make_voltage_plot(['capacitor_voltage', 'input_voltage', 'output_voltage'])
    my_sim_curves.make_charge_plot(['capacitor_charge', 'output_charge'])
