#!/usr/bin/env python

import argparse
import uproot

def main():
    # command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_filename', type=str,
           default='mppc_20200728.root')
    parser.add_argument('-b', '--board_id', type=int, default=0)
    parser.add_argument('-c', '--channel', type=int, default=0)
    args = parser.parse_args()
    infpn = args.input_filename
    board_id = args.board_id
    channel = args.channel

    # read data with uproot
    tr = uproot.open(infpn)['mppc']
    df = tr.pandas.df()
    # add a row for FEB board ID according to the mac5 value
    mac5s = list(df.mac5.unique())
    df['feb_num'] = df['mac5'].apply(lambda x: mac5s.index(x))
    
    if channel >= 0:
        single_channel_plot(df, board_id, channel)
    else:
        plot_32_channels(df, board_id)


if __name__ == '__main__':
    main()
