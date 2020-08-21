#!/usr/bin/env python

import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                'agilent-n6700b-power-system'))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                't2k-temperature-sensor'))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                'tektronix-afg3252-function-generator'))
import socket

# for making plots
import pyqtgraph as pg

# other utilities
import collections
import datetime, time
import numpy as np
import signal

# device API imports
from AFG3252 import AFG3252
from N6700B import N6700B
from T2KTEMPSENSOR import T2KTEMPSENSOR

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
        self.puVoltageSwitch.clicked.connect(self.puPowerSwitch)
        self.puChCB = QComboBox()
        self.puChCB.addItems(['all', '1', '2', '3', '4'])
        self.puChCB.setCurrentIndex(4)
        self.puChCB.setEnabled(False)
        self.puVsetEdit = QLineEdit('58')
        self.puVsetEdit.setValidator(QDoubleValidator(bottom=0, top=60, decimals=10))
        self.puVRbEdit = QLineEdit()

        # function generator stars with fg
        self.fgChSel = QComboBox()
        self.fgChSel.addItems(['1', '2'])
        self.fgChSel.setCurrentIndex(0)
        self.fgOutputSwitch = QPushButton(text='Switch On')
        self.fgOutputSwitch.setCheckable(True)
        self.fgOutputSwitch.clicked.connect(self.fgToggleOutput)
        self.fgRecallChSel = QComboBox()
        self.fgRecallChSel.addItems(['0', '1', '2', '3', '4'])
        # recall waveform when a saved state is selected
        self.fgRecallChSel.activated.connect(self.fgRecallState)
        self.fgRecallChSel.setCurrentIndex(4)
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
        self.msgBox.setText('Welcome to the control application!\n')
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
        self.tsPoints = 33
        self.tsX = dict()
        self.tsY = dict()
        for sen in ['T0', 'T1', 'T2', 'T3', 'T4']:
            self.tsX[sen] = collections.deque(maxlen=self.tsPoints)
            self.tsY[sen] = collections.deque(maxlen=self.tsPoints)
        # end of widgets declaration *******************************************

        grid = QGridLayout()
        grid.addWidget(self.createVoltageControl(), 0, 0, 1, 1)
        grid.addWidget(self.createPulserControl(), 0, 1, 1, 1)
        grid.addWidget(self.msgBox, 1, 0, 1, 2)
        grid.addWidget(self.createTemperatureSensor(), 0, 2, 2, 1)
        self.setLayout(grid)

        self.setWindowTitle('MPPC Slow Control App')
        self.resize(1000, 300)

        # use a figure as this app's icon
        # ref: https://stackoverflow.com/questions/42602713/how-to-set-a-window-icon-with-pyqt5
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QtGui.QIcon(os.path.join(scriptDir, 'logo.png')))

        # use a timer for voltage readback
        # ref: https://pythonpyqt.com/qtimer/
        self.timer = QTimer()
        self.timer.start(self.timerTime)
        self.timer.timeout.connect(self.puReadbackVoltage)
        self.puReadbackVoltage()
        self.timer.timeout.connect(self.tsReadTemperature)
        self.tsReadTemperature()

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

        grid = QGridLayout()
        grid.addWidget(QLabel('Sensor: '), 0, 0)
        grid.addWidget(self.tsTemperatureCB, 0, 1)
        grid.addWidget(self.tsTemperatureEdit, 0, 2)
        grid.addWidget(QLabel(u'\u00B0C'), 0, 3)
        grid.addWidget(self.tsView, 1, 0, 2, 4)
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
        grid.addWidget(self.puVoltageSwitch, 3, 2)

        groupBox.setLayout(grid)

        return groupBox

    def fgToggleOutput(self):
        # if button is checked 
        if self.fgOutputSwitch.isChecked(): 
  
            # setting background color to light-blue 
            self.fgOutputSwitch.setStyleSheet("background-color : lightgreen")
            self.fgOutputSwitch.setText('Switch Off')
            self.devFunGen.enableOutput(1)
  
        # if it is unchecked 
        else: 
  
            # set background color back to light-grey 
            self.fgOutputSwitch.setStyleSheet("background-color : lightgrey")
            self.fgOutputSwitch.setText('Switch On')
            self.devFunGen.disableOutput(1)
    
    def fgApplyAmpl(self):
        ampl = float(self.fgAmplEdit.text())
        ch = int(self.fgChSel.currentText())
        self.devFunGen.setAmplitude(ch, '{}'.format(ampl))

    def fgApplyFreq(self):
        freq = float(self.fgFreqEdit.text())
        self.devFunGen.setFrequency('{} kHz'.format(freq))

    def fgRecallState(self):
        sel_state = int(self.fgRecallChSel.currentText())
        self.devFunGen.recallWaveform(sel_state)
        freq = float(self.devFunGen.querySetFrequency())/1000.
        self.fgFreqEdit.setText(('{:10.9f}'.format(freq)).strip())
        sel_ch = int(self.fgChSel.currentText())
        amp = float(self.devFunGen.querySetAmplitude(sel_ch))
        self.fgAmplEdit.setText(('{:10.4f}'.format(amp)).strip())

    def puPowerSwitch(self):
        # get the active channel
        active_ch = int(self.puChCB.currentText())

        # if button is checked
        if self.puVoltageSwitch.isChecked(): 
            # voltage safeguard
            vol_uplim = 60
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
    
    def tsReadTemperature(self):
        sen_id = self.tsTemperatureCB.currentText()

        ## If I open the temperature sensor as a member variable,
        ## temperature readings will all turn empty after the first reading.
        ## Don't quite know what happens here. However, opening the connection
        ## everytime when I want to get readings seems to be a workaround...
        # devTempSen = T2KTEMPSENSOR()
        # temp_readings = devTempSen.query_temperature()
        temp_readings = self.devTempSen.query_temperature()
        # print(temp_readings)

        for sen_it in ['T0', 'T1', 'T2', 'T3', 'T4']:
            if sen_it in temp_readings.keys():
                # store data
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

        


if __name__ == '__main__':
    app = QApplication(sys.argv)
    clock = Window()
    clock.show()
    sys.exit(app.exec_())
