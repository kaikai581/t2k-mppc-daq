#!/usr/bin/env python

import serial

class NESLABRTE10:
    '''
    This is the API class for the T2K temperature sensors.
    The interface is RS232.
    '''

    def __init__(self):
        try:
            port_name = '/dev/ttyS0'
            self.conn = serial.Serial(
                port=port_name,
                baudrate=19200,
                parity=serial.PARITY_NONE,
                bytesize=serial.EIGHTBITS,
                stopbits=serial.STOPBITS_ONE,
                timeout=None
            )
        except Exception as e:
            print(e)
    
    def read_acknowledge(self):
        # Below is the way to send hexidecimal commands.
        # Source: https://stackoverflow.com/questions/17589942/using-pyserial-to-send-binary-data
        cmd = b'\xca\x00\x01\x00\x00\xfe'
        self.conn.write(cmd)
        response = self.conn.read(8)
        return response
    
    def read_low_temperature_limit(self):
        cmd = b'\xca\x00\x01\x40\x00\xbe'
        self.conn.write(cmd)
        response = self.conn.read(9)
        return response

    def read_status(self):
        cmd = b'\xca\x00\x01\x09\x00\xf5'
        self.conn.write(cmd)
        response = self.conn.read(11)
        return response

    def set_low_temperature_limit(self, target):
        # To pack target values, refer to
        # https://stackoverflow.com/questions/19287296/how-to-change-one-byte-int-to-two-bytes-in-python
        cmd = bytearray()
        for bs in [0xca, 0x00, 0x01, 0xc0, 0x02]:
            cmd.append(bs)
        return cmd