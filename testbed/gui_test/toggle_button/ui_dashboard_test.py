# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dashboard_test.ui',
# licensing of 'dashboard_test.ui' applies.
#
# Created: Thu Jun 25 14:38:19 2020
#      by: pyside2-uic  running on PySide2 5.13.2
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(460, 146)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBoxFunGen = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBoxFunGen.setGeometry(QtCore.QRect(230, 0, 211, 101))
        self.groupBoxFunGen.setObjectName("groupBoxFunGen")
        self.funGenSwitch = QtWidgets.QPushButton(self.groupBoxFunGen)
        self.funGenSwitch.setGeometry(QtCore.QRect(130, 70, 75, 23))
        self.funGenSwitch.setObjectName("funGenSwitch")
        self.groupBoxPower = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBoxPower.setGeometry(QtCore.QRect(10, 0, 211, 101))
        self.groupBoxPower.setObjectName("groupBoxPower")
        self.powerSwitch = QtWidgets.QPushButton(self.groupBoxPower)
        self.powerSwitch.setGeometry(QtCore.QRect(130, 70, 75, 23))
        self.powerSwitch.setObjectName("powerSwitch")
        self.labelVoltagePower = QtWidgets.QLabel(self.groupBoxPower)
        self.labelVoltagePower.setGeometry(QtCore.QRect(20, 30, 51, 21))
        self.labelVoltagePower.setObjectName("labelVoltagePower")
        self.lineEditVoltagePower = QtWidgets.QLineEdit(self.groupBoxPower)
        self.lineEditVoltagePower.setGeometry(QtCore.QRect(70, 30, 113, 20))
        self.lineEditVoltagePower.setObjectName("lineEditVoltagePower")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 460, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "MainWindow", None, -1))
        self.groupBoxFunGen.setTitle(QtWidgets.QApplication.translate("MainWindow", "Function Generator", None, -1))
        self.funGenSwitch.setText(QtWidgets.QApplication.translate("MainWindow", "On", None, -1))
        self.groupBoxPower.setTitle(QtWidgets.QApplication.translate("MainWindow", "Power", None, -1))
        self.powerSwitch.setText(QtWidgets.QApplication.translate("MainWindow", "On", None, -1))
        self.labelVoltagePower.setText(QtWidgets.QApplication.translate("MainWindow", "Voltage:", None, -1))

