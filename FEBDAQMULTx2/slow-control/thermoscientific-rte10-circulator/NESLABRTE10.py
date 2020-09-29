#!/usr/bin/env python

import serial, struct, sys

class NESLABRTE10:
    '''
    This is the API class for the T2K temperature sensors.
    The interface is RS232.
    '''

    def __init__(self, conn_timeout=1):
        try:
            port_name = '/dev/ttyS0'
            self.conn = serial.Serial(
                port=port_name,
                baudrate=19200,
                parity=serial.PARITY_NONE,
                bytesize=serial.EIGHTBITS,
                stopbits=serial.STOPBITS_ONE,
                timeout=conn_timeout
            )
        except Exception as e:
            print(e)
    
    def checksum(self, bstr):
        barr = bytearray(bstr)
        barr = barr[1:]
        return sum(barr) & 0x0FF ^ 0xFF

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

    def read_setpoint(self):
        cmd = b'\xca\x00\x01\x70\x00\x8e'
        self.conn.write(cmd)
        response = self.conn.read(9)
        return (int.from_bytes(response[6:8], 'big'))/10.

    def read_status(self):
        cmd = b'\xca\x00\x01\x09\x00\xf5'
        self.conn.write(cmd)
        response = self.conn.read(11)
        return response

    def set_low_temperature_limit(self, target):
        # To pack target values, refer to
        # https://stackoverflow.com/questions/19287296/how-to-change-one-byte-int-to-two-bytes-in-python

        # The status byte indicates a precision to the first decimal point digit,
        # so the target value has to be multiplied by 10.
        cmd = b'\xca\x00\x01\xc0\x02' + struct.pack('>h', target*10)
        print('Set low temperature limit checksum:', hex(self.checksum(cmd)))
        cmd += self.checksum(cmd).to_bytes(1, sys.byteorder)
        # If I naively print out the cmd, the result might not be what I expect.
        # However, it could be the right answer.
        # See https://stackoverflow.com/questions/25068477/python-converting-hex-string-to-bytes
        self.conn.write(cmd)
        response = self.conn.read(9)
        return response

    def set_off_array(self):
        cmd = b'\xca\x00\x01\x81\x08\x00\x02\x02\x02\x02\x02\x02\x02'
        cmd += self.checksum(cmd).to_bytes(1, sys.byteorder)
        self.conn.write(cmd)
        response = self.conn.read(14)
        return response

    def set_on_array(self):
        cmd = b'\xca\x00\x01\x81\x08\x01\x02\x02\x02\x02\x02\x02\x02'
        cmd += self.checksum(cmd).to_bytes(1, sys.byteorder)
        self.conn.write(cmd)
        response = self.conn.read(14)
        return response

    def set_setpoint(self, target):
        # The status byte indicates a precision to the first decimal point digit,
        # so the target value has to be multiplied by 10.
        cmd = b'\xca\x00\x01\xf0\x02' + struct.pack('>h', int(target*10))
        cmd += self.checksum(cmd).to_bytes(1, sys.byteorder)
        self.conn.write(cmd)
        response = self.conn.read(9)
        return response