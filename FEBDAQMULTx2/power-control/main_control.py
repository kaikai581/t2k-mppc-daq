#!/usr/bin/env python

import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                'agilent-n6700b-power-system'))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                'tektronix-afg3252-function-generator'))
import socket

from AFG3252 import AFG3252
from N6700B import N6700B
from PyQt5.QtCore import Qt
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
        self.puChEdit = QComboBox()
        self.puChEdit.addItems(['all', '1', '2', '3', '4'])
        self.puChEdit.setCurrentIndex(4)
        self.puChEdit.setEnabled(False)
        self.puVsetEdit = QLineEdit('58')
        self.puVsetEdit.setValidator(QDoubleValidator(bottom=0, top=60, decimals=10))

        # function generator stars with fg
        self.fgOutputSwitch = QPushButton(text='Switch On')
        self.fgOutputSwitch.setCheckable(True)
        self.fgOutputSwitch.clicked.connect(self.fgToggleOutput)

        # a message box
        self.msgBox = QTextEdit()
        self.msgBox.setText('Welcome to the control application!\n')
        self.msgBox.setReadOnly(True)
        # end of widgets declaration *******************************************

        grid = QGridLayout()
        grid.addWidget(self.createVoltageControl(), 0, 0, 1, 1)
        grid.addWidget(self.createPulserControl(), 0, 1, 1, 1)
        grid.addWidget(self.msgBox, 2, 0, 1, 2)
        self.setLayout(grid)

        self.setWindowTitle('MPPC Power Control App')
        self.resize(600, 300)

    def createPulserControl(self):
        groupBox = QGroupBox('Tektronix AFG3252 Function Generator')
        
        grid = QGridLayout()
        grid.addWidget(self.fgOutputSwitch, 0, 0)

        groupBox.setLayout(grid)

        return groupBox

    def createVoltageControl(self):
        groupBox = QGroupBox('Agilent N6700B Power Unit')

        grid = QGridLayout()
        grid.addWidget(QLabel('Output Channel: '), 0, 0, Qt.AlignRight)
        grid.addWidget(self.puChEdit, 0, 1)
        grid.addWidget(QLabel('Voltage Set: '), 1, 0, Qt.AlignRight)
        grid.addWidget(self.puVsetEdit, 1, 1)
        grid.addWidget(QLabel('V'), 1, 2)
        grid.addWidget(QLabel('Voltage Read: '), 2, 0, Qt.AlignRight)
        grid.addWidget(QLineEdit(), 2, 1)
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
    
    def puPowerSwitch(self):
        # get the active channel
        active_ch = int(self.puChEdit.currentText())

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
            self.devPowerUnit.set_voltage(active_ch, Vset)
            self.devPowerUnit.power_on(active_ch)
  
        # if it is unchecked 
        else: 
  
            # set background color back to light-grey 
            self.puVoltageSwitch.setStyleSheet("background-color : lightgrey")
            self.puVoltageSwitch.setText('Switch On')
            self.devPowerUnit.power_off(active_ch)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    clock = Window()
    clock.show()
    sys.exit(app.exec_())
