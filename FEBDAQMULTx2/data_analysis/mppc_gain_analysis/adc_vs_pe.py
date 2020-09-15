#!/usr/bin/env python

from scipy.signal import find_peaks
from matplotlib import markers
from operator import itemgetter
import argparse
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

def find_peak(df, feb_id, ch):

    # make the plot of a channel
    chvar = 'chg[{}]'.format(ch)
    # select data of the specified board
    df_1b = df[df['feb_num'] == feb_id]
    # make histogram and find peaks
    bins = np.linspace(0, 4100, 821)
    ax1 = plt.subplot(211)
    histy, bin_edges, _ = ax1.hist(df_1b[chvar], bins=bins, histtype='step')
    peaks, _ = find_peaks(histy, prominence=300)
    ax1.scatter(np.array(bin_edges)[peaks], np.array(histy)[peaks],
                   marker=markers.CARETDOWN, color='r', s=20)
    ax1.set_xlabel('ADC value')

    # make ADC difference vs PE number
    peak_adcs = list(np.array(bin_edges)[peaks])
    # peak_bins = [peaks[i] for i in range(len(peaks))]
    peak_diff = [peak_adcs[1] - peak_adcs[0]] + [peak_adcs[i+1]-peak_adcs[i] for i in range(len(peak_adcs)-1)]
    bins_adc_diff = np.linspace(0, len(peak_adcs)-1, len(peak_adcs)).astype(int)
    ax_adc_diff = plt.subplot(223)
    ax_adc_diff.step(bins_adc_diff, peak_diff, ls='-')
    ax_adc_diff.set_xticks(bins_adc_diff)
    ax_adc_diff.set_xlabel('PE id')
    ax_adc_diff.set_ylabel('adjacent ADC difference')
    

    # make the linear plot
    x_try = np.array(bins_adc_diff)
    y_try = np.array(peak_adcs)
    coeff = np.polyfit(x_try, y_try, 1)
    fitx = np.linspace(0, x_try[-1], 100)
    fity = coeff[0]*fitx + coeff[1]
    ax_fit_line = plt.subplot(224)
    ax_fit_line.plot(fitx, fity, '--g', alpha=.7)
    ax_fit_line.scatter(x_try, y_try, marker='o', color='r', s=20)
    ax_fit_line.set_xlim(left=-.5)
    ax_fit_line.set_ylim(bottom=0)
    ax_fit_line.set_xlabel('number of photons')
    ax_fit_line.set_ylabel('ADC value')
    # coeff = []
    # for i in range(2):
    #     x_try = np.linspace(1+i, len(peaks_no_ped)+i, len(peaks_no_ped))
    #     y_try = sorted(np.array(bin_edges)[peaks_no_ped])
    #     x_trys.append(x_try)
    #     y_trys.append(y_try)
    #     coeff.append(np.polyfit(x_try, y_try, 1))
    # # choose the one with smaller absolute intersection
    # intersecs = [np.abs(c[1]) for c in coeff]
    # correct_idx = min(enumerate(intersecs), key=itemgetter(1))[0]
    # x_try = x_trys[correct_idx]
    # y_try = y_trys[correct_idx]
    # fitx = np.linspace(0, x_try[-1], 100)
    # fity = coeff[correct_idx][0]*fitx + coeff[correct_idx][1]
    # axs[1].plot(fitx, fity, '--g', alpha=.7)
    # axs[1].scatter(x_try, y_try, marker='o', color='r', s=20)
    # axs[1].set_xlim(left=0)
    # axs[1].set_ylim(bottom=0)
    # axs[1].set_xlabel('number of photons')
    # axs[1].set_ylabel('ADC value')

    # # prepare for output
    # infn = os.path.basename(infpn)
    # outfdname = os.path.join(os.path.dirname(__file__), infn)
    # outfdname = os.path.join(os.path.splitext(outfdname)[0], 'single_channel')
    # if not os.path.exists(outfdname):
    #     os.makedirs(outfdname)

    # # save to file
    # outfig_pn = os.path.join(outfdname, 'bd{}ch{}.png'.format(feb_id, ch))
    # print('Saving output to {}'.format(outfig_pn))
    # ax1.set_title('board {} channel {}'.format(feb_id, ch))
    plt.tight_layout()
    plt.show()
    # plt.savefig(outfig_pn)

def process_one_channel(df, feb_num, ch_num):
    find_peak(df, feb_num, ch_num)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_file', type=str, default='../data/pandas/20200911_180348_mppc_volt58.0_temp20.0.h5')
    args = parser.parse_args()
    infpn = args.input_file
    df = pd.read_hdf(infpn, key='mppc')

    # get all different feb numbers
    feb_nums = list(df.feb_num.value_counts().keys())
    # get channel numbers
    ch_nums = [int(col[4:-1]) for col in df.columns if 'chg' in col]
    
    # deal with one channel
    # for feb_num in feb_nums:
    #     for ch_num in ch_nums:
    #         process_one_channel(df, feb_num, ch_num)
    process_one_channel(df, 0, 2)
