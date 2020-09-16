#!/usr/bin/env python

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import statistics

class PeakCleanup:
    def __init__(self, peak_adcs):
        self.peak_adcs = peak_adcs
        self.peak_diffs = [peak_adcs[i+1]-peak_adcs[i] for i in range(len(peak_adcs)-1)]
    
    def mad_based_outlier(self, points, thresh=3.5):
        '''
        Ref: https://stackoverflow.com/questions/22354094/pythonic-way-of-detecting-outliers-in-one-dimensional-observation-data/22357811#22357811
        '''
        if len(points.shape) == 1:
            points = points[:,None]
        median = np.median(points, axis=0)
        diff = np.sum((points - median)**2, axis=-1)
        diff = np.sqrt(diff)
        med_abs_deviation = np.median(diff)
        if med_abs_deviation < 1e-2: med_abs_deviation = 1

        modified_z_score = 0.6745 * diff / med_abs_deviation
        print(modified_z_score)

        return modified_z_score > thresh
    
    def mad_based_outlier_idx(self, points, thresh=3.5):
        '''
        Return the indices of the outliers.
        '''
        if len(points.shape) == 1:
            points = points[:,None]
        median = np.median(points, axis=0)
        diff = np.sum((points - median)**2, axis=-1)
        diff = np.sqrt(diff)
        med_abs_deviation = np.median(diff)
        if med_abs_deviation < 1e-2: med_abs_deviation = 1

        modified_z_score = 0.6745 * diff / med_abs_deviation
        # scale the threshold accordingly
        if len(modified_z_score): thresh = thresh * np.sqrt(8 / len(modified_z_score))

        return [i for i in range(len(modified_z_score)) if modified_z_score[i] > thresh]
    
    def plot(self, x, thresh=5):
        fig, axes = plt.subplots(nrows=1)
        for ax, func in zip([axes], [self.mad_based_outlier]):
            sns.distplot(x, ax=ax, rug=True, hist=False)
            outliers = x[func(x, thresh)]
            ax.plot(outliers, np.zeros_like(outliers), 'ro', clip_on=False)

        kwargs = dict(y=0.95, x=0.05, ha='left', va='top')
        axes.set_title('Median-based Outliers', **kwargs)
        fig.suptitle('Outlier Tests with n={}'.format(len(x)), size=14)
    
    def plot_to_axis(self, ax, x, thresh=5):
        sns.distplot(x, ax=ax, rug=True, hist=False)
        outliers = x[self.mad_based_outlier(x, thresh)]
        ax.plot(outliers, np.zeros_like(outliers), 'ro')

        ax.set_title('outlier detection')
        ax.set_xlabel('adjacent ADC difference')
    
    def remove_outlier(self, idx):
        # try to remove the left and the right data points
        # and compare which one is more reasonable
        left_removed = self.peak_adcs.copy()
        left_removed.pop(idx)
        right_removed = self.peak_adcs.copy()
        right_removed.pop(idx+1)
        left_diff = [left_removed[i+1]-left_removed[i] for i in range(len(left_removed)-1)]
        right_diff = [right_removed[i+1]-right_removed[i] for i in range(len(right_removed)-1)]
        # keep the one with a smaller standard deviation
        if statistics.stdev(left_diff) < statistics.stdev(right_diff):
            self.peak_adcs = left_removed
            self.peak_diffs = left_diff
        else:
            self.peak_adcs = right_removed
            self.peak_diffs = right_diff
    
    def remove_outlier_twice(self):
        for i in range(2):
            outl_idx = self.mad_based_outlier_idx(np.array(self.peak_diffs), thresh=5)
            if outl_idx:
                self.remove_outlier(outl_idx[-1])
        

if __name__ == '__main__':
    test_input1 = [320.0, 385.0, 450.0, 520.0, 585.0, 650.0]
    test_input2 = [320.0, 385.0, 455.0, 520.0, 590.0, 655.0, 705.0, 720.0]
    test_input3 = [520.0, 570.0, 610.0]
    pc = PeakCleanup(test_input2)

    # # detect outlier points
    # outl_idx = pc.mad_based_outlier_idx(np.array(pc.peak_diffs), thresh=5)
    # # only remove the right most index since indices change
    # if outl_idx:
    #     pc.remove_outlier(outl_idx[-1])
    pc.remove_outlier_twice()
    print(pc.peak_adcs)

    pc.plot(np.array(pc.peak_diffs), thresh=5)
    plt.show()

