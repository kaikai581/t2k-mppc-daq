#!/usr/bin/env python
'''
This script reads the scope waveform data and looks at the partial sum and amplitude.
'''

import sys
sys.path.append('..')
from draw_waveforms import ScopeWaveform, TwoWaveforms

if __name__ == '__main__':
    pcb_wf = ScopeWaveform('20211102_ch_inj_pcb000.csv', id_name='PCB')
    bb_wf = ScopeWaveform('20211102_ch_inj_breadboard000.csv', id_name='breadboard')
    wf_comp = TwoWaveforms(pcb_wf, bb_wf)
    wf_comp.plot_waveforms_and_partial_sums()
