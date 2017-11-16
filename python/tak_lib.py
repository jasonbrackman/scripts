'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date: 07/29/2015

Description:
This module is collection of functions in common usage.
'''
import os
import pprint
import re

import maya.OpenMaya as OpenMaya
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm


def showHUD(widgetName, title, sectionNum = 2, blockNum = 0):
	'''
	This function find available block and display hud.
	'''

	allHuds = cmds.headsUpDisplay(listHeadsUpDisplays = True)

	hudsInSection = []
	for hud in allHuds:
		if cmds.headsUpDisplay(hud, q = True, s = True) == sectionNum:
			hudsInSection.append(hud)

	if hudsInSection:
		invalidBlocks = []
		for hud in hudsInSection:
			invalidBlock = cmds.headsUpDisplay(hud, q = True, b = True)
			invalidBlocks.append(invalidBlock)

		blockNum = max(invalidBlocks) + 1
	
	cmds.headsUpDisplay(widgetName, s = sectionNum, b = blockNum, blockSize = 'medium', label = title, labelFontSize = 'large')


def loadSel(wdgType, wdgName, *args):
	'''
	Fill the text field with selected object.
	'''

	sel = cmds.ls(sl = True)[0]

	eval('cmds.%s("%s", e = True, text = sel)' %(wdgType, wdgName))
	

def populateTxtScrList(wdgType, wdgName, *args):
	'''
	Description:
	Populate text scroll list with selected objects.
	
	Arguments: 
	wdgType(string), wdgName(string)

	Returns:
	Nothing
	'''

	selList = cmds.ls(sl = True, fl = True)

	items = eval('cmds.%s("%s", q = True, allItems = True)' %(wdgType, wdgName))
	if items:
		eval('cmds.%s("%s", e = True, removeAll = True)' %(wdgType, wdgName))

	eval('cmds.%s("%s", e = True, append = %s)' %(wdgType, wdgName, selList))


def matchConSel(driver, driven):
	'''
	Match curve shape of target to source.
	Select source and then target.
	'''

	# get number of cvs of source
	degs = cmds.getAttr('%s.degree' %driver)
	spans = cmds.getAttr('%s.spans' %driver)
	cvs = degs + spans
	
	for i in range(cvs):
		# get worldspace translate value of each cv
		cvTr = cmds.xform('%s.cv[%d]' %(driver, i), q = True, t = True, ws = True)
		
		# set opposite control's cvs
		cmds.xform('%s.cv[%d]' %(driven, i), t = (cvTr[0], cvTr[1], cvTr[2]), ws = True)


def parentShpInPlace(src, trg):
	'''
	Parent source transform's shape to target transform node with no transition of the shape.
	'''

	# Keep source object for match target's shape
	srcTmp = cmds.duplicate(src, n = src + '_tmp')[0]

	# Get source object's shape
	srcShp = cmds.listRelatives(src, s = True)[0]

	# Parent shape to the target transform node
	cmds.parent(srcShp, trg, s = True, r = True)

	# Match shape with source object
	matchConSel(srcTmp, trg)

	cmds.delete(srcTmp)


def getAllDfms(obj):
	'''
	Description:
		Retrive all deformers assigned to the object.
	
	Arguments:
		obj: string, Object name.
	
	Returns:
		deformers: string list, List of deformer names.
	'''

	allDfmSets = cmds.listSets(object = obj, type = 2, extendToShape = True)
	if allDfmSets:
		deformers = [cmds.listConnections(x + '.usedBy')[0] for x in allDfmSets if not 'tweak' in x]
		return deformers

	return None


def setAllDefEnvlope(geo, envVal):
	'''
	Description:
		All deformers that associate with geometry set envelope to 0 or 1.

	Arguments:
		geo(string), Geometry name.
		envVal(integer), Envelope value of deformer.

	Returns:
		None
	'''

	hierMeshLs = cmds.listRelatives(geo, ad = True, type = 'mesh')

	deformerTypeLs = ['skinCluster', 'blendShape', 'cluster', 'ffd', 'wrap', 'nonLinear', 'sculpt', 'softMod', 'jiggle', 'wire']
	deformerLs = []
	
	if hierMeshLs:
		for mesh in hierMeshLs:
			allConnections = cmds.listHistory(mesh)
			for deformerType in deformerTypeLs:
				findDeformer = cmds.ls(allConnections, type = deformerType)
				if findDeformer:
					deformerLs.append(findDeformer[0])

		for dfm in deformerLs:
			cmds.setAttr(dfm + '.envelope', envVal)


def getAllDef(geo):
	'''
	Description:
		Get all deformer assigned to shape.
	'''

	deformerTypeLs = ['skinCluster', 'blendShape', 'cluster', 'ffd', 'wrap', 'nonLinear', 'sculpt', 'softMod', 'jiggle', 'wire']
	assignedDefLs = []

	if cmds.nodeType(geo) == 'transform':
		geo = cmds.listRelatives(geo, s = True, ni = True)[0]

	allConnections = cmds.listHistory(geo)
	for deformerType in deformerTypeLs:
		findDeformer = cmds.ls(allConnections, type = deformerType)
		if findDeformer:
			assignedDefLs.append(findDeformer[0])

	return assignedDefLs


def isUniqeName(obj):
	'''
	Description:
	Check given object is uniqe or not.

	Arguments:
	obj(string)

	Returns:
	True/False
	'''

	if len(cmds.ls(obj)) == 1:
		return True
	else:
		return False


def getMatFromSel(obj):
	'''
	Get material From selected object.
	'''

	shapeName = cmds.listRelatives(obj, ni = True, path = True, s = True)

	if shapeName:
		sgName = cmds.listConnections(shapeName[0], d = True, type = "shadingEngine")
		matName = cmds.ls(cmds.listConnections(sgName), materials = True)

		return list(set(matName))


def getSelAttrsNiceName():
	'''
	Get nice name of selected attributes in channelbox.
	'''

	sel = cmds.ls(sl = True)[-1]
	
	rawSelAttrs = cmds.channelBox('mainChannelBox', q = True, selectedMainAttributes = True)
	niceSelAttrs = []
	
	if rawSelAttrs:
		for rawAttr in rawSelAttrs:
			niceSelAttrs.append(cmds.attributeQuery(rawAttr, longName = True, node = sel))
		return niceSelAttrs
	else:
		return None


def findShadingEngine(startNode):
	destinationNodes = cmds.listConnections(startNode, s = False, scn = True)
	
	resultShadingEngine = ''
	
	if destinationNodes:		
		for node in destinationNodes:
			if cmds.nodeType(node) == 'shadingEngine':
				resultShadingEngine = node
			else:
				pass

		if resultShadingEngine:
			return resultShadingEngine
		else:
			for node in destinationNodes:
				result = findShadingEngine(node)
				if result:
					return result


def unlockChannelBoxAttr(transformNode):
	mel.eval('source channelBoxCommand;')

	attrList = ['translate', 'rotate', 'scale']
	axisList = ['X', 'Y', 'Z']

	for attr in attrList:
		for axis in axisList:
			cmds.setAttr('%s.%s%s' %(transformNode, attr, axis), keyable = True)
			mel.eval('CBunlockAttr "%s.%s%s";' %(transformNode, attr, axis))

	cmds.setAttr('%s.visibility' %transformNode, keyable = True)
	mel.eval('CBunlockAttr "%s.visibility";' %transformNode)


def loadPath(wdgName):
	'''
	Fill folder path textFieldGrp.
	'''
	curScenePath = cmds.file(q = True, sceneName = True)
	curWorkDir = os.path.dirname(curScenePath)
	fldrPath = cmds.fileDialog2(dialogStyle = 1, fileMode = 2, startingDirectory = curWorkDir)[0]
	cmds.textFieldButtonGrp(wdgName, e = True, text = fldrPath)


def rmvEndInt(name):
	'''
	Remove integer that end of the name.
	'''

	newName = re.sub(r"(\d+)$", r"", name)
	cmds.rename(name, newName)
	
	return newName


def printLs(parm_list):
	for item in parm_list:
		print item


def getClosestVtx():
	'''
	Description
		Get closest target mesh's vertices from source mesh.

	Parameters
		None

	Retruns
		closestVtxs: string list - Target mesh's closest vertices.
	'''

	# Get selections.
	selLs = OpenMaya.MSelectionList()
	OpenMaya.MGlobal.getActiveSelectionList(selLs)
	
	# Get dagpath.
	srcDagPath = OpenMaya.MDagPath()
	selLs.getDagPath(0, srcDagPath)
	trgDagPath = OpenMaya.MDagPath()
	selLs.getDagPath(1, trgDagPath)
	
	# Set MItMeshVertex.
	srcVtxIt = OpenMaya.MItMeshVertex(srcDagPath)
	trgVtxIt = OpenMaya.MItMeshVertex(trgDagPath)
	
	# Find closest vertices id on target mesh.
	closestVtxIds = []
	while not srcVtxIt.isDone():
		minDist = 1000000
		closestVtxId = -1
		srcVtxWsPos = srcVtxIt.position(OpenMaya.MSpace.kWorld)
		trgVtxIt.reset()
		while not trgVtxIt.isDone():
			trgVtxWsPos = trgVtxIt.position(OpenMaya.MSpace.kWorld)
			dist = srcVtxWsPos.distanceTo(trgVtxWsPos)
			if dist < minDist:
				minDist = dist
				closestVtxId = trgVtxIt.index()
			trgVtxIt.next()
	
		closestVtxIds.append(closestVtxId)
		
		srcVtxIt.next()
	
	# Get vertices name.
	trgDagPathFullName = trgDagPath.fullPathName()
	closestVtxs = []
	for vtxId in closestVtxIds:
		vtxName = trgDagPathFullName + '.vtx[' + str(vtxId) + ']'
		closestVtxs.append(vtxName)
	
	return closestVtxs


def rmvRepeatItem(parm_list):
	""" Remove repeated item in the given list """
	return list(set(parm_list))


def findMultiAttributeEmptyIndex(node, attribute):
	"""
	Find available index of multi attribute
	Args:
		node: Node or node name
		attribute (string): Attribute name

	Returns:
		Available index
	"""
	if isinstance(node, basestring):
		node = pm.PyNode(node)

	id = 0

	while node.attr(attribute)[id].isConnected():
		id += 1

	return id


def searchMethods(obj, *args):
	"""
	Print out methods that includes all search strings

	Args:
		obj: Object
		*args: Search strings. Not case sensitive

	Examples:
		tak_lib.searchMethods(obj, 'get', 'name')
	"""
	methods = dir(obj)
	origMethods = methods

	for searchStr in args:
		methods = [method for method in methods if re.search(searchStr, method, re.IGNORECASE)]

	if origMethods == methods or not methods:
		print 'Not found'
	else:
		pprint.pprint(methods)


def searchAttributes(obj, *args):
	"""
	Print out methods that includes all search strings

	Args:
		obj: Object
		*args: Search strings. Not case sensitive

	Examples:
		tak_lib.searchMethods(obj, 'get', 'name')
	"""
	attributes = obj.listAttr()
	origAttributes = attributes

	for searchStr in args:
		attributes = [attr for attr in attributes if re.search(searchStr, attr.name(), re.IGNORECASE)]

	if origAttributes == attributes or not attributes:
		print 'Not found'
	else:
		pprint.pprint(attributes)


def getMDagPath(node):
	"""
	Args:
		node(str): Node name

	Returns:
		MDagPath
	"""
	mSelLs = OpenMaya.MSelectionList()
	mSelLs.add(node)

	mDagPath = OpenMaya.MDagPath()

	mSelLs.getDagPath(0, mDagPath)

	return mDagPath
