#!/usr/bin/env python
'''
This script is the OOP version that finds the peak ADC position for a single channel.

The file names follow the convention such as:
"ch0.root" for charge injected to channel 0.
"ch0_ped.root" for pedestal ADC measurement for channel 0.
'''

import argparse
import os
from typing import OrderedDict
import pandas as pd
import statistics
import uproot

class peak_adc:
    def __init__(self, infpn):
        '''
        Load an input data and fill some properties.
        '''

        # store the path name
        self.infp = os.path.dirname(infpn)
        # store the file name
        self.infn = os.path.basename(infpn)
        # store the measurement type
        self.meas_type = None
        # store the injection channel
        self.inj_ch = None

        # open the file and store the tree to a dataframe
        tr_mppc = uproot.open(infpn)['mppc']
        self.df_mppc = tr_mppc.arrays(library='pd')
        
        # create an output dataframe
        self.peak_positions = OrderedDict()

        # initialize member variables
        # initialize meas_type
        self.fill_measurement_type()
        self.fill_injection_channel()
        self.fill_peak_positions()
    
    def fill_measurement_type(self):
        '''
        Two types: 'pedestal' or 'injection'
        '''
        file_atts = self.infn.rstrip('.root').split('_')
        if 'ped' in file_atts:
            self.meas_type = 'pedestal'
        else:
            self.meas_type = 'injection'
    
    def fill_injection_channel(self):
        '''
        Find the injection channel from the file name.
        '''
        file_atts = self.infn.rstrip('.root').split('_')
        for att in file_atts:
            if 'ch' in att:
                self.inj_ch = int(att.lstrip('ch'))
                return
        self.inj_ch = -1
    
    def fill_peak_positions(self):
        '''
        Fill peak positions for all channels.
        Note that charge injection measurement is conducted with only one FEB.
        '''
        for i in range(32):
            self.peak_positions[i] = int(self.df_mppc['chg[{}]'.format(i)].value_counts().idxmax())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_filenames', type=str, nargs='*')
    parser.add_argument('-sn', '--feb_serial_number', type=int, default='428')
    args = parser.parse_args()
    infpns = args.input_filenames

    # make two containers, for the injection and the pedestal measurement
    peak_adcs_ped = OrderedDict()
    peak_adcs_inj = OrderedDict()
    for infpn in infpns:
        my_peak_adc = peak_adc(infpn)

        if my_peak_adc.meas_type == 'injection':
            peak_adcs_inj[my_peak_adc.inj_ch] = my_peak_adc.peak_positions[my_peak_adc.inj_ch]
    
        # store the peak ADC of non-injection channels as the pedestal
        for ch in range(32):
            if ch != my_peak_adc.inj_ch:
                if not ch in peak_adcs_ped.keys():
                    peak_adcs_ped[ch] = []
                peak_adcs_ped[ch].append(my_peak_adc.peak_positions[ch])
    
    # replace the lists by the averages
    for ch in peak_adcs_ped.keys():
        peak_adcs_ped[ch] = statistics.mean(peak_adcs_ped[ch])
    
    # output a csv file with peak adc, ped adc, and calibration factor as columns
    df_calib = pd.DataFrame()
    df_calib['peak_adc'] = peak_adcs_inj.values()
    df_calib['ped_adc'] = peak_adcs_ped.values()
    df_calib['calib_factor'] = [21.7096875e-3*100e-12/1.6e-19/(peak_adcs_inj[ch]-peak_adcs_ped[ch]) for ch in peak_adcs_inj.keys()]
    
    # save results to file
    out_dir = 'processed_data'
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    df_calib.to_csv(os.path.join(out_dir, 'calib_factors_feb{}.csv'.format(args.feb_serial_number)), index=False)
        