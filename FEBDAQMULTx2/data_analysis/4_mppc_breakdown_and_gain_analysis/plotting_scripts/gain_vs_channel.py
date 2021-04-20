#!/usr/bin/env python

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file_names', nargs='*', type=str, default=['20200929*volt58.0*.h5'], help='List of files to proccess. Wildcards can be used.')
    parser.add_argument('-b', '--board', type=int, default=-1)
    parser.add_argument('-p', '--prominence', type=int, default=250)
    parser.add_argument('-l', '--left_threshold', type=float, default=0.7)
    parser.add_argument('-r', '--right_threshold', type=float, default=1.23)
    args = parser.parse_args()
    print(args.file_names)