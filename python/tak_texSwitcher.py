'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date: 02/04/2016

Description:
You can switch model's texture resolution using this script.
Texture naming convention must have suffix '_high' or '_low'.

Usage:
In maya python tab run following code.
import tak_texSwitcher
reload(tak_texSwitcher)
tak_texSwitcher.MainUI()
'''


import maya.cmds as cmds
from functools import partial
import os


class MainUI(object):
	'''
	Main class.
	'''

	wdgNameDic = {}
	sceneFileTexLs = cmds.ls(type = 'file')

	@classmethod
	def __init__(cls):
		'''
		Delete window if window already exists then show window.
		'''

		cls.wdgNameDic['winName'] = 'texSwitcherWin'

		if cmds.window(cls.wdgNameDic['winName'], exists = True):
			cmds.deleteUI(cls.wdgNameDic['winName'])
		
		# Show main ui.
		cls.ui()

		# Add asset ui in main ui.
		cls.addAssetUi()

	
	@classmethod
	def ui(cls):
		'''
		Build main ui.
		'''

		cmds.window(cls.wdgNameDic['winName'], title = 'Texture Switcher')

		cls.wdgNameDic['mainColLo'] = cmds.columnLayout(p = cls.wdgNameDic['winName'], adj = True)

		cls.wdgNameDic['assetUiColLo'] = cmds.columnLayout(p = cls.wdgNameDic['mainColLo'], adj = True)
		
		cls.wdgNameDic['btnRowColLo'] = cmds.rowColumnLayout(p = cls.wdgNameDic['mainColLo'], numberOfColumns = 2, columnSpacing = [(2, 5)])
		cmds.button(p = cls.wdgNameDic['btnRowColLo'], label = 'High Tex for Sels', c = partial(cls.swithTexSel, 'high'))
		cmds.button(p = cls.wdgNameDic['btnRowColLo'], label = 'Low Tex for Sels', c = partial(cls.swithTexSel, 'low'))

		cmds.window(cls.wdgNameDic['winName'], e = True, w = 100, h = 10)
		cmds.showWindow(cls.wdgNameDic['winName'])


	@classmethod
	def addAssetUi(cls):
		'''
		Add asset ui in main window.
		'''

		# Add asset ui for referenced assets.
		referenceNodeList = cmds.ls(references = True)
		for refNode in referenceNodeList:
			namespace = cmds.referenceQuery(refNode, namespace = True, shortName = True)
			refFileTexLs = cls.getRefFileTexLs(namespace)

			# If referenced asset has file texture, make asset ui.
			if refFileTexLs:
				assetObj = AssetUI(namespace, refFileTexLs)
				assetObj.assetUi(cls.wdgNameDic['assetUiColLo'])
		
		# If remain texture node in sceneFileTexLs, create asset ui with name 'Misc Textures'.
		if cls.sceneFileTexLs:
			assetObj = AssetUI('Misc Textures', cls.sceneFileTexLs)
			assetObj.assetUi(cls.wdgNameDic['assetUiColLo'])


	@classmethod
	def getRefFileTexLs(cls, refNodeNamespace):
		'''
		Make file texture list associated with referenced asset.
		'''

		refFileTexLs = []
		for fileTex in cls.sceneFileTexLs:
			if refNodeNamespace in fileTex:
				refFileTexLs.append(fileTex)

		# Remove file texture nodes that job done in whole file texture node list.
		cls.sceneFileTexLs = list(set(cls.sceneFileTexLs) - set(refFileTexLs))

		return refFileTexLs


	@classmethod
	def swithTexSel(cls, res, *args):
		'''
		# Description
			Switch texture for selected objects.

		# Parameters
			res(Resolution): string

		# Returns
			None
		'''

		selLs = cmds.ls(sl = True)
		
		for sel in selLs:
			# Get file texture list.
			selShp = cmds.listRelatives(sel, s = True)[0]
			selSG = cmds.listConnections(selShp, s = False, type = 'shadingEngine')[0]
			selAllConnect = cmds.listHistory(selSG)
			selFileTexLs = cmds.ls(selAllConnect, type = 'file')

			# Set file textures's fileTextureName attribute depend on given resolution.
			for fileTex in selFileTexLs:
				fileTexPath = cmds.getAttr('%s.fileTextureName' %fileTex)

				fileTexBaseName = fileTexPath.rsplit('_', 1)[0]
				fileTexExt = fileTexPath.rsplit('.', 1)[-1]

				newPath = fileTexBaseName + '_' + res + '.' + fileTexExt
				if os.path.exists(newPath):
					cmds.setAttr('%s.fileTextureName' %fileTex, newPath, type = 'string')			



class AssetUI(object):
	'''
	Asset objects in current scene.
	'''

	def __init__(self, assetName, fileTexLs):
		'''
		Initialize asset object.
		'''

		# Class members
		self.assetNamespace = assetName
		self.fileTexNodeLs = fileTexLs
		self.assetFileTexInfo = {}
		self.assetWdgNameDic = {}

		self.getAssetFileTexInfo()


	def getAssetFileTexInfo(self):
		'''
		Store file texture node's information.
		'''

		# In case referenced assets.
		if not self.assetNamespace == 'Misc Textures':
			for texNode in self.fileTexNodeLs:
				fileTexBaseName = cmds.getAttr('%s.fileTextureName' %texNode).rsplit('_', 1)[0]
				fileTexExt = cmds.getAttr('%s.fileTextureName' %texNode).rsplit('.', 1)[-1]
				self.assetFileTexInfo[texNode] = [fileTexBaseName, fileTexExt]

		# In case not referenced assets.
		else:
			for texNode in self.fileTexNodeLs:
				fileTexBaseName = cmds.getAttr('%s.fileTextureName' %texNode).rsplit('_', 1)[0]
				fileTexExt = cmds.getAttr('%s.fileTextureName' %texNode).rsplit('.', 1)[-1]
				self.assetFileTexInfo[texNode] = [fileTexBaseName, fileTexExt]


	def assetUi(self, prntLo):
		'''
		Build ui for switching texture for asset.
		'''

		self.assetWdgNameDic['assetOptMenuGrp'] = cmds.optionMenuGrp(p = prntLo, label = self.assetNamespace)
		cmds.optionMenuGrp(self.assetWdgNameDic['assetOptMenuGrp'], e = True, cc = partial(self.texResOptCC, self.assetWdgNameDic['assetOptMenuGrp']), columnWidth = [(1, 120)], columnAttach = [(1, 'left', 5), (2, 'left', 5)])
		cmds.menuItem(label = 'high')
		cmds.menuItem(label = 'low')


	def  texResOptCC(self, wdgName, *args):
		'''
		Textrue resolution option menu change command.
		'''

		# Get texture resolution option that user selected.
		userSelResOpt = cmds.optionMenuGrp(wdgName, q = True, v = True)

		# Set file textures's fileTextureName attribute depend on selected resolution.
		for fileTex in self.assetFileTexInfo.keys():
			newPath = self.assetFileTexInfo[fileTex][0] + '_' + userSelResOpt + '.' + self.assetFileTexInfo[fileTex][1]
			if os.path.exists(newPath):
				cmds.setAttr('%s.fileTextureName' %fileTex, newPath, type = 'string')