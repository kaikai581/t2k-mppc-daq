#!/usr/bin/env python

import platform
import re
import serial
import pandas as pd
from numpy import flip, array
from scipy.interpolate import InterpolatedUnivariateSpline


class MPPCTEMPSENSOR:
    '''
    This is the API class for the internal temperature sensors of an MPPC-PCB.
    The interface is RS232.
    '''

    def __init__(self):
        try:
            port_name = '/dev/ttyACM0'
            if platform.system() == 'Windows':
                port_name = 'COM1'
            self.conn = serial.Serial(
                port=port_name,
                baudrate=115200,
                parity=serial.PARITY_NONE,
                bytesize=serial.EIGHTBITS,
                timeout=None
            )
        except Exception as e:
            print(e)
        #Create serial connection
        self.conn = serial.Serial(
                port=port_name,
                baudrate=9600,
            )
        #Load calibration file 
        self.adc2temp = pd.read_csv('./temp_calib.csv')
        x_meas = flip(array(self.adc2temp['ADC']))
        y_meas = flip(array(self.adc2temp['temperatuer (°C)']))

        self.ius = InterpolatedUnivariateSpline(x_meas, y_meas)

    
    def __del__(self):
        try:
            self.conn.flush()
            self.conn.close()
        except Exception as e:
            print(e)

    def process_readout(self, rb):
        temps = {'ADC0': 0.0,'ADC1': 0.0 , 'B0': -1.0 ,'B1': -1.0}
        adc1 = float(rb.split(',')[0])
        adc2 = float(rb.split(',')[1])
        temps['ADC0'] = adc1
        temps['ADC1'] = adc2
        temp_b0 = float(self.ius(adc1))
        temp_b1 = float(self.ius(adc2))
        temps['B0'] = temp_b0
        temps['B1'] = temp_b1
        #
        return temps

    def query_temperature(self):
        rb = self.conn.readline().decode('utf-8')
        temp_dict = self.process_readout(rb)
        # self.conn.write('run 0\r'.encode())
        return temp_dict
