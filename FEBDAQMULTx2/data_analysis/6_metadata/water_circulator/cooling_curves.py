#!/usr/bin/env python

from datetime import datetime
import argparse
import matplotlib.pyplot as plt
import os
import pandas as pd

if __name__ == '__main__':
    # command line arguments for specifying input file names
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--thermal_file', type=str, default='../../data/metadata/temperature_sensor_readings.csv')
    parser.add_argument('-w', '--water_file', type=str, default='../../data/metadata/water_circulator_readback.csv')
    args = parser.parse_args()
    inf_therm = args.thermal_file
    inf_water = args.water_file

    # load dataframe
    df_therm = pd.read_csv(inf_therm, parse_dates=['Datetime'])
    df_therm['Time'] = df_therm['Datetime'].dt.strftime('%H:%M:%S')
    df_water = pd.read_csv(inf_water, parse_dates=['Datetime'])
    df_water['Time'] = df_water['Datetime'].dt.strftime('%H:%M:%S')
    
    # plot readings from all sensors
    for i in range(5):
        plt.plot(df_therm['Time'], df_therm['T{}'.format(i)], 'o', markersize=2, alpha=50, label='sensor {}'.format(i))
    
    # plot water circulator setpoint readout
    plt.plot(df_water['Time'], df_water['Internal Temperature'], '*', label='setpoint readback', fillstyle='none')

    # decorations
    plt.ylim(bottom=min(list(df_water['Internal Temperature'])+list(df_therm['T0'])+list(df_therm['T1'])+list(df_therm['T2'])+list(df_therm['T3'])+list(df_therm['T4']))*.8)
    plt.legend()
    plt.grid(axis='y')
    plt.xlabel('wall time')
    plt.ylabel(u'temperature (℃)')
    plt.xticks(rotation='vertical', ticks=df_therm[df_therm.index % 10 == 0]['Time'])
    plt.tight_layout()

    # save to file
    out_dir = 'plots'
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    plt.savefig(os.path.join(out_dir, '{}.jpg'.format(df_therm['Datetime'].dt.strftime('%m-%d-%Y_%H-%M-%S')[0])))