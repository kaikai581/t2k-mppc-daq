#!/usr/bin/env python
'''
This script is to test the implementation of the new peak numbering algorithm utilizing the full functional form between ADC, bias voltage, and photoelectron.
'''

# my own modules
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../utilities'))
import peak_numbering

# redirect output engine to avoid x11 errors
import matplotlib
matplotlib.use('Agg')

if __name__ == '__main__':
    # Due to the current DAQ implementation, the file names have "dark rate" in them. However, they are actually LED runs.
    channel = 0
    infpns = [
        '../data/root/led_1ch_trig_for_dac_calib/20210301_112158_led_gain52_ch0-31_feb170_volt57_thr205/20210301_112158_dark_rate_feb0_ch{}_thr205.0.root'.format(channel),
        '../data/root/led_1ch_trig_for_dac_calib/20210301_124140_led_gain52_ch0-31_feb170_volt58_thr205/20210301_124140_dark_rate_feb0_ch{}_thr205.0.root'.format(channel),
        '../data/root/led_1ch_trig_for_dac_calib/20210301_142803_led_gain52_ch0-31_feb170_volt59_thr205/20210301_142803_dark_rate_feb0_ch{}_thr205.0.root'.format(channel),
        '../data/root/led_1ch_trig_for_dac_calib/20210301_163042_led_gain52_ch0-31_feb170_volt60_thr205/20210301_163042_dark_rate_feb0_ch{}_thr205.0.root'.format(channel)
    ]
    my_pn = peak_numbering.fitting_algorithm(infpns, 1, channel, verbose=True, outpn='plots/peak_numbering_test/breakdown_voltage')
    my_pn.fit_peak_numbering(shift_limit=4)
    my_pn.refit_physics_parameters()