'''
Author: Sang-tak Lee
Contact: chst27@gmail.com

usage:
import tak_matchTransform
tak_matchTransform.UI()
'''

import maya.cmds as cmds


# UI
def UI():
	if cmds.window('mtWin', exists=True): cmds.deleteUI('mtWin')

	cmds.window('mtWin', title='Match Transform', mnb=False, mxb=False)

	cmds.tabLayout('mainTab', tv=False)
	cmds.tabLayout('subTab', tv=False, scrollable=True)

	cmds.formLayout('mainForm', nd=100, w=160, h=190)

	cmds.text('desText', label="Slect source and the traget.\nCan't mirror in constraint mode.", align='left')

	cmds.optionMenu('modeOptMenu', label='Mode:', cc=optMenuChangeCmd)
	cmds.menuItem(label='Constraint')
	cmds.menuItem(label='Xform')

	cmds.checkBoxGrp('optChkGrp', numberOfCheckBoxes=3, labelArray3=['Translate', 'Rotate', 'Scale'], vertical=True,
	                 v1=True, v2=True)
	cmds.checkBox('rvrsSel', label='Reverse Sel')
	cmds.checkBox('mirChk', label='Mirror X', vis=False)
	cmds.checkBox('loChk', label='Local', vis=False)
	cmds.button('matchButton', label='Match!', c=match)

	# arrange mainForm
	cmds.formLayout('mainForm', edit=True,
	                attachForm=[('desText', 'top', 5), ('desText', 'left', 5), ('modeOptMenu', 'left', 5),
	                            ('matchButton', 'bottom', 5), ('matchButton', 'right', 5), ('matchButton', 'left', 5),
	                            ('optChkGrp', 'left', 5), ('rvrsSel', 'right', 1.5)],
	                attachControl=[('modeOptMenu', 'top', 5, 'desText'), ('optChkGrp', 'top', 5, 'modeOptMenu'),
	                               ('matchButton', 'top', 5, 'optChkGrp'), ('loChk', 'left', 5, 'optChkGrp'),
	                               ('loChk', 'bottom', 5, 'matchButton'), ('mirChk', 'bottom', 0, 'loChk'),
	                               ('mirChk', 'left', 5, 'optChkGrp'), ('rvrsSel', 'top', 5, 'modeOptMenu')])

	cmds.setParent('subTab')

	cmds.window('mtWin', e=True, w=180, h=210)
	cmds.showWindow('mtWin')


# match button
def match(*args):
	# get the state of options
	modeOpt = cmds.optionMenu('modeOptMenu', q=True, v=True)
	tOpt = cmds.checkBoxGrp('optChkGrp', q=True, v1=True)
	rOpt = cmds.checkBoxGrp('optChkGrp', q=True, v2=True)
	sOpt = cmds.checkBoxGrp('optChkGrp', q=True, v3=True)
	mOpt = cmds.checkBox('mirChk', q=True, v=True)
	loOpt = cmds.checkBox('loChk', q=True, v=True)
	rvrsOpt = cmds.checkBox('rvrsSel', q=True, v=True)

	selList = cmds.ls(orderedSelection=True)
	# if first selected item is component, trackSlectionOrder
	if '[' in selList[0]: cmds.selectPref(trackSelectionOrder=True)
	src = selList[0]
	trg = selList[1]

	if rvrsOpt:
		src, trg = trg, src

	if modeOpt == 'Xform':
		matchWithXfrom(tOpt, rOpt, sOpt, mOpt, src, trg, loOpt)
	else:
		matchWithConst(tOpt, rOpt, sOpt, src, trg)

	cmds.select(trg, r=True)


def matchWithXfrom(translateOption, rotateOption, scaleOption, mirrorOption, source, target, localOption):
	# Get source information
	sourceTranslate = cmds.getAttr('%s.translate' % source)[0] if localOption else cmds.xform(source, q=True, ws=True, t=True)
	sourceRotate = cmds.xform(source, q=True, ws=True, ro=True)
	sourceScale = cmds.xform(source, q=True, ws=True, s=True)

	# Apply to the target
	if mirrorOption:
		sourceTranslate = [-sourceTranslate[0], sourceTranslate[1], sourceTranslate[2]]
		sourceRotate = [sourceRotate[0], sourceRotate[1], sourceRotate[2]]
		if localOption:
			sourceRotate = cmds.xform(source, q=True, r=True, ro=True)
			sourceScale = cmds.xform(source, q=True, r=True, s=True)
			sourceRotate = [sourceRotate[0], sourceRotate[1], sourceRotate[2]]

	if localOption:
		cmds.setAttr('%s.translate' % target, sourceTranslate[0], sourceTranslate[1], sourceTranslate[2])
	else:
		cmds.xform(target, t=sourceTranslate, ws=True)

	if rotateOption:
		cmds.xform(target, ro=sourceRotate, ws=True)
		if localOption:
			cmds.xform(target, ro=sourceRotate)
	if scaleOption: cmds.xform(target, s=sourceScale, ws=True)


def matchWithConst(tOpt, rOpt, sOpt, src, trg):
	# constraint depend on option
	if tOpt: cmds.delete(cmds.pointConstraint(src, trg, mo=False))
	if rOpt: cmds.delete(cmds.orientConstraint(src, trg, mo=False))
	if sOpt: cmds.delete(cmds.scaleConstraint(src, trg, mo=False))


def optMenuChangeCmd(*args):
	curMode = cmds.optionMenu('modeOptMenu', q=True, v=True)
	if curMode == 'Xform':
		cmds.checkBox('loChk', e=True, vis=True)
		cmds.checkBox('mirChk', e=True, vis=True)
	elif curMode == 'Constraint':
		cmds.checkBox('loChk', e=True, vis=False)
		cmds.checkBox('mirChk', e=True, vis=False)
