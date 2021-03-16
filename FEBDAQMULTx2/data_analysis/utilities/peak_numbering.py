#!/usr/bin/env python

# my own modules
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../utilities'))
import common_tools

from glob import glob
from scipy import optimize
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
import seaborn as sns

class fitting_algorithm(common_tools.MPPCLines):
    '''
    This algorithm finds the best peak numbering configuration by finding the configuration with the smallest spread of the pedestal ADCs from different bias voltages.
    The pedestal ADCs are estimated by an explicit functional form with number of photoelectrons and bias voltage as independent variables.

    The functional form of ADC is,
    ADC = beta * (V-Vbd) * PE + gamma
    , where the independent variables are V, bias voltage, and PE, photoelectron.
    Besides, beta is a proportional constant, Vbd the breakdown voltage, and gamma the ADC offset at 0 PE (i.e., pedestal ADC).
    '''
    def __init__(self, infpns, feb_id, ch, prom=100, pc_lth=0.7, pc_rth=1.4, voltage_offset=0, verbose=False, pcb_half=None, outpn=None):
        '''
        Initialize class data with a dataset of the same preamp gain and different bias voltages.
        '''
        if type(infpns) == str:
            infpns = sorted(glob(infpns))
        super().__init__(infpns, feb_id, ch, prom, pc_lth=pc_lth, pc_rth=pc_rth, voltage_offset=voltage_offset, verbose=False, pcb_half=pcb_half)

        # store debug message verbosity
        self.verbose = verbose

        # store output path
        self.outpn = outpn

        # 3D data container of the form (pe, V_bias, adc)
        self.df_3d_pts = pd.DataFrame(columns=['pe', 'bias_voltage', 'adc'])

        # container for all bias voltages involved in this datasets
        self.bias_voltages = []

        # container for all betas involved in these datasets
        self.betas = []

        # container for an estimated breakdown voltage
        self.breakdown_voltage = None

        # fitted physical parameters
        self.beta_fit = None
        self.gamma_fit = None
        self.breakdown_voltage_fit = None
        self.beta_err = None
        self.gamma_err = None
        self.breakdown_voltage_err = None

        # fill df_3d_pts and bias_voltages
        self.fill_measured_points()

        # fill breakdown_voltage and betas
        self.fill_breakdown_voltage(outpn=outpn)
    
    def fill_breakdown_voltage(self, outpn=None):
        '''
        Run the first breakdown voltage fit from the gain vs bias voltage graph.
        '''
        self.fit_total_gain_vs_bias_voltage(outpn, use_fit_fun=False)
        self.breakdown_voltage = self.fitp[1]
        self.betas = [line.gainfitp[0]/(line.bias_voltage - self.breakdown_voltage) for line in self.mppc_lines]

    def fill_measured_points(self):
        '''
        Assemble all measured (pe, V_bias, adc) points in 3D.
        '''
        for line in self.mppc_lines:
            self.bias_voltages.append(line.bias_voltage)
            for pe, adc in enumerate(line.peak_adcs):
                self.df_3d_pts.loc[len(self.df_3d_pts.index)] = [pe, line.bias_voltage, adc]
    
    def fit_peak_numbering(self, shift_limit=4):
        '''
        Find the best configuration by the following algorithm.
        1. For each bias voltage, calculate the average number of (measured ADC - beta*(v-vbd)*pe).
        2. Calculate the standard deviation of the array of numbers obtained in 1., and take the configuration with the smallest standard deviation.
        '''

        nlines = len(self.mppc_lines)
        if nlines < 3:
            print('This enumerating algorithm requires at least 3 MPPC lines to function.')
            print('You provide only', '1 line.' if len(self.mppc_lines) == 1 else '{} lines.'.format(len(self.mppc_lines)))
            sys.exit(-1)
        rranges = tuple([slice(0, shift_limit, 1) for _ in range(nlines)])
        # resbrute = optimize.brute(self.pedestal_adc_spreaad, rranges, full_output=True, finish=None, workers=-1)
        resbrute = optimize.brute(self.pedestal_adc_spreaad, rranges, full_output=True, finish=None, workers=1)
        # print some fit information
        if self.verbose:
            print('Best configuration:', resbrute[0])
            print('Loss function (pedestal ADC spread): {:.2f}'.format(resbrute[1]))

        # save optimal configuration to the dataframe
        # shift pe numbering in groups of bias voltages
        for vb, shift in zip(self.bias_voltages, resbrute[0]):
            self.df_3d_pts.loc[self.df_3d_pts.bias_voltage == vb, 'shifted_pe'] = self.df_3d_pts[self.df_3d_pts.bias_voltage == vb]['pe'] + shift
            df = self.df_3d_pts[self.df_3d_pts.bias_voltage == vb]
            self.df_3d_pts.loc[self.df_3d_pts.bias_voltage == vb, 'rough_pedestal_adc'] = df['adc'] - adc_function([df['shifted_pe'], df['bias_voltage']], np.mean(self.betas), self.breakdown_voltage, 0)

    
    def pedestal_adc_spreaad(self, z):
        '''
        This is the loss function for the grid search optimization of the fit_peak_numbering function.
        '''
        # use the average value of betas as a common parameter
        beta_bar = np.mean(self.betas)
        
        # shift pe numbering in groups of bias voltages
        for vb, shift in zip(self.bias_voltages, z):
            self.df_3d_pts.loc[self.df_3d_pts.bias_voltage == vb, 'shifted_pe'] = self.df_3d_pts[self.df_3d_pts.bias_voltage == vb]['pe'] + shift
            
        mean_pedestal_adc = []
        for vb in self.bias_voltages:
            df = self.df_3d_pts[self.df_3d_pts.bias_voltage == vb]
            pedestal_adcs = df['adc'] - adc_function([df['shifted_pe'], df['bias_voltage']], beta_bar, self.breakdown_voltage, 0)
            self.df_3d_pts.loc[self.df_3d_pts.bias_voltage == vb, 'rough_pedestal_adc'] = pedestal_adcs
            mean_pedestal_adc.append(np.mean(pedestal_adcs))

        return np.std(mean_pedestal_adc)
    
    def plot_breakdown_voltage_comparison(self):
        '''
        This method compares the breakdown voltage and its uncertainty obtained with the line fitting and the ADC function fitting.
        '''

        if not self.breakdown_voltage_fit:
            print('You have not fit the ADC function to data. I\'m not not plotting...')
            return
        
        xtick_labels = ['line fit', 'ADC function fit']
        x = [0, 1]
        y = [self.breakdown_voltage, self.breakdown_voltage_fit]
        yerr = [np.sqrt(self.fitpcov[1][1]), self.breakdown_voltage_err]

        plt.errorbar(x=x, y=y, yerr=yerr, fmt='o')
        plt.xlim((-.5, 1.5))
        plt.xticks(x, xtick_labels)
        plt.ylabel('breakdown voltage (V)')
        plt.grid(axis='y')

        # build title string
        aline = self.mppc_lines[0]
        title_str = 'FEB{} ch{}\n'.format(aline.feb_id, aline.ch)+r'preamp gain:{} temperature:{:.2f}°C DAC:{} bias:{}'.format(aline.preamp_gain, aline.temperature, aline.threshold, aline.bias_regulation)
        plt.title(title_str)

        # save to file
        common_tools.easy_save_to(plt, os.path.join(self.outpn, 'breakdown_voltage_comparison.png'))
        plt.close()


    def plot_gamma_spread(self):
        '''
        This method is to make distribution plots grouped by bias voltage to justify the use of the spread of the pedestal ADC as the loss function for shift configuration.
        '''

        # clear figure
        plt.figure(clear=True)

        # make a column for raw pedestal ADC
        for vb in self.bias_voltages:
            df = self.df_3d_pts[self.df_3d_pts.bias_voltage == vb]
            pedestal_adcs = df['adc'] - adc_function([df['pe'], df['bias_voltage']], np.mean(self.betas), self.breakdown_voltage, 0)
            self.df_3d_pts.loc[self.df_3d_pts.bias_voltage == vb, 'raw_pedestal_adc'] = pedestal_adcs

        # make swarm plot for raw pedestal ADC
        sns_plot = sns.catplot(x='bias_voltage', y='raw_pedestal_adc', kind='violin', inner=None, data=self.df_3d_pts)
        sns.swarmplot(x='bias_voltage', y='raw_pedestal_adc', color='k', size=3, data=self.df_3d_pts, ax=sns_plot.ax)
        sns_plot.ax.set_xlabel('bias voltage (V)')
        sns_plot.ax.set_ylabel('estimated pedestal ADC')
        sns_plot.ax.set_title('raw configuration')
        sns_plot.tight_layout()

        # save raw pedestal ADC plot
        common_tools.easy_save_to(plt, os.path.join(self.outpn, 'raw_pedestal_adc.png'))
        plt.close()

        # check if the rough_pedestal_adc column exists
        if not 'rough_pedestal_adc' in self.df_3d_pts.columns: return

        # make swarm plot for optimal pedestal ADC
        sns_plot = sns.catplot(x='bias_voltage', y='rough_pedestal_adc', kind='violin', inner=None, data=self.df_3d_pts)
        sns.swarmplot(x='bias_voltage', y='rough_pedestal_adc', color='k', size=3, data=self.df_3d_pts, ax=sns_plot.ax)
        sns_plot.ax.set_xlabel('bias voltage (V)')
        sns_plot.ax.set_ylabel('estimated pedestal ADC')
        sns_plot.ax.set_title('optimal configuration')
        sns_plot.tight_layout()

        # save raw pedestal ADC plot
        common_tools.easy_save_to(plt, os.path.join(self.outpn, 'optimal_pedestal_adc.png'))
        plt.close()
    
    def plot_adc_vs_peak_number(self):
        '''
        This method plots the ADC vs peak number before and after the optimal configuration is found.
        '''
        
        # fix a random seed for repeatable color map
        random.seed(100)

        # plot dots and lines
        for vb in self.bias_voltages:
            # determine line color
            rgb = (random.random(), random.random(), random.random())
            # select data of this bias voltage
            df = self.df_3d_pts[self.df_3d_pts.bias_voltage == vb]
            # make scatter plot of points
            px = df['shifted_pe']
            py = df['adc']
            plt.scatter(px, py, color=rgb)
            # fit a line and get parameters
            m, b = np.polyfit(px, py, 1)
            # calculate the range of x and plot
            xmax = max(px)*1.2
            xmin = -b/m * .6
            fitx = np.linspace(xmin, xmax, 100)
            fity = adc_function([fitx, np.full(len(fitx), vb)], self.beta_fit, self.breakdown_voltage_fit, self.gamma_fit)
            plt.plot(fitx, fity, '--', alpha=.7, color=rgb, label='{} V'.format(vb))
        
        # plot the fitted pedestal ADC
        if self.gamma_fit:
            xx = 0
            yy = self.gamma_fit
            plt.errorbar(xx, yy, yerr=self.gamma_err, color='r', fmt='--X')
            plt.annotate('({:.2f},{:.2f})'.format(xx, yy), xy=(xx, yy), xytext=(xx+0.35, yy-30))
        plt.title('best fit of the unified model')
        plt.grid(axis='x')
        plt.legend()
        plt.xlabel('photoelectron')
        plt.ylabel('ADC')
        common_tools.easy_save_to(plt, os.path.join(self.outpn, 'adc_vs_pe_best_fit.png'))
        plt.close()

    def refit_physics_parameters(self):
        '''
        After getting the correct pe numbers, fit adc_function again to obtain accurate
        beta, gamma, and breakdown voltage.
        '''

        # check if fit_peak_numbering is executed
        if not 'shifted_pe' in self.df_3d_pts.columns:
            print('One has to run "fit_peak_numbering()" function before calling this method.')
            return
        
        # fit the adc surface
        # get fit parameters from scipy curve fit
        parameters, covariance = optimize.curve_fit(adc_function, [self.df_3d_pts['shifted_pe'], self.df_3d_pts['bias_voltage']], self.df_3d_pts['adc'])

        # store fit results
        self.beta_fit = parameters[0]
        self.beta_err = np.sqrt(covariance[0][0])
        self.breakdown_voltage_fit = parameters[1]
        self.breakdown_voltage_err = np.sqrt(covariance[1][1])
        self.gamma_fit = parameters[2]
        self.gamma_err = np.sqrt(covariance[2][2])

        self.df_3d_pts['refit_adc'] = adc_function([self.df_3d_pts['shifted_pe'], self.df_3d_pts['bias_voltage']], self.beta_fit, self.breakdown_voltage_fit, self.gamma_fit)

        if self.verbose:
            print('Final fitted data:')
            print(self.df_3d_pts)
            print('Refitted breakdown voltage: {:.2f}±{:.2f} V'.format(self.breakdown_voltage_fit, self.breakdown_voltage_err))
            print('Refitted pedestal ADC: {:.2f}±{:.2f}'.format(self.gamma_fit, self.gamma_err))


#------------------------------------------------------------------------------
def adc_function(indep_vars, beta=11.3, vbd=52, gamma=170):
    '''
    The form of ADC as a function of photoelectron number and bias voltage.
    indep_vars[0]: photoelectron
    indep_vars[1]: breakdown voltage
    '''
    return beta*(indep_vars[1]-vbd)*indep_vars[0]+gamma
