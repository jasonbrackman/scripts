'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date: 2015.04.24

Description:
This script help to create range of motion easily.
'''

import maya.cmds as cmds

class UI(object):
	widgets = {}
	winName = 'romWin'

	@classmethod
	def __init__(cls):
		if cmds.window(cls.winName, exists = True):
			cmds.deleteUI(cls.winName)

		cls.ui()


	@classmethod
	def ui(cls):
		cmds.window(cls.winName, title = 'Create Range Of Motion', mnb = False, mxb = False)

		cls.widgets['mainColLo'] = cmds.columnLayout(adj = True)

		cls.widgets['txRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 4, columnOffset = [(1, 'left', 5), (2, 'left', 5), (4, 'right', 5)], columnWidth = [(3, 40), (4, 40)])
		cls.widgets['txChkBox'] = cmds.checkBox(label = '')
		cmds.text(label = 'TranslateX Min/Max: ')
		cls.widgets['txMinIntFld'] = cmds.intField(v = -10)
		cls.widgets['txMaxIntFld'] = cmds.intField(v = 10)
		cmds.setParent('..')

		cls.widgets['tyRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 4, columnOffset = [(1, 'left', 5), (2, 'left', 5), (4, 'right', 5)], columnWidth = [(3, 40), (4, 40)])
		cls.widgets['tyChkBox'] = cmds.checkBox(label = '')
		cmds.text(label = 'TranslateY Min/Max: ')
		cls.widgets['tyMinIntFld'] = cmds.intField(v = -10)
		cls.widgets['tyMaxIntFld'] = cmds.intField(v = 10)
		cmds.setParent('..')

		cls.widgets['tzRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 4, columnOffset = [(1, 'left', 5), (2, 'left', 5), (4, 'right', 5)], columnWidth = [(3, 40), (4, 40)])
		cls.widgets['tzChkBox'] = cmds.checkBox(label = '')
		cmds.text(label = 'TranslateZ Min/Max: ')
		cls.widgets['tzMinIntFld'] = cmds.intField(v = -10)
		cls.widgets['tzMaxIntFld'] = cmds.intField(v = 10)
		cmds.setParent('..')

		cmds.separator(style = 'in', h = 5)

		cls.widgets['rxRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 4, columnOffset = [(1, 'left', 5), (2, 'left', 5), (4, 'right', 5)], columnWidth = [(3, 40), (4, 40)])
		cls.widgets['rxChkBox'] = cmds.checkBox(label = '')
		cmds.text(label = 'RotateX Min/Max: ')
		cls.widgets['rxMinIntFld'] = cmds.intField(v = -60)
		cls.widgets['rxMaxIntFld'] = cmds.intField(v = 60)
		cmds.setParent('..')

		cls.widgets['ryRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 4, columnOffset = [(1, 'left', 5), (2, 'left', 5), (4, 'right', 5)], columnWidth = [(3, 40), (4, 40)])
		cls.widgets['ryChkBox'] = cmds.checkBox(label = '', v = True)
		cmds.text(label = 'RotateY Min/Max: ')
		cls.widgets['ryMinIntFld'] = cmds.intField(v = -60)
		cls.widgets['ryMaxIntFld'] = cmds.intField(v = 60)
		cmds.setParent('..')

		cls.widgets['rzRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 4, columnOffset = [(1, 'left', 5), (2, 'left', 5), (4, 'right', 5)], columnWidth = [(3, 40), (4, 40)])
		cls.widgets['rzChkBox'] = cmds.checkBox(label = '', v = True)
		cmds.text(label = 'RotateZ Min/Max: ')
		cls.widgets['rzMinIntFld'] = cmds.intField(v = -60)
		cls.widgets['rzMaxIntFld'] = cmds.intField(v = 60)
		cmds.setParent('..')

		cmds.separator(style = 'in', h = 5)

		# cls.widgets['sFrmRowColLo'] = cmds.rowColumnLayout(numberOfColumns = 2, columnOffset = [(1, 'left', 5), (2, 'left', 5)], columnWidth = [(2, 40)])
		# cmds.text(label = 'Start Frame: ')
		# cls.widgets['sFrmIntFld'] = cmds.intField(v = 1)
		# cmds.setParent('..')

		# cmds.separator(style = 'in', h = 5)

		cmds.button(label = 'Apply', h = 50, c = Functions.apply)

		cmds.window(cls.winName, e = True, w = 150, h = 150)
		cmds.showWindow(cls.winName)


class Functions(object):
	@staticmethod
	def apply(*args):
		selList = cmds.ls(sl = True)

		# get option state
		txOpt = cmds.checkBox(UI.widgets['txChkBox'], q = True, v = True)
		tyOpt = cmds.checkBox(UI.widgets['tyChkBox'], q = True, v = True)
		tzOpt = cmds.checkBox(UI.widgets['tzChkBox'], q = True, v = True)
		rxOpt = cmds.checkBox(UI.widgets['rxChkBox'], q = True, v = True)
		ryOpt = cmds.checkBox(UI.widgets['ryChkBox'], q = True, v = True)
		rzOpt = cmds.checkBox(UI.widgets['rzChkBox'], q = True, v = True)
		# sFrmOpt = cmds.intField(UI.widgets['sFrmIntFld'], q = True, v = True)

		# cmds.playbackOptions(minTime = sFrmOpt)
		# cmds.currentTime(sFrmOpt)

		for sel in selList:
			cmds.select(sel, r = True)

			# get minimun maximun value if option is turn on and set keyframe
			if txOpt:
				txMin = cmds.intField(UI.widgets['txMinIntFld'], q = True, v = True)
				txMax = cmds.intField(UI.widgets['txMaxIntFld'], q = True, v = True)
				curFrame = cmds.currentTime(q = True)
				Functions.setKeyframe('translateX', curFrame, txMin, txMax)

			if tyOpt:
				tyMin = cmds.intField(UI.widgets['tyMinIntFld'], q = True, v = True)
				tyMax = cmds.intField(UI.widgets['tyMaxIntFld'], q = True, v = True)
				curFrame = cmds.currentTime(q = True)
				Functions.setKeyframe('translateY', curFrame, tyMin, tyMax)

			if tzOpt:
				tzMin = cmds.intField(UI.widgets['tzMinIntFld'], q = True, v = True)
				tzMax = cmds.intField(UI.widgets['tzMaxIntFld'], q = True, v = True)
				curFrame = cmds.currentTime(q = True)
				Functions.setKeyframe('translateZ', curFrame, tzMin, tzMax)

			if rxOpt:
				rxMin = cmds.intField(UI.widgets['rxMinIntFld'], q = True, v = True)
				rxMax = cmds.intField(UI.widgets['rxMaxIntFld'], q = True, v = True)
				curFrame = cmds.currentTime(q = True)
				Functions.setKeyframe('rotateX', curFrame, rxMin, rxMax)

			if ryOpt:
				ryMin = cmds.intField(UI.widgets['ryMinIntFld'], q = True, v = True)
				ryMax = cmds.intField(UI.widgets['ryMaxIntFld'], q = True, v = True)
				curFrame = cmds.currentTime(q = True)
				Functions.setKeyframe('rotateY', curFrame, ryMin, ryMax)

			if rzOpt:
				rzMin = cmds.intField(UI.widgets['rzMinIntFld'], q = True, v = True)
				rzMax = cmds.intField(UI.widgets['rzMaxIntFld'], q = True, v = True)
				curFrame = cmds.currentTime(q = True)
				Functions.setKeyframe('rotateZ', curFrame, rzMin, rzMax)

		endFrame = cmds.currentTime(q = True)
		cmds.playbackOptions(maxTime = endFrame)


	@staticmethod
	def setKeyframe(attr, curFrame, minVal, maxVal):
		cmds.setKeyframe(v = 0, at = attr)
		cmds.currentTime(curFrame + 10)
		cmds.setKeyframe(v = minVal, at = attr)
		cmds.currentTime(curFrame + 20)
		cmds.setKeyframe(v = 0, at = attr)
		cmds.currentTime(curFrame + 30)
		cmds.setKeyframe(v = maxVal, at = attr)
		cmds.currentTime(curFrame + 40)
		cmds.setKeyframe(v = 0, at = attr)