#!/usr/bin/env python

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from peak_cleanup import PeakCleanup
from scipy import optimize
from scipy.signal import find_peaks
from sympy import Point2D, Line2D
import argparse
import copy
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random

class MPPCLine:
    def __init__(self, infpn, feb_id, ch):
        '''
        The constructor is responsible for finding peak positions given
        a filename and a channel ID.
        '''
        try:
            df = pd.read_hdf(infpn, key='mppc')
        except:
            print('Error reading file {}'.format(infpn))
            return

        # make the plot of a channel
        chvar = 'chg[{}]'.format(ch)
        # select data of the specified board
        df_1b = df[df['feb_num'] == feb_id]
        # make histogram and find peaks
        bins = np.linspace(0, 4100, 821)
        _, axs = plt.subplots(2)
        histy, bin_edges, _ = axs[0].hist(df_1b[chvar], bins=bins, histtype='step')
        peaks, _ = find_peaks(histy, prominence=300)
        
        # release memory
        plt.close()

        # store processed data
        pc = PeakCleanup(list(np.array(bin_edges)[peaks]))
        pc.remove_outlier_by_relative_interval()
        self.peak_adcs = pc.peak_adcs
        self.points = [Point2D(i, self.peak_adcs[i]) for i in range(len(self.peak_adcs))]

        # fit a line to the points
        x_try = np.array([p.x for p in self.points]).astype(float)
        y_try = np.array([p.y for p in self.points]).astype(float)
        self.coeff = np.polyfit(x_try, y_try, 1)
        self.line = Line2D(Point2D(0, self.coeff[1]), slope=self.coeff[0])

        # bias voltage
        self.voltage = self.voltage_from_filename(infpn)
    
    def shift_peak_id(self, x_shift):
        '''
        This method shifts all peak position assignments to the left or right
        by x_shift amount. It also shifts the fitted line by the same amount.
        '''
        self.points = [Point2D(i+x_shift, self.peak_adcs[i]) for i in range(len(self.peak_adcs))]
        self.coeff[1] -= self.coeff[0]*x_shift
        self.line = Line2D(Point2D(0, self.coeff[1]), slope=self.coeff[0])

    def voltage_from_filename(self, fn):
        for tmpstr in fn.split('_'):
            if 'volt' in tmpstr:
                return float(tmpstr.lstrip('volt'))
        return 0.

def average_distance(z, *params):
    shifted_lines = copy.deepcopy(params)
    # first, shift the lines
    assert(len(shifted_lines) == len(z)+1)
    for i in range(len(z)):
        shifted_lines[i+1].shift_peak_id(z[i])
    # then, calculate the intersection points
    int_pts = []
    for i in range(len(shifted_lines)):
        for j in range(i+1, len(shifted_lines)):
            l1 = shifted_lines[i].line
            l2 = shifted_lines[j].line
            pt = l1.intersection(l2)
            if pt:
                int_pts.append(pt[0])
    tot_dist = 0.
    npts = 0
    for i in range(len(int_pts)):
        for j in range(i+1, len(int_pts)):
            tot_dist += int_pts[i].distance(int_pts[j])
            npts += 1
    return (tot_dist/float(npts) if npts > 0 else tot_dist)

def find_best_intersection(lines):
    # make a list of intersection points
    shifted_lines = copy.deepcopy(lines)
    # variable for loop ranges
    # ref: https://stackoverflow.com/questions/7186518/function-with-varying-number-of-for-loops-python
    ranges = [(-3, 3) for _ in range(len(lines)-1)]
    print(ranges)
    # int_pts = []
    # for i in range(len(lines)):
    #     for j in range(i+1, len(lines)):
    #         l1 = lines[i].line
    #         l2 = lines[j].line
    #         pt = l1.intersection(l2)
    #         if pt:
    #             int_pts.append(pt[0])
    # tot_dist = loss_function(int_pts)
    # print(tot_dist)
    return lines

def group_shift(lines, shifts):
    assert(len(lines) == len(shifts)+1)
    for i in range(len(shifts)):
        lines[i+1].shift_peak_id(shifts[i])
    return lines

def loss_function(pts):
    tot_dist = 0.
    for i in range(len(pts)):
        for j in range(i+1, len(pts)):
            tot_dist += pts[i].distance(pts[j])
    return tot_dist

def plot_result(lines):
    # plot points for each line
    random.seed(100)
    for line in lines:
        # determine line color
        rgb = (random.random(), random.random(), random.random())
        # make scatter plot of points
        px = np.array([p.x for p in line.points]).astype(float)
        py = np.array([p.y for p in line.points]).astype(float)
        plt.scatter(px, py, color=rgb)
        # calculate the range of x and plot
        xmax = max(px)*1.2
        xmin = -line.coeff[1]/line.coeff[0]
        fitx = np.linspace(xmin, xmax, 100)
        fity = line.coeff[0]*fitx + line.coeff[1]
        plt.plot(fitx, fity, '--', alpha=.7, color=rgb)
    plt.show()


if __name__ == '__main__':
    # command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_filelist', type=str,
                        default='infiles.txt')
    parser.add_argument('-b', '--board_id', type=int, default=1)
    parser.add_argument('-c', '--channel', type=int, default=8)
    args = parser.parse_args()
    inflist = args.input_filelist
    board_id = args.board_id
    channel = args.channel
    
    # construct MPPC lines
    with open(inflist, 'r') as flist:
        mppc_lines = tuple([MPPCLine(line.rstrip('\n'), board_id, channel) for line in flist])
    
    # find the best intersection of lines by shifting
    # all but one lines in x with integral distances
    best_lines = mppc_lines
    rranges = tuple([slice(-3, 3, 1) for _ in range(len(mppc_lines)-1)])
    print(mppc_lines)
    if len(mppc_lines) >= 3:
        # best_lines = find_best_intersection(mppc_lines)
        # print(average_distance((0,0,1), mppc_lines))
        resbrute = optimize.brute(average_distance, rranges, args=mppc_lines, full_output=True, finish=None)
        print(resbrute)
    
    # make the resulting plot
    plot_result(group_shift(best_lines, resbrute[0]))
    