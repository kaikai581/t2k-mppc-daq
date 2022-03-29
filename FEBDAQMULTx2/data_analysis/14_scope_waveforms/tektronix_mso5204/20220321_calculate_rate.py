#!/usr/bin/env python

from glob import glob
from pathlib import Path
from statistics import mean, stdev
from waveform_tools import ScopeWaveform
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import sys
sys.dont_write_bytecode=True

class RateFromScope:
    def __init__(self, infpns, thresh=9e-3):
        self.infpns = infpns
        self.thresh = thresh

    def trigger_intervals_one_file(self, infpn):
        wf = ScopeWaveform(infpn)
        # find peaks with a threshold value
        wf.waveform_peaks(self.thresh)
        fig = wf.draw_waveform()
        # save the waveform
        fig.set_size_inches(12, 6)
        fig.axes[0].axhline(y=self.thresh, color = 'y', linestyle = '--')
        plt.savefig(f'plots/{Path(infpn).stem}_thresh{self.thresh}.png')
        return wf.waveform_peak_time_diffs(self.thresh)
        
    def trigger_intervals_all_files(self):
        time_intervals = []
        for infpn in self.infpns:
            time_intervals.extend(self.trigger_intervals_one_file(infpn))
        df = pd.DataFrame()
        df['time intervals (s)'] = time_intervals
        df.to_csv('processed_data/interarrival_times.csv', index=False)
        plt.clf()
        g = sns.histplot(data=df, x='time intervals (s)')
        g.figure.savefig(f'plots/t_interval_hist_thresh{self.thresh}.png')
        return time_intervals
    
    def rate_and_error(self):
        time_intervals = self.trigger_intervals_all_files()
        return 1./mean(time_intervals)

if __name__ == '__main__':
    infpns = glob('20220321_data_58V/*.csv')
    my_rate = RateFromScope(infpns, 9e-3)
    print(my_rate.rate_and_error())