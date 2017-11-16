'''
Author: Sang-tak Lee
Contact: chst27@gmail.com

Description:
Script to help clean up animation scene.

Usage:
import tak_cleanUpAniScene
reload(tak_cleanUpAniScene)
tak_cleanUpAniScene.ui()
'''


import maya.cmds as cmds


def ui():
	winName = 'CLEAN_UP_ANI_SCENE_WIN'
	if cmds.window(winName, exists = True):
		cmds.deleteUI(winName)

	cmds.window(winName, title = 'Clean Up Animation Scene', mnb = False, mxb = False)

	cmds.columnLayout('mainColLo', p = winName, adj = True)

	cmds.button(label = "Delete Display Layers", c = delDpLayers)

	cmds.window(winName, e = True, w = 200, h = 5)
	cmds.showWindow(winName)


def delDpLayers(*args):
	'''
	Delete display layers.
	'''
	
	dpLyrList = cmds.ls(type = 'displayLayer')
	
	for dpLyr in dpLyrList:
		if ('defaultLayer' in dpLyr) or ('geo_layer' in dpLyr) or ('jointLayer' in dpLyr):
			print dpLyr + ' was kept.'
			pass
		else:
			print dpLyr + ' was deleted.'
			cmds.delete(dpLyr)