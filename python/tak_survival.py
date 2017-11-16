'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date: 10/16/2015

Description:
Scripts For Survival project.

Usage:
import tak_survival
reload(tak_survival)
tak_survival.ui()
'''

import maya.cmds as cmds
import re


def ui():
	winName = 'svLitWin'

	if cmds.window(winName, exists = True):
		cmds.deleteUI(winName)

	cmds.window(winName, title = 'Survival Lighting Scene Set Up')

	cmds.columnLayout('mainColLo', adj = True, columnOffset = ['left', 2.5])
	cmds.text(label = '1. Select shot camera to set time slider range.', h = 15, align = 'left')
	cmds.button(label = 'Apply', c = timeRange)

	cmds.separator(h = 15, style = 'in')

	cmds.text(label = '2. Bake dynamic geometries with geometry cache.', h = 15, align = 'left')

	cmds.separator(h = 15, style = 'in')

	cmds.text(label = '3. Select character and prop geometry groups to set up render layers.', h = 15, align = 'left')
	cmds.button(label = 'Apply', c = setChar)
	
	cmds.separator(h = 15, style = 'in')

	cmds.text(label = '4. Select bg geometry groups to set up render layers.', h = 15, align = 'left')
	cmds.button(label = 'Apply', c = setBG)
	
	cmds.separator(h = 15, style = 'in')

	cmds.text(label = '5. Set lights position to the shot camera.', h = 15, align = 'left')
	cmds.button(label = 'Apply', c = setLit)
	
	cmds.window(winName, e = True, w = 300, h = 100)
	cmds.showWindow(winName)


def setFrameRange(*arg):
	global shotCam
	shotCam = cmds.ls(sl = True)[0]
	srchRslt = re.search(r'_(\d+)_(\d+)', shotCam)
	cmds.playbackOptions(minTime = srchRslt.group(1))
	cmds.playbackOptions(maxTime = srchRslt.group(2))


def timeRange(*arg):
	# Set to normal mode for all display layers
	dpLayers = cmds.ls(type = 'displayLayer')
	for dpLay in dpLayers:
		if dpLay == 'defaultLayer':
			continue
		cmds.setAttr('%s.displayType' %dpLay, 0)

	# Set fps to PAL
	cmds.currentUnit(time = 'pal')

	setFrameRange()

	cmds.editRenderLayerGlobals(currentRenderLayer = 'defaultRenderLayer')

	# Turn off dummy
	allCtrls = cmds.ls(type = 'transform')
	for ctrl in allCtrls:
		if 'ROOT' in ctrl:
			if cmds.objExists('%s.Dummy' %ctrl):
				cmds.cutKey(ctrl, at = 'Dummy', cl = True)
				cmds.setAttr('%s.Dummy' %ctrl, 0)


def setChar(*arg):
	'''
	Smooth and render layer set up for selected characters
	'''

	cmds.displaySmoothness(polygonObject = 3)

	allTrnsf = cmds.listRelatives(allDescendents = True, type = 'transform')
	if allTrnsf:
		for trnsf in allTrnsf:
			if 'facial' in trnsf:
				cmds.setAttr('%s.visibility' %trnsf, 0)

	selChs = cmds.ls(sl = True)

	for sel in selChs:
		cmds.editRenderLayerMembers('ch_master', sel, noRecurse = True)

	cmds.editRenderLayerGlobals(currentRenderLayer = 'ch_shadows')
	for sel in selChs:
		cmds.editRenderLayerMembers('ch_shadows', sel, noRecurse = True)
	allShps = cmds.listRelatives(allDescendents = True, type = 'mesh', fullPath = True)
	for shp in allShps:
			cmds.setAttr('%s.primaryVisibility' %shp, 0)

	cmds.editRenderLayerGlobals(currentRenderLayer = 'defaultRenderLayer')


def setBG(*arg):
	'''
	Smooth and render layer set up for selected BGs
	'''

	cmds.displaySmoothness(polygonObject = 3)

	selBGs = cmds.ls(sl = True)

	cmds.editRenderLayerGlobals(currentRenderLayer = 'ch_master')
	for sel in selBGs:
		cmds.editRenderLayerMembers('ch_master', sel, noRecurse = True)
	allShps = cmds.listRelatives(allDescendents = True, type = 'mesh', fullPath = True)
	for shp in allShps:
			cmds.setAttr('%s.primaryVisibility' %shp, 0)

	cmds.editRenderLayerGlobals(currentRenderLayer = 'bg_master')
	for sel in selBGs:
		cmds.editRenderLayerMembers('bg_master', sel, noRecurse = True)

	cmds.editRenderLayerGlobals(currentRenderLayer = 'ch_shadows')
	for sel in selBGs:
		cmds.editRenderLayerMembers('ch_shadows', sel, noRecurse = True)
	allShps = cmds.listRelatives(allDescendents = True, type = 'mesh', fullPath = True)
	for shp in allShps:
			cmds.setAttr('%s.castsShadows' %shp, 0)

	cmds.editRenderLayerGlobals(currentRenderLayer = 'defaultRenderLayer')


def setLit(*arg):
	'''
	Move lights to shot camera position
	'''

	lights = ['ch_key_light', 'bg_key_light', 'bg_ch_back_light1', 'bg_ch_back_light2']
	cmds.select(cl = True)
	for light in lights:
		pntCnst = cmds.pointConstraint(shotCam, light, mo = False)
		cmds.delete(pntCnst)
		cmds.select(light, add = True)


def copyRdLyr():
	allRdLyr = cmds.ls(type = 'renderLayer')
	doNotCopyRdLyrs = ['ch_master', 'bg_master', 'ch_shadows', 'ch_master_a', 'bg_master_a', 'cha_matte', 'bg_matte']
	for rdLyr in allRdLyr:
		if not rdLyr in doNotCopyRdLyrs and not 'defaultRenderLayer' in rdLyr:
			print rdLyr
			mel.eval('renderLayerEditorCopyLayer RenderLayerTab %s;' %rdLyr)