#!/usr/bin/env python

import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                'agilent-n6700b-power-system'))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                'tektronix-afg3252-function-generator'))
import socket

from AFG3252 import AFG3252
from N6700B import N6700B
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class Window(QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        # get the control handles
        # function generator
        self.devFunGen = AFG3252(socket.gethostbyname('192.168.0.101'))
        # power unit
        self.devPowerUnit = N6700B('192.168.0.201')

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

        # a message box
        self.msgBox = QTextEdit()
        self.msgBox.setText('Welcome to the control application!\n')
        self.msgBox.setReadOnly(True)
        # end of widgets declaration *******************************************

        grid = QGridLayout()
        grid.addWidget(self.createVoltageControl(), 0, 0, 1, 1)
        grid.addWidget(self.createPulserControl(), 0, 1, 1, 1)
        grid.addWidget(self.msgBox, 1, 0, 1, 2)
        self.setLayout(grid)

        self.setWindowTitle('MPPC Slow Control App')
        self.resize(800, 00)

        # use a figure as this app's icon
        # ref: https://stackoverflow.com/questions/42602713/how-to-set-a-window-icon-with-pyqt5
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QtGui.QIcon(os.path.join(scriptDir, 'logo.png')))

        # use a timer for voltage readback
        # ref: https://pythonpyqt.com/qtimer/
        self.timer = QTimer()
        self.timer.start(2000)
        self.timer.timeout.connect(self.puReadbackVoltage)

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    clock = Window()
    clock.show()
    sys.exit(app.exec_())
