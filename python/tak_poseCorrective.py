'''
Author: Sang-tak Lee
Contact: chst27@gmail.com

Description:
This script allow to correct the problematic pose shape.

Usage:
1. Copy this script and paste in your scripts folder.

2. In maya python tab, run following code.
import tak_poseCorrective
reload(tak_poseCorrective)
posCorObj = tak_poseCorrective.PoseCorrect()
posCorObj.UI()
'''

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
from functools import partial
import re


class PoseCorrect:

	deformerList = ['blendShape', 'cluster', 'ffd', 'wrap', 'nonLinear', 'sculpt', 'softMod', 'jiggle', 'wire']

	def __init__(self):
		self.winName = 'corPoseWin'
		if cmds.window(self.winName, exists = True):
			cmds.deleteUI(self.winName)

		# check if user no select or select a geometry not contain skin cluster
		try:
			selGeo = cmds.ls(sl = True)[0]
		except:
			cmds.confirmDialog(title = 'Confirm', message = 'Select a skin geometry that what you want to correct.')
			return

		skinClst = self.checkSkinClst()

		if not selGeo or not skinClst:
			cmds.confirmDialog(title = 'Confirm', message = 'Select a skin geometry that what you want to correct.')
			return
		else:
			self.skinGeo = selGeo
			# get blendshape node name for add corrective
			self.getBSNodeName()
			self.ui()


	def checkSkinClst(self):
		# get skin cluster
		sel = cmds.ls(sl = True)[0]
		cmds.select(sel, r = True)
		mel.eval('string $selList[] = `ls -sl`;')
		mel.eval('string $source = $selList[0];')	
		skinCluster = mel.eval('findRelatedSkinCluster($source);')
		return skinCluster


	def getBSNodeName(self):
		self.bsList = []
		allConnections = cmds.listHistory(self.skinGeo)
		for item in allConnections:
			if cmds.objectType(item) == 'blendShape':
				self.bsList.append(item)
		if self.bsList:
			self.bsName = self.bsList[0]
		else:
			self.bsName = '%s_CorrectiveBS' %self.skinGeo

		print self.bsList
	

	def ui(self):
		cmds.window(self.winName, title = 'Pose Corrective UI')
		
		cmds.rowColumnLayout('mainRowColLay', numberOfColumns = 2, h = 500, columnWidth = [(1,270), (2,150)])

		cmds.tabLayout('l_mainTabLay', tv = False)
		cmds.tabLayout('l_subTabLay', tv = False)
		cmds.columnLayout('l_mainColLay', adj = True)
		cmds.textFieldButtonGrp('jntTexButGrp', label = 'Driver Joint: ', text = 'Elbow_L', buttonLabel = '<<', columnWidth = [(1, 80), (2, 120), (3, 50)], bc = partial(self.loadSel, 'jntTexButGrp'))
		cmds.textFieldButtonGrp('prntJointTexBtnGrp', label = 'Parent Joint: ', text = 'Shoulder_L', buttonLabel = '<<', columnWidth = [(1, 80), (2, 120), (3, 50)], bc = partial(self.loadSel, 'prntJointTexBtnGrp'))
		cmds.textFieldButtonGrp('locJointTexBtnGrp', label = 'Child Joint: ', text = 'Wrist_L', buttonLabel = '<<', columnWidth = [(1, 80), (2, 120), (3, 50)], bc = partial(self.loadSel, 'locJointTexBtnGrp'))
		cmds.textFieldGrp('poseNameTexFld', label = 'Pose Name: ', text = 'lf_elbow_bicep', columnWidth = [(1, 80), (2, 120)])
		
		cmds.separator(h = 10, style = 'in')

		cmds.rowColumnLayout('sculptRowColLay', numberOfColumns = 2, columnWidth = [(1, 120), (2, 120)], columnAttach = [(2, 'left', 3)])
		cmds.button('sculptBut', label = 'Sculpt', c = self.sculptMode)
		cmds.button('cancelBut', label = 'Cancel', w = 120, c = self.cancel)
		cmds.setParent('l_mainColLay')
		
		cmds.separator(h = 10, style = 'in')
		
		cmds.rowColumnLayout('corRowColLay', numberOfColumns = 2, columnWidth = [(1, 185), (2, 50)], columnAttach = [(2, 'left', 3)])
		cmds.button('createCorBut', label = 'Create Corretive', c = self.createCorrective)
		cmds.checkBox('mirChkBox', label = 'Mirror', v = False, onc = "cmds.rowColumnLayout('symVtxTolRowColLay', e = True, vis = True)\ncmds.rowColumnLayout('rplcNameRowColLay', e = True, vis = True)", ofc = "cmds.rowColumnLayout('symVtxTolRowColLay', e = True, vis = False)\ncmds.rowColumnLayout('rplcNameRowColLay', e = True, vis = False)")
		cmds.setParent('l_mainColLay')

		cmds.rowColumnLayout('symVtxTolRowColLay', numberOfColumns = 2, columnWidth= [(1, 150), (2, 45)], columnAttach = [(1, 'left', 8), (2, 'left', 0)], vis = False)
		# cmds.text(label = '# Make sure pose in mirror.')
		# cmds.text(label = '')
		cmds.text(label = 'Symmetry Vertex Tolerance: ')
		cmds.floatField('symVtxTolTexFiel', minValue=0, maxValue=1, value=0.002)
		cmds.setParent('l_mainColLay')
		
		cmds.rowColumnLayout('rplcNameRowColLay', numberOfColumns = 2, columnWidth = [], columnAttach = [], vis = False)
		cmds.textFieldGrp('jntSrchTexFld', label = 'Joint Search for: ', columnWidth = [(1, 90), (2, 25)], text = '_L')
		cmds.textFieldGrp('jntRplcTexFld', label = 'Joint Replace with: ', columnWidth = [(1, 100), (2, 25)], text = '_R')
		cmds.textFieldGrp('poseSrchTexFld', label = 'Pose Search for: ', columnWidth = [(1, 90), (2, 25)], text = 'lf_')
		cmds.textFieldGrp('poseRplcTexFld', label = 'Pose Replace with: ', columnWidth = [(1, 100), (2, 25)], text = 'rt_')
		
		cmds.setParent('mainRowColLay')

		cmds.tabLayout('r_mainTabLay', tv = False)
		cmds.tabLayout('r_subTabLay', tv = False)
		cmds.columnLayout('r_mainColLay', adj = True)
		cmds.text(label = 'Pose Corrective List', font = 'smallBoldLabelFont', rs = True)
		cmds.textScrollList('r_poseTexScrList', h = 240, sc = self.texScrSel, allowMultiSelection = True)
		cmds.popupMenu()
		cmds.menuItem(label = 'Refresh', c = self.populatePoseList)
		cmds.menuItem(label = 'Edit', c = self.edit)
		cmds.menuItem(label = 'Remove', c = self.removePose)

		
		cmds.window(self.winName, e = True, w = 300, h = 150)
		cmds.showWindow(self.winName)	
		
		# populate pose list
		self.populatePoseList()


	def sculptMode(self, *args):
		# get data
		self.poseName = cmds.textFieldGrp('poseNameTexFld', q = True, text = True) + '_corShp'
		
		# duplicate skined geometry
		self.sculptGeo = cmds.duplicate(self.skinGeo, n = self.poseName + '_sculpt')[0]
	        # delete intermediate shape	
		shapList = cmds.ls(self.sculptGeo, dag = True, s = True)
		for shap in shapList:
			if cmds.getAttr('%s.intermediateObject' %(shap)): 
				cmds.delete(shap)        
	        # assign sculpt shader
		# if not cmds.objExists('poseCorrective_mat'):
		# 	shaderName = cmds.shadingNode('lambert', n = 'poseCorrective_mat', asShader = True)
		# 	cmds.setAttr("%s.color" %shaderName, 0.686, 0.316, 0.121)
		# else:
		# 	shaderName = 'poseCorrective_mat'
		# cmds.select(self.sculptGeo, r = True)
		# cmds.hyperShade(assign = shaderName)
		# hide skin geometry
		cmds.setAttr('%s.visibility' %self.skinGeo, False)
		'''# isolate selected object
		curPanel = cmds.paneLayout('viewPanes', q = True, pane1= True)
		cmds.isolateSelect(curPanel, state = True)
		cmds.isolateSelect(curPanel, addSelected = True)'''
		'''# heads up display
		cmds.headsUpDisplay('sculptModeDisplay', section = 2, block = 0, blockSize='medium', ba = 'center', label = self.poseName + '_Sculpt Mode', labelFontSize='large')'''

	
	def createCorrective(self, mode, *args):
		'''# remove heads up display
		cmds.headsUpDisplay('sculptModeDisplay', remove = True)'''
		'''# off the isolate
		curPanel = cmds.paneLayout('viewPanes', q = True, pane1= True)
		cmds.isolateSelect(curPanel, state = False)'''
		# show skin geometry
		cmds.setAttr('%s.visibility' %self.skinGeo, True)
		
		self.vtxDeltaDic = {}
		sculptVtxFinVecDic = {}
		sculptVtxPointDic = {}
		inverseVtxPosDic = {}
		
		# get skin cluster
		cmds.select(self.skinGeo, r = True)
		mel.eval('string $selList[] = `ls -sl`;')
		mel.eval('string $source = $selList[0];')	
		self.skinCluster = mel.eval('findRelatedSkinCluster($source);')
		
		# get number of vertex
		vtxNum = cmds.polyEvaluate(self.skinGeo, v = True)
		
		# progress window
		cmds.progressWindow(title = 'Creating Corrective Shape', maxValue = vtxNum, status = 'stand by', isInterruptable = True)

		# get the delta that between sculpted geometry and skin geometry 
		for i in xrange(vtxNum):
			if cmds.progressWindow(q = True, isCancelled = True):
				break
			cmds.progressWindow(e = True, step = 1, status = 'calculating delta...')

			sculptVtxPos = cmds.pointPosition('%s.vtx[%d]' %(self.sculptGeo, i), world = True)
			sculptVtxVec = OpenMaya.MVector(*sculptVtxPos)
			skinVtxPos = cmds.pointPosition('%s.vtx[%d]' %(self.skinGeo, i), world= True)
			skinVtxVec = OpenMaya.MVector(*skinVtxPos)
			delta = sculptVtxVec - skinVtxVec
			# if vertex didn't move, skip
			if delta.length() < 0.001:
				continue
			self.vtxDeltaDic[i] = delta
		
		cmds.progressWindow(e = True, progress = 0, status = 'calculating delta...')
		
		# set envelop to 0 about all deformers without skin cluster of skin geometry
		allConnections = cmds.listHistory(self.skinGeo)
		for item in allConnections:
			if cmds.objectType(item) in self.deformerList:
				cmds.setAttr('%s.envelope' %item, 0)
		
		# reset progression window maxValue
		cmds.progressWindow(e = True, maxValue = len(self.vtxDeltaDic))

		# get vertex position that skin cluster plus delta
		for i in self.vtxDeltaDic.keys():
			if cmds.progressWindow(q = True, isCancelled = True):
				break
			cmds.progressWindow(e = True, step = 1, status = 'calculating final sculpt vtx position...')

			skinVtxPos = cmds.pointPosition('%s.vtx[%d]' %(self.skinGeo, i), world= True)
			skinVtxVec = OpenMaya.MVector(*skinVtxPos)
			sculptVtxFinVecDic[i] = skinVtxVec + self.vtxDeltaDic[i]
			sculptVtxPointDic[i] = OpenMaya.MPoint(sculptVtxFinVecDic[i].x, sculptVtxFinVecDic[i].y, sculptVtxFinVecDic[i].z)
		
		cmds.progressWindow(e = True, progress = 0, status = 'calculating final sculpt vtx position...')
		
		# get inversed vertex position
		for i in self.vtxDeltaDic.keys():
			if cmds.progressWindow(q = True, isCancelled = True):
				break
			cmds.progressWindow(e = True, step = 1, status = 'calculating inverse matrix...')
		    
			# set matrix pallete
			matrixPallete = OpenMaya.MMatrix()
			matrixPalletInitList = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
			OpenMaya.MScriptUtil.createMatrixFromList(matrixPalletInitList, matrixPallete)
		    
			# get influences
			influenceList = cmds.skinCluster('%s.vtx[%d]' %(self.skinGeo, i), q = True, wi = True)

			# for each influence get the matrix and multiply inverse matrix
			for influence in influenceList:
				infBindMatrixList = cmds.getAttr('%s.bindPose' %influence)
				infWorldMatrixList = cmds.getAttr('%s.worldMatrix' %influence)
				infWeight = cmds.skinPercent(self.skinCluster, '%s.vtx[%d]' %(self.skinGeo, i), q = True, transform = influence, v = True)

				if infWeight == 0.0:
					continue
			
				infBindMatrix = OpenMaya.MMatrix()
				OpenMaya.MScriptUtil.createMatrixFromList(infBindMatrixList, infBindMatrix)		
				infWorldMatrix = OpenMaya.MMatrix()
				OpenMaya.MScriptUtil.createMatrixFromList(infWorldMatrixList, infWorldMatrix)
				matrixPallete += (infBindMatrix.inverse() * infWorldMatrix) * infWeight
				
			inverseVtxPosDic[i] = sculptVtxPointDic[i] * matrixPallete.inverse()

		cmds.progressWindow(e = True, progress = 0, status = 'calculating inverse matrix...')

		# on eidt mode, replace poseName to selTrg
		if mode == 'editMode':
			self.poseName = cmds.textScrollList('r_poseTexScrList', q = True, selectItem = True)[0]
		
		if mode != 'editMode':
			# get corrective geometry by duplicating skin geometry with skinCluster envelope 0
			cmds.setAttr('%s.envelope' %self.skinCluster, 0)
			cmds.duplicate(self.skinGeo, n = self.poseName)		
			# delete intermediate shape	
			shapList = cmds.ls(self.poseName, dag = True, s = True)
			for shap in shapList:
				if cmds.getAttr('%s.intermediateObject' %(shap)): 
				    cmds.delete(shap)
			    
		# set corrective shape's vertex position
		if mode != 'editMode':
			for i in self.vtxDeltaDic.keys():
				if cmds.progressWindow(q = True, isCancelled = True):
					break
				cmds.progressWindow(e = True, step = 1, status = 'calculating corrective vtx position...')

				cmds.xform('%s.vtx[%d]' %(self.poseName, i), ws = True, t = (inverseVtxPosDic[i].x, inverseVtxPosDic[i].y, inverseVtxPosDic[i].z))

		elif mode == 'editMode':
			for i in self.vtxDeltaDic.keys():
				if cmds.progressWindow(q = True, isCancelled = True):
					break
				cmds.progressWindow(e = True, step = 1, status = 'calculating facial target vtx position...')

				# get vertex position that no assigned deformer
				cmds.setAttr('%s.envelope' %self.skinCluster, 0)
				skinVtxPos = cmds.pointPosition('%s.vtx[%d]' %(self.skinGeo, i), world = True)

				# get modified vertex vector
				modifiedVtxPos = [(inverseVtxPosDic[i].x - skinVtxPos[0]), (inverseVtxPosDic[i].y - skinVtxPos[1]), (inverseVtxPosDic[i].z - skinVtxPos[2])]

				# add modified vertex vector to original target vertex vector
				facialTrgVtxPos = cmds.pointPosition('%s.vtx[%d]' %(self.poseName, i), world = True)
				finalVtxPos = [(facialTrgVtxPos[0] + modifiedVtxPos[0]), (facialTrgVtxPos[1] + modifiedVtxPos[1]), (facialTrgVtxPos[2] + modifiedVtxPos[2])]

				# set final vertex position
				cmds.xform('%s.vtx[%d]' %(self.poseName, i), ws = True, t = finalVtxPos)

		cmds.progressWindow(endProgress = True)

		# all deformer's envelope set to 1 of  skin geometry
		cmds.setAttr('%s.envelope' %self.skinCluster, 1)
		allConnections = cmds.listHistory(self.skinGeo)
		for item in allConnections:
			if cmds.objectType(item) in self.deformerList:
				cmds.setAttr('%s.envelope' %item, 1)
		
		# add corrective geometry to geo_grp
		if mode != 'editMode':
			corGeoGrpName = self.skinGeo + '_corrective_geo_grp'
			if cmds.objExists(corGeoGrpName):
				cmds.parent(self.poseName, corGeoGrpName)
				cmds.setAttr('%s.visibility' %self.poseName, False)
			else:
				cmds.createNode('transform', n = corGeoGrpName)
				cmds.parent(self.poseName, corGeoGrpName)
				cmds.setAttr('%s.visibility' %self.poseName, False)

		# delete sculpt geometry
		cmds.delete(self.sculptGeo)
		
		if mode != 'editMode':
			# add corrective to blend shape node
			if cmds.objExists(self.bsName):
				bsAttrList = cmds.aliasAttr(self.bsName, q=True)
				weightNumList = []
				for bsAttr in bsAttrList:
					if 'weight' in bsAttr:
						reObj = re.search(r'\d+', bsAttr)
						weightNum = reObj.group()
						weightNumList.append(int(weightNum))
				bsIndex = max(weightNumList) + 1
				cmds.blendShape(self.bsName, edit = True, target = (self.skinGeo, bsIndex, self.poseName, 1.0))
				cmds.setAttr('%s.%s' %(self.bsName, self.poseName), 1)
				# refresh pose list
				self.populatePoseList()
			else:
				cmds.blendShape(self.poseName, self.skinGeo, n = self.bsName, frontOfChain = True)[0]
				cmds.setAttr('%s.%s' %(self.bsName, self.poseName), 1)
				# refresh pose list
				self.populatePoseList()

			# get data for pose reader
			driverJoint = cmds.textFieldButtonGrp('jntTexButGrp', q = True, text = True)
			parentJoint = cmds.textFieldButtonGrp('prntJointTexBtnGrp', q = True, text = True)
			locatorJoint = cmds.textFieldButtonGrp('locJointTexBtnGrp', q = True, text = True)
			    
			# pose reader
			self.poseReader(driverJoint, parentJoint, locatorJoint, self.poseName)

			# mirror
			mirOpt = cmds.checkBox('mirChkBox', q = True, v = True)
			if mirOpt:
				# create fliped opposite side geometry
				flipGeo = self.flipGeo()

				# add opposite corrective to the blend shape node
				bsAttrList = cmds.aliasAttr(self.bsName, q=True)
				weightNumList = []
				for bsAttr in bsAttrList:
					if 'weight' in bsAttr:
						reObj = re.search(r'\d+', bsAttr)
						weightNum = reObj.group()
						weightNumList.append(int(weightNum))
				bsIndex = max(weightNumList) + 1
				cmds.blendShape(self.bsName, edit = True, target = (self.skinGeo, bsIndex, flipGeo, 1.0))
				cmds.setAttr('%s.%s' %(self.bsName, flipGeo), 1)
				# refresh pose list
				self.populatePoseList()

				# get data for opposite side pose reader
				jntSearchTex = cmds.textFieldGrp('jntSrchTexFld', q = True, text = True)
				jntReplaceTex = cmds.textFieldGrp('jntRplcTexFld', q = True, text = True)
				oppoDriverJnt = re.sub(jntSearchTex, jntReplaceTex, driverJoint, 1)
				oppoParentJnt = re.sub(jntSearchTex, jntReplaceTex, parentJoint)
				oppolocatorJnt = re.sub(jntSearchTex, jntReplaceTex, locatorJoint, 1)

				# set opposite side pose
				srcRo = cmds.getAttr('%s.rotate' %(driverJoint))[0]
				srcRo = (srcRo[0], -srcRo[1], srcRo[2])
				cmds.setAttr('%s.rotate' %(oppoDriverJnt), *srcRo)

				# create opposite side pose reader
				self.poseReader(oppoDriverJnt, oppoParentJnt, oppolocatorJnt, flipGeo)

		self.populatePoseList()

	def loadSel(self, wgtName):
		sel = cmds.ls(sl = True)[0]
		cmds.textFieldButtonGrp(wgtName, e = True, text = sel)


	def populatePoseList(self, *args):
		corPoseList = []
		if cmds.textScrollList('r_poseTexScrList', q = True, allItems = True):
			cmds.textScrollList('r_poseTexScrList', e = True, removeAll = True)
		try:
			poseList = cmds.blendShape(self.bsName, q = True, target = True)
			for pose in poseList:
				if not '_corShp' in pose:
					continue
				else:
					corPoseList.append(pose)					
		except:
			pass
		cmds.textScrollList('r_poseTexScrList', e = True, append = corPoseList)


	def cancel(self, *args):
		cmds.delete(self.sculptGeo)
		cmds.setAttr('%s.visibility' %self.skinGeo, True)


	def texScrSel(self, *args):
		selectedPose = cmds.textScrollList('r_poseTexScrList', q = True, selectItem = True)[0]
		cmds.select('%s_pose_loc' %selectedPose, r = True)
    
    
	def removePose(self, *args):
		selectedPoseList = cmds.textScrollList('r_poseTexScrList', q = True, selectItem = True)
		bsAttrList = cmds.aliasAttr(self.bsName, q=True)

		for selectedPose in selectedPoseList:
			selTrgIndexInList = bsAttrList.index(selectedPose)
			selTrgWeightIndex = selTrgIndexInList + 1
			reObj = re.search(r'\d+', bsAttrList[selTrgWeightIndex])
			poseIndex = int(reObj.group())

			cmds.blendShape(self.bsName, e = True, remove = True, target = (self.skinGeo, poseIndex, selectedPose, 1))
			cmds.delete(selectedPose)
			cmds.delete(selectedPose + '_pose_loc')
			cmds.delete(selectedPose + '_remapVal')
			cmds.delete(selectedPose + '_anglBtwn')
		# refresh pose list
		self.populatePoseList()
	

	def poseReader(self, driverJoint, parentJoint, locatorJoint, poseName):	
		# get joints position
		driverJointPos = cmds.xform(driverJoint, q = True, ws = True, t = True)
		locatorJointPos = cmds.xform(locatorJoint, q = True, ws = True, t = True)
		
		# create locator and place
		if not cmds.objExists(driverJoint + '_corrective_base_loc'):
			baseLoc = cmds.spaceLocator(n = driverJoint + '_corrective_base_loc')[0]
			cmds.xform(baseLoc, ws = True, t = driverJointPos)

			triggerLoc = cmds.spaceLocator(n = driverJoint + '_corrective_trigger_loc')[0]
			cmds.xform(triggerLoc, ws = True, t = locatorJointPos)

			corLocGrp = cmds.createNode('transform', n = driverJoint + '_correctiveLoc_grp')
		else:
			baseLoc = driverJoint + '_corrective_base_loc'
			triggerLoc = driverJoint + '_corrective_trigger_loc'
		
		poseLoc = cmds.spaceLocator(n = poseName + '_pose_loc')[0]
		cmds.addAttr(poseLoc, ln = 'angle', at = 'double', dv = 45, keyable = True)
		# add vector attribute for saving pose
		cmds.addAttr(poseLoc, ln = driverJoint + '_poseX', at = 'double', keyable = False)
		cmds.addAttr(poseLoc, ln = driverJoint + '_poseY', at = 'double', keyable = False)
		cmds.addAttr(poseLoc, ln = driverJoint + '_poseZ', at = 'double', keyable = False)
		driverJointRot = cmds.xform(driverJoint, q = True, os = True, ro = True)
		cmds.setAttr('%s.%s_poseX' %(poseLoc, driverJoint), driverJointRot[0])
		cmds.setAttr('%s.%s_poseY' %(poseLoc, driverJoint), driverJointRot[1])
		cmds.setAttr('%s.%s_poseZ' %(poseLoc, driverJoint), driverJointRot[2])
		cmds.xform(poseLoc, ws = True, t = locatorJointPos)
		
		# parenting
		# if create pose corrective in first time...
		if not triggerLoc in cmds.listRelatives(baseLoc, c = True):
			cmds.parent(triggerLoc, baseLoc)
			cmds.parent(baseLoc, corLocGrp)
		cmds.parent(poseLoc, baseLoc)

		# hide locator
		cmds.setAttr('%s.visibility' %baseLoc, 0)
		
		# create angle between node and remap value node
		anglBtwn = cmds.shadingNode('angleBetween', n = poseName + '_anglBtwn', asUtility = True)
		remapVal = cmds.shadingNode('remapValue', n = poseName + '_remapVal', asUtility = True)
		cmds.setAttr('%s.inputMax' %remapVal, 0)
		cmds.setAttr('%s.value[0].value_Interp' %remapVal, 2)
		
		# connect attributes
		cmds.connectAttr('%s.translate' %triggerLoc, '%s.vector1' %anglBtwn, force = True)
		cmds.connectAttr('%s.translate' %poseLoc, '%s.vector2' %anglBtwn, force = True)
		cmds.connectAttr('%s.angle' %anglBtwn, '%s.inputValue' %remapVal, force = True)
		cmds.connectAttr('%s.angle' %poseLoc, '%s.inputMin' %remapVal, force = True)
		cmds.connectAttr('%s.outValue' %remapVal, '%s.%s' %(self.bsName, poseName), force = True)
		
		# constraint
		cmds.parentConstraint(locatorJoint, triggerLoc, mo = True)
		cmds.parentConstraint(parentJoint, baseLoc, mo = True)


	def flipGeo(self):
		# for all deformers set envelop value to 0
		allConnections = cmds.listHistory(self.skinGeo)
		for item in allConnections:
			# blendshape envelop
			if cmds.objectType(item) in self.deformerList:
				cmds.setAttr('%s.envelope' %item, 0)
		# skin cluster envelop
		cmds.setAttr('%s.envelope' %self.skinCluster, 0)

		# get symmetry vertex info
		symVtxDic, cVtxList = self.matchSymVtx(self.skinGeo)

		# duplicate corrective geometry
		poseSearchText = cmds.textFieldGrp('poseSrchTexFld', q = True, text = True)
		poseReplaceText = cmds.textFieldGrp('poseRplcTexFld', q = True, text = True)
		flipGeoName = re.sub(poseSearchText, poseReplaceText, self.poseName)
		cmds.duplicate(self.poseName, n = flipGeoName)

		for lVtxIndex in symVtxDic.keys():
			# get left and right vertex position
			lVtxPos = cmds.pointPosition('%s.vtx[%d]' %(flipGeoName, lVtxIndex), local = True)
			rVtxPos = cmds.pointPosition('%s.vtx[%d]' %(flipGeoName, symVtxDic[lVtxIndex]), local = True)

			# change lVtxPos and rVtxPos
			lVtxPos, rVtxPos = (-rVtxPos[0], rVtxPos[1], rVtxPos[2]), (-lVtxPos[0], lVtxPos[1], lVtxPos[2])

			# set vertex position
			cmds.xform('%s.vtx[%d]' %(flipGeoName, lVtxIndex), os = True, t = lVtxPos)
			cmds.xform('%s.vtx[%d]' %(flipGeoName, symVtxDic[lVtxIndex]), os = True, t = rVtxPos)

		#  for all deformers set envelop value to 1
		allConnections = cmds.listHistory(self.skinGeo)
		for item in allConnections:
			# blendshape envelop
			if cmds.objectType(item) in self.deformerList:
				cmds.setAttr('%s.envelope' %item, 1)
		# skin cluster envelop
		cmds.setAttr('%s.envelope' %self.skinCluster, 1)

		return flipGeoName


	# function for match symmetry vertex
	def matchSymVtx(self, geomtry):
		# get number of vertex
		numOfVtx = cmds.polyEvaluate(geomtry, v = True)
		# get symmtry vertex tolerance
		symVtxTol = cmds.floatField('symVtxTolTexFiel', q = True, v = True)

		# get left and right and center vertex list
		lVtxList = []
		rVtxList = []
		cVtxList = []
		symVtxDic = {}

		for i in xrange(numOfVtx):
			vtxPos = cmds.pointPosition('%s.vtx[%d]' %(geomtry, i), local = True)

			# refine raw vtxPos data
			for val in xrange(len(vtxPos)):
				if 'e' in str(vtxPos[val]):
					vtxPos[val] = 0.0
				else:
					vtxPos[val] = round(vtxPos[val], 3)

				if vtxPos[0] > 0:
					lVtxList.append(i)
				elif vtxPos[0] < 0:
					rVtxList.append(i)
				else:
					cVtxList.append(i)

		# get symVtxDic
		for lVtxIndex in lVtxList:
			lVtxPos = cmds.pointPosition('%s.vtx[%d]' %(geomtry, lVtxIndex), local = True)
			symVtxPos = -lVtxPos[0], lVtxPos[1], lVtxPos[2]
			symVtxVec = OpenMaya.MVector(*symVtxPos)

			for rVtxIndex in rVtxList:
				rVtxPos = cmds.pointPosition('%s.vtx[%d]' %(geomtry, rVtxIndex), local = True)
				rVtxVec = OpenMaya.MVector(*rVtxPos)

				dist = symVtxVec - rVtxVec

				if dist.length() <= symVtxTol:
					symVtxDic[lVtxIndex] = rVtxIndex
					index = rVtxList.index(rVtxIndex)
					rVtxList.pop(index)
					break

		return symVtxDic, cVtxList


	def edit(self, *args):
		# set to pose
		selPoseLoc = cmds.textScrollList('r_poseTexScrList', q = True, selectItem = True)[0] + '_pose_loc'
		attrList = cmds.listAttr(selPoseLoc, userDefined = True)
		poseAttrList = []
		for attr in attrList:
			if 'pose' in attr:
				poseAttrList.append(attr)

		for poseAttr in poseAttrList:
			poseInfo = poseAttr.rsplit('_pose')
			poseInfo.append(cmds.getAttr('%s.%s' %(selPoseLoc, poseAttr)))
			cmds.setAttr('%s.rotate%s' %(poseInfo[0],poseInfo[1]), poseInfo[2])

		# into the sculpt mode
		self.sculptMode()

		# create hud button
		cmds.hudButton('doneEditHudBtn', s = 3, b = 4, vis = 1, l = 'Done Edit', bw = 80, bsh = 'roundRectangle', rc = self.doneEdit)
		cmds.hudButton('cancelEditHudBtn', s = 3, b = 6, vis = 1, l = 'Cancel Edit', bw = 80, bsh = 'roundRectangle', rc = self.cancelEdit)


	def doneEdit(self, *args):
		self.createCorrective('editMode')
		self.removeHudBtn()


	def cancelEdit(self, *args):
		self.cancel()
		self.removeHudBtn()


	def removeHudBtn(self, *args):
		cmds.headsUpDisplay('doneEditHudBtn', remove = True)
		cmds.headsUpDisplay('cancelEditHudBtn', remove = True)