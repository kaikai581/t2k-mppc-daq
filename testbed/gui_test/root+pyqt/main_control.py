#!/usr/bin/env python

import sys
sys.path.append('../../agilent-n6700b-power-system')
import json
import os
import threading
import zmq
from N6700B import N6700B
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QTimer
from PyQt5.QtWidgets import *

# For a GUI application, the receiver needs to run in a separate thread for
# not blocking the app. Ref:
# https://stackoverflow.com/questions/62898418/how-to-display-an-output-from-zmq-to-a-qt-gui-in-run-time
class ZMQReceiver(QObject):
    dataChanged = pyqtSignal(bytes)

    def start(self):
        threading.Thread(target=self._execute, daemon=True).start()

    def _execute(self):
        context = zmq.Context()
        consumer_receiver = context.socket(zmq.PAIR)
        consumer_receiver.connect("tcp://localhost:5556")
        while True:
            buff = consumer_receiver.recv()
            self.dataChanged.emit(buff)

class Window(QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        # zmq business
        # zmq_receiver = ZMQReceiver(self)
        # zmq_receiver.dataChanged.connect(self.on_data_changed)
        # zmq_receiver.start()

        # zmq timer implementation
        context = zmq.Context()
        self.socket = context.socket(zmq.PAIR)
        self.socket.connect("tcp://localhost:5556")
        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)
        self.timerPoll = QTimer()
        self.timerPoll.start(100)
        self.timerPoll.timeout.connect(self.pollMsg)

        # widgets I want to have control
        self.voltageSwitch = QPushButton(text='Switch On')
        self.voltageSwitch.setCheckable(True)
        self.msgBox = QTextEdit()
        self.msgBox.setText('hi')
        # push button for sending message
        self.editSendMsg = QLineEdit()
        self.btnSendMsg = QPushButton(text='Send')
        self.btnSendMsg.clicked.connect(self.sendMsg)

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        # Add tabs
        self.tabs.addTab(self.tab1, 'Simple Control')
        self.tabs.addTab(self.tab2, 'Parameter Scan')
        self.tabs.addTab(self.tab3, 'Dark Rate Scan')
        self.tab1.layout = QVBoxLayout(self)
        self.tab1.layout.addWidget(self.createVoltageControl())
        self.tab1.setLayout(self.tab1.layout)
        # self.tab2.layout2 = QVBoxLayout(self)
        # self.tab2.layout2.addWidget(self.createParameterScan())
        # self.tab2.setLayout(self.tab2.layout2)
        self.tab2.setLayout(self.createParameterScan())
        self.tab3.setLayout(self.createDarkRateScan())
        self.tabs.setCurrentIndex(1)

        grid = QGridLayout()
        grid.addWidget(self.tabs, 0, 0, 1, 2)
        grid.addWidget(self.msgBox, 2, 0, 1, 2)
        grid.addWidget(self.createSendMessage(), 3, 0, 1, 2)
        self.setLayout(grid)

        self.setWindowTitle("MPPC DAQ Control App")
        self.resize(600, 500)

        # use a figure as this app's icon
        # ref: https://stackoverflow.com/questions/42602713/how-to-set-a-window-icon-with-pyqt5
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QtGui.QIcon(os.path.join(scriptDir, 'logo.png')))

    def createDarkRateScan(self):
        # widgets belonging to this tab
        self.drsFebCB = QComboBox()
        self.drsFebCB.addItems(['All', '0', '1'])
        self.drsChCB = QComboBox()
        self.drsChCB.addItems(['All']+[str(i) for i in range(32)])
        self.drsStartBtn = QPushButton(text='Start Scan')
        # lay out widgets
        grid = QGridLayout()
        grid.addWidget(QLabel('FEB'), 0, 0, Qt.AlignCenter)
        grid.addWidget(QLabel('Channel'), 0, 1, Qt.AlignCenter)
        grid.addWidget(self.drsFebCB, 1, 0, Qt.AlignCenter)
        grid.addWidget(self.drsChCB, 1, 1, Qt.AlignCenter)
        grid.addWidget(self.drsStartBtn, 2, 1, Qt.AlignCenter)
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
        self.editParVal['feb1dac']['from'] = QLineEdit('230')
        self.editParVal['feb1dac']['to'] = QLineEdit('250')
        self.editParVal['feb1dac']['step'] = QLineEdit('5')
        self.editParVal['feb1gain']['from'] = QLineEdit('50')
        self.editParVal['feb1gain']['to'] = QLineEdit('60')
        self.editParVal['feb1gain']['step'] = QLineEdit('5')
        self.editParVal['feb1bias']['from'] = QLineEdit('190')
        self.editParVal['feb1bias']['to'] = QLineEdit('200')
        self.editParVal['feb1bias']['step'] = QLineEdit('5')
        self.editParVal['feb2dac']['from'] = QLineEdit('230')
        self.editParVal['feb2dac']['to'] = QLineEdit('250')
        self.editParVal['feb2dac']['step'] = QLineEdit('5')
        self.editParVal['feb2gain']['from'] = QLineEdit('50')
        self.editParVal['feb2gain']['to'] = QLineEdit('60')
        self.editParVal['feb2gain']['step'] = QLineEdit('5')
        self.editParVal['feb2bias']['from'] = QLineEdit('190')
        self.editParVal['feb2bias']['to'] = QLineEdit('200')
        self.editParVal['feb2bias']['step'] = QLineEdit('5')
        self.editParVal['temp']['from'] = QLineEdit('18')
        self.editParVal['temp']['to'] = QLineEdit('22')
        self.editParVal['temp']['step'] = QLineEdit('1')
        self.scanBut = QPushButton(text='Start Scan')
        self.scanBut.clicked.connect(self.sendJsonMsg)

        # layout
        # groupBox = QGroupBox()

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

        grid.addWidget(self.scanBut, 9, 6)

        # put on checkboxes
        self.includeParCB = dict()
        for i in range(len(self.parKeys)):
            k = self.parKeys[i]
            self.includeParCB[k] = QCheckBox()
            self.includeParCB[k].setChecked(True)
            grid.addWidget(self.includeParCB[k], i+1, 0, Qt.AlignCenter)

        # groupBox.setLayout(grid)

        # return groupBox
        return grid

    def createSendMessage(self):
        groupBox = QGroupBox('Send Message')

        grid = QGridLayout()
        grid.addWidget(self.editSendMsg, 0, 0)
        grid.addWidget(self.btnSendMsg, 0, 1)

        groupBox.setLayout(grid)

        return groupBox

    def createVoltageControl(self):
        groupBox = QGroupBox("Voltage Control")

        grid = QGridLayout()
        grid.addWidget(QLabel('Voltage Set: '), 0, 0, Qt.AlignRight)
        grid.addWidget(QLineEdit(), 0, 1)
        grid.addWidget(QLabel('Voltage Read: '), 1, 0, Qt.AlignRight)
        grid.addWidget(QLineEdit(), 1, 1)
        grid.addWidget(self.voltageSwitch, 2, 2)

        groupBox.setLayout(grid)

        return groupBox
    
    # @pyqtSlot(bytes)
    # def on_data_changed(self, buff):
    #     text = '\n'.join([self.msgBox.toPlainText(), buff.decode('utf-8')])
    #     self.msgBox.setText(text)

    def pollMsg(self):
        socks = dict(self.poller.poll(0))
        if self.socket in socks and socks[self.socket] == zmq.POLLIN:
            recv_msg = self.socket.recv()
            message = self.msgBox.toPlainText() + '\n{}'.format(recv_msg.decode())
            self.msgBox.setText(message)
    
    def sendJsonMsg(self):
        packedMsg = dict()
        for par in self.parKeys:
            if self.includeParCB[par].isChecked():
                packedMsg[par] = dict()
                for val_st in ['from', 'to', 'step']:
                    packedMsg[par][val_st] = self.editParVal[par][val_st].text()
        print(json.dumps(packedMsg))
        self.socket.send_string(json.dumps(packedMsg))

    def sendMsg(self):
        send_msg = self.editSendMsg.text()
        print(send_msg)
        self.socket.send_string(send_msg)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    clock = Window()
    clock.show()
    sys.exit(app.exec_())
