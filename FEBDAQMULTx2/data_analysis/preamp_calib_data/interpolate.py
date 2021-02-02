#!/usr/bin/env python
'''
This is a test script to do interpolation with the gain
measurement data.
By inspecting the results, InterpolatedUnivariateSpline
gives the smoother results. Therefore, this algorithm
will be adopted.
'''

from scipy.interpolate import Rbf, InterpolatedUnivariateSpline
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

if __name__ == '__main__':
    '''
    Test interpolation with numpy and scipy.
    '''
    df_gain_lookup = pd.read_csv('../preamp_calib_data/caen_measurement.csv')

    x_meas = np.array(df_gain_lookup['High Gain'])
    y_meas = np.array(df_gain_lookup['Gain (ch/pC)'])
    x_plot = np.linspace(x_meas.min(), x_meas.max(), 101)
    
    rbf = Rbf(x_meas, y_meas)
    y_rbf = rbf(x_plot)

    ius = InterpolatedUnivariateSpline(x_meas, y_meas)
    y_ius = ius(x_plot)

    plt.plot(x_meas, y_meas, 'bo', label='measured')
    plt.plot(x_plot, y_rbf, 'g', label='RBF smoothing', alpha=.75)
    plt.plot(x_plot, y_ius, 'y', label='spline', alpha=.9)
    plt.legend()
    plt.ylabel('gain (ADC/pC)')
    plt.xlabel('preamp gain setting')

    plt.savefig('adc_per_charge_vs_preamp_gain.png')
