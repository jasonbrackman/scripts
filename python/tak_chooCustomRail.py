import maya.cmds as cmds
import re

def customRail():
	selList = cmds.ls(sl = True)
	chooRoot = selList[0]
	chooNamespace = chooRoot.rsplit(r':')[0]
	customCurve = selList[1]

	# rebuild curve
	cmds.rebuildCurve(customCurve, rpo = True, rt = 0, end = 1, kr = 0, kcp = 0, kep = 1, kt = 0, s = 0, d = 3, tol = 0.01)

	# delete original ik handle and garbage nodes
	if cmds.objExists('%s:ikHandle' %chooNamespace):
	    cmds.delete('%s:ikHandle' %chooNamespace)
	if cmds.objExists('%s:md' %chooNamespace):
	    cmds.delete('%s:md' %chooNamespace)


	# build spline ik with custom curve
	ikHandleName = cmds.ikHandle(n = '%s:ikHandle' %chooNamespace, startJoint = '%s:joint252' %chooNamespace, endEffector = '%s:joint261' %chooNamespace, solver = 'ikSplineSolver', curve = customCurve, ccv = False, pcv = False)

	# multiply divide node for remap value of Root.run
	mulDivNode = cmds.shadingNode('multiplyDivide', n = '%s:md' %chooNamespace, asUtility = True)
	cmds.setAttr('%s.input2X' %mulDivNode, 0.1)

	# connect Root.run attribute and new ik handle's offset attribute
	cmds.connectAttr('%s:Root.run' %chooNamespace, '%s.input1X' %mulDivNode)
	cmds.connectAttr('%s.outputX' %mulDivNode, '%s.offset' %ikHandleName[0])