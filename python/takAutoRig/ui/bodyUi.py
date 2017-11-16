"""
Author: Sang-tak Lee
Contact: chst27@gmail.Com
Created: 08/07/2017
Updated:

Description
	Sub-ui of takAutoRig main ui.
"""

from Qt import QtWidgets, QtCore, QtGui


class BodyUI(QtWidgets.QWidget):
    def __init__(self):
        super(BodyUI, self).__init__()

        self.createLayout()
        self.addWidget()

    def createLayout(self):
        self.mainLayout = QtWidgets.QVBoxLayout()

        self.setLayout(self.mainLayout)

    def addWidget(self):
        btn = QtWidgets.QPushButton("Body Button")
        self.mainLayout.addWidget(btn)
