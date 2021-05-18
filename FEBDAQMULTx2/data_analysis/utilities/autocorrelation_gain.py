#!/usr/bin/env python

from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from scipy.signal import find_peaks
from scipy import optimize
import common_tools
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import uproot

class MPPCLine:
    def __init__(self, infpn, verbose=False, swap_feb=False, pcb_half=0):
        # store constructor options
        self.infpn = infpn
        # boolean options
        self.verbose = verbose
        self.swap_feb = swap_feb
        self.pcb_half = pcb_half
        # data containers
        self.df_mppc = None
        self.df_metadata = None
        # derived variables
        self.nboards = None
        self.nchannels = None
        self.gains = dict()
        self.gain_errs = dict()

        # invoke initialization functions
        self.load_data()
    
    def load_data(self):
        '''
        Load a data file and other basic information
        to member variables.
        '''
        # store metadata
        tr_metadata = uproot.open(self.infpn)['metadata']
        self.df_metadata = tr_metadata.arrays(library='pd')

        # load mppc data
        tr_mppc = uproot.open(self.infpn)['mppc']
        df = tr_mppc.arrays(library='pd')

        # helper list to assign feb_id
        reversed = False
        if self.swap_feb: reversed = True
        lmacs = sorted(df['mac5'].unique(), reverse=reversed)
        self.nboards = len(lmacs)
        self.nchannels = self.nboards*32
        # process mppc data and store
        df['feb_id'] = df['mac5'].apply(lambda x: lmacs.index(x))
        self.df_mppc = df
    
    def gain_from_autocorrelation(self, ch=0, nbins=820, prom_frac=.001, outpn=None, full_plot=False):
        '''
        Use autocorrelation to estimate gain.
        Also save the autocorrelation plots.
        prom_frac: the fraction of the maximum autocorrelation value used as the prominence
        parameter for peak finding.
        '''
        # failsafe check
        if ch >= self.nboards*32:
            if self.verbose:
                print(f'PCB channel {ch} does not exist in this file.')
            return

        if ch in self.gains: return

        if self.verbose:
            print(f'\n*** Processing: channel {ch} of file {self.infpn}')

        # select data
        feb_id = self.get_feb_id(ch)
        df = self.df_mppc[self.df_mppc.feb_id == feb_id]
        chvar = 'chg[{}]'.format(ch%32)
        # make histogram and find peaks
        bins = np.linspace(0, 4100, nbins+1)
        _, axs = plt.subplots(2)
        histy, bin_edges, _ = axs[0].hist(df[chvar], bins=bins, histtype='step')

        # remove trailing zeroes
        while histy[-1] == 0.:
            histy = histy[:-1]
            bin_edges = bin_edges[:-1]
        
        # do the autocorrelation
        result = np.correlate(histy, histy, mode='full')

        # find autocorrelation peak adcs
        corr_size = result[result.size//2:]
        dbin = bins[1]-bins[0]
        peak_bins, _ = find_peaks(corr_size, prominence=np.max(corr_size)*prom_frac)
        peak_bins = np.insert(peak_bins*dbin, 0, 0)
        peak_dists = [peak_bins[i+1]-peak_bins[i] for i in range(peak_bins.size-1)]
        gain_err = np.std(peak_dists) if len(peak_dists) else -1
        self.gains[ch] = peak_dists[0] if len(peak_dists) else -1
        self.gain_errs[ch] = gain_err
        if self.verbose:
            print('First peak distance:', self.gains[ch])
            print('Average distance:', np.mean(peak_dists) if len(peak_dists) else -1)
            print('Standard deviation:', gain_err)

        # save plot to file
        if outpn is None:
            out_dir = os.path.join('plots', os.path.basename(os.path.splitext(__file__)[0]))
        else:
            out_dir = os.path.join(outpn, f'b{self.get_feb_id(ch)}c{ch%32}')
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        # save autocorrelation plots
        for res, tag in zip([result, result[result.size//2:]], ['full', 'half']):
            plt.close('all')
            fig, axs = plt.subplots(nrows=2, constrained_layout=True)
            fig.suptitle(self.get_parameter_string(ch), fontsize=9)
            axs[0].hist(df[chvar], bins=bins, histtype='step')
            axs[0].set_xlabel('ADC')
            axs[0].set_ylabel('counts')
            npts = len(res)
            axs[1].scatter(x=np.arange(0, npts, 1), y=res, s=7, c='r')
            axs[1].set_xlabel('ADC shift')
            axs[1].set_ylabel('autocorrelation')
            axs[1].annotate(r'total gain={:.2f}$\pm${:.2f} ADC/PE'.format(self.gains[ch], gain_err), xy=(0.52, 0.4), xycoords='axes fraction')
            if tag == 'half' or full_plot:
                # plt.tight_layout()
                plt.savefig(os.path.join(out_dir, f'b{self.get_feb_id(ch)}c{ch%32}_preamp{self.get_preamp_gain(ch)}_volt{self.get_bias_voltage()}_totgain_autocorrelation_{tag}.png'))
    
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
    
    def get_bias_regulation(self, ch=0):
        if not self.df_metadata.empty:
            df = self.df_metadata
            if self.nboards == 1:
                df_sel = df[(df['isTrigger'] == True)]
            else:
                df_sel = df[(df['isTrigger'] == True) & (df.board == self.get_feb_id(ch))]
            if not df_sel.empty:
                return df_sel['channelBias'].iloc[0]
        else: # try to get bias voltage from the file name
            for substr in os.path.basename(self.infpn.rstrip('.root')).split('_'):
                if 'biasregulation' in substr:
                    pos = substr.rfind('biasregulation')
                    return int(substr[pos+len('biasregulation'):])
        return -1

    def get_date(self):
        '''
        Return the date of the dataset.
        '''
        fn = os.path.basename(self.infpn)
        substrs = fn.split('_')
        if len(substrs):
            return substrs[0]
        return '19700101'

    def get_feb_id(self, ch=0):
        # No feb to swap if only one FEB is present.
        if self.nboards == 1: self.swap_feb = False
        return ch//32 if not self.swap_feb else 1-ch//32

    def get_parameter_string(self, ch=0):
        '''
        Return a string of physical parameters for use as plots' title.
        '''
        return f'PCB ch{ch%32+self.pcb_half*32}    date: {self.get_date()}\n' + r'V$_{{set}}$:{:.2f}V preamp gain:{} temperature:{:.2f}°C'.format(self.get_bias_voltage(), self.get_preamp_gain(ch), self.get_temperature()) + f'\nDAC:{self.get_threshold()} bias:{self.get_bias_regulation(ch)}'
    
    def get_preamp_gain(self, ch=0):
        if not self.df_metadata.empty:
            # if self.verbose:
            #     print('Getting preamp gain from the metadata tree...')
            df = self.df_metadata.copy()
            if not df.empty:
                if self.nboards == 1:
                    df_sel = df[(df['isTrigger'] == True)]
                else:
                    df_sel = df[(df['isTrigger'] == True) & (df.board == self.get_feb_id(ch))]
                # if self.verbose:
                #     print('metadata entry:\n', df_sel)
                if not df_sel.empty:
                    return df_sel['preampGain'].iloc[0]
        else:
            # if self.verbose:
            #     print('Getting preamp gain from file name...')
            for substr in self.infpn.split('_'):
                # I happen to use two different kinds of conventions...
                if 'preamp' in substr:
                    return float(substr.lstrip('preamp'))
                if 'gain' in substr:
                    return float(substr.lstrip('gain'))
        return -1
    
    def get_temperature(self):
        if not self.df_metadata.empty:
            return self.df_metadata['temperature'].iloc[0]
        else: # try to get bias voltage from the file name
            for substr in os.path.basename(self.infpn.rstrip('.root')).split('_'):
                if 'temp' in substr:
                    return float(substr.lstrip('temp'))
        return -1
    
    def get_threshold(self):
        if not self.df_metadata.empty:
            df_selch = self.df_metadata[self.df_metadata['isTrigger'] == True]

            if len(df_selch) >= 1:
                return df_selch['DAC'].iloc[0]
        else: # try to get threshold from file name
            for substr in os.path.basename(self.infpn).split('_'):
                if 'thr' in substr:
                    return substr.lstrip('thr')
        
        return -1


class MPPCLines:
    def __init__(self, infpns, verbose=False, swap_feb=False, pcb_half=0):
        '''
        Given a set of input root files, construct the group of MPPC lines.
        '''
        self.mppc_lines = [MPPCLine(infpn, verbose, swap_feb, pcb_half) for infpn in infpns]
        self.pcb_half = pcb_half
        self.swap_feb = swap_feb
        self.verbose = verbose
        # breakdown fit variables
        self.fitp = None
        self.fitpcov = None
        self.r2_gof = None
    
    def fit_total_gain_vs_bias_voltage(self, ch=0, nbins=820, prom_frac=0.001, outpn=None):
        '''
        This method takes a set of measurements with various bias voltages,
        plots total gain vs. bias voltage, fits a line, and takes the
        x intercept as the breakdown voltage.
        '''
        # failsafe check
        if ch >= self.mppc_lines[0].nboards*32:
            if self.verbose:
                print(f'PCB channel {ch} does not exist in this file.')
            return

        # estimate total gain and uncertainty from autocorrelation method
        for line in self.mppc_lines: line.gain_from_autocorrelation(ch, nbins, prom_frac, outpn)

        # construct x and y arrays for line fit
        y_raw = np.array([line.gains[ch] for line in self.mppc_lines])
        valid_idx = (y_raw>0)
        y = np.array([line.gains[ch] for line in self.mppc_lines])[valid_idx]
        x = np.array([line.get_bias_voltage() for line in self.mppc_lines])[valid_idx]
        yerr = np.array([line.gain_errs[ch] for line in self.mppc_lines])[valid_idx]

        # perform the line fit
        if len(y) > 1:
            p_init = np.array([y[1]-y[0], 50])
            # avoid infinite elements in the covariance matrix
            nonzero_yerrs = [val for val in yerr if val > 0]
            min_error = min(nonzero_yerrs) if len(nonzero_yerrs) else 1
            yerr = [min_error if val == 0 else val for val in yerr]
            self.fitp, self.fitpcov = optimize.curve_fit(common_tools.breakdown_voltage_linear_function, x, y, p_init, sigma=yerr)

            # mark the original data points
            plt.clf()
            # plt.errorbar(x, y, yerr=yerr, fmt='o', ms=7, mfc='r', mec='r', ecolor='r')
            plt.errorbar(x, y, yerr=yerr, fmt='o', markersize=3)
            plt.xlabel('bias voltage (V)')
            plt.ylabel('total gain (ADC/pe)')

            # plot the fit result
            vbd = self.fitp[1]
            vmax = max(x)*1.01
            vmin = vbd*.95
            xgain = np.linspace(vbd, vmax, 101)
            ygain = common_tools.breakdown_voltage_linear_function(xgain, *self.fitp)
            vbd_err = np.sqrt(self.fitpcov[1][1])
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

            # use r2 score as a goodness of fit measure
            lin_model = LinearRegression()
            lin_model.fit(np.array(x).reshape(-1,1), y)
            self.r2_gof = r2_score(y, lin_model.predict(np.array(x).reshape(-1,1)))

            # prepare the output folder
            if outpn is None:
                out_dir = os.path.join('plots', os.path.basename(os.path.splitext(__file__)[0]))
            else:
                out_dir = os.path.join(outpn, f'b{self.mppc_lines[0].get_feb_id(ch)}c{ch%32}')
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            plt.title(self.get_parameter_string(ch), fontsize=9)
            # plt.tight_layout(False)
            plt.savefig(os.path.join(out_dir, f'b{self.mppc_lines[0].get_feb_id(ch)}c{ch%32}_breakdown_autocorrelation.png'))
        else:
            self.fitp = (-1, -1)
            self.fitpcov = ((-1, -1), (-1, -1))
            self.r2_gof = -1
        
        # release memory
        plt.close('all')
    
    def get_parameter_string(self, ch=0):
        '''
        Return a string of physical parameters for use as plots' title.
        '''
        resstr = f'PCB ch{ch%32+self.pcb_half*32}    date:{self.mppc_lines[0].get_date()}\n' + r'preamp gain:{} temperature:{:.2f}°C'.format(self.mppc_lines[0].get_preamp_gain(ch), self.mppc_lines[0].get_temperature()) + f'\nDAC:{self.mppc_lines[0].get_threshold()} bias:{self.mppc_lines[0].get_bias_regulation(ch)}'
        # if the r2 linearity has a value, attach it
        if self.r2_gof:
            resstr += r' $R^2$:{:.4f}'.format(self.r2_gof)
        return resstr
    
    def get_pcb_ch(self, ch):
        '''
        Given a channel number, return its PCB channel number.
        '''
        if self.mppc_lines[0].nboards == 1: return ch
        if not self.swap_feb:
            return ch
        return ch+32 if ch <= 31 else ch-32


    def save_breakdowns(self, outfpn, ch=0):
        # if file exists, read it into a dataframe;
        # otherwise create a new dataframe
        columns = ['measurement_id','board','channel','pcb_ch','breakdown_voltage','breakdown_voltage_err','temperature','total_gain_5V_over','r2']
        if os.path.exists(outfpn):
            df = pd.read_csv(outfpn)
        else:
            df = pd.DataFrame(columns=columns)
        df = df.set_index(columns[:3])

        # construct the data dictionary
        new_data = dict()
        new_data['measurement_id'] = os.path.dirname(self.mppc_lines[0].infpn).split('/')[-1]
        new_data['board'] = self.mppc_lines[0].get_feb_id(ch)
        new_data['channel'] = ch%32
        new_data['pcb_ch'] = self.get_pcb_ch(ch) + (self.pcb_half*32 if self.mppc_lines[0].nboards == 1 else 0)
        new_data['breakdown_voltage'] = self.fitp[1]
        new_data['breakdown_voltage_err'] = np.sqrt(self.fitpcov[1][1]) if self.fitpcov[1][1] > 0 else -1
        new_data['temperature'] = self.mppc_lines[0].get_temperature()
        new_data['total_gain_5V_over'] = self.fitp[0]*5
        new_data['r2'] = self.r2_gof

        # make a new dataframe out of the new data record
        df_new = pd.DataFrame(columns=columns)
        df_new = df_new.append(new_data, ignore_index=True)
        df_new = df_new.set_index(columns[:3])
        print('Saving breakdown voltage:')
        print(df_new.head())

        # append new data if not exist
        # otherwise overwrite
        df = df.combine_first(df_new)

        # Write to file
        outpn = os.path.dirname(outfpn)
        if not os.path.exists(outpn):
            os.makedirs(outpn)
        df.to_csv(outfpn, mode='w')


# Turns out the idea does not work out.
# The function assumes 0 in x ranges not defined in the piecewise subroutine.
def piecewise_gaussian(x, pars):
    '''
    A 1d function composed of piecewise gaussian functions.
    '''
    pass