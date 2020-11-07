
from matplotlib import markers
from scipy.signal import find_peaks
from sympy import Point2D, Line2D
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import seaborn as sns
import statistics
import sys
import uproot

class MPPCLine:
    def __init__(self, infpn, feb_id, ch, prom=300, pc_lth=0.7, pc_rth=1.4, verbose=False):
        '''
        The constructor is responsible for finding peak positions given
        a filename and a channel ID.
        '''
        if verbose:
            print('Processing:\n', infpn)
        # get the dataframe either from a .h5 file or a .root file directly
        fext = os.path.splitext(infpn)[1]
        if fext == '.h5':
            try:
                df = pd.read_hdf(infpn, key='mppc')
            except:
                print('Error reading file {}'.format(infpn))
                sys.exit(-1)
                return
        elif fext == '.root':
            tr_mppc = uproot.open(infpn)['mppc']
            df = tr_mppc.pandas.df()
            df['feb_num'] = df['mac5'].apply(lambda x: 0 if x == 85 else 1 if x == 170 else -1)
            if verbose:
                print('Converted dataframe from ROOT:\n', df)
            tr_metadata = uproot.open(infpn)['metadata']
            self.df_metadata = tr_metadata.pandas.df()
        else:
            print('File format is neither a hdf5 nor a root.')
            sys.exit(-1)

        # store verbosity
        self.verbose = verbose
        # store the input file name
        self.infpn = infpn
        # make the plot of a channel
        self.feb_id = feb_id
        self.ch = ch
        self.chvar = 'chg[{}]'.format(ch)
        # record the preamp gain
        self.preamp_gain = self.get_preamp_gain()
        # record the bias voltage
        self.bias_voltage = self.get_bias_voltage()
        # record the temperature
        self.temperature = self.get_temperature()

        # select data of the specified board
        self.df_1b = df[df['feb_num'] == feb_id]
        if verbose:
            print('FEB{} dataframe:\n'.format(feb_id), self.df_1b)
        # make histogram and find peaks
        self.bins = np.linspace(0, 4100, 821)
        _, axs = plt.subplots(2)
        histy, bin_edges, _ = axs[0].hist(self.df_1b[self.chvar], bins=self.bins, histtype='step')
        self.peaks, _ = find_peaks(histy, prominence=prom)
        if verbose:
            print('Found peaks with heights:\n', self.peaks)
        
        # release memory
        plt.close()

        # store processed data
        pc = PeakCleanup(list(np.array(bin_edges)[self.peaks]))
        pc.remove_outlier_by_relative_interval(pc_rth, pc_lth)
        self.peak_adcs = pc.peak_adcs
        if verbose:
            print('Peak ADCs:\n', self.peak_adcs)
        self.points = [Point2D(i, self.peak_adcs[i]) for i in range(len(self.peak_adcs))]

        # fit a line to the points
        if len(self.peaks) > 1:
            self.line, self.coeff = self.get_line_from_points(self.points)

        # bias voltage
        self.voltage = self.voltage_from_filename(infpn)
    
    def get_bias_voltage(self):
        df = self.df_metadata
        if not df.empty:
            df_sel = df[df['isTrigger'] == True]
            if not df_sel.empty:
                return df_sel['biasVoltage'].iloc[0]
        else: # try to get bias voltage from the file name
            for substr in os.path.basename(self.infpn).split('_'):
                if 'volt' in substr:
                    return float(substr.lstrip('volt'))
        return -1

    def get_line_from_points(self, pts):
        # fit a line to the points
        x_try = np.array([p.x for p in pts]).astype(float)
        y_try = np.array([p.y for p in pts]).astype(float)
        coeff = np.polyfit(x_try, y_try, 1)
        return Line2D(Point2D(0, coeff[1]), slope=coeff[0]), coeff
    
    def get_preamp_gain(self):
        df = self.df_metadata.copy()
        if not df.empty:
            df_sel = df[df['isTrigger'] == True]
            if not df_sel.empty:
                return df_sel['preampGain'].iloc[0]
        return -1
    
    def get_temperature(self):
        df = self.df_metadata
        if not df.empty:
            df_sel = df[(df.board == self.feb_id) & (df.channel == self.ch)]
            if not df_sel.empty:
                return df_sel['temperature'].iloc[0]
        else: # try to get bias voltage from the file name
            for substr in os.path.basename(self.infpn).split('_'):
                if 'temp' in substr:
                    return float(substr.lstrip('temp'))
        return -1

    def get_threshold_from_metadata(self):
        # get the dataframe either from a .h5 file or a .root file directly
        fext = os.path.splitext(self.infpn)[1]
        if fext == '.h5':
            try:
                df = pd.read_hdf(self.infpn, key='metadata')
            except:
                print('Error reading metadata from {}'.format(self.infpn))
                return 0
        elif fext == '.root':
            tr_mppc = uproot.open(self.infpn)['metadata']
            df = tr_mppc.pandas.df()
        df_selch = df[df['isTrigger'] == True]

        if len(df_selch) >= 1:
            return df_selch['DAC'].iloc[0]
        
        return -1

    def shift_and_match(self, pkadcs):
        '''
        This method shifts the peak IDs to the left or right in a small range,
        and find the best fit to the peak ADC input array.
        The "pkadcs" is a known input array in which the index is the peak number and the value is the peak ADC.
        '''

        # get the line formed by the input array
        ref_points = [Point2D(i, pkadcs[i]) for i in range(len(pkadcs))]
        ref_line, _ = self.get_line_from_points(ref_points)

        diff_sum = []
        shift_min = -3
        shift_max = 6
        for shift in range(shift_min, shift_max):
            pts = [Point2D(float(p.x)+shift, float(p.y)) for p in self.points]
            dist_sum = 0
            for p in pts:
                dist_sum += ref_line.distance(p)
            diff_sum.append(dist_sum)
        best_shift = np.argmin(diff_sum) + shift_min
        if self.verbose:
            print('Sum of distances from points to the reference line, shifting from {} to {} in x:\n'.format(shift_min, shift_max-1), diff_sum)
            print('Best shift:', best_shift)
        self.shift_peak_id(best_shift)

    def shift_peak_id(self, x_shift):
        '''
        This method shifts all peak position assignments to the left or right
        by x_shift amount. It also shifts the fitted line by the same amount.
        '''
        self.points = [Point2D(i+x_shift, self.peak_adcs[i]) for i in range(len(self.peak_adcs))]
        self.coeff[1] -= self.coeff[0]*x_shift
        self.line = Line2D(Point2D(0, self.coeff[1]), slope=self.coeff[0])
    
    def show_gain_vs_pe(self, savefpn=None):
        x = [float(p.x) for p in self.points]
        y = [float(p.y) for p in self.points]
        plt.scatter(x, y)
        plt.show()
        plt.close()
    
    def show_spectrum(self, savefpn=None):
        histy, bin_edges, _ = plt.hist(self.df_1b[self.chvar], bins=self.bins, histtype='step')
        plt.scatter(np.array(bin_edges)[self.peaks], np.array(histy)[self.peaks],
                    marker=markers.CARETDOWN, color='r', s=20)
        threshold = self.get_threshold_from_metadata()
        if threshold > 0:
            plt.title('DAC {}'.format(threshold))
        for i in range(len(self.points)):
            p = self.points[i]
            h = histy[self.peaks[i]]
            plt.text(float(p.y), h, str(int(p.x)))
        if savefpn:
            plt.savefig(savefpn)
        else:
            plt.show()
        plt.close()
    
    def show_spectrum_and_fit(self, savefpn=None):
        _, axs = plt.subplots(nrows=2)
        histy, bin_edges, _ = axs[0].hist(self.df_1b[self.chvar], bins=self.bins, histtype='step')
        axs[0].scatter(np.array(bin_edges)[self.peaks], np.array(histy)[self.peaks],
                    marker=markers.CARETDOWN, color='r', s=20)
        
        # build the histogram title
        threshold = self.get_threshold_from_metadata()
        if threshold > 0:
            axs[0].set_title('DAC {}'.format(threshold))

        # label peaks
        for i in range(len(self.points)):
            p = self.points[i]
            h = histy[self.peaks[i]]
            axs[0].text(float(p.y), h, str(int(p.x)))
        # plot decoration
        axs[0].set_xlabel('ADC')
        axs[0].set_ylabel('count')
        
        # plot the fitted line
        xfit = np.linspace(0, len(self.points)-1, 100)
        yfit = self.coeff[0]*xfit + self.coeff[1]
        axs[1].scatter([float(p.x) for p in self.points], [float(p.y) for p in self.points])
        axs[1].plot(xfit, yfit, '--g', alpha=.7)
        axs[1].set_xlabel('PE number')
        axs[1].set_ylabel('ADC')
        
        plt.tight_layout()
        if savefpn:
            plt.savefig(savefpn)
        else:
            plt.show()
        plt.close()

    def voltage_from_filename(self, fn):
        for tmpstr in fn.split('_'):
            if 'volt' in tmpstr:
                return float(tmpstr.lstrip('volt'))
        return 0.

class MPPCLines:
    def __init__(self, infpns, feb_id, ch, prom=300, pc_lth=0.7, pc_rth=1.4, verbose=False):
        '''
        Given a set of input root files, construct the group of MPPC lines.
        '''
        self.mppc_lines = [MPPCLine(infpn, feb_id, ch, prom, pc_lth, pc_rth, verbose) for infpn in infpns]

class PeakCleanup:
    def __init__(self, peak_adcs):
        self.peak_adcs = peak_adcs
        self.peak_diffs = [peak_adcs[i+1]-peak_adcs[i] for i in range(len(peak_adcs)-1)]
    
    def mad_based_outlier(self, points, thresh=3.5):
        '''
        Ref: https://stackoverflow.com/questions/22354094/pythonic-way-of-detecting-outliers-in-one-dimensional-observation-data/22357811#22357811
        '''
        if len(points.shape) == 1:
            points = points[:,None]
        median = np.median(points, axis=0)
        diff = np.sum((points - median)**2, axis=-1)
        diff = np.sqrt(diff)
        med_abs_deviation = np.median(diff)
        if med_abs_deviation < 1e-2: med_abs_deviation = 1

        modified_z_score = 0.6745 * diff / med_abs_deviation
        print(modified_z_score)

        return modified_z_score > thresh
    
    def mad_based_outlier_idx(self, points, thresh=3.5):
        '''
        Return the indices of the outliers.
        '''
        if len(points.shape) == 1:
            points = points[:,None]
        median = np.median(points, axis=0)
        diff = np.sum((points - median)**2, axis=-1)
        diff = np.sqrt(diff)
        med_abs_deviation = np.median(diff)
        if med_abs_deviation < 1e-2: med_abs_deviation = 1

        modified_z_score = 0.6745 * diff / med_abs_deviation
        # scale the threshold accordingly
        if len(modified_z_score): thresh = thresh * np.sqrt(8 / len(modified_z_score))

        return [i for i in range(len(modified_z_score)) if modified_z_score[i] > thresh]
    
    def plot(self, x, thresh=5):
        fig, axes = plt.subplots(nrows=1)
        for ax, func in zip([axes], [self.mad_based_outlier]):
            sns.distplot(x, ax=ax, rug=True, hist=False)
            outliers = x[func(x, thresh)]
            ax.plot(outliers, np.zeros_like(outliers), 'ro', clip_on=False)

        kwargs = dict(y=0.95, x=0.05, ha='left', va='top')
        axes.set_title('Median-based Outliers', **kwargs)
        fig.suptitle('Outlier Tests with n={}'.format(len(x)), size=14)
    
    def plot_to_axis(self, ax, x, thresh=5):
        sns.distplot(x, ax=ax, rug=True, hist=False)
        outliers = x[self.mad_based_outlier(x, thresh)]
        ax.plot(outliers, np.zeros_like(outliers), 'ro')

        ax.set_title('outlier detection')
        ax.set_xlabel('adjacent ADC difference')
    
    def relative_interval(self):
        points = np.array(self.peak_diffs)
        if len(points.shape) == 1:
            points = points[:,None]
        median = np.median(points, axis=0)

        if median > 0:
            return [x/np.asscalar(median) for x in self.peak_diffs]
        
        return self.peak_diffs

    def remove_outlier(self, idx):
        # try to remove the left and the right data points
        # and compare which one is more reasonable
        left_removed = self.peak_adcs.copy()
        left_removed.pop(idx)
        right_removed = self.peak_adcs.copy()
        right_removed.pop(idx+1)
        left_diff = [left_removed[i+1]-left_removed[i] for i in range(len(left_removed)-1)]
        right_diff = [right_removed[i+1]-right_removed[i] for i in range(len(right_removed)-1)]
        # keep the one with a smaller standard deviation
        if len(left_diff) >= 2 and len(right_diff) >= 2:
            if statistics.stdev(left_diff) < statistics.stdev(right_diff):
                self.peak_adcs = left_removed
                self.peak_diffs = left_diff
            else:
                self.peak_adcs = right_removed
                self.peak_diffs = right_diff
    
    def remove_outlier_by_relative_interval(self, right_th=1.2, left_th=0.8):
        rel_int = self.relative_interval()
        outl_idx = [i for i in range(len(rel_int)) if rel_int[i] > right_th or rel_int[i] < left_th]
        while outl_idx:
            self.remove_outlier(outl_idx[-1])
            outl_idx = outl_idx[:-1]
    
    def remove_outlier_twice(self):
        for _ in range(2):
            outl_idx = self.mad_based_outlier_idx(np.array(self.peak_diffs), thresh=5)
            if outl_idx:
                self.remove_outlier(outl_idx[-1])
