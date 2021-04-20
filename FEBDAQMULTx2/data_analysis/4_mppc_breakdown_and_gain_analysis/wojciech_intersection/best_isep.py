#!/usr/bin/env python

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from matplotlib import markers
from peak_cleanup import PeakCleanup
from scipy import optimize
from scipy.signal import find_peaks
from sympy import Point2D, Line2D
from sympy.geometry.util import centroid
import argparse
import copy
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
import uproot

class MPPCLine:
    def __init__(self, infpn, feb_id, ch, verbose=False):
        '''
        The constructor is responsible for finding peak positions given
        a filename and a channel ID.
        '''
        if verbose:
            print('Processing:\n', infpn)
        # get the dataframe either from a .h5 file or a .root file directly
        fext = os.path.splitext(infpn)[1]
        if fext == '.h5':
            try:
                df = pd.read_hdf(infpn, key='mppc')
            except:
                print('Error reading file {}'.format(infpn))
                sys.exit(-1)
                return
        elif fext == '.root':
            tr_mppc = uproot.open(infpn)['mppc']
            df = tr_mppc.pandas.df()
            mac5s = list(df.mac5.unique())
            df['feb_num'] = df['mac5'].apply(lambda x: mac5s.index(x))
            if verbose:
                print('Converted dataframe from ROOT:\n', df)
        else:
            print('File format is neither a hdf5 nor a root.')
            sys.exit(-1)

        # store verbosity
        self.verbose = verbose
        # store the input file name
        self.infpn = infpn
        # make the plot of a channel
        self.feb_id = feb_id
        self.chvar = 'chg[{}]'.format(ch)
        # select data of the specified board
        self.df_1b = df[df['feb_num'] == feb_id]
        if verbose:
            print('FEB{} dataframe:\n'.format(feb_id), self.df_1b)
        # make histogram and find peaks
        self.bins = np.linspace(0, 4100, 821)
        _, axs = plt.subplots(2)
        histy, bin_edges, _ = axs[0].hist(self.df_1b[self.chvar], bins=self.bins, histtype='step')
        self.peaks, _ = find_peaks(histy, prominence=300)
        if verbose:
            print('Found peaks with heights:\n', self.peaks)
        
        # release memory
        plt.close()

        # store processed data
        pc = PeakCleanup(list(np.array(bin_edges)[self.peaks]))
        pc.remove_outlier_by_relative_interval()
        self.peak_adcs = pc.peak_adcs
        if verbose:
            print('Peak ADCs:\n', self.peak_adcs)
        self.points = [Point2D(i, self.peak_adcs[i]) for i in range(len(self.peak_adcs))]

        # fit a line to the points
        if len(self.peaks) > 1:
            self.line, self.coeff = self.get_line_from_points(self.points)

        # bias voltage
        self.voltage = self.voltage_from_filename(infpn)
    
    def get_line_from_points(self, pts):
        # fit a line to the points
        x_try = np.array([p.x for p in pts]).astype(float)
        y_try = np.array([p.y for p in pts]).astype(float)
        coeff = np.polyfit(x_try, y_try, 1)
        return Line2D(Point2D(0, coeff[1]), slope=coeff[0]), coeff
    
    def get_threshold_from_metadata(self):
        # get the dataframe either from a .h5 file or a .root file directly
        fext = os.path.splitext(self.infpn)[1]
        if fext == '.h5':
            try:
                df = pd.read_hdf(self.infpn, key='metadata')
            except:
                print('Error reading metadata from {}'.format(self.infpn))
                return 0
        elif fext == '.root':
            tr_mppc = uproot.open(self.infpn)['metadata']
            df = tr_mppc.pandas.df()
        df_selch = df[df['isTrigger'] == True]

        if len(df_selch) >= 1:
            return df_selch['DAC'].iloc[0]
        
        return -1

    def shift_and_match(self, pkadcs):
        '''
        This method shifts the peak IDs to the left or right in a small range,
        and find the best fit to the peak ADC input array.
        The "pkadcs" is a known input array in which the index is the peak number and the value is the peak ADC.
        '''

        # get the line formed by the input array
        ref_points = [Point2D(i, pkadcs[i]) for i in range(len(pkadcs))]
        ref_line, _ = self.get_line_from_points(ref_points)

        diff_sum = []
        shift_min = -3
        shift_max = 6
        for shift in range(shift_min, shift_max):
            pts = [Point2D(float(p.x)+shift, float(p.y)) for p in self.points]
            dist_sum = 0
            for p in pts:
                dist_sum += ref_line.distance(p)
            diff_sum.append(dist_sum)
        best_shift = np.argmin(diff_sum) + shift_min
        if self.verbose:
            print('Sum of distances from points to the reference line, shifting from {} to {} in x:\n'.format(shift_min, shift_max-1), diff_sum)
            print('Best shift:', best_shift)
        self.shift_peak_id(best_shift)

    def shift_peak_id(self, x_shift):
        '''
        This method shifts all peak position assignments to the left or right
        by x_shift amount. It also shifts the fitted line by the same amount.
        '''
        self.points = [Point2D(i+x_shift, self.peak_adcs[i]) for i in range(len(self.peak_adcs))]
        self.coeff[1] -= self.coeff[0]*x_shift
        self.line = Line2D(Point2D(0, self.coeff[1]), slope=self.coeff[0])
    
    def show_spectrum(self, savefpn=None):
        histy, bin_edges, _ = plt.hist(self.df_1b[self.chvar], bins=self.bins, histtype='step')
        plt.scatter(np.array(bin_edges)[self.peaks], np.array(histy)[self.peaks],
                    marker=markers.CARETDOWN, color='r', s=20)
        threshold = self.get_threshold_from_metadata()
        if threshold > 0:
            plt.title('DAC {}'.format(threshold))
        for i in range(len(self.points)):
            p = self.points[i]
            h = histy[self.peaks[i]]
            plt.text(float(p.y), h, str(int(p.x)))
        if savefpn:
            plt.savefig(savefpn)
        else:
            plt.show()
        plt.close()

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
    int_pts = find_intersection_points(shifted_lines)
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
    return shifted_lines

def find_intersection_points(lines):
    int_pts = []
    for i in range(len(lines)):
        for j in range(i+1, len(lines)):
            l1 = lines[i].line
            l2 = lines[j].line
            pt = l1.intersection(l2)
            if pt:
                int_pts.append(pt[0])
    return int_pts

def group_shift(lines, shifts):
    assert(len(lines) == len(shifts)+1)
    for i in range(len(shifts)):
        lines[i+1].shift_peak_id(shifts[i])
    int_pts = find_intersection_points(lines)
    p_cent = centroid(*int_pts)
    return lines, p_cent

def loss_function(pts):
    tot_dist = 0.
    for i in range(len(pts)):
        for j in range(i+1, len(pts)):
            tot_dist += pts[i].distance(pts[j])
    return tot_dist

def plot_result(lines, p_cent, outfpn):
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
        plt.plot(fitx, fity, '--', alpha=.7, color=rgb, label='{} V'.format(line.voltage))
    if p_cent:
        xx = float(p_cent.x)
        yy = float(p_cent.y)
        plt.plot(xx, yy, 'X', color='r')
        plt.annotate('({:.2f},{:.2f})'.format(xx, yy), xy=(xx, yy), xytext=(xx+0.35, yy-30))
    plt.legend()
    plt.xlabel('PE ID')
    plt.ylabel('ADC')
    plt.savefig(outfpn)
    plt.close()


if __name__ == '__main__':
    # command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--input_filelist', type=str,
                        default='infiles.txt')
    parser.add_argument('-i', '--input_files', type=str,
                        default=['../../data/root/20201030_165210_mppc_volt59.0_temp22.8.root', '../../data/root/20201030_165731_mppc_volt59.5_temp22.8.root', '../../data/root/20201030_170151_mppc_volt60.0_temp22.8.root', '../../data/root/20201030_170540_mppc_volt60.5_temp22.8.root', '../../data/root/20201030_170925_mppc_volt61.0_temp22.8.root'], nargs='*')
    # parser.add_argument('-i', '--input_files', type=str,
    #                     default=['../../data/root/20201030_165210_mppc_volt59.0_temp22.8.root', '../../data/root/20201030_165731_mppc_volt59.5_temp22.8.root', '../../data/root/20201030_170151_mppc_volt60.0_temp22.8.root', '../../data/root/20201030_170540_mppc_volt60.5_temp22.8.root'], nargs='*')
    parser.add_argument('-b', '--board_id', type=int, default=1)
    parser.add_argument('-c', '--channel', type=int, default=8)
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()
    inflist = args.input_filelist
    infs = args.input_files
    board_id = args.board_id
    channel = args.channel
    verbosity = args.verbose
    
    # construct MPPC lines
    if infs:
        mppc_lines = tuple([MPPCLine(line.rstrip('\n'), board_id, channel, verbosity) for line in infs])
    else:
        with open(inflist, 'r') as flist:
            mppc_lines = tuple([MPPCLine(line.rstrip('\n'), board_id, channel, verbosity) for line in flist])
    
    # find the best intersection of lines by shifting
    # all but one lines in x with integral distances
    best_lines = mppc_lines
    rranges = tuple([slice(-3, 3, 1) for _ in range(len(mppc_lines)-1)])
    print(mppc_lines)
    if len(mppc_lines) >= 3:
        # best_lines = find_best_intersection(mppc_lines)
        # print(average_distance((0,0,1), mppc_lines))
        resbrute = optimize.brute(average_distance, rranges, args=mppc_lines, full_output=True, finish=None)
        # print(resbrute)
    
    # make the resulting plot
    p_cent = None
    plot_result(mppc_lines, p_cent, 'before.png')
    lines, p_cent = group_shift(best_lines, resbrute[0])
    plot_result(lines, p_cent, 'after.png')
    