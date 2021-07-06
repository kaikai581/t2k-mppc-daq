#!/usr/bin/env python

import uproot

class DAQFile:
    def __init__(self, infpn):
        '''
        Constructor in charge of loading a data file.
        '''
        tr_mppc = uproot.open(infpn)['mppc']
        self.df = tr_mppc.arrays(library='pd')

        # store the input file pathname
        self.infpn = infpn
        # store the FEB SN
        self.feb_sn = None

if __name__ == '__main__':
    my_file = DAQFile('../data//root/led/20210615_200000_new_ch24_thr205_gain56_temp22.75_trig24_feb12808_olddaq/mppc_56.5V.root')
    print(my_file.df)