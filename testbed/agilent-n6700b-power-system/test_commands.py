#!/usr/bin/env python

################################################################################
# © Keysight Technologies 2016
#
# You have a royalty-free right to use, modify, reproduce and distribute
# the Sample Application Files (and/or any modified version) in any way
# you find useful, provided that you agree that Keysight Technologies has no
# warranty, obligations or liability for any Sample Application Files.
#
################################################################################

import sys
import time
import visa

def find(searchString):

    resourceManager = visa.ResourceManager()

    print('Find with search string \'%s\':' % searchString)
    devices = resourceManager.list_resources(searchString)
    if len(devices) > 0:
        device_names = ['%s' % device for device in devices]
    else:
        print('... didn\'t find anything!')
        sys.exit()

    resourceManager.close()
    return device_names

def is_n6700b(visa_addr):
    # Create a connection (session) to the TCP/IP socket on the instrument.
    resourceManager = visa.ResourceManager()
    session = resourceManager.open_resource(visa_addr)

    # For Serial and TCP/IP socket connections enable the read Termination Character, or read's will timeout
    if session.resource_name.startswith('ASRL') or session.resource_name.endswith('SOCKET'):
        session.read_termination = '\n'

    # We can find out details of the connection
    # print('IP: %s\nHostname: %s\nPort: %d\n' %
    #       (session.get_visa_attribute(visa.constants.VI_ATTR_TCPIP_ADDR),
    #        session.get_visa_attribute(visa.constants.VI_ATTR_TCPIP_HOSTNAME),
    #        session.get_visa_attribute(visa.constants.VI_ATTR_TCPIP_PORT)))
    # Code below prints all available attributes.
    #print(visa.constants.__dict__)

    # Send the *IDN? and read the response
    session.write('*IDN?')
    idn = session.read()

    print('Detailed model of this device:')
    print('*IDN? returned: %s' % idn.rstrip('\n'))

    # Close the connection to the instrument
    session.close()
    resourceManager.close()

    if 'N6700B' in idn: return True
    return False

def main():
    # At this moment, only look for ethernet connected device.
    VISA_ADDRESSES = find('TCPIP?*')

    # Loop through all ethernet devices and look for the power system.
    for VISA_ADDRESS in VISA_ADDRESSES:
        try:
            if is_n6700b(VISA_ADDRESS):
                # try_commands(VISA_ADDRESS)
                step_voltage(VISA_ADDRESS)
        except visa.Error as ex:
            print('An error occurred: %s' % ex)

def step_voltage(visa_addr):
    # Create a connection (session) to the TCP/IP socket on the instrument.
    resourceManager = visa.ResourceManager()
    session = resourceManager.open_resource(visa_addr)

    # For Serial and TCP/IP socket connections enable the read Termination Character, or read's will timeout
    if session.resource_name.startswith('ASRL') or session.resource_name.endswith('SOCKET'):
        session.read_termination = '\n'
    
    '''
    Here are the commands to scan voltages!
    First try: scan voltage from 0 to 5 V in 1 V steps.
    Stay 3 seconds at each voltage.
    '''
    # Switch to the single channel view
    session.write('DISP:VIEW METER1')

    # Start to step
    for voltage in range(6):
        session.write('VOLT {},(@4)'.format(voltage))
        session.write('OUTP ON,(@4)')
        time.sleep(3)
        session.write('OUTP OFF,(@4)')
    
    # Close the connection to the instrument
    session.close()
    resourceManager.close()

def try_commands(visa_addr):
    # Create a connection (session) to the TCP/IP socket on the instrument
    resourceManager = visa.ResourceManager()
    session = resourceManager.open_resource(visa_addr)

    # For Serial and TCP/IP socket connections enable the read Termination Character, or read's will timeout
    if session.resource_name.startswith('ASRL') or session.resource_name.endswith('SOCKET'):
        session.read_termination = '\n'
    
    '''
    Here are the commands to play with!
    '''

    # Front panel single/multiple channel view
    # session.write('DISP:VIEW METER4')
    # time.sleep(2)
    session.write('DISP:VIEW METER1')

    # Select the channel of interest. NOT WORKING.
    # session.write('OUTP:STAT? (@3)')

    # Set target voltage of a channel.
    session.write('VOLT 5,(@4)')

    # Enable the Output
    session.write('OUTP ON,(@4)')
    time.sleep(2)

    # Disable the Output
    session.write('OUTP OFF,(@4)')
    
    # Close the connection to the instrument
    session.close()
    resourceManager.close()

if __name__ == '__main__':
    main()