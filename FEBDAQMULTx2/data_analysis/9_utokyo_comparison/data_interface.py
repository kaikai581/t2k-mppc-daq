#!/usr/bin/env python
'''
This script implements the data interface to the LSU and UTotyo excel files.
'''

import os
import pandas as pd

class utokyo_data:
    def __init__(self, infpn):
        '''
        This constructor tries to load the excel file provided by UTokyo directly.

        Column names are as follows.
        ['Hamamatsu measured Vbr', 'Utokyo measured Vbr|Temp=25C',
         'Utokyo measured Vbr|Temp=20C', 'Gain @ over_voltage=5V|Temp=25C',
         'Gain @ over_voltage=5V|Temp=20C',
         'Noise Rate @ over_voltage=5V|Temp=25C',
         'Noise Rate @ over_voltage=5V|Temp=20C',
         'Cross Talk @ over_voltage=5V|Temp=25C',
         'Cross Talk @ over_voltage=5V|Temp=20C']
        '''
        self.df_data = pd.read_excel(infpn, index_col=0, sheet_name=1)
        self.df_data['channel'] = range(64)

class lsu_data:
    def __init__(self, infpn):
        '''
        This constructor loads the data file storing LSU measurements.

        Column names are as follows.
        ['Hamamatsu measured Vbr', 'LSU measured Vbr|Temp=25C',
         'LSU measured Vbr|Temp=20C',
         'Uncalibrated Gain @ over_voltage=5V|Temp=25C',
         'MPPC Gain @ over_voltage=5V|Temp=25C',
         'Uncalibrated Gain @ over_voltage=5V|Temp=20C',
         'MPPC Gain @ over_voltage=5V|Temp=20C',
         'Noise Rate @ bias_voltage=57V|Temp=25C',
         'Noise Rate @ bias_voltage=57V|Temp=20C',
         'Cross Talk @ over_voltage=5V|Temp=25C',
         'Cross Talk @ over_voltage=5V|Temp=20C', 'Unnamed: 12',
         'calibration factor from charge injection\n(electrons/ADC)']
        '''
        # self.df_data = pd.read_excel(infpn, index_col=0, sheet_name='LSU Meausred PCB v1')
        if os.path.splitext(infpn)[-1] == '.xlsx':
            self.df_data = pd.read_excel(infpn, index_col=0, sheet_name=0)
        if os.path.splitext(infpn)[-1] == '.csv':
            self.df_data = pd.read_csv(infpn, index_col=0)
        self.df_data['channel'] = range(64)


if __name__ == '__main__':
    '''
    Test code for the class implementation.
    '''
    my_utokyo_data = utokyo_data('data/Utokyo_Measurement_For crschk_ .xlsx')
    print(my_utokyo_data.df_data.columns)

    my_lsu_data = lsu_data('data/mppc_summary_lsu_pcb_lsu_measurements.xlsx')
    print(my_lsu_data.df_data.columns)