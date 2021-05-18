#!/usr/bin/env python
'''
This script compares the MPPC gain measurements of the UTokyo MPPC-PCB from LSU and UTotyo.
'''

from data_interface import utokyo_data, lsu_data
from pandas.plotting import table
import matplotlib.pyplot as plt
import numpy as np
import os

if __name__ == '__main__':
    # load utokyo measurements and lsu measurements of the LSU board
    my_utokyo_data = utokyo_data('data/Utokyo_PCB_Measurement_For crschk_ .xlsx')
    # my_lsu_data = lsu_data('data/mppc_summary_lsu_pcb_lsu_measurements.xlsx')
    my_lsu_data = lsu_data('data/mppc_summary_utokyo_pcb_lsu_measurements.csv')

    # make output folder
    out_dir = 'plots'
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # make plots:
    # LSU and UTokyo individually
    # LSU and UTokyo together
    # LSU and UTokyo difference

    # loop for two temperatures
    for temp in [20, 25]:
        # LSU Vbd
        # if temp == 20: # only 20 degree C data for now
        fig, (ax_lsu20, axhist, ax_table) = plt.subplots(ncols=3, sharey=True,
                                    gridspec_kw={"width_ratios" : [3,1,2], "wspace" : 0})
        ax_table.axis("off")
        fig.set_size_inches(10, 5)
        df = my_lsu_data.df_data[['channel','MPPC Gain @ over_voltage=5V|Temp={}C'.format(temp)]].dropna()
        ax_lsu20.errorbar(x=df['channel'], y=df['MPPC Gain @ over_voltage=5V|Temp={}C'.format(temp)], fmt='o')
        ax_lsu20.grid('both')
        ax_lsu20.set_title('UTokyo PCB\nMPPC Gain\nLSU, temperature {}°C'.format(temp))
        ax_lsu20.set_xlabel('channel')
        ax_lsu20.set_ylabel('MPPC gain')
        ax_lsu20.figure.tight_layout()
        # LSU Vbd histogram
        axhist.hist(df['MPPC Gain @ over_voltage=5V|Temp={}C'.format(temp)], bins='auto', orientation='horizontal', histtype='step')
        axhist.tick_params(axis='y', left=False)
        axhist.grid(axis='y')
        results = df.describe()['MPPC Gain @ over_voltage=5V|Temp={}C'.format(temp)]
        the_table = table(ax_table, np.round(results, 0), loc="upper right", colWidths=[0.7])
        the_table.scale(1, 2)
        the_table.auto_set_font_size(False)
        the_table.set_fontsize(15)
        fig.savefig(os.path.join(out_dir, 'mppc_gain_utokyo_pcb_lsu_meas_{}C.png'.format(temp)), bbox_inches='tight')

        # UTokyo Vbd
        fig, (ax_utokyo20, axhist, ax_table) = plt.subplots(ncols=3, sharey=True,
                                    gridspec_kw={"width_ratios" : [3,1,2], "wspace" : 0})
        ax_table.axis("off")
        fig.set_size_inches(10, 5)
        ax_utokyo20.scatter(x=my_utokyo_data.df_data['channel'], y=my_utokyo_data.df_data['Gain @ over_voltage=5V|Temp={}C'.format(temp)])
        ax_utokyo20.grid('both')
        ax_utokyo20.set_xlabel('channel')
        ax_utokyo20.set_ylabel('MPPC gain')
        ax_utokyo20.set_title('UTokyo PCB\nMPPC Gain\nUTokyo, temperature {}°C'.format(temp))
        axhist.hist(my_utokyo_data.df_data['Gain @ over_voltage=5V|Temp={}C'.format(temp)], bins='auto', orientation='horizontal', histtype='step')
        axhist.tick_params(axis='y', left=False)
        axhist.grid(axis='y')
        results = my_utokyo_data.df_data.describe()['Gain @ over_voltage=5V|Temp={}C'.format(temp)]
        the_table = table(ax_table, np.round(results, 0), loc="upper right", colWidths=[0.7])
        the_table.scale(1, 2)
        the_table.auto_set_font_size(False)
        the_table.set_fontsize(15)
        fig.tight_layout()
        fig.savefig(os.path.join(out_dir, 'mppc_gain_utokyo_pcb_utokyo_meas_{}C.png').format(temp))

        # UTokyo Vbd and LSU Vbd
        _, ax_lsu20_utokyo_20 = plt.subplots()
        ax_lsu20_utokyo_20.scatter(x=my_utokyo_data.df_data.channel, y=my_utokyo_data.df_data['Gain @ over_voltage=5V|Temp={}C'.format(temp)], c='r', label='UTokyo')
        ax_lsu20_utokyo_20.errorbar(x=df.channel, y=df['MPPC Gain @ over_voltage=5V|Temp={}C'.format(temp)], c='purple', label='LSU', fmt='o')
        ax_lsu20_utokyo_20.legend()
        ax_lsu20_utokyo_20.grid('both')
        ax_lsu20_utokyo_20.set_xlabel('channel')
        ax_lsu20_utokyo_20.set_ylabel('MPPC gain')
        ax_lsu20_utokyo_20.set_title('UTokyo PCB\nMPPC Gain\ntemperature {}°C'.format(temp))
        ax_utokyo20.figure.tight_layout()
        ax_lsu20_utokyo_20.figure.savefig(os.path.join(out_dir, 'mppc_gain_utokyo_pcb_lsu_meas_utokyo_meas_{}C.png'.format(temp)))

        # difference
        fig, ax_lsu20_diff_utokyo_20 = plt.subplots()
        ax_lsu20_diff_utokyo_20.scatter(x=my_utokyo_data.df_data.channel, y=my_lsu_data.df_data['MPPC Gain @ over_voltage=5V|Temp={}C'.format(temp)]-my_utokyo_data.df_data['Gain @ over_voltage=5V|Temp={}C'.format(temp)])
        ax_lsu20_diff_utokyo_20.grid('both')
        ax_lsu20_diff_utokyo_20.set_xlabel('channel')
        ax_lsu20_diff_utokyo_20.set_ylabel(r'MPPC gain difference, LSU$-$UTokyo (V)')
        ax_lsu20_diff_utokyo_20.set_title('UTokyo PCB\nMPPC Gain\n'+r'LSU$-$UTokyo, temperature {}°C'.format(temp))
        fig.tight_layout()
        fig.savefig(os.path.join(out_dir, 'mppc_gain_utokyo_pcb_lsu_meas_diff_utokyo_meas_{}C.png'.format(temp)))

        # ratio
        fig, (ax_lsu20_ratio_utokyo_20, axhist, ax_table) = plt.subplots(ncols=3, sharey=True,
                                    gridspec_kw={"width_ratios" : [3,1,2], "wspace" : 0})
        ax_table.axis('off')
        fig.set_size_inches(10, 5)
        df_ratio = (df['MPPC Gain @ over_voltage=5V|Temp={}C'.format(temp)]/my_utokyo_data.df_data['Gain @ over_voltage=5V|Temp={}C'.format(temp)]).dropna()
        ax_lsu20_ratio_utokyo_20.scatter(x=[i for i in range(len(df_ratio))], y=df_ratio)
        ax_lsu20_ratio_utokyo_20.grid('both')
        ax_lsu20_ratio_utokyo_20.set_xlabel('channel')
        ax_lsu20_ratio_utokyo_20.set_ylabel(r'MPPC gain ratio, LSU$/$UTokyo')
        ax_lsu20_ratio_utokyo_20.set_title('UTokyo PCB\nMPPC Gain\n'+r'LSU$/$UTokyo, temperature {}°C'.format(temp))
        axhist.hist(df_ratio, bins='auto', orientation='horizontal', histtype='step')
        axhist.tick_params(axis='y', left=False)
        axhist.grid(axis='y')
        results = df_ratio.describe()
        the_table = table(ax_table, np.round(results, 2), loc="upper right", colWidths=[0.7])
        the_table.scale(1, 2)
        the_table.auto_set_font_size(False)
        the_table.set_fontsize(15)
        fig.tight_layout()
        fig.savefig(os.path.join(out_dir, 'mppc_gain_utokyo_pcb_lsu_meas_ratio_utokyo_meas_{}C.png'.format(temp)))

        # # LSU Vbd
        # ax_lsu20 = my_lsu_data.df_data.plot.scatter(x='channel', y='MPPC Gain @ over_voltage=5V|Temp={}C'.format(temp))
        # ax_lsu20.grid('both')
        # ax_lsu20.set_title('MPPC Gain\nLSU, temperature {}°C'.format(temp))
        # ax_lsu20.figure.tight_layout()
        # ax_lsu20.figure.savefig(os.path.join(out_dir, 'mppc_gain_utokyo_pcb_lsu_meas_{}C.png'.format(temp)))

        # # UTokyo Vbd
        # ax_utokyo20 = my_utokyo_data.df_data.plot.scatter(x='channel', y='Gain @ over_voltage=5V|Temp={}C'.format(temp))
        # ax_utokyo20.grid('both')
        # ax_utokyo20.set_title('MPPC Gain\nUTokyo, temperature {}°C'.format(temp))
        # ax_utokyo20.figure.tight_layout()
        # ax_utokyo20.figure.savefig(os.path.join(out_dir, 'mppc_gain_utokyo_pcb_utokyo_meas_{}C.png').format(temp))

        # # UTokyo Vbd and LSU Vbd
        # _, ax_lsu20_utokyo_20 = plt.subplots()
        # ax_lsu20_utokyo_20.scatter(x=my_utokyo_data.df_data.channel, y=my_utokyo_data.df_data['Gain @ over_voltage=5V|Temp={}C'.format(temp)], c='r', label='UTokyo')
        # ax_lsu20_utokyo_20.scatter(x=my_lsu_data.df_data.channel, y=my_lsu_data.df_data['MPPC Gain @ over_voltage=5V|Temp={}C'.format(temp)], c='purple', label='LSU')
        # ax_lsu20_utokyo_20.legend()
        # ax_lsu20_utokyo_20.grid('both')
        # ax_lsu20_utokyo_20.set_xlabel('channel')
        # ax_lsu20_utokyo_20.set_ylabel('MPPC gain')
        # ax_lsu20_utokyo_20.set_title('MPPC Gain\ntemperature {}°C'.format(temp))
        # ax_lsu20_utokyo_20.figure.tight_layout()
        # ax_lsu20_utokyo_20.figure.savefig(os.path.join(out_dir, 'mppc_gain_utokyo_pcb_lsu_meas_utokyo_meas_{}C.png'.format(temp)))

        # # difference
        # _, ax_lsu20_diff_utokyo_20 = plt.subplots()
        # ax_lsu20_diff_utokyo_20.scatter(x=my_utokyo_data.df_data.channel, y=my_lsu_data.df_data['MPPC Gain @ over_voltage=5V|Temp={}C'.format(temp)]-my_utokyo_data.df_data['Gain @ over_voltage=5V|Temp={}C'.format(temp)])
        # ax_lsu20_diff_utokyo_20.grid('both')
        # ax_lsu20_diff_utokyo_20.set_xlabel('channel')
        # ax_lsu20_diff_utokyo_20.set_ylabel(r'MPPC gain, LSU$-$UTokyo')
        # ax_lsu20_diff_utokyo_20.set_title('MPPC Gain\n'+r'LSU$-$UTokyo, temperature {}°C'.format(temp))
        # ax_lsu20_diff_utokyo_20.figure.tight_layout()
        # ax_lsu20_diff_utokyo_20.figure.savefig(os.path.join(out_dir, 'mppc_gain_utokyo_pcb_lsu_meas_diff_utokyo_meas_{}C.png'.format(temp)))