#!/usr/bin/env python

import argparse
import os
import pandas as pd
import sys
import uproot

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_files', nargs='*', required=True)
    parser.add_argument('-o', '--output_file_pathname', type=str, default='combined.h5')
    args = parser.parse_args()
    input_files = args.input_files
    outfpn = args.output_file_pathname

    # convert all root files into dataframes
    dfs = []
    for infpn in input_files:
        if not os.path.exists(infpn):
            print('File {} does not exist!'.format(infpn))
            sys.exit(-1)
        tr = uproot.open(infpn)['mppc']
        dfs.append(tr.pandas.df())
    
    # concatenate all files in the input_files list
    df = pd.concat(dfs, axis=0)
    # add a row for FEB board ID according to the mac5 value
    mac5s = list(df.mac5.unique())
    df['feb_num'] = df['mac5'].apply(lambda x: mac5s.index(x))
    dfs.append(df)

    # output dataframe to file
    df.to_hdf(outfpn, key='mppc', complib='bzip2', complevel=9)
    print(df)
    