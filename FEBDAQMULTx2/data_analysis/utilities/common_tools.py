
from matplotlib import markers
from scipy.signal import find_peaks
from scipy.stats import norm, poisson
from sympy import Point2D, Line2D
import math
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import scipy.optimize as optimization
import seaborn as sns
import statistics
import sys
import uproot

class MPPCLine:
    def __init__(self, infpn, feb_id, ch, prom=300, pc_lth=0.7, pc_rth=1.4, voltage_offset=0, verbose=False):
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
            try:
                tr_metadata = uproot.open(infpn)['metadata']
                self.df_metadata = tr_metadata.pandas.df()
            except:
                self.df_metadata = pd.DataFrame()
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
        # record the voltage offset in case Vset is not Vbias
        self.voltage_offset = voltage_offset
        # record the bias voltage
        self.bias_voltage = self.get_bias_voltage() + voltage_offset
        # record the bias regulation on FEB
        self.bias_regulation = self.get_bias_regulation()
        # record the temperature
        self.temperature = self.get_temperature()
        # record the threshold
        self.threshold = self.get_threshold()
        # record the fit parameters from a function fit to the ADC spectrum
        self.fitp = None
        self.fitpcov = None

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

        # do linear fit with scipy's curve_fit for uncertainties in total gain
        x_try = [float(p.x) for p in self.points]
        y_try = [float(p.y) for p in self.points]
        self.gainfitp, self.gainfitpcov = optimization.curve_fit(my_linear_fun, x_try, y_try, [70, -250])
    
    def adc_spectrum(self, adcmin = 0, adcmax = 4100, savepn=None):
        histy, bin_edges, _ = plt.hist(self.df_1b[self.chvar], bins=self.bins, histtype='step')
        plt.xlim(left=adcmin, right=adcmax)
        plt.title('FEB{} ch{}\n{}'.format(self.feb_id, self.ch, self.get_parameter_string()))
        plt.xlabel('ADC')
        plt.ylabel('Count')
        if savepn:
            outfn = os.path.basename(self.infpn).rstrip('.root')+'_b{}c{}.png'.format(self.feb_id, self.ch)
            easy_save_to(plt, os.path.join(savepn, outfn))
        else:
            plt.show()
        plt.close()

    def fit_adc_spectrum(self, func, save_fpn=None):
        # notify the user what is being done
        print('Fitting', os.path.basename(self.infpn))

        # make the ADC spectrum
        histy, bin_edges, _ = plt.hist(self.df_1b[self.chvar], bins=self.bins, histtype='step', label='data')
        bin_centers = [(bin_edges[i+1]+bin_edges[i])/2 for i in range(len(bin_edges)-1)]

        # continuous zero removal from the end of the data
        zero_y_idx = []
        for i in range(len(histy)):
            idx = len(histy)-1-i
            if histy[idx] == 0.:
                zero_y_idx.append(idx)
            else: break
        xdata = [bin_centers[i] for i in range(len(bin_centers)) if i not in zero_y_idx]
        ydata = [histy[i] for i in range(len(histy)) if i not in zero_y_idx]

        # initial parameter guess
        # (N, gain, zero, noise, avnpe, excess, xtalk_frac)
        N = len(self.df_1b)
        gain = self.coeff[0]
        zero = float(self.points[0].y) if len(self.points) > 0 else 0
        noise = gain/100.
        avnpe = 6
        excess = gain/100.
        xtalk_frac = .1
        p_init = np.array([N, gain, zero, noise, avnpe, excess, xtalk_frac])

        # fit and show the results
        # print(optimization.curve_fit(func, xdata, ydata, p_init, bounds=([0,0,-np.inf,0,0,0,0],[np.inf,np.inf,np.inf,np.inf,np.inf,np.inf,np.inf])))
        try:
            self.fitp, self.fitpcov = optimization.curve_fit(func, xdata, ydata, p_init)
        except RuntimeError as e:
            plt.close()
            return -1
        yfit = func(xdata, *self.fitp)
        plt.plot(xdata, yfit, label='fit curve')
        plt.xlabel('ADC')
        plt.ylabel('count')
        plt.title('FEB{} ch{}\n{}'.format(self.feb_id, self.ch, self.get_parameter_string()))
        plt.legend()
        plt.annotate(r'total gain={:.2f}$\pm${:.2f} ADC/PE'.format(self.fitp[1],math.sqrt(self.fitpcov[1][1])), xy=(0.5, 0.5), xycoords='axes fraction')
        if save_fpn:
            easy_save_to(plt, save_fpn)
        else:
            plt.show()
        plt.close()

        return 1

    def get_bias_regulation(self):
        if not self.df_metadata.empty:
            df = self.df_metadata
            df_sel = df[(df['isTrigger'] == True) & (df['board'] == self.feb_id)]
            if not df_sel.empty:
                return df_sel['channelBias'].iloc[0]
        else: # try to get bias voltage from the file name
            for substr in os.path.basename(self.infpn.rstrip('.root')).split('_'):
                if 'biasregulation' in substr:
                    pos = substr.rfind('biasregulation')
                    return int(substr[pos+len('biasregulation'):])
        return -1

    def get_bias_voltage(self):
        if not self.df_metadata.empty:
            df = self.df_metadata
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
    
    def get_parameter_string(self):
        '''
        Return a string of physical parameters for use as plots' title.
        '''
        if self.voltage_offset != 0:
            return r'V$_{{bias}}$:{:.2f}V preamp gain:{} temperature:{:.2f}°C DAC:{} bias:{}'.format(self.bias_voltage, self.preamp_gain, self.temperature, self.threshold, self.bias_regulation)
        return r'V$_{{set}}$:{:.2f}V preamp gain:{} temperature:{:.2f}°C DAC:{} bias:{}'.format(self.bias_voltage+self.voltage_offset, self.preamp_gain, self.temperature, self.threshold, self.bias_regulation)

    def get_preamp_gain(self):
        if not self.df_metadata.empty:
            df = self.df_metadata.copy()
            if not df.empty:
                df_sel = df[(df['isTrigger'] == True) & (df.board == self.feb_id)]
                if not df_sel.empty:
                    return df_sel['preampGain'].iloc[0]
        else:
            for substr in self.infpn.split('_'):
                if 'preamp' in substr:
                    return float(substr.lstrip('preamp'))
        return -1
    
    def get_temperature(self):
        if not self.df_metadata.empty:
            df = self.df_metadata
            df_sel = df[(df.board == self.feb_id) & (df.channel == self.ch)]
            if not df_sel.empty:
                return df_sel['temperature'].iloc[0]
        else: # try to get bias voltage from the file name
            for substr in os.path.basename(self.infpn.rstrip('.root')).split('_'):
                if 'temp' in substr:
                    return float(substr.lstrip('temp'))
        return -1

    def get_threshold(self):
        if not self.df_metadata.empty:
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
        else: # try to get threshold from file name
            for substr in os.path.basename(self.infpn).split('_'):
                if 'thr' in substr:
                    return substr.lstrip('thr')
        
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
        threshold = self.get_threshold()
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
    
    def show_spectrum_and_fit(self, savepn=None, savefn=None):
        _, axs = plt.subplots(nrows=2)
        histy, bin_edges, _ = axs[0].hist(self.df_1b[self.chvar], bins=self.bins, histtype='step')
        axs[0].scatter(np.array(bin_edges)[self.peaks], np.array(histy)[self.peaks],
                    marker=markers.CARETDOWN, color='r', s=20)
        
        # build the histogram title
        axs[0].set_title('FEB{} ch{}\n{}'.format(self.feb_id, self.ch, self.get_parameter_string()), fontsize=10)

        # label peaks
        for i in range(len(self.points)):
            p = self.points[i]
            h = histy[self.peaks[i]]
            axs[0].text(float(p.y), h, str(int(p.x)))
        # plot decoration
        axs[0].set_xlabel('ADC')
        axs[0].set_ylabel('count')
        
        # plot the default fitted line
        xfit = np.linspace(0, len(self.points)-1, 100)
        yfit = self.coeff[0]*xfit + self.coeff[1]
        axs[1].scatter([float(p.x) for p in self.points], [float(p.y) for p in self.points])
        axs[1].plot(xfit, yfit, '--g', alpha=.7)
        axs[1].set_xlabel('PE number')
        axs[1].set_ylabel('ADC')

        axs[1].annotate(r'total gain={:.2f}$\pm${:.2f} ADC/PE'.format(self.gainfitp[0],math.sqrt(self.gainfitpcov[0][0])), xy=(0.52, 0.4), xycoords='axes fraction')
        # compare curve_fit results to polyfit
        if self.verbose:
            print(self.coeff[0], fitp[0])
            print(self.coeff[1], fitp[1])
        
        plt.tight_layout()
        if savepn:
            if not savefn:
                savefn = os.path.basename(self.infpn.replace('.root', 'voffset{}.png'.format(self.voltage_offset)))
            outfpn = os.path.join(savepn, savefn)
            easy_save_to(plt, outfpn)
        else:
            plt.show()
        plt.close()

    def voltage_from_filename(self, fn):
        for tmpstr in os.path.basename(fn).split('_'):
            if 'volt' in tmpstr:
                return float(tmpstr.lstrip('volt'))
        return 0.

class MPPCLines:
    def __init__(self, infpns, feb_id, ch, prom=300, pc_lth=0.7, pc_rth=1.4, voltage_offset=0, verbose=False):
        '''
        Given a set of input root files, construct the group of MPPC lines.
        '''
        self.mppc_lines = [MPPCLine(infpn, feb_id, ch, prom, pc_lth, pc_rth, voltage_offset, verbose) for infpn in infpns]
        self.voltage_offset = voltage_offset
    
    def enumerate_peaks(self):
        '''
        This method implements Wojciech's algorithm to number each peak correctly.
        The idea is to plot ADC vs. peak number where peak numbers can have arbitrary offset due to unknown data taking thresholds.
        If one plots the ADC vs. peak number lines with several different gains, and shifts them to the left or right,
        then the configuration where all lines intersect is the correct solution.
        '''
        nlines = len(self.mppc_lines)
        if nlines < 3:
            print('This enumerating algorithm requires at least 3 MPPC lines to ')
        rranges = tuple([slice(-1, 5, 1) for _ in range(nlines-1)])
        resbrute = optimize.brute(average_distance, rranges, args=mppc_lines, full_output=True, finish=None)

    
    def fit_total_gain_vs_bias_voltage(self, outpn=None, use_fit_fun=True, vset=False):
        '''
        This method takes a set of measurements with various bias voltages,
        plots total gain vs. bias voltage, fits a line, and takes the
        x intercept as the breakdown voltage.
        '''
        x = []
        y = []
        yerr = []
        for line in self.mppc_lines:
            if (not line.fitp) or (not line.fitpcov):
                outfpn = None
                if outpn:
                    outfn = os.path.basename(line.infpn).rstrip('.root')+'_b{}c{}_voffset{}.png'.format(line.feb_id, line.ch, line.voltage_offset)
                if use_fit_fun:
                    if line.fit_adc_spectrum(gaussian_sum_fit_func, outfpn) > 0:
                        x.append(line.bias_voltage)
                        y.append(line.fitp[1])
                        yerr.append(math.sqrt(line.fitpcov[1][1]))
                else:
                    x.append(line.bias_voltage)
                    y.append(line.gainfitp[0])
                    cur_yerr = math.sqrt(line.gainfitpcov[0][0]) # avoid divide by zero issue when fitting
                    yerr.append(cur_yerr if cur_yerr > 0 else 0.01)
                    # store intermediate plots
                    line.show_spectrum_and_fit(outpn, outfn)
        plt.errorbar(x, y, yerr=yerr, fmt='o', markersize=3)
        # decide x label
        xtitle = 'bias voltage (V)'
        if vset:
            xtitle = r'V$_{set}$ (V)'
        plt.xlabel(xtitle)
        plt.ylabel('total gain (ADC/PE)')
        par_str = r'preamp gain:{} temperature:{:.2f}°C DAC:{} bias:{}'.format(self.mppc_lines[0].preamp_gain, self.mppc_lines[0].temperature, self.mppc_lines[0].threshold, self.mppc_lines[0].bias_regulation)
        plt.title('FEB{} ch{}\n{}'.format(self.mppc_lines[0].feb_id, self.mppc_lines[0].ch, par_str), fontsize=10)

        # make a linear fit to extract the breakdown voltage
        slope = (y[1]-y[0])/(x[1]-x[0]) if len(y) >= 2 else 10
        intercept = 50
        p_init = np.array([slope, intercept])
        try:
            self.fitp, self.fitpcov = optimization.curve_fit(breakdown_voltage_linear_function, x, y, p_init, sigma=yerr)
        except RuntimeError as e:
            plt.close()
            return -1
        vbd = self.fitp[1]
        vmax = max(x)*1.01
        vmin = vbd*.95
        xgain = np.linspace(vbd, vmax, 101)
        ygain = breakdown_voltage_linear_function(xgain, *self.fitp)
        vbd_err = math.sqrt(self.fitpcov[1][1])
        # plot the breakdown voltage line
        plt.xlim(left=vmin, right=vmax)
        plt.ylim(bottom=0)
        plt.plot(xgain, ygain)
        # mark the x-intercept
        arrow_ylen = (ygain[-1]-ygain[0])*.2
        arrow_xlen = (xgain[-1]-xgain[0])*.2
        xtext = vbd-1.5*arrow_xlen if vbd-1.5*arrow_xlen > vmin else vmin*1.005
        plt.annotate(r'{:.2f}$\pm${:.3f}V'.format(vbd, vbd_err), xy=(vbd, 0),
                     xytext=(xtext, arrow_ylen),
                     arrowprops=dict(color='magenta', shrink=0.05), c='b')

        # save results to files
        if outpn:
            substrs = os.path.basename(self.mppc_lines[0].infpn).rstrip('.root').split('_')
            del substrs[1]
            outfn = '_'.join(substrs) + '_b{}c{}_voffset{}.png'.format(self.mppc_lines[0].feb_id, self.mppc_lines[0].ch, self.voltage_offset)
            outfpn = os.path.join(outpn, outfn)
            easy_save_to(plt, outfpn)
        else:
            plt.show()
        plt.close()

        return 1
    
    def fit_total_gain_vs_preamp_gain(self, outpn=None, use_fit_fun=True):
        '''
        This method takes a set of measurements with various preamp gains,
        plots total gain vs. preamp gain, fits a line, and takes the
        x intercept as the breakdown voltage.
        If use_fit_fun is set, use the 7-parameter function to get gain. Otherwise, use the simple line fit.
        '''
        x = []
        y = []
        yerr = []
        for line in self.mppc_lines:
            outfpn = None
            if outpn:
                outfn = os.path.basename(line.infpn).rstrip('.root')+'_b{}c{}_voffset{}.png'.format(line.feb_id, line.ch, line.voltage_offset)
            if use_fit_fun:
                if (not line.fitp) or (not line.fitpcov):
                    if line.fit_adc_spectrum(gaussian_sum_fit_func, outfpn) > 0:
                        x.append(line.preamp_gain)
                        y.append(line.fitp[1])
                        yerr.append(math.sqrt(line.fitpcov[1][1]))
            else:
                x.append(line.preamp_gain)
                y.append(line.gainfitp[0])
                yerr.append(math.sqrt(line.gainfitpcov[0][0]))
                # store intermediate plots
                line.show_spectrum_and_fit(outpn, outfn)
        plt.errorbar(x, y, yerr=yerr, fmt='o', markersize=3)
        plt.xlabel('preamp gain')
        plt.ylabel('total gain')
        par_str = r'V$_{{set}}$:{}V temperature:{:.2f}°C DAC:{}'.format(self.mppc_lines[0].bias_voltage+self.mppc_lines[0].voltage_offset, self.mppc_lines[0].temperature, self.mppc_lines[0].threshold)
        plt.title('FEB{} ch{}\n{}'.format(self.mppc_lines[0].feb_id, self.mppc_lines[0].ch, par_str))
        if outpn:
            substrs = os.path.basename(self.mppc_lines[0].infpn).rstrip('.root').split('_')
            del substrs[1]
            outfn = '_'.join(substrs) + '.png'
            outfpn = os.path.join(outpn, outfn)
            easy_save_to(plt, outfpn)
        else:
            plt.show()
        plt.close()


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

def breakdown_voltage_linear_function(x, slope, vbd):
    '''
    Instead of the blind y = m * x + b, write the breakdown voltage explicitely
    in the equation for easy error estimate. That is,
    y = slope * (x - vbd)
    '''
    return slope*(x-vbd)

def easy_save_to(thisplt, outfpn):
    '''
    Make saveing file effortless.
    outfpn is a full pathname.
    '''
    out_dir = os.path.dirname(outfpn)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    thisplt.savefig(outfpn)

def multipoisson_fit_function(x, N, gain, zero, noise, avnpe, excess, mu):
    '''
    This is the multipoisson formula used for fit the MPPC ADC spectrum.
    Source: http://zeus.phys.uconn.edu/wiki/index.php/Characterizing_SiPMs
    A set of parameters leading to conpicuous peaks is
    {x,1000,10,10,0.2,3,0.05,0.5} where x is in [0,200]
    '''
    maxpe = 13
    retval = 0
    q = (x-zero)/gain
    for p in range(maxpe+1):
        for s in range(maxpe+1):
            retval += poisson(avnpe).pmf(p)*poisson(avnpe*mu).pmf(s)*norm.pdf(q, p+s, math.sqrt(noise**2+excess**2*(p+s)))
    retval *= N
    return retval

def my_linear_fun(x, m, b):
    '''
    The most mundane function form of a linear function.
    '''
    return m*x+b

def gaussian_sum_fit_func(x, N, gain, zero, noise, avnpe, excess, xtalk):
    '''
    This is the gaussian sum formula used for fit the MPPC ADC spectrum.
    Source: CAEN DT5702 reference DAQ
    '''
    maxpe = 15
    retval = 0
    peaks = []
    peaksint = []
    for i in range(maxpe):
        peaks.append(zero+gain*i)
        peaksint.append(poisson(avnpe).pmf(i))
        if i > 1:
            peaksint[i] = peaksint[i] + peaksint[i-1] * xtalk
    for i in range(maxpe):
        retval += peaksint[i]*(norm.pdf(x, peaks[i], math.sqrt(noise**2+i*excess**2)))
    retval *= N
    return retval

def longestSubstringFinder(string1, string2):
    '''
    Source: https://stackoverflow.com/questions/18715688/find-common-substring-between-two-strings
    '''
    answer = ''
    len1, len2 = len(string1), len(string2)
    for i in range(len1):
        match = ''
        for j in range(len2):
            if (i + j < len1 and string1[i + j] == string2[j]):
                match += string2[j]
            else:
                if (len(match) > len(answer)): answer = match
                match = ''
    return answer
