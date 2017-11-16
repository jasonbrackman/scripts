'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date: 07/29/2015

Description:
This script for creating control curve from selected edges.

Usage:
'''


import maya.cmds as cmds
import re
import tak_lib
import tak_misc
from functools import partial



class UI(object):
	widgets = {}
	widgets['winName'] = 'ctrlFromEdgesWin'

	@classmethod
	def __init__(cls):
		if cmds.window(cls.widgets['winName'], exists = True):
			cmds.deleteUI(cls.widgets['winName'])

		cls.ui()


	@classmethod
	def ui(cls):
		cmds.window(cls.widgets['winName'], title = 'Control From Edges UI')

		cls.widgets['mainColLo'] = cmds.columnLayout(adj = True)

		cls.widgets['edgeRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 3, columnSpacing = [(1, 5), (2, 5), (3, 5)], p = cls.widgets['mainColLo'])
		cmds.text(label = 'Edges: ', p = cls.widgets['edgeRowColLo'])
		cls.widgets['edgeTxtScrLs'] = cmds.textScrollList(w = 150, h = 100, p = cls.widgets['edgeRowColLo'])
		cls.widgets['edgeBtnColLo'] = cmds.columnLayout(adj = True, p = cls.widgets['edgeRowColLo'])
		cmds.button(label = 'Convert Face to Edges', c = 'cmds.ConvertSelectionToEdgePerimeter()', p = cls.widgets['edgeBtnColLo'])
		cmds.separator(h = 5, style = 'none', p = cls.widgets['edgeBtnColLo'])
		cmds.button(label = 'Load Sels', c = partial(tak_lib.populateTxtScrList, 'textScrollList', cls.widgets['edgeTxtScrLs']), p = cls.widgets['edgeBtnColLo'])

		cmds.separator(h = 10, style = 'in', p = cls.widgets['mainColLo'])

		cls.widgets['jntTxtFldBtnGrp'] = cmds.textFieldButtonGrp(label = 'Joint: ', buttonLabel = 'Load Sel', columnWidth = [(1, 80), (2, 150)], p = cls.widgets['mainColLo'])
		cmds.textFieldButtonGrp(cls.widgets['jntTxtFldBtnGrp'], e = True, bc = partial(tak_lib.loadSel, 'textFieldButtonGrp', cls.widgets['jntTxtFldBtnGrp']))

		cmds.separator(h = 10, style = 'in', p = cls.widgets['mainColLo'])

		cls.widgets['jntSrchRplcColLo'] = cmds.columnLayout(adj = True, p = cls.widgets['mainColLo'])
		cls.widgets['jntsrchTxtFldGrp'] = cmds.textFieldGrp(label = 'Joint Search: ', columnWidth = [(1, 80), (2, 50)], p = cls.widgets['jntSrchRplcColLo'])
		cls.widgets['jntrplcTxtFldGrp'] = cmds.textFieldGrp(label = 'Joint Replace: ', columnWidth = [(1, 80), (2, 50)], p = cls.widgets['jntSrchRplcColLo'])

		cmds.separator(h = 10, style = 'in', p = cls.widgets['mainColLo'])

		cmds.text(label = 'Mirror Search and Replace', p = cls.widgets['mainColLo'])
		cmds.separator(h = 5, style = 'none', p = cls.widgets['mainColLo'])
		cls.widgets['srchRplcRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 2, columnSpacing = [(2, 5)], p = cls.widgets['mainColLo'])

		cls.widgets['suffixSrchRplcColLo'] = cmds.columnLayout(adj = True,  p = cls.widgets['srchRplcRowColLo'])
		cls.widgets['suffixSrchTxtFldGrp'] = cmds.textFieldGrp(label = 'Suffix Search: ', columnWidth = [(1, 100), (2, 50)], p = cls.widgets['suffixSrchRplcColLo'])
		cls.widgets['suffixRplcTxtFldGrp'] = cmds.textFieldGrp(label = 'Suffix Replace: ', columnWidth = [(1, 100), (2, 50)], p = cls.widgets['suffixSrchRplcColLo'])

		cls.widgets['prefixSrchRplcColLo'] = cmds.columnLayout(adj = True,  p = cls.widgets['srchRplcRowColLo'])
		cls.widgets['prefixSrchTxtFldGrp'] = cmds.textFieldGrp(label = 'Prefix Search: ', columnWidth = [(1, 80), (2, 50)], p = cls.widgets['prefixSrchRplcColLo'])
		cls.widgets['prefixRplcTxtFldGrp'] = cmds.textFieldGrp(label = 'Prefix Replace: ', columnWidth = [(1, 80), (2, 50)], p = cls.widgets['prefixSrchRplcColLo'])

		cmds.separator(h = 10, style = 'in', p = cls.widgets['mainColLo'])

		cls.widgets['mainBtnRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 2, columnWidth = [(1, 150), (2, 150)], columnSpacing = [(2, 20)], p = cls.widgets['mainColLo'])
		cmds.button(label = 'Create', h = 30, c = Functions.ctrlFromEdges, p = cls.widgets['mainBtnRowColLo'])
		cmds.button(label = 'Mirror Selected Control', h = 30, c = Functions.mirrorCtrl, p = cls.widgets['mainBtnRowColLo'])

		cmds.window(cls.widgets['winName'], e = True, w = 200, h = 100)
		cmds.showWindow(cls.widgets['winName'])




class Functions(object):

	@classmethod
	def ctrlFromEdges(cls, *args):
		'''
		This function create control from selected polygon for selected joint.
		First select a joint and select polygons.
		'''
		jnt = cmds.textFieldButtonGrp(UI.widgets['jntTxtFldBtnGrp'], q = True, text = True)
		edges = cmds.textScrollList(UI.widgets['edgeTxtScrLs'], q = True, allItems = True)

		jntSrchStr = cmds.textFieldGrp(UI.widgets['jntsrchTxtFldGrp'], q = True, text = True)
		jntRplcStr = cmds.textFieldGrp(UI.widgets['jntrplcTxtFldGrp'], q = True, text = True)

		# Convert selected faces to control shape
		cmds.select(edges, r = True)
		ctrlCrv = cmds.polyToCurve(form = 2, degree = 1)[0]
		cmds.delete(ctrlCrv, ch = True)

		# Match control transform node to the joint
		ctrlName = re.sub(jntSrchStr, jntRplcStr, jnt)
		trnsf = cmds.createNode('transform', n = ctrlName)
		cnst = cmds.parentConstraint(jnt, trnsf, mo = False)
		cmds.delete(cnst)

		# Parent control shape to the control transform node in place
		tak_lib.parentShpInPlace(ctrlCrv, trnsf)

		# Match shape name to transform name
		shapName = cmds.listRelatives(trnsf, s = True)[0]
		if shapName != '%sShape' %trnsf:
			cmds.rename(shapName, '%sShape' %trnsf)

		# tak_misc.doGroup(trnsf, '_zero')

		# Connect joint to the control
		cmds.parentConstraint(trnsf, jnt, mo = False)

		cmds.delete(ctrlCrv)


	@staticmethod
	def mirrorCtrl(*args):
		'''
		This function copy and mirror for selected controls
		'''
		suffixSrchStr = cmds.textFieldGrp(UI.widgets['suffixSrchTxtFldGrp'], q = True, text = True)
		suffixRplcStr = cmds.textFieldGrp(UI.widgets['suffixRplcTxtFldGrp'], q = True, text = True)
		prefixSrchStr = cmds.textFieldGrp(UI.widgets['prefixSrchTxtFldGrp'], q = True, text = True)
		prefixRplcStr = cmds.textFieldGrp(UI.widgets['prefixRplcTxtFldGrp'], q = True, text = True)

		selList = cmds.ls(sl = True)

		for sel in selList:
			mirCtrlName = re.sub(prefixSrchStr, prefixRplcStr, sel)
			mirCtrl = cmds.duplicate(sel, n = mirCtrlName)[0]
			mirJnt = re.sub(suffixSrchStr, suffixRplcStr, mirCtrl)
			cnst = cmds.parentConstraint(mirJnt, mirCtrl, mo = False)
			cmds.delete(cnst)
			cmds.parentConstraint(mirCtrl, mirJnt, mo = False)