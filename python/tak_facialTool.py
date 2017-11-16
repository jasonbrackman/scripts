'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date: 2015.05.14

Description:
This script help facial set up.
'''

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
from functools import partial
import softClusterEX
import re

class UI(object):
	widgets = {}
	winName = 'takFacialUI'


	@classmethod
	def __init__(cls):
		if cmds.window(cls.winName, exists = True):
			cmds.deleteUI(cls.winName)

		cls.ui()


	@classmethod
	def ui(cls):
		cmds.window(cls.winName, title = 'Tak Facial Tool', mnb = False, mxb = False)

		cls.widgets['mainColLo'] = cmds.columnLayout(adj = True)
		
		cls.widgets['skinGeoRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 3)
		cmds.text(label = 'Skin Geometry: ', p = cls.widgets['skinGeoRowColLo'])
		cls.widgets['skinGeoTxtFld'] = cmds.textField(p = cls.widgets['skinGeoRowColLo'])
		cmds.button(label = '<<', p = cls.widgets['skinGeoRowColLo'], c = Functions.loadGeoBS)

		cls.widgets['bsNodeRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 2, p = cls.widgets['mainColLo'])
		cmds.text(label = 'Blend Shape Node: ', p = cls.widgets['bsNodeRowColLo'])
		cls.widgets['bsNodeOptMenu'] = cmds.optionMenu(p = cls.widgets['bsNodeRowColLo'])

		cmds.separator(h = 10, style = 'in', p = cls.widgets['mainColLo'])

		cls.widgets['facialTrgNameRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 2, p = cls.widgets['mainColLo'])
		cmds.text(label = 'New Facial Target Name: ', p = cls.widgets['facialTrgNameRowColLo'])
		cls.widgets['facialTrgNameTxtFld'] = cmds.textField(p = cls.widgets['facialTrgNameRowColLo'])

		cls.widgets['scltBtnRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 2, columnWidth = [(1, 205), (2, 205)], columnSpacing = [(2, 5)], p = cls.widgets['mainColLo'])
		cmds.button(label = 'Sculpt', p = cls.widgets['scltBtnRowColLo'], c = Functions.sculptMode)
		cmds.button(label = 'Cancel', p = cls.widgets['scltBtnRowColLo'], c = Functions.cancelSculpt)

		cmds.button(label = 'Create', p = cls.widgets['mainColLo'], c = partial(Functions.createFacialTarget, Functions.modeList[0]))

		cmds.separator(h = 5, style = 'none', p = cls.widgets['mainColLo'])

		cls.widgets['facialTrgFrmLo'] = cmds.frameLayout(label = 'Facial Target List', collapsable = True, p = cls.widgets['mainColLo'])
		cls.widgets['facialTrgColLo'] = cmds.columnLayout(adj = True, p = cls.widgets['facialTrgFrmLo'])
		cls.widgets['facialTrgTxtScrList'] = cmds.textScrollList(allowMultiSelection = True, p = cls.widgets['facialTrgColLo'], sc = Functions.facialTrgListSelCmd)
		cmds.popupMenu(postMenuCommand = Functions.popupMenuCmd)
		cmds.menuItem(label = 'Refresh List', c = Functions.populateFacialTrgList)
		cls.widgets['popMenuRename'] = cmds.menuItem(label = 'Rename', c = Functions.rename, enable = False)
		cls.widgets['popMenuEdit'] = cmds.menuItem(label = 'Edit', c = Functions.trgListEidtCmd, enable = False)
		cls.widgets['popMenuInb'] = cmds.menuItem(label = 'Inbetween', c = Functions.trgListInbetweenCmd, enable = False)
		cls.widgets['popMenuCombo'] = cmds.menuItem(label = 'Combo', c = Functions.trgListComboCmd, enable = False)
		cls.widgets['popupMenuSplit'] = cmds.menuItem(label = 'Split L/R', c = Functions.splitLR, enable = False)
		cls.widgets['popMenuMerge'] = cmds.menuItem(label = 'Merge Selected', c = Functions.mergeTrg, enable = False)
		cls.widgets['popMenuFlip'] = cmds.menuItem(label = 'Flip', c = Functions.flip, enable = False)
		cls.widgets['popMenuMirror'] = cmds.menuItem(label = 'Mirror', c = Functions.mirror, enable = False)
		cls.widgets['popMenuDup'] = cmds.menuItem(label = 'Duplicate', c = Functions.dupTrg)
		cls.widgets['popMenuRmv'] = cmds.menuItem(label = 'Remove', c = Functions.removeTrg)
		cls.widgets['trgFltSldrGrp'] = cmds.floatSliderGrp(field = True, columnWidth = [(1, 30)], min = 0.00, max = 1.00, step = 0.01, p =cls.widgets['facialTrgColLo'], dc = Functions.trgSldrDragCmd, enable = False)

		cls.widgets['sdkFrmLo'] = cmds.frameLayout(label = 'Set Driven Key', collapse = True, collapsable = True, p = cls.widgets['mainColLo'])
		cls.widgets['sdkColLo'] = cmds.columnLayout(adj = True, p = cls.widgets['sdkFrmLo'])
		cls.widgets['sdkDrvrFrmLo'] = cmds.frameLayout(label = 'Driver', p = cls.widgets['sdkColLo'])
		cls.widgets['sdkDrvrColLo'] = cmds.columnLayout(adj = True, p = cls.widgets['sdkDrvrFrmLo'])
		cls.widgets['sdkDrvrRowColLo'] = cmds.rowColumnLayout(w = 300, numberOfColumns = 4, columnWidth = [(1, 50), (2, 250), (3, 40), (4, 50)], columnAttach = [(1, 'left', 10), (4, 'right', 5)], bgc = [0.5, 0.5, 0.5], p = cls.widgets['sdkDrvrColLo'])
		cmds.text(label = 'Object', p = cls.widgets['sdkDrvrRowColLo'])
		cmds.text(label = 'Attribute', p = cls.widgets['sdkDrvrRowColLo'])
		cmds.text(label = 'Start', p = cls.widgets['sdkDrvrRowColLo'])
		cmds.text(label = 'End', p = cls.widgets['sdkDrvrRowColLo'])
		cls.widgets['sdkDrvrSclLo'] = cmds.scrollLayout(h = 100, p = cls.widgets['sdkDrvrColLo'])
		cls.widgets['sdkDrvnFrmLo'] = cmds.frameLayout(label = 'Driven', p = cls.widgets['sdkColLo'])
		cls.widgets['sdkDrvnColLo'] = cmds.columnLayout(adj = True, p = cls.widgets['sdkDrvnFrmLo'])
		cls.widgets['sdkDrvnRowColLo'] = cmds.rowColumnLayout(w = 300, numberOfColumns = 4, columnWidth = [(1, 50), (2, 250), (3, 40), (4, 50)], columnAttach = [(1, 'left', 10), (4, 'right', 5)], bgc = [0.5, 0.5, 0.5], p = cls.widgets['sdkDrvnColLo'])
		cmds.text(label = 'Object', p = cls.widgets['sdkDrvnRowColLo'])
		cmds.text(label = 'Attribute', p = cls.widgets['sdkDrvnRowColLo'])
		cmds.text(label = 'Start', p = cls.widgets['sdkDrvnRowColLo'])
		cmds.text(label = 'End', p = cls.widgets['sdkDrvnRowColLo'])
		cls.widgets['sdkDrvnSclLo'] = cmds.scrollLayout(h = 100, p = cls.widgets['sdkDrvnColLo'])
		cls.widgets['sdkBtnRowColLo'] = cmds.rowColumnLayout(w = 300, numberOfColumns = 4, columnWidth = [(1, 105), (2, 105), (3, 105), (4, 97)], p = cls.widgets['sdkFrmLo'])
		cmds.button(label = 'Load Driver', p = cls.widgets['sdkBtnRowColLo'], c = Functions.loadDriver)
		cmds.button(label = 'Load Driven', p = cls.widgets['sdkBtnRowColLo'], c = Functions.loadDriven)
		cmds.button(label = 'Add Driven', p = cls.widgets['sdkBtnRowColLo'], c = Functions.addDriven)
		cmds.button(label = 'Key', p = cls.widgets['sdkBtnRowColLo'], c = Functions.sdk)

		cls.widgets['sdkExtraFrmLo'] = cmds.frameLayout(label = 'Extra Set Up', collapse = True, collapsable = True, p = cls.widgets['mainColLo'])
		cls.widgets['onFaceCtrlRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 2, columnWidth = [(1, 320), (2, 80)], columnOffset = [(2, 'left', 10)], p = cls.widgets['sdkExtraFrmLo'])
		cmds.button(label = 'On Face Control', c = Functions.onFaceCtrl, p = cls.widgets['onFaceCtrlRowColLo'])
		cls.widgets['onFaceCtrlSymChkbox'] = cmds.checkBox(label = 'Symmetry')
		cmds.button(label = 'Sticky Lips', p = cls.widgets['sdkExtraFrmLo'])

		cmds.window(cls.winName, e = True, w = 400, h = 300)
		cmds.showWindow(cls.winName)



class Functions(object):
	skinGeo = ''
	bsNodeName = ''
	modeList = ['create', 'edit', 'inbetween', 'combo']
	deformerList = ['blendShape', 'cluster', 'ffd', 'wrap', 'nonLinear', 'sculpt', 'softMod', 'jiggle', 'wire']

	@classmethod
	def loadGeoBS(cls, *args):
		cls.skinGeo = cmds.ls(sl = True)[0]
		if not cmds.nodeType(cls.skinGeo) == 'transform':
			cmds.error('Please select skined geometry.')
		cmds.textField(UI.widgets['skinGeoTxtFld'], e = True, text = cls.skinGeo)

		# load BS nodes
		cls.bsList = []
		allConnections = cmds.listHistory(cls.skinGeo)
		for item in allConnections:
			if cmds.objectType(item) == 'blendShape':
				cls.bsList.append(item)

		# if already exists menu item in the bsOptMenu, delete menu items before populate
		bsOptItems = cmds.optionMenu(UI.widgets['bsNodeOptMenu'], q = True, itemListLong = True)
		if bsOptItems != None:
			for bsOptItem in bsOptItems:
				cmds.deleteUI(bsOptItem)
		if cls.bsList:
			for bsNode in cls.bsList:
				cmds.menuItem(label = bsNode, p = UI.widgets['bsNodeOptMenu'])
		elif not cls.bsList:
			cmds.menuItem(label = 'New', p = UI.widgets['bsNodeOptMenu'])

		cls.bsNodeName = cmds.optionMenu(UI.widgets['bsNodeOptMenu'], q = True, v = True)

		cls.populateFacialTrgList()


	@classmethod
	def sculptMode(cls, *args):
		# get data
		cls.facialTrgName = cmds.textField(UI.widgets['facialTrgNameTxtFld'], q = True, text = True) + '_ftrg'
		
		# duplicate skined geometry
		cls.sculptGeo = cmds.duplicate(cls.skinGeo, n = cls.facialTrgName + '_sculpt')[0]

		# delete intermediate shape
		shapList = cmds.ls(cls.sculptGeo, dag = True, s = True)
		for shap in shapList:
			if cmds.getAttr('%s.intermediateObject' %(shap)): 
				cmds.delete(shap)

		# assign sculpt shader
		# if not cmds.objExists('sculpt_mat'):
		# 	shaderName = cmds.shadingNode('lambert', n = 'sculpt_mat', asShader = True)
		# 	cmds.setAttr("%s.color" %shaderName, 0.686, 0.316, 0.121)
		# else:
		# 	shaderName = 'sculpt_mat'
		# cmds.select(cls.sculptGeo, r = True)
		# cmds.hyperShade(assign = shaderName)

		# display hud
		cmds.headsUpDisplay('sclptHUD', section = 2, block = 2, blockSize = 'large', label = 'Sculpt Mode')

		# hide skin geometry
		cmds.setAttr('%s.visibility' %cls.skinGeo, False)


	@classmethod
	def cancelSculpt(cls, *args):
		cmds.headsUpDisplay('sclptHUD', remove = True)
		cmds.delete(cls.sculptGeo)
		cmds.setAttr('%s.visibility' %cls.skinGeo, True)


	@classmethod
	def createFacialTarget(cls, mode, *args):
		cmds.headsUpDisplay('sclptHUD', remove = True)

		# show skin geometry
		cmds.setAttr('%s.visibility' %cls.skinGeo, True)
		
		cls.vtxDeltaDic = {}
		sculptVtxFinVecDic = {}
		sculptVtxFinPointDic = {}
		inverseVtxPosDic = {}
		
		cls.getSkinCluster()
		
		# get number of vertex
		vtxNum = cmds.polyEvaluate(cls.skinGeo, v = True)
		
		# progress window
		cmds.progressWindow(title = 'Creating facial Target Shape', maxValue = vtxNum, status = 'stand by', isInterruptable = True)

		# get the delta that between sculpted geometry and skin geometry 
		for i in xrange(vtxNum):
			if cmds.progressWindow(q = True, isCancelled = True):
				break
			cmds.progressWindow(e = True, step = 1, status = 'calculating delta...')

			sculptVtxPos = cmds.pointPosition('%s.vtx[%d]' %(cls.sculptGeo, i), world = True)
			sculptVtxVec = OpenMaya.MVector(*sculptVtxPos)
			skinVtxPos = cmds.pointPosition('%s.vtx[%d]' %(cls.skinGeo, i), world= True)
			skinVtxVec = OpenMaya.MVector(*skinVtxPos)
			delta = sculptVtxVec - skinVtxVec
			# if vertex didn't move, skip
			if delta.length() < 0.001:
				continue
			cls.vtxDeltaDic[i] = delta

		cmds.progressWindow(e = True, progress = 0, status = 'calculating delta...')

		# if any vertex didn't move cancel and exit
		if not cls.vtxDeltaDic:
			cls.cancelSculpt()
			cmds.progressWindow(endProgress = True)
			return
		
		# set envelop to 0 about all deformers without skin cluster of skin geometry
		allConnections = cmds.listHistory(cls.skinGeo)
		for item in allConnections:
			if cmds.objectType(item) in cls.deformerList:
				cmds.setAttr('%s.envelope' %item, 0)
		
		# reset progression window maxValue
		cmds.progressWindow(e = True, maxValue = len(cls.vtxDeltaDic))

		# get vertex position that skin cluster plus delta
		for i in cls.vtxDeltaDic.keys():
			if cmds.progressWindow(q = True, isCancelled = True):
				break
			cmds.progressWindow(e = True, step = 1, status = 'calculating final sculpt vtx position...')

			skinVtxPos = cmds.pointPosition('%s.vtx[%d]' %(cls.skinGeo, i), world= True)
			skinVtxVec = OpenMaya.MVector(*skinVtxPos)
			sculptVtxFinVecDic[i] = skinVtxVec + cls.vtxDeltaDic[i]
			sculptVtxFinPointDic[i] = OpenMaya.MPoint(sculptVtxFinVecDic[i].x, sculptVtxFinVecDic[i].y, sculptVtxFinVecDic[i].z)
		
		cmds.progressWindow(e = True, progress = 0, status = 'calculating final sculpt vtx position...')
		
		# if on inbetween mode replace sculptVtxFinPointDic to sculpt geometry vertex vector
		if mode == cls.modeList[2]:
			for i in xrange(vtxNum):
				sculptVtxPos = cmds.pointPosition('%s.vtx[%d]' %(cls.sculptGeo, i), world = True)
				sculptVtxVec = OpenMaya.MVector(*sculptVtxPos)
				sculptVtxFinPointDic[i] = OpenMaya.MPoint(sculptVtxVec.x, sculptVtxVec.y, sculptVtxVec.z)
				cls.vtxDeltaDic[i] = sculptVtxVec
			# reset progression window maxValue
			cmds.progressWindow(e = True, maxValue = len(cls.vtxDeltaDic))

		# get inversed vertex position
		for i in cls.vtxDeltaDic.keys():
			if cmds.progressWindow(q = True, isCancelled = True):
				break
			cmds.progressWindow(e = True, step = 1, status = 'calculating inverse matrix...')

			# set matrix pallete
			matrixPallete = OpenMaya.MMatrix()
			matrixPalletInitList = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
			OpenMaya.MScriptUtil.createMatrixFromList(matrixPalletInitList, matrixPallete)

			# get influences
			influenceList = cmds.skinCluster('%s.vtx[%d]' %(cls.skinGeo, i), q = True, wi = True)

			# for each influence get the matrix and multiply inverse matrix
			for influence in influenceList:
				infBindMatrixList = cmds.getAttr('%s.bindPose' %influence)
				infWorldMatrixList = cmds.getAttr('%s.worldMatrix' %influence)
				infWeight = cmds.skinPercent(cls.skinCluster, '%s.vtx[%d]' %(cls.skinGeo, i), q = True, transform = influence, v = True)

				if infWeight == 0.0:
					continue
			
				infBindMatrix = OpenMaya.MMatrix()
				OpenMaya.MScriptUtil.createMatrixFromList(infBindMatrixList, infBindMatrix)
				infWorldMatrix = OpenMaya.MMatrix()
				OpenMaya.MScriptUtil.createMatrixFromList(infWorldMatrixList, infWorldMatrix)
				matrixPallete += (infBindMatrix.inverse() * infWorldMatrix) * infWeight
				
			inverseVtxPosDic[i] = sculptVtxFinPointDic[i] * matrixPallete.inverse()

		cmds.progressWindow(e = True, progress = 0, status = 'calculating inverse matrix...')

		# on eidt mode, replace facialTrgName to selTrg
		if mode == cls.modeList[1]:
			cls.facialTrgName = cmds.textScrollList(UI.widgets['facialTrgTxtScrList'], q = True, selectItem = True)[0]

		# on inbetween mode, replace facialTrgName to selTrg_inb
		if mode == cls.modeList[2]:
			cls.facialTrgName = cmds.textScrollList(UI.widgets['facialTrgTxtScrList'], q = True, selectItem = True)[0] + '_inb'

		# on combo mode rename facialTrgName
		if mode == cls.modeList[3]:
			selTrgList = cmds.textScrollList(UI.widgets['facialTrgTxtScrList'], q = True, selectItem = True)
			joinStr = '_'
			selTrgNameList = []
			for selTrg in selTrgList:
				selTrgNameList.append(selTrg.rsplit('_ftrg')[0])
			cls.facialTrgName =  joinStr.join(selTrgNameList) + '_cb_ftrg'

		# get facial target geometry by duplicating skin geometry with skinCluster envelope 0
		if mode in (cls.modeList[0], cls.modeList[2], cls.modeList[3]):
			cmds.setAttr('%s.envelope' %cls.skinCluster, 0)
			cmds.duplicate(cls.skinGeo, n = cls.facialTrgName)
			# delete intermediate shape	
			shapList = cmds.ls(cls.facialTrgName, dag = True, s = True)
			for shap in shapList:
				if cmds.getAttr('%s.intermediateObject' %(shap)): 
					cmds.delete(shap)

		# set facial target shape's vertex position
		if mode in (cls.modeList[0], cls.modeList[2], cls.modeList[3]):
			for i in cls.vtxDeltaDic.keys():
				if cmds.progressWindow(q = True, isCancelled = True):
					break
				cmds.progressWindow(e = True, step = 1, status = 'calculating facial target vtx position...')

				cmds.xform('%s.vtx[%d]' %(cls.facialTrgName, i), ws = True, t = (inverseVtxPosDic[i].x, inverseVtxPosDic[i].y, inverseVtxPosDic[i].z))

		elif mode == cls.modeList[1]:
			for i in cls.vtxDeltaDic.keys():
				if cmds.progressWindow(q = True, isCancelled = True):
					break
				cmds.progressWindow(e = True, step = 1, status = 'calculating facial target vtx position...')

				# get vertex position that no assigned deformer
				cmds.setAttr('%s.envelope' %cls.skinCluster, 0)
				skinVtxPos = cmds.pointPosition('%s.vtx[%d]' %(cls.skinGeo, i), world = True)

				# get modified vertex vector
				modifiedVtxPos = [(inverseVtxPosDic[i].x - skinVtxPos[0]), (inverseVtxPosDic[i].y - skinVtxPos[1]), (inverseVtxPosDic[i].z - skinVtxPos[2])]

				# add modified vertex vector to original target vertex vector
				facialTrgVtxPos = cmds.pointPosition('%s.vtx[%d]' %(cls.facialTrgName, i), world = True)
				finalVtxPos = [(facialTrgVtxPos[0] + modifiedVtxPos[0]), (facialTrgVtxPos[1] + modifiedVtxPos[1]), (facialTrgVtxPos[2] + modifiedVtxPos[2])]

				# set final vertex position
				cmds.xform('%s.vtx[%d]' %(cls.facialTrgName, i), ws = True, t = finalVtxPos)


		cmds.progressWindow(endProgress = True)

		# all deformer's envelope set to 1 of  skin geometry
		cmds.setAttr('%s.envelope' %cls.skinCluster, 1)
		allConnections = cmds.listHistory(cls.skinGeo)
		for item in allConnections:
			if cmds.objectType(item) in cls.deformerList:
				cmds.setAttr('%s.envelope' %item, 1)
		
		# add facial target geometry to geo_grp
		if mode in (cls.modeList[0], cls.modeList[3]):
			facialTrgGeoGrpName = cls.skinGeo + '_facialTrg_geo_grp'
			if cmds.objExists(facialTrgGeoGrpName):
				cmds.parent(cls.facialTrgName, facialTrgGeoGrpName)
				cmds.setAttr('%s.visibility' %cls.facialTrgName, False)
			else:
				cmds.createNode('transform', n = facialTrgGeoGrpName)
				cmds.parent(cls.facialTrgName, facialTrgGeoGrpName)
				cmds.setAttr('%s.visibility' %cls.facialTrgName, False)

		# delete sculpt geometry
		cmds.delete(cls.sculptGeo)
		
		# add facial target to blend shape node
		if mode in (cls.modeList[0], cls.modeList[3]):
			if cls.bsNodeName != 'New':
				bsAttrList = cmds.aliasAttr(cls.bsNodeName, q=True)
				if not bsAttrList:
					cmds.blendShape(cls.bsNodeName, edit = True, target = (cls.skinGeo, 0, cls.facialTrgName, 1.0))
					cmds.setAttr('%s.%s' %(cls.bsNodeName, cls.facialTrgName), 1)
				else:
					weightNumList = []
					for bsAttr in bsAttrList:
						if 'weight' in bsAttr:
							reObj = re.search(r'\d+', bsAttr)
							weightNum = reObj.group()
							weightNumList.append(int(weightNum))
					bsIndex = max(weightNumList) + 1

					cmds.blendShape(cls.bsNodeName, edit = True, target = (cls.skinGeo, bsIndex, cls.facialTrgName, 1.0))
					cmds.setAttr('%s.%s' %(cls.bsNodeName, cls.facialTrgName), 1)
			elif cls.bsNodeName == 'New':
				cls.bsNodeName = '{0}_facialBS'.format(cls.skinGeo)
				cmds.blendShape(cls.facialTrgName, cls.skinGeo, n = cls.bsNodeName, frontOfChain = True)[0]
				cmds.setAttr('%s.%s' %(cls.bsNodeName, cls.facialTrgName), 1)
				# fill blend shape node option menu
				# load BS nodes
				cls.bsList = []
				allConnections = cmds.listHistory(cls.skinGeo)
				for item in allConnections:
					if cmds.objectType(item) == 'blendShape':
						cls.bsList.append(item)

				# if already exists menu item in the bsOptMenu, delete menu items before populate
				bsOptItems = cmds.optionMenu(UI.widgets['bsNodeOptMenu'], q = True, itemListLong = True)
				if bsOptItems != None:
					for bsOptItem in bsOptItems:
						cmds.deleteUI(bsOptItem)
				if cls.bsList:
					for bsNode in cls.bsList:
						cmds.menuItem(label = bsNode, p = UI.widgets['bsNodeOptMenu'])

		if mode == cls.modeList[2]:
			selTrg = cmds.textScrollList(UI.widgets['facialTrgTxtScrList'], q = True, selectItem = True)[0]
			bsAttrList = cmds.aliasAttr(cls.bsNodeName, q=True)
			selTrgIndexInList = bsAttrList.index(selTrg)
			selTrgWeightIndex = selTrgIndexInList + 1
			reObj = re.search(r'\d+', bsAttrList[selTrgWeightIndex])
			selTrgIndex = int(reObj.group())

			weight = cmds.floatSliderGrp(UI.widgets['trgFltSldrGrp'], q = True, v = True)
			cmds.blendShape(cls.bsNodeName, e = True, inBetween = True, target = (cls.skinGeo, selTrgIndex, cls.facialTrgName, weight))
			cmds.delete(cls.facialTrgName)

		# connect combo facial target blend shape
		if mode == cls.modeList[3]:
			exprNodeName = cls.facialTrgName.replace('_ftrg', '_expr')
			exprStr = '{0}.{1} = '.format(cls.bsNodeName, cls.facialTrgName)
			# replace target list name to 'blend shape node.target name'
			for i in xrange(len(selTrgList)):
				selTrgList[i] = cls.bsNodeName + '.' + selTrgList[i]
			exprStr += ' * '.join(selTrgList)

			cmds.expression(s = exprStr, ae = True, uc = 'all', n = exprNodeName)

		# refresh facial target list
		cls.populateFacialTrgList()

	@classmethod
	def getSkinCluster(cls):
		cmds.select(cls.skinGeo, r = True)
		mel.eval('string $selList[] = `ls -sl`;')
		mel.eval('string $source = $selList[0];')
		cls.skinCluster = mel.eval('findRelatedSkinCluster($source);')
		return cls.skinCluster


	@classmethod
	def populateFacialTrgList(cls, *args):
		facialTrgBsList = []
		facialTrgScrList = []

		if cmds.textScrollList(UI.widgets['facialTrgTxtScrList'], q = True, allItems = True):
			cmds.textScrollList(UI.widgets['facialTrgTxtScrList'], e = True, removeAll = True)

		if cls.bsNodeName != 'New':
			facialTrgBsList = cmds.listAttr('%s.w' %(cls.bsNodeName), multi = True)
			if facialTrgBsList:
				for i in xrange(len(facialTrgBsList)):
					if not '_ftrg' in facialTrgBsList[i]:
						continue
					else:
						facialTrgScrList.append(facialTrgBsList[i])

				cmds.textScrollList(UI.widgets['facialTrgTxtScrList'], e = True, append = facialTrgScrList)

				# set bold font to connected targets
				for i in xrange(len(facialTrgScrList)):
					if cmds.listConnections('{0}.{1}'.format(cls.bsNodeName, facialTrgScrList[i]), source = True, destination = False):
						cmds.textScrollList(UI.widgets['facialTrgTxtScrList'], e = True, lineFont = (i + 1, 'boldLabelFont'))

		cmds.floatSliderGrp(UI.widgets['trgFltSldrGrp'], e = True, enable = False)


	@classmethod
	def trgSldrDragCmd(cls, *args):
		trgSldrVal = cmds.floatSliderGrp(UI.widgets['trgFltSldrGrp'], q = True, v = True)
		selTrgList = cmds.textScrollList(UI.widgets['facialTrgTxtScrList'], q = True, selectItem = True)
		for selTrg in selTrgList:
			try:
				cmds.setAttr('{0}.{1}'.format(cls.bsNodeName, selTrg), trgSldrVal)
			except:
				pass


	@classmethod
	def facialTrgListSelCmd(cls, *args):
		selTrgList = cmds.textScrollList(UI.widgets['facialTrgTxtScrList'], q = True, selectItem = True)

		if selTrgList >= 1:
			cmds.floatSliderGrp(UI.widgets['trgFltSldrGrp'], e = True, enable = True)
		else:
			cmds.floatSliderGrp(UI.widgets['trgFltSldrGrp'], e = True, enable = False)


	@classmethod
	def popupMenuCmd(cls, *args):
		selTrgList = cmds.textScrollList(UI.widgets['facialTrgTxtScrList'], q = True, selectItem = True)

		if selTrgList == None:
			cmds.menuItem(UI.widgets['popMenuEdit'], e = True, enable = False)
			cmds.menuItem(UI.widgets['popMenuRename'], e = True, enable = False)
			cmds.menuItem(UI.widgets['popMenuInb'], e = True, enable = False)
			cmds.menuItem(UI.widgets['popMenuCombo'], e = True, enable = False)
			cmds.menuItem(UI.widgets['popupMenuSplit'], e = True, enable = False)
			cmds.menuItem(UI.widgets['popMenuMerge'], e = True, enable = False)
			cmds.menuItem(UI.widgets['popMenuFlip'], e = True, enable = False)
			cmds.menuItem(UI.widgets['popMenuMirror'], e = True, enable = False)
			cmds.menuItem(UI.widgets['popMenuRmv'], e = True, enable = False)

		elif len(selTrgList) == 1:
			cmds.menuItem(UI.widgets['popMenuEdit'], e = True, enable = True)
			cmds.menuItem(UI.widgets['popMenuRename'], e = True, enable = True)
			cmds.menuItem(UI.widgets['popMenuInb'], e = True, enable = True)
			cmds.menuItem(UI.widgets['popMenuCombo'], e = True, enable = False)
			cmds.menuItem(UI.widgets['popupMenuSplit'], e = True, enable = True)
			cmds.menuItem(UI.widgets['popMenuMerge'], e = True, enable = False)
			cmds.menuItem(UI.widgets['popMenuFlip'], e = True, enable = True)
			cmds.menuItem(UI.widgets['popMenuMirror'], e = True, enable = True)
			cmds.menuItem(UI.widgets['popMenuRmv'], e = True, enable = True)

		elif len(selTrgList) >= 2:
			cmds.menuItem(UI.widgets['popMenuEdit'], e = True, enable = False)
			cmds.menuItem(UI.widgets['popMenuRename'], e = True, enable = False)
			cmds.menuItem(UI.widgets['popMenuInb'], e = True, enable = False)
			cmds.menuItem(UI.widgets['popMenuCombo'], e = True, enable = True)
			cmds.menuItem(UI.widgets['popupMenuSplit'], e = True, enable = True)
			cmds.menuItem(UI.widgets['popMenuMerge'], e = True, enable = True)
			cmds.menuItem(UI.widgets['popMenuFlip'], e = True, enable = True)
			cmds.menuItem(UI.widgets['popMenuMirror'], e = True, enable = True)
			cmds.menuItem(UI.widgets['popMenuRmv'], e = True, enable = True)


	@classmethod
	def rename(cls, *args):
		selTrg = cmds.textScrollList(UI.widgets['facialTrgTxtScrList'], q = True, selectItem = True)[0]
		selTrgName = selTrg.rsplit('_ftrg')[0]
		result = cmds.promptDialog(title = 'Rename Blend Target', message = 'New Blend Target Name', text = selTrgName, button = ['OK', 'Cancel'], defaultButton = 'OK', cancelButton = 'Cancel', dismissString = 'Cancel')
		if result == 'OK':
			replaceName = cmds.promptDialog(q = True, text = True) + '_ftrg'

			# rename blend shape name
			cmds.aliasAttr(replaceName, '%s.%s' %(cls.bsNodeName, selTrg))

			# rename target geometry name
			cmds.rename(selTrg, replaceName)

		cls.populateFacialTrgList()


	@classmethod
	def trgListEidtCmd(cls, *args):
		cls.sculptMode()
		cls.createHudBtn(cls.modeList[1])


	@classmethod
	def doneEdit(cls, *args):
		cls.createFacialTarget(cls.modeList[1])
		cls.removeHudBtn(cls.modeList[1])


	@classmethod
	def cancelEdit(cls, *args):
		cls.cancelSculpt()
		cls.removeHudBtn(cls.modeList[1])


	@classmethod
	def trgListInbetweenCmd(cls, *args):
		cls.sculptMode()
		cls.createHudBtn(cls.modeList[2])


	@classmethod
	def addInbetween(cls, *args):
		cls.createFacialTarget(cls.modeList[2])
		cls.removeHudBtn(cls.modeList[2])


	@classmethod
	def cancelInbetween(cls, *args):
		cls.cancelSculpt()
		cls.removeHudBtn(cls.modeList[2])


	@classmethod
	def trgListComboCmd(cls, *args):
		cls.sculptMode()
		cls.createHudBtn(cls.modeList[3])


	@classmethod
	def addCombo(cls, *args):
		cls.createFacialTarget(cls.modeList[3])
		cls.removeHudBtn(cls.modeList[3])
		cls.populateFacialTrgList()


	@classmethod
	def cancelCombo(cls, *args):
		cls.cancelSculpt()
		cls.removeHudBtn(cls.modeList[3])


	@classmethod
	def createHudBtn(cls, mode):
		if mode == cls.modeList[1]:
			cmds.hudButton('doneEditHudBtn', s = 3, b = 4, vis = 1, l = 'Done Edit', bw = 80, bsh = 'roundRectangle', rc = cls.doneEdit)
			cmds.hudButton('cancelEditHudBtn', s = 3, b = 6, vis = 1, l = 'Cancel Edit', bw = 80, bsh = 'roundRectangle', rc = cls.cancelEdit)

		if mode == cls.modeList[2]:
			cmds.hudButton('addInbetweenHudBtn', s = 3, b = 4, vis = 1, l = 'Add Inbtween', bw = 80, bsh = 'roundRectangle', rc = cls.addInbetween)
			cmds.hudButton('cancelInbetweenHudBtn', s = 3, b = 6, vis = 1, l = 'Cancel', bw = 80, bsh = 'roundRectangle', rc = cls.cancelInbetween)

		if mode == cls.modeList[3]:
			cmds.hudButton('addComboHudBtn', s = 3, b = 4, vis = 1, l = 'Add Combo', bw = 80, bsh = 'roundRectangle', rc = cls.addCombo)
			cmds.hudButton('cancelComboHudBtn', s = 3, b = 6, vis = 1, l = 'Cancel', bw = 80, bsh = 'roundRectangle', rc = cls.cancelCombo)


	@classmethod
	def removeHudBtn(cls, mode):
		if mode == cls.modeList[1]:
			cmds.headsUpDisplay('doneEditHudBtn', remove = True)
			cmds.headsUpDisplay('cancelEditHudBtn', remove = True)

		if mode == cls.modeList[2]:
			cmds.headsUpDisplay('addInbetweenHudBtn', remove = True)
			cmds.headsUpDisplay('cancelInbetweenHudBtn', remove = True)

		if mode == cls.modeList[3]:
			cmds.headsUpDisplay('addComboHudBtn', remove = True)
			cmds.headsUpDisplay('cancelComboHudBtn', remove = True)


	@classmethod
	def dupTrg(cls, *args):
		selTrgList = cmds.textScrollList(UI.widgets['facialTrgTxtScrList'], q = True, selectItem = True)
		facialTrgBsList = cmds.listAttr('%s.w' %(cls.bsNodeName), multi = True)

		for selTrg in selTrgList:
			bsAttrList = cmds.aliasAttr(cls.bsNodeName, q=True)
			weightNumList = []
			for bsAttr in bsAttrList:
				if 'weight' in bsAttr:
					reObj = re.search(r'\d+', bsAttr)
					weightNum = reObj.group()
					weightNumList.append(int(weightNum))
			bsIndex = max(weightNumList) + 1

			# duplicate
			dupGeo = cmds.duplicate(selTrg, n = selTrg.rsplit('_ftrg')[0] + '_dup_ftrg')[0]
			# add to blend shape node
			cmds.blendShape(cls.bsNodeName, edit = True, target = (cls.skinGeo, bsIndex, dupGeo, 1.0))

		cls.populateFacialTrgList()


	@classmethod
	def removeTrg(cls, *args):
		selTrgList = cmds.textScrollList(UI.widgets['facialTrgTxtScrList'], q = True, selectItem = True)
		facialTrgBsList = cmds.listAttr('%s.w' %(cls.bsNodeName), multi = True)

		for selTrg in selTrgList:
			bsAttrList = cmds.aliasAttr(cls.bsNodeName, q=True)
			selTrgIndexInList = bsAttrList.index(selTrg)
			selTrgWeightIndex = selTrgIndexInList + 1
			reObj = re.search(r'\d+', bsAttrList[selTrgWeightIndex])
			selTrgIndex = int(reObj.group())

			# delete blend shape
			cmds.blendShape(cls.bsNodeName, e = True, remove = True, target = (cls.skinGeo, selTrgIndex, selTrg, 1.0))
			# delete target geometry
			cmds.delete(selTrg)
			if '_cb' in selTrg:
				exprNodeName = selTrg.replace('_ftrg', '_expr')
		cls.populateFacialTrgList()


	@classmethod
	def splitLR(cls, *args):
		baseName = cls.skinGeo
		targetList = cmds.textScrollList(UI.widgets['facialTrgTxtScrList'], q = True, selectItem = True)
		lPrefix = 'L_'
		rPrefix = 'R_'
		facialTrgGeoGrpName = cls.skinGeo + '_facialTrg_geo_grp'

		# percentage of center fall off distance
		centerFallOff = 10 * 0.01
		maxVtxX = cls.getMaxXPos(baseName)
		fallOffRange = (centerFallOff * maxVtxX) * 2

		# set all deformer of skin geometry envelop to 0
		cls.getSkinCluster()
		cmds.setAttr('%s.envelope' %cls.skinCluster, 0)
		allConnections = cmds.listHistory(cls.skinGeo)
		for item in allConnections:
			if cmds.objectType(item) in cls.deformerList:
				cmds.setAttr('%s.envelope' %item, 0)

		for targetName in targetList:
			targetPos = cmds.xform(targetName, q = True, ws = True, t = True)
			boundingBox = cmds.exactWorldBoundingBox(targetName)
			LRDist = boundingBox[3] - boundingBox[0]

			lrTargets = []

			# create left side blend target
			lBlendTarget = cmds.duplicate(baseName, n = lPrefix + targetName, rr = True, renameChildren = True)
			lrTargets.append(lBlendTarget[0])
			# unlock attributes
			attrList = ['translateX', 'translateY', 'translateZ']
			for attr in attrList:
				cmds.setAttr(lBlendTarget[0] + '.' + str(attr), lock = False)
			# move to target's left side
			cmds.xform(lBlendTarget, ws = True, t = ((targetPos[0] + LRDist), targetPos[1], targetPos[2]))
			# parent to facialTrg_geo_grp
			cmds.parent(lBlendTarget[0], facialTrgGeoGrpName)
			cmds.setAttr('%s.visibility' %lBlendTarget[0], False)

			# create right side belnd target
			rBlendTarget = cmds.duplicate(baseName, n = rPrefix + targetName, rr = True, renameChildren = True)
			lrTargets.append(rBlendTarget[0])
			# unlock attributes
			for attr in attrList:
				cmds.setAttr(rBlendTarget[0] + '.' + str(attr), lock = False)
			# move to target's right side
			cmds.xform(rBlendTarget, ws = True, t = ((targetPos[0] - LRDist), targetPos[1], targetPos[2]))
			# parent to facialTrg_geo_grp
			cmds.parent(rBlendTarget[0], facialTrgGeoGrpName)
			cmds.setAttr('%s.visibility' %rBlendTarget[0], False)

			# initialize list variables
			baseChildList = []
			targetChildList = []
			lTargetChildList = []
			rTargetChildList = []

			baseChildList.append(baseName)
			targetChildList.append(targetName)
			lTargetChildList.append(lBlendTarget[0])
			rTargetChildList.append(rBlendTarget[0])

			# vector calculation for each geometry
			for x in xrange(len(baseChildList)):
				# get symmetrical matching vertex data
				symVtxDic, cVtxList = cls.matchSymVtx(baseChildList[x])

				for lVtxIndex in symVtxDic.keys():
					trgVtxPos = cmds.pointPosition('%s.vtx[%d]' %(targetChildList[x], lVtxIndex), local = True)
					baseVtxPos = cmds.pointPosition('%s.vtx[%d]' %(baseChildList[x], lVtxIndex), local = True)

					trgVtxVec = OpenMaya.MVector(*trgVtxPos)
					baseVtxVec = OpenMaya.MVector(*baseVtxPos)
					moveVec = trgVtxVec - baseVtxVec

					# if vertex didn't move, skip caculation
					if moveVec.length() == 0:
						continue

					# weight value calculation
					weightVal = 0.5 + (baseVtxVec.x / fallOffRange)
					if weightVal >= 1:
						weightVal = 1
					symWeightVal = 1 - weightVal


					lTrgVtxVec = baseVtxVec
					lMoveVec = moveVec * weightVal
					finalVec = lTrgVtxVec + lMoveVec

					# assign to the left blend target
					cmds.xform('%s.vtx[%d]' %(lTargetChildList[x], lVtxIndex), os = True, t = (finalVec.x, finalVec.y, finalVec.z))
					# assign to the right blend target's symmetry vertex
					cmds.xform('%s.vtx[%d]' %(rTargetChildList[x], symVtxDic[lVtxIndex]), os = True, t = (-finalVec.x, finalVec.y, finalVec.z))

					# assign to the symmetry vertex
					symVtxPos = cmds.pointPosition('%s.vtx[%d]' %(baseChildList[x], symVtxDic[lVtxIndex]), local = True)
					symVtxVec = OpenMaya.MVector(*symVtxPos)

					if 0 < abs(symVtxVec.x) <= fallOffRange:
						symMoveVec = moveVec * symWeightVal
						symFinalVec = [(symVtxVec.x + -symMoveVec.x), (symVtxVec.y + symMoveVec.y), (symVtxVec.z + symMoveVec.z)]

						# assign to the right blend target
						cmds.xform('%s.vtx[%d]' %(lTargetChildList[x], symVtxDic[lVtxIndex]), os = True, t = (symFinalVec[0], symFinalVec[1], symFinalVec[2]))
						# assign to the left blend target's symmetry vertex
						cmds.xform('%s.vtx[%d]' %(rTargetChildList[x], lVtxIndex), os = True, t = (-symFinalVec[0], symFinalVec[1], symFinalVec[2]))

				# center vertex
				for cVtxIndex in cVtxList:
					trgVtxPos = cmds.pointPosition('%s.vtx[%d]' %(targetChildList[x], cVtxIndex), local = True)
					baseVtxPos = cmds.pointPosition('%s.vtx[%d]' %(baseChildList[x], cVtxIndex), local = True)

					trgVtxVec = OpenMaya.MVector(*trgVtxPos)
					baseVtxVec = OpenMaya.MVector(*baseVtxPos)
					moveVec = trgVtxVec - baseVtxVec

					# if vertex didn't move, skip caculation
					if moveVec.length() == 0:
						continue

					cMoveVec = moveVec * 0.5

					# final center vertex position
					finalVec = baseVtxVec + cMoveVec
					cmds.xform('%s.vtx[%d]' %(lTargetChildList[x], cVtxIndex), os = True, t = (finalVec.x, finalVec.y, finalVec.z))
					cmds.xform('%s.vtx[%d]' %(rTargetChildList[x], cVtxIndex), os = True, t = (finalVec.x, finalVec.y, finalVec.z))

			# add left and right targets to the blend shape
			for target in lrTargets:
				# bsIndex =cmds.blendShape(cls.bsNodeName, q = True, weightCount = True)
				# if bsIndex >= 2:
				# 	bsIndex += 1
				bsAttrList = cmds.aliasAttr(cls.bsNodeName, q=True)
				weightNumList = []
				for bsAttr in bsAttrList:
					if 'weight' in bsAttr:
						reObj = re.search(r'\d+', bsAttr)
						weightNum = reObj.group()
						weightNumList.append(int(weightNum))
				bsIndex = max(weightNumList) + 1

				cmds.blendShape(cls.bsNodeName, edit = True, target = (cls.skinGeo, bsIndex, target, 1.0))
				#cmds.setAttr('%s.%s' %(cls.bsNodeName, target), 1)

		# set all deformer of skin geometry envelop to 1
		cmds.setAttr('%s.envelope' %cls.skinCluster, 1)
		allConnections = cmds.listHistory(cls.skinGeo)
		for item in allConnections:
			if cmds.objectType(item) in cls.deformerList:
				cmds.setAttr('%s.envelope' %item, 1)

		cls.populateFacialTrgList()


	@staticmethod
	def getMaxXPos(base):
		maxXPos = 0
		numOfVtx = cmds.polyEvaluate(base, v = True)
		for i in xrange(numOfVtx):
			vtxPos = cmds.pointPosition('{0}.vtx[{1}]'.format(base, i), local = True)
			if vtxPos[0] > maxXPos:
				maxXPos = vtxPos[0]
		return maxXPos


	# function for match symmetry vertex
	@staticmethod
	def matchSymVtx(geomtry):
		# get number of vertex
		numOfVtx = cmds.polyEvaluate(geomtry, v = True)

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

		# get symmetry vertex tolerance value for find matching right side symmetry vertex
		symVtxTol = 0.01

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


	@classmethod
	def mergeTrg(cls, *args):
		# merged target name
		selTrgList = cmds.textScrollList(UI.widgets['facialTrgTxtScrList'], q = True, selectItem = True)
		joinStr = '_'
		selTrgNameList = []
		for selTrg in selTrgList:
			selTrgNameList.append(selTrg.rsplit('_ftrg')[0])
		merTrgName =  joinStr.join(selTrgNameList) + '_mrg_ftrg'

		# set all deformer of skin geometry envelop to 0
		cls.getSkinCluster()
		cmds.setAttr('%s.envelope' %cls.skinCluster, 0)
		allConnections = cmds.listHistory(cls.skinGeo)
		for item in allConnections:
			if cmds.objectType(item) in cls.deformerList:
				cmds.setAttr('%s.envelope' %item, 0)

		# duplicate skin geometry to get merged target
		cmds.duplicate(cls.skinGeo, n = merTrgName)
		# delete intermediate shape	
		shapList = cmds.ls(merTrgName, dag = True, s = True)
		for shap in shapList:
			if cmds.getAttr('%s.intermediateObject' %(shap)): 
				cmds.delete(shap)

		# get vertex number
		numOfVtx = cmds.polyEvaluate(cls.skinGeo, v = True)

		# for each target in selected targets
		finDeltaDic = {}
		trgCounter = 0
		for trg in selTrgList:
			# for each vertex of target
			for i in xrange(numOfVtx):
				# get delta between target geometry vertex position and merge target vertex position
				trgVtxPos = cmds.pointPosition('%s.vtx[%d]' %(trg, i), local = True)
				trgVtxVec = OpenMaya.MVector(*trgVtxPos)
				mrgTrgVtxPos = cmds.pointPosition('%s.vtx[%d]' %(merTrgName, i), local = True)
				mrgTrgVtxVec = OpenMaya.MVector(*mrgTrgVtxPos)
				
				delta = trgVtxVec - mrgTrgVtxVec

				# initialize finDeltaDic
				if trgCounter == 0:
					finDeltaDic[i] = delta

				# if vertex didn't move, skip caculation
				if delta.length() == 0:
					continue

				# sum to the final delta dictionary
				if trgCounter != 0:
					finDeltaDic[i] += delta

			trgCounter += 1

		# set final vertex position
		for i in xrange(numOfVtx):
			mrgTrgVtxPos = cmds.pointPosition('%s.vtx[%d]' %(merTrgName, i), local = True)
			mrgTrgVtxVec = OpenMaya.MVector(*mrgTrgVtxPos)

			# add delta to merged target vertex position
			finVec = mrgTrgVtxVec + finDeltaDic[i]

			# set merged target vertex position
			cmds.xform('%s.vtx[%d]' %(merTrgName, i), os = True, t = (finVec.x, finVec.y, finVec.z))

		# set all deformer of skin geometry envelop to 0
		cmds.setAttr('%s.envelope' %cls.skinCluster, 1)
		allConnections = cmds.listHistory(cls.skinGeo)
		for item in allConnections:
			if cmds.objectType(item) in cls.deformerList:
				cmds.setAttr('%s.envelope' %item, 1)

		facialTrgGeoGrpName = cls.skinGeo + '_facialTrg_geo_grp'
		# parent to facialTrg_geo_grp
		cmds.parent(merTrgName, facialTrgGeoGrpName)
		cmds.setAttr('%s.visibility' %merTrgName, False)

		# add to blend shape node
		bsAttrList = cmds.aliasAttr(cls.bsNodeName, q=True)
		weightNumList = []
		for bsAttr in bsAttrList:
			if 'weight' in bsAttr:
				reObj = re.search(r'\d+', bsAttr)
				weightNum = reObj.group()
				weightNumList.append(int(weightNum))
		bsIndex = max(weightNumList) + 1

		cmds.blendShape(cls.bsNodeName, edit = True, target = (cls.skinGeo, bsIndex, merTrgName, 1.0))
		cmds.setAttr('%s.%s' %(cls.bsNodeName, merTrgName), 1)

		# refresh facial target list
		cls.populateFacialTrgList()


	@classmethod
	def flip(cls, *args):
		selTrgList = cmds.textScrollList(UI.widgets['facialTrgTxtScrList'], q = True, selectItem = True)

		# set all deformer of skin geometry envelop to 0
		cls.getSkinCluster()
		cmds.setAttr('%s.envelope' %cls.skinCluster, 0)
		allConnections = cmds.listHistory(cls.skinGeo)
		for item in allConnections:
			if cmds.objectType(item) in cls.deformerList:
				cmds.setAttr('%s.envelope' %item, 0)

		symVtxDic, cVtxList = cls.matchSymVtx(cls.skinGeo)
		for selTrg in selTrgList:
			for lVtxIndex in symVtxDic.keys():
				# get left and right vertex position
				lVtxPos = cmds.pointPosition('%s.vtx[%d]' %(selTrg, lVtxIndex), local = True)
				rVtxPos = cmds.pointPosition('%s.vtx[%d]' %(selTrg, symVtxDic[lVtxIndex]), local = True)

				# change lVtxPos and rVtxPos
				lVtxPos, rVtxPos = (-rVtxPos[0], rVtxPos[1], rVtxPos[2]), (-lVtxPos[0], lVtxPos[1], lVtxPos[2])

				# set vertex position
				cmds.xform('%s.vtx[%d]' %(selTrg, lVtxIndex), os = True, t = lVtxPos)
				cmds.xform('%s.vtx[%d]' %(selTrg, symVtxDic[lVtxIndex]), os = True, t = rVtxPos)

		# set all deformer of skin geometry envelop to 1
		cmds.setAttr('%s.envelope' %cls.skinCluster, 1)
		allConnections = cmds.listHistory(cls.skinGeo)
		for item in allConnections:
			if cmds.objectType(item) in cls.deformerList:
				cmds.setAttr('%s.envelope' %item, 1)
		cmds.select(cl = True)


	@classmethod
	def mirror(cls, *args):
		mirOpt = cmds.confirmDialog(title = 'Mirror Option', message = 'What do you want?', button = ['x to -x', '-x to x'], defaultButton = 'Cancel', cancelButton = 'Cancel', dismissString = 'Cancel' )
		if mirOpt == 'Cancel':
			return
		selTrgList = cmds.textScrollList(UI.widgets['facialTrgTxtScrList'], q = True, selectItem = True)

		# set all deformer of skin geometry envelop to 0
		cls.getSkinCluster()
		cmds.setAttr('%s.envelope' %cls.skinCluster, 0)
		allConnections = cmds.listHistory(cls.skinGeo)
		for item in allConnections:
			if cmds.objectType(item) in cls.deformerList:
				cmds.setAttr('%s.envelope' %item, 0)

		symVtxDic, cVtxList = cls.matchSymVtx(cls.skinGeo)
		for selTrg in selTrgList:
			for lVtxIndex in symVtxDic.keys():
				if mirOpt == 'x to -x':
					lVtxPos = cmds.pointPosition('%s.vtx[%d]' %(selTrg, lVtxIndex), local = True)
					cmds.xform('%s.vtx[%d]' %(selTrg, symVtxDic[lVtxIndex]), os = True, t = (-lVtxPos[0], lVtxPos[1], lVtxPos[2]))
				elif mirOpt == '-x to x':
					lVtxPos = cmds.pointPosition('%s.vtx[%d]' %(selTrg, symVtxDic[lVtxIndex]), local = True)
					cmds.xform('%s.vtx[%d]' %(selTrg, lVtxIndex), os = True, t = (-lVtxPos[0], lVtxPos[1], lVtxPos[2]))

		# set all deformer of skin geometry envelop to 1
		cmds.setAttr('%s.envelope' %cls.skinCluster, 1)
		allConnections = cmds.listHistory(cls.skinGeo)
		for item in allConnections:
			if cmds.objectType(item) in cls.deformerList:
				cmds.setAttr('%s.envelope' %item, 1)
		cmds.select(cl = True)


	@staticmethod
	def loadDriver(*args):
		drvrs = cmds.scrollLayout(UI.widgets['sdkDrvrSclLo'], q = True, childArray = True)
		if drvrs:
			for drvr in drvrs:
				cmds.deleteUI(drvr)
		sel = cmds.ls(sl = True)[0]
		SdkObject(UI.widgets['sdkDrvrSclLo'], sel, 'driver')


	@staticmethod
	def loadDriven(*args):
		drvns = cmds.scrollLayout(UI.widgets['sdkDrvnSclLo'], q = True, childArray = True)
		if drvns:
			for drvn in drvns:
				cmds.deleteUI(drvn)
		selList = cmds.ls(sl = True)
		for sel in selList:
			SdkObject(UI.widgets['sdkDrvnSclLo'], sel, 'driven')


	@staticmethod
	def addDriven(*args):
		sel = cmds.ls(sl = True)[0]
		SdkObject(UI.widgets['sdkDrvnSclLo'], sel, 'driven')


	@staticmethod
	def sdk(*args):
		driverVals = []
		# get driver data
		drvrObj = cmds.scrollLayout(UI.widgets['sdkDrvrSclLo'], q = True, childArray = True)
		drvrElem = cmds.rowColumnLayout(drvrObj, q = True, childArray = True)
		drvrName = cmds.text(drvrElem[0], q = True, label = True)
		drvrAttrName = cmds.optionMenu(drvrElem[1], q = True, value = True)
		drvrStartVal = cmds.textField(drvrElem[2], q = True, text = True)
		driverVals.append(drvrStartVal)
		drvrEndVal = cmds.textField(drvrElem[3], q = True, text = True)
		driverVals.append(drvrEndVal)

		# get drivens data
		drvnObjs = cmds.scrollLayout(UI.widgets['sdkDrvnSclLo'], q = True, childArray = True)
		drvnElems = []		
		for drvnObj in drvnObjs:
			drvnElem = cmds.rowColumnLayout(drvnObj, q = True, childArray = True)
			drvnElems.append(tuple(drvnElem))
		drvnDatas = []
		for drvnElem in drvnElems:
			drvnElemBuffer = []
			drvnName = cmds.text(drvnElem[0], q = True, label = True)
			drvnElemBuffer.append(drvnName)
			drvnAttrName = cmds.optionMenu(drvnElem[1], q = True, value = True)
			drvnElemBuffer.append(drvnAttrName)
			drvnStartVal = cmds.textField(drvnElem[2], q = True, text = True)
			drvnElemBuffer.append(drvnStartVal)
			drvnEndVal = cmds.textField(drvnElem[3], q = True, text = True)
			drvnElemBuffer.append(drvnEndVal)
			drvnDatas.append(tuple(drvnElemBuffer))

		# set driven key
		for drvnData in drvnDatas:
			j = 2
			for i in xrange(2):
				cmds.setDrivenKeyframe('%s.%s' %(drvnData[0], drvnData[1]), cd = '%s.%s' %(drvrName, drvrAttrName), dv = float(driverVals[i]), v = float(drvnData[j]))
				j += 1


	@classmethod
	def onFaceCtrl(cls, *args):
		selVtxList = cmds.ls(sl = True)

		# set all deformer of skin geometry envelop to 0
		cls.getSkinCluster()
		cmds.setAttr('%s.envelope' %cls.skinCluster, 0)
		allConnections = cmds.listHistory(cls.skinGeo)
		for item in allConnections:
			if cmds.objectType(item) in cls.deformerList:
				cmds.setAttr('%s.envelope' %item, 0)

		if cmds.checkBox(UI.widgets['onFaceCtrlSymChkbox'], q = True, v = True):

			symVtxDic, cVtxList = cls.matchSymVtx(cls.skinGeo)

			selGeoName = re.search(r'(.+).vtx\[(\d+)\]', selVtxList[0]).group(1)
			selVtxIndex = re.search(r'(.+).vtx\[(\d+)\]', selVtxList[0]).group(2)

			symVtxIndex = symVtxDic[int(selVtxIndex)]

			selVtxList.append('%s.vtx[%d]' %(selGeoName, symVtxIndex))

		for selVtx in selVtxList:
			cmds.select(selVtx, r = True)

			# convert soft selection to cluster
			softClstObj = softClusterEX.GUI()
			clstNode, clstHandle = softClstObj.createSoftClusterCmd()
			cmds.deleteUI(softClstObj.window)
			cmds.setAttr('%s.visibility' %(clstHandle), False)

			# create follicle on a vertex
			selVtxMap = cmds.polyListComponentConversion(selVtx, tuv = True)
			selVtxUV = cmds.polyEditUV(selVtxMap, q = True, u = True, v = True)

			fol = cmds.createNode('follicle')
			mesh = selVtx.rsplit('.')[0]
			cmds.select(fol, r = True)
			cmds.pickWalk(direction = 'up')
			folPrnt = cmds.ls(sl = True)[0]

			cmds.connectAttr('{0}.outMesh'.format(mesh), '{0}.inputMesh'.format(fol))
			cmds.connectAttr('{0}.worldMatrix'.format(mesh), '{0}.inputWorldMatrix'.format(fol))
			cmds.connectAttr('{0}.outTranslate'.format(fol), '{0}.translate'.format(folPrnt))
			#cmds.connectAttr('{0}.outRotate'.format(fol), '{0}.rotate'.format(folPrnt))
			cmds.setAttr('{0}.parameterU'.format(fol), selVtxUV[0])
			cmds.setAttr('{0}.parameterV'.format(fol), selVtxUV[1])
			cmds.setAttr('%s.visibility' %(fol), False)


			# create control curve
			ctrlCrvName = cmds.createNode('transform', n = 'onFaceCtrl#')
			crvList = []
			crvList.append(cmds.curve( d = 3,p = [[5.3290705182007512e-17, 6.123233995736766e-17, -1.0], [-0.26120387496374148, 6.123233995736766e-17, -1.0], [-0.78361162489122427, 4.7982373409884707e-17, -0.78361162489122427], [-1.1081941875543879, 1.9663354616187859e-32, -3.2112695072372299e-16], [-0.78361162489122449, -4.7982373409884701e-17, 0.78361162489122405], [-3.3392053635905195e-16, -6.7857323231109146e-17, 1.1081941875543881], [0.78361162489122382, -4.7982373409884713e-17, 0.78361162489122438], [1.1081941875543879, -3.6446300679047921e-32, 5.9521325992805852e-16], [0.78361162489122504, 4.7982373409884682e-17, -0.78361162489122382], [0.26120387496374164, 6.123233995736766e-17, -0.99999999999999978], [8.8817841970012528e-17, 6.123233995736766e-17, -0.99999999999999989]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
			crvList.append(cmds.curve( d = 3,p = [[5.3290705182007512e-17, 1.0, 0.0], [-0.26120387496374148, 1.0, 0.0], [-0.78361162489122427, 0.78361162489122427, 0.0], [-1.1081941875543879, 3.2112695072372299e-16, 0.0], [-0.78361162489122449, -0.78361162489122405, 0.0], [-3.3392053635905195e-16, -1.1081941875543881, 0.0], [0.78361162489122382, -0.78361162489122438, 0.0], [1.1081941875543879, -5.9521325992805852e-16, 0.0], [0.78361162489122504, 0.78361162489122382, 0.0], [0.26120387496374164, 0.99999999999999978, 0.0], [8.8817841970012528e-17, 0.99999999999999989, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
			crvList.append(cmds.curve( d = 3,p = [[1.9721522630525296e-33, 1.0, -5.3290705182007512e-17], [-1.5994124469961577e-17, 1.0, 0.26120387496374148], [-4.7982373409884707e-17, 0.78361162489122427, 0.78361162489122427], [-6.7857323231109134e-17, 3.2112695072372299e-16, 1.1081941875543879], [-4.7982373409884731e-17, -0.78361162489122405, 0.78361162489122449], [-2.0446735801084019e-32, -1.1081941875543881, 3.3392053635905195e-16], [4.7982373409884682e-17, -0.78361162489122438, -0.78361162489122382], [6.7857323231109134e-17, -5.9521325992805852e-16, -1.1081941875543879], [4.7982373409884762e-17, 0.78361162489122382, -0.78361162489122504], [1.5994124469961583e-17, 0.99999999999999978, -0.26120387496374164], [4.9303806576313241e-33, 0.99999999999999989, -8.8817841970012528e-17]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
			for crv in crvList:
				cmds.delete(crv, ch = True)
				crvShp = cmds.listRelatives(crv, s = True)
				cmds.parent(crvShp, ctrlCrvName, s = True, r = True)
				cmds.delete(crv)

			prntNameList = ['orient', 'reverse']
			for prntName in prntNameList:
				cmds.select(ctrlCrvName, r = True)
				prnt = cmds.duplicate(n = '%s_%s' %(ctrlCrvName, prntName), po=True)
				cmds.parent(ctrlCrvName, prnt)
			cmds.parent('{0}_{1}'.format(ctrlCrvName, prntNameList[0]), folPrnt)

			attrList = ['translateX', 'translateY', 'translateZ']
			for attr in attrList:
				cmds.setAttr('{0}.{1}'.format('{0}_{1}'.format(ctrlCrvName, prntNameList[0]), attr), 0)

			mulNode = cmds.shadingNode('multiplyDivide', asUtility = True, n = 'onFaceCtrl#_mul')
			inputList = ['input2X', 'input2Y', 'input2Z']
			for input in inputList:
				cmds.setAttr('{0}.{1}'.format(mulNode, input), -1)
			cmds.connectAttr('{0}.translate'.format(ctrlCrvName), '{0}.input1'.format(mulNode), f = True)
			cmds.connectAttr('{0}.output'.format(mulNode), '{0}.translate'.format('{0}_{1}'.format(ctrlCrvName, prntNameList[1])), f = True)
			cmds.connectAttr('{0}.translate'.format(ctrlCrvName), '{0}.translate'.format(clstHandle), f = True)
			cmds.connectAttr('{0}.rotate'.format(ctrlCrvName), '{0}.rotate'.format(clstHandle), f = True)
			cmds.connectAttr('{0}.scale'.format(ctrlCrvName), '{0}.scale'.format(clstHandle), f = True)

			# reoerder deformers
			skinClst = cls.getSkinCluster()
			cmds.reorderDeformers(skinClst, clstNode, cls.skinGeo)

			# clean up outliner
			if not cmds.objExists('onFaceCtrl_grp'):
				cmds.createNode('transform', n = 'onFaceCtrl_grp')
			ctrlCrvGrp = cmds.createNode('transform', n = '%s_grp' %(ctrlCrvName))
			cmds.parent(clstHandle, folPrnt, ctrlCrvGrp)
			cmds.parent(ctrlCrvGrp, 'onFaceCtrl_grp')

		# set all deformer of skin geometry envelop to 1
		cls.getSkinCluster()
		cmds.setAttr('%s.envelope' %cls.skinCluster, 1)
		allConnections = cmds.listHistory(cls.skinGeo)
		for item in allConnections:
			if cmds.objectType(item) in cls.deformerList:
				cmds.setAttr('%s.envelope' %item, 1)



class SdkObject(object):
	sdkWidgets = {}

	def __init__(self, layout, selObj, sdkType):
		self.prntLayout = layout
		self.selObj = selObj
		self.sdkType = sdkType
		self.ui()
		self.popSdkOptMenu()


	def ui(self):
		self.sdkWidgets[self.selObj + 'sdkRowColLo'] = cmds.rowColumnLayout(w = 400, numberOfColumns = 4, columnWidth = [(1, 100), (2, 170), (3, 65), (4, 60)], columnOffset = [(1, 'left', 5), (3, 'left', 25), (4, 'left', 20)], columnAttach = [(4, 'right', 5)], p = self.prntLayout)
		self.sdkWidgets[self.selObj + 'sdkTxt'] = cmds.text(label = self.selObj)
		self.sdkWidgets[self.selObj + 'sdkOptMenu'] = cmds.optionMenu()
		self.sdkWidgets[self.selObj + 'sdkSartTxtFld'] = cmds.textField(text = 0)
		self.sdkWidgets[self.selObj + 'sdkEndTxtFld'] = cmds.textField(text = 0)
		if self.sdkType == 'driver':
			cmds.textField(self.sdkWidgets[self.selObj + 'sdkEndTxtFld'], e = True, text = 10)
		elif self.sdkType == 'driven':
			cmds.textField(self.sdkWidgets[self.selObj + 'sdkEndTxtFld'], e = True, text = 1)


	def popSdkOptMenu(self):
		if cmds.objectType(self.selObj) == 'blendShape':
			attrList = cmds.listAttr('%s.w' %(self.selObj), multi = True)
		else:
			attrList = cmds.listAttr(self.selObj, k = True)
		for attr in attrList:
			cmds.menuItem(label = attr, p = self.sdkWidgets[self.selObj + 'sdkOptMenu'])