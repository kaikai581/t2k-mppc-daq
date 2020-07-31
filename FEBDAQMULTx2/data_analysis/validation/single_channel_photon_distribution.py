#!/usr/bin/env python

import argparse
import uproot

def main():
    # command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_filename', type=str,
           default='mppc_20200728.root')
    args = parser.parse_args()
    infpn = args.input_filename


if __name__ == '__main__':
    main()