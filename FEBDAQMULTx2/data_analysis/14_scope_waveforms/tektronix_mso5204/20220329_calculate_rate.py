#!/usr/bin/env python

from glob import glob
from pathlib import Path
from statistics import mean, stdev
from waveform_tools import ScopeWaveform
import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns
import sys
sys.dont_write_bytecode=True

class RateFromScope:
    def __init__(self, infpns, thresh=9e-3, polarity=+1):
        self.infpns = infpns
        self.thresh = thresh
        self.polarity = polarity
        self.interarrival_times = None

    def trigger_intervals_one_file(self, infpn):
        wf = ScopeWaveform(infpn)
        # find peaks with a threshold value
        wf.waveform_peaks(self.thresh, polarity=self.polarity)
        fig = wf.draw_waveform()
        # save the waveform
        fig.set_size_inches(12, 6)
        fig.axes[0].axhline(y=self.polarity*self.thresh, color = 'y', linestyle = '--')

        # prepare the folder for output
        out_dir = f'plots/{os.path.dirname(infpn)}'
        os.makedirs(out_dir, exist_ok=True)

        # save the figure
        plt.savefig(f'{out_dir}/{Path(infpn).stem}_thresh{self.thresh}.png')
        return wf.waveform_peak_time_diffs(self.thresh, polarity=self.polarity)
        
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
        g.figure.savefig(f'{out_dir}/t_interval_hist_thresh{self.thresh}.png')
        return time_intervals
    
    def rate_and_error(self):
        if self.interarrival_times is None:
            self.interarrival_times = self.trigger_intervals_all_files()
        return 1./mean(self.interarrival_times)

if __name__ == '__main__':
    # the datasets have negative polarity since a preamp is used that outputs
    # inverted signal
    infpns_diff = glob('20220329_rate_waveform_57V_amp_diff_box_25C/*.csv')
    infpns_same = glob('20220329_rate_waveform_57V_amp_in_box_25C/*.csv')
    rate_diff = RateFromScope(infpns_diff, 8e-3, polarity=-1)
    rate_same = RateFromScope(infpns_same, 8e-3, polarity=-1)
    print(rate_diff.rate_and_error())
    print(rate_same.rate_and_error())
