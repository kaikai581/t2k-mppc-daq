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
    
    def compare_hamamatsu_lsu(self, dac_offset=False):
        '''
        Make breakdown voltage vs channel plots.
        Plot different measurements on the same plot.
        '''
        if not dac_offset:
            cols = ['position no.', 'Hamamatsu measured Vbr @ 25C', 'LSU Vbr spectrum shape fit|Temp=25C']
        else:
            cols = ['position no.', 'Hamamatsu measured Vbr @ 25C', 'LSU Vbr spectrum shape fit offset corrected|Temp=25C']

        df = self.df[cols]
        df = df.melt('position no.', var_name='measurements',  value_name='breakdown voltage (V)')
        g = sns.relplot(x='position no.', y='breakdown voltage (V)', hue='measurements', data=df, kind='line', marker='o', height=6, aspect=12/6)

        # make output directory
        out_dir = os.path.join('plots', os.path.splitext(os.path.basename(__file__))[0])
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        
        # save plot to file
        outfn = 'compare_only_lsu_hamamatsu_{}dac_offset.jpg'.format('no_' if dac_offset == False else '')
        g.tight_layout()
        g.fig.savefig(os.path.join(out_dir, outfn))

        g.fig.clf()
        g = sns.histplot(data=df, x='breakdown voltage (V)', hue='measurements')
        outfn = 'compare_hist_lsu_hamamatsu_{}dac_offset.jpg'.format('no_' if dac_offset == False else '')
        g.figure.tight_layout()
        g.figure.savefig(os.path.join(out_dir, outfn))
    
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

    def compare_r2(self):
        '''
        Compare the R2 channel by channel from the three different methods.
        1. Peak finding
        2. Spectrum fit
        3. Autocorrelation
        '''
        cols = ['position no.', 'R2 peak finding', 'R2 spectrum fit', 'R2 autocorrelation']
        df = self.df[cols]
        df = df.melt('position no.', var_name='methods',  value_name=r'$R^2$')
        g = sns.relplot(x='position no.', y='$R^2$', hue='methods', data=df, kind='line', marker='o', height=6, aspect=12/6)

        # make output directory
        out_dir = os.path.join('plots', os.path.splitext(os.path.basename(__file__))[0])
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        
        # save plot to file
        outfn = 'R2_comparison.jpg'
        g.tight_layout()
        g.fig.savefig(os.path.join(out_dir, outfn))

        # zoom in y-axis
        g.set(ylim=(0.97, 1.001))
        outfn = 'R2_comparison_zoom_in.jpg'
        g.tight_layout()
        g.fig.savefig(os.path.join(out_dir, outfn))

if __name__ == '__main__':
    my_data = data_csv('data/20210517_mppc_summary_utokyo_pcb_lsu_measurements_feb136_feb13294.csv')
    print(my_data.df.columns)
    my_data.compare_hamamatsu_utokyo_lsu()
    my_data.compare_hamamatsu_utokyo_lsu(dac_offset=True)
    my_data.compare_hamamatsu_lsu(dac_offset=True)
    my_data.compare_r2()