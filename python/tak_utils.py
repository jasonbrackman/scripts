'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date: 07/29/2015

Description:
This module is collection of functions in common usage.
'''

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya


def showHUD(widgetName, title, sectionNum = 2, blockNum = 0):
	'''
	This function find available block and display hud.
	'''
	try:
		cmds.headsUpDisplay(widgetName, s = sectionNum, b = blockNum, blockSize = 'large', label = title, labelFontSize = 'large')
	except:
		blockNum += 1
		showHUD(widgetName, title, blockNum)


def loadSel(wdgType, wdgName, *args):
	'''
	Fill the text field with selected object.
	'''
	sel = cmds.ls(sl = True)[0]

	eval('cmds.%s("%s", e = True, text = sel)' %(wdgType, wdgName))
	

def populateTxtScrList(wdgType, wdgName, *args):
	'''
	Populate text scroll list with selected objects.
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

