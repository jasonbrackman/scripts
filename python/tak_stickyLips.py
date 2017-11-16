'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date: 09/10/2015

Description:
This script set up sticky lips.

Usage:
import tak_stickyLips
reload(tak_stickyLips)
tak_stickyLips.UI()
'''


import maya.cmds as cmds
import maya.mel as mel
import tak_logging
from functools import partial
import tak_misc
import tak_cleanUpModel
import tak_lib
reload(tak_lib)

# creat logger
logger = tak_logging.Logger()
# set level
logger.setLevel('WARNING')


class UI(object):
	# Attributes #
	widgets = {}
	widgets['winName'] = 'stickyLipsWin'
	upperLipEdges = []
	lowerLipEdges = []

	# Methods #	
	@classmethod
	def __init__(cls):
		# Check the window exists
		if cmds.window(cls.widgets['winName'], exists = True):
			cmds.deleteUI(cls.widgets['winName'])

		cls.ui()

	@classmethod
	def ui(cls):
		cmds.window(cls.widgets['winName'], title = 'Sticky Lips Set Up')

		cls.widgets['mainColLo'] = cmds.columnLayout(adj = True, p = cls.widgets['winName'])

		cmds.button(label = 'Define Upper Lip Edges', c = partial(cls.defineEdges, 'upper'), p = cls.widgets['mainColLo'])
		cmds.button(label = 'Define Lower Lip Edges', c = partial(cls.defineEdges, 'lower'), p = cls.widgets['mainColLo'])
		cmds.text(label = 'Go to the default pose. Then click build button.', p = cls.widgets['mainColLo'])
		cmds.button(label = 'Build!', h = 30, c = cls.buildStickyLips, p = cls.widgets['mainColLo'])

		cmds.window(cls.widgets['winName'], e = True, w = 100, h = 50)
		cmds.showWindow(cls.widgets['winName'])


	@classmethod
	def defineEdges(cls, direction, *args):
		'''
		Save given edges.
		'''

		selEdges = cmds.ls(sl = True)

		if direction == 'upper':
			cls.upperLipEdges = selEdges
			logger.info('Upper Lip Edges: %s' %cls.upperLipEdges)

		elif direction == 'lower':
			cls.lowerLipEdges = selEdges
			logger.info('Lower Lip Edges: %s' %cls.lowerLipEdges)


	@classmethod
	def buildStickyLips(cls, *args):
		'''
		Main method.
		'''

		# Duplicate geometry
		oriGeo = cls.upperLipEdges[0].rsplit('.e')[0]
		
		logger.debug('Geometry Name: %s' %oriGeo)

		dupGeo = cmds.duplicate(oriGeo, n = oriGeo + '_stickyLipsSrcCrv_geo')[0]

		cmds.select(dupGeo, r = True)
		tak_cleanUpModel.delHis()
		tak_cleanUpModel.delInterMediObj()
		
		cmds.select(oriGeo, dupGeo, r = True)
		tak_misc.TransSkinWeights()

		# Convert polygon edges to curves
		dupGeoUpperEdges = cls.rplcStrInList(cls.upperLipEdges, oriGeo, dupGeo)
		cmds.select(dupGeoUpperEdges, r = True)
		upperLipCrv = mel.eval('polyToCurve -form 2 -degree 3;')
		upperLipCrv = cmds.rename(upperLipCrv[0], 'upper_lip_sticky_crv')

		dupGeoLowerEdges = cls.rplcStrInList(cls.lowerLipEdges, oriGeo, dupGeo)
		cmds.select(dupGeoLowerEdges, r = True)
		lowerLipCrv = mel.eval('polyToCurve -form 2 -degree 3;')
		lowerLipCrv = cmds.rename(lowerLipCrv[0], 'lower_lip_sticky_crv')

		# Create sticky lips curve
		stickyLipsCrv = cmds.duplicate(upperLipCrv, n = 'stickyLips_crv')[0]

		stickyLipsCrvShp = cmds.listRelatives(stickyLipsCrv, s = True)[0]
		upperLipCrvShp = cmds.listRelatives(upperLipCrv, s = True)[0]
		lowerLipCrvShp = cmds.listRelatives(lowerLipCrv, s = True)[0]
		
		avgCrvNode = cmds.createNode('avgCurves', n = 'stickyLips_avgCurve')
		cmds.setAttr('%s.automaticWeight' %avgCrvNode, 0)
		cmds.setAttr('%s.normalizeWeights' %avgCrvNode, 0)
		cmds.connectAttr('%s.worldSpace[0]' %upperLipCrvShp, '%s.inputCurve1' %avgCrvNode)
		cmds.connectAttr('%s.worldSpace[0]' %lowerLipCrvShp, '%s.inputCurve2' %avgCrvNode)
		cmds.connectAttr('%s.outputCurve' %avgCrvNode, '%s.create' %stickyLipsCrvShp)

		# Grouping
		stklGrp = cmds.createNode('transform', n = 'stickyLips_grp')
		cmds.parent(dupGeo, upperLipCrv, lowerLipCrv, stickyLipsCrv, stklGrp)
		cmds.setAttr('%s.visibility' %stklGrp, 0)

		# Assign wire deformer to the geometry
		wire = cmds.wire(oriGeo, w = stickyLipsCrv)[0]
		cmds.setAttr('%s.scale[0]' %wire, 0)
		cmds.setAttr('%s.envelope' %wire, 2)
		cmds.setAttr('%s.envelope' %wire, lock = True)
		cmds.connectAttr('%s.outputCurve' %avgCrvNode, '%sBaseWireShape.create' %stickyLipsCrv)

		# Weighting
		vtxNumber = cmds.polyEvaluate(oriGeo, vertex = True)
		cmds.percent(wire, '%s.vtx[0:%d]' %(oriGeo, vtxNumber - 1), v = 0)
		wireVtxList = cmds.polyListComponentConversion(cls.upperLipEdges, cls.lowerLipEdges, tv = True)
		cmds.percent(wire, wireVtxList, v = 1)


	@staticmethod
	def rplcStrInList(srcList, srchStr, rplcStr):
		'''
		Search and replace a specific string in the list.
		'''

		logger.debug('%s %s %s' %(srcList, srchStr, rplcStr))

		resultList = []

		for item in srcList:
			resultStr = item.replace(srchStr, rplcStr)
			resultList.append(resultStr)

		return resultList