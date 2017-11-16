'''
Author: Sang-tak Lee
Contact: chst27@gmail.com

Description:
This script will connect one attribute to the others.

Usage:
1. Copy this script and paste in your scripts folder.

2. In maya python tab, run following code.
import tak_multiConnectAttr
reload(tak_multiConnectAttr)
tak_multiConnectAttr.UI()
'''

import maya.cmds as cmds
from functools import partial

def UI():
	winName = 'multiConnectAttrWin'
	if cmds.window(winName, exists = True):
		cmds.deleteUI(winName)

	cmds.window(winName, title = 'Multi Connect Attribute UI')

	cmds.tabLayout(tv = False)
	cmds.tabLayout(w =283, h = 160, tv = False, scrollable = True)

	cmds.columnLayout('mainColLay', adj = True)

	cmds.rowColumnLayout('drvrRowColLay', numberOfColumns = 4)
	cmds.text(label = 'Driver:   ')
	cmds.textField('drvrTxtFld')
	cmds.popupMenu()
	cmds.menuItem(label = 'Load Selected', c = partial(loadSel, 'drvrTxtFld'))
	cmds.text(label = '.')
	cmds.textField('drvrAttrTxtFld')
	cmds.popupMenu()
	cmds.menuItem(label = 'Load Selected Attribute from Channelbox', c = partial(loadSelAttrFromChbx, 'drvrAttrTxtFld'))

	cmds.setParent('mainColLay')
	cmds.separator(h = 5, style = 'none')
	cmds.rowColumnLayout('drvnRowColLay', numberOfColumns = 4)
	cmds.text(label = 'Drivens: ')
	cmds.textScrollList('drvnTxtScrList', h = 50, w = 110)
	cmds.popupMenu()
	cmds.menuItem(label = 'Load Selected', c = partial(loadSel, 'drvnTxtScrList'))
	cmds.menuItem(label = 'Add Selected', c = partial(addSel, 'drvnTxtScrList'))
	cmds.text(label = '.')
	cmds.textField('drvnAttrTxtFld')
	cmds.popupMenu()
	cmds.menuItem(label = 'Load Selected Attribute from Channelbox', c = partial(loadSelAttrFromChbx, 'drvnAttrTxtFld'))

	cmds.setParent('mainColLay')
	cmds.separator(h = 5, style = 'none')
	cmds.button(label = 'Connect Attribute', h = 60, c = connectAttr)

	cmds.window(winName, e = True, w = 200, h = 100)
	cmds.showWindow(winName)


def loadSel(widget, *args):
	selList = cmds.ls(sl = True)

	if widget == 'drvrTxtFld':
		cmds.textField(widget, e = True, text = selList[0])

	elif widget == 'drvnTxtScrList':
		txtScrItems = cmds.textScrollList(widget, q = True, allItems = True)
		if txtScrItems:
			cmds.textScrollList(widget, e = True, removeAll = True)

		cmds.textScrollList(widget, e = True, append = selList)


def addSel(widget, *args):
	selList = cmds.ls(sl = True)

	cmds.textScrollList(widget, e = True, append = selList)


def connectAttr(*args):
	driver = cmds.textField('drvrTxtFld', q = True, text = True)
	driverAttr = cmds.textField('drvrAttrTxtFld', q = True, text = True)
	drivens = cmds.textScrollList('drvnTxtScrList', q = True, allItems = True)
	drivenAttr = cmds.textField('drvnAttrTxtFld', q = True, text = True)

	for driven in drivens:
		cmds.connectAttr('%s.%s' %(driver, driverAttr), '%s.%s' %(driven, drivenAttr), f = True)


def loadSelAttrFromChbx(txtFldName, *args):
	'''
	Description:
		Fill given text field with selected attribute from channelbox.

	Parameters:
		textFldName: string - Text field widget name.

	Returns:
		None
	'''

	# Get selected attribute on channelbox.
	selObj = cmds.ls(sl = True)[0]
	selAttr = cmds.channelBox('mainChannelBox', q = True, selectedMainAttributes = True)[0]

	# Convert selAttr's short name to long name.
	selAttr = cmds.attributeQuery(selAttr, node = selObj, longName = True)

	# Handle compound attribute.
	prntAttr = cmds.attributeQuery(selAttr, node = selObj, listParent = True)
	if prntAttr:
		selAttr = prntAttr

	# Handle list type selAttr.
	if type(selAttr) == list:
		selAttr = selAttr[0]

	# Fill the given text field.
	cmds.textField(txtFldName, e = True, text = selAttr)