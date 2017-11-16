"""
Author: Sang-tak Lee
Contact: chst27@gmail.Com
Created: 08/07/2017
Updated:

Description
	Sub-ui of takAutoRig main ui.
"""

from Qt import QtWidgets, QtCore, QtGui
from frameWidget import FrameWidget
import pymel.core as pm


class FaceUI(QtWidgets.QWidget):
    def __init__(self):
        super(FaceUI, self).__init__()

        self.createLayout()
        self.addWidget()

    def createLayout(self):
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(2)
        self.mainLayout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(self.mainLayout)

    def addWidget(self):
        self.mainLayout.addWidget(EyebrowUI("Eyebrow"))
        self.mainLayout.addWidget(EyelidUI("Eyelid"))


class EyebrowUI(FrameWidget):
    def __init__(self, title=""):
        super(EyebrowUI, self).__init__(title)

        self.setCollapsed(True)

        self.createLayout()
        self.createWidget()
        self.addWidget()

    def createLayout(self):
        self.mainLayout = QtWidgets.QGridLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.mainLayout)

    def createWidget(self):
        self.edgesLabel = QtWidgets.QLabel("Edges: ")
        self.edgesText = QtWidgets.QLineEdit()
        self.edgesText.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.fitBtn = QtWidgets.QPushButton("Fit")
        self.buildBtn = QtWidgets.QPushButton("Build")

    def addWidget(self):
        self.mainLayout.addWidget(self.edgesLabel, 0, 0)
        self.mainLayout.addWidget(self.edgesText, 0, 1)
        self.mainLayout.addWidget(self.fitBtn, 1, 0, 1, 2)
        self.mainLayout.addWidget(self.buildBtn, 2, 0, 1, 2)

        loadSelAction = QtWidgets.QAction(self.edgesText)
        loadSelAction.setText("Load Selected")
        loadSelAction.triggered.connect(self.loadSel)
        self.edgesText.addAction(loadSelAction)

    def loadSel(self):
        selEdges = pm.ls(sl=True, fl=True)
        self.edgesText.setText(str(selEdges))


class EyelidUI(FrameWidget):
    def __init__(self, title=""):
        super(EyelidUI, self).__init__(title)

        self.setCollapsed(True)

        self.createLayout()
        self.addWidget()

    def createLayout(self):
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.mainLayout)

    def addWidget(self):
        self.buildBtn = QtWidgets.QPushButton("Build Eyelid Rig")
        self.mainLayout.addWidget(self.buildBtn)
