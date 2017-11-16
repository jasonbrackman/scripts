'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date: 2015/06/06

Description: Create locator and parent selected object to the locator.

Usage:
import tak_prntLocator
reload(tak_prntLocator)
tak_prntLocator.ui()
'''


import maya.cmds as cmds
from functools import partial


def ui():
	winName = 'pLocWin'
	if cmds.window(winName, exists = True): 
		cmds.deleteUI(winName)

	cmds.window(winName, title = 'Parent Locator')

	cmds.formLayout('mainForm', nd = 100)

	cmds.tabLayout('mainTab', tv = False)
	cmds.tabLayout('subTab', tv = False, scrollable = True)

	cmds.formLayout('subForm', nd = 100, w = 260, h = 140)
	cmds.textScrollList('trgTexScrLis', w = 230, allowMultiSelection = True, sc = partial(sel, 'trgTexScrLis'))
	cmds.button('addButton', label = '+', w = 20, c = loadSel)
	cmds.button('delButton', label = '-', w = 20, c = delSel)
	cmds.text('suffixText', label = 'Suffix: ')
	cmds.textField('sufFixTexFiel', w = 190, text = '')

	cmds.formLayout('subForm', e = True,
		attachForm = [('trgTexScrLis', 'top', 5), ('trgTexScrLis', 'left', 5), ('sufFixTexFiel', 'bottom', 5), ('suffixText', 'left', 5), ('suffixText', 'bottom', 5), ('addButton', 'top', 5)],
		attachControl = [('sufFixTexFiel', 'left', 5, 'suffixText'), ('trgTexScrLis', 'bottom', 5, 'sufFixTexFiel'), ('addButton', 'left', 5, 'trgTexScrLis'), ('delButton', 'top', 5, 'addButton'), ('delButton', 'left', 5, 'trgTexScrLis')])
    
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
    
	cmds.window(winName, edit = True, w = 300, h = 200)
	cmds.showWindow(winName)
    
	loadSel()


# addButton
def loadSel(*args):
	selList = cmds.ls(sl = True)
	items = cmds.textScrollList('trgTexScrLis', q = True, allItems = True)
	if items:
		cmds.textScrollList('trgTexScrLis', e = True, removeAll = True)
	cmds.textScrollList('trgTexScrLis', e = True, append = selList)


# delButton
def delSel(*args):
	selItem = cmds.textScrollList('trgTexScrLis', q = True, selectItem = True)
	cmds.textScrollList('trgTexScrLis', e = True, removeItem = selItem)


# close button
def clos(*args):
	cmds.deleteUI('pLocWin')


def sel(texScLiName):
	# get selected items in specified textScrollList
	selItems = cmds.textScrollList(texScLiName, q = True, selectItem = True)

	cmds.select(cl = True)

	# select items
	for item in selItems:
		cmds.select(item, add = True)


def app(*args):
	# get target list
	trgList = cmds.textScrollList('trgTexScrLis', q = True, allItems = True)
	# get suffix
	suffix = cmds.textField('sufFixTexFiel', q = True, text = True)

	trgList = cmds.ls(sl = True)
	for trg in trgList:
		# if cmds.objectType(trg) == 'joint':
		# 	cmds.makeIdentity(trg, apply = True)

		loc = cmds.spaceLocator(n = trg + suffix)

		pCnst = cmds.parentConstraint(trg, loc, mo = False)
		cmds.delete(pCnst)

		prnt = cmds.listRelatives(trg, p = True)
		cmds.parent(trg, loc)
		if prnt:
			cmds.parent(loc, prnt)

	cmds.deleteUI('pLocWin')