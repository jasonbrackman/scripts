import pymel.core as pm
from maya import OpenMaya


class SplineRigger():
    def __init__(self, name='new'):
        self.name = name

    def build(self, startJoint, endJoint, curve=None, numOfCurveSpans=1):
        if curve:
            OpenMaya.MGlobal.displayWarning('Curve is specified, numOfCurveSpans option will be ignored')
            ikHandle, effecotor = pm.ikHandle(startJoint=startJoint, endEffector=endJoint,
                                              createCurve=False, curve=curve,
                                              solver='ikSplineSolver', parentCurve=False,
                                              name=self.name + '_ikh', rootOnCurve=True)
        else:
            ikHandle, effector, curve = pm.ikHandle(startJoint=startJoint, endEffector=endJoint,
                                                    createCurve=True, numSpans=numOfCurveSpans,
                                                    solver='ikSplineSolver', parentCurve=False,
                                                    name=self.name + '_ikh', rootOnCurve=True)

        clusters = self.createClusters(curve)

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
