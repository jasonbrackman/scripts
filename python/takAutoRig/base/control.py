import pymel.core as pm
from maya import cmds


class Control():
    def __init__(self, name='new', shape='circle', color='yellow'):
        self.name = name
        self.shape = shape
        self.color = color

    def create(self):
        pm.curve(n='%s_ctrl' % self.name)

    def setShape(self):
        pass

    def setColor(self):
        pass

    def createGroups(self, zero=True, auto=False, extra=False):
        pass

    def driveWithConstraint(self, parentConstraint=True, pointConstraint=False, orientConstraint=False,
                            scaleConstraint=False):
        pass

    def driveWithConnection(self, translate=True, rotate=True, scale=False):
        pass

    def matchHierarchy(self):
        pass

    def matchRotationOrder(self):
        pass

    def matchZeroGroup(self):
        pass

    def matchLimit(self):
        pass
