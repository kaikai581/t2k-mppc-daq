#!/usr/bin/env python

'''
Base on the example code found in this GitHub repository.
https://github.com/larks/AFG3252-Automation
The example code is for controling Tektronix function generator AFG3252.
'''

import vxi11

class PowerSystem:
    '''
    This is a virtual interface class to define the functions for controlling
    the power unit.
    '''
    def __init__(self, host):
        pass

    def power_off(self, ch):
        pass

    def power_on(self, ch):
        pass

    def set_voltage(self, ch, v):
        pass

class N6700B(PowerSystem):
    '''
    This is the concrete class of the Agilent N6700B power system.
    Currently the IP reads 169.254.130.161.
    '''
    def __init__(self, host):
        try:
            self.conn = vxi11.Instrument(host)
            self.dType = self.conn.ask('*IDN?')
            print(self.dType)
        except Exception as e:
            print(e)
    
    def power_off(self, ch):
        self.conn.write('OUTP OFF,(@{})'.format(ch))
    
    def power_on(self, ch):
        self.conn.write('OUTP ON,(@{})'.format(ch))
    
    def set_voltage(self, ch, v):
        self.conn.write('VOLT {},(@{})'.format(v, ch))
