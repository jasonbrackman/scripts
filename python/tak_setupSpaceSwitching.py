'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
'''



import maya.cmds as cmds
import tak_mayaUiUtils 
reload(tak_mayaUiUtils)
from functools import partial



def ui():
	winName = 'setSpcSwc'

	if cmds.window(winName, exists = True):
		cmds.deleteUI(winName)

	cmds.window(winName, title = 'Set Up Space Switching', mnb = False, mxb = False)
	
	cmds.columnLayout(adj = True, rs = 3)

	cmds.rowColumnLayout(numberOfColumns = 2, columnOffset = [2, 'left', 5])
	cmds.frameLayout(label = 'Objects', w = 150)
	cmds.textScrollList('objTxtScrLs', sc = partial(tak_mayaUiUtils.txtScrLsSC, 'objTxtScrLs'), allowMultiSelection = True)
	cmds.popupMenu()
	cmds.menuItem(label = 'Load Sels', c = partial(tak_mayaUiUtils.populateTxtScrList,'textScrollList', 'objTxtScrLs'))
	cmds.setParent('..') # Move to parent layout that is rowColumnLayout.
	cmds.frameLayout(label = 'Target Spaces', w = 150)
	cmds.textScrollList('trgSpcTxtScrLs', sc = partial(tak_mayaUiUtils.txtScrLsSC, 'trgSpcTxtScrLs'), allowMultiSelection = True)
	cmds.popupMenu()
	cmds.menuItem(label = 'Load Sels', c = partial(tak_mayaUiUtils.populateTxtScrList,'textScrollList', 'trgSpcTxtScrLs'))
	cmds.setParent('..') # Move to parent layout that is rowColumnLayout.
	cmds.setParent('..') # Move to parent layout that is columnLayout.

	cmds.checkBoxGrp('cnstChkBoxGrp', label = 'Constraint: ', numberOfCheckBoxes = 3, v1 = True, labelArray3 = ['Parent', 'Point', 'Orient'], columnAlign = [1, 'left'], columnWidth = [(1, 70), (2, 80), (3, 80), (4, 80)], on1 = prntCnstChkBoxOn, on2 = posOriCnstChkBoxOn, on3 = posOriCnstChkBoxOn)

	cmds.button(label = 'Apply', c = main, h = 30)

	cmds.window(winName, e = True, w = 300, h = 100)
	cmds.showWindow(winName)


def main(*args):
	# Get data.
	trgSpcs = cmds.textScrollList('trgSpcTxtScrLs', q = True, allItems = True)
	objs = cmds.textScrollList('objTxtScrLs', q = True, allItems = True)
	prntCnstOpt = cmds.checkBoxGrp('cnstChkBoxGrp', q = True, v1 = True)
	pntCnstOpt = cmds.checkBoxGrp('cnstChkBoxGrp', q = True, v2 = True)
	oriCnstOpt = cmds.checkBoxGrp('cnstChkBoxGrp', q = True, v3 = True)
	
	for obj in objs:
		spcLocs = []
		for trgSpc in trgSpcs:
			spcLoc = '%s_%s_space_loc' %(obj, trgSpc)
			if cmds.objExists(spcLoc):
				spcLocs.append(spcLoc) # When locator is already exists, just append to the locator list.
				pass
			else:
				# Create locators on object position.
				cmds.spaceLocator(n = spcLoc)[0]
				cmds.delete(cmds.parentConstraint(obj, spcLoc, mo = False)) # Match locator to object's transform.
				spcLocs.append(spcLoc)
			
			# Constraint locator with target space.
			if prntCnstOpt:
				cmds.parentConstraint(trgSpc, spcLoc, mo = True)
			if pntCnstOpt:
				cmds.pointConstraint(trgSpc, spcLoc, mo = True)
			if oriCnstOpt:
				cmds.orientConstraint(trgSpc, spcLoc, mo = True)
		
		# Grouping space locators.
		spcLocGrp = 'space_loc_grp'
		if not cmds.objExists(spcLocGrp):
			spcLocGrp = cmds.createNode('transform', n = spcLocGrp)
			cmds.setAttr('%s.visibility' %spcLocGrp, False)
		for spcLoc in spcLocs:
			if not cmds.listRelatives(spcLoc, p = True):
				cmds.parent(spcLoc, spcLocGrp)

		# Create spaces group.
		spcsGrp = obj + '_spaces'
		if not cmds.objExists(spcsGrp):
			objPrnt = cmds.listRelatives(obj, p = True)
			spcsGrp = cmds.createNode('transform', n = obj + '_spaces')
			cmds.delete(cmds.parentConstraint(obj, spcsGrp, mo = False)) # Match spcsGrp's transform to the object.
			cmds.parent(obj, spcsGrp)
			if objPrnt:
				cmds.parent(spcsGrp, objPrnt[0])

		# Constraint object's parnet spaces group with locators.
		if prntCnstOpt:
			prntCnst = cmds.parentConstraint(spcLocs, spcsGrp, mo = False)[0]
		if pntCnstOpt:
			pntCnst = cmds.pointConstraint(spcLocs, spcsGrp, mo = False)[0]
		if oriCnstOpt:
			oriCnst = cmds.orientConstraint(spcLocs, spcsGrp, mo = False)[0]

		# Add divider.
		if not cmds.objExists(obj + '.spaceSwitch'):
			cmds.addAttr(obj, ln = 'spaceSwitch', at = 'enum', en = '---------------:')
			cmds.setAttr('%s.%s' %(obj, 'spaceSwitch'), channelBox = True)

		# Add space switching atributes.
		cnsts = cmds.listRelatives(spcsGrp, type = 'constraint')
		spaces = ':'.join(trgSpcs) + ':'

		for cnst in cnsts:
			cnstType = cmds.nodeType(cnst)
			if cnstType == 'parentConstraint' and prntCnstOpt:
				cmds.addAttr(obj, ln = "parentSpace", nn = "Parent Space", at = "enum", en = spaces, keyable = True)
			
			if cnstType == 'pointConstraint' and pntCnstOpt:
				cmds.addAttr(obj, ln = "positionSpace", nn = "Position Space", at = "enum", en = spaces, keyable = True)
			
			if cnstType == 'orientConstraint' and oriCnstOpt:
				cmds.addAttr(obj, ln = "orientSpace", nn = "Orient Space", at = "enum", en = spaces, keyable = True)

		# Add spaces to the object and connect to constraint weights.
		for trgSpc in trgSpcs:
			defaultVal = 0
			if trgSpcs.index(trgSpc) == 0: # Set first target value to 1.
				defaultVal = 1
			if prntCnstOpt:
				cmds.addAttr(obj, ln = trgSpc + '_parentSpace', at = 'short', keyable = True, min = 0, max = 1, dv = defaultVal)
				prntCnstWeights = cmds.parentConstraint(prntCnst, q = True, weightAliasList = True)
				for prntCnstW in prntCnstWeights:
					if trgSpc in prntCnstW:
						cmds.connectAttr(obj + '.' + trgSpc + '_parentSpace', prntCnst + '.' + prntCnstW, f = True)
						break
			if pntCnstOpt:
				cmds.addAttr(obj, ln = trgSpc + '_positionSpace', at = 'short', keyable = True, min = 0, max = 1, dv = defaultVal)
				pntCnstWeights = cmds.pointConstraint(pntCnst, q = True, weightAliasList = True)
				for pntCnstW in pntCnstWeights:
					if trgSpc in pntCnstW:
						cmds.connectAttr(obj + '.' + trgSpc + '_positionSpace', pntCnst + '.' + pntCnstW, f = True)
						break
			if oriCnstOpt:
				cmds.addAttr(obj, ln = trgSpc + '_orientSpace', at = 'short', keyable = True, min = 0, max = 1, dv = defaultVal)
				oriCnstWeights = cmds.orientConstraint(oriCnst, q = True, weightAliasList = True)
				for oriCnstW in oriCnstWeights:
					if trgSpc in oriCnstW:
						cmds.connectAttr(obj + '.' + trgSpc + '_orientSpace', oriCnst + '.' + oriCnstW, f = True)
						break

		# Connect Space switching objects to spaceSwitchAttrObjs's message attribute.
		# This set up is for namespace handling when referenced to a scene.
		spcSwchAttrObjsNode = 'spaceSwitchAttrObjsInfo'
		if not cmds.objExists(spcSwchAttrObjsNode):
			cmds.createNode('transform', n = spcSwchAttrObjsNode)
		if not cmds.objExists(spcSwchAttrObjsNode + '.' + obj):
			cmds.addAttr(spcSwchAttrObjsNode, at = 'message', ln = obj)
			cmds.connectAttr(obj + '.message', spcSwchAttrObjsNode + '.' + obj)

	# Create script node
	scriptNodeName = 'spaceSwitchMatchTrsfExpr'

	if cmds.objExists(scriptNodeName):
		cmds.scriptNode(scriptNodeName, executeBefore = True)
	else:
		exprStr = '''def spaceSwitchMatchTrsf():
	print 'Try to Matching Transform'
	# Get selected object namespace.
	nameSpace = ''
	sel = cmds.ls( sl = True )[0]
	splitResult = sel.rsplit(':', 1)
	if len(splitResult) > 1:
		nameSpace = splitResult[0] + ':'

	# Store current transform
	curPos = cmds.xform(sel, q = True, rp = True, ws = True)
	curRo = cmds.xform(sel, q = True, ro = True, ws = True)

	# Get selected attribute.
	rawSelAttr = cmds.channelBox('mainChannelBox', q = True, selectedMainAttributes = True)
	selAttrName = cmds.attributeQuery(rawSelAttr, longName = True, node = sel)
	selAttrFullName = sel + '.' + selAttrName

	# Get slected space name.
	selSpace = cmds.getAttr(selAttrFullName, asString = True)

	# Space weight attribute name depend on selected attribute.
	selSpaceWeightAttr = sel + '.' + selSpace + '_' + selAttrName

	# Set spaces weight
	udAttrs = cmds.listAttr(sel, ud = True)
	for udAttr in udAttrs: # Convert to full attribute name
		udAttrs[udAttrs.index(udAttr)] = sel + '.' + udAttr
	for udAttr in udAttrs:
		if selAttrFullName == udAttr:
			continue
		elif selAttrName in udAttr and selSpaceWeightAttr == udAttr:
			cmds.setAttr(selSpaceWeightAttr, 1)
		elif selAttrName in udAttr and selSpaceWeightAttr != udAttr:
			cmds.setAttr(udAttr, 0)

	# Match transform
	cmds.xform(sel, t = curPos, ws = True)
	cmds.xform(sel, ro = curRo, ws = True)

	print 'Transfrom Matched'


# Attach script job to the objects containing space switch attribute.
spaceSwitchAttrObjInfos = cmds.ls('*spaceSwitchAttrObjsInfo', r = True)

for spaceSwitchAttrObjInfo in spaceSwitchAttrObjInfos:
	spaceSwitchAttrObjs = cmds.listAttr(spaceSwitchAttrObjInfo, ud = True)    
	for spaceSwitchAttrObj in spaceSwitchAttrObjs:
		spaceSwitchAttrObj = cmds.listConnections(spaceSwitchAttrObjInfo + '.' + spaceSwitchAttrObj, s = True, d = False)[0]
		keyableUdAttrs = cmds.listAttr(spaceSwitchAttrObj, ud = True, keyable = True)
		for keyableUdAttr in keyableUdAttrs:
			if 'Space' in keyableUdAttr and cmds.attributeQuery(keyableUdAttr, node = spaceSwitchAttrObj, at = True) == 'enum':
				cmds.scriptJob(kws = True, ac = [spaceSwitchAttrObj + '.' + keyableUdAttr, spaceSwitchMatchTrsf])
					'''

		cmds.scriptNode(beforeScript = exprStr, scriptType = 1, sourceType = 'python', n = scriptNodeName)
		cmds.scriptNode(scriptNodeName, executeBefore = True)


def prntCnstChkBoxOn(*args):
	cmds.checkBoxGrp('cnstChkBoxGrp', e = True, v2 = False)
	cmds.checkBoxGrp('cnstChkBoxGrp', e = True, v3 = False)


def posOriCnstChkBoxOn(*args):
	cmds.checkBoxGrp('cnstChkBoxGrp', e = True, v1 = False)
	