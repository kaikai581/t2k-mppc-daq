#!/usr/bin/env python
'''
This script is to take one DT5702 root file and draw the MPPC luminosity.
'''

from collections import defaultdict
from numpy.typing import _256Bit
from scipy.optimize import curve_fit

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../utilities'))

import argparse
import common_tools
import copy
# redirect output figures
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
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

        # luminosity getting mapped to the PCB
        self.data_2d = [[0]*8 for _ in range(8)]

        # try to load results from file
        # if not exists, calculate it
        self.load_or_create_results()
    
    def find_beam_center(self):
        '''
        Fitting a 2D gaussian to find the beam center.
        Ref:
        https://scipython.com/blog/non-linear-least-squares-fitting-of-a-two-dimensional-data/
        '''
        # below is a full gaussian
        # def gauss2d(x, y, amp, x0, y0, a, b, c):
        #     inner = a * (x - x0)**2 
        #     inner += 2 * b * (x - x0)**2 * (y - y0)**2
        #     inner += c * (y - y0)**2
        #     return amp * np.exp(-inner)

        # code below does not work
        # xy = list(zip(*[(x, y) for x in range(8) for y in range(8)]))
        # popt, pcov = curve_fit(gauss2d, xy[0], xy[1], self.data_2d, p0=[4, 3, 3, 1, 0, 1])
        # print(popt)
        a = np.array(self.data_2d)
        # note that x and y are row and column reversed
        ym, xm = np.unravel_index(a.argmax(), a.shape)
        # print(np.unravel_index(a.argmax(), a.shape))

        def gauss2d(x, y, x0, y0, a, b, amp):
            inner = a * (x - x0)**2 
            inner += b * (y - y0)**2
            return amp * np.exp(-inner)
        
        # Our function to fit is going to be a sum of two-dimensional Gaussians
        def gaussian(x, y, x0, y0, xalpha, yalpha, A):
            return A * np.exp( -((x-x0)/xalpha)**2 -((y-y0)/yalpha)**2)
        
        xmin, xmax, nx = -.5, 7.5, 8
        ymin, ymax, ny = -.5, 7.5, 8
        x, y = np.linspace(xmin, xmax, nx), np.linspace(ymin, ymax, ny)
        X, Y = np.meshgrid(x, y)

        # This is the callable that is passed to curve_fit. M is a (2,N) array
        # where N is the total number of data points in Z, which will be ravelled
        # to one dimension.
        def _gaussian(M, *args):
            x, y = M
            arr = np.zeros(x.shape)
            for i in range(len(args)//5):
                arr += gaussian(x, y, *args[i*5:i*5+5])
            return arr

        # Initial guesses to the fit parameters.
        guess_prms = [(xm, ym, 1, 1, 4)]
        # Flatten the initial guess parameter list.
        p0 = [p for prms in guess_prms for p in prms]
        # We need to ravel the meshgrids of X, Y points to a pair of 1-D arrays.
        xdata = np.vstack((X.ravel(), Y.ravel()))
        # Do the fit, using our custom _gaussian function which understands our
        # flattened (ravelled) ordering of the data points.
        print('Initial parameters:\n', p0)
        popt, pcov = curve_fit(_gaussian, xdata, a.ravel(), p0)
        fit = np.zeros(a.shape)
        for i in range(len(popt)//5):
            fit += gaussian(X, Y, *popt[i*5:i*5+5])
        print('Fitted parameters:\n', popt)
        
        # Plot the test data as a 2D image and the fit as overlaid contours.
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.imshow(a, origin='lower', cmap='plasma',
                  extent=(x.min(), x.max(), y.min(), y.max()))
        ax.contour(X, Y, fit, colors='w')

        # deal with out-of-pcb cases
        xbest = max(popt[0], -0.5)
        ybest = popt[1]
        plt.plot(xbest, ybest, 's')

        out_dir = 'plots'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        out_fn = os.path.splitext(os.path.basename(self.infpn))[0]+'_contour_overlaid.png'
        out_fpn = os.path.join(out_dir, out_fn)
        plt.savefig(out_fpn)

        return round(xbest), round(ybest)
    
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
        
        # fill the PCB map
        def map_to_2d(rec):
            col = int(rec.channel%8)
            row = int(7-rec.channel//8)
            return row, col, rec.mean_pe

        res = self.df_avgsigs.apply(map_to_2d, axis=1)
        for row, col, pe in res:
            self.data_2d[row][col] = pe

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
        data_2d = [[0]*8 for _ in range(8)]
        if swap_row_col:
            for row in range(8):
                for col in range(8):
                    data_2d[row][col] = self.data_2d[col][row]
        self.data_2d = data_2d

        ax = sns.heatmap(self.data_2d, cbar_kws={'label': 'mean PE'})

        out_dir = 'plots'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        out_fn = os.path.splitext(os.path.basename(self.infpn))[0]+'.png'
        out_fpn = os.path.join(out_dir, out_fn)

        ax.get_figure().savefig(out_fpn)
    
    def plot_radial_luminosity(self):
        '''
        Plot the luminosity as a function of the radial distance to the beam center.
        '''
        x0, y0 = self.find_beam_center()
        radial_lys = defaultdict(list)
        for row in range(8):
            for col in range(8):
                radial_lys[(row-y0)**2+(col-x0)**2].append(self.data_2d[row][col])
        radial_ly = {np.sqrt(r): np.mean(ll) for r, ll in radial_lys.items()}
        
        plt.clf()
        plt.scatter(x=radial_ly.keys(), y=radial_ly.values())
        plt.xlabel('radial diatance')
        plt.ylabel('mean photoelectrons')
        plt.grid(axis='both')

        out_dir = 'plots'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        out_fn = os.path.splitext(os.path.basename(self.infpn))[0]+'_radial_luminosity.png'
        out_fpn = os.path.join(out_dir, out_fn)
        plt.savefig(out_fpn)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_filenames', nargs='*', type=str, default=['/cshare/vol2/users/shihkai/data/mppc/root/led/20210914_163354_64chpcb_thr210_gain56_temp21_trig0-63_feb12808_feb13294/20210914_165113_mppc_volt58.0_thr210_gain56_temp22.4.root'])
    parser.add_argument('--swap_row_col', action='store_true')
    args = parser.parse_args()

    for infpn in args.input_filenames:
        my_lumin = board_luminosity(infpn)
        my_lumin.plot_pcb_luminosity(args.swap_row_col)
        my_lumin.plot_radial_luminosity()
    