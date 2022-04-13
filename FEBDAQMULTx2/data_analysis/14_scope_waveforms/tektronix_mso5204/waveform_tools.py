from curses import window
from pathlib import Path
from scipy.fftpack import fft, ifft
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import seaborn as sns

class ScopeWaveform:
    def __init__(self, infpn, remove_dc=True):
        columns = ['info_name', 'value', 'units', 'time', 'waveform_value']
        self.infpn = infpn
        self.df = pd.read_csv(infpn, names=columns, dtype={'info_name': 'str', 'units': 'str'})
        if remove_dc:
            self.df.waveform_value = self.df.waveform_value - self.df.waveform_value.median()
        self.threshold = None

        # add a partial sum column
        self.waveform_partial_integral()
    
    def add_moving_average(self, window_size=100):
        self.df[f'waveform_value_moving_average_{window_size}'] = self.df['waveform_value'].rolling(window_size).mean()

    def draw_waveform(self, window_size=None):
        if window_size is None or window_size == 0:
            yname = 'waveform_value'
        else:
            yname = f'waveform_value_moving_average_{window_size}'
            if not yname in self.df.columns:
                self.add_moving_average(window_size=window_size)
        fig, ax = plt.subplots()
        print(self.infpn, yname)
        sns.lineplot(data=self.df, x='time', y=yname, ax=ax)
        # Peak finding algorithm has to be rerun for each different window size since data points shift!!!
        cname = 'is_peak' if window_size is None else f'is_peak_{window_size}'
        if cname in self.df.columns:
            sns.scatterplot(data=self.df[self.df[cname] == True], x='time', y=yname, ax=ax, color='r')
        # if the threshold is not None, draw it as well
        if not self.threshold is None:
            plt.axhline(y=self.threshold, color='y', linestyle='--')

        # save to file
        out_dir = f'plots/{os.path.dirname(self.infpn)}'
        os.makedirs(out_dir, exist_ok=True)
        outfn = f'{Path(self.infpn).stem}_thresh{self.threshold}_window{window_size}.png'
        fig.savefig(os.path.join(out_dir, outfn))

        return fig

    def peaks_freqiencies(self, amp, xs):
        '''
        Apply peak finding algorithms to identify peak values.
        '''
        peaks, props = find_peaks(amp, height=0.075)
        return [(xs[i], amp[i]) for i in peaks]

    def waveform_partial_integral(self):
        '''
        Partial sum of the waveform to study the pulse area.
        '''
        self.df['partial_integral'] = self.df.waveform_value.cumsum()
    
    def waveform_fft(self):
        '''
        Ref: https://pythonnumericalmethods.berkeley.edu/notebooks/chapter24.04-FFT-in-Python.html
        '''
        X = fft(self.df.waveform_value.values)
        N = len(X)
        n = np.arange(N)
        # get the sampling rate
        sr = 1 / 2e-10
        T = N/sr
        freq = n/T

        # Get the one-sided specturm
        n_oneside = N//2
        # get the one side frequency
        f_oneside = freq[:n_oneside]

        # find the peaks in the frequency spectrum
        peak_coords = self.peaks_freqiencies(np.abs(X[:n_oneside]), f_oneside)

        # first, plot the original signal
        _, (ax1, ax2) = plt.subplots(2, figsize=(12,12))
        ax1.plot(self.df.time, self.df.waveform_value)
        ax1.set_xlabel('time (s)')
        ax1.set_ylabel('amplitude (V)')

        ax2.plot(f_oneside, np.abs(X[:n_oneside]), 'b')
        ax2.set_xlabel('Freq (Hz)')
        ax2.set_ylabel('FFT Amplitude |X(freq)|')
        for x, y in peak_coords:
            # ax2.annotate(f'{int(x*1e-6)} MHz', xy=(x, y))
            ax2.text(x, y+0.003, f'{int(x*1e-6)} MHz', rotation=90)
        
        # save to file
        out_dir = 'plots'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        outfn = Path(self.infpn).stem
        outfpn = os.path.join(out_dir, outfn+'.png')
        
        plt.savefig(outfpn)
        plt.show()

    def waveform_peaks(self, height_thresh=5e-3, polarity=1, window_size=None):
        '''
        Apply peak finding algorithms to identify peak values.
        '''
        wv = self.df.waveform_value
        if not window_size is None:
            wv_name = f'waveform_value_moving_average_{window_size}'
            if not wv_name in self.df.columns:
                self.add_moving_average(window_size=window_size)
            wv = self.df[wv_name]
        peaks, props = find_peaks(polarity*wv, prominence=height_thresh, height=height_thresh, distance=50)
        is_peak = [True if i in peaks else False for i in range(len(self.df))]
        cname = 'is_peak' if window_size is None else f'is_peak_{window_size}'
        self.df[cname] = is_peak
        self.threshold = polarity*height_thresh
        return [(self.df.time[i], wv[i]) for i in peaks]

    def waveform_peak_time_diffs(self, height_thresh=5e-3, polarity=1, window_size=None):
        cname = 'is_peak' if window_size is None else f'is_peak_{window_size}'
        if not cname in self.df.columns:
            _ = self.waveform_peaks(height_thresh=height_thresh, polarity=polarity, window_size=window_size)
        peak_df = self.df[self.df[cname] == True]
        return peak_df.time.diff().dropna().tolist()
