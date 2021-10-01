#!/usr/bin/env python
'''
This script takes the measured root file where charge is injected to one channel.
Input data format is
<channel_number>.root
'''

import argparse
import os
import uproot

class injection_data:
    def __init__(self, infpns):
        self.infpns = infpns
        self.single_ch_dfs = dict()

        self.load_data_to_dfs()
    
    def load_data_to_dfs(self):
        for infpn in self.infpns:
            try:
                self.single_ch_dfs[self.get_ch_from_infpn(infpn)] = uproot.open(infpn)['mppc'].arrays(library='pd')
            except:
                pass
        print(self.single_ch_dfs.keys())

    def get_ch_from_infpn(self, s):
        return int(os.path.splitext(os.path.basename(s))[0].lstrip('ch'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_files', type=str, nargs='*')
    args = parser.parse_args()

    my_injection = injection_data(infpns=args.input_files)
