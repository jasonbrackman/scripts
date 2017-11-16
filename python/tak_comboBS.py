'''
Author: Sang-tak Lee
Contact: chst27@gmail.com

Description:

'''

import maya.cmds as cmds
import maya.OpenMaya as OpenMaya

class UI():
	widgets = {}
	winName = 'cBSWin'

	@classmethod
	def __init__(cls):
		if cmds.window(cls.winName, exists = True):
			cmds.deleteUI(cls.winName)
		cls.ui()

	@classmethod
	def ui(cls):
		cmds.window(cls.winName, title = 'Combo Blend Shape', mnb = False, mxb = False)

		cmds.window(cls.winName, e = True, w = 300, h = 300)
		cmds.showWindow(cls.winName)