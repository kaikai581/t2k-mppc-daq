#!/usr/bin/env python

import platform
import re
import serial


class T2KTEMPSENSOR:
    '''
    This is the API class for the T2K temperature sensors.
    The interface is RS232.
    '''

    def __init__(self):
        try:
            port_name = '/dev/ttyUSB0'
            if platform.system() == 'Windows':
                port_name = 'COM1'
            self.conn = serial.Serial(
                port=port_name,
                baudrate=115200,
                parity=serial.PARITY_NONE,
                bytesize=serial.EIGHTBITS,
                timeout=None
            )
        except Exception as e:
            print(e)

        port_name = '/dev/ttyUSB0'
        self.conn = serial.Serial(
                port=port_name,
                baudrate=115200,
                parity=serial.PARITY_NONE,
                bytesize=serial.EIGHTBITS,
                timeout=None
            )
        self.conn.write('run 1\r'.encode())
    
    def __del__(self):
        try:
            self.conn.write('run 0\r'.encode())
        except Exception as e:
            print(e)

    def process_readout(self, rb):
        str = rb[rb.find('T'):].strip()
        sen_id = []
        for i in range(5):
            token = 'T{}'.format(i)
            if token in str:
                sen_id.append(token)
        values = re.split('|'.join(sen_id), str)
        # clean up the values list
        values = [v.strip() for v in values if v != '']
        temps = dict()
        for i in range(len(sen_id)):
            temps[sen_id[i]] = values[i] if i < len(values) else '0'
        return temps

    def query_temperature(self):
        # self.conn.write('run 1\r'.encode())
        rb = self.conn.readline().decode()
        # flush "run 1" in the returned message
        while 'run 1' in rb:
            rb = self.conn.readline().decode()
        temp_dict = self.process_readout(rb)
        # self.conn.write('run 0\r'.encode())
        return temp_dict
