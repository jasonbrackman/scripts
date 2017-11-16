'''
Author: Sang-tak Lee
Contact: chst27@gmail.com

Description:
This script set up corrective joint system.
Corrective joint is driven by pose reader and have control.
Animator can modify corrective joint transform using control when needed.
Sometimes joint rotation value that drive corrective joint spit out wrong value because of gimbal lock.
That's why angle based pose reader is good for handling corrective joint. 

Usage:
1. Copy this script and paste in your scripts folder.

2. In maya python tab, run following code.
import tak_correctiveJoint
reload(tak_correctiveJoint)
tak_correctiveJoint.ui()
'''


import maya.cmds as cmds
import maya.mel as mel
from functools import partial
import re
import tak_createCtrl, tak_mayaUiUtils


def ui():
	winName = 'correctiveJointWin'

	if cmds.window(winName, exists = True):
		cmds.deleteUI(winName)

	cmds.window(winName, title = 'Corrective Joint UI')
	
	cmds.tabLayout('mainTabLay', tv = False)
	cmds.tabLayout('subTabLay', tv = False)
	cmds.columnLayout('mainColLay', adj = True)

	cmds.textFieldGrp('poseNameTexFld', label = 'Pose Name: ', columnWidth = [(1, 120), (2, 120)])
	cmds.popupMenu()
	cmds.menuItem(label = 'Load Sel', c = fillPoseName)
	cmds.intFieldGrp('targetPoseFrameIntFldGrp', label = 'Target Pose Frame: ')
	cmds.popupMenu()
	cmds.menuItem(label = 'Load Current Frame', c = partial(loadCurrentFrame, 'targetPoseFrameIntFldGrp'))
	cmds.intFieldGrp('startPoseFrameIntFldGrp', label = 'Start Pose Frame: ', value1 = 1)
	cmds.popupMenu()
	cmds.menuItem(label = 'Load Current Frame', c = partial(loadCurrentFrame, 'startPoseFrameIntFldGrp'))

	cmds.separator(h = 10, style = 'in')

	cmds.textFieldButtonGrp('drvrJointTexButGrp', label = 'Driver Joint: ', buttonLabel = '<<', columnWidth = [(1, 120), (2, 120), (3, 50)], bc = partial(loadSel, 'drvrJointTexButGrp'))
	cmds.textFieldButtonGrp('chldJointTexBtnGrp', label = 'Child Joint: ', buttonLabel = '<<', columnWidth = [(1, 120), (2, 120), (3, 50)], bc = partial(loadSel, 'chldJointTexBtnGrp'))
	cmds.textFieldButtonGrp('prntJointTexBtnGrp', label = 'Parent Joint: ', buttonLabel = '<<', columnWidth = [(1, 120), (2, 120), (3, 50)], bc = partial(loadSel, 'prntJointTexBtnGrp'))
	
	cmds.separator(h = 10, style = 'in')

	cmds.text(label = 'Select a vertex on problem pose.')
	cmds.button(label = 'Set Initial State', h = 30, c = initState)

	cmds.separator(h = 10, style = 'none')

	cmds.text(label = 'Place corrective joint using the sdk locator.')
	cmds.button(label = 'Set Pose State', h = 30, c = setPoseState)
	
	cmds.separator(h = 10, style = 'in')

	cmds.text(label = 'Go to the bind pose and select corrective joints.')
	cmds.rowColumnLayout('srchRplcRowColLo', numberOfColumns = 3, columnWidth = [(2, 50), (3, 50)])
	cmds.text(label = 'Driver Joint Search / Replace: ')
	cmds.textField('jntSrchTxtFld', text = '_L')
	cmds.textField('jntRplcTxtFld', text = '_R')
	cmds.text(label = 'Corrective Joint Search / Replace: ')
	cmds.textField('corJntSrchTxtFld', text = '_L')
	cmds.textField('corJntRplcTxtFld', text = '_R')
	cmds.setParent('mainColLay')

	cmds.button(label = 'Mirror Selected Corrective Joint', h = 30, c = mirrorCorJnt)

	cmds.window(winName, e = True, w = 250, h = 150)
	cmds.showWindow(winName)


def fillPoseName(*args):
	selObj = cmds.ls(sl = True)[0]
	selAttrs = cmds.channelBox('mainChannelBox', q = True, selectedMainAttributes = True)
	poseName = selObj
	
	if selAttrs:
		rawAttrVal = cmds.getAttr(selObj + '.' + selAttrs[0])
		niceAttrVal = int(round(rawAttrVal, 0))
		niceValName = ''
		if niceAttrVal >= 0:
			niceValName = 'p' + str(abs(niceAttrVal))
		else:
			niceValName = 'n' + str(abs(niceAttrVal))
		poseName += '_' + selAttrs[0] + '_' + niceValName

	cmds.textFieldGrp('poseNameTexFld', e = True, text = poseName)


def loadSel(wgtName):
	sel = cmds.ls(sl = True)[0]
	cmds.textFieldButtonGrp(wgtName, e = True, text = sel)

	# Fill parent joint text field and child joint text field.
	prntJnt = cmds.listRelatives(sel, p = True, type = 'joint')[0]
	cmds.textFieldButtonGrp('prntJointTexBtnGrp', e = True, text = prntJnt)
	childJnt = cmds.listRelatives(sel, c = True, type = 'joint')[0]
	cmds.textFieldButtonGrp('chldJointTexBtnGrp', e = True, text = childJnt)


def loadCurrentFrame(wgtName, *args):
	curFrame = cmds.currentTime(q = True)
	cmds.intFieldGrp(wgtName, e = True, value1 = curFrame)


def initState(*args):
	global corJntInst
	corJntInst = CorrectiveJoint()
	corJntInst.mainInit()


def setPoseState(*args):
	corJntInst.poseReaderFin()



class CorrectiveJoint:
	def __init__(self):
		# Initialize instance member varialbes
		self.poseName = cmds.textFieldGrp('poseNameTexFld', q = True, text = True)
		self.trgPoseFrame = cmds.intFieldGrp('targetPoseFrameIntFldGrp', q = True, value1 = True)
		self.startPoseFrame = cmds.intFieldGrp('startPoseFrameIntFldGrp', q = True, value1 = True)
		self.driverJnt = cmds.textFieldButtonGrp('drvrJointTexButGrp', q = True, text = True)
		self.childJnt = cmds.textFieldButtonGrp('chldJointTexBtnGrp', q = True, text = True)
		self.prntJnt = cmds.textFieldButtonGrp('prntJointTexBtnGrp', q = True, text = True)
		self.corJnt = self.poseName + '_cor_jnt'


	def mainInit(self):
		# Check if same pose name exists.
		if cmds.objExists(self.poseName + '_cor_jnt'):
			cmds.error('Pose name already exists!')

		# Store current target pose frame and go to the start pose frame.
		cmds.currentTime(self.startPoseFrame)

		# Create a corrective joint with selected vertex.
		self.createCorJnt()

		self.createLocGrp()

		self.poseReaderInit()

		# Back to the current pose frame.
		cmds.currentTime(self.trgPoseFrame)

		cmds.select(self.sdkLoc, r = True)


	def createCorJnt(self):
		'''
		Creat a corrective joint with selected vertex.
		'''

		vtx = cmds.ls(sl = True)[0]
		
		# Create a joint from selected vertex.
		vtxWldPos = cmds.pointPosition(vtx, world = True)
		cmds.select(cl = True)
		cmds.joint(p = (vtxWldPos), n = self.corJnt)
		cmds.CompleteCurrentTool()
		
		# Constraint for align to the driver joint.
		geo = vtx.split('.')[0]
		cmds.delete(cmds.orientConstraint(self.driverJnt, self.corJnt, mo = False))
		
		# Freeze transform
		cmds.makeIdentity(self.corJnt, apply = True)

		# Add influence.
		skinClst = mel.eval('findRelatedSkinCluster("%s");' %geo)
		cmds.skinCluster(skinClst, e = True, dr = 4, lw = True, wt = 0, ai = self.corJnt)
		cmds.setAttr('%s.liw' %self.corJnt, False)


	def createLocGrp(self):
		# Create set driven key locator
		self.sdkLoc = cmds.spaceLocator(n = '%s_sdk_loc' %self.corJnt)[0]
		cmds.delete(cmds.parentConstraint(self.corJnt, self.sdkLoc, mo = False, w = 1))
		cmds.parent(self.corJnt, self.sdkLoc)

		# Create constraint group
		corJntCnstGrp = cmds.createNode('transform', n = '%s_cnst_grp' %self.corJnt)
		cmds.delete(cmds.parentConstraint(self.corJnt, corJntCnstGrp, mo = False, w = 1))
		cmds.parent(self.sdkLoc, corJntCnstGrp)
		cmds.parentConstraint(self.prntJnt, corJntCnstGrp, mo = True)

		
		driverJntCorJntGrp = self.driverJnt + '_cor_jnt_grp'
		if cmds.objExists(driverJntCorJntGrp):
			cmds.parent(corJntCnstGrp, driverJntCorJntGrp)
		else:
			cmds.createNode('transform', n = driverJntCorJntGrp)
			cmds.parent(corJntCnstGrp, driverJntCorJntGrp)


	def poseReaderInit(self):
		# Get joints position
		driverJntPos = cmds.xform(self.driverJnt, q = True, ws = True, t = True)
		childJntPos = cmds.xform(self.childJnt, q = True, ws = True, t = True)
		
		# Create locator and place
		if not cmds.objExists(self.driverJnt + '_poseReader_base_loc'):
			self.baseLoc = cmds.spaceLocator(n = self.driverJnt + '_poseReader_base_loc')[0]
			cmds.xform(self.baseLoc, ws = True, t = driverJntPos)
			
			self.triggerLoc = cmds.spaceLocator(n = self.driverJnt + '_poseReader_trigger_loc')[0]
			cmds.xform(self.triggerLoc, ws = True, t = childJntPos)
			
		else:
			self.baseLoc = self.driverJnt + '_poseReader_base_loc'
			self.triggerLoc = self.driverJnt + '_poseReader_trigger_loc'

		self.startPoseLoc = cmds.spaceLocator(n = self.driverJnt + '_' + self.poseName + '_startPose_loc')[0]
		cmds.xform(self.startPoseLoc, ws = True, t = childJntPos)
		
		# Parenting
		if not self.triggerLoc in cmds.listRelatives(self.baseLoc, c = True):
			cmds.parent(self.triggerLoc, self.baseLoc)
		cmds.parent(self.startPoseLoc, self.baseLoc)
		
		# Create angle between and remap value node
		self.startToTargetPoseAnglBtwn = cmds.shadingNode('angleBetween', n = self.poseName + '_startToTargetPose_anglBtwn', asUtility = True)
		self.triggerToTargetPoseAnglBtwn = cmds.shadingNode('angleBetween', n = self.poseName + '_triggerToTargetPose_anglBtwn', asUtility = True)
		self.remapVal = cmds.shadingNode('remapValue', n = self.poseName + '_remapVal', asUtility = True)
		
		# Constraint
		cmds.pointConstraint(self.childJnt, self.triggerLoc, mo = False)
		cmds.parentConstraint(self.prntJnt, self.baseLoc, mo = True)


	def poseReaderFin(self):
		# Create target pose locator
		childJntPos = cmds.xform(self.childJnt, q = True, ws = True, t = True)
		self.trgPoseLoc = cmds.spaceLocator(n = self.driverJnt + '_' + self.poseName + '_targetPose_loc')[0]
		cmds.xform(self.trgPoseLoc, ws = True, t = childJntPos)

		# Parent target pose locator to the base locator
		cmds.parent(self.trgPoseLoc, self.baseLoc)

		# Connect attribute
		cmds.connectAttr('%s.translate' %self.startPoseLoc, '%s.vector1' %self.startToTargetPoseAnglBtwn, force = True)
		cmds.connectAttr('%s.translate' %self.trgPoseLoc, '%s.vector2' %self.startToTargetPoseAnglBtwn, force = True)
		
		cmds.connectAttr('%s.translate' %self.triggerLoc, '%s.vector1' %self.triggerToTargetPoseAnglBtwn, force = True)
		cmds.connectAttr('%s.translate' %self.trgPoseLoc, '%s.vector2' %self.triggerToTargetPoseAnglBtwn, force = True)
		
		cmds.connectAttr('%s.angle' %self.triggerToTargetPoseAnglBtwn, '%s.inputValue' %self.remapVal, force = True)
		cmds.connectAttr('%s.angle' %self.startToTargetPoseAnglBtwn, '%s.inputMax' %self.remapVal, force = True)

		# Set attributes
		cmds.setAttr('%s.outputMin' %self.remapVal, 1.0)
		cmds.setAttr('%s.outputMax' %self.remapVal, 0.0)

		# SDK
		cmds.setDrivenKeyframe('%s.translate' %self.sdkLoc, cd = '%s.outValue' %self.remapVal)
		cmds.setDrivenKeyframe('%s.rotate' %self.sdkLoc, cd = '%s.outValue' %self.remapVal)
		cmds.setDrivenKeyframe('%s.scale' %self.sdkLoc, cd = '%s.outValue' %self.remapVal)

		# Go back to the start pose frame
		cmds.currentTime(self.startPoseFrame)
		cmds.xform(self.sdkLoc, t = (0, 0, 0))

		cmds.setDrivenKeyframe('%s.translate' %self.sdkLoc, cd = '%s.outValue' %self.remapVal)
		cmds.setDrivenKeyframe('%s.rotate' %self.sdkLoc, cd = '%s.outValue' %self.remapVal)
		cmds.setDrivenKeyframe('%s.scale' %self.sdkLoc, cd = '%s.outValue' %self.remapVal)

		cmds.currentTime(self.trgPoseFrame)

		self.poseLocGrp()

		self.addCtrl()

		self.offLocShapeVis()


	def poseLocGrp(self):
		poseLocGrp = cmds.createNode('transform', n = self.poseName + '_pose_loc_grp')
		cmds.delete(cmds.parentConstraint(self.baseLoc, poseLocGrp, mo = False))
		cmds.parent(self.trgPoseLoc, self.startPoseLoc, poseLocGrp)
		cmds.parent(poseLocGrp, self.baseLoc)


	def addCtrl(self):
		'''
		Add control curve above to the joint.
		Animator can modify corrective joint using control curve.
		'''

		ctrl = tak_createCtrl.createCurve('sphere')
		ctrlNewName = cmds.rename(ctrl, self.corJnt + '_ctrl')
		cmds.delete(cmds.parentConstraint(self.sdkLoc, ctrlNewName))
		cmds.parent(self.corJnt, ctrlNewName)
		cmds.parent(ctrlNewName, self.sdkLoc)


	def offLocShapeVis(self):
		'''
		Trun off locator shape visibility.
		Because locator does not used when animation.
		'''

		# cmds.setAttr(self.baseLoc + 'Shape.visibility', False)
		# cmds.setAttr(self.triggerLoc + 'Shape.visibility', False)
		# cmds.setAttr(self.startPoseLoc + 'Shape.visibility', False)
		# cmds.setAttr(self.trgPoseLoc + 'Shape.visibility', False)
		cmds.setAttr(self.sdkLoc + 'Shape.visibility', False)



def mirrorCorJnt(*args):
	'''
	Mirror corrective joints.
	'''

	jntSrch = cmds.textField('jntSrchTxtFld', q = True, text = True)
	jntRplc = cmds.textField('jntRplcTxtFld', q = True, text = True)
	corJntSrch = cmds.textField('corJntSrchTxtFld', q = True, text = True)
	corJntRplc = cmds.textField('corJntRplcTxtFld', q = True, text = True)

	selcorJntLs = cmds.ls(sl = True)
	
	for corJnt in selcorJntLs:
		# Check if target objects exists.
		sdkLoc = corJnt + '_sdk_loc'
		sDriver = cmds.setDrivenKeyframe(sdkLoc, q=True, cd=True)[0].split('.')[0]
		print sDriver
		tDriver = re.sub(jntSrch, jntRplc, sDriver)
		tDriven = re.sub(corJntSrch, corJntRplc, sdkLoc)

		# In case target driver is not exists.
		if sDriver == tDriver:
			cmds.warning("Target driver object is not exists. Check the 'Driver Search/Replace' string.")
			return
		# In case target driven is not exists.
		elif sdkLoc == tDriven:
			cmds.warning("Target driven object is not exists. Check the 'Corrective Joint Search/Replace' string.")
			return

		# Mirror joint.
		eachPrnt = cmds.listRelatives(corJnt, parent = True)

		cmds.select(cl = True)
		cmds.joint(n='tmp_root_jnt', p=(0, 0, 0))
		cmds.parent(corJnt, 'tmp_root_jnt')

		cmds.select(corJnt, r = True)
		mirCorJnt = cmds.mirrorJoint(mirrorYZ = True, mirrorBehavior = True, searchReplace = (corJntSrch, corJntRplc))[0]

		if eachPrnt:
			cmds.parent(corJnt, eachPrnt[0])
		else:
			cmds.parent(corJnt, w = True)

		cmds.parent(mirCorJnt, w = True)
		cmds.delete('tmp_root_jnt')

		# Add influence.
		skClst = cmds.listConnections(corJnt, s = False, d = True, type = 'skinCluster')[0]
		geo = cmds.listConnections(skClst, s = False, d = True, type = 'mesh')[0]
		cmds.skinCluster(skClst, e = True, dr = 4, lw = True, wt = 0, ai = mirCorJnt)
		cmds.setAttr('%s.liw' %mirCorJnt, False)

		# Mirror skin weights.
		cmds.select(geo)
		cmds.MirrorSkinWeights()
		cmds.select(cl = True)

		# Create locator and group.
		createCtrl(mirCorJnt)

		# Constraint to the othersdie parent joint.
		pCnst = list(set(cmds.listConnections('%s_cnst_grp' %corJnt, s = False, d = True, type = 'parentConstraint')))[0]
		corJntPrntJnt = list(set(cmds.listConnections(pCnst, s = True, d = False, type = 'joint')))[0]
		mirPrntJnt = re.sub(jntSrch, jntRplc, corJntPrntJnt)
		cmds.parentConstraint(mirPrntJnt, '%s_cnst_grp' %mirCorJnt, mo = True)

		# Mirror pose reader.
		mirPoseReader(sdkLoc, jntSrch, jntRplc, corJntSrch, corJntRplc)

		# Mirror set driven key.
		driverAttr = cmds.setDrivenKeyframe(sdkLoc, q=True, cd=True)[0].split('.')[-1]
		rawDrivenAttrs = cmds.setDrivenKeyframe(sdkLoc, q=True, dn=True)
		for rawDrivenAttr in rawDrivenAttrs:
			drvnAttr = rawDrivenAttr.split('.')[-1]
			drvrVals = cmds.keyframe(rawDrivenAttr, q = True, fc = True)
			drvnVals = cmds.keyframe(rawDrivenAttr, q = True, vc = True)

			# Check if driver is more than two.
			if not drvrVals:
				cmds.warning("There is more than two drivers for source corrective joint's locator.")
				return

			for i in xrange(len(drvrVals)):
				if 'translate' in drvnAttr:
					cmds.setDrivenKeyframe('%s.%s' %(tDriven, drvnAttr), cd = '%s.%s' %(tDriver,driverAttr), dv = drvrVals[i], v = -drvnVals[i])
				elif 'rotate' in drvnAttr:
					cmds.setDrivenKeyframe('%s.%s' %(tDriven, drvnAttr), cd = '%s.%s' %(tDriver,driverAttr), dv = drvrVals[i], v = drvnVals[i])
				elif 'scale' in drvnAttr:
					cmds.setDrivenKeyframe('%s.%s' %(tDriven, drvnAttr), cd = '%s.%s' %(tDriver,driverAttr), dv = drvrVals[i], v = drvnVals[i])
				else:
					cmds.setDrivenKeyframe('%s.%s' %(tDriven, drvnAttr), cd = '%s.%s' %(tDriver,driverAttr), dv = drvrVals[i], v = drvnVals[i])


def createCtrl(mirCorJnt):
	# Create locator.
	sdkLoc = cmds.spaceLocator(n = '%s_sdk_loc' %mirCorJnt)[0]
	cmds.setAttr(sdkLoc + 'Shape.visibility', False)
	cmds.delete(cmds.parentConstraint(mirCorJnt, sdkLoc, mo = False, w = 1))
	cmds.parent(mirCorJnt, sdkLoc)

	# Create control.
	ctrl = tak_createCtrl.createCurve('sphere')
	ctrlNewName = cmds.rename(ctrl, mirCorJnt + '_ctrl')
	cmds.delete(cmds.parentConstraint(sdkLoc, ctrlNewName))
	cmds.parent(mirCorJnt, ctrlNewName)
	cmds.parent(ctrlNewName, sdkLoc)

	# Create constraint group.
	corJntCnstGrp = cmds.createNode('transform', n = '%s_cnst_grp' %mirCorJnt)
	cmds.delete(cmds.parentConstraint(mirCorJnt, corJntCnstGrp, mo = False, w = 1))
	cmds.parent(sdkLoc, corJntCnstGrp)


def mirPoseReader(sdkLoc, jntSrch, jntRplc, corJntSrch, corJntRplc):
	'''
	Description
		Mirror pose reader that connected to corrective joint.

	Parameters
		sdkLoc: string - Source locator that applied set driven keyframe.

	Retruns
		None
	'''

	allCnnts = cmds.listHistory(sdkLoc, ac = True)

	# Retrive pose reader base locators.
	trigLoc = [x for x in allCnnts if 'trigger_loc' in x and cmds.objectType(x) == 'transform'][0]
	baseLoc = cmds.listRelatives(trigLoc, p = True)[0]

	mirTrigLocName = re.sub(corJntSrch, corJntRplc, trigLoc)
	mirBaseLocName = re.sub(corJntSrch, corJntRplc, baseLoc)

	# Retrive pose reader locators.
	startPoseLoc = [x for x in allCnnts if 'startPose_loc' in x][0]
	trgPoseLoc = [x for x in allCnnts if 'targetPose_loc' in x][0]
	poseReaderLocGrp = cmds.listRelatives(trgPoseLoc, p = True)[0]

	mirStartPoseLocName = re.sub(corJntSrch, corJntRplc, startPoseLoc)
	mirTrgPoseLocName = re.sub(corJntSrch, corJntRplc, trgPoseLoc)
	mirPoseReaderLocGrpName = re.sub(corJntSrch, corJntRplc, poseReaderLocGrp)

	# Extra nodes.
	anglBtwns = [x for x in allCnnts if 'anglBtwn' in x]
	remapVal = [x for x in allCnnts if 'remapVal' in x][0]

	mirAnglBtwnNames = []
	for anglBtwn in anglBtwns:
		mirAnglBtwnNames.append(re.sub(corJntSrch, corJntRplc, anglBtwn))
	mirRemapValName = re.sub(corJntSrch, corJntRplc, remapVal)

	# Retrive joints.
	drvrJntPrnt = list(set(cmds.ls(cmds.listConnections(list(set(cmds.listConnections(baseLoc, d = False))), d = False), type = 'joint')))[0]
	drvrJnt = cmds.listRelatives(drvrJntPrnt, c = True, type = 'joint')[0]
	drvrJntChld = cmds.listRelatives(drvrJnt, c = True, type = 'joint')[0]

	mirDrvrJntPrntName = re.sub(jntSrch, jntRplc, drvrJntPrnt)
	mirDrvrJntName = re.sub(jntSrch, jntRplc, drvrJnt)
	mirDrvrJntChldName = re.sub(jntSrch, jntRplc, drvrJntChld)

	# If pose reader base locator is not exists then create.
	mirPoseReaderBaseLoc = mirDrvrJntName + '_poseReader_base_loc'
	if not cmds.objExists(mirDrvrJntName + '_poseReader_base_loc'):
		cmds.spaceLocator(n = mirPoseReaderBaseLoc)
		cmds.delete(cmds.parentConstraint(mirDrvrJntName, mirPoseReaderBaseLoc, mo = False))
		cmds.parentConstraint(mirDrvrJntPrntName, mirPoseReaderBaseLoc, mo = True)

		mirPoseReaderTriggerLoc = cmds.spaceLocator(n = mirDrvrJntName + '_poseReader_trigger_loc')
		cmds.pointConstraint(mirDrvrJntChldName, mirPoseReaderTriggerLoc, mo = False)

		cmds.parent(mirPoseReaderTriggerLoc, mirPoseReaderBaseLoc)

	# Create pose reader group.
	cmds.group(n = mirPoseReaderLocGrpName, em = True)
	cmds.delete(cmds.parentConstraint(mirPoseReaderBaseLoc, mirPoseReaderLocGrpName, mo = False))
	cmds.parent(mirPoseReaderLocGrpName, mirPoseReaderBaseLoc)

	# Create pose reader locators.
	cmds.spaceLocator(n = mirStartPoseLocName)
	cmds.spaceLocator(n = mirTrgPoseLocName)
	cmds.parent(mirStartPoseLocName, mirTrgPoseLocName, mirPoseReaderLocGrpName)

	# Move to the mirrored position.
	startPoseLocTrans = cmds.xform(startPoseLoc, q = True, t = True, ws = True)
	cmds.xform(mirStartPoseLocName, t = [-startPoseLocTrans[0], startPoseLocTrans[1], startPoseLocTrans[2]], ws = True)
	trgPoseLocTrans = cmds.xform(trgPoseLoc, q = True, t = True, ws = True)
	cmds.xform(mirTrgPoseLocName, t = [-trgPoseLocTrans[0], trgPoseLocTrans[1], trgPoseLocTrans[2]], ws = True)

	# Create extra nodes.
	for mirAnglBtwnName in mirAnglBtwnNames:
		cmds.createNode('angleBetween', n = mirAnglBtwnName)
	
	cmds.createNode('remapValue', n = mirRemapValName)
	cmds.setAttr(mirRemapValName + '.outputMin', 1)
	cmds.setAttr(mirRemapValName + '.outputMax', 0)

	# Connections.
	for mirAnglBtwnName in mirAnglBtwnNames:
		if 'triggerToTargetPose' in mirAnglBtwnName:
			cmds.connectAttr(mirTrigLocName + '.translate', mirAnglBtwnName + '.vector1')
			cmds.connectAttr(mirTrgPoseLocName + '.translate', mirAnglBtwnName + '.vector2')
			cmds.connectAttr(mirAnglBtwnName + '.angle', mirRemapValName + '.inputValue')
		elif 'startToTargetPose' in mirAnglBtwnName:
			cmds.connectAttr(mirStartPoseLocName + '.translate', mirAnglBtwnName + '.vector1')
			cmds.connectAttr(mirTrgPoseLocName + '.translate', mirAnglBtwnName + '.vector2')
			cmds.connectAttr(mirAnglBtwnName + '.angle', mirRemapValName + '.inputMax')