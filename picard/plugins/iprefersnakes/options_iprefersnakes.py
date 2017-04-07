# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_options_iprefersnakes.ui'
#
# Created by: PyQt5 UI code generator 5.8
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_IPreferSnakesOptionsPage(object):
    def setupUi(self, IPreferSnakesOptionsPage):
        IPreferSnakesOptionsPage.setObjectName("IPreferSnakesOptionsPage")
        IPreferSnakesOptionsPage.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(IPreferSnakesOptionsPage)
        self.verticalLayout.setObjectName("verticalLayout")
        self.code = QtWidgets.QPlainTextEdit(IPreferSnakesOptionsPage)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.code.sizePolicy().hasHeightForWidth())
        self.code.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Monospace")
        font.setPointSize(12)
        self.code.setFont(font)
        self.code.setObjectName("code")
        self.verticalLayout.addWidget(self.code)
        self.code_error = QtWidgets.QLabel(IPreferSnakesOptionsPage)
        self.code_error.setText("")
        self.code_error.setObjectName("code_error")
        self.verticalLayout.addWidget(self.code_error)

        self.retranslateUi(IPreferSnakesOptionsPage)
        QtCore.QMetaObject.connectSlotsByName(IPreferSnakesOptionsPage)

    def retranslateUi(self, IPreferSnakesOptionsPage):
        _translate = QtCore.QCoreApplication.translate
        IPreferSnakesOptionsPage.setWindowTitle(_translate("IPreferSnakesOptionsPage", "Form"))

