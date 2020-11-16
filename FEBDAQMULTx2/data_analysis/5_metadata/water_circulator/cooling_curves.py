#!/usr/bin/env python

from datetime import datetime
import argparse
import dateparser
import matplotlib.pyplot as plt
import os
import pandas as pd
import statistics
import sys

def single_plot(df_therm, df_water):
    # plot readings from all sensors
    for i in range(5):
        plt.plot(df_therm['Time'], df_therm['T{}'.format(i)], 'o', markersize=2, alpha=50, label='sensor {}'.format(i))
    
    # plot water circulator setpoint readout
    plt.plot(df_water['Time'], df_water['Internal Temperature'], '*', label='setpoint readback', fillstyle='none')

    # decorations
    plt.ylim(bottom=min(list(df_water['Internal Temperature'])+list(df_therm['T0'])+list(df_therm['T1'])+list(df_therm['T2'])+list(df_therm['T3'])+list(df_therm['T4']))*.7)
    plt.legend()
    plt.grid(axis='y')
    plt.xlabel('wall time')
    plt.ylabel(u'temperature (℃)')
    plt.xticks(rotation='vertical', ticks=df_therm[df_therm.index % (len(df_therm)//20) == 0]['Time'])
    plt.tight_layout()

    # save to file
    out_dir = 'plots'
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    plt.savefig(os.path.join(out_dir, '{}-{}.jpg'.format(df_therm['Datetime'].dt.strftime('%m-%d-%Y_%H-%M-%S').iloc[0], df_therm['Datetime'].dt.strftime('%H-%M-%S').iloc[-1])))

def two_axes_plot(df_therm, df_water, more_info=False):
    # make two subplots
    _, axs = plt.subplots(2, sharex=True)

    # plot readings from thermal sensors
    l_s = []
    for i in range(5):
        l1, = axs[0].plot(df_therm['Time'], df_therm['T{}'.format(i)], 'o', markersize=2, alpha=50, label='sensor {}'.format(i))
        l_s.append(l1)
    
    # plot water circulator setpoint readout
    l2, = axs[1].plot(df_water['Time'], df_water['Internal Temperature'], '*', label='setpoint readback', fillstyle='none')
    l_s.append(l2)

    # decorations
    for i in range(2):
        axs[i].grid(axis='both')
        axs[i].set_ylabel(u'temperature (℃)')
    axs[1].set_xlabel('wall time')
    axs[1].set_ylabel(u'circulator readback\ntemperature (℃)')
    tot_labels = ['sensor {}'.format(i) for i in range(5)] + ['setpoint readback']
    axs[0].legend(handles = l_s, labels=tot_labels, loc='upper left', 
                  bbox_to_anchor=(1.05, 1), fancybox=False, shadow=False)
    plt.xticks(rotation='vertical', ticks=df_therm[df_therm.index % (len(df_therm)//10) == 0]['Time'])
    plt.tight_layout()
    
    # write some more information to the plots
    if more_info:
        df_therm_last = df_therm[['T0','T1','T2','T3','T4']].iloc[-1].tolist()
        mean_temp = statistics.mean(df_therm_last)
        spread = max(df_therm_last)-min(df_therm_last)
        axs[0].annotate('steady state\naverage:{:.2f}℃\n$T_{{max}}-T_{{min}}$:{:.2f}℃'.format(mean_temp, spread), xy=(0.6, 0.5), xycoords='axes fraction')
        axs[1].annotate('steady state\nsetpoint readback\n{:.2f}℃'.format(df_water['Internal Temperature'].iloc[-1]), xy=(0.6, 0.5), xycoords='axes fraction')

    # save to file
    out_dir = 'plots'
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    plt.savefig(os.path.join(out_dir, '{}-{}_2axes.jpg'.format(df_therm['Datetime'].dt.strftime('%m-%d-%Y_%H-%M-%S').iloc[0], df_therm['Datetime'].dt.strftime('%H-%M-%S').iloc[-1])))

if __name__ == '__main__':
    # command line arguments for specifying input file names
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--thermal_file', type=str, default='../../data/metadata/temperature_sensor_readings.csv')
    parser.add_argument('-w', '--water_file', type=str, default='../../data/metadata/water_circulator_readback.csv')
    parser.add_argument('-s', '--start_datetime', type=dateparser.parse, default='2020/10/5 9:00:00', help='Wrap the date and time in quotes!')
    parser.add_argument('-e', '--end_datetime', type=dateparser.parse, default=datetime.now(), help='Wrap the date and time in quotes!')
    parser.add_argument('--two_axes', action='store_true', help='Separate the circulator temperature from those of the thermal sensors.')
    parser.add_argument('--list_dates', action='store_true', help='List all existing dates in the database.')
    parser.add_argument('--annotate', action='store_true', help='Show more information on the result plots.')
    args = parser.parse_args()
    inf_therm = args.thermal_file
    inf_water = args.water_file
    start_datetime = args.start_datetime
    end_datetime = args.end_datetime
    two_axes = args.two_axes

    # load dataframe
    df_therm = pd.read_csv(inf_therm, parse_dates=['Datetime'])
    df_therm = df_therm[(df_therm['Datetime'] >= start_datetime) & (df_therm['Datetime'] <= end_datetime)]
    df_therm['Date'] = df_therm['Datetime'].dt.strftime('%Y-%m-%d')
    df_therm['Time'] = df_therm['Datetime'].dt.strftime('%H:%M:%S')
    df_water = pd.read_csv(inf_water, parse_dates=['Datetime'])
    df_water = df_water[(df_water['Datetime'] >= start_datetime) & (df_water['Datetime'] <= end_datetime)]
    df_water['Date'] = df_water['Datetime'].dt.strftime('%Y-%m-%d')
    df_water['Time'] = df_water['Datetime'].dt.strftime('%H:%M:%S')
    
    # If listing dates is requested, show the available dates in the database and quit.
    if args.list_dates:
        date_therm = df_therm.Date.unique()
        date_water = df_water.Date.unique()
        print('Dates of data in the database:')
        for date in sorted(list(set().union(date_therm, date_water))):
            print(date)
        sys.exit(0)

    if not two_axes:
        single_plot(df_therm, df_water)
    else:
        two_axes_plot(df_therm, df_water, args.annotate)