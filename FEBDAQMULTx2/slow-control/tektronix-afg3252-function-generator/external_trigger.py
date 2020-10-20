#!/usr/bin/env python

from AFG3252 import * 

import argparse
import socket

def send_led_driver_and_ext_trigger(dev):
    # first recall channel 1
    dev.recallWaveform(1)
    dev.enableOutput(1)
    # dev.setBurstTrig(2)
    dev.setDutyCycle(2, 0.032)
    dev.setFrequency(1000.923077, 2)
    dev.setVoltageHigh(2, '3.3V')
    # dev.setLeading(1, '2.5ns')
    # dev.setTrailing(1, '2.5ns')
    dev.outputType('pulse', 2)
    dev.enableOutput(2)


if __name__ == '__main__':
    # Command line argument to use another IP
    parser = argparse.ArgumentParser()
    # Default IP address of the function generator assigned by me.
    parser.add_argument('-i','--ip', help='IP address of the function generator', default='192.168.0.101', type=str)
    parser.add_argument('--off', help='Switch off the output channels', action='store_true')
    args = parser.parse_args()

    fg = socket.gethostbyname(args.ip)

    print('Function generator on IP {0}...'.format(fg))
    dev = AFG3252(fg)

    # switch on or off the output channels
    if args.off:
        dev.disableOutput(1)
        dev.disableOutput(2)
    else:
        send_led_driver_and_ext_trigger(dev)
