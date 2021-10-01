#!/usr/bin/env python
'''
This script is to take one DT5702 root file and draw the MPPC luminosity.
'''

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../utilities'))

import argparse
import common_tools
# redirect output figures
import matplotlib
matplotlib.use('Agg')
import pandas as pd
import seaborn as sns
import uproot

class board_luminosity:
    def __init__(self, infpn):
        self.infpn = infpn

        # load raw data
        self.df_raw = self.load_raw_data()

        # data containers where keys are channel numbers
        self.ped_adcs = dict()
        self.tot_gains = dict()

        # final results container
        self.df_avgsigs = pd.DataFrame()

        # try to load results from file
        # if not exists, calculate it
        self.load_or_create_results()
        
    
    def get_calib_const(self):
        for feb_id in range(self.df_raw.mac5.nunique()):
            for ch_id in range(32):
                my_line = common_tools.MPPCLine(self.infpn, feb_id, ch_id, prom=100)
                self.ped_adcs[feb_id*32+ch_id] = my_line.gainfitp[1]
                self.tot_gains[feb_id*32+ch_id] = my_line.gainfitp[0]
    
    def get_mean_sig(self):
        df = self.df_avgsigs
        df['feb_id'] = [0]*32+[1]*32
        df['ch_id'] = [i for i in range(32)]*2
        df['channel'] = df.feb_id*32+df.ch_id
        
        # one value per channel
        mean_pe = []
        for feb_id in range(self.df_raw.mac5.nunique()):
            for ch in range(32):
                b_n_ch = feb_id*32+ch
                adcs = self.df_raw[self.df_raw.feb_id == feb_id][f'chg[{ch}]']
                mean_pe.append(((adcs-self.ped_adcs[b_n_ch])/self.tot_gains[b_n_ch]).mean())
        df['mean_pe'] = mean_pe
    
    def load_or_create_results(self):
        '''
        Check if the results are previously calculated and stored on disk.
        If not, calculate them.
        '''
        out_dir = 'processed_data'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        out_fn = os.path.splitext(os.path.basename(self.infpn))[0]+'.csv'
        out_fpn = os.path.join(out_dir, out_fn)

        # if not exists, calculate it
        if not os.path.exists(out_fpn):
            # get calibration parameters
            # fill self.ped_adcs and self.tot_gains
            self.get_calib_const()

            # for each channel, calculate the average signal size
            self.get_mean_sig()

            # save results to disk
            self.df_avgsigs.to_csv(out_fpn, index=False)
        else:
            self.df_avgsigs = pd.read_csv(out_fpn)

    def load_raw_data(self):
        df = uproot.open(self.infpn)['mppc'].arrays(library='pd')
        mac_dict = {mac: i for i, mac in enumerate(sorted(df.mac5.unique()))}
        df['feb_id'] = df.mac5.apply(lambda x: mac_dict[x])

        return df

    def plot_pcb_luminosity(self, swap_row_col=False):
        '''
        Make a heatmap of mean PE where values are arranged
        according to the physics channel map.

        A better way is hinted here:
        https://stackoverflow.com/questions/42092218/how-to-add-a-label-to-seaborn-heatmap-color-bar
        '''
        def map_to_2d(rec):
            col = int(rec.channel%8)
            row = int(7-rec.channel//8)
            if swap_row_col:
                col, row = row, col
            return row, col, rec.mean_pe

        data_2d = [[0]*8 for _ in range(8)]
        res = self.df_avgsigs.apply(map_to_2d, axis=1)
        for row, col, pe in res:
            data_2d[row][col] = pe
        
        ax = sns.heatmap(data_2d, cbar_kws={'label': 'mean PE'})

        out_dir = 'plots'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        out_fn = os.path.splitext(os.path.basename(self.infpn))[0]+'.png'
        out_fpn = os.path.join(out_dir, out_fn)

        ax.get_figure().savefig(out_fpn)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_filenames', nargs='*', type=str, default=['/cshare/vol2/users/shihkai/data/mppc/root/led/20210914_163354_64chpcb_thr210_gain56_temp21_trig0-63_feb12808_feb13294/20210914_165113_mppc_volt58.0_thr210_gain56_temp22.4.root'])
    parser.add_argument('--swap_row_col', action='store_true')
    args = parser.parse_args()

    for infpn in args.input_filenames:
        my_lumin = board_luminosity(infpn)
        my_lumin.plot_pcb_luminosity(args.swap_row_col)
    