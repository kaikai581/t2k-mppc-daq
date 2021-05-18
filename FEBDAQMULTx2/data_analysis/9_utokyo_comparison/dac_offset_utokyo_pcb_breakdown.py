#!/usr/bin/env python
'''
This script compares the breakdown voltage measurements of the LSU MPPC-PCB from LSU, UTotyo and Hamamatsu.
'''

import os
import pandas as pd
import seaborn as sns

class data_csv:
    def __init__(self, infpn) -> None:
        self.df = pd.read_csv(infpn)
    
    def compare_hamamatsu_utokyo_lsu(self, dac_offset=False):
        '''
        Make breakdown voltage vs channel plots.
        Plot different measurements on the same plot.
        '''
        if not dac_offset:
            cols = ['position no.', 'Hamamatsu measured Vbr @ 25C', 'Utokyo measured Vbr|Temp=25C', 'LSU Vbr peak fit|Temp=25C',
                      'LSU Vbr autocorrelation|Temp=25C', 'LSU Vbr spectrum shape fit|Temp=25C']
        else:
            cols = ['position no.', 'Hamamatsu measured Vbr @ 25C', 'Utokyo measured Vbr|Temp=25C', 'LSU Vbr peak fit offset corrected|Temp=25C',
                      'LSU Vbr autocorrelation offset corrected|Temp=25C', 'LSU Vbr spectrum shape fit offset corrected|Temp=25C']

        df = self.df[cols]
        df = df.melt('position no.', var_name='measurements',  value_name='breakdown voltage (V)')
        g = sns.relplot(x='position no.', y='breakdown voltage (V)', hue='measurements', data=df, kind='line', marker='o', height=6, aspect=12/6)

        # make output directory
        out_dir = os.path.join('plots', os.path.splitext(os.path.basename(__file__))[0])
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        
        # save plot to file
        outfn = 'compare_{}dac_offset.jpg'.format('no_' if dac_offset == False else '')
        g.tight_layout()
        g.fig.savefig(os.path.join(out_dir, outfn))


if __name__ == '__main__':
    my_data = data_csv('data/20210517_mppc_summary_utokyo_pcb_lsu_measurements_feb136_feb13294.csv')
    print(my_data.df.columns)
    my_data.compare_hamamatsu_utokyo_lsu()
    my_data.compare_hamamatsu_utokyo_lsu(dac_offset=True)