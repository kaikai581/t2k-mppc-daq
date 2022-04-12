#!/usr/bin/env python

from glob import glob
from pathlib import Path
from scipy.stats import expon
from statistics import mean, stdev
from waveform_tools import ScopeWaveform
import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns
import sys
sys.dont_write_bytecode=True

class RateFromScope:
    def __init__(self, infpns, thresh=9e-3, polarity=+1, window_size=1):
        self.infpns = infpns
        self.thresh = thresh
        self.polarity = polarity
        self.interarrival_times = None
        self.window_size = window_size
        self.max_values = []

    def trigger_intervals_one_file(self, infpn):
        wf = ScopeWaveform(infpn)
        # find peaks with a threshold value
        wf.waveform_peaks(self.thresh, polarity=self.polarity, window_size=self.window_size)
        fig = wf.draw_waveform(window_size=self.window_size)
        # save the waveform
        fig.set_size_inches(12, 6)
        fig.axes[0].axhline(y=self.polarity*self.thresh, color = 'y', linestyle = '--')

        # prepare the folder for output
        out_dir = f'plots/{os.path.dirname(infpn)}'
        os.makedirs(out_dir, exist_ok=True)

        # save the figure
        plt.savefig(f'{out_dir}/{Path(infpn).stem}_thresh{self.thresh}_average{self.window_size}.png')
        plt.clf()
        # save max values
        self.max_values.append((self.polarity*wf.df.waveform_value).max())

        return wf.waveform_peak_time_diffs(self.thresh, polarity=self.polarity, window_size=self.window_size)
        
    def trigger_intervals_all_files(self):
        time_intervals = []
        for infpn in self.infpns:
            time_intervals.extend(self.trigger_intervals_one_file(infpn))
        df = pd.DataFrame()
        df['time intervals (s)'] = time_intervals
        plt.clf()
        g = sns.histplot(data=df, x='time intervals (s)')

        # prepare the folder for output
        out_dir = f'plots/{os.path.dirname(self.infpns[0])}'
        os.makedirs(out_dir, exist_ok=True)

        # save the figure
        g.figure.savefig(f'{out_dir}/t_interval_hist_thresh{self.thresh}_average{self.window_size}.png')
        print(max(self.max_values))
        return time_intervals
    
    def rate_and_error(self):
        if self.interarrival_times is None:
            self.interarrival_times = self.trigger_intervals_all_files()
        return 1./mean(self.interarrival_times)
    
    def rate_from_exp_fit(self):
        '''
        We know the interarrival time of a poisson process has an exponential distribution.
        Fit to it to get the rate!
        To fit to the exponential distribution form for interarrival time, refer to this link.
        https://stackoverflow.com/questions/25085200/scipy-stats-expon-fit-with-no-location-parameter
        '''
        if self.interarrival_times is None:
            self.interarrival_times = self.trigger_intervals_all_files()
        loc, scale = expon.fit(self.interarrival_times, floc=0)
        return 1/scale

if __name__ == '__main__':
    # the datasets have negative polarity since a preamp is used that outputs
    # inverted signal
    window_size = 200
    infpns_diff = glob('20220329_rate_waveform_57V_amp_diff_box_25C/*.csv')
    infpns_same = glob('20220329_rate_waveform_57V_amp_in_box_25C/*.csv')
    df = pd.DataFrame(columns=['threshold', 'same', 'separate'])
    rate_same = []
    rate_sep = []
    # By running the script in advance, the max value is like 16.
    # The max value I can go is 11. Above that, fit error.
    for i in range(11):
        diff = RateFromScope(infpns_diff, i*1e-3, polarity=-1, window_size=window_size)
        same = RateFromScope(infpns_same, i*1e-3, polarity=-1, window_size=window_size)
        rate_sep.append(diff.rate_from_exp_fit())
        rate_same.append(same.rate_from_exp_fit())

    df.same = rate_same
    df.separate = rate_sep
    df.threshold = list(range(11))
    os.makedirs('processed_data', exist_ok=True)
    df.to_csv(f'processed_data/20220329_average{window_size}.csv', index=False)
