'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date: 2015.07.23

Description:
This script can correct cached geometry.

Usage:
import tak_cacheCorrect
reload(tak_cacheCorrect)
tak_cacheCorrect.UI()
'''

import maya.cmds as cmds
import maya.mel as mel
from functools import partial
import re
import tak_lib

class UI(object):
	widgets = {}
	winName = 'takCacheCorrectUI'


	@classmethod
	def __init__(cls):
		if cmds.window(cls.winName, exists = True):
			cmds.deleteUI(cls.winName)

		cls.ui()


	@classmethod
	def ui(cls):
		cmds.window(cls.winName, title = 'Cache Correct Tool', menuBar = True)

		cls.widgets['createMenu'] = cmds.menu(label = 'Create', tearOff = True, p = cls.winName)
		cls.widgets['addBsMenuItem'] = cmds.menuItem(label = 'Add Blend Shape Node', c = Functions.addBsNode)

		cls.widgets['editMenu'] = cmds.menu(label = 'Edit', tearOff = True, p = cls.winName)
		cls.widgets['selBsMenuItem'] = cmds.menuItem(label = 'Select Blend Shape Node', c = Functions.selBsNode)

		cls.widgets['helpMenu'] = cmds.menu(label = 'Help', tearOff = True, p = cls.winName)

		cls.widgets['mainColLo'] = cmds.columnLayout(adj = True)

		cmds.separator(h = 5, p = cls.widgets['mainColLo'])
		
		cls.widgets['cacheGeoRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 3)
		cmds.text(label = 'Cache Geometry: ', p = cls.widgets['cacheGeoRowColLo'])
		cls.widgets['cacheGeoTxtFld'] = cmds.textField(p = cls.widgets['cacheGeoRowColLo'])
		cmds.button(label = '<<', p = cls.widgets['cacheGeoRowColLo'], c = Functions.loadGeoBS)

		cls.widgets['bsNodeRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 2, p = cls.widgets['mainColLo'])
		cmds.text(label = 'Blend Shape Node: ', p = cls.widgets['bsNodeRowColLo'])
		cls.widgets['bsNodeOptMenu'] = cmds.optionMenu(cc = Functions.populateCorrectiveTrgList, p = cls.widgets['bsNodeRowColLo'])

		cmds.separator(h = 10, style = 'in', p = cls.widgets['mainColLo'])

		cls.widgets['correctiveTrgNameRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 4, columnSpacing = [(3, 30)], p = cls.widgets['mainColLo'])
		cmds.text(label = 'New Corrective: ', p = cls.widgets['correctiveTrgNameRowColLo'])
		cls.widgets['correctiveTrgNameTxtFld'] = cmds.textField(p = cls.widgets['correctiveTrgNameRowColLo'])


		cls.widgets['scltBtnRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 2, columnWidth = [(1, 205), (2, 205)], columnSpacing = [(2, 5)], p = cls.widgets['mainColLo'])
		cls.widgets['sculptBtn'] = cmds.button(label = 'Sculpt', p = cls.widgets['scltBtnRowColLo'], c = Functions.sculptMode)
		cls.widgets['cancelBtn'] = cmds.button(label = 'Cancel', p = cls.widgets['scltBtnRowColLo'], c = Functions.cancelSculpt, enable = False)
		cls.widgets['createBtn'] = cmds.button(label = 'Create', h = 40, p = cls.widgets['mainColLo'], c = Functions.createCorrectiveTarget, enable = False)

		cmds.separator(h = 5, style = 'none', p = cls.widgets['mainColLo'])

		cls.widgets['correctiveTrgFrmLo'] = cmds.frameLayout(label = 'Corrective List', collapsable = True, p = cls.widgets['mainColLo'])
		cls.widgets['correctiveTrgColLo'] = cmds.columnLayout(adj = True, p = cls.widgets['correctiveTrgFrmLo'])
		cls.widgets['correctiveTrgTxtScrList'] = cmds.textScrollList(allowMultiSelection = True, p = cls.widgets['correctiveTrgColLo'])
		cmds.popupMenu()
		cmds.menuItem(label = 'Refresh List', c = Functions.populateCorrectiveTrgList)
		cls.widgets['popMenuRename'] = cmds.menuItem(label = 'Rename', c = Functions.rename)
		cls.widgets['popMenuBreak'] = cmds.menuItem(label = 'Delete Key', c = Functions.delKey)
		cls.widgets['popMenuRmv'] = cmds.menuItem(label = 'Remove', c = Functions.removeTrg)
		cls.widgets['slderRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 2, columnWidth = [(1, 370)], p = cls.widgets['correctiveTrgColLo'])
		cls.widgets['trgFltSldrGrp'] = cmds.floatSliderGrp(field = True, columnWidth = [(1, 30)], min = 0.00, max = 1.00, step = 0.01, dc = Functions.trgSldrDragCmd, cc = Functions.trgSldrDragCmd, enable = True, p = cls.widgets['slderRowColLo'])
		cmds.symbolButton(image = 'setKeyframe.png', c = Functions.setKey, p = cls.widgets['slderRowColLo'])

		cmds.window(cls.winName, e = True, w = 400, h = 300)
		cmds.showWindow(cls.winName)



class Functions(object):
	cacheGeo = ''
	bsNodeName = ''
	deformerList = ['blendShape', 'cluster', 'ffd', 'wrap', 'nonLinear', 'sculpt', 'softMod', 'jiggle', 'wire']


	@classmethod
	def loadGeoBS(cls, *args):
		cls.cacheGeo = cmds.ls(sl = True)[0]
		if not cmds.nodeType(cls.cacheGeo) == 'transform':
			cmds.error('Please select cache geometry.')
		cmds.textField(UI.widgets['cacheGeoTxtFld'], e = True, text = cls.cacheGeo)

		# load BS nodes
		cls.bsList = []

		# If cacheGeo is group, gather all blend shape node for child meshes.
		if cmds.listRelatives(cls.cacheGeo, c = True, type = 'transform'):
			allChldGeo = cmds.listRelatives(cls.cacheGeo, ad = True, type = 'mesh')
			for chldGeo in allChldGeo:
				try:
					allConnections = cmds.listHistory(chldGeo)
					for item in allConnections:
						if cmds.objectType(item) == 'blendShape':
							cls.bsList.append(item)
				except:
					pass
			# Remove repeated item.
			cls.bsList = list(set(cls.bsList))
		else:
			bsNode = cmds.ls(cmds.listHistory(cls.cacheGeo, levels = 2), type = 'blendShape')
			if bsNode:
				cls.bsList.append(bsNode[0])


		# if already exists menu item in the bsOptMenu, delete menu items before populate
		bsOptItems = cmds.optionMenu(UI.widgets['bsNodeOptMenu'], q = True, itemListLong = True)
		if bsOptItems != None:
			for bsOptItem in bsOptItems:
				cmds.deleteUI(bsOptItem)

		if cls.bsList:
			for bsNode in cls.bsList:
				cmds.menuItem(label = bsNode, p = UI.widgets['bsNodeOptMenu'])
		elif not cls.bsList:
			cmds.menuItem(label = 'None', p = UI.widgets['bsNodeOptMenu'])

		cls.populateCorrectiveTrgList()


	@classmethod
	def addBsNode(cls, *args):
		if cls.isBsNode():
			cmds.confirmDialog(title = 'Error', message = "Blendshape is already applied.\nSelect a existing blendshape node.", button = 'OK')
			return False

		bsNode = cmds.blendShape(cls.cacheGeo, frontOfChain = True)[0]
		bsOptItems = cmds.optionMenu(UI.widgets['bsNodeOptMenu'], q = True, itemListLong = True)
		if bsOptItems != None:
			for bsOptItem in bsOptItems:
				cmds.deleteUI(bsOptItem)
		cmds.menuItem(label = bsNode, p = UI.widgets['bsNodeOptMenu'])

		cls.bsNodeName = cmds.optionMenu(UI.widgets['bsNodeOptMenu'], q = True, v = True)

		cls.populateCorrectiveTrgList()


	@classmethod
	def isBsNode(cls):
		'''
		Cheking whether blendshape node is already applied to the mesh.
		'''

		bsNode = cmds.ls(cmds.listHistory(cls.cacheGeo, levels = 2), type = 'blendShape')

		if bsNode:
			return True
		else:
			return False


	@classmethod
	def selBsNode(cls, *args):
		cmds.select(cls.bsNodeName, r = True)


	@classmethod
	def sculptMode(cls, *args):
		# Get corrective name
		cls.correctiveTrgName = cmds.textField(UI.widgets['correctiveTrgNameTxtFld'], q = True, text = True)

		# Check if already exists same corrective name
		if cmds.objExists(cls.correctiveTrgName):
			cmds.confirmDialog(title = 'Warning', message = "'%s' is already exists.\nTry another corrective name." %(cls.correctiveTrgName), button = 'OK')
			cmds.textField(UI.widgets['correctiveTrgNameTxtFld'], e = True, text = '')
			return

		# If cache geometry has no blend shape node add one
		if cls.bsNodeName == 'None':
			cls.addBsNode()

		# Duplicate cache geometry twice
		cls.sculptGeo = cmds.duplicate(cls.cacheGeo, n = cls.correctiveTrgName)[0]
		cls.invGeo = cmds.duplicate(cls.cacheGeo, n = cls.correctiveTrgName + '_inv')[0]

		# Delete intermediate shape
		for geo in [cls.sculptGeo, cls.invGeo]:
			shapList = cmds.ls(geo, dag = True, s = True)
			for shap in shapList:
				if cmds.getAttr('%s.intermediateObject' %(shap)): 
					cmds.delete(shap)

		# Display HUD
		if cmds.headsUpDisplay('sclptHUD', exists = True):
			cmds.headsUpDisplay('sclptHUD', remove = True)
		tak_lib.showHUD('sclptHUD', 'Sculpt Mode')

		# Button enable control
		cmds.button(UI.widgets['sculptBtn'], e = True, enable = False)
		cmds.button(UI.widgets['cancelBtn'], e = True, enable = True)
		cmds.button(UI.widgets['createBtn'], e = True, enable = True)

		# Hide cache geometry and invGeo
		cls.shpVisOnOff(cls.cacheGeo, 'off')
		cls.shpVisOnOff(cls.invGeo, 'off')


	@classmethod
	def cancelSculpt(cls, *args):
		cmds.headsUpDisplay('sclptHUD', remove = True)
		cmds.delete(cls.sculptGeo)
		cmds.delete(cls.invGeo)
		cls.shpVisOnOff(cls.cacheGeo, 'off')

		# Button enable control
		cmds.button(UI.widgets['sculptBtn'], e = True, enable = True)
		cmds.button(UI.widgets['cancelBtn'], e = True, enable = False)
		cmds.button(UI.widgets['createBtn'], e = True, enable = False)


	@classmethod
	def createCorrectiveTarget(cls, *args):
		# Check working uint
		curUnit = cmds.currentUnit(q = True, linear = True)
		if curUnit != 'cm':
			cmds.currentUnit(linear = 'cm')

		# Remove HUD
		cmds.headsUpDisplay('sclptHUD', remove = True)

		# Refresh new corrective name text field
		cmds.textField(UI.widgets['correctiveTrgNameTxtFld'], e = True, text = '')

		# Show cache geometry and inverse geometry shape.
		cls.shpVisOnOff(cls.cacheGeo, 'on')
		cls.shpVisOnOff(cls.invGeo, 'on')

		# Add invGeo and sculptGeo to blendshape node
		for cls.correctiveTrgName in [cls.sculptGeo, cls.invGeo]:
			if cls.bsNodeName != 'None':
				bsAttrList = cmds.aliasAttr(cls.bsNodeName, q=True)
				if not bsAttrList:
					cmds.blendShape(cls.bsNodeName, edit = True, target = (cls.cacheGeo, 0, cls.correctiveTrgName, 1.0))
					cmds.setAttr('%s.%s' %(cls.bsNodeName, cls.correctiveTrgName), 1)
				else:
					weightNumList = []
					for bsAttr in bsAttrList:
						if 'weight' in bsAttr:
							reObj = re.search(r'\d+', bsAttr)
							weightNum = reObj.group()
							weightNumList.append(int(weightNum))
					bsIndex = max(weightNumList) + 1

					cmds.blendShape(cls.bsNodeName, edit = True, target = (cls.cacheGeo, bsIndex, cls.correctiveTrgName, 1.0))
					cmds.setAttr('%s.%s' %(cls.bsNodeName, cls.correctiveTrgName), 1)
			elif cls.bsNodeName == 'None':
				cls.bsNodeName = '{0}_correctiveBS'.format(cls.cacheGeo)
				cmds.blendShape(cls.correctiveTrgName, cls.cacheGeo, n = cls.bsNodeName, frontOfChain = True)[0]
				cmds.setAttr('%s.%s' %(cls.bsNodeName, cls.correctiveTrgName), 1)

				# Fill blend shape node option menu
				# Load BS nodes
				cls.bsList = []
				allConnections = cmds.listHistory(cls.cacheGeo)
				for item in allConnections:
					if cmds.objectType(item) == 'blendShape':
						cls.bsList.append(item)

				# If already exists menu item in the bsOptMenu, delete menu items before populate
				bsOptItems = cmds.optionMenu(UI.widgets['bsNodeOptMenu'], q = True, itemListLong = True)
				if bsOptItems != None:
					for bsOptItem in bsOptItems:
						cmds.deleteUI(bsOptItem)
				if cls.bsList:
					for bsNode in cls.bsList:
						cmds.menuItem(label = bsNode, p = UI.widgets['bsNodeOptMenu'])

		# Build node network for inverse target
		mulNode = cmds.shadingNode('multiplyDivide', n = cls.sculptGeo + '_mul', asUtility = True)
		cmds.setAttr('%s.input2X' %mulNode, -1)
		cmds.connectAttr('%s.%s' %(cls.bsNodeName, cls.sculptGeo), '%s.input1X' %mulNode)
		cmds.connectAttr('%s.outputX' %mulNode, '%s.%s' %(cls.bsNodeName, cls.invGeo))
		
		# Add corrective and inverse target geometry to geo_grp
		correctiveTrgGeoGrpName = cls.cacheGeo + '_correctiveTrg_geo_grp'
		if cmds.objExists(correctiveTrgGeoGrpName):
			cmds.parent(cls.sculptGeo, correctiveTrgGeoGrpName)
			cmds.parent(cls.invGeo, correctiveTrgGeoGrpName)
		else:
			cmds.createNode('transform', n = correctiveTrgGeoGrpName)
			cmds.parent(cls.sculptGeo, correctiveTrgGeoGrpName)
			cmds.parent(cls.invGeo, correctiveTrgGeoGrpName)
		# Visibility off for sculpt and inverse geo shapes.
		cls.shpVisOnOff(cls.sculptGeo, 'off')
		cls.shpVisOnOff(cls.invGeo, 'off')

		# Refresh corrective target list
		cls.populateCorrectiveTrgList()

		# Return working unit
		cmds.currentUnit(linear = curUnit)

		# Button enable control
		cmds.button(UI.widgets['sculptBtn'], e = True, enable = True)
		cmds.button(UI.widgets['cancelBtn'], e = True, enable = False)
		cmds.button(UI.widgets['createBtn'], e = True, enable = False)


	@classmethod
	def populateCorrectiveTrgList(cls, *args):
		cls.bsNodeName = cmds.optionMenu(UI.widgets['bsNodeOptMenu'], q = True, v = True)
		bsTrgList = []

		if cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, allItems = True):
			cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], e = True, removeAll = True)

		if cls.bsNodeName != 'None':
			bsTrgList = cmds.listAttr('%s.w' %(cls.bsNodeName), multi = True)
			if bsTrgList:
				for bsTrg in bsTrgList:
					if '_inv' in bsTrg:
						bsTrgList.remove(bsTrg)
				bsTrgList.sort()
				cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], e = True, append = bsTrgList)
				# set bold font to connected targets
				for i in xrange(len(bsTrgList)):
					if cmds.listConnections('{0}.{1}'.format(cls.bsNodeName, bsTrgList[i]), source = True, destination = False):
						cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], e = True, lineFont = (i + 1, 'boldLabelFont'))


	@classmethod
	def trgSldrDragCmd(cls, *args):
		trgSldrVal = cmds.floatSliderGrp(UI.widgets['trgFltSldrGrp'], q = True, v = True)
		selTrgList = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, selectItem = True)
		if selTrgList:
			for selTrg in selTrgList:
				try:
					cmds.setAttr('{0}.{1}'.format(cls.bsNodeName, selTrg), trgSldrVal)
				except:
					pass


	@classmethod
	def rename(cls, *args):
		selTrg = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, selectItem = True)[0]
		result = cmds.promptDialog(title = 'Rename Blend Target', message = 'New Blend Target Name', text = selTrg, button = ['OK', 'Cancel'], defaultButton = 'OK', cancelButton = 'Cancel', dismissString = 'Cancel')
		if result == 'OK':
			replaceName = cmds.promptDialog(q = True, text = True)

			# rename blend shape name
			cmds.aliasAttr(replaceName, '%s.%s' %(cls.bsNodeName, selTrg))
			cmds.aliasAttr(replaceName + '_inv', '%s.%s' %(cls.bsNodeName, selTrg + '_inv'))

			# rename target geometry name
			try:
				cmds.rename(selTrg, replaceName)
				cmds.rename(selTrg + '_inv', replaceName + '_inv')
			except:
				pass

			# Rename multiplyDivide node
			cmds.rename(selTrg + '_mul', replaceName + '_mul')

		cls.populateCorrectiveTrgList()


	@classmethod
	def delKey(cls, *args):
		mel.eval('source channelBoxCommand;')

		selTrgList = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, selectItem = True)

		for selTrg in selTrgList:
			attr = cls.bsNodeName + '.' + selTrg
			mel.eval('CBdeleteConnection "%s"' %attr)

		cls.populateCorrectiveTrgList()
		cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], e = True, selectItem = selTrgList)


	@classmethod
	def removeTrg(cls, *args):
		selTrgList = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, selectItem = True)

		for selTrg in selTrgList:
			cmds.delete(selTrg + '_mul')
			for trg in [selTrg, selTrg + '_inv']:
				bsAttrList = cmds.aliasAttr(cls.bsNodeName, q=True)
				selTrgIndexInList = bsAttrList.index(trg)
				selTrgWeightIndex = selTrgIndexInList + 1
				reObj = re.search(r'\d+', bsAttrList[selTrgWeightIndex])
				selTrgIndex = int(reObj.group())

				if cmds.objExists(trg):
					cmds.delete(trg)
				
				# delete blend shape
				cmds.removeMultiInstance(cls.bsNodeName + '.it[' + str(selTrgIndex) + ']' + '.' + 'itg[' + str(selTrgIndex) + ']', b=True)
				cmds.removeMultiInstance(cls.bsNodeName + '.w[' + str(selTrgIndex) + ']', b = True)
				# cmds.removeMultiInstance('%s.%s' %(cls.bsNodeName, selTrg), b = True)
				try:
					cmds.aliasAttr(cls.bsNodeName + '.' + trg, rm = True)
				except:
					pass
				try:
					cmds.blendShape(cls.bsNodeName, e = True, remove = True, target = (cls.cacheGeo, selTrgIndex, trg, 1.0))
				except:
					pass

		cls.populateCorrectiveTrgList()


	@classmethod
	def setKey(cls, *args):
		selTrgList = cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], q = True, selectItem = True)
		val =  cmds.floatSliderGrp(UI.widgets['trgFltSldrGrp'], q = True, v = True)
		curFrame = cmds.currentTime(q = True)

		for selTrg in selTrgList:
			cmds.setKeyframe('%s.%s' %(cls.bsNodeName, selTrg), v = val, time = curFrame, itt = 'linear', ott = 'linear')

		cls.populateCorrectiveTrgList()

		cmds.textScrollList(UI.widgets['correctiveTrgTxtScrList'], e = True, selectItem = selTrgList)


	@classmethod
	def shpVisOnOff(cls, trnsf, state):
		'''
		Turn on/off for trnasform node's child shapes.
		'''
		
		if state == 'on':
			val = True
		if state == 'off':
			val = False

		shpLs = cmds.listRelatives(trnsf, s = True, path = True)
		if shpLs:
			for shp in shpLs:
				print shp
				cmds.setAttr('%s.visibility' %shp, val)
		else:
			pass