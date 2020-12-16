#!/usr/bin/env python

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_file', type=str, default='processed_data/channel_summary.csv')
    parser.add_argument('--output_path', type=str, default=os.path.join(os.path.dirname(__file__), 'plots'))
    args = parser.parse_args()
    infpn = args.input_file

    