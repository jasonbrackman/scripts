'''
Author: Sang-tak Lee
Contact: chst27@gmail.com

Description:
This script is for correct problematic shape of rigged character.

Usage:
1. Copy this script and paste in your scripts folder.

2. In maya python tab, run following code.
import tak_aniSculpt
reload(tak_aniSculpt)
aniSculptObj = tak_aniSculpt.AniSculpt()
aniSculptObj.UI()
'''

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya

class AniSculpt:

	deformerList = ['blendShape', 'cluster', 'ffd', 'wrap', 'nonLinear', 'sculpt', 'softMod', 'jiggle', 'wire']

	def UI(self):
		winName = 'asWin'
		if cmds.window(winName, exists = True):
			cmds.deleteUI(winName)
		cmds.window(winName, title = 'Ani Sculpt UI')

		cmds.columnLayout('mainColLay', adj = True)

		cmds.separator(h = 10, style = 'none')

		cmds.textFieldButtonGrp('geoTexFld', label = 'Geo to Sculpt: ', buttonLabel = '<<', columnWidth = [(1, 75), (2, 100)], bc = self.loadGeoBS)

		cmds.separator(h = 5, style = 'none')

		cmds.optionMenuGrp('bsOptMenu', label = 'Blendshape Node: ', columnWidth = [(1, 95)])
		cmds.setParent('mainColLay')

		cmds.separator(h = 5, style = 'none')

		cmds.textFieldGrp('correctiveNameTexFld', label = 'Corrective Name: ', columnWidth = [(1, 100)],columnAttach = [(1, 'left', 5), (2, 'left', 0)])

		cmds.separator(h = 5, style = 'none')

		cmds.rowColumnLayout('sculptRowColLay', numberOfColumns = 2, columnWidth = [(1, 105), (2, 60)], columnAttach = [(2, 'left', 3)])
		cmds.button('sculptBut', label = 'Sculpt', c = self.sculptMode)
		cmds.button('cancelBut', label = 'Cancel', w = 105, c = self.cancel)
		cmds.setParent('mainColLay')

		cmds.separator(h = 5, style = 'none')

		cmds.button('appBtn', label = 'Apply', h = 50, c = self.createCorrective)


		cmds.window(winName, e = True, w = 190, h = 100)
		cmds.showWindow(winName)

	def sculptMode(self, *args):
		self.bsName = cmds.optionMenuGrp('bsOptMenu', q = True, v = True)
		if self.bsName == 'New':
			self.bsName = '%s_CorrectiveBS' %self.skinGeo
		
		# get data
		self.correctiveName = cmds.textFieldGrp('correctiveNameTexFld', q = True, text = True)
		
		if not cmds.objExists('%s.%s' %(self.bsName, self.correctiveName)) and cmds.objExists(self.correctiveName):
			cmds.error('Please enter another corrective name.')

		# duplicate skined geometry
		self.sculptGeo = cmds.duplicate(self.skinGeo, n = self.correctiveName + '_sculpt')[0]

	        	# delete intermediate shape
		shapList = cmds.ls(self.sculptGeo, dag = True, s = True)
		for shap in shapList:
			if cmds.getAttr('%s.intermediateObject' %(shap)): 
			    cmds.delete(shap)

	        	# assign sculpt shader
		if not cmds.objExists('correctiveCorrective_mat'):
		    	shaderName = cmds.shadingNode('lambert', n = 'correctiveCorrective_mat', asShader = True)
		    	cmds.setAttr("%s.color" %shaderName, 0.686, 0.316, 0.121)
		else:
		   	 shaderName = 'correctiveCorrective_mat'
		cmds.select(self.sculptGeo, r = True)
		cmds.hyperShade(assign = shaderName)

		# hide skin geometry
		cmds.setAttr('%s.visibility' %self.skinGeo, False)

	def cancel(self, *args):
		cmds.delete(self.sculptGeo)
		cmds.setAttr('%s.visibility' %self.skinGeo, True)
		
	def createCorrective(self, *args):
		curUnit = cmds.currentUnit(q = True, linear = True)
		if curUnit == 'm':
			cmds.currentUnit(linear = 'cm')

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

		# when edit exists corrective, set corrective value to 0
		if cmds.objExists(self.correctiveName):
			cmds.setAttr('%s.%s' %(self.bsName, self.correctiveName), 0)

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
		    	if item == 'parallelBlender':
           			 continue
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
		
		# get corrective geometry by duplicating skin geometry with skinCluster envelope 0
		if not cmds.objExists(self.correctiveName):
			cmds.setAttr('%s.envelope' %self.skinCluster, 0)
			cmds.duplicate(self.skinGeo, n = self.correctiveName)
			# delete intermediate shape	
			shapList = cmds.ls(self.correctiveName, dag = True, s = True)
			for shap in shapList:
				if cmds.getAttr('%s.intermediateObject' %(shap)): 
				    cmds.delete(shap)
			    
		# set corrective shape's vertex position
		for i in self.vtxDeltaDic.keys():
		    if cmds.progressWindow(q = True, isCancelled = True):
			break
		    cmds.progressWindow(e = True, step = 1, status = 'calculating corrective vtx position...')
		    
		    cmds.xform('%s.vtx[%d]' %(self.correctiveName, i), ws = True, t = (inverseVtxPosDic[i].x, inverseVtxPosDic[i].y, inverseVtxPosDic[i].z))
		    
		cmds.progressWindow(endProgress = True)
		    
		# all deformer's envelope set to 1 of  skin geometry
		cmds.setAttr('%s.envelope' %self.skinCluster, 1)
		allConnections = cmds.listHistory(self.skinGeo)
		for item in allConnections:
		    if cmds.objectType(item) in self.deformerList:
		    	if item == 'parallelBlender':
           			 continue
			cmds.setAttr('%s.envelope' %item, 1)
		
		# add corrective geometry to geo_grp
		corGeoGrpName = self.skinGeo + '_corrective_geo_grp'
		if cmds.objExists(corGeoGrpName):
			try:
				cmds.parent(self.correctiveName, corGeoGrpName)
				cmds.setAttr('%s.visibility' %self.correctiveName, False)
			except:
				pass
		else:
			cmds.createNode('transform', n = corGeoGrpName)
			cmds.parent(self.correctiveName, corGeoGrpName)
			cmds.setAttr('%s.visibility' %self.correctiveName, False)
		    
		# delete sculpt geometry
		cmds.delete(self.sculptGeo)
		
		# add corrective to blend shape node
		if not cmds.objExists('%s.%s' %(self.bsName, self.correctiveName)):
			if cmds.objExists(self.bsName):
			    bsIndex = len(cmds.blendShape(self.bsName, q = True, target = True))
			    cmds.blendShape(self.bsName, edit = True, target = (self.skinGeo, bsIndex, self.correctiveName, 1.0))
			    cmds.setAttr('%s.%s' %(self.bsName, self.correctiveName), 1)
			else:
			    cmds.blendShape(self.correctiveName, self.skinGeo, n = self.bsName, frontOfChain = True)[0]
			    cmds.setAttr('%s.%s' %(self.bsName, self.correctiveName), 1)

		    	# key frame to corrective blend shape
		    	self.keyBS()
	    	# when complete editing exists corrective, set corrective value to 1
		else:
			cmds.setAttr('%s.%s' %(self.bsName, self.correctiveName), 1)

		cmds.currentUnit(linear = curUnit)

	def keyBS(self):
		curFrame = cmds.currentTime(q = True)
		preFrame = curFrame - 10
		postFrame = curFrame + 10

		# key to corrective on current frame
		cmds.setKeyframe('%s.%s' %(self.bsName, self.correctiveName), v = 1, time = curFrame, itt = 'linear', ott = 'linear')

		# key to corrective on pre frame
		cmds.setKeyframe('%s.%s' %(self.bsName, self.correctiveName), v = 0, time = preFrame, itt = 'linear', ott = 'linear')

		# key to corrective on post frame
		cmds.setKeyframe('%s.%s' %(self.bsName, self.correctiveName), v = 0, time = postFrame, itt = 'linear', ott = 'linear')

	def loadGeoBS(self):
		self.skinGeo = cmds.ls(sl = True)[0]
		if not cmds.nodeType(self.skinGeo) == 'transform':
			cmds.error('Please select skined geometry.')
		cmds.textFieldButtonGrp('geoTexFld', e = True, text = self.skinGeo)

		# load BS nodes
		self.bsList = []
		allConnections = cmds.listHistory(self.skinGeo)
		for item in allConnections:
		    if cmds.objectType(item) in self.deformerList:
		    	self.bsList.append(item)

	    	# if already exists menu item in the bsOptMenu, delete menu items before populate
	    	bsOptItems = cmds.optionMenuGrp('bsOptMenu', q = True, itemListLong = True)
		if bsOptItems != None:
			for bsOptItem in bsOptItems:
				cmds.deleteUI(bsOptItems)

	    	if self.bsList:
			for bsNode in self.bsList:
				cmds.menuItem(label = bsNode, p = ('bsOptMenu' + '|OptionMenu'))
		elif not self.bsList:
			cmds.menuItem(label = 'New', p = ('bsOptMenu' + '|OptionMenu'))