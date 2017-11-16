'''
Author: Sang-tak Lee
Contact: chst27@gamil.com

Usage:
import tak_group
tak_group.UI()
'''

import maya.cmds as cmds
from functools import partial
import tak_misc
import re
reload(tak_misc)

def UI():
	if cmds.window('grpWin', exists = True): cmds.deleteUI('grpWin')
	cmds.window('grpWin', title = 'Make Group')
	
	cmds.formLayout('mainForm', nd = 100)
	
	cmds.tabLayout('mainTab', tv = False)
	cmds.tabLayout('subTab', tv = False, scrollable = True)
	
	cmds.formLayout('subForm', nd = 100, w = 250, h = 200)
	cmds.textScrollList('mainTrgTexScrLis', w = 200, allowMultiSelection = True, sc = partial(sel, 'mainTrgTexScrLis'))
	cmds.button('addButton', label = '+', w = 20, c = loadSel)
	cmds.button('delButton', label = '-', w = 20, c = delSel)
	cmds.optionMenu('suffixOptMenu', label = 'suffix: ')
	cmds.menuItem(label = '_zero')
	cmds.menuItem(label = '_auto')
	cmds.menuItem(label = '_extra')
	cmds.textFieldGrp('delTxtFldGrp', label = 'Remove for: ', columnWidth = [(1, 70), (2, 70)])
	cmds.textFieldGrp('rplcTxtFldGrp', label = 'Replace with: ', columnWidth = [(1, 70), (2, 70)], visible = False)
	cmds.checkBox('ctrlGrpChkBox', label = 'Control Groups')
	
	cmds.formLayout('subForm', e = True,
					attachForm = [('mainTrgTexScrLis', 'top', 5), ('mainTrgTexScrLis', 'left', 5), ('suffixOptMenu', 'left', 5), ('addButton', 'top', 5), ('delTxtFldGrp', 'left', 5), ('rplcTxtFldGrp', 'left', 5), ('rplcTxtFldGrp', 'bottom', 5)],
					attachControl = [('suffixOptMenu', 'bottom', 5, 'delTxtFldGrp'), ('ctrlGrpChkBox', 'bottom', 5, 'delTxtFldGrp'), ('mainTrgTexScrLis', 'bottom', 5, 'suffixOptMenu'), ('addButton', 'left', 5, 'mainTrgTexScrLis'), ('delButton', 'top', 5, 'addButton'), ('delButton', 'left', 5, 'mainTrgTexScrLis'), ('ctrlGrpChkBox', 'left', 40, 'suffixOptMenu'), ('delTxtFldGrp', 'bottom', 5, 'rplcTxtFldGrp')])
	
	
	# attach subForm to the subTab
	cmds.setParent('subTab')
	
	# attach mainTab to the mainForm
	cmds.setParent('mainForm')
	
	cmds.button('appButton', label = 'Apply', c = app)
	cmds.button('closButton', label = 'Close', c = clos)
	
	cmds.formLayout('mainForm', e = True, 
					attachForm = [('mainTab', 'top', 5), ('mainTab', 'left', 5), ('mainTab', 'right', 5), ('appButton', 'left', 5), ('appButton', 'bottom', 5), ('closButton', 'right', 5), ('closButton', 'bottom', 5)],
					attachPosition = [('appButton', 'right', 2.5, 50), ('closButton', 'left', 2.5, 50)],
					attachControl = [('mainTab', 'bottom', 5, 'appButton')])
	
	cmds.window('grpWin', edit = True, w = 280, h = 260)
	cmds.showWindow('grpWin')
	
	loadSel()
	
# addButton
def loadSel(*args):
	selList = cmds.ls(sl = True)
	items = cmds.textScrollList('mainTrgTexScrLis', q = True, allItems = True)
	if items:
		cmds.textScrollList('mainTrgTexScrLis', e = True, removeAll = True)
	cmds.textScrollList('mainTrgTexScrLis', e = True, append = selList)
	
# delButton
def delSel(*args):
	selItem = cmds.textScrollList('mainTrgTexScrLis', q = True, selectItem = True)
	cmds.textScrollList('mainTrgTexScrLis', e = True, removeItem = selItem)
	
	
# apply button
def app(*args):
	# get target list
	trgList = cmds.textScrollList('mainTrgTexScrLis', q = True, allItems = True)

	# get suffix
	suffixOptState = cmds.optionMenu('suffixOptMenu', q = True, select = True)
	if suffixOptState == 1:
		suffix = '_zero'
	elif suffixOptState == 2:
		suffix = '_auto'
	elif suffixOptState == 3:
		suffix = '_extra'

	delTxt = cmds.textFieldGrp('delTxtFldGrp', q = True, text = True)
	rplc = cmds.textFieldGrp('rplcTxtFldGrp', q = True, text = True)

	ctrlGrpOpt = cmds.checkBox('ctrlGrpChkBox', q = True, value = True)
	
	for trg in trgList:
		if ctrlGrpOpt:
			tak_misc.doGroup(trg, '_zero')
			# tak_misc.doGroup(trg, '_cnst')
			tak_misc.doGroup(trg, '_auto')
			tak_misc.doGroup(trg, '_extra')
		# nodType = cmds.nodeType(trg)
		# if nodType == 'joint':
		# 			grpNode = cmds.createNode('transform', n = '%s%s' %(trg, suffix))
		# 			constName = cmds.parentConstraint(trg, grpNode, mo = False, w = 1)
		# 			cmds.delete(constName)
		# 			prnt = cmds.listRelatives(trg, p = True)
		# 			cmds.parent(trg, grpNode)
		# 			if prnt:
		# 				cmds.parent(grpNode, prnt)
		elif suffix and delTxt:
			grpName = tak_misc.doGroup(trg, suffix)
			baseName = re.sub(delTxt, '', trg)
			cmds.rename(grpName, baseName + suffix)
		elif suffix:
			# cmds.select(trg, r = True)
			# grpNode = cmds.duplicate(n = '%s%s' %(trg, suffix), po=True)
			# cmds.parent(trg, grpNode)
			tak_misc.doGroup(trg, suffix)
		
# close button
def clos(*args):
	cmds.deleteUI('grpWin')


def sel(texScLiName):
	# get selected items in specified textScrollList
	selItems = cmds.textScrollList(texScLiName, q = True, selectItem = True)
	
	cmds.select(cl = True)
	
	# select items
	for item in selItems:
		cmds.select(item, add = True)