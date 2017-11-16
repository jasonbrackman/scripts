
import maya.cmds as cmds
import maya.mel as mel
import tak_misc


def setUpQualoth():
	'''
	Setup Qualoth simulation.
	'''

	# Select in order cloth source to simulate, blend shape cloth source, collider geometrys
	# Blend shape cloth source should be skined
	selList = cmds.ls(sl = True)
	simSrc = selList[0]
	bsCloth = selList[1]
	colliders = selList[2:]
	clothName = str(bsCloth).split('_')[0]

	# Create groups
	qualothGrp = cmds.createNode('transform', n = clothName + '_qualoth_grp')
	colliderGrp = cmds.createNode('transform', n = clothName + '_qualoth_collider_grp')
	constraintGrp = cmds.createNode('transform', n = clothName + '_qualoth_cnst_grp')
	cmds.parent(colliderGrp, constraintGrp, qualothGrp)

	# Duplicate simulation source geometry for goal constraint geo
	goalGeo = cmds.duplicate(simSrc, n = clothName + '_cnst')
	cmds.hide(goalGeo)

	# Create qlCloth
	cmds.select(simSrc, r = True)
	clothShp = mel.eval('qlCreateCloth;')
	clothTrnf = cmds.listRelatives(clothShp, p = True)[0]
	clothOut = cmds.rename('%sOut' %clothTrnf, clothName + '_qlOut')
	clothTrnf = cmds.rename(clothTrnf, clothName + '_qlCloth')
	cmds.parent(clothOut, clothTrnf, qualothGrp)

	# Set collider
	for collider in colliders:
		cmds.select(clothOut, collider, r = True)
		colliderShp = mel.eval('qlCreateCollider;')
		colliderPrnt = cmds.listRelatives(colliderShp, p = True)[0]
		colliderOffset = cmds.rename(colliderPrnt + 'Offset', collider + '_qlColliderOffset')
		colliderPrnt = cmds.rename(colliderPrnt, collider + '_qlCollider')
		cmds.parent(collider, colliderOffset, colliderPrnt, colliderGrp)

	# Goal constraint with goal geo
	cmds.select(clothOut, goalGeo, r = True)
	goalCnst = mel.eval('qlCreateGoalConstraint;')
	goalCnstTrnsf = cmds.listRelatives(goalCnst, p = True)[0]
	cmds.setAttr('%s.attractionMethod' %goalCnst, 2)
	# Copy skin from blend shape geo to goal geo
	cmds.select(bsCloth, goalGeo, r = True)
	tak_misc.TransSkinWeights()
	cmds.parent(goalCnstTrnsf, goalGeo[0], goalGeo[0] + '_Goal', constraintGrp)

	# Add outCloth to blend shape geo as influence
	skinClst = mel.eval('findRelatedSkinCluster("%s");' %bsCloth)
	cmds.skinCluster(skinClst, e = True, ug = True, ps = 0, ns = 10, dr = 4, ai = clothOut)
	cmds.setAttr('%s.useComponents' %skinClst, 1)
	# vtxNumber = cmds.polyEvaluate(bsCloth, vertex = True)
	# for i in xrange(0, vtxNumber, 1):
	# 	cmds.skinPercent(skinClst, '%s.vtx[%d]' %(bsCloth, i), transformValue = [(clothOut, 1)])

	# Clean up outliner
	cmds.parent(simSrc, bsCloth, qualothGrp)

setUpQualoth()



# Script Node for Dynamic Setup #
// charName = "kanae"
// scriptNodeName = "kanae_dynCtrl_expr"

// Get namespace if exists
{
global string $kanae_namespace = "";

// Get namepace if exists
string $scriptNodeName[] = `ls "*:kanae_dynCtrl_expr"`;
string $buff[];
tokenize ($scriptNodeName[0]) ":" $buff;
if ((size($buff)) > 1){
	$kanae_namespace = ($buff[0] + ":");
}

// Qualoth Update Initial Pose //
global proc kanae_updateQlInitialPose(){
	string $kanae_dynState = `getAttr ($kanae_namespace + "dyn_ctr_crv.clothDynOnOff")`;
	if ($kanae_dynState == 1){
		select -r ($kanae_namespace + "sweater_qlOut");
		select -add ($kanae_namespace + "sweater_goal_src");
		qlUpdateInitialPose;
		select -r ($kanae_namespace + "skirt_qlOut");
		select -add ($kanae_namespace + "skirt_goal_src");
		qlUpdateInitialPose;
		select -cl;
	}
}
scriptJob -kws -attributeChange ($kanae_namespace + "dyn_ctr_crv.clothDynOnOff") kanae_updateQlInitialPose;


// Controlling Geometry Visibility When Dynmic On/Off //
global proc kanae_dynVisCtrl(){
	string $kanae_hairDynState = `getAttr ($kanae_namespace + "dyn_ctr_crv.hairDynOnOff")`;
	string $kanae_clothDynState = `getAttr ($kanae_namespace + "dyn_ctr_crv.clothDynOnOff")`;

	if (($kanae_hairDynState == 1) || ($kanae_clothDynState == 1)){
		setAttr ($kanae_namespace + "geometry" + ".visibility") 0;
		setAttr ($kanae_namespace + "Geometry" + ".visibility") 0;
	}
	else if (($kanae_hairDynState == 0) && ($kanae_clothDynState == 0)){
		setAttr ($kanae_namespace + "geometry" + ".visibility") 1;
		setAttr ($kanae_namespace + "Geometry" + ".visibility") 1;
	}
}
scriptJob -kws -attributeChange ($kanae_namespace + "dyn_ctr_crv.hairDynOnOff") kanae_dynVisCtrl;
scriptJob -kws -attributeChange ($kanae_namespace + "dyn_ctr_crv.clothDynOnOff") kanae_dynVisCtrl;
}



# Add cloth attributes to selected dynamic control
dynAttrDic = {'clothDyn': ['enum', '---------------'], 'clothSolverOnOff': ['bool'], 'clothSolverStartFrame': ['double'], 'clothBlend': ['double'], 'hairDyn': ['enum', '---------------'], 'hairSolverOnOff': ['bool'], 'hairSolverStartFrame': ['double'], 'hairBlend': ['double']}

dynCtrl = cmds.ls(sl = True)[0]

for dynAttr in dynAttrDic.keys():
	if cmds.objExists('%s.%s' %(dynCtrl, dynAttr)):
		continue
	else:
		if dynAttrDic[dynAttr][0] == 'enum':
			joinStr = ':'
			cmds.addAttr(dynCtrl, ln = dynAttr, at = dynAttrDic[dynAttr][0], en = joinStr.join(dynAttrDic[dynAttr][1:]))
			cmds.setAttr('%s.%s' %(dynCtrl, dynAttr), channelBox = True)
		elif dynAttrDic[dynAttr][0] == 'bool':
			cmds.addAttr(dynCtrl, ln = dynAttr, at = dynAttrDic[dynAttr][0])
			cmds.setAttr('%s.%s' %(dynCtrl, dynAttr), channelBox = True)
		elif dynAttrDic[dynAttr][0] == 'double':
			cmds.addAttr(dynCtrl, ln = dynAttr, at = dynAttrDic[dynAttr][0], keyable = True)
			cmds.setAttr('%s.%s' %(dynCtrl, dynAttr), channelBox = False, keyable = True)


# Dynamic control visibility setup
if cmds.objExists('dyn_ctr_crv'):
	if cmds.objExists('dyn_ctr_crv.clothSolverOnOff'):
		dynExprStr = '''
		// Expression for Cloth Dynamic Visibility //
		string $clothSolverState = dyn_ctr_crv.clothSolverOnOff;

		if ($clothSolverState == 1){
			geometry.visibility = 0;
			Geometry.visibility = 0;
		}
		else if ($clothSolverState == 0){
			geometry.visibility = 1;
			Geometry.visibility = 1;
		} 
		'''
		cmds.expression(s = dynExprStr, ae = True, uc = 'all', n = 'clothDynVis_expr')
	if cmds.objExists('dyn_ctr_crv.hairSolverOnOff'):
		dynExprStr = '''
		// Expression for Hair Dynamic Visibility //
		string $hairSolverState = dyn_ctr_crv.hairSolverOnOff;

		if ($hairSolverState == 1){
			geometry.visibility = 0;
			Geometry.visibility = 0;
		}
		else if ($hairSolverState == 0){
			geometry.visibility = 1;
			Geometry.visibility = 1;
		} 
		'''
		cmds.expression(s = dynExprStr, ae = True, uc = 'all', n = 'hairDynVis_expr')
