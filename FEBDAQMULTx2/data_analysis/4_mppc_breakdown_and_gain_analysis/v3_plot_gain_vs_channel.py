#!/usr/bin/env python
'''
Note: this script currently only works with analysis method of fitting the spectrum shape.
'''

from pandas.plotting import table

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../utilities'))

import argparse
import common_tools
import glob
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# redirect output to avoid x11 error
import matplotlib
matplotlib.use('Agg')

from v2_plot_breakdown_vs_channel import ChannelBreakdown

class ChannelGain(ChannelBreakdown):
    def __init__(self, in_db_name, meas_id):
        super().__init__(in_db_name, meas_id)

        # store the conversion factors for MPPC calibration if exist
        self.conversion_factors = self.get_conversion_factors(meas_id)

    def describe_helper(self, series):
        '''
        This function formats the summary statistics of a pandas series.
        '''
        # splits = str(series.describe()).split()[:-6]
        splits = str(series.describe()).split()
        splits = splits[:splits.index('Name:')]
        keys, values = "", ""
        for i in range(0, len(splits), 2):
            keys += "{:8}\n".format(splits[i])
            values += "{:>8}\n".format(splits[i+1])
        return keys, values

    def get_conversion_factors(self, meas_id):
        '''
        Retrieve conversion factors for all 64 channels if data exist.
        '''
        # feb SN should be contained in the measurement ID string
        feb_sns = [x for x in meas_id.split('_') if x.lower().startswith('feb')]
        if not feb_sns: return None

        # retrieve data from database
        proj_root = common_tools.get_git_root(os.getcwd())
        db_path = os.path.join(proj_root, 'FEBDAQMULTx2/data_analysis/11_charge_injection/old_new_circuit_pcb/process_taken_data/processed_data')
        res = []
        for feb_sn in feb_sns:
            db_fpns = glob.glob(os.path.join(db_path, f'*{feb_sn}*.csv'))
            if not db_fpns: continue
            # take the first database file
            db_fpn = db_fpns[0]
            df_cf = pd.read_csv(db_fpn)
            df_cf = df_cf[df_cf.method == 'mpv']
            res.extend(df_cf.conversion_factor_from_charge)
        return res

    def get_uncalibrated_gain_and_error(self, rec):
        '''
        This function returns the uncalibrated gain and error
        for a given channel and overvoltage.
        '''
        m = rec.total_gain_per_overvoltage
        dm = rec.total_gain_per_overvoltage_err
        v = rec.overvoltage
        dv = rec.breakdown_voltage_err
        g = m*v
        rec['uncalibrated gain (ADC/PE)'] = g
        dg = g*math.sqrt((dm/m)**2+(dv/v)**2)
        rec['uncalibrated gain error'] = dg
        return rec

    def plot_uncalibrated_gain_vs_channel_with_bias_voltage(self, bias_voltage=57, dac_corrected=True):
        # make sure DAC offset correction can be done
        if dac_corrected and len(self.feb_sns) == 0:
            print('No DAC correction can be done!')
            return

        df = self.df.copy()
        df['overvoltage'] = bias_voltage - (df.corrected_breakdown_voltage if dac_corrected else df.breakdown_voltage)
        df = df.apply(self.get_uncalibrated_gain_and_error, axis=1)
        print(df.columns)

        g = sns.JointGrid(data=df, x='ch_id', y='uncalibrated gain (ADC/PE)')
        g.ax_joint.errorbar(x=df['ch_id'], y=df['uncalibrated gain (ADC/PE)'], yerr=df['uncalibrated gain error'], fmt='o')
        g.ax_joint.grid(axis='both')
        g.ax_joint.set_xlabel('PCB channel number')
        g.ax_joint.set_title('Uncalibrated gain at {}V bias voltage\n{}'.format(bias_voltage, 'DAC offset corrected' if dac_corrected else 'No DAC offset correction'))
        g.plot_marginals(sns.histplot)
        g.ax_marg_y.grid(axis='y')
        g.ax_marg_x.remove()

        # save figure to file
        outfpn = 'plots/{}/{}uncalib_gain_vs_ch_biasvoltage_{}V.png'.format(self.meas_id, 'dac_corrected_' if dac_corrected else '', bias_voltage)
        # common_tools.easy_save_to(plt, outfpn)
        g.fig.set_figwidth(10)
        g.fig.set_figheight(5)
        g.fig.suptitle(f'Dataset: {self.meas_id}')
        plt.subplots_adjust(right=0.95)
        plt.figtext(.96, .54, self.describe_helper(df['uncalibrated gain (ADC/PE)'])[0], {'multialignment':'left'})
        plt.figtext(1.03, .54, self.describe_helper(df['uncalibrated gain (ADC/PE)'])[1], {'multialignment':'right'})
        '''
        Creating custom axis with JointGrid is hard.
        See https://stackoverflow.com/questions/35042255/how-to-plot-multiple-seaborn-jointplot-in-subplot
        # results = df['uncalibrated gain (ADC/PE)'].describe()
        # the_table = table(ax_table, np.round(results, 3), loc="upper right", colWidths=[0.5])
        # the_table.scale(1, 2)
        # the_table.auto_set_font_size(False)
        # the_table.set_fontsize(15)
        '''
        g.savefig(outfpn, bbox_inches='tight')
        print('Output figure to', outfpn)

    def plot_uncalibrated_gain_vs_channel_with_overvoltage(self, overvoltage=5):
        df = self.df.copy()
        df['overvoltage'] = overvoltage
        df = df.apply(self.get_uncalibrated_gain_and_error, axis=1).reset_index(drop=True)

        g = sns.JointGrid(data=df, x='ch_id', y='uncalibrated gain (ADC/PE)')
        g.ax_joint.errorbar(x=df['ch_id'], y=df['uncalibrated gain (ADC/PE)'], yerr=df['uncalibrated gain error'], fmt='o')
        g.ax_joint.grid(axis='both')
        g.ax_joint.set_xlabel('PCB channel number')
        g.ax_joint.set_title(f'Uncalibrated gain at {overvoltage}V overvoltage')
        g.plot_marginals(sns.histplot)
        g.ax_marg_y.grid(axis='y')
        g.ax_marg_x.remove()

        # set the figure title and show summary statistics
        g.fig.set_figwidth(10)
        g.fig.set_figheight(5)
        g.fig.suptitle(f'Dataset: {self.meas_id}')
        plt.subplots_adjust(right=0.95)
        plt.figtext(.96, .54, self.describe_helper(df['uncalibrated gain (ADC/PE)'])[0], {'multialignment':'left'})
        plt.figtext(1.03, .54, self.describe_helper(df['uncalibrated gain (ADC/PE)'])[1], {'multialignment':'right'})

        # save figure to file
        outfpn = f'plots/{self.meas_id}/uncalib_gain_vs_ch_overvoltage_{overvoltage}V.png'
        g.savefig(outfpn, bbox_inches='tight')
        print('Output figure to', outfpn)

        # do calibration and plot again
        if not self.conversion_factors: return
        df['calibrated gain'] = df['uncalibrated gain (ADC/PE)'] * pd.Series(self.conversion_factors)
        g = sns.JointGrid(data=df, x='ch_id', y='calibrated gain')
        g.ax_joint.errorbar(x=df['ch_id'], y=df['calibrated gain'], yerr=df['uncalibrated gain error']*pd.Series(self.conversion_factors), fmt='o')
        g.ax_joint.grid(axis='both')
        g.ax_joint.set_xlabel('PCB channel number')
        g.ax_joint.set_title(f'Calibrated gain at {overvoltage}V overvoltage')
        g.plot_marginals(sns.histplot)
        g.ax_marg_y.grid(axis='y')
        g.ax_marg_x.remove()

        # set the figure title and show summary statistics
        g.fig.set_figwidth(10)
        g.fig.set_figheight(5)
        g.fig.suptitle(f'Dataset: {self.meas_id}')
        plt.subplots_adjust(right=0.95)
        plt.figtext(.96, .54, self.describe_helper(df['calibrated gain'])[0], {'multialignment':'left'})
        plt.figtext(1.03, .54, self.describe_helper(df['calibrated gain'])[1], {'multialignment':'right'})

        # save figure to file
        outfpn = f'plots/{self.meas_id}/calib_gain_vs_ch_overvoltage_{overvoltage}V.png'
        g.savefig(outfpn, bbox_inches='tight')
        print('Output figure to', outfpn)
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--input_database', type=str, default='processed_data/breakdown_database_fit_spec_shape.csv')
    parser.add_argument('-m', '--measurement_id', type=str, default='20210112_lanl_bd1_64ch_thr220_temp20')
    parser.add_argument('-b', '--bias_voltage', type=float, default=57)
    parser.add_argument('-o', '--over_voltage', type=float, default=5)
    args = parser.parse_args()

    gain_and_ch = ChannelGain(args.input_database, args.measurement_id)
    gain_and_ch.plot_uncalibrated_gain_vs_channel_with_bias_voltage(bias_voltage=args.bias_voltage, dac_corrected=False)
    gain_and_ch.plot_uncalibrated_gain_vs_channel_with_bias_voltage(bias_voltage=args.bias_voltage)
    gain_and_ch.plot_uncalibrated_gain_vs_channel_with_overvoltage(overvoltage=args.over_voltage)
