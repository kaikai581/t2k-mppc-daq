#!/usr/bin/env python
'''
This script compares the breakdown voltage measurements of the LSU MPPC-PCB from LSU, UTotyo and Hamamatsu.
'''

import argparse

from pandas.io import parsers
import data_interface
import os
import pandas as pd
import seaborn as sns

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data_path', type=str, default='data/20210422_first_meeting')
    args = parser.parse_args()

    # load data files
    utokyo_meas = data_interface.utokyo_data(f'{args.data_path}/Utokyo_PCB_Measurement_For crschk_ .xlsx')
    lsu_meas = data_interface.lsu_data(f'{args.data_path}/mppc_summary_utokyo_pcb_lsu_measurements.csv')

    # join into a single table
    df_join = pd.merge(left=utokyo_meas.df_data, right=lsu_meas.df_data, left_on='channel', right_on='channel')
    sel_cols_base = ['channel', 'Hamamatsu measured Vbr_x', 'Utokyo measured Vbr|Temp=25C']
    my_cols = ['Vbr peak fit|Temp=25C', r'Vbr spectrum shape fit|Temp=25C', r'Vbr peak fit ped removed|Temp=25C']
    my_method_names = ['peak_fit', 'peak_fit_ped_removed', 'spectrum_shape']

    out_dir = f'plots/{args.data_path}'
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # loop through all 3 methods
    for col, method_name in zip(my_cols, my_method_names):
        sel_cols = sel_cols_base + [col]
        df_cur = df_join[sel_cols]
        
        df_cur = df_cur.melt('channel', var_name='institution',  value_name='breakdown voltage (v)')
        g = sns.relplot(x='channel', y='breakdown voltage (v)', hue='institution', data=df_cur)
        g.tight_layout()
        g.fig.savefig(f'{out_dir}/Vbd_utokyo_pcb_lsu_utokyo_hamamatsu_{method_name}.jpg')
