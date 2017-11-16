"""
Author: Sang-tak Lee
Contact: chst27@gmail.com

Created: 07/20/2017
Updated: 09/22/2017

Description:
	Utils for xgen.
"""


import pymel.core as pm

import tak_lib


def assignNewSolver(solver=None, hairSystems=None):
	"""
	Assign new nucleus solver to the selected hair systems or given hairSystem list
	Args:
		solver: Nucleus node or nucleus node name
		hairSystems (list): Hair system list

	Returns:
		None
	"""
	if not hairSystems:
		hairSystems = pm.ls(sl=True)

	# Prepare solver
	if not solver:
		solver = pm.createNode('nucleus')
	if isinstance(solver, basestring):
		solver = pm.PyNode(solver)
	time1 = pm.PyNode('time1')
	time1.outTime.connect(solver.currentTime, f=True)

	for hairSystem in hairSystems:
		if isinstance(hairSystem, basestring):
			hairSystem = pm.PyNode(hairSystem)
		if type(hairSystem) == pm.nodetypes.Transform:
			hairSystem = hairSystem.getShape()

		solver.startFrame.connect(hairSystem.startFrame, f=True)

		index = tak_lib.findMultiAttributeEmptyIndex(node=solver, attribute='outputObjects')
		solver.outputObjects[index].connect(hairSystem.nextState, f=True)

		index = tak_lib.findMultiAttributeEmptyIndex(node=solver, attribute='inputActive')
		hairSystem.currentState.disconnect()
		hairSystem.currentState.connect(solver.inputActive[index])

		index = tak_lib.findMultiAttributeEmptyIndex(node=solver, attribute='inputActiveStart')
		hairSystem.startState.disconnect()
		hairSystem.startState.connect(solver.inputActiveStart[index])


def connectScalpToPatch(scalp, patch):
	"""
	Description
		Connect scalp mesh to xgen patch to follow guides to scalp mesh.

	Parameters
		scalp: string, Scalp mesh name.
		patch: string, Xgen patch name.

	Returns
		None

	Examples
		tak_xgenUtils.connectScalpToPatch(scalp="hairScalp_geo", patch="hairScalp_geo_teajung_frontHair")
	"""

	patchShp = pm.listRelatives(patch)[0]
	pm.connectAttr(scalp + ".worldMesh", patchShp + ".geometry")
	pm.connectAttr(scalp + ".matrix", patchShp + ".transform")


def connectScalpToFollicle(scalp, follicle):
	"""
	Description
		Connect scalp mesh to follicle.

	Parameters
		scalp: string, Scalp mesh name.
		follicle: string, Follicle name.

	Returns
		None

	Examples
		tak_xgenUtils.connectScalpToFollicle(scalp="hairScalp_geo", follicle="follicle1")
	"""

	folShp = pm.listRelatives(follicle)[0]
	pm.connectAttr(scalp + ".outMesh", folShp + ".inputMesh", f=True)
	pm.connectAttr(scalp + ".worldMatrix", folShp + ".inputWorldMatrix", f=True)


def attachGuideToScalp():
	xgGuides = pm.ls(type='xgmSplineGuide')
	for xgGuide in xgGuides:
		xgmMakeGuide = xgGuide.toMakeGuide.connections()[0]
		xgmMakeGuide.outputMesh.connect(xgGuide.inputMesh, f=True)
