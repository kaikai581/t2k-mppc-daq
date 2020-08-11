import vxi11
import time, sys
from math import sqrt



outputMap = {
    'sine' : 'SIN',
    'square' : 'SQU',
    'ramp' : 'RAMP',
    'pulse' : 'PULS'
    }


class FunctionGenerator:
    def __init__(self, host):
        pass

    def setFrequency(self, frequency):
        pass

    def setAmplitude(self, ch, V):
        pass

    def setOffset(self, ch, V):
        pass

    def enableOutput(self):
        pass

    def disableOutput(self):
        pass

    def outputType(self, sigType):
        pass
    
    def outputPolarity(self, ch, sigPolarity):
        pass

    def runSweep(self, fStart, fStop, holdTime, steps): 
        pass

    def setLeading(self, ch, seconds):
        pass

    def setTrailing(self, ch, seconds):
        pass

    def setVoltageHigh(self, ch, val):
        pass
    
    def setVoltageLow(self, ch, val):
        pass
        
    def setVoltageUnit(self, ch, val):
        pass

class AFG3252(FunctionGenerator):
    def __init__(self, host):
        try:
            self.conn = vxi11.Instrument(host)
            self.dType = self.conn.ask('*IDN?')
            print(self.dType)
        except Exception as e:
            print(e)


    def setFrequency(self, frequency):
        print('Setting fixed frequency to {0}'.format(frequency))
        self.conn.write('SOUR:FREQ:FIX {0}'.format(frequency))

    def setAmplitude(self, ch, V):
        if 1 <= ch <= 2:
            self.conn.write('SOURCE{0}:VOLTAGE:LEVEL:IMMEDIATE:AMPLITUDE {1}'.format(ch, V))
        else:
            print('I don\'t have channel {0}'.format(ch))
        pass

    def setOffset(self, ch, V):
        if 1 <= ch <= 2:
            self.conn.write('SOURCE{0}:VOLTAGE:LEVEL:IMMEDIATE:OFFSet {1}'.format(ch, V))
        else:
            print('I don\'t have channel {0}'.format(ch))
        pass
    
    def enableOutput(self, ch):
        print('Enabling channel {0}'.format(ch))
        if 1 <= ch <= 2:
            self.conn.write('OUTP{0}:STAT ON'.format(ch))
        else:
            print('I don\'t have channel {0}'.format(ch))

    def disableOutput(self, ch):
        print('Disabling channel {0}'.format(ch))
        if 1 <= ch <= 2:
            self.conn.write('OUTP{0}:STAT OFF'.format(ch))
        else:
            print('I don\'t have channel {0}'.format(ch))
        
    def outputType(self, sigType):
        try:
            sig = outputMap[sigType]
            self.conn.write('SOUR:FUNC:SHAP {0}'.format(sig))

        except Exception as e:
            print(e)

    def outputPolarity(self, ch, sigPolarity):
        if 1 <= ch <= 2:
            self.conn.write('OUTPUT{0}:POLARITY {1}'.format(ch, sigPolarity))
        else:
            print('I don\'t have channel {0}'.format(ch))

    def sweep(self, start, stop, step, wait):
        
        self.setFrequency(start)
        delta = round((float(stop)-start)/step)
        f = start
        for i in range(0, step-1):
            time.sleep(wait)
            f += delta
            self.setFrequency(f)
                        
        self.setFrequency(stop)
        time.sleep(wait)

    def setLeading(self, ch, seconds):
        print('Setting leading edge on channel {0} to {1}'.format(ch,seconds))
        if 1 <= ch <= 2:
            self.conn.write('SOURCE{0}:PULSE:TRANSITION:LEADING {1}'.format(ch, seconds))
        else:
            print('I don\'t have that channel {0}'.format(ch))

    def setTrailing(self, ch, seconds):
        print('Setting trailing edge on channel {0} to {1}'.format(ch,seconds))
        if 1 <= ch <= 2:
            self.conn.write('SOURCE{0}:PULSE:TRANSITION:TRAILING {1}'.format(ch, seconds))
        else:
            print('I don\'t have that channel {0}'.format(ch))

    def setVoltageHigh(self, ch, val):
        print('Setting high voltage on channel {0} to {1}'.format(ch,val))
        if 1 <= ch <= 2:
            self.conn.write('SOURCE{0}:VOLTAGE:LIMIT:HIGH {1}'.format(ch, val))
        else:
            print('I don\'t have that channel {0}'.format(ch))
  
    def setVoltageLow(self, ch, val):
        print('Setting low voltage on channel {0} to {1}'.format(ch,val))
        if 1<= ch <= 2:
            self.conn.write('SOURCE{0}:VOLTAGE:LIMIT:LOW {1}'.format(ch, val))
        else:
            print('I don\'t have that channel {0}'.format(ch))