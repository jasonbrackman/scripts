'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date: 12/15/2016

Description:
This script is created for to edit maya ascii scene file without opening.

Usage:
import tak_editMayaAsciiFile
reload(tak_editMayaAsciiFile)
tak_editMayaAsciiFile.ui()
'''



import maya.cmds as cmds
import re, os



def ui():
	winName = 'editMaWin'
	if cmds.window(winName, exists = True):
		cmds.deleteUI(winName)

	cmds.window(winName, title = 'Edit Maya ASCII', mnb = False, mxb = False)
	
	cmds.columnLayout('mainColLo', adj = True, rowSpacing = 5)
	
	cmds.rowColumnLayout('fileLsRowColLo', numberOfColumns = 2, columnWidth = [(1, 500)])
	cmds.textScrollList('fileLsTxtScrLs', allowMultiSelection = True)
	cmds.columnLayout('fileLsBtnColLo', adj = True, rowSpacing = 5)
	cmds.button(label = '+', c = addFileToLs)
	cmds.button(label = '-', c = rmvFileFromLs)
	cmds.setParent('mainColLo')

	cmds.button(label = 'Apply', c = main, h = 50)
	
	cmds.window(winName, e = True, w = 300, h = 100)
	cmds.showWindow(winName)


def main(*args):
	filePathToEditLs = cmds.textScrollList('fileLsTxtScrLs', q = True, allItems = True)

	charVisorCtrlNameDic = {
	'TP_001RN': 'vizer_ctrl', 
	'cyan_001RN': 'viser_ctrl', 
	'toto_001RN': 'vizer_ctrl', 
	'hammer_001RN': 'visor_ctrl'
	}

	charRefNodeCntnsDic = {
	'TP_001RN': '''\t\t2 "|cha|TP_001:root|TP_001:rig|TP_001:Group|TP_001:ExtraMain|TP_001:Main|TP_001:Sub|TP_001:extra_ctrl_grp|TP_001:vizer_rig_grp|TP_001:vizer_ctrl_pos|TP_001:vizer_ctrl_auto|TP_001:vizer_ctrl_extra|TP_001:vizer_ctrl"\n\t\t"rotateX" " 0"\n''', 
	'cyan_001RN': '''\t\t2 "|cha|cyan_001:root|cyan_001:rig|cyan_001:Group|cyan_001:ExtraMain|cyan_001:Main|cyan_001:Sub|cyan_001:extra_ctrl_grp|cyan_001:viser_rig_grp|cyan_001:viser_ctrl_pos|cyan_001:viser_ctrl_auto|cyan_001:viser_ctrl_extra|cyan_001:viser_ctrl"\n\t\t"rotateX" " 0"\n''', 
	'toto_001RN': '''\t\t2 "|cha|toto_001:root|toto_001:rig|toto_001:Group|toto_001:ExtraMain|toto_001:Main|toto_001:Sub|toto_001:extra_ctrl_grp|toto_001:viser_rig_grp|toto_001:viser_ctrl_pos|toto_001:viser_ctrl_auto|toto_001:viser_ctrl_extra|toto_001:vizer_ctrl"\n\t\t"rotateX" " 0"\n''', 
	'hammer_001RN': '''\t\t2 "|cha|hammer_001:root|hammer_001:rig|hammer_001:Group|hammer_001:ExtraMain|hammer_001:Main|hammer_001:Sub|hammer_001:extra_ctrl_grp|hammer_001:viser_rig_grp|hammer_001:viser_ctrl_pos|hammer_001:viser_ctrl_auto|hammer_001:viser_ctrl_extra|hammer_001:visor_ctrl"\n\t\t"rotateX" " 0"\n'''
	}

	for filePath in filePathToEditLs:
		# Open file and read contents.
		fR = open(filePath, 'r')
		cntns = fR.read()
		fR.close()

		# Delete vi???_ctrl's keyframe.
		# newCntns = re.sub('createNode animCurveTA .*vi.*\n\tsetAttr.*\n\tsetAttr.*\n\tsetAttr.*[\n];', '', cntns)
		animCrvCntns = re.search(r'(createNode animCurveTA -n "vi.*)[createNode|select]', cntns, re.DOTALL)
		if animCrvCntns:
			newCntns = cntns.replace(animCrvCntns.group(1), '')
		else:
			newCntns = cntns

		for refNode in charRefNodeCntnsDic.keys():
			# If vi???_ctrl exists in reference edtis, replace value.
			namespace = refNode.split('RN')[0]
			viRefEditCntns = re.search(r'\t\t2 ".*%s.*%s" \n\t\t"rotateX" "(.*?)"' %(namespace, charVisorCtrlNameDic[refNode]), newCntns)
			if viRefEditCntns:
				print viRefEditCntns.group()
				val = viRefEditCntns.group(1)
				newCntns = re.sub(val, '0', newCntns)
			# else:
			# 	# If vi???_ctrl is not exists add reference edit contents.
			# 	matchObj = re.search(r'(createNode reference -n "%s".*?)(\t\t2 .*?)(\t\t5 \d .*)(lockNode)' %refNode, newCntns, re.DOTALL)

			# 	if matchObj:
			# 		cntnsToAdd = charRefNodeCntnsDic[refNode]
			# 		addedCntns = matchObj.group(1) + matchObj.group(2) + cntnsToAdd + matchObj.group(3) + matchObj.group(4)

			# 		newCntns = newCntns.replace(matchObj.group(), addedCntns)

		# Create backup file.
		sepOriPath = filePath.rsplit('.', 1)
		backupFilePath = sepOriPath[0] + '_backup' + '.' + sepOriPath[1]
		bFW = open(backupFilePath, 'w')
		bFW.write(cntns)
		bFW.close()

		# Overwrite original file.
		fw = open(filePath, 'w')
		fw.write(newCntns)
		fw.close()


def addFileToLs(*args):
	curScenePath = cmds.file(q = True, sceneName = True)
	curWorkDir = os.path.dirname(curScenePath)

	filePath = cmds.fileDialog2(fileMode = 4, caption = 'Load', fileFilter = '*.ma', startingDirectory = curWorkDir)
	print filePath
	cmds.textScrollList('fileLsTxtScrLs', e = True, append = filePath)


def rmvFileFromLs(*args):
	selItemLs = cmds.textScrollList('fileLsTxtScrLs', q = True, selectItem = True)

	cmds.textScrollList('fileLsTxtScrLs', e = True, removeItem = selItemLs)