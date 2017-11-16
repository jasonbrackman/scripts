import pymel.core as pm
from maya import OpenMaya


class SplineRigger():
    def __init__(self, startJoint, endJoint, curve=None, name='new'):
        self.name = name
        self.startJoint = startJoint
        self.endJoint = endJoint
        self.curve = curve
        self.createCurve = False if self.curve else True

    def build(self, numOfCurveSpans=1):
        if self.curve:
            OpenMaya.MGlobal.displayWarning('Curve is specified, numOfCurveSpans option will be ignored')
            ikHandle, effecotor = pm.ikHandle(startJoint=self.startJoint, endEffector=self.endJoint,
                                              createCurve=self.createCurve, curve=self.curve, solver='ikSplineSolver',
                                              parentCurve=False, name=self.name + '_ikh', rootOnCurve=True)
        else:
            ikHandle, effector, self.curve = pm.ikHandle(startJoint=self.startJoint, endEffector=self.endJoint,
                                                         createCurve=self.createCurve, numSpans=numOfCurveSpans,
                                                         solver='ikSplineSolver', parentCurve=False,
                                                         name=self.name + '_ikh', rootOnCurve=True)

        clusters = self.createClusters(self.curve)

        self.createControls(clusters)

        self.setStretch()

        self.setSquash()

    def createClusters(self, curve):
        clusters = []

        curveCVs = pm.ls('%s.cv[*]' % curve, fl=True)

        startCluster = pm.cluster(curveCVs[:2], n='%s_%d_clst' % (self.name, 1))[1]
        clusters.append(startCluster)

        for i in range(curve.numCVs())[2:-2:]:
            clusters.append(pm.cluster(curveCVs[i], n='%s_%d_clst' % (self.name, i))[1])

        endCluster = pm.cluster(curveCVs[-2:], n='%s_%d_clst' % (self.name, len(curveCVs) - 2))[1]
        clusters.append(endCluster)

        return clusters

    def createControls(self, clusters):
        pass

    def setStretch(self):
        pass

    def setSquash(self):
        pass
