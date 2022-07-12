# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '界面.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


import CTA
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(520, 120)
        MainWindow.setMinimumSize(QtCore.QSize(520, 120))
        MainWindow.setMaximumSize(QtCore.QSize(520, 120))
        MainWindow.setBaseSize(QtCore.QSize(520, 120))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(80, 20, 360, 20))
        self.lineEdit.setInputMask("")
        self.lineEdit.setObjectName("lineEdit")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(200, 60, 120, 40))
        self.pushButton.setObjectName("pushButton")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        #绑定按钮事件
        self.pushButton.clicked.connect(self.do_CTA)
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "平差课设"))
        self.lineEdit.setPlaceholderText(_translate("MainWindow", "请输入闭合导线"))
        self.pushButton.setText(_translate("MainWindow", "平差"))

    def do_CTA(self):

        cta = CTA.CTA('./JFadjust_all.in2')
        cta.calculate(self.lineEdit.text())

        print(cta.deg_azi)