'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date:

Description:

How To Use:

'''

import maya.cmds as cmds
import tak_curveToPoly

def main():
	selCrv = cmds.ls(sl = True)[0]
	
	# rebuild selCrv
	cmds.rebuildCurve(selCrv, ch = 1, rpo = 1, rt = 0, end = 1, kr = 0, kcp = 0, kep = 1, kt = 0, s = 0, d = 3, tol = 0)
	numCvs = getNumCvs(selCrv)
	cmds.delete('%s.cv[%d]' %(selCrv, numCvs - 2))
	cmds.delete('%s.cv[%d]' %(selCrv, 1))

	# duplicated curve is for back to original position using blend shape
	dupCrv = cmds.duplicate(selCrv, n = selCrv + '_dup')[0]
	
	# align duplicated curve to world space origin as straighten
	arcLength = straightCrvToOrigin(dupCrv)

	# build braid curve
	braidCrv = cmds.duplicate(dupCrv, n = selCrv + '_braid')[0]
	cmds.rebuildCurve(braidCrv, ch = 1, rpo = 1, rt = 0, end = 1, kr = 0, kcp = 0, kep = 1, kt = 0, s = int(arcLength), d = 3, tol = 0)
	braidCrvNumCvs = getNumCvs(braidCrv)
	# move x axis
	baseIndexOne = 2
	baseIndexTwo = 3
	switch = 1
	for j in xrange(braidCrvNumCvs):
		baseIndexOnePos = cmds.xform('%s.cv[%d]' %(braidCrv, baseIndexOne), q = True, ws = True, t = True)
		baseIndexTwoPos = cmds.xform('%s.cv[%d]' %(braidCrv, baseIndexTwo), q = True, ws = True, t = True)

		if switch:
			cmds.xform('%s.cv[%d]' %(braidCrv, baseIndexOne), ws = True, t = (-1, baseIndexOnePos[1], 0))
			cmds.xform('%s.cv[%d]' %(braidCrv, baseIndexTwo), ws = True, t = (-1, baseIndexTwoPos[1], 0))
			switch = 0
		else:
			cmds.xform('%s.cv[%d]' %(braidCrv, baseIndexOne), ws = True, t = (1, baseIndexOnePos[1], 0))
			cmds.xform('%s.cv[%d]' %(braidCrv, baseIndexTwo), ws = True, t = (1, baseIndexTwoPos[1], 0))
			switch = 1
		baseIndexOne += 3
		baseIndexTwo += 3
	# move z axis
	baseIndexOne = 2
	baseIndexTwo = 3
	switch = 1
	for j in xrange(braidCrvNumCvs):
		baseIndexOnePos = cmds.xform('%s.cv[%d]' %(braidCrv, baseIndexOne), q = True, ws = True, t = True)
		baseIndexTwoPos = cmds.xform('%s.cv[%d]' %(braidCrv, baseIndexTwo), q = True, ws = True, t = True)

		if switch:
			cmds.xform('%s.cv[%d]' %(braidCrv, baseIndexOne), ws = True, t = (baseIndexOnePos[0], baseIndexOnePos[1], -1))
			cmds.xform('%s.cv[%d]' %(braidCrv, baseIndexTwo), ws = True, t = (baseIndexTwoPos[0], baseIndexTwoPos[1], 1))
			switch = 0
		else:
			cmds.xform('%s.cv[%d]' %(braidCrv, baseIndexOne), ws = True, t = (baseIndexOnePos[0], baseIndexOnePos[1], -1))
			cmds.xform('%s.cv[%d]' %(braidCrv, baseIndexTwo), ws = True, t = (baseIndexTwoPos[0], baseIndexTwoPos[1], 1))
			switch = 1
		baseIndexOne += 3
		baseIndexTwo += 3

	braidCrv1 = cmds.duplicate(braidCrv, n = selCrv + '_braid1')[0]
	braidCrv2 = cmds.duplicate(braidCrv, n = selCrv + '_braid2')[0]

	cmds.xform(braidCrv1, ws = True, t = (0, 2, 0))
	cmds.xform(braidCrv2, ws = True, t = (0, 4, 0))

	cmds.select(braidCrv, braidCrv1, braidCrv2, r = True)
	tak_curveToPoly.Functions.convert()

	



	cmds.setAttr('%s.visibility' %(dupCrv), False)


def straightCrvToOrigin(crv):
	arcLength = cmds.arclen(crv)
	numCvs = getNumCvs(crv)
	interval = arcLength / (numCvs - 1)
	startYPos = 0
	for i in xrange(numCvs):
		cmds.xform('%s.cv[%d]' %(crv, i), ws = True, t = (0, startYPos, 0))
		startYPos += interval
	return arcLength


def getNumCvs(crv):
	degs = cmds.getAttr('%s.degree' %(crv))
	spans = cmds.getAttr('%s.spans' %(crv))
	numCvs = degs+spans
	return numCvs
