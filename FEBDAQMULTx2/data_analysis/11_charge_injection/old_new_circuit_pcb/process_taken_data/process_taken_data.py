#!/usr/bin/env python
'''
This script takes the measured root file where charge is injected to one channel.
Input data format is
<channel_number>.root
'''

from scipy.stats import norm

import argparse
import glob
import os
import pandas as pd
import uproot

class injection_data:
    def __init__(self, infpns, pulse_amp):
        self.infpns = infpns
        self.pulse_amp = pulse_amp
        self.single_ch_dfs = dict()
        # col_names = ['channel']+[f'ch{i}_mpv_adc' for i in range(32)]+\
        #             [f'ch{i}_gauss_adc' for i in range(32)]
        self.df_peak_adcs_mpv = pd.DataFrame(columns=['trigger_channel']+[f'ch{i}_peak_adc' for i in range(32)])
        self.df_peak_adcs_gauss = pd.DataFrame(columns=['trigger_channel']+[f'ch{i}_peak_adc' for i in range(32)])

        # final results: peak ADC and average pedestal ADC
        self.df_peak_and_ped_adcs_mpv = pd.DataFrame()
        self.df_peak_and_ped_adcs_gauss = pd.DataFrame()

        self.load_data_to_dfs()

        self.fill_peak_adcs()

        # calculate the final results: peak ADC and pedestal ADC
        self.get_peak_and_ped_adcs()
    
    def fill_peak_adcs(self):
        '''
        Fill peak ADC positions into the resulting dataframe.
        Two methods are used.
        The first one finds the peak ADC by the most probable value.
        The second fits a gaussian to the data and records the peak position.
        '''
        for ch, df in self.single_ch_dfs.items():
            rec_mpv = dict()
            rec_gauss = dict()
            rec_mpv['trigger_channel'] = rec_gauss['trigger_channel'] = ch
            for ch_2 in range(32):
                # calculate peak ADCs with the most probable value
                ser = df[f'chg[{ch_2}]']
                mpv = ser.mode()[0]
                rec_mpv[f'ch{ch_2}_peak_adc'] = mpv
                # calculate peak ADCs with a gaussian fit
                mean, _ = norm.fit(ser, loc=mpv)
                rec_gauss[f'ch{ch_2}_peak_adc'] = mean
            self.df_peak_adcs_mpv = self.df_peak_adcs_mpv.append(rec_mpv, ignore_index=True)
            self.df_peak_adcs_mpv['trigger_channel'] = self.df_peak_adcs_mpv.trigger_channel.astype('int64')
            self.df_peak_adcs_gauss = self.df_peak_adcs_gauss.append(rec_gauss, ignore_index=True)
            self.df_peak_adcs_gauss['trigger_channel'] = self.df_peak_adcs_gauss.trigger_channel.astype('int64')

    def load_data_to_dfs(self):
        '''
        It happens that some files are corrupted.
        Use a try except clause to bypass it.
        '''
        for infpn in self.infpns:
            try:
                self.single_ch_dfs[self.get_ch_from_infpn(infpn)] = uproot.open(infpn)['mppc'].arrays(library='pd')
            except:
                pass

    def get_ch_from_infpn(self, s):
        fstem = os.path.splitext(os.path.basename(s))[0]
        for substr in fstem.split('_'):
            if 'ch' in substr:
                return int(substr.lstrip('ch'))
        return int(os.path.splitext(os.path.basename(s))[0].lstrip('ch'))
    
    def get_peak_and_ped_adcs(self):
        '''
        After getting all peak ADCs for all channels,
        this function calculates the peak and pedestal ADCs.
        For a trigger channel, the peak ADC is the peak ADC of that channel.
        The pedestal ADC is the mean peak ADCs of all except the trigger channel. In other words, average along the column excluding the trigger channel row.

        A good reference:
        https://stackoverflow.com/questions/20829748/pandas-assigning-multiple-new-columns-simultaneously
        '''
        def peak_and_ped_adcs(df_in):
            rec = dict()
            df_out = pd.DataFrame()
            for ch in sorted(df_in.trigger_channel.unique()):
                rec['trigger_channel'] = ch
                rec['scope_amplitude'] = self.pulse_amp
                rec['peak_adc'] = df_in[df_in.trigger_channel == ch][f'ch{ch}_peak_adc'].iloc[0]
                rec['ped_adc'] = df_in[df_in.trigger_channel != ch][f'ch{ch}_peak_adc'].mean()
                # the circuit uses a 100 pF capacitor
                rec['conversion_factor'] = 100e-12*self.pulse_amp*1e-3*6.25e18/(rec['peak_adc']-rec['ped_adc'])
                rec['conversion_factor_from_charge'] = 5.942e-12*6.25e18/(rec['peak_adc']-rec['ped_adc'])
                df_out = df_out.append(rec, ignore_index=True)
            df_out['trigger_channel'] = df_out.trigger_channel.astype('int64')
            return df_out

        self.df_peak_and_ped_adcs_mpv = peak_and_ped_adcs(self.df_peak_adcs_mpv)
        self.df_peak_and_ped_adcs_mpv['method'] = 'mpv'
        self.df_peak_and_ped_adcs_gauss = peak_and_ped_adcs(self.df_peak_adcs_gauss)
        self.df_peak_and_ped_adcs_gauss['method'] = 'gauss'
    
    def save_results(self):
        out_dir = 'processed_data'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        path_prefixes = self.infpns[0].split('/')
        out_fn = ('conversion_factors' if len(path_prefixes) < 2 else path_prefixes[-2])+'.csv'
        out_fpn = os.path.join(out_dir, out_fn)

        # combine the two dataframes
        df_all = pd.concat([self.df_peak_and_ped_adcs_mpv, self.df_peak_and_ped_adcs_gauss])
        df_all.set_index(['trigger_channel', 'scope_amplitude', 'method'], inplace=True)
        # if output file exists, combine the dataframe already stored with df_all
        if os.path.exists(out_fpn):
            df_old = pd.read_csv(out_fpn, index_col=['trigger_channel', 'scope_amplitude', 'method'])
            df_all = df_all.combine_first(df_old)

        # save to file
        df_all.to_csv(out_fpn, index=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--scope_amplitude', help='Pulse amplitude observed on the scope in mV', type=float, default=28)
    parser.add_argument('-i', '--input_files', type=str, nargs='*', default=glob.glob('/cshare/vol2/users/shihkai/data/mppc/root/charge_injection_calib_data/20210625_new_pcb_without_t_feb428/*.root'))
    args = parser.parse_args()

    my_injection = injection_data(infpns=args.input_files, pulse_amp=args.scope_amplitude)
    # print(my_injection.df_peak_adcs_mpv)
    # print(my_injection.df_peak_adcs_gauss)
    print(my_injection.df_peak_and_ped_adcs_mpv)
    print(my_injection.df_peak_and_ped_adcs_gauss)
    my_injection.save_results()
