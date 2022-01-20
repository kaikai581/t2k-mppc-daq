#!/usr/bin/env python

import matplotlib.pyplot as plt
import os
import seaborn as sns

# redirect output to avoid x11 error
import matplotlib
matplotlib.use('Agg')

class OnePCBSummary:
    def __init__(self, data):
        '''
        Specify the data used for making summary plots.
        data is a pandas dataframe.
        '''
        self.df = data
    
    def describe_helper(self, series):
        '''
        This function formats the summary statistics of a pandas series.
        '''
        splits = str(series.describe()).split()[:-4]
        keys, values = "", ""
        for i in range(0, len(splits), 2):
            keys += "{:8}\n".format(splits[i])
            values += "{:>8}\n".format(splits[i+1])
        return keys, values

    def make_summary_plot(self, x, y, joint_title, figure_title, y_title, x_title='PCB channel number', y_error=None, outfpn='test.png'):
        g = sns.JointGrid(data=self.df, x=x, y=y)

        # if y_error is provided, make plot with error bars
        if y_error is None:
            g.plot_joint(sns.scatterplot)
        else:
            g.ax_joint.errorbar(
                x=self.df[x],
                y=self.df[y],
                yerr=self.df[y_error],
                fmt='o'
            )

        # set up all kinds of titles
        g.ax_joint.grid(axis='both')
        g.ax_joint.set_xlabel(x_title)
        g.ax_joint.set_ylabel(y_title)
        g.ax_joint.set_title(joint_title)
        g.plot_marginals(sns.histplot)
        g.ax_marg_y.grid(axis='y')
        g.ax_marg_x.remove()

        # set the figure title and show summary statistics
        g.fig.set_figwidth(10)
        g.fig.set_figheight(5)
        g.fig.suptitle(figure_title)
        plt.subplots_adjust(right=0.95)
        plt.figtext(.96, .54, self.describe_helper(self.df[y])[0], {'multialignment':'left'})
        plt.figtext(1.03, .54, self.describe_helper(self.df[y])[1], {'multialignment':'right'})

        # save figure to file
        out_dir = os.path.dirname(outfpn)
        if not out_dir:
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
        g.savefig(outfpn, bbox_inches='tight')
