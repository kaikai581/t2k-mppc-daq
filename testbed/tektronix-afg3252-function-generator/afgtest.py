from AFG3252 import * 

import argparse
import time
import socket

if __name__ == '__main__':
    # Command line argument to use another IP
    parser = argparse.ArgumentParser()
    # Default IP address of the function generator assigned by me.
    parser.add_argument('-i','--ip', help='IP address of the function generator', default='192.168.0.101', type=str)
    args = parser.parse_args()

    fg = socket.gethostbyname(args.ip)

    print('Function generator on IP {0}...'.format(fg))
    dev = AFG3252(fg)

    dev.disableOutput(1)
    dev.disableOutput(2)

    dev.outputType('pulse')
    dev.outputPolarity(1,'INVerted')
    dev.setFrequency(7000)
    #dev.setVoltage(1, "50mV")
    dev.setVoltageHigh(1,"50mV")
    dev.setVoltageLow(1,"0mV")
    dev.setLeading(1, "4ns")
    dev.setTrailing(1, "55us")

    dev.enableOutput(1)
    time.sleep(2)
    dev.disableOutput(1)
