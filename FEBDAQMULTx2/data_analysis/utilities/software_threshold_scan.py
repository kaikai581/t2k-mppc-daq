#!/usr/bin/env python

# my own modeuls
import common_tools

from glob import glob
from scipy.interpolate import UnivariateSpline
from scipy.signal import argrelextrema, find_peaks
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import scipy.signal
import seaborn as sns
import sys
import uproot

class adc_scan:
    '''
    This class consumes an ADC spectrum, simulates the rate vs ADC threshold plot,
    and find the best correspondence between software simulation and real measurements.
    '''
    def __init__(self, dark_rate_fpns, led_calib_file, savgol_npts=11, prom=100, pc_lth=0.7, pc_rth=1.4, pcb_half=None):
        '''
        Constructor calculates dark rate as a function of threshold and loads a calibration LED spectrum.
        
        dark_rate_fpns: a list or a string with wildcards of the threshold scan files
        led_calib_file: a LED file with the same bias voltage and preamp gain for photoelectron calibration
        '''
        # query and store the uproot veresion
        self.uproot_ver = common_tools.get_uproot_version()
        if type(dark_rate_fpns) == str:
            self.dark_rate_fpns = glob(dark_rate_fpns)
        else:
            self.dark_rate_fpns = dark_rate_fpns
        
        # load data trees one by one
        x_dac = []
        y_rate = []
        for f in self.dark_rate_fpns:
            tr = uproot.open(f)['mppc']
            if self.uproot_ver == 3:
                df = tr.pandas.df()
            elif self.uproot_ver == 4:
                df = tr.arrays(library='pd')
            rate = len(df)/(df['ns_epoch'].max()-df['ns_epoch'].min())*1e9
            y_rate.append(rate)
            
            tr_metadata = uproot.open(f)['metadata']
            if self.uproot_ver == 3:
                df_metadata = tr_metadata.pandas.df()
            elif self.uproot_ver == 4:
                df_metadata = tr_metadata.arrays(library='pd')
            x_dac.append(df_metadata[df_metadata.isTrigger == True]['DAC'].iloc[0])
        
        ##
        # construct the rate scan dataframe
        # and find inflection points
        ##
        self.df_rate_scan = pd.DataFrame()
        self.df_rate_scan['rate'] = y_rate
        self.df_rate_scan['dac'] = x_dac
        self.df_rate_scan = self.df_rate_scan.sort_values(by='dac')
        self.df_rate_scan = self.df_rate_scan.reset_index(drop=True)
        self.df_rate_scan['diff_rate'] = -self.df_rate_scan['rate'].diff().bfill()
        self.df_rate_scan['log_rate'] = np.log10(self.df_rate_scan['rate'])
        self.df_rate_scan['diff_log_rate'] = -self.df_rate_scan['log_rate'].diff().bfill()
        # using Savitzky–Golay filter to smooth the curve of the first derivative
        # ref: https://stackoverflow.com/questions/56486999/savitzky-golay-filtering-giving-incorrect-derivative-in-1d
        # ref: https://riptutorial.com/scipy/example/15878/using-a-savitzky-golay-filter
        dx = self.df_rate_scan['dac'][1]-self.df_rate_scan['dac'][0]
        self.df_rate_scan['diff_log_rate_savgol'] = -scipy.signal.savgol_filter(self.df_rate_scan['log_rate'], savgol_npts, 3, deriv=1, delta=dx)
        self.df_rate_scan['log_rate_savgol'] = scipy.signal.savgol_filter(self.df_rate_scan['log_rate'], savgol_npts, 3, deriv=0, delta=dx)
        self.df_rate_scan['diff_log_rate_savgol_savgol'] = -scipy.signal.savgol_filter(self.df_rate_scan['log_rate_savgol'], savgol_npts, 3, deriv=1, delta=dx)
        # finding local minima
        # ref: https://stackoverflow.com/questions/48023982/pandas-finding-local-max-and-min
        minarg = scipy.signal.find_peaks(self.df_rate_scan['diff_log_rate_savgol_savgol'], height=self.df_rate_scan['diff_log_rate_savgol'].max()*.4)
        self.df_rate_scan['is_inflection'] = [True if i in minarg[0] else False for i in range(len(self.df_rate_scan))]

        # store board number
        self.feb_id = df_metadata[df_metadata.isTrigger == True]['board'].iloc[0]
        # store channel number
        self.ch = df_metadata[df_metadata.isTrigger == True]['channel'].iloc[0]

        # This is a design miss. Now I am hoping the board number for
        # the MPPCLine class can be identified by path name.
        for tmp_str in os.path.dirname(led_calib_file).split('_'):
            if 'feb' in tmp_str: bid_str = tmp_str.lstrip('feb')
        self.mppcline_bid = 1 if int(bid_str) == 170 else 0

        # construct the reference LED spectrum
        self.led_spec = common_tools.MPPCLine(led_calib_file, self.mppcline_bid, self.ch, prom=prom, pc_lth=pc_lth, pc_rth=pc_rth, pcb_half=pcb_half)

        # store the led filename
        self.led_fpn = led_calib_file

        # store output folder
        self.outdir = os.path.join('plots', os.path.dirname(self.dark_rate_fpns[0]).split('/')[-1])
    
    def dac_to_adc_and_pe(self, force_first_peak_number=None):
        '''
        Calculate the linear parameters for DAC to ADC conversion.
        Check whether the pe numbering algorithm is already applied.
        If not, spit a message to tell users to run it first and come back later.
        '''
        # check if pe numbering algorithm is run already
        pe_numbering_file = os.path.join(os.path.dirname(__file__), '../4_mppc_gain_analysis/processed_data/gain_database.csv')
        df_pe_numbering = pd.read_csv(pe_numbering_file)
        # get the first peak number
        df_temp = df_pe_numbering[(df_pe_numbering.filename == os.path.basename(self.led_fpn)) & (df_pe_numbering.board == self.mppcline_bid) & (df_pe_numbering.channel == self.ch)]
        if len(df_temp) == 0:
            print('PE information does not exist. Please run v2_breakdown_loop_*.py script first.')
            sys.exit(-1)
        if force_first_peak_number is None:
            first_peak_number = df_temp.iloc[0]['first_peak_number']
        else:
            first_peak_number = force_first_peak_number
        if first_peak_number < 0:
            print('Peak numbering algorithm is not run. Please run the algorithm before this.')
            sys.exit(-1)

        # build a list of increasing integers with equal interval 1 and of the same length as
        # the number of found inflection points.
        # The element of the new list has the first_peak_number value at the index at which the value in the inflection list is the first element larger than LED file's threshold.
        df = self.df_rate_scan[self.df_rate_scan.is_inflection]
        idx_first_peak = next(i for i, v in enumerate(df['dac']) if v > self.led_spec.threshold)
        pe_numbers = [i-(idx_first_peak-first_peak_number) for i in range(len(df))]
        m, b = np.polyfit(df['dac'], pe_numbers, 1)
        self.df_rate_scan['pe'] = self.df_rate_scan['dac']*m + b
        
        # make calibrated plot and save
        plt.scatter(self.df_rate_scan['pe'], self.df_rate_scan['log_rate'], s=4, label='raw')
        plt.plot(self.df_rate_scan['pe'], self.df_rate_scan['log_rate_savgol'], 'r--', label='Savitzky–Golay filtered')
        plt.grid(axis='both')
        plt.xlabel('photoelectron')
        plt.ylabel(r'$\log_{10}(rate/Hz)$')
        plt.legend()

        outfpn = os.path.join(self.outdir, 'calibrated_dark_rate_scan.png')
        common_tools.easy_save_to(plt, outfpn)

        # clear canvas
        plt.close()

    def plot_rate_and_diff_rate_vs_dac(self):
        '''
        Plot dark rate vs DAC and differentiated dark rate vs DAC sharing the same x axis.
        '''
        
        fig, ax = plt.subplots(nrows=2, ncols=1)
        ax[0].scatter(self.df_rate_scan['dac'], self.df_rate_scan['log_rate'], s=3, label='raw')
        ax[0].scatter(self.df_rate_scan['dac'], self.df_rate_scan['log_rate_savgol'], s=3, c='r', label='Savitzky–Golay filtered')
        ax[0].set_ylabel(r'$\log_{10}(rate/Hz)$')
        ax[0].legend()

        # using
        # ref: https://stackoverflow.com/questions/56486999/savitzky-golay-filtering-giving-incorrect-derivative-in-1d
        # ref: https://riptutorial.com/scipy/example/15878/using-a-savitzky-golay-filter
        ax[1].scatter(self.df_rate_scan['dac'], self.df_rate_scan['diff_log_rate_savgol'], s=3, label='raw')
        ax[1].scatter(self.df_rate_scan['dac'], self.df_rate_scan['diff_log_rate_savgol_savgol'], s=3, c='r', label='Savitzky–Golay filtered')
        ax[1].set_xlabel('DAC')
        ax[1].set_ylabel(r'$-\frac{d}{dx}\log_{10}(rate/Hz)$')
        ax[1].legend()

        # draw vertical line on all inflection points and all axes
        for axn in ax:
            for x_inflec in self.df_rate_scan[self.df_rate_scan.is_inflection]['dac']:
                axn.axvline(x=x_inflec, color='g', linestyle='--')

        # second derivative does not do any good
        # y_der2 = scipy.signal.savgol_filter(self.df_rate_scan['log_rate'], 11, 3, deriv=2, delta=dx)
        # ax[2].scatter(self.df_rate_scan['dac'], y_der2, s=3)
        # ax[2].set_ylabel(r'$d^2\log_{10}(rate/Hz)/dx^2$')

        # Using seaborn to make plots
        # sns.scatterplot(x='dac', y='rate', data=self.df_rate_scan, ax=ax[0], palette=['red'])
        # ax[0].set_yscale('log')
        # sns.scatterplot(x='dac', y='diff_log_rate', data=self.df_rate_scan, ax=ax[1], palette=['blue'])

        # spline does not work well.
        # spl = UnivariateSpline(self.df_rate_scan.dac, self.df_rate_scan.log_rate, k=4, s=0)
        # print(-spl.derivative()(self.df_rate_scan.dac))
        # plt.scatter(x=self.df_rate_scan.dac, y=-spl.derivative()(self.df_rate_scan.dac))

        fig.tight_layout()  # otherwise the right y-label is slightly clipped

        outfpn = os.path.join(self.outdir, os.path.basename(self.dark_rate_fpns[0]).strip('.root')+'.png')
        common_tools.easy_save_to(plt, outfpn)

        # clear canvas
        plt.close()