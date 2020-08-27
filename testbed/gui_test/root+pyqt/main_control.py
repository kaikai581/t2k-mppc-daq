#!/usr/bin/env python

import sys
sys.path.append('../../agilent-n6700b-power-system')
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
        # Add tabs
        self.tabs.addTab(self.tab1, 'Simple Control')
        self.tabs.addTab(self.tab2, 'Parameter Scan')
        self.tab1.layout = QVBoxLayout(self)
        self.tab1.layout.addWidget(self.createVoltageControl())
        self.tab1.setLayout(self.tab1.layout)

        grid = QGridLayout()
        grid.addWidget(self.tabs, 0, 0, 1, 2)
        grid.addWidget(self.msgBox, 2, 0, 1, 2)
        grid.addWidget(self.createSendMessage(), 3, 0, 1, 2)
        self.setLayout(grid)

        self.setWindowTitle("MPPC DAQ Control App")
        self.resize(400, 300)

        # use a figure as this app's icon
        # ref: https://stackoverflow.com/questions/42602713/how-to-set-a-window-icon-with-pyqt5
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QtGui.QIcon(os.path.join(scriptDir, 'logo.png')))


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
    
    def sendMsg(self):
        send_msg = self.editSendMsg.text()
        print(send_msg)
        self.socket.send_string(send_msg)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    clock = Window()
    clock.show()
    sys.exit(app.exec_())
