# encoding: utf-8

"""
Author: Sang-tak Lee
Contact: chst27@gmail.com

Description:
This module is the library that relatively simple functions.
"""

import os
import random
import re
import shutil
import subprocess
from functools import partial

import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

import tak_cleanUpModel
import tak_createCtrl
import tak_lib


def mirJntUi():
	if cmds.window('mjWin', exists=True):
		cmds.deleteUI('mjWin')
	cmds.window('mjWin', title='Mirror Joint', maximizeButton=False, minimizeButton=False)

	cmds.columnLayout('mainColLay', adj=True)

	cmds.checkBox('mirFuncChkBox', label='Behavior')
	cmds.checkBox('inverseScaleXChkBox', label='Inverse Scale X')
	cmds.checkBox('useTmpJntChkBox', label='Use Temp Joint')

	cmds.separator(h=10, style='in')

	cmds.textFieldGrp('srchTxtFldGrp', label='Search For: ', columnWidth=[(1, 70), (2, 50)], text='lf_')
	cmds.textFieldGrp('rplcTxtFldGrp', label='Replace With: ', columnWidth=[(1, 70), (2, 50)], text='rt_')

	cmds.button(label='Mirror', h=50, c=mirrorJnt)

	cmds.window('mjWin', e=True, w=100, h=100)
	cmds.showWindow('mjWin')


def mirrorJnt(*args):
	mirFuncOpt = cmds.checkBox('mirFuncChkBox', q=True, v=True)
	invScaleX = cmds.checkBox('inverseScaleXChkBox', q=True, v=True)
	useTmpJntOpt = cmds.checkBox('useTmpJntChkBox', q=True, v=True)
	srchStr = cmds.textFieldGrp('srchTxtFldGrp', q=True, text=True)
	rplcStr = cmds.textFieldGrp('rplcTxtFldGrp', q=True, text=True)

	selList = cmds.ls(sl=True)
	cmds.select(cl=True)
	miredJntLs = []

	for each in selList:
		if useTmpJntOpt:
			eachPrnt = cmds.listRelatives(each, parent=True)

			# Create temp joint on world origin.
			cmds.select(cl=True)
			cmds.joint(n='tmp_root_jnt', p=(0, 0, 0))
			cmds.parent(each, 'tmp_root_jnt')

			cmds.select(each, r=True)
			miredJnt = cmds.mirrorJoint(mirrorYZ=True, mirrorBehavior=mirFuncOpt, searchReplace=(srchStr, rplcStr))
			miredJntLs.append(miredJnt[0])

			if eachPrnt:
				cmds.parent(each, eachPrnt[0])
			else:
				cmds.parent(each, w=True)

			cmds.parent(miredJnt, w=True)
			cmds.delete('tmp_root_jnt')
		else:
			cmds.select(each, r=True)
			miredJnt = cmds.mirrorJoint(mirrorYZ=True, mirrorBehavior=mirFuncOpt, searchReplace=(srchStr, rplcStr))
			miredJntLs.append(miredJnt[0])

		if invScaleX:
			jntOriY = cmds.getAttr('%s.jointOrientY' % each)
			jntOriZ = cmds.getAttr('%s.jointOrientZ' % each)
			cmds.setAttr('%s.jointOrientY' % miredJnt[0], -jntOriY)
			cmds.setAttr('%s.jointOrientZ' % miredJnt[0], -jntOriZ)
			cmds.setAttr('%s.scaleX' % miredJnt[0], -1)

	cmds.select(miredJntLs, r=True)


def mirObjUi():
	'''
	Mirror object ui.
	'''

	winName = 'mirObjWin'

	if cmds.window(winName, exists=True):
		cmds.deleteUI(winName)

	cmds.window(winName, title='Mirror Object', maximizeButton=False, minimizeButton=False)

	cmds.columnLayout('mainColLo', adj=True)
	cmds.radioButtonGrp('typeRadBtnGrp', label='Type: ', labelArray2=['Mesh', 'Control'], numberOfRadioButtons=2,
	                    columnWidth=[(1, 70), (2, 70)], select=1, cc=typeRadBtnGrpCC)

	cmds.columnLayout('mirBehaviorColLo', adj=True, visible=False)
	cmds.checkBox('mirBehaviorChkBox', label='Mirror Behavior')
	cmds.setParent('|')

	cmds.textFieldGrp('srchTxtFldGrp', label='Search for: ', text='lf_', columnWidth=[1, 70])
	cmds.textFieldGrp('rplcTxtFldGrp', label='Replace with', text='rt_', columnWidth=[1, 70])
	cmds.button(label='Apply', h=50, c=mirrorObj)

	cmds.window(winName, e=True, w=100, h=100)
	cmds.showWindow(winName)


def typeRadBtnGrpCC(*args):
	selType = cmds.radioButtonGrp('typeRadBtnGrp', q=True, select=True)

	if selType == 1:
		cmds.columnLayout('mirBehaviorColLo', e=True, visible=False)
	elif selType == 2:
		cmds.columnLayout('mirBehaviorColLo', e=True, visible=True)


def mirrorObj(*args):
	# Options
	selType = cmds.radioButtonGrp('typeRadBtnGrp', q=True, select=True)
	mirBehaviorOpt = cmds.checkBox('mirBehaviorChkBox', q=True, v=True)
	srchTxt = cmds.textFieldGrp('srchTxtFldGrp', q=True, text=True)
	rplcTxt = cmds.textFieldGrp('rplcTxtFldGrp', q=True, text=True)

	selList = cmds.ls(sl=True)

	for each in selList:

		# Determine duplicated object's name.
		newName = re.sub(srchTxt, rplcTxt, each)

		# Duplicate
		cmds.duplicate(each, n=newName, renameChildren=True)

		if selType == 1:  # In case selected object is mesh.
			# Filp duplicated object to opposite x side.
			cmds.select(cmds.listRelatives(newName, s=False))
			tak_cleanUpModel.allInOne()

			if not cmds.getAttr('%s.inheritsTransform' % newName):
				cmds.setAttr('%s.inheritsTransform' % newName, 1)

			cmds.select(newName, r=True)
			mel.eval('doGroup 0 1 1;')
			groupName = cmds.ls(sl=True)
			cmds.setAttr("%s.scaleX" % (groupName[0]), -1)

			cmds.parent(newName, w=True)
			cmds.delete(groupName)
			cmds.makeIdentity(newName, apply=True, pn=True)

			# Parent to the same parent node of each
			eachPrnt = cmds.listRelatives(each, p=True)
			if eachPrnt:
				cmds.parent(newName, eachPrnt)

			# Rename child objects
			newChldLs = cmds.listRelatives(newName, ad=True, type='transform')
			dupObjLs = []
			if newChldLs:
				for chld in newChldLs:
					newName = re.sub(srchTxt, rplcTxt, chld)
					# Clear int if exists.
					try:
						newName = re.match(r'(.*)(\d+)', newName).group(1)
					except:
						pass
					cmds.rename(chld, newName)
					dupObjLs.append(newName)

			cmds.select(dupObjLs, r=True)
			tak_cleanUpModel.allInOne()

		elif selType == 2:  # In case selected object is control.
			if mirBehaviorOpt:
				cmds.select(cl=True)
				tmp1Jnt = cmds.joint()
				cmds.CompleteCurrentTool()
				cmds.delete(cmds.parentConstraint(each, tmp1Jnt, mo=False))

				miredJnt = cmds.mirrorJoint(tmp1Jnt, mirrorYZ=True, mirrorBehavior=True)
				cmds.delete(cmds.parentConstraint(miredJnt, newName, mo=False))

				cmds.delete(tmp1Jnt, miredJnt)

			else:
				cmds.select(newName, r=True)
				mel.eval('doGroup 0 1 1;')
				groupName = cmds.ls(sl=True)
				cmds.setAttr("%s.scaleX" % (groupName[0]), -1)

				cmds.parent(newName, w=True)
				cmds.delete(groupName)

			# Rename child objects
			newChldLs = cmds.listRelatives(newName, ad=True, type='transform')
			if newChldLs:
				for chld in newChldLs:
					newName = re.sub(srchTxt, rplcTxt, chld)
					# Clear int if exists.
					try:
						newName = re.match(r'(.*)(\d+)', newName).group(1)
					except:
						pass
					cmds.rename(chld, newName)


# assign the shader of first selection to the others #
def copyMat():
	selList = cmds.ls(sl=True)
	firShape = cmds.ls(selList[0], dag=True, o=True, s=True, sl=True)
	firShadingGrps = cmds.listConnections(firShape, type='shadingEngine')
	i = 0
	while i < (len(selList) - 1):
		i = i + 1
		cmds.select(selList[i], r=True)
		cmds.sets(e=True, forceElement=firShadingGrps[0])
	cmds.select(selList)


def siglJntUI():
	win = 'sjWin'
	if cmds.window(win, exists=True):
		cmds.deleteUI(win)
	cmds.window(win, title='Create Joint on Selected', maximizeButton=False, minimizeButton=False)

	cmds.columnLayout('mainColLay', adj=True)
	cmds.checkBox('hierarchyChkBox', label='Hierarchy')
	cmds.button('createBtn', label='Create', h=50, c=siglJoint)

	cmds.window(win, e=True, w=200, h=70)
	cmds.showWindow(win)


# Create single Joints #
def siglJoint(*args):
	hierOpt = cmds.checkBox('hierarchyChkBox', q=True, v=True)

	selList = cmds.ls(os=True, fl=True)
	jntList = []
	for sel in selList:
		cmds.select(cl=True)
		if '.' in sel:
			pos = cmds.xform(sel, q=True, ws=True, t=True)
		else:
			pos = cmds.xform(sel, q=True, ws=True, rp=True)
		if pos == [0, 0, 0]:
			jnt = cmds.joint(p=(pos), n=sel + '_jnt')
			cmds.CompleteCurrentTool()
			constName = cmds.parentConstraint(sel, jnt, mo=False)
			cmds.delete(constName)
		else:
			jnt = cmds.joint(p=(pos), n=sel + '_jnt')
			cmds.CompleteCurrentTool()
		jntList.append(jnt)

	cmds.select(jntList, r=True)

	# If want to reverse hierarchy, 'childIndex = 0, parentIndex = childIndex + 1'
	if hierOpt:
		while len(jntList) > 1:
			childIndex = -1
			parentIndex = childIndex - 1
			cmds.parent(jntList[childIndex], jntList[parentIndex])
			jntList.pop(childIndex)


# Mirror Controls #
def mirCtrlShapeUi():
	winName = 'mirConWin'
	if cmds.window(winName, exists=True):
		cmds.deleteUI(winName)

	cmds.window(winName, title='Mirror Controls UI', maximizeButton=False, minimizeButton=False)

	cmds.columnLayout('mainClLo', adj=True)
	cmds.textFieldGrp('srchTxtFld', label='Search: ', text='lf_', columnWidth=[(1, 50), (2, 50)])
	cmds.textFieldGrp('rplcTxtFld', label='Replace: ', text='rt_', columnWidth=[(1, 50), (2, 50)])
	cmds.button(label='Apply', h=30, c=mirCtrlShape)

	cmds.window(winName, e=True, w=100, h=50)
	cmds.showWindow(winName)


def mirCtrlShape(*args):
	srch = cmds.textFieldGrp('srchTxtFld', q=True, text=True)
	rplc = cmds.textFieldGrp('rplcTxtFld', q=True, text=True)

	cons = cmds.ls(sl=True)
	for con in cons:
		shpList = cmds.listRelatives(con, s=True)
		symCtrl = re.sub(srch, rplc, con)
		symCtrlShps = cmds.listRelatives(symCtrl, s=True)
		for i in xrange(len(shpList)):
			# get number of cvs
			degs = cmds.getAttr('%s.degree' % shpList[i])
			spans = cmds.getAttr('%s.spans' % shpList[i])
			cvs = degs + spans
			for ii in xrange(cvs):
				# get worldspace translate value of each cv
				cvTr = cmds.xform('%s.cv[%d]' % (shpList[i], ii), q=True, t=True, ws=True)
				# set opposite control's cvs
				cmds.xform('%s.cv[%d]' % (symCtrlShps[i], ii), t=(cvTr[0] * -1, cvTr[1], cvTr[2]), ws=True)


# Mirror Con Selected #
def mirConSel():
	sels = cmds.ls(sl=True)
	src = sels[0]
	trg = sels[1]

	shpList = cmds.listRelatives(src, s=True)
	trgCtrlShps = cmds.listRelatives(trg, s=True)
	for i in xrange(len(shpList)):
		# get number of cvs of source
		degs = cmds.getAttr('%s.degree' % shpList[i])
		spans = cmds.getAttr('%s.spans' % shpList[i])
		cvs = degs + spans
		for ii in xrange(cvs):
			# get worldspace translate value of each cv
			cvTr = cmds.xform('%s.cv[%d]' % (shpList[i], ii), q=True, t=True, ws=True)
			# set opposite control's cvs
			cmds.xform('%s.cv[%d]' % (trgCtrlShps[i], ii), t=(cvTr[0] * -1, cvTr[1], cvTr[2]), ws=True)


# seek the pole vector position #
# description: selcect the shoulder joint, wrist joint, elbow joint, locator and run this script
def poleVector():
	import maya.cmds as cmds
	import maya.OpenMaya as om

	# get position of jnts 
	selList = cmds.ls(sl=True)
	strtJnt = selList[0]
	endJnt = selList[1]
	midJnt = selList[2]
	loc = cmds.spaceLocator(n='poleVector_loc')

	strtJntRawPos = cmds.xform(strtJnt, q=True, rp=True, ws=True)
	endJntRawPos = cmds.xform(endJnt, q=True, rp=True, ws=True)
	midJntRawPos = cmds.xform(midJnt, q=True, rp=True, ws=True)

	# convert the rawPos to the vector
	strtJntPos = om.MVector(strtJntRawPos[0], strtJntRawPos[1], strtJntRawPos[2])
	endJntPos = om.MVector(endJntRawPos[0], endJntRawPos[1], endJntRawPos[2])
	midJntPos = om.MVector(midJntRawPos[0], midJntRawPos[1], midJntRawPos[2])

	# calculate the pole vector position
	midOfStEn = (strtJntPos + endJntPos) / 2
	vec = midJntPos - midOfStEn
	poleVecPos = midJntPos + vec

	# place locator to the pole vector position
	cmds.xform(loc, t=(poleVecPos.x, poleVecPos.y, poleVecPos.z), ws=True)


# Sorting Outliner #
def sortOutl():
	# get the data
	selList = cmds.ls(sl=True)
	prntNode = cmds.listRelatives(selList[0], p=True)

	# make an empty group
	cmds.group(n='tmpGrp', em=True)

	# sorting selList
	reorList = sorted(selList)

	for each in reorList:
		# parent selected items to the tmpGrp in reodered list
		cmds.parent(each, 'tmpGrp')

		# reparent to the origin parent node
		if bool(prntNode) == False:
			cmds.parent(each, w=True)
		else:
			cmds.parent(each, prntNode)

	cmds.delete('tmpGrp')


# Transfer Skin Weights #
def TransSkinWeights():
	selList = mel.eval('string $selList[] = `ls -sl`;')
	src = mel.eval('string $source = $selList[0];')
	trgs = selList[1:]

	for trg in trgs:
		# get the source's shape
		srcShape = cmds.listRelatives(src, c=True, s=True)[0]
		# get skin cluster of the source
		skClu = mel.eval('findRelatedSkinCluster($source);')
		jnts = cmds.skinCluster(skClu, q=True, inf=True)
		# get the target shape
		trgShape = cmds.listRelatives(trg, c=True, s=True, path=True)[0]
		# bind target shape with joints of the source
		desSkClu = cmds.skinCluster(jnts, trgShape, mi=3, dr=4.5, tsb=True, omi=False, nw=1)[0]
		# copy skin weights from the source to the target
		cmds.copySkinWeights(ss=skClu, ds=desSkClu, sa='closestPoint', ia='oneToOne', nm=True)
		print 'Skin weights transfered from %s to %s.' % (src, trg)
	print '#' * 50
	print 'Transfer skin weights job is done.'
	print '#' * 50
	cmds.select(selList)


# Select Influences #
def selInflu():
	sel = cmds.ls(sl=True)[0]

	# get the skin cluster of the source
	skClu = mel.eval('findRelatedSkinCluster("%s");' % sel)

	# get the influences
	infls = cmds.skinCluster(skClu, q=True, inf=True)
	cmds.select(infls)

	return infls


# Attach Hairconstraint to The Joints #
# Frits select a hair constraint and select joints
def hairCnst():
	selList = cmds.ls(sl=True)
	hCnst = selList[0]
	jnts = selList[1:]
	for jnt in jnts:
		# get the hair constraint name
		Name = jnt.split('_jnt')
		dupCnst = cmds.duplicate(hCnst, n='%s_hairConst' % Name[0])
		# place hair constraint to the joint
		constName = cmds.parentConstraint(jnt, dupCnst, mo=False)
		cmds.delete(constName)
		# make zero group
		cmds.select(dupCnst, r=True)
		zroGrp = cmds.group(n='%s_zero' % dupCnst[0])
		# parentConstraint the zero group with the joint
		cmds.parentConstraint(jnt, zroGrp, mo=False)


def addInfUI():
	winName = 'addInfWin'

	if cmds.window(winName, exists=True):
		cmds.deleteUI(winName)

	cmds.window(winName, title='Add Influences', maximizeButton=False, minimizeButton=False)

	cmds.columnLayout('addInfMainColLo', adj=True)

	cmds.rowColumnLayout('addInfListRoColLo', numberOfColumns=2, columnWidth=[(1, 150), (2, 150)],
	                     columnSpacing=[(2, 10)], p='addInfMainColLo')
	cmds.frameLayout('infFrameLo', label='Influences', p='addInfListRoColLo')
	cmds.textScrollList('infTxtScrLs', p='infFrameLo')
	cmds.popupMenu()
	cmds.menuItem(label='Load Selected', c=partial(tak_lib.populateTxtScrList, 'textScrollList', 'infTxtScrLs'))
	cmds.frameLayout('geoFrameLo', label='Geometry', p='addInfListRoColLo')
	cmds.textScrollList('geoTxtScrLs', p='geoFrameLo')
	cmds.popupMenu()
	cmds.menuItem(label='Load Selected', c=partial(tak_lib.populateTxtScrList, 'textScrollList', 'geoTxtScrLs'))

	cmds.checkBox('useGeoChkBox', label='Use Geometry', p='addInfMainColLo')
	# cmds.checkBox('fldWeightsChkBox', label = 'Flood Weights 1 to Influence', p = 'addInfMainColLo')
	cmds.checkBox('lockWeightsChkBox', label='Lock Weights', v=True, p='addInfMainColLo')
	cmds.button(label='Apply', h=50, c=addInf, p='addInfMainColLo')

	cmds.window(winName, e=True, w=300, h=100)
	cmds.showWindow(winName)


# # Populate influences and geometry field with selections
# selList = cmds.ls(sl = True)
# if selList:
# 	infs = selList[0:-1]
# 	geo = selList[-1]
# 	cmds.textScrollList('infTxtScrLs', e = True, append = infs)
# 	cmds.textScrollList('geoTxtScrLs', e = True, append = geo)


def addInf(*args):
	infs = cmds.textScrollList('infTxtScrLs', q=True, allItems=True)
	geos = cmds.textScrollList('geoTxtScrLs', q=True, allItems=True)
	useGeoOpt = cmds.checkBox('useGeoChkBox', q=True, v=True)
	# fldWeightsOpt = cmds.checkBox('fldWeightsChkBox', q = True, v = True)
	lockWeightsOpt = cmds.checkBox('lockWeightsChkBox', q=True, v=True)

	for geo in geos:
		# Get skin cluster
		skinClst = mel.eval('findRelatedSkinCluster("%s");' % geo)

		if not skinClst:
			cmds.select(cl=True)
			tmpBndJnt = cmds.joint(n=geo + '_bnd_jnt')
			cmds.skinCluster(tmpBndJnt, geo, mi=4, dr=4, tsb=True, omi=False, nw=1)
			skinClst = mel.eval('findRelatedSkinCluster("%s");' % geo)

		# Get influences that assigned to geo
		infsAssignGeo = cmds.skinCluster(skinClst, q=True, inf=True)

		for inf in infs:
			if inf in infsAssignGeo:
				continue
			else:
				cmds.skinCluster(skinClst, e=True, dr=4, ug=useGeoOpt, lw=lockWeightsOpt, wt=0, ai=inf)
				cmds.setAttr('%s.liw' % inf, False)

		if useGeoOpt:
			cmds.setAttr('%s.useComponents' % skinClst, 1)
			vtxNumber = cmds.polyEvaluate(geo, vertex=True)
			cmds.skinPercent(skinClst, '%s.vtx[%d:%d]' % (geo, 0, vtxNumber - 1), transformValue=[(inf, 1)])

			cmds.select(geo, r=True)
			mel.eval('removeUnusedInfluences;')

			cmds.delete(tmpBndJnt)
		# for i in xrange(0, vtxNumber, 1):
		# 	cmds.skinPercent(skinClst, '%s.vtx[%d]' %(geo, i), transformValue = [(inf, 1)])


# Assign Random Color Lambert #
def ranColLam():
	selList = cmds.ls(sl=True)
	colRange = (0, 1)
	for x in selList:
		shapeName = cmds.ls(x, s=True, dag=True)
		sgName = cmds.listConnections(shapeName, d=True, type="shadingEngine")
		if not cmds.objExists('%s_ranCol_mat' % x):
			shaderName = cmds.shadingNode('lambert', n='%s_ranCol_mat' % x, asShader=True)
		cmds.setAttr('%s_ranCol_mat.color' % x, random.uniform(*colRange), random.uniform(*colRange),
		             random.uniform(*colRange), type='double3')
		cmds.select(x)
		cmds.hyperShade(assign='%s_ranCol_mat' % x)
	cmds.select(selList, r=True)


# Open with Current Working Directory #
def openCWD():
	curScenePath = cmds.file(q=True, sceneName=True)
	curWorkDir = os.path.dirname(curScenePath)
	filePath = cmds.fileDialog2(fileMode=1, caption='Open', startingDirectory=curWorkDir)[0]
	cmds.file(filePath, open=True, force=True)


# Save in Current Working Directory #
def saveCWD():
	curScenePath = cmds.file(q=True, sceneName=True)
	curWorkDir = os.path.dirname(curScenePath)
	filePath = cmds.fileDialog2(fileMode=0, caption='Save as', startingDirectory=curWorkDir, fileFilter='*.ma')[0]

	if '.ma' in filePath:
		fileType = 'mayaAscii'
	elif '.mb' in filePath:
		fileType = 'mayaBinary'

	cmds.file(rename=filePath)
	cmds.file(save=True, force=True, type=fileType)


def increSave():
	curScenePath = cmds.file(q=True, sceneName=True)
	curWorkDir = os.path.dirname(curScenePath)
	fileName = os.path.basename(curScenePath)
	curVer = re.search(r'_v\d*\d', fileName).group()
	curVerNum = re.search(r'\d*\d', curVer).group()
	padding = len(curVerNum)
	increVer = '_v' + str(int(curVerNum) + 1).zfill(padding)
	filePath = curWorkDir + '/' + re.sub(curVer, increVer, fileName)
	cmds.file(rename=filePath)
	cmds.file(save=True, force=True)


def importCWD():
	curScenePath = cmds.file(q=True, sceneName=True)
	curWorkDir = os.path.dirname(curScenePath)
	filePath = cmds.fileDialog2(fileMode=1, caption='Import', startingDirectory=curWorkDir)[0]
	cmds.file(filePath, i=True, force=True, preserveReferences=True)


def exportCWD():
	curScenePath = cmds.file(q=True, sceneName=True)
	curWorkDir = os.path.dirname(curScenePath)
	filePath = cmds.fileDialog2(fileMode=0, caption='Export', startingDirectory=curWorkDir)[0]
	cmds.file(rename=filePath)
	cmds.file(exportSelected=True, force=True, preserveReferences=True, options='v=0;')


# Set to Wire Mode #
def Wire():
	selList = cmds.ls(sl=True)
	selListShape = cmds.listRelatives(selList, s=True, c=True)
	for sel in selListShape:
		if cmds.getAttr('%s.overrideEnabled' % (sel)):
			cmds.setAttr('%s.overrideShading' % (sel), 1)
			cmds.setAttr('%s.overrideEnabled' % (sel), 0)
		else:
			cmds.setAttr('%s.overrideEnabled' % (sel), 1)
			cmds.setAttr('%s.overrideShading' % (sel), 0)
			cmds.setAttr('%s.overrideColor' % (sel), 14)


# Following Cam #
def followingCam():
	sel = cmds.ls(sl=True)[0]
	camName = cmds.camera(n='%s_follwingCam' % sel)[0]
	grpNode = cmds.duplicate(n='%s_grp' % camName, po=True)
	cmds.parent(camName, grpNode)
	cmds.pointConstraint(sel, grpNode, mo=False)


# Rename Reference Node and Namespace #
def renameRefNode():
	refNode = cmds.ls(sl=True)[0]
	oldNamespace = cmds.referenceQuery(refNode, namespace=True, shortName=True).split('RN')[0]
	result = cmds.promptDialog(title='Rename Reference Node and Namespace', message='New Reference Node Name',
	                           button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel',
	                           dismissString='Cancel', text=refNode)
	if result == 'OK':
		# rename reference node name
		newRefNodeName = cmds.promptDialog(q=True, text=True)
		cmds.lockNode(refNode, lock=False)
		resultNode = cmds.rename(refNode, newRefNodeName)
		cmds.lockNode(resultNode, lock=True)
		if resultNode[-1] in ['1', '2', '3']:
			cmds.error('There is same reference node name.')
		# renmae namespace	
		newNamespace = resultNode.split('RN')[0]
		cmds.namespace(rename=[oldNamespace, newNamespace])


def matchRefNodeNameToNamespace():
	refNodeList = cmds.ls(references=True)

	for refNode in refNodeList:
		refNamespace = cmds.referenceQuery(refNode, namespace=True, shortName=True)
		corRefNodeName = refNamespace + "RN"
		if refNode != corRefNodeName:
			cmds.lockNode(refNode, lock=False)
			resultNode = cmds.rename(refNode, corRefNodeName)
			cmds.lockNode(resultNode, lock=True)


# Line Width #
def lineWidth():
	# window part
	if cmds.window('lwWin', exists=True):
		cmds.deleteUI('lwWin')
	cmds.window('lwWin', title='Line Width', maximizeButton=False, minimizeButton=False)
	cmds.columnLayout(adj=True)
	cmds.floatSliderGrp('lwFSlider', label='Line Width: ', field=True, minValue=1.0, maxValue=10.0, fieldMinValue=1.0,
	                    fieldMaxValue=20.0, value=1.0, step=0.1, dc=changeLineWidth)
	cmds.window('lwWin', e=True, w=200, h=20)
	cmds.showWindow('lwWin')
	mel.eval('PreferencesWindow;')
	mel.eval('preferencesWnd "Display";')


def changeLineWidth(*args):
	lwVal = cmds.floatSliderGrp('lwFSlider', q=True, v=True)
	mel.eval('updateLineWidth %d;' % lwVal)


### Joint Draw Style ###
# 0: bone, 2: none
def drawJntStyle():
	if cmds.window('JSWin', exists=True):
		cmds.deleteUI('JSWin')
	cmds.window('JSWin', title='Draw Joint Style', maximizeButton=False, minimizeButton=False)
	cmds.columnLayout()
	cmds.optionMenu('jsOptMenu', label='Draw Style: ', cc=djsChangeCmd)
	cmds.menuItem(label='None')
	cmds.menuItem(label='Bone')
	cmds.showWindow('JSWin')


def djsChangeCmd(*args):
	opt = cmds.optionMenu('jsOptMenu', q=True, v=True)
	if opt == 'None': opt = 2
	if opt == 'Bone': opt = 0
	selList = cmds.ls(sl=True)
	for sel in selList:
		if cmds.objectType(sel) == 'joint':
			cmds.setAttr('%s.drawStyle' % sel, opt)


class SelHilightTogg:
	switch = 0

	def UI(self):
		win = 'selHilTog'
		if cmds.window(win, exists=True):
			cmds.deleteUI(win)
		cmds.window(win, title='Selection Hilighting', maximizeButton=False, minimizeButton=False)
		cmds.columnLayout(adj=True)
		cmds.button(label='On/Off', c=self.onOff)
		cmds.showWindow(win)

	def onOff(self, *args):
		curPanel = cmds.getPanel(withFocus=True)
		if switch:
			cmds.modelEditor(curPanel, e=True, sel=False)
			self.switch = 0
		else:
			cmds.modelEditor(curPanel, e=True, sel=True)
			self.switch = 1


def setJntColorUI():
	winName = 'setJntCol'
	if cmds.window(winName, exists=True):
		cmds.deleteUI(winName)

	cmds.window(winName, title='Color Override', maximizeButton=False, minimizeButton=False)
	cmds.columnLayout(columnAttach=('both', 5), backgroundColor=[.2, .2, .2], adj=True)
	colorSwatchMenu = cmds.gridLayout(aec=False, numberOfRowsColumns=(10, 3), cwh=(40, 24),
	                                  backgroundColor=[.2, .2, .2])
	colorSwatchesList = [1, 2, 3, 11, 24, 21, 12, 10, 25, 4, 13, 20, 8, 30, 9, 5, 6, 18, 15, 29, 28, 7, 27, 19, 23, 26,
	                     14, 17, 22, 16]

	for i in colorSwatchesList:
		colorBuffer = cmds.colorIndex(i, q=True)
		cmds.canvas(('%s%i' % ('colorCanvas_', i)), rgb=colorBuffer, pc=partial(setJntColor, i))

	cmds.showWindow(winName)


def setJntColor(color, *args):
	selList = cmds.ls(sl=True)
	for x in selList:
		shps = cmds.listRelatives(x, s=True)
		if shps:
			print shps
			for shp in shps:
				print shp
				cmds.setAttr('%s|%s.overrideEnabled' % (x, shp), 1)
				cmds.setAttr('%s|%s.overrideColor' % (x, shp), int(color))

		cmds.setAttr('%s.overrideEnabled' % (x), 1)
		cmds.setAttr('%s.overrideColor' % (x), int(color))


def getVertsCenter():
	# selList = cmds.ls(sl = True, fl = True)
	# vectorPallette = OpenMaya.MVector(0.0, 0.0, 0.0)

	# for sel in selList:
	# 	# selWorldPos = cmds.xform(sel, q = True, ws = True, t = True)
	# 	selWorldPos = cmds.pointPosition(sel, w = True)
	# 	selVec = OpenMaya.MVector(*selWorldPos)
	# 	vectorPallette += selVec

	# centerVec = vectorPallette / len(selList)

	# cmds.select(cl = True)
	# tmpCntJnt = cmds.joint(n = 'temp_center_jnt')
	# cmds.xform(tmpCntJnt, ws = True, t = (centerVec.x, centerVec.y, centerVec.z))

	clst = cmds.cluster()
	cmds.select(cl=True)
	tmpJnt = cmds.joint(n='temp_center_jnt')

	cmds.delete(cmds.parentConstraint(clst, tmpJnt))
	cmds.delete(clst)


def combinedTexture(*args):
	# Hardware Texturing Set to Combined Texture of Selected Objects's Materials #
	selObjs = cmds.ls(sl=True)

	for obj in selObjs:
		shaderNode = tak_lib.getMatFromSel(obj)[0]
		if cmds.objExists(shaderNode):
			materialInfoNode = cmds.ls(cmds.listConnections(shaderNode), type='materialInfo')[-1]
			try:
				cmds.connectAttr('%s.message' % shaderNode, '%s.texture' % materialInfoNode, nextAvailable=True)
			except:
				pass


# Duplicate Material and Assign for Selected Mesh #
def dupMatAndAssign():
	selGeoLs = cmds.ls(sl=True)

	# Get materials
	lod03Mats = []
	for selGeo in selGeoLs:
		selGeoMat = tak_lib.getMatFromSel(selGeo)
		lod03Mats.extend(selGeoMat)
	lod03Mats = list(set(lod03Mats))

	for lod03Mat in lod03Mats:
		cmds.select(lod03Mat, r=True)
		cmds.hyperShade(duplicate=True)
		dupMat = cmds.ls(sl=True)[0]
		print dupMat

		# Assign duplicated material to lod02 geometries.
		cmds.hyperShade(objects=lod03Mat)
		lod02Geos = [x for x in cmds.ls(sl=True) if "lod02_" in x]
		print lod02Geos
		cmds.select(lod02Geos, r=True)
		cmds.hyperShade(assign=dupMat)


def lod02Mat():
	selGeoLs = cmds.ls(sl=True)

	# Get materials
	lod03Mats = []
	for selGeo in selGeoLs:
		selGeoMat = tak_lib.getMatFromSel(selGeo)
		lod03Mats.extend(selGeoMat)
	lod03Mats = list(set(lod03Mats))

	for lod03Mat in lod03Mats:
		# Default maya shader attribute names.
		colorAttr = ".color"
		transparencyAttr = ".transparency"
		invertTransMapOpt = False

		# Decide attribute names depend on material.
		lod03MatNodeType = cmds.nodeType(lod03Mat)

		if lod03MatNodeType in ["VRayMtl"]:
			transparencyAttr = ".opacityMap"
			invertTransMapOpt = True
		elif lod03MatNodeType in ["aiStandardSurface"]:
			colorAttr = ".baseColor"
			transparencyAttr = ".opacity"
		elif lod03MatNodeType in ["surfaceShader"]:
			colorAttr = ".outColor"
			transparencyAttr = ".outTransparency"

		# Create lod02 material.
		lod02Mat = cmds.shadingNode("lambert", asShader=True, n="lod02_" + lod03Mat)

		# Check color file node.
		colorFileNode = cmds.listConnections(lod03Mat + colorAttr)
		if colorFileNode:
			cmds.select(colorFileNode, r=True)
			cmds.hyperShade(duplicate=True)
			dupColorFileNode = cmds.ls(sl=True)[0]
			# print dupColorFileNode
			cmds.connectAttr(dupColorFileNode + ".outColor", lod02Mat + ".color", f=True)
		else:
			colorRgb = cmds.getAttr(lod03Mat + colorAttr)
			# print colorRgb
			cmds.setAttr(lod02Mat + ".color", colorRgb[0][0], colorRgb[0][1], colorRgb[0][2])

		# Check transparency file node.
		trspFileNode = cmds.listConnections(lod03Mat + transparencyAttr)
		if trspFileNode:
			cmds.select(trspFileNode, r=True)
			cmds.hyperShade(duplicate=True)
			dupTrspFileNode = cmds.ls(sl=True)[0]
			cmds.setAttr(dupTrspFileNode + ".invert", invertTransMapOpt)
			cmds.connectAttr(dupTrspFileNode + ".outColor", lod02Mat + ".transparency", f=True)
		else:
			trspRgb = cmds.getAttr(lod03Mat + transparencyAttr)
			if "VRay" in lod03MatNodeType or "ai" in lod03MatNodeType:
				cmds.setAttr(lod02Mat + ".transparency", 1 - trspRgb[0][0], 1 - trspRgb[0][1], 1 - trspRgb[0][2])
			else:
				cmds.setAttr(lod02Mat + ".transparency", trspRgb[0][0], trspRgb[0][1], trspRgb[0][2])

		# Assign lod02 material to lod02 geometry.
		cmds.hyperShade(objects=lod03Mat)
		lod02Geos = [x for x in cmds.ls(sl=True) if "lod02_" in x]
		cmds.select(lod02Geos)
		cmds.hyperShade(assign=lod02Mat)

		# Set hardware texturing to combined texture.
		materialInfoNode = cmds.ls(cmds.listConnections(lod02Mat), type='materialInfo')[-1]
		connectedMat = cmds.listConnections(materialInfoNode + ".texture[0]")
		if connectedMat:
			cmds.disconnectAttr('%s.message' % connectedMat[0], '%s.texture[0]' % materialInfoNode)
		cmds.connectAttr('%s.message' % lod02Mat, '%s.texture[0]' % materialInfoNode, nextAvailable=True)


def solidColMat():
	selGeos = cmds.ls(sl=True)
	color = cmds.grabColor(rgb=True)
	shaderName = cmds.shadingNode('lambert', n='solCol_mat', asShader=True)
	cmds.setAttr("%s.color" % shaderName, color[0], color[1], color[2], type='double3')
	cmds.setAttr('%s.diffuse' % shaderName, 1)

	# assign shader
	cmds.select(selGeos)
	cmds.hyperShade(assign=shaderName)


# cmds.select(cl = True)





def assignLambertWithSelectedTexture():
	selLs = cmds.ls(sl=True)
	selectedTexture = selLs[0]
	selectedGeos = selLs[1:]

	shadingEngine = tak_lib.findShadingEngine(selectedTexture)
	meshes = cmds.listConnections(shadingEngine, d=False, scn=True, type='mesh')

	if selectedGeos:
		meshes = selectedGeos

	shaderName = cmds.shadingNode('lambert', n='%s_lambert' % selectedTexture, asShader=True)
	cmds.connectAttr("%s.outColor" % selectedTexture, "%s.color" % shaderName, f=True)

	cmds.select(meshes, r=True)
	cmds.hyperShade(assign=shaderName)

	cmds.select(cl=True)


def useDfltMat():
	curPanel = cmds.getPanel(withFocus=True)
	curUdmState = cmds.modelEditor(curPanel, q=True, udm=True)
	if curUdmState:
		cmds.modelEditor(curPanel, e=True, udm=False)
	# remove heads up display
	# cmds.headsUpDisplay('defaultMatModeDisplay', remove = True)
	else:
		cmds.modelEditor(curPanel, e=True, udm=True)
	# show heads up display
	# tak_lib.showHUD(widgetName = 'defaultMatModeDisplay', title = 'Default Material Mode')


def iso():
	selList = cmds.ls(sl=True)
	if selList:
		cmds.InvertSelection()
	invSel = cmds.ls(sl=True)

	curPanel = cmds.getPanel(withFocus=True)
	curIsoState = cmds.isolateSelect(curPanel, q=True, state=True)

	if curIsoState:
		cmds.headsUpDisplay('isoDisplay', remove=True)
		cmds.isolateSelect(curPanel, state=False)
		mel.eval('isoSelectAutoAddNewObjs %s false;' % curPanel)
		cmds.select(cl=True)
	else:
		tak_lib.showHUD('isoDisplay', 'Isolate Mode')
		cmds.isolateSelect(curPanel, state=True)
		mel.eval('isoSelectAutoAddNewObjs %s true;' % curPanel)

		cmds.select(selList, r=True)
		cmds.isolateSelect(curPanel, addSelected=True)

		if invSel:
			cmds.select(invSel, r=True)
			cmds.isolateSelect(curPanel, removeSelected=True)

		cmds.select(cl=True)


def isoAdd():
	curPanel = cmds.getPanel(withFocus=True)
	cmds.isolateSelect(curPanel, addSelected=True)


def isoRmv():
	curPanel = cmds.getPanel(withFocus=True)
	cmds.isolateSelect(curPanel, removeSelected=True)


def wireOnOff():
	wsaState = cmds.displayPref(q=True, wsa=True)
	if wsaState in ['full', 'reduced']:
		cmds.displayPref(wsa='none')
	# tak_lib.showHUD('wireStateDisplay', 'Wire Off')
	else:
		cmds.displayPref(wsa='full')
	# cmds.headsUpDisplay('wireStateDisplay', remove = True)


def plcHldr():
	selList = cmds.ls(sl=True)
	for sel in selList:
		loc = cmds.spaceLocator(n='%s_plcHldr_loc' % (sel))
		if '[' in sel:
			vtxPos = cmds.xform(sel, q=True, ws=True, t=True)
			cmds.xform(loc, t=vtxPos, ws=True)
		else:
			pCnst = cmds.parentConstraint(sel, loc, mo=False)
			cmds.delete(pCnst)


def delBsTargetUI():
	win = 'delBsTrgWin'
	if cmds.window(win, exists=True):
		cmds.deleteUI(win)
	cmds.window(win, title='Delete BlendShape Target', maximizeButton=False, minimizeButton=False)
	cmds.columnLayout('mainColLay', adj=True)
	cmds.textFieldButtonGrp('bsNameTexFld', label='BlendShape Name: ', buttonLabel='<<',
	                        bc=partial(loadSel, 'bsNameTexFld'), columnWidth=[(1, 100), (2, 100)])
	cmds.textFieldButtonGrp('baseNameTexFld', label='Base Geometry: ', buttonLabel='<<',
	                        bc=partial(loadSel, 'baseNameTexFld'), columnWidth=[(1, 100), (2, 100)])
	cmds.textFieldButtonGrp('trgNameTexFld', label='Target Name: ', buttonLabel='<<',
	                        bc=partial(loadSel, 'trgNameTexFld'), columnWidth=[(1, 100), (2, 100)])
	cmds.button('appBtn', label='Apply', h=50, c=delBsTarget)
	cmds.window(win, e=True, w=200, h=100)
	cmds.showWindow(win)


def delBsTarget(*args):
	bsName = cmds.textFieldButtonGrp('bsNameTexFld', q=True, text=True)
	baseName = cmds.textFieldButtonGrp('baseNameTexFld', q=True, text=True)
	targetName = cmds.textFieldButtonGrp('trgNameTexFld', q=True, text=True)
	bsAttrList = cmds.aliasAttr(bsName, q=True)
	selTrgIndexInList = bsAttrList.index(targetName)
	selTrgWeightIndex = selTrgIndexInList + 1
	reObj = re.search(r'\d+', bsAttrList[selTrgWeightIndex])
	targetIndex = int(reObj.group())
	cmds.blendShape(bsName, e=True, remove=True, target=(baseName, targetIndex, targetName, 1.0))


def loadSel(widget, *args):
	sel = cmds.ls(sl=True)[0]
	cmds.textFieldButtonGrp(widget, e=True, text=sel)


def trackingLoc():
	sel = cmds.ls(sl=True)
	# get frame range
	# startFrame = cmds.playbackOptions(q = True, min = True)
	startFrame = cmds.currentTime(q=True)
	endFrame = cmds.playbackOptions(q=True, max=True)
	for i in xrange(int(startFrame), int(endFrame) + 1):
		cmds.currentTime(i)
		loc = cmds.spaceLocator(n='%s_%s_tLoc' % (sel[0], i))
		vtxPos = cmds.xform(sel, q=True, ws=True, t=True)
		cmds.xform(loc, t=vtxPos, ws=True)


def crvFromSelsUi():
	if cmds.window('cfsWin', exists=True):
		cmds.deleteUI('cfsWin')
	cmds.window('cfsWin', title='Curve From Selections', maximizeButton=False, minimizeButton=False)

	cmds.columnLayout('mainClo', adj=True)
	cmds.rowColumnLayout('mainRclo', numberOfColumns=2, columnSpacing=[(2, 30)])
	cmds.optionMenu('dgrOptMenu', label='Degree: ')
	cmds.menuItem(label='1 Linear', p='dgrOptMenu')
	cmds.menuItem(label='3 Cubic', p='dgrOptMenu')
	cmds.optionMenu('dgrOptMenu', e=True, v='3 Cubic')
	cmds.checkBox('clsChkBox', label='Colse')

	cmds.button(label='Create', h=50, c=crvFromSels, p='mainClo')

	cmds.window('cfsWin', e=True, w=100, h=50)
	cmds.showWindow('cfsWin')


def crvFromSels(*args):
	dOpt = cmds.optionMenu('dgrOptMenu', q=True, v=True)
	if dOpt == '1 Linear':
		dOpt = 1
	elif dOpt == '3 Cubic':
		dOpt = 3

	clsOpt = cmds.checkBox('clsChkBox', q=True, v=True)

	selList = cmds.ls(os=True)
	positionList = []
	for sel in selList:
		if '.' in sel:
			worldPosition = cmds.xform(sel, q=True, t=True, ws=True)
		else:
			worldPosition = cmds.xform(sel, q=True, rp=True, ws=True)
		positionList.append(tuple(worldPosition))
	crv = cmds.curve(d=dOpt, ep=positionList)
	if clsOpt:
		cmds.closeCurve(crv, ps=1, rpo=1, bb=0.5, bki=0, p=0.1)


def zeroVtx():
	selVtxs = cmds.ls(sl=True, fl=True)
	for vtx in selVtxs:
		vtxPos = cmds.pointPosition(vtx, world=True)
		cmds.xform(vtx, ws=True, t=(0, vtxPos[1], vtxPos[2]))


def symmetry(axis):
	x = 1
	y = 1
	z = 1

	if axis == 'x':
		x = -1
	elif axis == 'y':
		y = -1
	elif axis == 'z':
		z = -1

	sel = cmds.ls(sl=True)[0]

	# delete history
	cmds.delete(sel, ch=True)
	# freeze transform
	cmds.makeIdentity(sel, apply=True)

	if axis != 'z':
		# pivot to world 0, 0, 0
		cmds.dR_customPivotTool()
		cmds.move(0, 0, 0, '%s.scalePivot' % (sel), '%s.rotatePivot' % (sel), a=True, ws=True)
		cmds.dR_customPivotTool()

	instGeo = cmds.instance(sel)
	cmds.scale(x, y, z, instGeo, r=True)


def mirrorCtrlsUI():
	winName = 'mirCtrlWin'
	if cmds.window(winName, exists=True):
		cmds.deleteUI(winName)
	cmds.window(winName, title='Mirror Controls', maximizeButton=False, minimizeButton=False)

	cmds.columnLayout('mainColLo', adj=True, p=winName)
	cmds.optionMenu('searchStrOpMenu', label='Search For: ')
	cmds.menuItem(label='lf_')
	cmds.menuItem(label='_L')
	cmds.optionMenu('replaceStrOpMenu', label='Replace With: ')
	cmds.menuItem(label='rt_')
	cmds.menuItem(label='_R')
	cmds.checkBox('bhvrChkBox', label='Behavior', p='mainColLo')
	cmds.button(label='Apply', c=mirrorCtrls, p='mainColLo')

	cmds.window(winName, e=True, w=100, h=50)
	cmds.showWindow(winName)


# mirror controls
def mirrorCtrls(*args):
	selList = cmds.ls(sl=True)
	srchStr = cmds.optionMenu('searchStrOpMenu', q=True, value=True)
	rplcStr = cmds.optionMenu('replaceStrOpMenu', q=True, value=True)
	bhvrOpt = cmds.checkBox('bhvrChkBox', q=True, v=True)

	for sel in selList:
		trg = re.sub(srchStr, rplcStr, sel)

		selTr = cmds.getAttr('%s.translate' % (sel))[0]
		selRo = cmds.getAttr('%s.rotate' % (sel))[0]
		selSc = cmds.getAttr('%s.scale' % (sel))[0]

		if bhvrOpt:
			selTr = (-selTr[0], -selTr[1], -selTr[2])
			selRo = (selRo[0], selRo[1], selRo[2])
			selSc = (selSc[0], selSc[1], selSc[2])
		else:
			selTr = (-selTr[0], selTr[1], selTr[2])
			selRo = (selRo[0], -selRo[1], -selRo[2])
			selSc = (selSc[0], selSc[1], selSc[2])

		cmds.setAttr('%s.translate' % (trg), *selTr)
		cmds.setAttr('%s.rotate' % (trg), *selRo)
		cmds.setAttr('%s.scale' % (trg), *selSc)


# hide/show viewport polygon
def hideShowViewPoly():
	curPanel = cmds.getPanel(withFocus=True)
	state = cmds.modelEditor(curPanel, q=True, polymeshes=True)
	if state:
		cmds.modelEditor(curPanel, e=True, polymeshes=False)
	else:
		cmds.modelEditor(curPanel, e=True, polymeshes=True)


# hide/show viewport joint
def hideShowViewJnt():
	curPanel = cmds.getPanel(withFocus=True)
	state = cmds.modelEditor(curPanel, q=True, joints=True)
	if state:
		cmds.modelEditor(curPanel, e=True, joints=False)
	else:
		cmds.modelEditor(curPanel, e=True, joints=True)


# hide/show viewport curve
def hideShowViewCrv():
	curPanel = cmds.getPanel(withFocus=True)
	state = cmds.modelEditor(curPanel, q=True, nurbsCurves=True)
	if state:
		cmds.modelEditor(curPanel, e=True, nurbsCurves=False)
	else:
		cmds.modelEditor(curPanel, e=True, nurbsCurves=True)


# hide/show viewport wireframe
def hideShowViewWire():
	curPanel = cmds.getPanel(withFocus=True)
	state = cmds.modelEditor(curPanel, q=True, sel=True)
	if state:
		cmds.modelEditor(curPanel, e=True, sel=False)
	else:
		cmds.modelEditor(curPanel, e=True, sel=True)


# hide/show viewport model only
def hideShowViewMdl():
	curPanel = cmds.getPanel(withFocus=True)
	state = cmds.modelEditor(curPanel, q=True, clipGhosts=True)

	if state:
		cmds.modelEditor(curPanel, e=True, allObjects=False)
		cmds.modelEditor(curPanel, e=True, polymeshes=True)
		cmds.modelEditor(curPanel, e=True, nurbsSurfaces=True)
		cmds.modelEditor(curPanel, e=True, strokes=True)
		cmds.modelEditor(curPanel, e=True, nParticles=True)
		cmds.modelEditor(curPanel, e=True, fluids=True)
		cmds.modelEditor(curPanel, e=True, nCloths=True)
	# cmds.modelEditor(curPanel, e = True, lights = True)

	else:
		cmds.modelEditor(curPanel, e=True, allObjects=True)


# turn off shape visibility
def turnOffShp():
	selList = cmds.ls(sl=True)
	for sel in selList:
		shp = cmds.listRelatives(sel, s=True)[0]
		cmds.setAttr("%s.visibility" % (shp), False)


def locGrp():
	"""
	Create locator and group above selected object.
	"""

	selList = cmds.ls(sl=True)
	for sel in selList:
		# Create locator and match to selection.
		loc = cmds.spaceLocator(n=sel + '_loc')[0]
		cmds.delete(cmds.parentConstraint(sel, loc, mo=False))
		cmds.delete(cmds.scaleConstraint(sel, loc, mo=False))

		zroGrp = cmds.duplicate(loc, po=True, n=loc + "_zero")
		autoGrp = cmds.duplicate(loc, po=True, n=loc + "_auto")

		cmds.parent(sel, loc)
		cmds.parent(loc, autoGrp)
		cmds.parent(autoGrp, zroGrp)


### Set Display Type ###
def displayType():
	if cmds.window('dtWin', exists=True):
		cmds.deleteUI('dtWin')
	cmds.window('dtWin', title='Display Type', maximizeButton=False, minimizeButton=False)
	cmds.columnLayout()
	cmds.optionMenu('dtOptMenu', label='Display Type: ', cc=dtChangeCmd)
	cmds.menuItem(label='Normal')
	cmds.menuItem(label='Template')
	cmds.menuItem(label='Reference')
	cmds.showWindow('dtWin')


def dtChangeCmd(*args):
	opt = cmds.optionMenu('dtOptMenu', q=True, v=True)
	if opt == 'Normal':
		opt = 0
	elif opt == 'Template':
		opt = 1
	elif opt == 'Reference':
		opt = 2
	selList = cmds.ls(sl=True)
	for sel in selList:
		shps = cmds.listRelatives(sel, s=True)
		for shp in shps:
			try:
				cmds.setAttr('%s.overrideEnabled' % shp, 1)
			except:
				pass
			try:
				cmds.setAttr('%s.overrideDisplayType' % shp, opt)
			except:
				cmds.error('Same shape name exists.')


def revGrp():
	"""
	Create reverse group that subtract control transform.
	"""
	selList = cmds.ls(sl=True)
	for sel in selList:
		# revGrp = doGroup(sel, '_rev')
		revGrp = cmds.duplicate(sel, po=True, n=sel + '_rev')[0]
		cmds.parent(sel, revGrp)
		mulNode = cmds.createNode('multiplyDivide', n=sel + '_rev_mul')
		inputList = ['input2X', 'input2Y', 'input2Z']
		for input in inputList:
			cmds.setAttr('{0}.{1}'.format(mulNode, input), -1)
		cmds.connectAttr('{0}.translate'.format(sel), '{0}.input1'.format(mulNode), f=True)
		cmds.connectAttr('{0}.output'.format(mulNode), '{0}.translate'.format(revGrp), f=True)


def doGroup(obj, suffix):
	objPrnt = cmds.listRelatives(obj, p=True)
	grpNode = cmds.createNode('transform', n=obj+suffix)

	cmds.delete(cmds.parentConstraint(obj, grpNode, mo=False))

	objScale = cmds.getAttr('%s.scale' % obj)[0]
	cmds.setAttr('%s.scale' % obj, 1, 1, 1)

	cmds.parent(obj, grpNode)

	cmds.setAttr('%s.scale' % grpNode, *objScale)

	if objPrnt:
		cmds.parent(grpNode, objPrnt)

	return grpNode


# bake camera #
def bakeCam():
	# Disable viewport update
	cmds.refresh(su=True)

	# select cam to bake
	cam = cmds.ls(sl=True)[0]

	# duplicate camera
	dupCam = cmds.duplicate(cam, n=cam + '_baked')[0]
	if cmds.listRelatives(dupCam, p=True):
		cmds.parent(dupCam, world=True)

	# unlock duplicated camera
	attrList = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ',
	            'visibility']
	for attr in attrList:
		cmds.setAttr('%s.%s' % (dupCam, attr), lock=False)

		# constriant with original camera
	prntCnst = cmds.parentConstraint(cam, dupCam, mo=False)

	# Connect keyable shape attributes
	toCnctAttrs = ['focalLength']
	for attr in toCnctAttrs:
		cmds.connectAttr('%sShape.%s' % (cam, attr), '%sShape.%s' % (dupCam, attr), f=True)

	# bake camera animation
	minFrame = cmds.playbackOptions(q=True, min=True)
	maxFrame = cmds.playbackOptions(q=True, max=True)
	cmds.bakeResults(dupCam, simulation=True, t=(minFrame, maxFrame))

	# delete parent constraint of baked camera
	cmds.delete(prntCnst)

	# Enable viewport update
	cmds.refresh(su=False)
	cmds.refresh(f=True)


def dockOutliner():
	'''
	Dockable outliner
	'''
	# check the dock existing
	if cmds.dockControl("dockOutliner", q=True, exists=True):
		cmds.deleteUI("dockOutliner")

	cmds.window('dockOutl')

	cmds.frameLayout(labelVisible=False)
	panel = cmds.outlinerPanel()
	outliner = cmds.outlinerPanel(panel, query=True, outlinerEditor=True)
	cmds.outlinerEditor(outliner, edit=True, mainListConnection='worldList', selectionConnection='modelList',
	                    showShapes=False, showReferenceNodes=True, showReferenceMembers=False, showAttributes=False,
	                    showConnected=False, showAnimCurvesOnly=False, autoExpand=False, showDagOnly=True,
	                    ignoreDagHierarchy=False, expandConnections=False, showCompounds=True,
	                    showNumericAttrsOnly=False, highlightActive=True, autoSelectNewObjects=False,
	                    doNotSelectNewObjects=False, transmitFilters=False, showSetMembers=True,
	                    setFilter='defaultSetFilter')

	cmds.showWindow('dockOutl')

	# make dockable
	allowedAreas = ['right', 'left']
	cmds.dockControl('dockOutliner', label="Outliner", area='left', content='dockOutl', allowedArea=allowedAreas)
	cmds.dockControl('dockOutliner', e=True, w=353, h=420)


def editDfmMemberUI():
	winName = 'editDfmMemberWin'

	if cmds.window(winName, exists=True):
		cmds.deleteUI(winName)

	cmds.window(winName, title='Edit Deformer Membership', maximizeButton=False, minimizeButton=False)

	cmds.columnLayout(adj=True)

	cmds.textFieldButtonGrp('dfmTxtFldBtnGrp', label='Deformer: ', buttonLabel='Load Sel',
	                        columnWidth=[(1, 60), (2, 100)],
	                        bc=partial(tak_lib.loadSel, 'textFieldButtonGrp', 'dfmTxtFldBtnGrp'))

	cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 105), (2, 105)], columnSpacing=[(2, 5)])
	cmds.button(label='Add', c=partial(editDfmMember, 'add'))
	cmds.button(label='Remove', c=partial(editDfmMember, 'remove'))

	cmds.window(winName, e=True, w=100, h=50)
	cmds.showWindow(winName)


def editDfmMember(mode, *args):
	dfm = cmds.textFieldButtonGrp('dfmTxtFldBtnGrp', q=True, text=True)
	dfmSet = ''

	# Get deformer set
	connections = cmds.listConnections(dfm, s=False, d=True)
	for connection in connections:
		if cmds.objectType(connection) == 'objectSet' and not 'modelPanel' in connection:
			dfmSet = connection
			print 'Result: %s\'s deformer set is "%s"' % (dfm, dfmSet)
			break
	if not dfmSet:
		print 'There is no valid deformer set.'
		return

	# Add selected vertex to the deformer set
	vtxList = cmds.ls(sl=True)

	if mode == 'add':
		cmds.sets(vtxList, add=dfmSet)
	if mode == 'remove':
		cmds.sets(vtxList, remove=dfmSet)


def selEveryNUI():
	winName = 'selEveryNWin'

	if cmds.window(winName, exists=True):
		cmds.deleteUI(winName)

	cmds.window(winName, title='Select EveryN Edge Ring/Loop', maximizeButton=False, minimizeButton=False)

	cmds.columnLayout(adj=True)

	cmds.textFieldGrp('skipTxtFldGrp', label='Every N: ', text='2', columnWidth=[(1, 70), (2, 30)], enable=True)

	cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 100), (2, 100)], columnSpacing=[(2, 5)])
	cmds.button(label='Edge Ring', c=partial(selEveryN, 'edgeRing'))
	# cmds.button(label = 'Edge Ring Delete', c = partial(selEveryN, 'edgeRingDel'))
	cmds.button(label='Edge Loop', c=partial(selEveryN, 'edgeLoopOrBorder'))
	# cmds.button(label = 'Edge Loop Delete', c = partial(selEveryN, 'polyDelEdge'))

	cmds.window(winName, e=True, w=100, h=50)
	cmds.showWindow(winName)


def selEveryN(mode, *args):
	skipNum = cmds.textFieldGrp('skipTxtFldGrp', q=True, text=True)

	if mode == 'edgeLoopOrBorderDel':
		mel.eval('polySelectEdgesEveryN "edgeLoopOrBorder" %d;' % int(skipNum))
		mel.eval('polyConvertToRingAndCollapse;')
	elif mode == 'edgeRingDel':
		mel.eval('polySelectEdgesEveryN "edgeRing" %d;' % int(skipNum))
		cmds.SelectEdgeLoopSp()
		cmds.DeleteEdge()
	else:
		mel.eval('polySelectEdgesEveryN "%s" %d;' % (mode, int(skipNum)))


def arrangeInARow(offset=1.0):
	'''
	Arrange in a row layout for selected objects.
	'''

	selList = cmds.ls(sl=True)
	bndBox = cmds.exactWorldBoundingBox(selList[0])
	objWidth = bndBox[3] - bndBox[0]
	offset = objWidth * offset

	firstObjPos = cmds.xform(selList[0], q=True, ws=True, t=True)

	for sel in selList[1:]:
		firstObjPos = [firstObjPos[0] + objWidth + offset, firstObjPos[1], firstObjPos[2]]
		cmds.xform(sel, ws=True, t=firstObjPos)


def arrangeInAColumn(offset=.1):
	'''
	Arrange in a column layout for selected objects.
	'''

	selList = cmds.ls(sl=True)
	bndBox = cmds.exactWorldBoundingBox(selList[0])
	objHeight = bndBox[4] - bndBox[1]
	offset = objHeight * offset

	firstObjPos = cmds.xform(selList[0], q=True, ws=True, t=True)

	for sel in selList[1:]:
		firstObjPos = [firstObjPos[0], firstObjPos[1] - objHeight - offset, firstObjPos[2]]
		cmds.xform(sel, ws=True, t=firstObjPos)


def keyRglrInterval(startFrame=1, interval=10, count=50):
	'''
	Key regular interval with user defined info.
	'''

	cmds.autoKeyframe(state=True)

	cmds.refresh(su=True)
	cmds.currentTime(startFrame)
	for i in xrange(count):
		cmds.setKeyframe()
		startFrame += interval
		cmds.currentTime(startFrame)
	cmds.refresh(su=False)
	cmds.refresh(f=True)


def assignSurfMat():
	'''
	Assign surface material. 
	Select a color texture then run.
	'''

	# Get shading group from selected texture node.
	colFile = cmds.ls(sl=True)[0]
	colFileCons = cmds.listConnections(colFile, s=False, d=True)
	for item in colFileCons:
		if not cmds.objectType(item) in ['defaultTextureList', 'materialInfo']:
			mat = item

	matCons = cmds.listConnections(mat, s=False, d=True)
	for item in matCons:
		if cmds.objectType(item) == 'shadingEngine':
			sgNode = item

	# Create a lambert material.
	lamShd = cmds.shadingNode('lambert', asShader=True, n='%s_surf_mat' % sgNode.split('_SG')[0])
	cmds.connectAttr('%s.outColor' % colFile, '%s.color' % lamShd)

	# Connect color file node outColor attribute to surface material attribute of shading group.
	cmds.connectAttr('%s.outColor' % lamShd, '%s.surfaceShader' % sgNode)
	cmds.disconnectAttr('%s.outColor' % lamShd, '%s.surfaceShader' % sgNode)
	cmds.connectAttr('%s.outColor' % lamShd, '%s.surfaceShader' % sgNode)


def attachSpecSphere():
	'''
	Attach mesh specular to selected vertex(s) or between two edges.
	'''

	radius = 0.1
	selLs = cmds.ls(sl=True, fl=True)
	chName = selLs[0].split(':')[0]

	# Create specular material for specular sphere.
	if not cmds.objExists('specular_mat'):
		cmds.shadingNode('surfaceShader', asShader=True, n='specular_mat')
		cmds.setAttr('specular_mat.outColor', 1, 1, 1)

	if '.vtx' in selLs[0]:
		for vtx in selLs:
			# Get vertex world position.
			vtxPos = cmds.pointPosition(vtx, w=True)

			# Create a sphere.
			specSphere = cmds.polySphere(n='%s_specSphere#' % (chName), r=radius, ch=False)[0]
			anchGrp = cmds.group(specSphere, n=specSphere + '_anchor')

			# Assign shader.
			cmds.select(specSphere, r=True)
			cmds.hyperShade(assign='specular_mat')

			# Move sphere to a vertex position.
			cmds.xform(specSphere, ws=True, t=vtxPos)

			# Attach to the vertex.
			objName = vtx.split('.')[0]
			cmds.select(anchGrp, objName, r=True)
			mel.eval('djRivet;')

	elif '.e' in selLs[0]:
		# Create rivet.
		rv = mel.eval('rivet;')

		# Create a sphere.
		specSphere = cmds.polySphere(n='%s_specSphere#' % (chName), r=radius, ch=False)[0]
		anchGrp = cmds.group(specSphere, n=specSphere + '_anchor')

		# Assign shader.
		cmds.select(specSphere, r=True)
		cmds.hyperShade(assign='specular_mat')

		# Move sphere to a vertex position.
		cmds.parent(specSphere, rv)
		cmds.xform(specSphere, t=[0, 0, 0], os=True)
		cmds.xform(specSphere, ro=[0, 0, 0], os=True)


### Snap to Closest Border Vertex ###
def snapToBrdrVtx():
	'''
	Snap selected vertices to the target geometry's closest border vertex.
	'''
	srcVtxLs = cmds.ls(sl=True, fl=True)
	trgGeo = srcVtxLs.pop(-1)

	# Get target geometry's border vertex list.
	# For calculation efficiency, just caculate with target geometry's border vertices.
	cmds.select(trgGeo, r=True)
	cmds.polySelectConstraint(m=3, t=1, w=1)
	trgVtxLs = cmds.ls(sl=True, fl=True)
	cmds.polySelectConstraint(dis=True)

	# Seek closest vertex on target geometry.
	for srcVtx in srcVtxLs:
		# Initialize variables.
		dist = 1000000
		closestTrgVtx = ''
		finalTrgVtxVec = 0

		# Get source vertex's vector in world space.
		srcVtxPos = cmds.pointPosition(srcVtx, world=True)
		srcVtxVec = OpenMaya.MVector(*srcVtxPos)

		for trgVtx in trgVtxLs:
			# Get target vertex's vector in world space.
			trgVtxPos = cmds.pointPosition(trgVtx, world=True)
			trgVtxVec = OpenMaya.MVector(*trgVtxPos)

			# Calculate distance between source and target vertex.
			delta = trgVtxVec - srcVtxVec

			if delta.length() < dist:
				dist = delta.length()
				closestTrgVtx = trgVtx
				finalTrgVtxVec = trgVtxVec
			else:
				continue

		# Move source vertex to closest target vertex.
		cmds.xform(srcVtx, ws=True, t=[finalTrgVtxVec.x, finalTrgVtxVec.y, finalTrgVtxVec.z])
	cmds.select(srcVtxLs, r=True)


def crvToPolyStrp():
	'''
	Convert selected curves to polygon stripe plane.
	'''

	selCrvs = cmds.ls(sl=True)

	strkDens = 0.15
	strkWidth = 0.5
	strkLs = []

	for crv in selCrvs:
		cmds.select(crv, r=True)

		cmds.AttachBrushToCurves()
		strk = cmds.ls(sl=True)[0]
		strkLs.append(strk)
		strkShp = cmds.listRelatives(strk, s=True)[0]
		brush = cmds.listConnections(strkShp, s=True, type='brush')[0]

		cmds.setAttr('%s.sampleDensity' % strkShp, strkDens)
		cmds.setAttr('%s.smoothing' % strkShp, 1)
		cmds.setAttr('%s.brushWidth' % brush, strkWidth)
		cmds.setAttr('%s.flatness1' % brush, 1)

	# Convert stroke paint effect to polygon.
	cmds.select(strkLs, r=True)
	mel.eval('doPaintEffectsToPoly( 1,0,1,1,100000);')
	cmds.hyperShade(assign='lambert1')


### Connect Facial Control to ROM Facial Locator with SDK ###
def cntFacCtrlLocUI():
	'''
	UI for connect facial control to range of motion animated locators.
	'''

	winName = 'cntFacCtrlLocWin'

	if cmds.window(winName, exists=True):
		cmds.deleteUI(winName)

	cmds.window(winName, title='Connect Facial Control to Facial Locators', maximizeButton=False, minimizeButton=False)

	cmds.columnLayout('mainColLo', adj=True)

	cmds.rowColumnLayout('drvrRowColLo', p='mainColLo', numberOfColumns=5, columnWidth=[(3, 80), (4, 100), (5, 100)],
	                     columnSpacing=[(4, 10)])
	cmds.textField('drvrTxtFld', p='drvrRowColLo', text='Driver Object')
	cmds.popupMenu()
	cmds.menuItem(label='Load Selected', c=partial(tak_lib.loadSel, 'textField', 'drvrTxtFld'))
	cmds.text(p='drvrRowColLo', label='.')
	cmds.textField('drvrAttrTxtFld', p='drvrRowColLo', text='translateY')
	cmds.textField('drvrMinValTxtFld', p='drvrRowColLo', text='-1')
	cmds.textField('drvrMaxValTxtFld', p='drvrRowColLo', text='1')

	cmds.rowColumnLayout('drvnRowColLo', p='mainColLo', numberOfColumns=3, columnWidth=[(1, 193), (2, 100), (3, 100)],
	                     columnSpacing=[(2, 10)])
	cmds.textScrollList('drvnTxtSclLs', p='drvnRowColLo', append='Driven Objects', h=100)
	cmds.popupMenu()
	cmds.menuItem(label='Load Selected', c=partial(tak_lib.populateTxtScrList, 'textScrollList', 'drvnTxtSclLs'))
	cmds.textField('drvnMinPoseTxtFld', p='drvnRowColLo', text='Min Pose Frame', w=100)
	cmds.textField('drvnMaxPoseTxtFld', p='drvnRowColLo', text='Max Pose Frame', w=100)

	cmds.button(p='mainColLo', label='Apply', c=cntFacCtrlLoc, h=50)

	cmds.window(winName, e=True, w=200, h=100)
	cmds.showWindow(winName)


def cntFacCtrlLoc(*args):
	'''
	Connect facial control to locators with set driven key.
	'''

	drvr = cmds.textField('drvrTxtFld', q=True, text=True)
	drvrAttr = cmds.textField('drvrAttrTxtFld', q=True, text=True)
	drvrAttrMinVal = cmds.textField('drvrMinValTxtFld', q=True, text=True)
	drvrAttrMaxVal = cmds.textField('drvrMaxValTxtFld', q=True, text=True)
	drvrAttrValLs = [drvrAttrMinVal, drvrAttrMaxVal]

	drvnObjs = cmds.textScrollList('drvnTxtSclLs', q=True, allItems=True)
	minPoseFrame = cmds.textField('drvnMinPoseTxtFld', q=True, text=True)
	maxPoseFrame = cmds.textField('drvnMaxPoseTxtFld', q=True, text=True)
	poseFrameLs = [minPoseFrame, maxPoseFrame]

	curFrame = cmds.currentTime(q=True)

	for i in xrange(len(poseFrameLs)):
		# Go to the pose frame
		cmds.currentTime(poseFrameLs[i])
		for drvn in drvnObjs:
			# Set multiply value 0.5 or 1 depend on driven's direction.
			if 'ct_' in drvn:
				mulVal = 0.5
			else:
				mulVal = 1

			autoGrp = cmds.listRelatives(drvn, p=True)[0]
			attrList = cmds.listAttr(drvn, keyable=True)
			for attr in attrList:
				# If attributes is scale or visibility skip this attribute.
				if 'scale' in attr or 'visibility' in attr:
					continue
				else:
					# Set set driven key frame default value first.
					cmds.setDrivenKeyframe('%s.%s' % (autoGrp, attr), cd='%s.%s' % (drvr, drvrAttr), dv=0, v=0)

					drvnAttrVal = cmds.getAttr('%s.%s' % (drvn, attr))
					cmds.setDrivenKeyframe('%s.%s' % (autoGrp, attr), cd='%s.%s' % (drvr, drvrAttr),
					                       dv=float(drvrAttrValLs[i]), v=drvnAttrVal * mulVal)
	cmds.currentTime(curFrame)


def delKeySetDflt():
	'''
	Delete keys and set default value for selected controls.
	'''

	# Delete keys.
	mel.eval(
		'doClearKeyArgList 3 { "1","0:10","keys","none","0","1","0","0","animationList","0","noOptions","0","0" };')

	# Set default value.
	selCtrl = cmds.ls(sl=True)
	for ctrl in selCtrl:
		attrLs = cmds.listAttr(ctrl, keyable=True)
		if attrLs:
			for attr in attrLs:
				if 'translate' in attr or 'rotate' in attr:
					try:
						cmds.setAttr('%s.%s' % (ctrl, attr), 0)
					except:
						pass


def delKey():
	'''
	Delete keys for selected controls.
	'''

	# Delete keys.
	mel.eval(
		'doClearKeyArgList 3 { "1","0:10","keys","none","0","1","0","0","animationList","0","noOptions","0","0" };')


def cnntAttrs():
	'''
	Connect selected attributes in channelbox from first selected object to second selected object.
	'''

	selLs = cmds.ls(sl=True)
	srcObj = selLs[0]
	trgObj = selLs[1]

	selAttrs = tak_lib.getSelAttrsNiceName()

	if selAttrs:
		for attr in selAttrs:
			cmds.connectAttr('%s.%s' % (srcObj, attr), '%s.%s' % (trgObj, attr), f=True)
	else:
		cmds.warning('Select attribute in channelbox.')


# def cnntAttrUI():
# 	winName = 'connectAttrWin'

# 	if cmds.window(winName, exists = True):
# 		cmds.deleteUI(winName)

# 	cmds.window(winName, title = 'Connect Attributes')

# 	cmds.columnLayout(adj = True)

# 	cmds.checkBoxGrp('attrChkBoxGrp', numberOfCheckBoxes = 3, label = 'Attributes: ', labelArray3 = ['Translate', 'Rotate', 'Scale'], columnWidth = [(1, 60), (2, 90), (3, 80)], v1 = True, v2 = True, v3 = True)
# 	cmds.checkBoxGrp('attrChkBoxGrp1', numberOfCheckBoxes = 3, label = '', labelArray3 = ['Mesh', '', 'Custom'], columnWidth = [(1, 60), (2, 90), (3, 80)], v1 = False, v2 = False, v3 = False)

# 	cmds.textFieldGrp('customAttrTxtFldGrp', label = 'Custom Attributes: ')
# 	cmds.popupMenu()
# 	cmds.menuItem(label = 'Load Selected Attributes in Channelbox', c = loadAttrsFromSelChAttrs)

# 	cmds.button(label = 'Apply', h = 50, c = cnntAttr)

# 	cmds.window(winName, e = True, w = 100, h = 50)
# 	cmds.showWindow(winName)


# def cnntAttr(*args):
# 	'''
# 	Connect attributes of first selected object to second selected object.
# 	'''

# 	# Get options.
# 	tOpt = cmds.checkBoxGrp('attrChkBoxGrp', q = True, v1 = True)
# 	rOpt = cmds.checkBoxGrp('attrChkBoxGrp', q = True, v2 = True)
# 	sOpt = cmds.checkBoxGrp('attrChkBoxGrp', q = True, v3 = True)
# 	mOpt = cmds.checkBoxGrp('attrChkBoxGrp1', q = True, v1 = True)
# 	customOpt = cmds.checkBoxGrp('attrChkBoxGrp1', q = True, v3 = True)

# 	# Connect first selected object's attribute to second selected object's attribute.
# 	selList = cmds.ls(sl = True)
# 	driverObj = selList[0]
# 	drivenObj = selList[1]
# 	if tOpt:
# 		cmds.connectAttr('%s.translate' %driverObj, '%s.translate' %drivenObj, f = True)
# 	if rOpt:
# 		cmds.connectAttr('%s.rotate' %driverObj, '%s.rotate' %drivenObj, f = True)
# 	if sOpt:
# 		cmds.connectAttr('%s.scale' %driverObj, '%s.scale' %drivenObj, f = True)
# 	if mOpt:
# 		drvrShp = cmds.listRelatives(driverObj, s = True)[0]
# 		drvnShp = cmds.listRelatives(drivenObj, s = True)[0]
# 		cmds.connectAttr('%s.outMesh' %drvrShp, '%s.inMesh' %drvnShp, f = True)


# def loadAttrsFromSelChAttrs(*args):
# 	'''
# 	Fill text field with attributes from selected in channelbox.
# 	'''

# 	selAttrs = tak_lib.getSelAttrsNiceName()

# 	cmds.textFieldGrp('customAttrTxtFldGrp', e = True, text = str(selAttrs))





def matchPivot():
	'''
	Match rotate and scale pivot.
	'''

	selLs = cmds.ls(sl=True)
	driver = selLs[0]
	drivens = selLs[1:]

	for driven in drivens:
		# Match rotate pivot
		drvrRpPos = cmds.xform(driver, q=True, rp=True, ws=True)
		cmds.xform(driven, rp=drvrRpPos, ws=True)

		# Match scale pivot
		drvrRpPos = cmds.xform(driver, q=True, sp=True, ws=True)
		cmds.xform(driven, sp=drvrRpPos, ws=True)


def dupUniqName():
	sels = cmds.ls(sl=True)

	for sel in sels:
		# Duplicate with unique name.
		dupObj = cmds.duplicate(sel, rr=True, renameChildren=True)

		# Set parent to the world for duplicated object.
		try:
			cmds.parent(dupObj, w=True)
		except:
			pass


def dupNoDefUniqName():
	'''
	Duplicate selected objects with original state and assign unique name.
	'''

	sels = cmds.ls(sl=True)
	dupObjs = []

	for sel in sels:
		# Set envelope value to 0 for assigned deformers.
		tak_lib.setAllDefEnvlope(geo=sel, envVal=0)

		# Duplicate with unique name.
		dupObj = cmds.duplicate(sel, rr=True, renameChildren=True)

		# Set parent to the world for duplicated object.
		try:
			cmds.parent(dupObj, w=True)
		except:
			pass

		# Back deformers envelope to 1 for sel.
		tak_lib.setAllDefEnvlope(geo=sel, envVal=1)

		dupObjs.append(dupObj)

	return dupObjs


def sepGeoWithEdge():
	'''
	Separate geometry with slected edge.
	'''

	sel = cmds.ls(sl=True)[0]

	searchObj = re.search(r'(.*)\.', sel)
	transformName = searchObj.group(1)

	cmds.SelectEdgeLoopSp()
	cmds.DetachComponent()
	cmds.select(transformName, r=True)
	cmds.SeparatePolygon()
	cmds.delete(ch=True)
	cmds.polyOptions(r=True, db=True)
	cmds.select(cl=True)


def sepGeoWithFace():
	'''
	Separete selected faces.
	'''
	selFaces = cmds.ls(sl=True)
	geo = selFaces[0].rsplit('.')[0]
	cmds.polyChipOff(selFaces, dup=False)
	cmds.polySeparate(geo)
	cmds.delete(ch=1)
	cmds.polyOptions(r=True, db=True)
	cmds.select(cl=True)


def cbMrgGeo():
	'''
	Combine meshes and merge vertex.
	'''
	cmds.polyUnite(mergeUVSets=1)
	cmds.polyMergeVertex(d=0.0001, am=1)
	cmds.delete(ch=1)


def combineAndRenameWithParentName():
	selGeos = cmds.ls(sl=True)

	parentNameLs = []

	for selGeo in selGeos:
		parentNameLs.append(cmds.listRelatives(selGeo, p=True)[0])
	parentNameLs = list(set(parentNameLs))

	cmds.polyUnite(mergeUVSets=1)
	cmds.delete(ch=True)

	cmds.rename(parentNameLs[0])


def combineAndAssignRandomMat():
	'''
	Combine geometries and assign random lambert material.
	Useful when grouping bunch of geometries like a hair.
	'''

	cmds.polyUnite(mergeUVSets=1)
	cmds.delete(ch=True)

	ranColLam()


def renameWithSrcUi():
	'''
	Rename with source ui.
	'''

	if cmds.window('renameWithSrcWin', exists=True):
		cmds.deleteUI('renameWithSrcWin')

	cmds.window('renameWithSrcWin', title='Rename with Source', maximizeButton=False, minimizeButton=False)

	cmds.columnLayout('mainColLo', adj=True, rs=2.5)
	cmds.textFieldGrp('prefixTxtFldGrp', label='Prefix: ', text='lod01_', columnWidth=[(1, 50), (2, 150)])
	cmds.textFieldGrp('suffixTxtFldGrp', label='Suffix: ', text='', columnWidth=[(1, 50), (2, 150)])
	cmds.button(label='Apply', c=renameWithSrc)

	cmds.window('renameWithSrcWin', e=True, w=50, h=50)
	cmds.showWindow('renameWithSrcWin')


def renameWithSrc(*args):
	'''
	Rename second selected object with first selected object's name.
	'''

	sel = cmds.ls(sl=True)
	srcObj = sel[0]
	trgObj = sel[1]
	prefix = 'lod01_'
	suffix = ''

	cmds.rename(trgObj, prefix + srcObj + suffix)


def setSmoothLevelUI():
	if cmds.window('setSmoothLevelWin', exists=True):
		cmds.deleteUI('setSmoothLevelWin')

	cmds.window('setSmoothLevelWin', title='Set Smooth Level', maximizeButton=False, minimizeButton=False)

	cmds.columnLayout('mainColLo', adj=True, rs=2.5)
	cmds.optionMenu('smLevelOpt', label='Smooth Level: ')
	cmds.menuItem(label='0')
	cmds.menuItem(label='1')
	cmds.menuItem(label='2')
	cmds.button(label='Apply', c=setSmoothLevel)

	cmds.window('setSmoothLevelWin', e=True, w=50, h=50)
	cmds.showWindow('setSmoothLevelWin')


def setSmoothLevel(*args):
	smLevelOpt = int(cmds.optionMenu('smLevelOpt', q=True, v=True))

	selGeoLs = cmds.ls(sl=True)

	if smLevelOpt == 0:
		for geo in selGeoLs:
			cmds.select(geo, r=True)
			mel.eval('setDisplaySmoothness 1;')
			cmds.setAttr(geo + '.smoothLevel', 0)
	else:
		for geo in selGeoLs:
			cmds.select(geo, r=True)
			mel.eval('setDisplaySmoothness 3;')
			cmds.setAttr(geo + '.useGlobalSmoothDrawType', 1)
			cmds.setAttr(geo + '.smoothLevel', smLevelOpt)


def delSupportEdgesUI():
	if cmds.window('delSupporEdgeWin', exists=True):
		cmds.deleteUI('delSupporEdgeWin')

	cmds.window('delSupporEdgeWin', title='Remove Supporting Edges', maximizeButton=False, minimizeButton=False)

	cmds.columnLayout('mainColLo', adj=True, rs=2.5)
	cmds.rowColumnLayout('thresholdRowColLo', numberOfColumns=2)
	cmds.text(label='Edge Length: ', align='left')
	cmds.floatSliderGrp('thresholdFloatSldrGrp', field=True, step=0.00001, min=0, max=5, cc=selEdgeByLength)
	cmds.setParent('..')
	cmds.button(label='Collapse Convert to Edge Ring and Collapse', c="mel.eval('polyConvertToRingAndCollapse;')")
	cmds.button(label='Collapse Selected Edge', c='cmds.polyCollapseEdge()')

	cmds.window('delSupporEdgeWin', e=True, w=50, h=50)
	cmds.showWindow('delSupporEdgeWin')


def selEdgeByLength(*args):
	'''
	Select edges with given length value.
	'''

	length = cmds.floatSliderGrp('thresholdFloatSldrGrp', q=True, v=True)

	cmds.selectType(pe=True)
	cmds.polySelectConstraint(m=3, t=0x8000, l=True, lb=(0, length))
	cmds.polySelectConstraint(dis=True)


def addInfCopySkin():
	'''
	Add source skin geometry's influences to the target geoemtry if not exists in the target skin geometry.
	And copy skin weights.
	'''

	selLs = cmds.ls(sl=True)
	srcSkinGeo = selLs[0]
	trgs = selLs[1:]

	cmds.select(srcSkinGeo, r=True)
	srcInfs = selInflu()

	if '.' in str(trgs):
		trgSkinGeo = trgs[0].split('.')[0]

		skinClst = mel.eval('findRelatedSkinCluster("%s");' % trgSkinGeo)

		if not skinClst:
			cmds.skinCluster(srcInfs, trgSkinGeo, mi=4, dr=4, tsb=True, omi=False, nw=1)
			skinClst = mel.eval('findRelatedSkinCluster("%s");' % trgSkinGeo)

		cmds.select(trgSkinGeo, r=True)
		trgInfs = selInflu()

		for inf in srcInfs:
			if inf in trgInfs:
				continue
			else:
				cmds.skinCluster(skinClst, e=True, dr=4, lw=True, wt=0, ai=inf)
				cmds.setAttr('%s.liw' % inf, False)

		cmds.select(srcSkinGeo, trgs, r=True)
		cmds.CopySkinWeights()
	else:
		for trgSkinGeo in trgs:
			skinClst = mel.eval('findRelatedSkinCluster("%s");' % trgSkinGeo)

			if not skinClst:
				cmds.skinCluster(srcInfs, trgSkinGeo, mi=4, dr=4, tsb=True, omi=False, nw=1)
				skinClst = mel.eval('findRelatedSkinCluster("%s");' % trgSkinGeo)

			cmds.select(trgSkinGeo, r=True)
			trgInfs = selInflu()

			for inf in srcInfs:
				if inf in trgInfs:
					continue
				else:
					cmds.skinCluster(skinClst, e=True, dr=4, lw=True, wt=0, ai=inf)
					cmds.setAttr('%s.liw' % inf, False)

			cmds.select(srcSkinGeo, trgSkinGeo, r=True)
			cmds.CopySkinWeights()


def smoothSkinBind():
	selLs = cmds.ls(sl=True)
	jntLs = cmds.ls(selLs, type='joint')
	geoShpLs = cmds.ls(selLs, dag=True, ni=True, type=['mesh', 'nurbsCurve', 'nurbsSurface'])

	for geoShp in geoShpLs:
		skinClst = mel.eval('findRelatedSkinCluster("%s");' % geoShp)
		if skinClst:
			cmds.select(geoShp, r=True)
			cmds.DetachSkin()
		geoTrsf = cmds.listRelatives(geoShp, p=True)[0]
		if cmds.nodeType(geoTrsf) != "transform":
			continue
		cmds.skinCluster(jntLs, geoTrsf, mi=1, dr=2, tsb=True, omi=False, nw=1)


def dupRenameUI():
	"""
	Duplicate selected objects with renaming user interface.
	"""

	if cmds.window('dupRenameWin', exists=True):
		cmds.deleteUI('dupRenameWin')
	cmds.window('dupRenameWin', title='Duplicate Rename', maximizeButton=False, minimizeButton=False)

	cmds.columnLayout('mainColLay', adj=True, columnAlign='left')

	cmds.textFieldGrp('prefixTxtFldGrp', label='Prefix: ', columnAlign=[(1, 'left')], columnWidth=[(1, 30), (2, 50)],
	                  text='lod02_')
	cmds.textFieldGrp('suffixTxtFldGrp', label='Suffix: ', columnAlign=[(1, 'left')], columnWidth=[(1, 30), (2, 50)],
	                  text='')

	cmds.button(label='Apply', h=25, c=addSubPrefix)

	cmds.separator(h=10, style='in')

	cmds.textFieldGrp('searchTxtFldGrp', label='Search: ', columnAlign=[(1, 'left')], columnWidth=[(1, 40), (2, 50)],
	                  text='lod02_')
	cmds.textFieldGrp('rplcTxtFldGrp', label='Replace: ', columnAlign=[(1, 'left')], columnWidth=[(1, 40), (2, 50)],
	                  text='lod01_')

	cmds.button(label='Apply', h=25, c=srchRplce)

	cmds.window('dupRenameWin', e=True, w=100, h=50)
	cmds.showWindow('dupRenameWin')


def addSubPrefix(*args):
	'''
	Duplicate selected object and rename with prefix, suffix.
	'''

	prefix = cmds.textFieldGrp('prefixTxtFldGrp', q=True, text=True)
	suffix = cmds.textFieldGrp('suffixTxtFldGrp', q=True, text=True)

	selObjLs = cmds.ls(sl=True)

	for obj in selObjLs:
		dupObj = cmds.duplicate(obj, n=prefix + obj + suffix, returnRootsOnly=True)

		try:
			cmds.parent(dupObj, world=True)
		except:
			pass

		dupObjChldLs = cmds.listRelatives(dupObj, type='transform', ad=True, path=True)
		if dupObjChldLs:
			for chldObj in dupObjChldLs:
				chldObjBaseName = chldObj.split('|')[-1]
				renamedObj = cmds.rename(chldObj, prefix + chldObjBaseName + suffix)


def srchRplce(*args):
	'''
	Duplicate selected object and rename with search, replace string.
	'''

	srchStr = cmds.textFieldGrp('searchTxtFldGrp', q=True, text=True)
	rplcStr = cmds.textFieldGrp('rplcTxtFldGrp', q=True, text=True)

	selObjLs = cmds.ls(sl=True)

	for obj in selObjLs:
		subDupName = re.sub(srchStr, rplcStr, obj)
		dupObj = cmds.duplicate(obj, returnRootsOnly=True, n=subDupName)

		try:
			cmds.parent(dupObj, world=True)
		except:
			pass

		dupObjChldLs = cmds.listRelatives(dupObj, type='transform', ad=True, path=True)
		if dupObjChldLs:
			for chldObj in dupObjChldLs:
				chldObjBaseName = chldObj.split('|')[-1]
				subName = re.sub(srchStr, rplcStr, chldObjBaseName)
				cmds.rename(chldObj, subName)


def copyTexRenameUI():
	if cmds.window('copyTexWin', exists=True):
		cmds.deleteUI('copyTexWin')

	cmds.window('copyTexWin', title='Copy Textrue And Reset File Path for Selected Objects', mnb=False, mxb=False)

	cmds.columnLayout('mainColLo', adj=True, columnAlign='left', rowSpacing=3)
	cmds.textFieldButtonGrp('trgFldrTxtFldBtnGrp', label='Target Folder Path: ', columnAlign=[(1, 'left')],
	                        columnWidth=[(1, 100)], buttonLabel='...',
	                        bc=partial(tak_lib.loadPath, 'trgFldrTxtFldBtnGrp'))
	cmds.rowColumnLayout('percentRowColLo', numberOfColumns=2)
	cmds.setParent('..')

	cmds.textFieldGrp('suffixTxtFldGrp', label='Suffix: ', text='_low', columnAlign=[(1, 'left')],
	                  columnWidth=[(1, 40), (2, 50)])

	cmds.button(label='Apply', c=copyTexRename, h=25)

	cmds.window('copyTexWin', e=True, w=50, h=10)
	cmds.showWindow('copyTexWin')


def copyTexRename(*args):
	"""
	Copy selected object's texture to target directory and modify file node path.
	"""

	suffix = cmds.textFieldGrp('suffixTxtFldGrp', q=True, text=True)
	trgDir = cmds.textFieldButtonGrp('trgFldrTxtFldBtnGrp', q=True, text=True)

	selObjLs = cmds.ls(sl=True)

	if not selObjLs:
		cmds.confirmDialog(title='Warning', message='Nothing selected.\nSelect geometry(s).')
		return

	finalFileNodeLs = []
	for selObj in selObjLs:
		selObjMat = tak_lib.getMatFromSel(selObj)
		fileNodes = cmds.ls(cmds.listHistory(selObjMat), type='file')
		if fileNodes:
			for node in fileNodes:
				finalFileNodeLs.append(node)

	for fileNode in list(set(finalFileNodeLs)):
		srcFilePath = cmds.getAttr(fileNode + '.fileTextureName')
		fileName = os.path.basename(srcFilePath)
		newFileName = fileName.rsplit('.', 1)[0] + suffix + '.' + fileName.rsplit('.', 1)[-1]
		trgFilePath = trgDir + '/' + newFileName

		shutil.copy(srcFilePath, trgFilePath)

		cmds.setAttr(fileNode + '.fileTextureName', trgFilePath, type='string')

	cmds.deleteUI('copyTexWin')
	return subprocess.call(
		['C:/Python27/python.exe', 'D:/Tak/Program_Presets/tak_scripts/python_scripts/cliResizeImage.py', trgDir,
		 '0.25'])


def cntShpGeo():
	"""
	Duplicate selected geometry(s) and connect source outMesh to duplicated geometry inMesh.
	"""

	selLs = cmds.ls(sl=True)

	for sel in selLs:
		cntGeo = cmds.duplicate(n=sel + '_cntGeo')
		cmds.parent(cntGeo, world=True)
		cmds.select(cntGeo, r=True)
		tak_cleanUpModel.allInOne()

		srcShp = cmds.ls(cmds.listRelatives(sel), ni=True)[0]
		trgShp = cmds.listRelatives(cntGeo, ni=True)[0]
		cmds.connectAttr('%s.outMesh' % srcShp, '%s.inMesh' % trgShp, f=True)


def cutGeoWithJnts():
	'''
	Cut selected geometry with selected joints.
	Using 'js_cutPlane.mel' script.
	Select first joints and geometry last.
	'''

	mel.eval('source "D:/Tak/Program_Presets/tak_maya_preset/prefs/scripts/mel/js_cutPlane";')

	selLs = cmds.ls(sl=True)
	bndJntLs = selLs[0:-1]
	geo = selLs[-1]

	cutPlaneLs = []
	for bndJnt in bndJntLs:
		cmds.select(geo, r=True)
		cutPlane = mel.eval('js_cutPlane_create;')
		cutPlaneLs.append(cutPlane)
		cmds.delete(cmds.parentConstraint(bndJnt, cutPlane, mo=False))
		cmds.select(cl=True)

	cmds.select(cutPlaneLs, r=True)


# cmds.select(geo, r = True)
# mel.eval('js_cutPlane_cut 1;')





def simplePropAutoRigging():
	'''
	Auto rigging function for simple props like sword, gun... etc.
	'''

	jntLs = cmds.ls(sl=True)

	srchStr = '_jnt'
	rplcStr = '_ctrl'

	ctrlZeroGrpLs = []

	for jnt in jntLs:
		crv = tak_createCtrl.createCurve('circle')
		ctrlName = re.sub(srchStr, rplcStr, jnt)
		cmds.rename(crv, ctrlName)

		ctrlZeroGrp = createCtrlGrp(ctrlName)

		cmds.delete(cmds.parentConstraint(jnt, ctrlZeroGrp, mo=False))

		cmds.parentConstraint(ctrlName, jnt, mo=True)

		lockAndHideAttr(ctrlName)

		ctrlZeroGrpLs.append(ctrlZeroGrp)

	glbCtrl = tak_createCtrl.createCurve('masterAnim')
	glbCtrlName = cmds.rename(glbCtrl, 'global_ctrl')
	doGroup(glbCtrlName, '_zero')

	doNotTouchGrp = cmds.group(jntLs, n='doNotTouch_grp')
	ctrlGrp = cmds.group(ctrlZeroGrpLs, n='ctrl_grp')
	cmds.parent(doNotTouchGrp, ctrlGrp, glbCtrlName)

	rigGrp = cmds.group(glbCtrlName + '_zero', n='rig_grp')

	cmds.parent(rigGrp, 'root')


def createCtrlGrp(ctrl):
	doGroup(ctrl, '_zero')
	doGroup(ctrl, '_auto')
	doGroup(ctrl, '_extra')

	return ctrl + '_zero'


def lockAndHideAttr(ctrl):
	lockHideAttrLs = ['scaleX', 'scaleY', 'scaleZ', 'visibility']

	for attr in lockHideAttrLs:
		cmds.setAttr('%s.%s' % (ctrl, attr), keyable=False, lock=True)


def copyUvMat():
	'''
	Copy all uv sets and material from source to target.
	'''

	selLs = cmds.ls(sl=True)

	src = selLs[0]
	trg = selLs[1]

	cmds.transferAttributes(src, trg, transferUVs=2, sampleSpace=1)
	cmds.select(src, trg, r=True)
	copyMat()
	cmds.delete(trg, ch=True)


def reverseSmoothUI():
	if cmds.window('reverseSmoothWin', exists=True):
		cmds.deleteUI('reverseSmoothWin')
	cmds.window('reverseSmoothWin', title='Reverse Smooth', maximizeButton=False, minimizeButton=False)

	cmds.columnLayout('mainColLay', adj=True, columnAlign='left')

	cmds.button(label='1. Vertex Id Method', h=50, c=partial(reverseSmooth, 'vtxId'))
	cmds.button(label='2. Skipped Edge Method', h=50, c=partial(reverseSmooth, 'skippedEdge'))

	cmds.window('reverseSmoothWin', e=True, w=100, h=50)
	cmds.showWindow('reverseSmoothWin')


def reverseSmooth(method, *args):
	'''
	Get rid of the edges that added by smooth subdivision.
	'''

	selMeshLs = cmds.ls(sl=True)

	for selMesh in selMeshLs:
		numOfVtx = cmds.polyEvaluate(selMesh, v=True)

		if method == 'skippedEdge':
			cmds.select('%s.vtx[%d]' % (selMesh, numOfVtx), r=True)

			# Convert selected a vertex to edges.
			mel.eval('PolySelectConvert 2;')

			mel.eval('SelectEdgeLoopSp;')
			mel.eval('polySelectEdgesEveryN "edgeRing" 2;')
			mel.eval('SelectEdgeLoopSp;')
			mel.eval('SelectEdgeLoopSp;')
			mel.eval('SelectEdgeLoopSp;')
			mel.eval('polySelectEdgesEveryN "edgeRing" 2;')
			cmds.polyDelEdge(cv=True)

		elif method == 'vtxId':
			numOfCurFace = cmds.polyEvaluate(selMesh, f=True)
			numOfOriFace = numOfCurFace / 4  # 1 original face subdivided into 4

			# Select inner edges.
			cmds.selectType(pe=True)
			cmds.polySelectConstraint(m=3, t=0x8000, w=2)
			cmds.polySelectConstraint(dis=True)
			numOfCurInEdge = len(cmds.ls(sl=True, fl=True))

			dividedOriInEdge = numOfCurInEdge - numOfCurFace  # Number of current face is equal to number of added edges on each original face.
			numOfOriInEdge = dividedOriInEdge / 2  # 1 original inner edge subdivied into 2

			numOfAddedVtxAtEachFace = 5
			numOfAddedVtx = numOfOriFace * numOfAddedVtxAtEachFace

			numOfAddedVtx = numOfAddedVtx - numOfOriInEdge  # Remove number of repeated vertex on original inner edge.

			numOfVtx = cmds.polyEvaluate(v=True)
			numOfOriVtx = numOfVtx - numOfAddedVtx
			cmds.select('%s.vtx[%d:]' % (selMesh, numOfOriVtx), r=True)  # Select all added vertex.

			cmds.InvertSelection()  # Select original vertex.
			mel.eval('PolySelectConvert 2;')  # Convert to edge.
			cmds.InvertSelection()  # Select added edges.
			cmds.polyDelEdge(cv=True)

	cmds.select(selMeshLs, r=True)


def reduceMesh():
	'''
	Reduce polygon resolution.
	'''

	selMeshLs = cmds.ls(sl=True)

	for selMesh in selMeshLs:
		numOfFace = cmds.polyEvaluate(selMesh, f=True)

		cmds.select('%s.f[%d]' % (selMesh, numOfFace), r=True)

		# Convert selected a face to edges.
		mel.eval('PolySelectConvert 2;')

		mel.eval('polySelectEdgesEveryN "edgeLoopOrBorder" 2;')

		mel.eval('polyConvertToRingAndCollapse;')

	cmds.select(selMeshLs, r=True)


def delCnst():
	selLs = cmds.ls(sl=True)

	for sel in selLs:
		cmds.delete(list(set(cmds.listConnections(sel, d=False, scn=True, type='constraint'))))


def prntLoc():
	'''
	Create a locator and parent selected object to the locator.
	'''

	selLs = cmds.ls(sl=True)

	for sel in selLs:
		loc = cmds.spaceLocator(n=sel + "_loc")

		cmds.delete(cmds.parentConstraint(sel, loc, mo=False))

		prnt = cmds.listRelatives(sel, p=True)
		cmds.parent(sel, loc)
		if prnt:
			cmds.parent(loc, prnt)


def clMeshBeforeReduce():
	'''
	Clean up mesh before reduce resolution.
	'''

	selGeo = cmds.ls(sl=True)
	for sel in selGeo:
		cmds.select(sel, r=True)
		cmds.polySelectConstraint(t=0x8000, m=3, w=1)
		cmds.polySelectConstraint(dis=True)
		cmds.polyMergeVertex(d=0.05)
		cmds.select(sel, r=True)
		mel.eval(
			'polyCleanupArgList 3 { "0","2","1","0","1","1","1","1","0","1e-005","1","3","0","1e-005","0","1","1" };')
		cmds.selectMode(object=True)
		cmds.delete(ch=True)


def alignObjToVtx(obj, vtx, normalAixs='y'):
	'''
	Description
		Align object to vertex noraml and position.

	Parameters
		obj: string, Object name to aligned.
		vtx: string, Target vertex name.
		normalAixs: string, Object's axis that align to the vertex normal.

	Returns
		None
	'''

	# Get yVector that vertex normal vector.
	pVtxNormals = cmds.polyNormalPerVertex(vtx, q=True, normalXYZ=True)
	vtxNormalVec = OpenMaya.MVector(sum(pVtxNormals[0::3]) / 4, sum(pVtxNormals[1::3]) / 4, sum(pVtxNormals[2::3]) / 4)
	vtxNormalVec.normalize()

	# Get zVector using cross product with world yVector and vertex normal vector.
	worldYVec = OpenMaya.MVector(0.0, 1.0, 0.0)
	matrixZVec = worldYVec ^ vtxNormalVec
	matrixZVec.normalize()

	# Get xVector using cross product with vertex normal vector and zVector.
	matrixXVec = vtxNormalVec ^ matrixZVec
	matrixXVec.normalize()

	# Get position for matrix position in world sapce.
	vtxWsPos = cmds.pointPosition(vtx, w=True)

	# Compose matrix depend on normalAxis option.
	matrixTable = [matrixXVec.x, matrixXVec.y, matrixXVec.z, 0,
	               vtxNormalVec.x, vtxNormalVec.y, vtxNormalVec.z, 0,
	               matrixZVec.x, matrixZVec.y, matrixZVec.z, 0,
	               vtxWsPos[0], vtxWsPos[1], vtxWsPos[2], 1]
	if normalAixs == 'x':  # Swap xVector and yVector.
		matrixTable = [vtxNormalVec.x, vtxNormalVec.y, vtxNormalVec.z, 0,
		               matrixXVec.x, matrixXVec.y, matrixXVec.z, 0,
		               matrixZVec.x, matrixZVec.y, matrixZVec.z, 0,
		               vtxWsPos[0], vtxWsPos[1], vtxWsPos[2], 1]
	elif normalAixs == 'z':  # Swap zVector and yVector.
		matrixTable = [matrixXVec.x, matrixXVec.y, matrixXVec.z, 0,
		               matrixZVec.x, matrixZVec.y, matrixZVec.z, 0,
		               vtxNormalVec.x, vtxNormalVec.y, vtxNormalVec.z, 0,
		               vtxWsPos[0], vtxWsPos[1], vtxWsPos[2], 1]

	# Set matrix to the object.
	cmds.xform(obj, m=matrixTable, ws=True)


def autoRenameChldWithGrp():
	'''
	Rename group's children with selected group.
	'''

	selGrps = cmds.ls(sl=True)

	for grp in selGrps:
		chlds = cmds.listRelatives(grp, c=True)
		baseName = grp.rsplit('_', 1)[0]
		for chld in chlds:
			cmds.rename(chld, baseName + '_#')


def copySkinByName(dst, prefix="", srchStr="", rplcStr="", copyMatOpt=False):
	"""
	Copy skined source geometry/group to destination geometry/group by matching name.
	
	Parameters:
		dst: string, Destination geometry or group.
		prefix: string, Prefix attached to source.
		srchStr: string, Search string on destination.
		rplcStr: string, Replace string for source.
		copyMatOpt: boolean, Copy material option.
	
	Returns:
		None

	Examples:
		tak_misc.copySkinByName(dst = "lod02_GRP", srchStr = "lod02_", rplcStr = "old_lod02_", copyMatOpt = False)
		tak_misc.copySkinByName(dst = "temp_lod02_hair_bottom", srchStr = "temp_", rplcStr = "")
		tak_misc.copySkinByName(dst = "lod03_GRP", prefix = "photoBook_001:") # Copy skin 'photoBook_001:lod03_GRP -> lod03_GRP'.
		tak_misc.copySkinByName(dst = "lod02_GRP", prefix = "old_", copyMatOpt = True) # Copy skin and material 'old_lod02_GRP -> lod02_GRP.'
	"""

	dstGeos = [x for x in cmds.listRelatives(dst, ad=True, type='shape') if not cmds.getAttr(x + '.intermediateObject')]

	nonMatchGeos = []

	for dstGeo in dstGeos:
		if srchStr or rplcStr:
			srcGeo = re.sub(srchStr, rplcStr, dstGeo)
		elif prefix:
			srcGeo = prefix + dstGeo

		print ">>> Source Geometry: " + srcGeo
		print ">>> Destination Geometry: " + dstGeo

		if cmds.objExists(srcGeo):
			cmds.select(srcGeo, dstGeo, r=True)
			try:
				addInfCopySkin()
			except:
				pass

			if copyMatOpt:
				copyMat()
		else:
			nonMatchGeos.append(dstGeo)

	if nonMatchGeos:
		cmds.select(nonMatchGeos, r=True)
		OpenMaya.MGlobal.displayWarning("Selected geometries didn't found matching source geometry.")
	else:
		cmds.select(cl=True)
		OpenMaya.MGlobal.displayInfo('All geometries copied skin successfully.')


def selBndJnt():
	"""
	Description
		Filter bind joints for selected childs.
	"""

	bndJnts = []

	sels = cmds.ls(sl=True)
	for sel in sels:
		if cmds.nodeType(sel) == "joint" and "_bnd" in sel:
			bndJnts.append(sel)
		chlds = cmds.listRelatives(sel, ad=True, type="joint")
		if chlds:
			chldBndJnts = [x for x in chlds if "_bnd" in x]
			if chldBndJnts:
				bndJnts.extend(chldBndJnts)

	cmds.select(bndJnts, r=True)


def selAffectedVertex(inf):
	"""
	Select affected vertices by given influence
	Args:
		inf: Influence name or pynode

	Returns:
		None
	"""
	if isinstance(inf, basestring):
		inf = pm.PyNode(inf)
	skinClusters = inf.worldMatrix.listConnections()

	pm.select(cl=True)

	selLs = OpenMaya.MSelectionList()
	skinNode = OpenMaya.MObject()
	infDagPath = OpenMaya.MDagPath()
	componentsSelLs = OpenMaya.MSelectionList()
	weights = OpenMaya.MDoubleArray()
	geoDagPath = OpenMaya.MDagPath()
	vertices = OpenMaya.MObject()

	for skinCluster in skinClusters:
		# Get skin cluster function
		selLs.add(skinCluster.name())
		selLs.getDependNode(0, skinNode)
		skinFn = OpenMayaAnim.MFnSkinCluster(skinNode)

		# Get geometry dag path
		geo = skinCluster.outputGeometry.listConnections()[0]
		selLs.add(inf.name())
		selLs.getDagPath(1, infDagPath)

		# Get affected points
		skinFn.getPointsAffectedByInfluence(infDagPath, componentsSelLs, weights)

		# Get vertices
		componentsSelLs.getDagPath(0, geoDagPath, vertices)

		OpenMaya.MGlobal.select(geoDagPath, vertices, OpenMaya.MGlobal.kAddToList)

		selLs.clear()
