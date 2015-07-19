# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_options_iprefersnakes.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_IPreferSnakesOptionsPage(object):
    def setupUi(self, IPreferSnakesOptionsPage):
        IPreferSnakesOptionsPage.setObjectName(_fromUtf8("IPreferSnakesOptionsPage"))
        IPreferSnakesOptionsPage.resize(400, 300)
        self.verticalLayout = QtGui.QVBoxLayout(IPreferSnakesOptionsPage)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.code = QtGui.QTextEdit(IPreferSnakesOptionsPage)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.code.sizePolicy().hasHeightForWidth())
        self.code.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Monospace"))
        font.setPointSize(12)
        self.code.setFont(font)
        self.code.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.code.setObjectName(_fromUtf8("code"))
        self.verticalLayout.addWidget(self.code)
        self.code_error = QtGui.QLabel(IPreferSnakesOptionsPage)
        self.code_error.setText(_fromUtf8(""))
        self.code_error.setObjectName(_fromUtf8("code_error"))
        self.verticalLayout.addWidget(self.code_error)

        self.retranslateUi(IPreferSnakesOptionsPage)
        QtCore.QMetaObject.connectSlotsByName(IPreferSnakesOptionsPage)

    def retranslateUi(self, IPreferSnakesOptionsPage):
        IPreferSnakesOptionsPage.setWindowTitle(_translate("IPreferSnakesOptionsPage", "Form", None))

