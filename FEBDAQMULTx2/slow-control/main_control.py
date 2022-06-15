#!/usr/bin/env python

import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                'agilent-n6700b-power-system'))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                't2k-temperature-sensor'))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                'tektronix-afg3252-function-generator'))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                'thermoscientific-rte10-circulator'))
import socket

# for making plots
import pyqtgraph as pg

# other utilities
import collections
import datetime, time
import json
import numpy as np
import pandas as pd
import signal
import statistics
import zmq

# device API imports
from AFG3252 import AFG3252
from N6700B import N6700B
from T2KTEMPSENSOR import T2KTEMPSENSOR
from NESLABRTE10 import NESLABRTE10

# PyQt imports
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


# helper function for dealing with timestamp axis
# ref: https://gist.github.com/iverasp/9349dffa42aeffb32e48a0868edfa32d
def timestamp():
    return int(time.mktime(datetime.datetime.now().timetuple()))


# helper class for dealing with timestamp axis
# ref: https://gist.github.com/iverasp/9349dffa42aeffb32e48a0868edfa32d
class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLabel(text='Time', units=None)
        self.enableAutoSIPrefix(False)

    def attachToPlotItem(self, plotItem):
        """Add this axis to the given PlotItem
        :param plotItem: (PlotItem)
        """
        self.setParentItem(plotItem)
        viewBox = plotItem.getViewBox()
        self.linkToView(viewBox)
        self._oldAxis = plotItem.axes[self.orientation]['item']
        self._oldAxis.hide()
        plotItem.axes[self.orientation]['item'] = self
        pos = plotItem.axes[self.orientation]['pos']
        plotItem.layout.addItem(self, *pos)
        self.setZValue(-1000)

    def tickStrings(self, values, scale, spacing):
        return [datetime.datetime.fromtimestamp(value).strftime("%H:%M") for value in values]


class Window(QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        # get the control handles
        # function generator
        self.devFunGen = AFG3252(socket.gethostbyname('192.168.0.101'))
        # power unit
        self.devPowerUnit = N6700B('192.168.0.201')
        # temperature sensor
        ## If I open the temperature sensor as a member variable,
        ## temperature readings will all turn empty after the first reading.
        ## Don't quite know what happens here. However, opening the connection
        ## everytime when I want to get readings seems to be a workaround...
        self.devTempSen = T2KTEMPSENSOR()

        # widgets I want to have control ***************************************
        # power unit starts with pu
        self.puVoltageSwitch = QPushButton(text='Switch On')
        self.puVoltageSwitch.setCheckable(True)
        # self.puVoltageSwitch.clicked.connect(self.puPowerSwitch)
        self.puVoltageSwitch.toggled.connect(self.puPowerSwitch)
        self.puChCB = QComboBox()
        self.puChCB.addItems(['all', '1', '2', '3', '4'])
        self.puChCB.setCurrentIndex(3)
        # self.puChCB.setEnabled(False)
        self.puVsetEdit = QLineEdit('60')
        self.puVsetEdit.setValidator(QDoubleValidator(bottom=0, top=60, decimals=10))
        self.puVRbEdit = QLineEdit()

        # function generator stars with fg
        self.fgChSel = QComboBox()
        self.fgChSel.addItems(['1', '2', 'all'])
        self.fgChSel.setCurrentIndex(2)
        self.fgOutputSwitch = QPushButton(text='Switch On')
        self.fgOutputSwitch.setCheckable(True)
        self.fgOutputSwitch.clicked.connect(self.fgToggleOutput)
        self.fgRecallChSel = QComboBox()
        self.fgRecallChSel.addItems(['0', '1', '2', '3', '4'])
        # recall waveform when a saved state is selected
        self.fgRecallChSel.activated.connect(self.fgRecallState)
        self.fgRecallChSel.setCurrentIndex(2)
        self.fgFreqEdit = QLineEdit('1')
        self.fgFreqEdit.setValidator(QDoubleValidator(bottom=0, decimals=10))
        self.fgFreqBtn = QPushButton(text='Apply')
        self.fgFreqBtn.clicked.connect(self.fgApplyFreq)
        self.fgAmplEdit = QLineEdit('2.8')
        self.fgAmplEdit.setValidator(QDoubleValidator(decimals=10))
        self.fgAmplBtn = QPushButton(text='Apply')
        self.fgAmplBtn.clicked.connect(self.fgApplyAmpl)
        # touch the selected state to initialize readings
        self.fgRecallState()

        # a message box
        self.msgBox = QTextEdit()
        # self.msgBox.setText('Welcome to the control application!\n')
        self.msgBox.append('Welcome to the control application!')
        self.msgBox.setReadOnly(True)

        # T2K temperature sensor interface
        self.tsTemperatureCB = QComboBox()
        self.tsTemperatureCB.addItems(['T0', 'T1', 'T2', 'T3', 'T4'])
        self.tsTemperatureCB.activated.connect(self.tsReadTemperature)
        self.tsTemperatureEdit = QLineEdit()
        self.tsView = pg.GraphicsView()
        self.tsLo = pg.GraphicsLayout()
        self.tsPlot = None # member variable place holder
        # below are data structure for plotting
        self.timerTime = 2000
        self.tsPoints = 90
        self.tsX = dict()
        self.tsY = dict()
        for sen in ['T0', 'T1', 'T2', 'T3', 'T4']:
            self.tsX[sen] = collections.deque(maxlen=self.tsPoints)
            self.tsY[sen] = collections.deque(maxlen=self.tsPoints)
        # end of widgets declaration *******************************************

        # main window layout
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        # Add tabs
        self.tabs.addTab(self.tab1, 'Simple Control')
        self.tabs.addTab(self.tab2, 'Parameter Scan')
        self.tabs.addTab(self.tab3, 'Single Channel Dark Rate Scan')
        self.tab1.layout = QGridLayout()
        self.tab1.layout.addWidget(self.createVoltageControl(), 0, 0, 1, 1)
        self.tab1.layout.addWidget(self.createPulserControl(), 0, 1, 1, 1)
        self.tab1.layout.addWidget(self.createCirculatorControl(), 0, 2, 1, 1)
        self.tab1.layout.addWidget(self.msgBox, 1, 0, 1, 3)
        self.tab1.layout.addWidget(self.createTemperatureSensor(), 0, 3, 2, 1)
        self.tab1.setLayout(self.tab1.layout)
        self.tab2.setLayout(self.createParameterScan())
        self.tab3.setLayout(self.createDarkRateScan())
        grid = QGridLayout()
        grid.addWidget(self.tabs, 0, 0)
        self.setLayout(grid)
        # end of main window layout

        self.setWindowTitle('MPPC Slow Control App')
        self.resize(1200, 300)

        # use a figure as this app's icon
        # ref: https://stackoverflow.com/questions/42602713/how-to-set-a-window-icon-with-pyqt5
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QtGui.QIcon(os.path.join(scriptDir, 'logo.png')))

        #***** DAQ STATUS VARIABLE *****
        # Make sure this variable is defined before any timer instantiation.
        self.daqReady = True
        # Parameter scan queue for parameter values to be gone through
        # whenever the DAQ status is ready
        self.psQueue = []

        # use a timer for voltage readback
        # ref: https://pythonpyqt.com/qtimer/
        self.timer = QTimer()
        self.timer.start(self.timerTime)
        self.timer.timeout.connect(self.puReadbackVoltage)
        self.puReadbackVoltage()
        self.timer.timeout.connect(self.tsReadTemperature)
        self.tsReadTemperature()
        self.timer.timeout.connect(self.wcReadInternalTemperature)

        # zmq and polling timer implementation
        context = zmq.Context()
        self.socket = context.socket(zmq.PAIR)
        self.socket.connect("tcp://localhost:5556")
        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)
        self.timerPoll = QTimer()
        self.timerPoll.start(100)
        self.timerPoll.timeout.connect(self.pollMsg)

        # make a timer to log instrument readback data
        # every 10 seconds.
        self.logDataTimer = QTimer()
        self.logDataTimer.start(10000)
        self.logDataTimer.timeout.connect(self.tsLogReadouts)
        self.logDataTimer.timeout.connect(self.wcLogInternalTemperature)
        # also make dataframes for storing data points to be saved to disk.
        self.dfTempSensor = pd.DataFrame(columns=['Datetime','T0','T1','T2',
                                         'T3','T4'])
        self.dfWcIntTemp = pd.DataFrame(columns=['Datetime',
                                        'Internal Temperature'])

    def closeEvent(self, a0):
        '''
        Application destructor. Turn off various hardware components on window
        exit.
        '''
        ## turn off the power system
        # get the active channel
        active_ch = int(self.puChCB.currentText())
        self.devPowerUnit.power_off(active_ch)
        ## turn off the function generator
        self.devFunGen.disableOutput(1)
        self.devFunGen.disableOutput(2)
        
        return super().closeEvent(a0)

    def createCirculatorControl(self):
        # connect to the water circulator
        self.devWaterCirculator = NESLABRTE10()
        # member widgets for the water circulator
        self.wcLogDataCkB = QCheckBox()
        self.wcSetpointEdit = QLineEdit(text=str(self.devWaterCirculator.read_setpoint()))
        self.wcApplySetpointBtn = QPushButton('Apply')
        self.wcReadbackEdit = QLineEdit(text=str(self.devWaterCirculator.read_internal_temperature()))
        self.wcSwitchBtn = QPushButton('Switch On')
        self.wcSwitchBtn.setCheckable(True)
        # event connection
        self.wcApplySetpointBtn.clicked.connect(self.wcApplySetpoint)
        self.wcSwitchBtn.clicked.connect(self.wcSwitch)

        # layout of water circulator control panel
        groupBox = QGroupBox('Thermo Scientific Water Circulator')

        grid = QGridLayout()
        grid.addWidget(QLabel('Setpoint: '), 0, 0, Qt.AlignRight)
        grid.addWidget(self.wcSetpointEdit, 0, 1)
        grid.addWidget(QLabel(u'\u00B0C'), 0, 2)
        grid.addWidget(self.wcApplySetpointBtn, 0, 3)
        grid.addWidget(QLabel('Readback: '), 1, 0, Qt.AlignRight)
        grid.addWidget(self.wcReadbackEdit, 1, 1)
        grid.addWidget(QLabel(u'\u00B0C'), 1, 2)
        grid.addWidget(self.wcSwitchBtn, 2, 3)
        grid.addWidget(self.wcLogDataCkB, 3, 0, Qt.AlignRight)
        grid.addWidget(QLabel('Log Data to File'), 3, 1, 1, 3)

        groupBox.setLayout(grid)

        return groupBox

    def createDarkRateScan(self):
        # widgets belonging to this tab
        self.drsFebCB = QComboBox()
        self.drsFebCB.addItems(['All', '0', '1'])
        self.drsChCB = QComboBox()
        self.drsChCB.addItems(['All']+[str(i) for i in range(32)])
        # editors for setting threshold
        self.drsDac1From = QLineEdit(text='220')
        self.drsDac1To = QLineEdit(text='220')
        self.drsDac1Step = QLineEdit(text='1')
        ### Legacy variables below
        self.drsDac2From = QLineEdit(text='220')
        self.drsDac2To = QLineEdit(text='220')
        self.drsDac2Step = QLineEdit(text='1')
        ### Legacy variables above
        self.drsEditPreGain = QLineEdit(text='55')
        self.drsEditNEvt = QLineEdit('10000')
        self.drsStartBtn = QPushButton(text='Start Scan')
        self.drsStartBtn.clicked.connect(self.sendDrJsonMsg)

        # lay out widgets
        grid = QGridLayout()

        groupBox1 = QGroupBox('Channels to Scan')
        grid1 = QGridLayout()
        grid1.addWidget(QLabel('FEB'), 0, 0, Qt.AlignRight)
        grid1.addWidget(self.drsFebCB, 0, 1, Qt.AlignLeft)
        grid1.addWidget(QLabel('Channel'), 0, 2, Qt.AlignRight)
        grid1.addWidget(self.drsChCB, 0, 3, Qt.AlignLeft)
        groupBox1.setLayout(grid1)
        grid.addWidget(groupBox1, 0, 0, 1, 5)

        groupBox2 = QGroupBox('Thresholds to Scan')
        grid2 = QGridLayout()
        grid2.addWidget(QLabel('from'), 0, 1, Qt.AlignCenter)
        grid2.addWidget(QLabel('to'), 0, 2, Qt.AlignCenter)
        grid2.addWidget(QLabel('step'), 0, 3, Qt.AlignCenter)
        grid2.addWidget(QLabel('DAC'), 1, 0, Qt.AlignRight)
        grid2.addWidget(self.drsDac1From, 1, 1, Qt.AlignCenter)
        grid2.addWidget(self.drsDac1To, 1, 2, Qt.AlignCenter)
        grid2.addWidget(self.drsDac1Step, 1, 3, Qt.AlignCenter)
        groupBox2.setLayout(grid2)
        grid.addWidget(groupBox2, 1, 0, 1, 5)
        

        # grid.addWidget(QLabel('FEB2 DAC from'), 1, 2, Qt.AlignRight)
        # grid.addWidget(self.drsDac2From, 1, 3, Qt.AlignCenter)
        # grid.addWidget(QLabel('FEB2 DAC to'), 2, 2, Qt.AlignRight)
        # grid.addWidget(self.drsDac2To, 2, 3, Qt.AlignCenter)
        # grid.addWidget(QLabel('FEB2 DAC step'), 3, 2, Qt.AlignRight)
        # grid.addWidget(self.drsDac2Step, 3, 3, Qt.AlignCenter)

        groupBox3 = QGroupBox('Other Parameters')
        grid3 = QGridLayout()
        grid3.addWidget(QLabel('preamp gain'), 0, 0, Qt.AlignRight)
        grid3.addWidget(self.drsEditPreGain, 0, 1, Qt.AlignLeft)
        grid3.addWidget(QLabel('number of events'), 0, 2, Qt.AlignRight)
        grid3.addWidget(self.drsEditNEvt, 0, 3, Qt.AlignLeft)
        groupBox3.setLayout(grid3)
        grid.addWidget(groupBox3, 4, 0, 1, 5)

        grid.addWidget(self.drsStartBtn, 5, 4, Qt.AlignCenter)
        return grid

    def createParameterScan(self):
        # member widgets
        self.parKeys = ['vol', 'feb1dac', 'feb1gain', 'feb1bias', 'feb2dac', 'feb2gain', 'feb2bias', 'temp']
        self.editParVal = dict()
        for key in self.parKeys:
            self.editParVal[key] = dict()

        self.editParVal['vol']['from'] = QLineEdit('58')
        self.editParVal['vol']['to'] = QLineEdit('60')
        self.editParVal['vol']['step'] = QLineEdit('1')
        self.editParVal['feb1dac']['from'] = QLineEdit('200')
        self.editParVal['feb1dac']['to'] = QLineEdit('200')
        self.editParVal['feb1dac']['step'] = QLineEdit('1')
        self.editParVal['feb1gain']['from'] = QLineEdit('52')
        self.editParVal['feb1gain']['to'] = QLineEdit('52')
        self.editParVal['feb1gain']['step'] = QLineEdit('1')
        self.editParVal['feb1bias']['from'] = QLineEdit('200')
        self.editParVal['feb1bias']['to'] = QLineEdit('200')
        self.editParVal['feb1bias']['step'] = QLineEdit('0')
        self.editParVal['feb2dac']['from'] = QLineEdit('230')
        self.editParVal['feb2dac']['to'] = QLineEdit('230')
        self.editParVal['feb2dac']['step'] = QLineEdit('0')
        self.editParVal['feb2gain']['from'] = QLineEdit('52')
        self.editParVal['feb2gain']['to'] = QLineEdit('52')
        self.editParVal['feb2gain']['step'] = QLineEdit('1')
        self.editParVal['feb2bias']['from'] = QLineEdit('200')
        self.editParVal['feb2bias']['to'] = QLineEdit('200')
        self.editParVal['feb2bias']['step'] = QLineEdit('0')
        self.editParVal['temp']['from'] = QLineEdit('18')
        self.editParVal['temp']['to'] = QLineEdit('22')
        self.editParVal['temp']['step'] = QLineEdit('1')
        self.editNEvt = QLineEdit('10000')
        self.scanBut = QPushButton(text='Start Scan')
        self.scanBut.clicked.connect(self.sendJsonMsg)

        grid = QGridLayout()
        grid.addWidget(QLabel('Include'), 0, 0, Qt.AlignCenter)
        grid.addWidget(QLabel('Parameter'), 0, 1, Qt.AlignCenter)
        grid.addWidget(QLabel('From'), 0, 2, 1, 2, Qt.AlignCenter)
        grid.addWidget(QLabel('To'), 0, 4, 1, 2, Qt.AlignCenter)
        grid.addWidget(QLabel('Step'), 0, 6, 1, 2, Qt.AlignCenter)

        grid.addWidget(QLabel('Voltage'), 1, 1)
        grid.addWidget(self.editParVal['vol']['from'], 1, 2)
        grid.addWidget(QLabel('V'), 1, 3)
        grid.addWidget(self.editParVal['vol']['to'], 1, 4)
        grid.addWidget(QLabel('V'), 1, 5)
        grid.addWidget(self.editParVal['vol']['step'], 1, 6)
        grid.addWidget(QLabel('V'), 1, 7)
        
        grid.addWidget(QLabel('FEB1 DAC'), 2, 1)
        grid.addWidget(self.editParVal['feb1dac']['from'], 2, 2)
        grid.addWidget(self.editParVal['feb1dac']['to'], 2, 4)
        grid.addWidget(self.editParVal['feb1dac']['step'], 2, 6)

        grid.addWidget(QLabel('FEB1 Gain'), 3, 1)
        grid.addWidget(self.editParVal['feb1gain']['from'], 3, 2)
        grid.addWidget(self.editParVal['feb1gain']['to'], 3, 4)
        grid.addWidget(self.editParVal['feb1gain']['step'], 3, 6)

        grid.addWidget(QLabel('FEB1 Bias'), 4, 1)
        grid.addWidget(self.editParVal['feb1bias']['from'], 4, 2)
        grid.addWidget(self.editParVal['feb1bias']['to'], 4, 4)
        grid.addWidget(self.editParVal['feb1bias']['step'], 4, 6)

        grid.addWidget(QLabel('FEB2 DAC'), 5, 1)
        grid.addWidget(self.editParVal['feb2dac']['from'], 5, 2)
        grid.addWidget(self.editParVal['feb2dac']['to'], 5, 4)
        grid.addWidget(self.editParVal['feb2dac']['step'], 5, 6)

        grid.addWidget(QLabel('FEB2 Gain'), 6, 1)
        grid.addWidget(self.editParVal['feb2gain']['from'], 6, 2)
        grid.addWidget(self.editParVal['feb2gain']['to'], 6, 4)
        grid.addWidget(self.editParVal['feb2gain']['step'], 6, 6)

        grid.addWidget(QLabel('FEB2 Bias'), 7, 1)
        grid.addWidget(self.editParVal['feb2bias']['from'], 7, 2)
        grid.addWidget(self.editParVal['feb2bias']['to'], 7, 4)
        grid.addWidget(self.editParVal['feb2bias']['step'], 7, 6)

        grid.addWidget(QLabel('Temperature'), 8, 1)
        grid.addWidget(self.editParVal['temp']['from'], 8, 2)
        grid.addWidget(QLabel(u'\u00B0C'), 8, 3)
        grid.addWidget(self.editParVal['temp']['to'], 8, 4)
        grid.addWidget(QLabel(u'\u00B0C'), 8, 5)
        grid.addWidget(self.editParVal['temp']['step'], 8, 6)
        grid.addWidget(QLabel(u'\u00B0C'), 8, 7)

        grid.addWidget(QLabel('number of events'), 9, 1, Qt.AlignRight)
        grid.addWidget(self.editNEvt, 9, 2)
        grid.addWidget(self.scanBut, 9, 6)

        # put on checkboxes
        self.includeParCB = dict()
        for i in range(len(self.parKeys)):
            k = self.parKeys[i]
            self.includeParCB[k] = QCheckBox()
            self.includeParCB[k].setChecked(True)
            grid.addWidget(self.includeParCB[k], i+1, 0, Qt.AlignCenter)
        
        # After discussion with the boss, these parameters might not need to be
        # scanned. Therefore by default uncheck the checkboxes.
        for parkey in ['feb1bias', 'feb2dac', 'feb2bias', 'feb2gain']:
            self.includeParCB[parkey].setChecked(False)
            self.includeParCB[parkey].setEnabled(False)
        # Temperature scan takes much time, so disabe by default
        self.includeParCB['temp'].setChecked(False)

        return grid

    def createPulserControl(self):
        groupBox = QGroupBox('Tektronix AFG3252 Function Generator')
        
        grid = QGridLayout()
        grid.addWidget(QLabel('Channel: '), 0, 0, Qt.AlignRight)
        grid.addWidget(self.fgChSel, 0, 1)
        grid.addWidget(QLabel('Recall Waveform: '), 1, 0, Qt.AlignRight)
        grid.addWidget(self.fgRecallChSel, 1, 1)
        grid.addWidget(QLabel('Set Pulse Frequency: '), 2, 0, Qt.AlignRight)
        grid.addWidget(self.fgFreqEdit, 2, 1)
        grid.addWidget(QLabel('kHz'), 2, 2)
        grid.addWidget(self.fgFreqBtn, 2, 3)
        grid.addWidget(QLabel('Set Pulse Amplitude: '), 3, 0, Qt.AlignRight)
        grid.addWidget(self.fgAmplEdit, 3, 1)
        grid.addWidget(QLabel('Vpp'), 3, 2)
        grid.addWidget(self.fgAmplBtn, 3, 3)
        grid.addWidget(self.fgOutputSwitch, 4, 3)

        groupBox.setLayout(grid)

        return groupBox

    def createTemperatureSensor(self):
        groupBox = QGroupBox('T2K Temperature Sensor')
        self.tsLogDataCkB = QCheckBox()

        grid = QGridLayout()
        grid.addWidget(QLabel('Sensor: '), 0, 0)
        grid.addWidget(self.tsTemperatureCB, 0, 1)
        grid.addWidget(self.tsTemperatureEdit, 0, 2)
        grid.addWidget(QLabel(u'\u00B0C'), 0, 3)
        grid.addWidget(self.tsLogDataCkB, 1, 0, Qt.AlignRight)
        grid.addWidget(QLabel('Log Data to File'), 1, 1, 1, 4)
        grid.addWidget(self.tsView, 2, 0, 2, 4)
        self.tsView.setCentralItem(self.tsLo)
        self.tsView.show()
        self.tsView.resize(200, 100)
        yaxis = pg.AxisItem('left')
        yaxis.setLabel(text=u'Temperature (\u00B0C)', units=None)
        self.tsPlot = self.tsLo.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom'), 'left': yaxis})
        ## Below is how to set axis ranges. If not set, scales change automatically.
        # self.tsPlot.setYRange(0, 40)
        # self.tsPlot.setXRange(timestamp(), timestamp() + 100)
        self.plotCurve = self.tsPlot.plot(pen='b')
        self.tsView.setBackground('w')

        groupBox.setLayout(grid)
        return groupBox

    def createVoltageControl(self):
        groupBox = QGroupBox('Agilent N6700B Power Unit')

        grid = QGridLayout()
        grid.addWidget(QLabel('Output Channel: '), 0, 0, Qt.AlignRight)
        grid.addWidget(self.puChCB, 0, 1)
        grid.addWidget(QLabel('Voltage Set: '), 1, 0, Qt.AlignRight)
        grid.addWidget(self.puVsetEdit, 1, 1)
        grid.addWidget(QLabel('V'), 1, 2)
        grid.addWidget(QLabel('Voltage Read: '), 2, 0, Qt.AlignRight)
        grid.addWidget(self.puVRbEdit, 2, 1)
        grid.addWidget(QLabel('V'), 2, 2)
        grid.addWidget(self.puVoltageSwitch, 3, 1)

        groupBox.setLayout(grid)

        return groupBox

    def fgToggleOutput(self):
        # if button is checked 
        if self.fgOutputSwitch.isChecked(): 
  
            # setting background color to light-blue 
            self.fgOutputSwitch.setStyleSheet("background-color : lightgreen")
            self.fgOutputSwitch.setText('Switch Off')
            ch_str = self.fgChSel.currentText()
            if ch_str in ['1', '2']:
                self.devFunGen.enableOutput(int(ch_str))
            else:
                self.devFunGen.enableOutput(1)
                self.devFunGen.enableOutput(2)
  
        # if it is unchecked 
        else: 
  
            # set background color back to light-grey 
            self.fgOutputSwitch.setStyleSheet("background-color : lightgrey")
            self.fgOutputSwitch.setText('Switch On')
            ch_str = self.fgChSel.currentText()
            if ch_str in ['1', '2']:
                self.devFunGen.disableOutput(int(ch_str))
            else:
                self.devFunGen.disableOutput(1)
                self.devFunGen.disableOutput(2)
    
    def fgApplyAmpl(self):
        ampl = float(self.fgAmplEdit.text())
        if self.fgChSel.currentText() != 'all':
            ch = int(self.fgChSel.currentText())
            self.devFunGen.setAmplitude(ch, '{}'.format(ampl))
        else:
            for ch in [1, 2]:
                self.devFunGen.setAmplitude(ch, '{}'.format(ampl))

    def fgApplyFreq(self):
        freq = float(self.fgFreqEdit.text())
        self.devFunGen.setFrequency('{} kHz'.format(freq))

    def fgRecallState(self):
        sel_state = int(self.fgRecallChSel.currentText())
        self.devFunGen.recallWaveform(sel_state)
        freq = float(self.devFunGen.querySetFrequency())/1000.
        self.fgFreqEdit.setText(('{:10.9f}'.format(freq)).strip())
        sel_ch = int(self.fgChSel.currentText()) if self.fgChSel.currentText() != 'all' else 1
        amp = float(self.devFunGen.querySetAmplitude(sel_ch))
        self.fgAmplEdit.setText(('{:10.4f}'.format(amp)).strip())

    def pollMsg(self):
        socks = dict(self.poller.poll(0))
        if self.socket in socks and socks[self.socket] == zmq.POLLIN:
            recv_str = self.socket.recv().decode()
            # Check if any message from DAQ indicates the DAQ status
            try:
                a_json = json.loads(recv_str)
                if 'daq status' in a_json.keys():
                    self.daqReady = True if a_json['daq status'] == 'ready' else False
                if 'quit scan' in a_json.keys():
                     if a_json['quit scan'] == 'true':
                        self.psQueue = []
            except:
                message = self.msgBox.toPlainText() + '\n{}'.format(recv_str)
                self.msgBox.setText(message)
        
        # Issue data taking command to the DAQ if necessary
        if self.daqReady and len(self.psQueue) > 0:
            par_table = self.psQueue[0]
            if 'vol' in par_table.keys():
                if self.puVoltageSwitch.isChecked():
                    self.puVoltageSwitch.setChecked(False)
                self.puVsetEdit.setText(str(par_table['vol']))
                self.puVoltageSwitch.setChecked(True)
                par_table['number of events'] = self.editNEvt.text()
                par_table['parameter scan'] = 'on'
                par_table['bias_voltage'] = self.puVsetEdit.text()
                par_table['temperature'] = statistics.mean([self.tsY[sen_it][-1] for sen_it in ['T0', 'T1', 'T2', 'T3', 'T4']])
                if self.fgOutputSwitch.isChecked:
                    par_table['led_Vpp'] = float(self.fgAmplEdit.text())
                else:
                    par_table['led_Vpp'] = -1
            self.socket.send_string(json.dumps(par_table))
            self.daqReady = False
            self.psQueue = self.psQueue[1:]

    def puPowerSwitch(self):
        # get the active channel
        active_ch = int(self.puChCB.currentText())

        # if button is checked
        if self.puVoltageSwitch.isChecked(): 
            # voltage safeguard
            vol_uplim = 66
            Vset = float(self.puVsetEdit.text())
            if Vset > vol_uplim:
                print('Input voltage {} V is too high!'.format(vol_uplim))
                return
            
            # setting background color to light-blue
            self.puVoltageSwitch.setStyleSheet("background-color : lightgreen")
            self.puVoltageSwitch.setText('Switch Off')
            self.puVsetEdit.setEnabled(False)
            self.devPowerUnit.set_voltage(active_ch, Vset)
            self.devPowerUnit.power_on(active_ch)
  
        # if it is unchecked
        else:
  
            # set background color back to light-grey
            self.puVoltageSwitch.setStyleSheet("background-color : lightgrey")
            self.puVoltageSwitch.setText('Switch On')
            self.puVsetEdit.setEnabled(True)
            self.devPowerUnit.power_off(active_ch)
    
    def puReadbackVoltage(self):
        Vrb = float(self.devPowerUnit.query_voltage(self.puChCB.currentText()))
        self.puVRbEdit.setText(('{:10.4f}'.format(Vrb)).lstrip())
    
    def sendDrJsonMsg(self):
        packedMsg = dict()
        packedMsg['dark rate scan'] = dict()
        packedMsg['dark rate scan']['feb'] = self.drsFebCB.currentText()
        packedMsg['dark rate scan']['ch'] = self.drsChCB.currentText()
        packedMsg['dark rate scan']['dac1_from'] = self.drsDac1From.text()
        packedMsg['dark rate scan']['dac1_to'] = self.drsDac1To.text()
        packedMsg['dark rate scan']['dac1_step'] = self.drsDac1Step.text()
        packedMsg['dark rate scan']['dac2'] = self.drsDac2From.text()
        packedMsg['dark rate scan']['preamp_gain'] = self.drsEditPreGain.text()
        packedMsg['drs_nevt'] = self.drsEditNEvt.text()
        packedMsg['bias_voltage'] = self.puVsetEdit.text()
        packedMsg['temperature'] = statistics.mean([self.tsY[sen_it][-1] for sen_it in ['T0', 'T1', 'T2', 'T3', 'T4']])
        print('Slow control sending:', json.dumps(packedMsg))
        self.psQueue = []
        self.psQueue.append(packedMsg)

    def sendJsonMsg(self):
        packedMsg = dict()
        for par in self.parKeys:
            if self.includeParCB[par].isChecked():
                packedMsg[par] = dict()
                for val_st in ['from', 'to', 'step']:
                    packedMsg[par][val_st] = self.editParVal[par][val_st].text()
        try:
            nevt = int(self.editNEvt.text())
        except:
            print('Error processing number of events!')
            return
        packedMsg['number of events'] = self.editNEvt.text()
        print('Slow control sending:', json.dumps(packedMsg))
        self.socket.send_string(json.dumps(packedMsg))
        # Put the temperature and voltage parameters to the scan queue.
        temp_vals = []
        if self.includeParCB['temp'].isChecked():
            temp_from = float(self.editParVal['temp']['from'].text())
            temp_to = float(self.editParVal['temp']['to'].text())
            temp_step = float(self.editParVal['temp']['step'].text())
            if temp_step > 0:
                # add a small epsilon to include the endpoint
                temp_vals = list(np.arange(temp_from, temp_to+temp_step/1e5, temp_step))
        vol_vals = []
        if self.includeParCB['vol'].isChecked():
            vol_from = float(self.editParVal['vol']['from'].text())
            vol_to = float(self.editParVal['vol']['to'].text())
            vol_step = float(self.editParVal['vol']['step'].text())
            if vol_step > 0:
                # add a small epsilon to include the endpoint
                vol_vals = list(np.arange(vol_from, vol_to+vol_step/1e5, vol_step))
        # Scan preamp gain. One value for both FEBs.
        gain_vals = []
        if self.includeParCB['feb1gain'].isChecked():
            gain_from = float(self.editParVal['feb1gain']['from'].text())
            gain_to = float(self.editParVal['feb1gain']['to'].text())
            gain_step = float(self.editParVal['feb1gain']['step'].text())
            if gain_step > 0:
                # add a small epsilon to include the endpoint
                gain_vals = list(np.arange(gain_from, gain_to+gain_step/1e5, gain_step))
        # Scan threshold. One value for both FEBs.
        threshold_vals = []
        if self.includeParCB['feb1dac'].isChecked():
            threshold_from = float(self.editParVal['feb1dac']['from'].text())
            threshold_to = float(self.editParVal['feb1dac']['to'].text())
            threshold_step = float(self.editParVal['feb1dac']['step'].text())
            if threshold_step > 0:
                # add a small epsilon to include the endpoint
                threshold_vals = list(np.arange(threshold_from, threshold_to+threshold_step/1e5, threshold_step))
        # assemble the parameter scan queue
        ntemp = len(temp_vals) if len(temp_vals) > 0 else 1
        nvol = len(vol_vals) if len(vol_vals) > 0 else 1
        ngain = len(gain_vals) if len(gain_vals) > 0 else 1
        itemp = 0
        self.psQueue = []
        for i in range(ntemp):
            ivol = 0
            for j in range(nvol):
                self.psQueue.append(dict())
                if itemp < len(temp_vals):
                    self.psQueue[-1]['temp'] = temp_vals[itemp]
                if ivol < len(vol_vals):
                    self.psQueue[-1]['vol'] = vol_vals[ivol]
                    ivol += 1
            itemp += 1
        
        # add threshold into queue
        proliferate_list = []
        for threshold in threshold_vals:
            for j in range(len(self.psQueue)):
                self.psQueue[j]['dac'] = threshold
                proliferate_list.append(self.psQueue[j].copy())
        self.psQueue = proliferate_list

        # add gain and time into queue
        current_time = datetime.datetime.now()
        proliferate_list = []
        for gain in gain_vals:
            for j in range(len(self.psQueue)):
                self.psQueue[j]['gain'] = gain
                self.psQueue[j]['time'] = current_time.strftime('%H%M%S')
                proliferate_list.append(self.psQueue[j].copy())
        self.psQueue = proliferate_list
        print('Packaged message:', self.psQueue)

    def tsLogReadouts(self):
        if not self.tsLogDataCkB.isChecked():
            return
        # retrieve data and store them to the dataframe
        temp_readings = self.devTempSen.query_temperature()
        self.dfTempSensor['Datetime'] = [datetime.datetime.now()]
        for i in range(5):
            sen_id = 'T{}'.format(i)
            self.dfTempSensor[sen_id] = [float(temp_readings[sen_id])]
        # self.msgBox.append(self.dfTempSensor.to_string())

        # prepare the output directory
        save_dir = self.prepare_metadata_directory()

        # file name to store the temperature data
        save_fn = 'temperature_sensor_readings.csv'
        save_fpn = os.path.join(save_dir, save_fn)
        self.dfTempSensor.to_csv(save_fpn, mode='a',
                                 header=not os.path.exists(save_fpn),
                                 index=False)


    def prepare_metadata_directory(self):
        # prepare the metadata output directory
        app_dir = os.path.dirname(os.path.abspath(__file__))
        meta_dir = os.path.join(app_dir, '../DAQ/metadata')
        if not os.path.exists(meta_dir):
            os.makedirs(meta_dir)
        return meta_dir

    def tsReadTemperature(self):
        sen_id = self.tsTemperatureCB.currentText()

        ## If I open the temperature sensor as a member variable,
        ## temperature readings will all turn empty after the first reading.
        ## Don't quite know what happens here. However, opening the connection
        ## everytime when I want to get readings seems to be a workaround...
        devTempSen = T2KTEMPSENSOR()
        #temp_readings = devTempSen.query_temperature()
        temp_readings = self.devTempSen.query_temperature()
        # print(temp_readings)

        for sen_it in ['T0', 'T1', 'T2', 'T3', 'T4']:
            if sen_it in temp_readings.keys():
                # store data
                if float(temp_readings[sen_it]) > 0.1:
                    #Check removes zero points from graph. Not Ideal.
                    self.tsX[sen_it].append(timestamp())
                    self.tsY[sen_it].append(float(temp_readings[sen_it]))

        if sen_id in temp_readings.keys():
            # display reading of the specified channel
            Trb = float(temp_readings[sen_id])
            self.tsTemperatureEdit.setText('{:10.2f}'.format(Trb).strip())
        else:
            self.tsTemperatureEdit.setText('')

        # update the temperature plot
        self.plotCurve.setData(list(self.tsX[sen_id]), list(self.tsY[sen_id]), pen=pg.mkPen(color=(0, 0, 255), width=3))

    def wcApplySetpoint(self):
        target_temp = float(self.wcSetpointEdit.text())
        self.devWaterCirculator.set_setpoint(target_temp)
    
    def wcLogInternalTemperature(self):
        if not self.wcLogDataCkB.isChecked():
            return
        # retrieve data and store them to the dataframe
        temp_readback = self.devWaterCirculator.read_internal_temperature()
        self.dfWcIntTemp['Datetime'] = [datetime.datetime.now()]
        self.dfWcIntTemp['Internal Temperature'] = [temp_readback]

        # prepare the output directory
        save_dir = self.prepare_metadata_directory()

        # file name to store the temperature data
        save_fn = 'water_circulator_readback.csv'
        save_fpn = os.path.join(save_dir, save_fn)
        self.dfWcIntTemp.to_csv(save_fpn, mode='a',
                                header=not os.path.exists(save_fpn),
                                index=False)

    def wcReadInternalTemperature(self):
        text=str(self.devWaterCirculator.read_internal_temperature())
        self.wcReadbackEdit.setText(text)

    def wcSwitch(self):
        if self.wcSwitchBtn.isChecked(): 
            
            # setting background color to light-green
            self.wcSwitchBtn.setStyleSheet("background-color : lightgreen")
            self.wcSwitchBtn.setText('Switch Off')
            self.wcSetpointEdit.setEnabled(False)
            self.devWaterCirculator.set_on_array()
  
        # if it is unchecked
        else:
  
            # set background color back to light-grey
            self.wcSwitchBtn.setStyleSheet("background-color : lightgrey")
            self.wcSwitchBtn.setText('Switch On')
            self.wcSetpointEdit.setEnabled(True)
            self.devWaterCirculator.set_off_array()
        


if __name__ == '__main__':
    app = QApplication(sys.argv)
    clock = Window()
    clock.show()
    sys.exit(app.exec_())
