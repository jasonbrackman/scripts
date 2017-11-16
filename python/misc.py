import maya.cmds as cmds
import random



# Set Relative for Selected Cluster #
clus = cmds.ls(sl = True)
for clu in clus:
	cmds.setAttr(clu + "Cluster.relative", 1)
	



	
# Print Matrix #    
sel = cmds.ls(sl = True)[0]
matrixArray = cmds.getAttr(sel + '.matrix')
matrix = zip(matrixArray[0::4], matrixArray[1::4], matrixArray[2::4], matrixArray[3::4])
for vector in matrix:
	print vector





# remove selected items from specific sets
selList = cmds.ls(sl = True)
cmds.sets(selList, rm = 'Set_CH_lamb')

# add selected items to specific sets
selList = cmds.ls(sl = True)
cmds.sets(selList, add = 'Set_CH_lamb')





# Unlock and Display All Attribute #
mel.eval('source channelBoxCommand;')

attrList = ['translate', 'rotate', 'scale']
axisList = ['X', 'Y', 'Z']
selList = cmds.ls(sl = True)
for sel in selList:
	for attr in attrList:
		for axis in axisList:
			cmds.setAttr('%s.%s%s' %(sel, attr, axis), keyable = True)
			mel.eval('CBunlockAttr "%s.%s%s";' %(sel, attr, axis))
	cmds.setAttr('%s.visibility' %sel, keyable = True)
	mel.eval('CBunlockAttr "%s.visibility";' %sel)





# Select Skiped Objects #
skipNum = 4
selList = cmds.ls(sl = True)
cmds.select(selList[1::skipNum], r = True)





# Set Enable to Render
selLs = cmds.ls(sl = True)

for sel in selLs:
	selShp = cmds.listRelatives(sel, s = True, path = True)[0]
	cmds.setAttr("%s.castsShadows" %selShp, 1)
	cmds.setAttr("%s.receiveShadows" %selShp, 1)
	cmds.setAttr("%s.motionBlur" %selShp, 1)
	cmds.setAttr("%s.primaryVisibility" %selShp, 1)
	cmds.setAttr("%s.smoothShading" %selShp, 1)
	cmds.setAttr("%s.visibleInReflections" %selShp, 1)
	cmds.setAttr("%s.visibleInRefractions" %selShp, 1)
	cmds.setAttr("%s.doubleSided" %selShp, 1)


# Set Disable to Render
selLs = cmds.ls(sl = True)

for sel in selLs:
	selShp = cmds.listRelatives(sel, s = True, path = True)[0]
	cmds.setAttr("%s.castsShadows" %selShp, 0)
	cmds.setAttr("%s.receiveShadows" %selShp, 0)
	cmds.setAttr("%s.motionBlur" %selShp, 0)
	cmds.setAttr("%s.primaryVisibility" %selShp, 0)
	cmds.setAttr("%s.smoothShading" %selShp, 0)
	cmds.setAttr("%s.visibleInReflections" %selShp, 0)
	cmds.setAttr("%s.visibleInRefractions" %selShp, 0)





# Set Smooth Level #
level = 0

selLs = cmds.ls(sl = True)

for sel in selLs:
	selShp = cmds.listRelatives(sel, s = True)[0]
	cmds.setAttr('%s.smoothLevel' %selShp, level)






### Transfer Control Transform Value to Parent Transform ###
ctrls = cmds.ls(sl = True)
noDfltValCtrls = []

for ctrl in ctrls:
	prntTrnsf = cmds.listRelatives(ctrl, parent = True)[0]
	attrs = cmds.listAttr(ctrl, keyable = True)
	if attrs:
		for attr in attrs:
			attrVal = cmds.getAttr('%s.%s' %(ctrl, attr))
			if attr in ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ'] and not attrVal == 0:
				if 'scale' in attr:
					cmds.setAttr('%s.%s' %(prntTrnsf, attr), attrVal)
					cmds.setAttr('%s.%s' %(ctrl, attr), 1)
				else:
					prntAttrVal = cmds.getAttr('%s.%s' %(prntTrnsf, attr))
					prntAttrVal += attrVal

					cmds.setAttr('%s.%s' %(prntTrnsf, attr), prntAttrVal)
					cmds.setAttr('%s.%s' %(ctrl, attr), 0)
	else:
		pass





# Match Pivot and Consraint #
selLs = cmds.ls(sl = True)
driver = selLs[0]
driven = selLs[1]

# Match rotate pivot
drvrRpPos = cmds.xform(driver, q = True, rp = True, ws = True)
cmds.xform(driven, rp = drvrRpPos, ws = True)

# Match scale pivot
drvrRpPos = cmds.xform(driver, q = True, sp = True, ws = True)
cmds.xform(driven, sp = drvrRpPos, ws = True)

# Parent constraint
cmds.parentConstraint(driver, driven, mo = True)





# Align Parent Joint Orientation to Child Joint #
selLs = cmds.ls(sl = True)
chldJnt = selLs[0]
prntJnt = selLs[1]

# Options
aimVec = [1, 0, 0]
upVec = [0, 1, 0]

upType = 'vector'
worldUpVec = [0, 1, 0]
cmds.delete(cmds.aimConstraint(chldJnt, prntJnt, offset = [0, 0, 0], weight = 1, aimVector = aimVec, upVector = upVec, worldUpType = upType, worldUpVector = worldUpVec))

upType = 'object'
upObject = 'upVec_loc'
cmds.delete(cmds.aimConstraint(chldJnt, prntJnt, offset = [0, 0, 0], weight = 1, aimVector = aimVec, upVector = upVec, worldUpType = upType, worldUpObject = upObject))

cmds.parent(chldJnt, prntJnt)






# Set Driven Key Source Code #
drvrObj = 'Sub'
drvrAttr = 'lodVis'
drvrVal = 0

drvnObj = 'lod01_GRP'
drvnAttr = 'visibility'
drvnVal = 1
cmds.setDrivenKeyframe('%s.%s' %(drvnObj, drvnAttr), cd = '%s.%s' %(drvrObj, drvrAttr), dv = drvrVal, v = drvnVal)

drvnObj = 'lod02_GRP'
drvnAttr = 'visibility'
drvnVal = 0
cmds.setDrivenKeyframe('%s.%s' %(drvnObj, drvnAttr), cd = '%s.%s' %(drvrObj, drvrAttr), dv = drvrVal, v = drvnVal)

drvnObj = 'lod03_GRP'
drvnAttr = 'visibility'
drvnVal = 1
cmds.setDrivenKeyframe('%s.%s' %(drvnObj, drvnAttr), cd = '%s.%s' %(drvrObj, drvrAttr), dv = drvrVal, v = drvnVal)





# Smooth Level Set Up #
ctrlToAddAttr = 'Main'
# Connect smoothLevel attribute to render geometry's smoothLevel attribute.
cmds.select(cmds.ls(sl = True), hi = True, r = True)
shpLs = cmds.ls(sl = True, type = 'mesh')
for shp in shpLs:
	try:
		cmds.connectAttr('%s.smoothLevel' %(ctrlToAddAttr), '%s.smoothLevel' %(shp), f = True)
	except:
		pass






# Trun Off Shape Visibility #
sels = cmds.ls(sl = True)

for sel in sels:
	selShp = cmds.listRelatives(sel, s = True)[0]
	cmds.setAttr('%s.visibility' %selShp, 0)





# Parent constraint geometries matching with advanced skeleton bind joints.
asBndJnts = cmds.ls(sl = True)

for bndJnt in asBndJnts:
	if cmds.objExists('lod01_' + bndJnt):
		cmds.parentConstraint(bndJnt, 'lod01_' + bndJnt, mo = True)
	else:
		pass





# Trun on inherits transform.
selLs = cmds.ls(sl = True)
for sel in selLs:
	try:
		cmds.setAttr(sel + '.inheritsTransform', True)
	except:
		pass





# Rebind Skin #
selLs = cmds.ls(sl = True)

for sel in selLs:
		# duplicate skin geometry for saving skin weights
		cmds.duplicate(sel, n = 'tempGeo')

		cmds.select('tempGeo', r = True)
		tak_cleanUpModel.delHis()
		tak_cleanUpModel.delInterMediObj()

		cmds.setAttr('%s.visibility' %'tempGeo', False)

		# transfer skin weights from skin geometry to the temporary geometry
		cmds.select(sel, r = True)
		cmds.select('tempGeo', add = True)
		tak_misc.TransSkinWeights()

		# clean up skin geometry
		cmds.select(sel, r = True)
		tak_cleanUpModel.delHis()
		tak_cleanUpModel.delInterMediObj()

		# transfer skin weights from temporary geometry to the original geometry
		cmds.select('tempGeo', r = True)
		cmds.select(sel, add = True)
		tak_misc.TransSkinWeights()
		
		# delete temporary geometry
		cmds.delete('tempGeo')





# Select AS FK Controls #
cmds.select('FKSystem')
cmds.select(cmds.ls(sl = True, dag = True, type = 'nurbsCurve'))
cmds.pickWalk(direction = 'up')





# Turn Off Opposite #
selLs = cmds.ls(sl = True, allPaths = True)
for sel in selLs:
	shape = cmds.listRelatives(sel, path = True, s = True)[0]
	cmds.setAttr(shape + '.opposite', False)




# Reconnect Constraint #
import tak_lib

selLs = cmds.ls(sl = True)
for sel in selLs:
	tak_lib.unlockChannelBoxAttr(sel)

	cnst = cmds.ls(cmds.listRelatives(sel), type = 'constraint')
	weightAttr = cmds.listAttr(cnst, ud = True)
	cmds.setAttr(cnst[0] + '.' + weightAttr[0], 0)
	
	cnstDriver = getCnstDriver(cnst[0])
	cnstType = cmds.objectType(cnst)
	cmds.delete(cnst)
	excuteStr = 'cmds.%s("%s", "%s", mo = True, w = 1)' %(cnstType, cnstDriver, sel)
	exec(excuteStr)

def getCnstDriver(cnst):
	cnstConSrcs = list(set(cmds.listConnections('%s.target' %cnst, s = True, d = False)))
	for cnstConSrc in cnstConSrcs:
		if cnstConSrc != cnst:
			return cnstConSrc





# Transfer Skin Weights with Matching Name #
import tak_misc

selMeshes = cmds.ls(sl = True)
prefix = 'lod02_'
for mesh in selMeshes:
	if cmds.objExists(prefix + mesh):
		cmds.select(mesh, prefix + mesh, r = True)
		try:
			tak_misc.TransSkinWeights()
		except:
			pass





# Connect Shape #
selLs = cmds.ls(sl = True)
srcGeo = selLs[0]
trgGeo = selLs[1]

srcShp = cmds.listRelatives(srcGeo, s = True)[0]
trgShp = cmds.listRelatives(trgGeo, s = True)[0]

cmds.connectAttr(srcShp + '.outMesh', trgShp + '.inMesh', f = True)





# Separate Multi #
selGeos = cmds.ls(sl = True)
for geo in selGeos:
	cmds.select(geo, r = True)
	try:
		mel.eval('performPolyChipOff 0 0;')
		cmds.delete(ch = True)
		cmds.select(cl = True)
		cmds.selectMode(object = True)
	except:
		pass



# Select Advanced Skeleton Hand Joints #
handJntLs = [u'Wrist', u'Cup', u'ThumbFinger1', u'ThumbFinger2', u'ThumbFinger3', u'IndexFinger1', u'IndexFinger2', u'IndexFinger3', u'MiddleFinger1', u'MiddleFinger2', u'MiddleFinger3', u'RingFinger1', u'RingFinger2', u'RingFinger3', u'PinkyFinger1', u'PinkyFinger2', u'PinkyFinger3']

cmds.select(handJntLs, r = True)





# On/Off Inherit Transform #
selTrsf = cmds.ls(sl = True, type = 'transform')

for trsf in selTrsf:
	cmds.setAttr('%s.inheritsTransform' %trsf, True)





# FK/IK Hybrid Setup #
selLs = cmds.ls(sl = True)
drvrCtrl = selLs[0]
drvnCtrlZero = selLs[1]

oriGrp = cmds.duplicate(drvrCtrl, po = True, n = drvrCtrl + '_ori_grp')
cmds.orientConstraint(drvrCtrl, oriGrp, mo = False)
cmds.parent(drvnCtrlZero, oriGrp)





# Stich detached edges.
cmds.polySelectConstraint(t = 0x8000, m = 3, w = 1)
cmds.polySelectConstraint(dis = True)
cmds.polyMergeVertex(d = 0.05)




import tak_misc

# Assign Material to Deformed Shape #
deformedShps = cmds.ls('*ShapeDeformed')
for shp in deformedShps:
	origShpPartialName = shp.split('Deformed')[0]
	origShpFullName = cmds.ls('*:' + origShpPartialName)
	if origShpFullName:
		cmds.select(origShpFullName, shp, r = True)
		tak_misc.copyMat()





# Eye Scale Set Up #
{
CBunlockAttr("lod02_eyeball_L_irisPlace.scaleX");
CBunlockAttr("lod02_eyeball_L_irisPlace.scaleY");
CBunlockAttr("lod02_eyeball_L_irisPlace.scaleZ");
CBunlockAttr("lod02_eyeball_R_irisPlace.scaleX");
CBunlockAttr("lod02_eyeball_R_irisPlace.scaleY");
CBunlockAttr("lod02_eyeball_R_irisPlace.scaleZ");

vector $rtPosition = `pointPosition -world ("FKEye_L.rotatePivot")`;
vector $lfPosition = `pointPosition -world ("FKEye_R.rotatePivot")`;
string $rtEyeScales[] = `spaceLocator -position ($rtPosition.x) ($rtPosition.y) ($rtPosition.z) -name "rt_eyeScale"`;
string $lfEyeScales[] = `spaceLocator -position ($lfPosition.x) ($lfPosition.y) ($lfPosition.z) -name "lf_eyeScale"`;
string $rtEyeScale = $rtEyeScales[0];
string $lfEyeScale = $lfEyeScales[0];
select -replace $lfEyeScale;
select -add "lod02_eyeball_L_irisPlace";
scaleConstraint -maintainOffset -weight 1;
select -replace $rtEyeScale;
select -add "lod02_eyeball_R_irisPlace";
scaleConstraint -maintainOffset -weight 1;

addAttr -longName "EyeScale" -keyable true -attributeType double -min 0 -max 4 -defaultValue 1 "FKEye_L";
addAttr -longName "EyeScale" -keyable true -attributeType double -min 0 -max 4 -defaultValue 1 "FKEye_R";

connectAttr -force "FKEye_L.EyeScale" ($lfEyeScale + ".scaleX");
connectAttr -force "FKEye_L.EyeScale" ($lfEyeScale + ".scaleY");
connectAttr -force "FKEye_L.EyeScale" ($lfEyeScale + ".scaleZ");
connectAttr -force "FKEye_R.EyeScale" ($rtEyeScale + ".scaleX");
connectAttr -force "FKEye_R.EyeScale" ($rtEyeScale + ".scaleY");
connectAttr -force "FKEye_R.EyeScale" ($rtEyeScale + ".scaleZ");

setAttr($lfEyeScale + ".visibility") false;
setAttr($rtEyeScale + ".visibility") false;
if(catch(`parent $lfEyeScale "facial_rig_grp"`) == true)
{
    parent $lfEyeScale "facial_grp";
}
if(catch(`parent $rtEyeScale "facial_rig_grp"`) == true)
{
    parent $rtEyeScale "facial_grp";
}
}



# Add Advanced Skeleton Twist Addition Attributes on Finger Controls #
{
addAttr -longName "TwistAdd" -keyable true -attributeType "enum" -enumName "---------------" "Fingers_L";
setAttr -lock true "Fingers_L.TwistAdd";
addAttr -longName "TwistAdd" -keyable true -attributeType "enum" -enumName "---------------" "Fingers_R";
setAttr -lock true "Fingers_R.TwistAdd";
addAttr -longName "Shoulder" -keyable true -attributeType "double" -defaultValue 0 "Fingers_L";
addAttr -longName "Shoulder" -keyable true -attributeType "double" -defaultValue 0 "Fingers_R";
addAttr -longName "ShoulderPart1" -keyable true -attributeType "double" -defaultValue 0 "Fingers_L";
addAttr -longName "ShoulderPart1" -keyable true -attributeType "double" -defaultValue 0 "Fingers_R";
addAttr -longName "ShoulderPart2" -keyable true -attributeType "double" -defaultValue 0 "Fingers_L";
addAttr -longName "ShoulderPart2" -keyable true -attributeType "double" -defaultValue 0 "Fingers_R";
addAttr -longName "Elbow" -keyable true -attributeType "double" -defaultValue 0 "Fingers_L";
addAttr -longName "Elbow" -keyable true -attributeType "double" -defaultValue 0 "Fingers_R";
addAttr -longName "ElbowPart1" -keyable true -attributeType "double" -defaultValue 0 "Fingers_L";
addAttr -longName "ElbowPart1" -keyable true -attributeType "double" -defaultValue 0 "Fingers_R";
addAttr -longName "ElbowPart2" -keyable true -attributeType "double" -defaultValue 0 "Fingers_L";
addAttr -longName "ElbowPart2" -keyable true -attributeType "double" -defaultValue 0 "Fingers_R";
connectAttr -force "Fingers_L.Shoulder" "Shoulder_L.twistAddition";
connectAttr -force "Fingers_R.Shoulder" "Shoulder_R.twistAddition";
connectAttr -force "Fingers_L.ShoulderPart1" "ShoulderPart1_L.twistAddition";
connectAttr -force "Fingers_R.ShoulderPart1" "ShoulderPart1_R.twistAddition";
connectAttr -force "Fingers_L.ShoulderPart2" "ShoulderPart2_L.twistAddition";
connectAttr -force "Fingers_R.ShoulderPart2" "ShoulderPart2_R.twistAddition";
connectAttr -force "Fingers_L.Elbow" "Elbow_L.twistAddition";
connectAttr -force "Fingers_R.Elbow" "Elbow_R.twistAddition";
connectAttr -force "Fingers_L.ElbowPart1" "ElbowPart1_L.twistAddition";
connectAttr -force "Fingers_R.ElbowPart1" "ElbowPart1_R.twistAddition";
connectAttr -force "Fingers_L.ElbowPart2" "ElbowPart2_L.twistAddition";
connectAttr -force "Fingers_R.ElbowPart2" "ElbowPart2_R.twistAddition";
}



# Add Selection to the 'jointLayer' #
selLs = cmds.ls(sl = True)
cmds.editDisplayLayerMembers('jointLayer', selLs)





# Create Joint on Object and Bind #
selLs = cmds.ls(sl = True)

for sel in selLs:
	# Create joint
	selWsPos = cmds.xform(sel, q = True, rp = True, ws = True)
	cmds.select(cl = True)
	bndJnt = cmds.joint(n = sel + '_bnd_jnt', p = selWsPos)
	cmds.CompleteCurrentTool()
	
	# Bind
	cmds.skinCluster(bndJnt, sel, mi = 3, dr = 4.5, tsb = True, omi = False, nw = 1)







selLs = cmds.ls(sl = True)

srcJnt = selLs[0]
trgGeos = selLs[1:]

for geo in trgGeos:
	#geoRpInWs = cmds.xform(geo, q = True, rp = True, ws = True)
	geoJnt = cmds.duplicate(srcJnt, n = geo + '_jnt')
	#cmds.xform(geoJnt, t = geoRpInWs, ws = True)
	
	cmds.skinCluster(geoJnt, geo, mi = 4, dr = 4, tsb = True, omi = False, nw = 1)
	

autoGrps = cmds.ls(sl = True)
for i in xrange(len(autoGrps)):
	if i == 0:
		continue
	pmaNode = cmds.createNode('plusMinusAverage', n = selLs[i] + '_offset_pma')
	cmds.connectAttr(autoGrps[i-1] + '.rotateY', pmaNode + '.input1D[0]')
	cmds.connectAttr('flip_ctrl' + '.offset', pmaNode + '.input1D[2]')
	cmds.connectAttr(pmaNode + '.output1D', autoGrps[i] + '.rotateY')
	cmds.setAttr(pmaNode + '.operation', 2)


geos = cmds.ls(sl = True)
for geo in geos:
	bendGeo = cmds.duplicate(geo, n = geo + '_bend_geo')[0]
	cmds.parent(bendGeo, w = True)
	bsNode = cmds.blendShape(bendGeo, geo, frontOfChain = True)[0]
	cmds.setAttr(bsNode + '.' + bendGeo, 1)
	cmds.setAttr(bendGeo + '.visibility', False)

	bendHndl = cmds.nonLinear(bendGeo, type = 'bend', lowBound = 0, highBound = 1, curvature = 0)[1]
	baseName = geo.split('_bend_geo')[0]
	bendHndl = cmds.rename(bendHndl, baseName + '_bendHndl')
	
	bendNode = cmds.listConnections(bendHndl + '.worldMatrix[0]')[0]
	ctrlBaseName = bendHndl.split('_bendHndl')[0]
	cmds.connectAttr(ctrlBaseName + '_ctrl.bend', bendNode + '.curvature')
	cmds.connectAttr(ctrlBaseName + '_ctrl.twist', bendHndl + '.rotateX')
	cmds.setAttr(bendHndl + '.translateY', 2.6)
	cmds.setAttr(bendHndl + '.scaleX', 9.5)
	cmds.setAttr(bendHndl + '.scaleY', 9.5)
	cmds.setAttr(bendHndl + '.scaleZ', 9.5)




# Match lattice point #
import maya.OpenMaya as OpenMaya

# Get selections
sels = OpenMaya.MSelectionList()
OpenMaya.MGlobal.getActiveSelectionList(sels)

# Get selection's dag path
srcLtcPath = OpenMaya.MDagPath()
trgLtcPath = OpenMaya.MDagPath()
sels.getDagPath(0, srcLtcPath)
sels.getDagPath(1, trgLtcPath)

# Get source lattice's points
srcLtcPnts = OpenMaya.MPointArray()
srcLtcGeoIt = OpenMaya.MItGeometry(srcLtcPath)
while not srcLtcGeoIt.isDone():
	pnt = srcLtcGeoIt.position()
	srcLtcPnts.append(pnt)
	srcLtcGeoIt.next()

# Set target lattice's points
trgLtcGeoIt = OpenMaya.MItGeometry(trgLtcPath)
while not trgLtcGeoIt.isDone():
	srcPnt = srcLtcPnts[trgLtcGeoIt.index()]
	trgLtcGeoIt.setPosition(srcPnt)
	trgLtcGeoIt.next()


###############################################################
# Delete Deformed Shape and Turn Off Original Reference Shape #
###############################################################
import pymel.core as pm

dfmedShps = [x for x in pm.listRelatives(ad=True, type="mesh") if "Deformed" in x.name()]
for dfmedShp in dfmedShps:
	trsf = pm.listRelatives( dfmedShp, parent=True )
	shp = [ x for x in pm.listRelatives( trsf ) if not "Deformed" in x ]
	if shp:
		shp[0].setAttr("intermediateObject", False)
		pm.delete(dfmedShp)


##############################################
# Select Joint Hierarchy Excluding End Joint #
##############################################
import pymel.core as pm

selJnts = pm.ls(sl=True)
bndJnts = [x for x in pm.listRelatives(selJnts, ad=True, type="joint") if pm.listRelatives(x, c=True, type="joint")]
pm.select(selJnts, bndJnts, r=True)



####################################
# Bake Posints Animation to Joints #
####################################
import pymel.core as pm

pntJntDic = {}

# Create joints
selPnts = pm.ls(sl=True, fl=True)

for pnt in selPnts:
	pm.select(pnt, r=True)
	pntPos = pm.pointPosition(pnt, w=True)
	pm.select(cl=True)
	jnt = pm.joint(n=pnt.name() + "_jnt", position=pntPos)
	pntJntDic[pnt] = jnt

# Tracking and baking
startFrame = 0
endFrame = 144

while startFrame != (endFrame+1):
	pm.currentTime(startFrame)
	for pnt, jnt in pntJntDic.items():
		pntPos = pm.pointPosition(pnt, w=True)
		pm.xform(jnt, ws=True, t=pntPos)
		pm.setKeyframe(jnt + ".translate")

	startFrame += 1


## Book Set Up ##
import pymel.core as pm
import tak_misc
reload(tak_misc)

# Page
bulgeClsts = []
selLs = pm.ls(sl=True)
for sel in selLs:
	pm.select(sel, r=True)
	ffdNodes = pm.lattice(sel, divisions=[2,5,2], objectCentered=True, ldv=[2,2,2], n=sel+"_ffd")
	ffdNodes[0].setAttr("local", 0)
	clst = pm.cluster("%s.pt[0:1][1][0]" %(ffdNodes[1]), "%s.pt[0:1][1][1]" %(ffdNodes[1]), n=sel+"_ffd_clst")
	
	pm.addAttr(sel.split("_")[0]+"_ctrl", ln="bulge", at="float", keyable=True)
	pm.connectAttr(sel.split("_")[0]+"_ctrl"+".bulge", clst[0]+"Handle.translateX")

# Page1~5
selLs = pm.ls(sl=True)
for sel in selLs:
	pm.select(sel, r=True)
	ffdNodes = pm.lattice(sel, divisions=[2,5,2], objectCentered=True, ldv=[2,2,2], n=sel+"_ffd")
	ffdNodes[0].setAttr("local", 0)
	clst = pm.cluster("%s.pt[0:1][1][0]" %(ffdNodes[1]), "%s.pt[0:1][1][1]" %(ffdNodes[1]), n=sel+"_ffd_clst")
	
	pm.addAttr(sel.rsplit("_", 1)[0] + "_ctrl", ln="bulge", at="float", keyable=True)
	pm.connectAttr(sel.rsplit("_", 1)[0]+"_ctrl"+".bulge", clst[0]+"Handle.translateX")
	
	groupName = sel.split("_", 1)[0] + "_bulge_system_grp"
	if groupName:
		pm.parent(ffdNodes[1:], clst[1], groupName)
	else:
		pm.group(ffdNodes[1:], clst[1], n=groupName)



# Set ParameterV to 0.5 of SurfaceInfo node #
import pymel.core as pm

srfcInfoNodes = pm.ls(sl=True)

for srfcInfoNode in srfcInfoNodes:
	srfcInfoNode.parameterV.set(0.5)


