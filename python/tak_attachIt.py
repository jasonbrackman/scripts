"""
Author: Sang-tak Lee
Contact: chst27@gmail.com
Created: 06/16/2015
Updated: 10/12/2017

Description:
You can attach object to nurbs curve, nurbs surface, poly mesh.
Select object to attach and select target object and run.
In case poly mesh, you can also attach by selecting two edges.

Usage:
import tak_attachIt
reload(tak_attachIt)
tak_attachIt.UI()

Requirement:
tak_misc.py
"""

import re

import maya.cmds as cmds
import pymel.core as pm

import tak_cleanUpModel
import tak_misc

# Load matrixNodes plug in for using decompose matrix node
if not cmds.pluginInfo('matrixNodes.mll', q=True, loaded=True):
	cmds.loadPlugin('matrixNodes.mll')


class UI(object):
	win = 'attachItWin'
	widgets = {}

	@classmethod
	def __init__(cls):
		if cmds.window(cls.win, exists=True):
			cmds.deleteUI(cls.win)
		cls.ui()

	@classmethod
	def ui(cls):
		cmds.window(cls.win, title='Attach It', mnb=False, mxb=False)

		cls.widgets['mainColLay'] = cmds.columnLayout(adj=True)

		cls.widgets['chkRowLay'] = cmds.rowLayout(numberOfColumns=4, p=cls.widgets['mainColLay'])
		cls.widgets['mPosOffChkBox'] = cmds.checkBox(label='Maintain Pos Offset', v=True, p=cls.widgets['chkRowLay'])
		cls.widgets['moOriOffChkBox'] = cmds.checkBox(label='Maintain Ori Offset', v=True, p=cls.widgets['chkRowLay'])
		cls.widgets['oriChkBox'] = cmds.checkBox(label='Orientation', p=cls.widgets['chkRowLay'])
		cls.widgets['revGrpChkBox'] = cmds.checkBox(label='Reverse Group', p=cls.widgets['chkRowLay'], visible=False)

		cmds.separator(h=5, style='none', p=cls.widgets['mainColLay'])

		cls.widgets['appBtn'] = cmds.button(label='Attach It!', h=50, c=Functions.main, p=cls.widgets['mainColLay'])

		cmds.window(cls.win, e=True, w=200, h=50)
		cmds.showWindow(cls.win)


class Functions(object):
	trgObj = None

	@classmethod
	def main(cls, *args):
		# get state of options
		oriOpt = cmds.checkBox(UI.widgets['oriChkBox'], q=True, v=True)
		revGrpOpt = cmds.checkBox(UI.widgets['revGrpChkBox'], q=True, v=True)
		mPosOffOpt = cmds.checkBox(UI.widgets['mPosOffChkBox'], q=True, v=True)
		mOriOffOpt = cmds.checkBox(UI.widgets['moOriOffChkBox'], q=True, v=True)

		selList = cmds.ls(sl=True)
		srcObjs = selList[0:-1]
		cls.trgObj = selList[-1]

		if '.e' in cls.trgObj:
			cls.attachToMeshEdge(oriOpt, revGrpOpt, mPosOffOpt, mOriOffOpt)
		else:
			trgShp = cmds.listRelatives(cls.trgObj, s=True)[0]
			trgType = cmds.objectType(trgShp)

			if trgType == 'nurbsCurve':
				for srcObj in srcObjs:
					cls.attachToCrv(srcObj, trgShp, oriOpt, revGrpOpt, mPosOffOpt, mOriOffOpt)
			elif trgType == 'nurbsSurface':
				for srcObj in srcObjs:
					cls.attachToSurface(srcObj, trgShp, oriOpt, revGrpOpt, mPosOffOpt, mOriOffOpt)
			elif trgType == 'mesh':
				folLs = []
				for srcObj in srcObjs:
					result = cls.attachToMeshFol(srcObj, trgShp, oriOpt, revGrpOpt, mPosOffOpt, mOriOffOpt)
					folLs.append(result)
				cmds.group(folLs, n='_fol_grp')

	@classmethod
	def attachToCrv(cls, srcObj, trgCrvShp, oriOpt, revGrpOpt, mPosOffOpt, mOriOffOpt):
		nPntCrvNode = cmds.createNode('nearestPointOnCurve', n=srcObj + '_nPntCrv')
		cmds.connectAttr('%s.worldSpace[0]' % (trgCrvShp), '%s.inputCurve' % (nPntCrvNode), force=True)
		cmds.connectAttr('%s.translate' % (srcObj), '%s.inPosition' % (nPntCrvNode), force=True)

		pOnCrvInfoNode = cmds.createNode('pointOnCurveInfo', n=srcObj + '_pOnCrvInfo')
		cmds.connectAttr('%s.worldSpace[0]' % (trgCrvShp), '%s.inputCurve' % (pOnCrvInfoNode), force=True)
		cmds.connectAttr('%s.parameter' % (nPntCrvNode), '%s.parameter' % (pOnCrvInfoNode), force=True)
		parmVal = cmds.getAttr('%s.parameter' % (pOnCrvInfoNode))

		anchorGrp = cmds.createNode('transform', n=srcObj + '_anchor')

		cmds.connectAttr('%s.position' % (pOnCrvInfoNode), '%s.translate' % (anchorGrp), force=True)
		cmds.delete(nPntCrvNode)
		cmds.setAttr('%s.parameter' % (pOnCrvInfoNode), parmVal)

		# Connect anchorGrp rotate depend on oriOpt.
		if oriOpt:
			cls.connectOri(srcObj, pOnCrvInfoNode, anchorGrp)

		# Get srcObj parent before parent to anchorGrp.
		srcPrnt = cmds.listRelatives(srcObj, p=True)

		# Parent srcObj to anchorGrp.
		cmds.parent(srcObj, anchorGrp)

		# If srcPrnt exists, reparent anchorGrp to srcObj's old parent.
		if srcPrnt:
			cmds.parent(anchorGrp, srcPrnt[0])

		if not mPosOffOpt:
			cls.setZeroAttr(srcObj, 'pos')

		if not mOriOffOpt:
			cls.setZeroAttr(srcObj, 'ori')
			if cmds.objectType(srcObj) == "joint":
				cls.setZeroJntOri(srcObj)

		if revGrpOpt:
			cls.reverseGrp(srcObj)

	@classmethod
	def attachToSurface(cls, srcObj, trgSurfShp, oriOpt, revGrpOpt, mPosOffOpt, mOriOffOpt):
		# Connect anchorGrp translate.
		clPtOnSurfNode = cmds.createNode('closestPointOnSurface', n=srcObj + '_clPtOnSurf')
		cmds.connectAttr('%s.worldSpace[0]' % (trgSurfShp), '%s.inputSurface' % (clPtOnSurfNode), force=True)
		cmds.connectAttr('%s.translate' % (srcObj), '%s.inPosition' % (clPtOnSurfNode), force=True)

		pOnSurfInfoNode = cmds.createNode('pointOnSurfaceInfo', n=srcObj + '_pOnSurfInfo')
		cmds.connectAttr('%s.worldSpace[0]' % (trgSurfShp), '%s.inputSurface' % (pOnSurfInfoNode), force=True)
		cmds.connectAttr('%s.parameterU' % (clPtOnSurfNode), '%s.parameterU' % (pOnSurfInfoNode), force=True)
		cmds.connectAttr('%s.parameterV' % (clPtOnSurfNode), '%s.parameterV' % (pOnSurfInfoNode), force=True)
		parmUVal = cmds.getAttr('%s.parameterU' % (pOnSurfInfoNode))
		parmVVal = cmds.getAttr('%s.parameterV' % (pOnSurfInfoNode))

		anchorGrp = cmds.createNode('transform', n=srcObj + '_anchor')

		cmds.connectAttr('%s.position' % (pOnSurfInfoNode), '%s.translate' % (anchorGrp), force=True)
		cmds.delete(clPtOnSurfNode)
		cmds.setAttr('%s.parameterU' % (pOnSurfInfoNode), parmUVal)
		cmds.setAttr('%s.parameterV' % (pOnSurfInfoNode), parmVVal)

		# Connect anchorGrp rotate depend on oriOpt.
		if oriOpt:
			cls.connectOri(srcObj, pOnSurfInfoNode, anchorGrp)

		# Get srcObj parent before parent to anchorGrp.
		srcPrnt = cmds.listRelatives(srcObj, p=True)

		# Parent srcObj to anchorGrp.
		cmds.parent(srcObj, anchorGrp)

		# If srcPrnt exists, reparent anchorGrp to srcObj's old parent.
		if srcPrnt:
			cmds.parent(anchorGrp, srcPrnt[0])

		if not mPosOffOpt:
			cls.setZeroAttr(srcObj, 'pos')

		if not mOriOffOpt:
			cls.setZeroAttr(srcObj, 'ori')
			if cmds.objectType(srcObj) == "joint":
				cls.setZeroJntOri(srcObj)

		if revGrpOpt:
			cls.reverseGrp(srcObj)

	@classmethod
	def attachToMeshFol(cls, srcObj, trgMeshShp, oriOpt, revGrpOpt, mPosOffOpt, mOriOffOpt):
		# Mesh uv is must exists.
		# Follicle ignore target mesh's transform value. So, Duplicate target mesh and freeze transform temporarily to get accurate u and v parameter.
		cmds.select(cls.trgObj, r=True)
		tak_cleanUpModel.cleanChBox()

		tmpMesh = cmds.duplicate(trgMeshShp)
		try:
			cmds.parent(tmpMesh, world=True)
		except:
			pass
		cmds.makeIdentity(tmpMesh, apply=True)
		tmpMeshShp = cmds.listRelatives(tmpMesh, s=True)[0]

		tmpSrcObj = cmds.duplicate(srcObj)[0]
		if not cmds.listRelatives(tmpSrcObj, p=True) is None:
			cmds.parent(tmpSrcObj, world=True)

		clPtOnMeshNode = cmds.createNode('closestPointOnMesh', n=srcObj + '_clPtOnMesh')
		cmds.connectAttr('%s.outMesh' % (tmpMeshShp), '%s.inMesh' % (clPtOnMeshNode), force=True)
		cmds.connectAttr('%s.translate' % (tmpSrcObj), '%s.inPosition' % (clPtOnMeshNode), force=True)

		parmUVal = cmds.getAttr('%s.parameterU' % (clPtOnMeshNode))
		parmVVal = cmds.getAttr('%s.parameterV' % (clPtOnMeshNode))
		cmds.delete(clPtOnMeshNode, tmpMesh, tmpSrcObj)

		# Create follicle and connect nodes.
		fol = cmds.createNode('follicle')
		folPrnt = cmds.listRelatives(fol, parent=True)[0]
		folPrnt = cmds.rename(folPrnt, srcObj + '_fol')
		fol = cmds.listRelatives(folPrnt, s=True)[0]

		cmds.connectAttr('{0}.worldMesh'.format(trgMeshShp), '{0}.inputMesh'.format(fol))
		cmds.connectAttr('{0}.worldMatrix'.format(trgMeshShp), '{0}.inputWorldMatrix'.format(fol))
		cmds.connectAttr('{0}.outTranslate'.format(fol), '{0}.translate'.format(folPrnt))
		cmds.setAttr('{0}.parameterU'.format(fol), parmUVal)
		cmds.setAttr('{0}.parameterV'.format(fol), parmVVal)
		cmds.setAttr('%s.visibility' % (fol), False)

		anchorGrp = cmds.createNode('transform', n=srcObj + '_anchor')

		cmds.connectAttr('{0}.translate'.format(folPrnt), '{0}.translate'.format(anchorGrp))

		if oriOpt:
			cmds.connectAttr('{0}.outRotate'.format(fol), '{0}.rotate'.format(folPrnt))
			cmds.connectAttr('{0}.rotate'.format(folPrnt), '{0}.rotate'.format(anchorGrp))

		# Get srcObj parent before parent to anchorGrp.
		srcPrnt = cmds.listRelatives(srcObj, p=True)

		# Parent srcObj to anchorGrp.
		cmds.parent(srcObj, anchorGrp)

		# If srcPrnt exists, reparent anchorGrp to srcObj's old parent.
		if srcPrnt:
			cmds.parent(anchorGrp, srcPrnt[0])

		if not mPosOffOpt:
			cls.setZeroAttr(srcObj, 'pos')

		if not mOriOffOpt:
			cls.setZeroAttr(srcObj, 'ori')
			if cmds.objectType(srcObj) == "joint":
				cls.setZeroJntOri(srcObj)

		if revGrpOpt:
			cls.reverseGrp(srcObj)

		return folPrnt

	@classmethod
	def attachToMeshEdge(cls, oriOpt, revGrpOpt, mPosOffOpt, mOriOffOpt):
		selList = cmds.ls(sl=True, fl=True)
		edgeDic = {}
		srcObj = selList[0]

		matchObj = re.match(r'(.+)\.(\w+)\[(\d+)\]', selList[1])
		edgeOneNiceName = matchObj.group(1) + '_' + matchObj.group(2) + matchObj.group(3)
		edgeDic[1] = [edgeOneNiceName, matchObj.group(3)]

		matchObj = re.match(r'(.+)\.(\w+)\[(\d+)\]', selList[2])
		edgeTwoNiceName = matchObj.group(1) + '_' + matchObj.group(2) + matchObj.group(3)
		edgeDic[2] = [edgeTwoNiceName, matchObj.group(3)]

		trgMesh = matchObj.group(1)
		trgMeshShp = cmds.listRelatives(trgMesh, s=True)[0]

		cmds.select(cl=True)

		for edge in edgeDic.keys():
			crvFromEdgeNode = cmds.createNode('curveFromMeshEdge', n=edgeDic[edge][0] + '_crvFromEdge')
			cmds.connectAttr('%s.worldMesh[0]' % (trgMeshShp), '%s.inputMesh' % (crvFromEdgeNode), force=True)
			cmds.setAttr('%s.edgeIndex[0]' % (crvFromEdgeNode), int(edgeDic[edge][1]))

		loftNode = cmds.createNode('loft', n=edgeOneNiceName + '_' + edgeTwoNiceName + '_loft')
		cmds.setAttr('%s.uniform' % loftNode, 1)
		cmds.setAttr('%s.reverseSurfaceNormals' % loftNode, 1)
		cmds.connectAttr('%s.outputCurve' % (edgeOneNiceName + '_crvFromEdge'), '%s.inputCurve[0]' % (loftNode),
		                 force=True)
		cmds.connectAttr('%s.outputCurve' % (edgeTwoNiceName + '_crvFromEdge'), '%s.inputCurve[1]' % (loftNode),
		                 force=True)

		# Get closest point's u,v parameter of lofted surface
		surfaceNode = cmds.createNode('nurbsSurface', n='%s_%s_surface' % (edgeOneNiceName, edgeTwoNiceName))
		surfaceNodeTransform = cmds.listRelatives(surfaceNode, p=True)
		cmds.connectAttr('%s.outputSurface' % loftNode, '%s.create' % surfaceNode)
		closestPointOnSurfaceNode = cmds.createNode('closestPointOnSurface', n='%s_%s_csinfo' % (edgeOneNiceName, edgeTwoNiceName))
		cmds.connectAttr('%s.worldSpace' % surfaceNode, '%s.inputSurface' % closestPointOnSurfaceNode)
		decomposeMatrixNode = cmds.createNode('decomposeMatrix', n='%s_%s_deMatrix' % (edgeOneNiceName, edgeTwoNiceName))
		cmds.connectAttr('%s.worldMatrix' % srcObj, '%s.inputMatrix' % decomposeMatrixNode)
		cmds.connectAttr('%s.outputTranslate' % decomposeMatrixNode, '%s.inPosition' % closestPointOnSurfaceNode)
		parmUVal = cmds.getAttr('%s.parameterU' % closestPointOnSurfaceNode)
		parmVVal = cmds.getAttr('%s.parameterV' % closestPointOnSurfaceNode)

		pOnSurfInfoNode = cmds.createNode('pointOnSurfaceInfo', n=srcObj + '_pOnSurfInfo')
		cmds.connectAttr('%s.outputSurface' % loftNode, '%s.inputSurface' % pOnSurfInfoNode, force=True)
		cmds.setAttr('%s.parameterU' % pOnSurfInfoNode, parmUVal)
		cmds.setAttr('%s.parameterV' % pOnSurfInfoNode, parmVVal)

		anchorGrp = cmds.createNode('transform', n=srcObj + '_anchor')

		cmds.connectAttr('{0}.position'.format(pOnSurfInfoNode), '{0}.translate'.format(anchorGrp))

		# Delete unnecessary nodes
		cmds.delete(surfaceNode, surfaceNodeTransform, closestPointOnSurfaceNode, decomposeMatrixNode)

		# Connect anchorGrp rotate depend on oriOpt.
		if oriOpt:
			cls.connectOri(srcObj, pOnSurfInfoNode, anchorGrp)

		# Get srcObj parent before parent to anchorGrp.
		srcPrnt = cmds.listRelatives(srcObj, p=True)

		# Parent srcObj to anchorGrp.
		cmds.parent(srcObj, anchorGrp)

		# If srcPrnt exists, reparent anchorGrp to srcObj's old parent.
		if srcPrnt:
			cmds.parent(anchorGrp, srcPrnt[0])

		if not mPosOffOpt:
			cls.setZeroAttr(srcObj, 'pos')

		if not mOriOffOpt:
			cls.setZeroAttr(srcObj, 'ori')
			if cmds.objectType(srcObj) == "joint":
				cls.setZeroJntOri(srcObj)

		if revGrpOpt:
			cls.reverseGrp(srcObj)

	@classmethod
	def setZeroAttr(cls, grp, zroType):
		posAttrList = ['translateX', 'translateY', 'translateZ']
		oriAttrList = ['rotateX', 'rotateY', 'rotateZ']

		if zroType == 'pos':
			for attr in posAttrList:
				cmds.setAttr('%s.%s' % (grp, attr), 0)
		elif zroType == 'ori':
			for attr in oriAttrList:
				cmds.setAttr('%s.%s' % (grp, attr), 0)

	@classmethod
	def setZeroJntOri(cls, srcObj):
		jntOriAttrs = ["jointOrientX", "jointOrientY", "jointOrientZ"]

		for jntOriAttr in jntOriAttrs:
			cmds.setAttr("%s.%s" % (srcObj, jntOriAttr), 0)

	@classmethod
	def reverseGrp(cls, srcObj):
		revGrp = tak_misc.doGroup(srcObj, '_rev')
		mulNode = cmds.createNode('multiplyDivide', n=srcObj + '_mul')
		inputList = ['input2X', 'input2Y', 'input2Z']
		for input in inputList:
			cmds.setAttr('{0}.{1}'.format(mulNode, input), -1)
		cmds.connectAttr('{0}.translate'.format(srcObj), '{0}.input1'.format(mulNode), f=True)
		cmds.connectAttr('{0}.output'.format(mulNode), '{0}.translate'.format(revGrp), f=True)

	@classmethod
	def connectOri(cls, srcObj, pntInfoNode, anchorGrp):
		"""
		Connect orientation to anchor group
		Args:
			srcObj: Object name for naming convention
			pntInfoNode: pointOnSurfaceInfo or pointOnCurveInfo node
			anchorGrp: Group that parent of srcObj

		Returns:
			None
		"""
		# Get Z Vector from normalizedNormal and normalizedTangent
		zVecNode = cmds.shadingNode('vectorProduct', asUtility=True, n=srcObj + '_Zvec')
		cmds.setAttr('%s.operation' % zVecNode, 2)

		cmds.connectAttr('%s.result.normalizedNormal' % pntInfoNode, '%s.input1' % zVecNode, force=True)
		if cmds.nodeType(pntInfoNode) == 'pointOnSurfaceInfo':  # In case nurbs surface
			cmds.connectAttr('%s.result.normalizedTangentU' % pntInfoNode, '%s.input2' % zVecNode, force=True)
		else:  # In case curve
			cmds.connectAttr('%s.result.normalizedTangent' % pntInfoNode, '%s.input2' % zVecNode, force=True)

		# Compose matrix node
		matrix = cmds.shadingNode('fourByFourMatrix', asUtility=True, n=srcObj + '_matrix')
		if cmds.nodeType(pntInfoNode) == 'pointOnSurfaceInfo':
			# X Vector is normalizedTangentU
			cmds.connectAttr('%s.normalizedTangentUX' % pntInfoNode, '%s.in00' % matrix, force=True)
			cmds.connectAttr('%s.normalizedTangentUY' % pntInfoNode, '%s.in01' % matrix, force=True)
			cmds.connectAttr('%s.normalizedTangentUZ' % pntInfoNode, '%s.in02' % matrix, force=True)

			# Y Vector is normalizedNormal
			cmds.connectAttr('%s.normalizedNormalX' % pntInfoNode, '%s.in10' % matrix, force=True)
			cmds.connectAttr('%s.normalizedNormalY' % pntInfoNode, '%s.in11' % matrix, force=True)
			cmds.connectAttr('%s.normalizedNormalZ' % pntInfoNode, '%s.in12' % matrix, force=True)

		else:  # In case curve
			# X Vector is curve's normalizedTangent
			cmds.connectAttr('%s.normalizedTangentX' % pntInfoNode, '%s.in00' % matrix, force=True)
			cmds.connectAttr('%s.normalizedTangentY' % pntInfoNode, '%s.in01' % matrix, force=True)
			cmds.connectAttr('%s.normalizedTangentZ' % pntInfoNode, '%s.in02' % matrix, force=True)

			# Y Vector is normalizedNormal
			cmds.setAttr('%s.in10' % matrix, cmds.getAttr('%s.normalizedNormalX' % pntInfoNode))
			cmds.setAttr('%s.in11' % matrix, cmds.getAttr('%s.normalizedNormalY' % pntInfoNode))
			cmds.setAttr('%s.in12' % matrix, cmds.getAttr('%s.normalizedNormalZ' % pntInfoNode))

		# Z Vector is the result of cross product with normal and tangent
		cmds.connectAttr('%s.outputX' % zVecNode, '%s.in20' % matrix, force=True)
		cmds.connectAttr('%s.outputY' % zVecNode, '%s.in21' % matrix, force=True)
		cmds.connectAttr('%s.outputZ' % zVecNode, '%s.in22' % matrix, force=True)

		cmds.connectAttr('%s.positionX' % pntInfoNode, '%s.in30' % matrix, force=True)
		cmds.connectAttr('%s.positionY' % pntInfoNode, '%s.in31' % matrix, force=True)
		cmds.connectAttr('%s.positionZ' % pntInfoNode, '%s.in32' % matrix, force=True)

		# Decompose matrix
		deMatrix = cmds.shadingNode('decomposeMatrix', asUtility=True, n=srcObj + 'deMatrix')
		cmds.connectAttr('%s.output' % matrix, '%s.inputMatrix' % deMatrix)

		# Connect to anchor group
		cmds.connectAttr('%s.outputTranslate' % deMatrix, '%s.translate' % anchorGrp, force=True)
		cmds.connectAttr('%s.outputRotate' % deMatrix, '%s.rotate' % anchorGrp, force=True)
