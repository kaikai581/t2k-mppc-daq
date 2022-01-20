#!/usr/bin/env python
'''
This script takes the output voltage from the scope and
calculate the charge out of it.
'''

import sys
sys.path.append('..')
from draw_waveforms import ScopeWaveform

if __name__ == '__main__':
    pcb_wf = ScopeWaveform('20211102_ch_inj_pcb000.csv', id_name='PCB')
    print(pcb_wf.get_mean_charge_in_window())
