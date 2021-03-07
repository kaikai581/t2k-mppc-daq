#!/usr/bin/env python
'''
This script aims to visualize the ADC graph as a function of bias voltage and photoelectron.
The functional form of ADC is,
ADC = beta * (V-Vbd) * PE + gamma
, where the independent variables are V, bias voltage, and PE, photoelectron.
Besides, beta is a proportional constant, Vbd the breakdown voltage, and gamma the ADC offset at 0 PE.
'''

# my own modules
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../utilities'))
import common_tools

# redirect output engine to avoid x11 errors
import matplotlib
matplotlib.use('Agg')

from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np

def adc_value(pe, v, beta=11.3, vbd=52, gamma=170):
    return beta*(v-vbd)*pe+gamma

if __name__ == '__main__':
    fig = plt.figure(num=1, clear=True)
    ax = fig.add_subplot(1, 1, 1, projection='3d')

    # create the meshgrid with corresponding ranges
    (x, y) = np.meshgrid(np.linspace(0, 8, 9), np.linspace(51, 61, 11))
    z = adc_value(x, y)
    
    # plot the surface
    ax.plot_surface(x, y, z, cmap=cm.hot)
    ax.set(xlabel='photoelectron', ylabel='bias voltage (V)', zlabel='ADC', title='ADC as a function of #PE and bias voltage')

    fig.tight_layout()

    common_tools.easy_save_to(plt, 'plots/draw_adc_surface/adc_surface.png')