#!/usr/bin/env python

# my own modules
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../utilities'))
import autocorrelation_gain

from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import numpy as np

class explain_autocorrelation(autocorrelation_gain.MPPCLine):
    def __init__(self, infpn, nbins=4100):
        super().__init__(infpn)

        self.nbins = nbins
        self.ch_bins = dict()
        self.ch_adc_spec = dict()
        self.ch_bin_edges = dict()
        self.ch_autocorr = dict()
        self.ch_autocorr_peak_pos = dict()
        self.ch_gain = dict()
        self.ch_gain_err = dict()
    
    def make_histogram(self, ch=0):
        # select data
        feb_id = self.get_feb_id(ch)
        df = self.df_mppc[self.df_mppc.feb_id == feb_id]
        chvar = 'chg[{}]'.format(ch%32)
        # make histogram and find peaks
        self.ch_bins[ch] = np.linspace(0, 4100, self.nbins+1)
        self.ch_adc_spec[ch], self.ch_bin_edges[ch] = np.histogram(df[chvar], bins=self.ch_bins[ch])

        # remove trailing zeroes
        while self.ch_adc_spec[ch][-1] == 0.:
            self.ch_adc_spec[ch] = self.ch_adc_spec[ch][:-1]
            self.ch_bin_edges[ch] = self.ch_bin_edges[ch][:-1]

    def plot_displacement(self, ch=0, outpn=None, prom_frac=.001):
        '''
        Plot displacement and mark the displacement on the autocorrelation plot.
        '''
        if not ch in self.ch_adc_spec:
            self.make_histogram(ch)
        histy = self.ch_adc_spec[ch]
        bins = self.ch_bins[ch]

        # do the autocorrelation
        if not ch in self.ch_autocorr:
            result = np.correlate(histy, histy, mode='full')
            self.ch_autocorr[ch] = result[result.size//2:]

        # find autocorrelation peak adcs
        corr_size = self.ch_autocorr[ch]
        dbin = bins[1]-bins[0]
        disp_list, _ = peak_bins, _ = find_peaks(corr_size, prominence=np.max(corr_size)*prom_frac)
        self.ch_autocorr_peak_pos[ch] = peak_bins = np.insert(peak_bins*dbin, 0, 0)
        peak_dists = [peak_bins[i+1]-peak_bins[i] for i in range(peak_bins.size-1)]
        gain_err = np.std(peak_dists) if len(peak_dists) else -1
        self.ch_gain[ch] = peak_dists[0] if len(peak_dists) else -1
        self.ch_gain_err[ch] = gain_err

        # prepare output folder
        if outpn is None:
            out_dir = os.path.join('plots', os.path.basename(os.path.splitext(__file__)[0]))
        else:
            out_dir = os.path.join(outpn, f'b{self.get_feb_id(ch)}c{ch%32}')
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        
        # construct the displacement list
        disp_list = [0] + list(disp_list)
        disp_list = disp_list + [(disp_list[i+1]+disp_list[i])//2 for i in range(len(disp_list)-1)]

        # make the figure
        for displacement in disp_list:
            fig, axs = plt.subplots(nrows=2, constrained_layout=True)
            fig.suptitle(self.get_parameter_string(ch), fontsize=9)
            shifted_y, shifted_bin_edges = self.shift_adc_spec(histy, self.ch_bin_edges[ch], displacement)
            axs[0].bar(self.ch_bin_edges[ch][:-1], histy, align='edge', width=bins[1]-bins[0], ec='None', color='b', alpha=.5)
            axs[0].bar(shifted_bin_edges[:-1], shifted_y, align='edge', width=bins[1]-bins[0], ec='None', color='r', alpha=.5)
            axs[0].set_xlabel('ADC')
            axs[0].set_ylabel('counts')
            axs[0].annotate(r'autocorrelation$_{{{}}}=\sum_{{i=0}}^{{\infty}}A_iA_{{i-{}}}={:.2e}$'.format(displacement, displacement, corr_size[displacement]), xy=(0.45, 0.55), xycoords='axes fraction')

            npts = len(corr_size)
            axs[1].scatter(x=np.arange(0, npts, 1), y=corr_size, s=7, c='r')
            axs[1].set_xlabel('ADC shift')
            axs[1].set_ylabel('autocorrelation')
            axs[1].annotate(r'total gain={:.2f}$\pm${:.2f} ADC/PE'.format(self.ch_gain[ch], gain_err), xy=(0.52, 0.4), xycoords='axes fraction')

            # mark the target
            axs[1].scatter(x=displacement, y=corr_size[displacement], s=8, c='k', ec='k')

            fig.savefig(os.path.join(out_dir, f'b{self.get_feb_id()}c{ch%32}_autocorr_disp_{displacement}.png'))
            plt.close()
    
    def shift_adc_spec(self, hist, bins, displacement):
        shist = list(hist)
        sbins = list(bins)
        dbins = bins[1]-bins[0]
        for i in range(displacement):
            shist = [0] + shist
            sbins = [sbins[0]-dbins] + sbins
            sbins = [b+dbins for b in sbins]
        return shist, sbins

if __name__ == '__main__':
    my_autocorrelation = explain_autocorrelation('../data/root/led/20210517_170336_utokyo_ch0-63_thr220_gain55_temp25_trig0-63_feb136_feb13294/20210517_171043_mppc_volt57.8_thr220_gain55_temp25.1.root')
    my_autocorrelation.plot_displacement(ch=32)