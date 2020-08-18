#!/usr/bin/env python

import argparse
import matplotlib.pyplot as plt
import numpy as np
import os, sys
import uproot

def main():
    # command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_filename', type=str,
           default='../data/mppc_20200817_2febs.root')
    parser.add_argument('-f', '--force_generate', action='store_true')
    args = parser.parse_args()
    global infpn
    infpn = args.input_filename
    global infn
    infn = os.path.basename(infpn)

    # assemble the output file pathname
    outpn = os.path.join(os.path.dirname(__file__), 'processed_data')
    if not os.path.exists(outpn):
        os.makedirs(outpn)
    outfn = infn.rstrip('.root') + '.h5'
    outfpn = os.path.join(outpn, outfn)

    # see if a run-through is necessary
    if os.path.exists(outfpn) and args.force_generate:
        print('Output {} exists. If you want to force executing, use --force_generate.'.format(outfpn))
        sys.exit(0)

    # read data with uproot
    infpn = os.path.join(os.path.dirname(__file__), '../data', infn)
    try:
        tr = uproot.open(infpn)['mppc']
    except:
        print('File {} does not exist. Terminating...'.format(infpn))
        sys.exit(0)
    df = tr.pandas.df()
    # add a row for FEB board ID according to the mac5 value
    mac5s = list(df.mac5.unique())
    df['feb_num'] = df['mac5'].apply(lambda x: mac5s.index(x))
    
    # output dataframe to file
    df.to_hdf(outfpn, key='mppc', complib='bzip2', complevel=9)

    print(df.head())

if __name__ == '__main__':
    main()
