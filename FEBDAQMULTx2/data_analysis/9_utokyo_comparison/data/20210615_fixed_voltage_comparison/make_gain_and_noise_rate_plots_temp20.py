#!/usr/bin/env python
'''
This script compares the gain and dark noise rate measurements
of the UTokyo MPPC-PCB from LSU and UTotyo at a fixed bias voltage.
'''

import argparse
import os
import pandas as pd
import seaborn as sns

class this_data:
    def __init__(self, infpn):
        '''
        This constructor tries to load the excel file provided by UTokyo directly.

        Column names are as follows.
        ['LSU measured Vbr|Temp=20C',
         'By UTokyo MPPC Gain @ bias_voltage=57V|Temp=20C',
         'By UTokyo Noise Rate @ bias_voltage=57V npe=1.5|Temp=20C',
         'By LSU MPPC Gain @ over_voltage=5V|Temp=20C',
         'By LSU Noise Rate @ bias_voltage=57V npe=1.5|Temp=20C',
         'By LSU Uncalibrated Gain @ bias_voltage=57V|Temp=20C',
         'calibration factor from charge injection (electrons/ADC)',
         'By LSU Calibrated Gain @ bias_voltage=57V|Temp=20C',
         'channel']
        '''
        
        self.df_data = pd.read_csv(infpn, index_col=0)
        self.df_data['channel'] = range(64)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data_path', type=str, default='LSU_0_20_57.csv')
    args = parser.parse_args()
    my_data = this_data(args.data_path)
    
    # make the output folder
    out_dir = '../../plots'
    foldername = os.path.dirname(os.path.abspath(__file__)).split('/')[-1]
    out_dir = os.path.join(out_dir, foldername)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # plot gain
    df = my_data.df_data[['By LSU Calibrated Gain @ bias_voltage=57V|Temp=20C', 'By UTokyo MPPC Gain @ bias_voltage=57V|Temp=20C', 'channel']]
    df = df.melt('channel', var_name='institution',  value_name='MPPC gain')
    g = sns.relplot(x='channel', y='MPPC gain', hue='institution', data=df)
    g.tight_layout()
    g.fig.savefig(f'{out_dir}/mppc_gain_lsu_pcb_lsu_utokyo_temp20.jpg')

    # plot dark noise rate
    df = my_data.df_data[['By LSU Noise Rate @ bias_voltage=57V npe=1.5|Temp=20C', 'By UTokyo Noise Rate @ bias_voltage=57V npe=1.5|Temp=20C', 'channel']]
    df = df.melt('channel', var_name='institution',  value_name='dark count rate (Hz)')
    g = sns.relplot(x='channel', y='dark count rate (Hz)', hue='institution', data=df)
    g.tight_layout()
    g.fig.savefig(f'{out_dir}/dark_count_rate_lsu_pcb_lsu_utokyo_temp20.jpg')
