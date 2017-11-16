"""
Author: Sang-tak Lee
Contact: chst27@gmail.Com
Created: 08/07/2017
Updated:

Description

"""

from Qt import QtWidgets, QtCore, QtGui
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from . import faceUi, bodyUi

reload(faceUi)
reload(bodyUi)


class MainUI(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    def __init__(self):
        super(MainUI, self).__init__()
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setWindowTitle("Tak Auto Rig")
        self.setGeometry(980, 520, 300, 300)

        self.createLayout()
        self.addWidget()

    def createLayout(self):
        self.mainLayout = QtWidgets.QVBoxLayout()

        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.mainLayout)

    def addWidget(self):
        mainTabWidget = QtWidgets.QTabWidget()

        mainTabWidget.addTab(bodyUi.BodyUI(), "Body")
        mainTabWidget.addTab(faceUi.FaceUI(), "Face")

        self.mainLayout.addWidget(mainTabWidget)
