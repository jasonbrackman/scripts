'''
Author: Lee Sang-tak
Contact: chst27@gmail.com

usage:
import tak_transferSkinWeight
reload(tak_transferSkinWeight)
tak_transferSkinWeight.UI()
'''
import maya.cmds as cmds
import maya.mel as mel
from functools import partial


def UI():
	win = 'TSWin'
	if cmds.window(win, exists = True):
		cmds.deleteUI(win)

	cmds.window(win, title = 'Transfer Skin Weight UI')

	cmds.columnLayout('mainColLay', adj = True)

	cmds.textFieldButtonGrp('srcInf', label = 'Source Influence: ', buttonLabel = '<<', columnWidth = [(1, 90), (2, 100)], bc = partial(loadSel, 'srcInf'))
	cmds.textFieldButtonGrp('trgInf', label = 'Target Influence: ', buttonLabel = '<<', columnWidth = [(1, 90), (2, 100)], bc = partial(loadSel, 'trgInf'))
	cmds.button(label = 'Transfer', h = 50, c = main)

	cmds.window(win, e = True, w = 100, h = 100)
	cmds.showWindow(win)

def main(*args):
	vtxList = cmds.ls(sl = True)

	srcInf = cmds.textFieldButtonGrp('srcInf', q = True, text = True)
	trgInf = cmds.textFieldButtonGrp('trgInf', q = True, text = True)

	# get skin cluster
	skinGeo = vtxList[0].split('.vtx')[0]
	cmds.select(skinGeo, r = True)
	mel.eval('string $selList[] = `ls -sl`;')
	mel.eval('string $source = $selList[0];')	
	skinCluster = mel.eval('findRelatedSkinCluster($source);')

	for vtx in vtxList:
		# get skin weight value
		srcInfSkinVal = cmds.skinPercent( skinCluster, vtx, transform = srcInf, query = True )
		trgInfSkinVal = cmds.skinPercent( skinCluster, vtx, transform = trgInf, query = True )

		resultSkinVal = srcInfSkinVal + trgInfSkinVal

		# transfer skin weights
		cmds.skinPercent( skinCluster, vtx, transformValue = [(srcInf, 0), (trgInf, resultSkinVal)])

def loadSel(widget, *args):
	sel = cmds.ls(sl = True)
	cmds.textFieldButtonGrp(widget, e = True, text = sel[0])

