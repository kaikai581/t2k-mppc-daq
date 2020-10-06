#!/usr/bin/env python

from datetime import datetime
import argparse
import dateparser
import matplotlib.pyplot as plt
import os
import pandas as pd

if __name__ == '__main__':
    # command line arguments for specifying input file names
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--thermal_file', type=str, default='../../data/metadata/temperature_sensor_readings.csv')
    parser.add_argument('-w', '--water_file', type=str, default='../../data/metadata/water_circulator_readback.csv')
    parser.add_argument('-s', '--start_datetime', type=dateparser.parse, default='2020/10/5 9:00:00', help='Wrap the date and time in quotes!')
    parser.add_argument('-e', '--end_datetime', type=dateparser.parse, default='2020/10/5 19:00:00', help='Wrap the date and time in quotes!')
    args = parser.parse_args()
    inf_therm = args.thermal_file
    inf_water = args.water_file
    start_datetime = args.start_datetime
    end_datetime = args.end_datetime

    # load dataframe
    df_therm = pd.read_csv(inf_therm, parse_dates=['Datetime'])
    df_therm = df_therm[(df_therm['Datetime'] >= start_datetime) & (df_therm['Datetime'] <= end_datetime)]
    df_therm['Time'] = df_therm['Datetime'].dt.strftime('%H:%M:%S')
    df_water = pd.read_csv(inf_water, parse_dates=['Datetime'])
    df_water = df_water[(df_water['Datetime'] >= start_datetime) & (df_water['Datetime'] <= end_datetime)]
    df_water['Time'] = df_water['Datetime'].dt.strftime('%H:%M:%S')
    
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