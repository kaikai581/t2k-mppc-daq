#!/usr/bin/env python

import platform
import re
import serial
import pandas as pd
from numpy import flip, array
from scipy.interpolate import InterpolatedUnivariateSpline
from scipy.stats import linregress


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
                baudrate=9600,
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
                parity=serial.PARITY_NONE,
                bytesize=serial.EIGHTBITS,
                timeout=None
            )
        #Load calibration file 
        self.adc2temp = pd.read_csv('mppc-temperature-sensor/temp_calib_08162022.csv')
        x_meas = flip(array(self.adc2temp['ADC']))
        y_meas = flip(array(self.adc2temp['Temperature (°C)']))

        self.line = linregress(x_meas, y_meas)

    
    def __del__(self):
        try:
            self.conn.flush()
            self.conn.close()
        except Exception as e:
            print(e)

    def process_readout(self, rb):
        temps = {'ADC0': 0.0,'ADC1': 0.0 ,'ADC2': 0.0 ,'ADC3': 0.0 , 'B0': -1.0 ,'B1': -1.0, 'B2': -1.0 ,'B3': -1.0}
        adc1 = float(rb.split(',')[0])
        adc2 = float(rb.split(',')[1])
        adc3 = float(rb.split(',')[2])
        adc4 = float(rb.split(',')[3])
        
        temps['ADC0'] = adc1
        temps['ADC1'] = adc2
        temps['ADC2'] = adc3
        temps['ADC3'] = adc4
        s = self.line.slope
        b = self.line.intercept
        temp_b0 = round(float(s*(adc1) + b),2)
        temp_b1 = round(float(s*(adc2) + b),2)
        temp_b2 = round(float(s*(adc3) + b),2)
        temp_b3 = round(float(s*(adc4) + b),2)
        
        temps['B0'] = temp_b0
        temps['B1'] = temp_b1
        temps['B2'] = temp_b2
        temps['B3'] = temp_b3
        
        return temps

    def query_temperature(self):
        rb = self.conn.readline().decode('utf-8')
        temp_dict = self.process_readout(rb)
        # self.conn.write('run 0\r'.encode())
        return temp_dict
