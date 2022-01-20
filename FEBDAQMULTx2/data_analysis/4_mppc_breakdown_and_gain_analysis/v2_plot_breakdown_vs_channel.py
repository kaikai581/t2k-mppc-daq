#!/usr/bin/env python

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../utilities'))
from data_summary import OnePCBSummary

import argparse
import common_tools
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# redirect output to avoid x11 error
import matplotlib
matplotlib.use('Agg')

class ChannelBreakdown:
    def __init__(self, in_db_name, meas_id):
        # load_dataframe
        self.in_db_name = in_db_name
        self.meas_id = meas_id
        # determine FEB serial numbers involved in the measurement
        # from the measurement ID
        self.feb_sns = self.get_feb_sns()

        self.df = self.load_data()
    
    def get_dac_offset(self):
        if len(self.feb_sns) == 1:
            df = pd.read_csv(f'processed_data/dac_offset_feb{self.feb_sns[0]}.csv')
            return list(df['DAC offset (V)'])*2
        df1 = pd.read_csv(f'processed_data/dac_offset_feb{self.feb_sns[0]}.csv')
        df2 = pd.read_csv(f'processed_data/dac_offset_feb{self.feb_sns[1]}.csv')
        return list(df1['DAC offset (V)'])+list(df2['DAC offset (V)'])

    def get_feb_sns(self):
        feb_sns = []
        for substr in self.meas_id.split('_'):
            substr = str.lower(substr)
            if 'feb' in str.lower(substr):
                feb_sns.append(substr.replace('feb', ''))
        return feb_sns

    def load_data(self):
        # load dataframe
        df = pd.read_csv(self.in_db_name)
        df = df[df.measurement_id == self.meas_id]
        df['ch_id'] = df.board * 32 + df.channel
        df['ch_label'] = df.apply(lambda x: 'b{}c{}'.format(x['board'], x['channel']), axis=1)
        if len(self.feb_sns) > 0:
            df['dac_offset'] = self.get_dac_offset()
            df['corrected_breakdown_voltage'] = df['breakdown_voltage']+df['dac_offset']
        return df
    
    def plot_breakdown_vs_channel(self, dac_corrected=True):
        # check if DAC correction exists
        if len(self.feb_sns) == 0:
            dac_corrected = False
        # use seaborn to make plot
        fig, (ax, axhist) = plt.subplots(ncols=2, sharey=True,
                                        gridspec_kw={"width_ratios" : [3,1], "wspace" : 0})
        fig.set_size_inches(10, 5)
        if dac_corrected:
            y_name = 'corrected_breakdown_voltage'
        else:
            y_name = 'breakdown_voltage'
        ax.errorbar(x=self.df['ch_id'], y=self.df[y_name], yerr=self.df['breakdown_voltage_err'], fmt='o')
        ax.grid(True)
        y_prefix = 'DAC offset corrected ' if dac_corrected else ''
        ax.set_ylabel(y_prefix + 'breakdown voltage (V)')
        ax.set_xlabel('PCB channel number')

        axhist.hist(self.df[y_name], bins='auto', orientation='horizontal', histtype='step')
        axhist.tick_params(axis="y", left=False)
        axhist.grid(axis='y')

        # save figure to file
        outfpn = 'plots/{}/{}vbd_vs_ch.png'.format(meas_id, 'dac_corrected_' if dac_corrected else '')
        common_tools.easy_save_to(plt, outfpn)
        print('Output figure to', outfpn)
    
    def plot_breakdown_vs_channel_common_style(self, dac_corrected=True):
        '''
        Use the class defined in utility to make plots in common style.
        '''
        my_style = OnePCBSummary(self.df)

        # set up parameters for plotting
        x = 'ch_id'
        y = 'corrected_breakdown_voltage' if dac_corrected else 'breakdown_voltage'
        joint_title = 'breakdown voltage {} DAC offset correction'.format('with' if dac_corrected else 'without')
        y_title = 'breakdown voltage (V)'
        y_error = 'breakdown_voltage_err'
        figure_title = f'Dataset: {self.meas_id}'
        outfpn = 'plots/{}/{}vbd_vs_ch_common_style.png'.format(meas_id, 'dac_corrected_' if dac_corrected else '')

        # plot!
        my_style.make_summary_plot(x=x, y=y, joint_title=joint_title, figure_title=figure_title, y_title=y_title, y_error=y_error, outfpn=outfpn)
        print('Output figure to', outfpn)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--input_database', type=str, default='processed_data/breakdown_database.csv')
    parser.add_argument('-m', '--measurement_id', type=str, default='20210112_lanl_bd1_64ch_thr220_temp20')
    args = parser.parse_args()
    in_db_name = args.input_database
    meas_id = args.measurement_id

    bd_and_ch = ChannelBreakdown(in_db_name, meas_id)
    bd_and_ch.plot_breakdown_vs_channel_common_style(dac_corrected=False)
    bd_and_ch.plot_breakdown_vs_channel_common_style()
