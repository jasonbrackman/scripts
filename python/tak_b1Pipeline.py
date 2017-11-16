'''
Author: Sang-tak Lee
Contact: chst27@gmail.com

Description:
Module for add extra functions to the b1 pipeline.

Usage:

'''

import maya.cmds as cmds
import maya.mel as mel
import os


def delDevRelHistory(type):
	'''
	Description:
	Function for delete release or develop history.

	Arguments:
	type(string)

	Returns:
	'''

	# Get selected history path
	if type == 'asset':
		selHisPath = mel.eval('textFieldButtonGrp -q -text astFileLocField;')
		#P:/1503_A63/4.Asset/cha/ryuji/rig/develop/v002/
	elif type == 'shot':
		selHisPath = mel.eval('textFieldButtonGrp -q -text shtFileLocField;')
		#P:/1503_A63/5.Shot/BG/T01A/BG_T01A_maya/scenes/ani/master/develop/v004/

	# Delete folder
	os.rmdir(selHisPath)

	# Modify xml file in _info folder

	# Refresh ui



