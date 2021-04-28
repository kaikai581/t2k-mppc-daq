#!/usr/bin/env python
'''
This script plots the two measurements in scattered plots to identify any possible correlations.
'''

from collections import namedtuple
import argparse
import data_interface
import pandas as pd
import seaborn as sns

CorrVars = namedtuple('CorrVars', 'utokyo lsu')

class scatter_util:
    def __init__(self, fnames: CorrVars, temperature) -> None:
        '''
        Initialize data.
        '''
        self.fnames = fnames
        self.utokyo_data = data_interface.utokyo_data(fnames.utokyo)
        self.lsu_data = data_interface.lsu_data(fnames.lsu)
        self.df_combine = pd.merge(self.utokyo_data.df_data, self.lsu_data.df_data, how='left', on='channel')

        self.temperature = temperature

        self.pcb_owner = None

        # find who owns the PCB
        self.fill_pcb_owner()
    
    def fill_pcb_owner(self):
        if 'lsu_pcb' in str.lower(self.fnames.lsu):
            self.pcb_owner = 'LSU PCB'
            self.pcb_label = 'lsu_pcb'
        else:
            self.pcb_owner = 'UTokyo PCB'
            self.pcb_label = 'utokyo_pcb'
    
    def plot_scatter(self, varnames: CorrVars):
        '''
        Make scatter plots.
        '''
        # make some selection.
        fname_suffix = 'gain'
        if 'gain' in str.lower(varnames.lsu):
            df = self.df_combine[self.df_combine[varnames.lsu] > 1000]
            xlbl = 'UTokyo gain'
            ylbl = 'LSU gain'
        elif 'vbr' in str.lower(varnames.lsu):
            df = self.df_combine[self.df_combine[varnames.lsu] > 50]
            xlbl = 'UTokyo breakdown voltage (V)'
            ylbl = 'LSU breakdown voltage (V)'
            fname_suffix = 'vbd'
        
        # per PI's request, make the axes same range
        minval = min(df[varnames.lsu].min(), df[varnames.utokyo].min())
        maxval = max(df[varnames.lsu].max(), df[varnames.utokyo].max())
        valspan = maxval-minval
        minval = minval-valspan*0.05
        maxval = maxval+valspan*0.05

        figtitle = f'{self.pcb_owner}\ntemperature {temp}°C'
        ax = sns.scatterplot(data=df, x=varnames.utokyo, y=varnames.lsu)
        ax.set_xlim([minval, maxval])
        ax.set_ylim([minval, maxval])
        ax.set_xlabel(xlbl)
        ax.set_ylabel(ylbl)
        ax.set_title(figtitle)
        ax.axline((1, 1), slope=1, color='r', linestyle='--')
        fig = ax.get_figure()
        fig.tight_layout()
        fig.savefig(f'plots/scatter_{self.pcb_label}_{fname_suffix}_temp{self.temperature}.png')
        fig.clf()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--temperature', choices=[20, 25], default=20)
    args = parser.parse_args()
    temp = args.temperature

    fnames_lsu_pcb = CorrVars('data/LSU_PCB_measured_by_UTokyo_crschk_.xlsx', 'data/mppc_summary_lsu_pcb_lsu_measurements.xlsx')
    fnames_utokyo_pcb = CorrVars('data/Utokyo_PCB_Measurement_For crschk_ .xlsx', 'data/mppc_summary_utokyo_pcb_lsu_measurements.csv')
    varname_vbd = CorrVars(f'Utokyo measured Vbr|Temp={temp}C', f'LSU measured Vbr|Temp={temp}C')
    varname_gain = CorrVars(f'Gain @ over_voltage=5V|Temp={temp}C', f'MPPC Gain @ over_voltage=5V|Temp={temp}C')

    # create an instance
    scatter_lsu_pcb = scatter_util(fnames_lsu_pcb, temp)
    scatter_lsu_pcb.plot_scatter(varname_gain)
    scatter_lsu_pcb.plot_scatter(varname_vbd)

    scatter_utokyo_pcb = scatter_util(fnames_utokyo_pcb, temp)
    scatter_utokyo_pcb.plot_scatter(varname_gain)
    scatter_utokyo_pcb.plot_scatter(varname_vbd)