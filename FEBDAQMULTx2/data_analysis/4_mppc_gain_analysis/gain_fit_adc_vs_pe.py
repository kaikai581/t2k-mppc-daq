#!/usr/bin/env python

from scipy import stats
from scipy.signal import find_peaks
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.neighbors import KernelDensity
from matplotlib import markers
from operator import itemgetter
from peak_cleanup import PeakCleanup
import argparse
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import seaborn as sns
import statistics

def find_gain(df, feb_id, ch, print_peak_adcs, prominence=300, left_threshold=0.7, right_threshold=1.4):

    # make the plot of a channel
    chvar = 'chg[{}]'.format(ch)
    # select data of the specified board
    df_1b = df[df['feb_num'] == feb_id]
    # make histogram and find peaks
    bins = np.linspace(0, 4100, 821)
    plt.figure(figsize=(12,6))
    ax1 = plt.subplot2grid((2, 3), (0, 0), colspan=2)
    histy, bin_edges, _ = ax1.hist(df_1b[chvar], bins=bins, histtype='step')
    peaks, _ = find_peaks(histy, prominence=prominence)
    ax1.scatter(np.array(bin_edges)[peaks], np.array(histy)[peaks],
                   marker=markers.CARETDOWN, color='r', s=20)
    ax1.set_xlabel('ADC value')

    # load the found peaks into a list
    peak_adcs = list(np.array(bin_edges)[peaks])
    if print_peak_adcs: print(peak_adcs)

    # make the ADC difference vs PE id plot
    if len(peak_adcs) >= 2:
        peak_diff = [peak_adcs[1] - peak_adcs[0]] + [peak_adcs[i+1]-peak_adcs[i] for i in range(len(peak_adcs)-1)]
    else:
        return 0
    bins_adc_diff = np.linspace(0, len(peak_adcs)-1, len(peak_adcs)).astype(int)
    ax_adc_diff = plt.subplot2grid((2, 3), (0, 2))
    ax_adc_diff.step(bins_adc_diff, peak_diff, ls='-')
    ax_adc_diff.set_xticks(bins_adc_diff)
    ax_adc_diff.set_xlabel('PE id')
    ax_adc_diff.set_ylabel('adjacent ADC difference')
    # plot mean and standard deviation of all the differences
    y_mean = statistics.mean(peak_diff)
    y_std = statistics.stdev(peak_diff)
    n_std = 3
    y_shifts = [y_mean + y_std*i for i in range(-n_std, n_std+1)]
    color_std = ['y', 'magenta', 'g', 'r', 'g', 'magenta', 'y']
    for i in range(2*n_std+1):
        ax_adc_diff.axhline(y_shifts[i], ls='--', c=color_std[i], alpha=.25)
    
    # # make kernel density plots
    # ref: https://stackoverflow.com/questions/9814429/gaussian-kernel-density-estimation-kde-of-large-numbers-in-python
    # # each bin is 5 ADC, so the bandwidth is multiple of 5
    # if y_std > 0:
    #     x_kde = np.linspace(min(peak_diff)*.8, max(peak_diff)*1.2, 101)
    #     density = stats.gaussian_kde(peak_diff, bw_method=5/y_std)
    #     y_kde = density(x_kde)
    #     ax_kde = plt.subplot2grid((2, 3), (1, 0))
    #     ax_kde.plot(x_kde, y_kde)
    #     ax_kde.set_xlabel('adjacent ADC difference')
    #     ax_kde.set_title('kernel density estimation')
    ax_kde = plt.subplot2grid((2, 3), (1, 0))
    pc = PeakCleanup(peak_adcs)
    pc.plot_to_axis(ax_kde, np.array(pc.peak_diffs), thresh=5)
    ax_kde.set_title('before outlier removal')

    # remove outliers
    peak_adcs_orig = peak_adcs.copy()
    peak_cleaner = PeakCleanup(peak_adcs)
    # peak_cleaner.remove_outlier_twice()
    peak_cleaner.remove_outlier_by_relative_interval(left_th=left_threshold, right_th=right_threshold)
    peak_adcs = peak_cleaner.peak_adcs
    # peak_diff2 = [peak_adcs[i+1]-peak_adcs[i] for i in range(len(peak_adcs)-1)]
    # make kernel density plots after outlier removal
    ax_kde2 = plt.subplot2grid((2, 3), (1, 1))
    peak_cleaner.plot_to_axis(ax_kde2, np.array(peak_cleaner.peak_diffs), thresh=5)
    ax_kde2.set_title('after outlier removal')

    # make the linear plot
    bins_adc_diff = np.linspace(0, len(peak_adcs)-1, len(peak_adcs)).astype(int)
    x_try = np.array(bins_adc_diff)
    y_try = np.array(peak_adcs)
    coeff = np.polyfit(x_try, y_try, 1)
    fitx = np.linspace(0, x_try[-1], 100)
    fity = coeff[0]*fitx + coeff[1]
    ax_fit_line = plt.subplot2grid((2, 3), (1, 2))
    ax_fit_line.plot(fitx, fity, '--g', alpha=.7)
    # plot the original peaks without cleanup
    if peak_adcs_orig != peak_adcs:
        ax_fit_line.scatter(list(range(len(peak_adcs_orig))), np.array(peak_adcs_orig), marker='o', color='r', s=20, facecolors='none', label='no peak cleanup')
        # plot the cleaned peaks
        ax_fit_line.scatter(x_try, y_try, marker='o', color='r', s=20, label='peak cleanup')
        ax_fit_line.legend()
    else:
        ax_fit_line.scatter(x_try, y_try, marker='o', color='r', s=20)
    ax_fit_line.set_xlim(left=-.5, right=len(peak_adcs_orig)-.5)
    ax_fit_line.set_ylim(bottom=0, top=max(peak_adcs_orig)*1.05)
    ax_fit_line.set_xlabel('PE id')
    ax_fit_line.set_ylabel('ADC value')

    # investigate sklearn's regression model
    lin_model = LinearRegression()
    lin_model.fit(x_try.reshape(-1,1), y_try)
    r2_gof = r2_score(y_try, lin_model.predict(x_try.reshape(-1,1)))
    print('r2_score', r2_gof)

    # prepare for output
    infn = os.path.basename(infpn)
    outfdname = os.path.join(os.path.dirname(__file__), infn)
    outfdname = os.path.join('plots', os.path.splitext(outfdname)[0]+'_prom{}_lth{}_rth{}'.format(prominence, left_threshold, right_threshold), 'single_channel')
    if not os.path.exists(outfdname):
        os.makedirs(outfdname)

    # save to file
    outfig_pn = os.path.join(outfdname, 'bd{}ch{}.png'.format(feb_id, ch))
    print('Saving output to {}'.format(outfig_pn))
    ax1.set_title('board {} channel {}'.format(feb_id, ch))
    plt.tight_layout()
    # plt.show()
    plt.savefig(outfig_pn)
    plt.close()

    # save to database
    save_gain_database(infpn, feb_id, ch, prominence, left_threshold, right_threshold, coeff, r2_gof)

    # return the slope (gain)
    return coeff[0], r2_gof

def processed_data_directory():
    out_dir = os.path.join(os.path.dirname(__file__), 'processed_data')
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    return out_dir

def process_all_channels(infpn, print_peak_adcs, prominence, left_threshold, right_threshold):
    df = pd.read_hdf(infpn, key='mppc')
    # get all different feb numbers
    feb_nums = list(df.feb_num.value_counts().keys())
    # get channel numbers
    ch_nums = [int(col[4:-1]) for col in df.columns if 'chg' in col]
    
    # get bias voltage from file name
    for tmpstr in infpn.split('_'):
        if 'volt' in tmpstr:
            bias_volt = tmpstr.lstrip('volt')
    file_date = infpn.split('_')[0].split('/')[-1]

    # create the output folder to store calculated values
    out_dir = processed_data_directory()

    # results container
    outfpn = os.path.join(out_dir, '{}_total_gain_peak_cleanup.txt'.format(file_date))
    if os.path.exists(outfpn):
        with open(outfpn) as json_file:
            gain = json.load(json_file)
    else:
        gain = dict()
    gain[bias_volt] = dict()
    
    # deal with one channel
    for feb_num in feb_nums:
        for ch_num in ch_nums:
            ch_name = 'b{}_ch{}'.format(feb_num, ch_num)
            gain[bias_volt][ch_name] = find_gain(df, feb_num, ch_num, print_peak_adcs, prominence, left_threshold, right_threshold)
    with open(outfpn, 'w') as outfile:
        json.dump(gain, outfile)
    # find_gain(df, 0, 5, print_peak_adcs)
    # find_gain(df, 0, 6, print_peak_adcs)
    # find_gain(df, 0, 7, print_peak_adcs)

def save_gain_database(infpn, feb_id, ch, prominence, left_th, right_th, coeff, r2_gof):
    # determine the output file pathname
    out_dir = processed_data_directory()
    outfn = 'gain_database.csv'
    outfpn = os.path.join(out_dir, outfn)
    
    # if file exists, read it into a dataframe;
    # otherwise create a new dataframe
    columns = ['filename','board','channel','prominence','left_threshold','right_threshold','gain','r2']
    if os.path.exists(outfpn):
        df = pd.read_csv(outfpn)
    else:
        df = pd.DataFrame(columns=columns)
    df = df.set_index(columns[:6])
    
    # construct the data dictionary
    new_data = dict()
    new_data['filename'] = os.path.basename(infpn)
    new_data['board'] = feb_id
    new_data['channel'] = ch
    new_data['prominence'] = prominence
    new_data['left_threshold'] = left_th
    new_data['right_threshold'] = right_th
    new_data['gain'] = coeff[0]
    new_data['r2'] = r2_gof

    # make a new dataframe out of the new data record
    df_new = pd.DataFrame(columns=columns)
    df_new = df_new.append(new_data, ignore_index=True)
    df_new = df_new.set_index(columns[:6])
    print(df_new)

    # append new data if not exist
    # otherwise overwrite
    df = df.combine_first(df_new)

    # Write to file
    df.to_csv(outfpn, mode='w')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_files', type=str, default='../data/pandas/20200911_180348_mppc_volt58.0_temp20.0.h5', nargs='*')
    parser.add_argument('-l', '--left_threshold', type=float, default=0.7)
    parser.add_argument('-r', '--right_threshold', type=float, default=1.4)
    parser.add_argument('-p', '--prominence', type=float, default=250)
    parser.add_argument('--print_peak_adcs', action='store_true')
    args = parser.parse_args()
    global infpn
    infpn = args.input_files
    global prominence
    prominence = args.prominence
    print_peak_adcs = args.print_peak_adcs

    # process all channels of data
    for fpn in args.input_files:
        infpn = fpn
        process_all_channels(infpn, print_peak_adcs, prominence, args.left_threshold, args.right_threshold)
