import maya.cmds as cmds
import re
import tak_lib
reload(tak_lib)


### Connect Facial Control to ROM Facial Locator with SDK ###
def cntFacCtrlLocUI():
	'''
	UI for connect facial control to range of motion animated locators.
	'''

	winName = 'cntFacCtrlLocWin'

	if cmds.window(winName, exists = True):
		cmds.deleteUI(winName)

	cmds.window(winName, title = 'Connect Facial Control to Facial Locators')

	cmds.columnLayout('mainColLo', adj = True)
	cmds.rowColumnLayout('drvrRowColLo', p = 'mainColLo', numberOfColumns = 5)
	cmds.textField('drvrTxtFld', p = 'drvrRowColLo', text = 'Driver Object')
	cmds.text(p = 'drvrRowColLo', label = '.')
	cmds.textField('drvrAttrTxtFld', p = 'drvrRowColLo', text = 'Driver Attribute')
	cmds.textField('drvrMinValTxtFld', p = 'drvrRowColLo', text = 'Min Value')
	cmds.textField('drvrMaxTxtFld', p = 'drvrRowColLo', text = 'Max Value')

	cmds.window(winName, e = True, w = 300, h = 300)
	cmds.showWindow(winName)




# Transfer Attributes Value to Parent #
selLs = cmds.ls(sl = True)
cmds.autoKeyframe(state = False)
for sel in selLs:	
	loc = sel
	prnt = cmds.listRelatives(loc, p = True)[0]
	attrList = cmds.listAttr(loc, keyable = True)
	for attr in attrList:
	    locAttrVal = cmds.getAttr('%s.%s' %(loc, attr))
	    cmds.setAttr('%s.%s' %(prnt, attr), locAttrVal)
	    
	    # Set default value for locator attribute
	    if 'scale' in attr or 'visibility' in attr:
	        dftVal = 1
	    else:
	        dftVal = 0
	    cmds.setAttr('%s.%s' %(loc, attr), dftVal)


### Eyebrows ###

def extractShp(normalPoseFrame, downPoseFrame, upPoseFrame, geo):
	'''
	Description:
	Main function.
	Extract target shape for selected controls.
	Select controls and select geometry last.

	Arguments:
	normalPoseFrame(int)
	downPoseFrame(int)
	upPoseFrame(int)
	geo(string)

	Returns:
	Nothing
	'''

	cmds.autoKeyframe(state = False)

	ctrls = cmds.ls(sl = True)

	# Unlock translate attribute of geo
	cmds.setAttr('%s.translate' %geo, lock = False)

	for ctrl in ctrls:
		# Go to the down pose frame and get translate and rotate
		ctrlTrns, ctrlRo = getTrRo(ctrl, downPoseFrame)
		
		# Back to the normal pose frame and extract target
		duplicateGeo(normalPoseFrame, ctrl, ctrlTrns, ctrlRo, geo, 'down')
		
		# Go to the up pose frame and get translate and rotate
		ctrlTrns, ctrlRo = getTrRo(ctrl, upPoseFrame)
		
		# Back to the normal pose frame and extract target
		duplicateGeo(normalPoseFrame, ctrl, ctrlTrns, ctrlRo, geo, 'up')


def getTrRo(ctrl, poseFrame):
	'''
	Description:
	Go to the pose frame and get translate, rotate values.
	
	Arguments: 
	ctrl(string)
	poseFrame(int)
	
	Returns:
	translateVal(float)
	rotateVal(float)
	'''
	
	cmds.currentTime(poseFrame)
	translateVal = cmds.getAttr('%s.translate' %ctrl)
	rotateVal = cmds.getAttr('%s.rotate' %ctrl)
	
	return translateVal, rotateVal


def duplicateGeo(normalPoseFrame, ctrl, trnsVal, roVal, geo, direction):
	'''
	Description:
	Go to the normal pose frame and set translate, rotate then duplicate geometry.

	Argumens:
	normalPoseFrame(int)
	trnsVal(float)
	roVal(float)
	geo(string)

	Retruns:
	Nothing
	'''

	suffix = '_crv_bnd_jnt_loc'

	cmds.currentTime(normalPoseFrame)
	cmds.setAttr('%s.translate' %ctrl, trnsVal[0][0], trnsVal[0][1], trnsVal[0][2])
	cmds.setAttr('%s.rotate' %ctrl, roVal[0][1], roVal[0][1], roVal[0][2])
	shpName = ctrl.rsplit(suffix)[0] + '_' + direction
	cmds.duplicate(geo, n = shpName)
	try:
		cmds.parent(shpName, world = True)
	except:
		pass

extractShp(normalPoseFrame = 1, downPoseFrame = 31, upPoseFrame = 11, geo = 'face6')



# Select eyebrow locators
select -cl;
catch (`select -add "rt_out_eyebrow_crv_bnd_jnt_loc"`);
catch (`select -add "rt_mid_eyebrow_crv_bnd_jnt_loc"`);
catch (`select -add "rt_in_eyebrow_crv_bnd_jnt_loc"`);
catch (`select -add "lf_in_eyebrow_crv_bnd_jnt_loc"`);
catch (`select -add "lf_mid_eyebrow_crv_bnd_jnt_loc"`);
catch (`select -add "lf_out_eyebrow_crv_bnd_jnt_loc"`);





### Eyelids ###

# Parent each joint to the base joint and create ikSCsolver
selList = cmds.ls(sl = True)
baseJntSrc = selList.pop(-1)
for sel in selList:
	dupBaseJntSrc = cmds.duplicate(baseJntSrc, n = sel + '_base')[0]
	cmds.parent(sel, dupBaseJntSrc)
	cmds.ikHandle(sj = dupBaseJntSrc, ee = sel, solver = 'ikSCsolver', n = sel + '_ikh')


# Aim constraint with last selected object
selList = cmds.ls(sl = True)
trgs = selList[0:-1]
aimObj = selList[-1]
for trg in trgs:
	cmds.aimConstraint(aimObj, trg, weight = 1, aimVector = [0, 0, -1], upVector = [0, 1, 0], worldUpType = 'vector', worldUpVector = [0, 1, 0], mo = True)



# Fleshy eyes #
eyeJnts = ['Eye_L', 'Eye_R']
prefix = ['lf', 'rt']
sides = ['up', 'dn']

for i in xrange(len(eyeJnts)):
	attrExst = cmds.objExists('FK%s.fleshyEye' %eyeJnts[i])
	if not attrExst:
		cmds.addAttr('FK' + eyeJnts[i], ln = 'fleshyEye', at = 'double', defaultValue = 0.5, minValue = 0.0, maxValue = 1.0, keyable = True)

	for j in xrange(len(sides)):
		flshEyeMul = cmds.shadingNode('multiplyDivide', asUtility = True, n = '%s_%s_eyelids_fleshy_mul' %(prefix[i], sides[j]))
		cmds.setAttr('%s.input2X' %flshEyeMul, 0.25)
		cmds.setAttr('%s.input2Y' %flshEyeMul, 0.25)
		cmds.setAttr('%s.input2Z' %flshEyeMul, 0.75)
		cmds.connectAttr('%s.rotate' %eyeJnts[i], '%s.input1' %flshEyeMul, f = True)

		flshEyeAmountMul = cmds.shadingNode('multiplyDivide', asUtility = True, n = '%s_%s_eyelids_fleshy_amount_mul' %(prefix[i], sides[j]))
		cmds.connectAttr('%s.output' %flshEyeMul, '%s.input1' %flshEyeAmountMul, f = True)
		cmds.connectAttr('FK%s.fleshyEye' %eyeJnts[i], '%s.input2X' %flshEyeAmountMul, f = True)
		cmds.connectAttr('FK%s.fleshyEye' %eyeJnts[i], '%s.input2Y' %flshEyeAmountMul, f = True)
		cmds.connectAttr('FK%s.fleshyEye' %eyeJnts[i], '%s.input2Z' %flshEyeAmountMul, f = True)
		cmds.connectAttr('%s.output' %flshEyeAmountMul, '%s_%s_eyelid_base_jnt_loc_auto.rotate' %(prefix[i], sides[j]), f = True)



# Select eyelid locators
select -cl;
catch (`select -add "rt_up_eyelid_base_jnt_loc"`);
catch (`select -add "rt_dn_eyelid_base_jnt_loc"`);
catch (`select -add "lf_up_eyelid_base_jnt_loc"`);
catch (`select -add "lf_dn_eyelid_base_jnt_loc"`);
catch (`select -add "rt_up_out_eyelid_crv_bnd_jnt_ikh_loc"`);
catch (`select -add "rt_up_mid_eyelid_crv_bnd_jnt_ikh_loc"`);
catch (`select -add "rt_up_in_eyelid_crv_bnd_jnt_ikh_loc"`);
catch (`select -add "rt_dn_out_eyelid_crv_bnd_jnt_ikh_loc"`);
catch (`select -add "rt_dn_mid_eyelid_crv_bnd_jnt_ikh_loc"`);
catch (`select -add "rt_dn_in_eyelid_crv_bnd_jnt_ikh_loc"`);
catch (`select -add "rt_out_corner_eyelid_crv_bnd_jnt_ikh_loc"`);
catch (`select -add "rt_in_corner_eyelid_crv_bnd_jnt_ikh_loc"`);
catch (`select -add "lf_up_out_eyelid_crv_bnd_jnt_ikh_loc"`);
catch (`select -add "lf_up_mid_eyelid_crv_bnd_jnt_ikh_loc"`);
catch (`select -add "lf_up_in_eyelid_crv_bnd_jnt_ikh_loc"`);
catch (`select -add "lf_dn_out_eyelid_crv_bnd_jnt_ikh_loc"`);
catch (`select -add "lf_dn_mid_eyelid_crv_bnd_jnt_ikh_loc"`);
catch (`select -add "lf_dn_in_eyelid_crv_bnd_jnt_ikh_loc"`);
catch (`select -add "lf_out_corner_eyelid_crv_bnd_jnt_ikh_loc"`);
catch (`select -add "lf_in_corner_eyelid_crv_bnd_jnt_ikh_loc"`);





### Nose & Cheeks ###

# Select nose cheek locators
select -cl;
catch (`select -add "nose_ikh_loc"`);
catch (`select -add "rt_cheek_puff_bnd_jnt_loc"`);
catch (`select -add "rt_sneer_bnd_jnt_loc"`);
catch (`select -add "lf_sneer_bnd_jnt_loc"`);
catch (`select -add "lf_cheek_puff_bnd_jnt_loc"`);
catch (`select -add "lf_flare_bnd_jnt_loc"`);
catch (`select -add "rt_flare_bnd_jnt_loc"`);





### Lips ###

# parentConstraint blender
selList = cmds.ls(sl = True)
drvr_a = selList[0]
drvr_b = selList[1]
drvn = selList[2]

prntCnst = cmds.parentConstraint(drvr_a, drvr_b, drvn, mo = True)[0]
blendAttr = cmds.addAttr(drvn, longName = 'blend', attributeType = 'float', min = 0, max = 1, keyable = True)
pmaNode = cmds.shadingNode('plusMinusAverage', asUtility = True, n = prntCnst + '_pma')

cmds.setAttr('%s.operation' %pmaNode, 2)
cmds.setAttr('%s.input1D[0]' %pmaNode, 1)
cmds.connectAttr('%s.blend' %drvn, '%s.input1D[1]' %pmaNode, force = True)
cmds.connectAttr('%s.output1D' %pmaNode, '%s.%s' %(prntCnst, drvr_b + 'W1'), force = True)
cmds.connectAttr('%s.blend' %drvn, '%s.%s' %(prntCnst, drvr_a + 'W0'), force = True)


# matching other side object constraint weight value
selList = cmds.ls(sl = True)

srch = 'lf_'
rplc = 'rt_'
cnst = 'parentConstraint'

weightList = ['Jaw_MW0', 'Jaw_lockW1']

for sel in selList:
	symObj = re.sub(srch, rplc, sel)
	for weight in weightList:
		val = cmds.getAttr('%s_%s1.%s' %(sel, cnst, weight))
		cmds.setAttr('%s_%s1.%s' %(symObj, cnst, weight), val)


# parent constraint interpolation set to shortest
selList = cmds.ls(sl = True)
for sel in selList:
	prntCnst = cmds.listRelatives(sel, c = True, type = 'parentConstraint')[0]
	cmds.setAttr('%s.interpType' %prntCnst, 2)


# Select lip locators
select -cl;
catch (`select -add "rt_up_mid_lip_crv_bnd_jnt_loc"`);
catch (`select -add "rt_dn_mid_lip_crv_bnd_jnt_loc"`);
catch (`select -add "rt_dn_in_lip_crv_bnd_jnt_loc"`);
catch (`select -add "rt_corner_lip_crv_bnd_jnt_loc"`);
catch (`select -add "rt_up_in_lip_crv_bnd_jnt_loc"`);
catch (`select -add "lf_up_mid_lip_crv_bnd_jnt_loc"`);
catch (`select -add "lf_dn_mid_lip_crv_bnd_jnt_loc"`);
catch (`select -add "lf_dn_in_lip_crv_bnd_jnt_loc"`);
catch (`select -add "ct_dn_lip_crv_bnd_jnt_loc"`);
catch (`select -add "lf_corner_lip_crv_bnd_jnt_loc"`);
catch (`select -add "lf_up_in_lip_crv_bnd_jnt_loc"`);
catch (`select -add "ct_up_lip_crv_bnd_jnt_loc"`);









# Script Job for Facial Controls Symmetry Selection #
// scriptNodeName: 'facialCtrl_scriptNode'
global proc facialCtrlSymSel(){
	string $namespace = "";

	// Get selected objects namespace
	string $sel[] = `ls -sl`;
	string $buffer[] = `stringToStringArray $sel[0] ":"`;
	if (`size($buffer)` > 1){
		$namespace = $buffer[0] + ":";
	}

	string $facialCtrlList[] = {$namespace + "rt_in_eyebrow_ctrl", $namespace + "rt_mid_eyebrow_ctrl", $namespace + "rt_out_eyebrow_ctrl", $namespace + "lf_in_eyebrow_ctrl", $namespace + "lf_mid_eyebrow_ctrl", $namespace + "lf_out_eyebrow_ctrl", $namespace + "lf_in_corner_eyelid_ctrl", $namespace + "lf_out_corner_eyelid_ctrl", $namespace + "lf_up_in_eyelid_ctrl", $namespace + "lf_up_mid_eyelid_ctrl", $namespace + "lf_up_out_eyelid_ctrl", $namespace + "lf_dn_in_eyelid_ctrl", $namespace + "lf_dn_mid_eyelid_ctrl", $namespace + "lf_dn_out_eyelid_ctrl", $namespace + "rt_in_corner_eyelid_ctrl", $namespace + "rt_out_corner_eyelid_ctrl", $namespace + "rt_up_in_eyelid_ctrl", $namespace + "rt_up_mid_eyelid_ctrl", $namespace + "rt_up_out_eyelid_ctrl", $namespace + "rt_dn_in_eyelid_ctrl", $namespace + "rt_dn_mid_eyelid_ctrl", $namespace + "rt_dn_out_eyelid_ctrl", $namespace + "lf_eyelid_blink_ctrl", $namespace + "rt_eyelid_blink_ctrl", $namespace + "lf_eyelid_smile_ctrl", $namespace + "rt_eyelid_smile_ctrl", $namespace + "lf_eyelid_crunch_ctrl", $namespace + "rt_eyelid_crunch_ctrl", $namespace + "lf_eyelid_squint_ctrl", $namespace + "rt_eyelid_squint_ctrl", $namespace + "rt_nose_sneer_ctrl", $namespace + "lf_nose_sneer_ctrl", $namespace + "lf_nose_flare_ctrl", $namespace + "rt_nose_flare_ctrl", $namespace + "rt_cheek_puff_ctrl", $namespace + "lf_cheek_puff_ctrl", $namespace + "rt_corner_lip_ctrl", $namespace + "rt_up_lip_ctrl", $namespace + "rt_dn_lip_ctrl", $namespace + "lf_corner_lip_ctrl", $namespace + "lf_up_lip_ctrl", $namespace + "lf_dn_lip_ctrl"};
	string $lfPrefix = $namespace + "lf_";
	string $rtPrefix = $namespace + "rt_";

	string $ctrlList[] = `ls -sl`;
	for ($ctrl in $ctrlList){
		// Check if selection is facial control
		int $found = stringArrayContains($ctrl, $facialCtrlList);

		if ($found){
			// Check if symmetry selection option is on
			string $facialSymSelState = `getAttr ($namespace + "facial_opt_ctrl.symmetrySelection")`;	

			if ($facialSymSelState == 1){
				if (`gmatch $ctrl ($namespace + "lf_*")`){
					string $rtCtrl = `substitute $lfPrefix $ctrl $rtPrefix`;
					select -add $rtCtrl;
				}
				else if (`gmatch $ctrl ($namespace + "rt_*")`){
					string $lfCtrl = `substitute $rtPrefix $ctrl $lfPrefix`;
					select -add $lfCtrl;
					
				}
			}
		}
	}
}


// If scriptjob exists do not create again
string $all_Jobs[];
$all_jobs = `scriptJob -lj`;
int $foundJob = 0;
string $look_for;

for($j = 0; $j < size($all_jobs); $j++){
	string $current_job = $all_jobs[$j];
	$look_for = "facialCtrlSymSel";
	string $match_result = `match $look_for $current_job`;
	if($match_result != ""){
		$foundJob = 1;
		break;
	}
}
if($foundJob == 0){
	scriptJob -kws -e "SelectionChanged" facialCtrlSymSel;
}







##### A64 Eye Texture Control Attribute Setup #####

'''
# Naming convention #
- eye_GRP: eyeball_L_GRP, eyeball_R_GRP
- lf_eye_layerd_tex
- lf_iris_col_tex, lf_iris_col_tex_place
- lf_iris_spec_large_tex, lf_iris_spec_large_tex_place
- lf_iris_spec_small_tex, lf_iris_spec_small_tex_place
'''


# Select iris geometry.
irises = cmds.ls(sl = True)

for iris in irises:
    # Add attributes
    irisGrp = cmds.listRelatives(iris, p = True, path = True)[0]
    driverAttrs = addEyeAttrs(irisGrp)

    # Set driven key
    mat = tak_lib.getMatFromSel(iris) # Get material
    texPlceLs = cmds.ls(cmds.listHistory(mat), type = 'place2dTexture') # Get texture placement nodes
    sdkTexCtrlAttr(driverAttrs, texPlceLs)
    print texPlceLs


def addEyeAttrs(grp):
    attrLs = ['eyeballUpDown', 'eyeballLfRt', 'largeSpecUpDown', 'largeSpecLfRt', 'smallSpecUpDown', 'smallSpecLfRt']
    
    addedAttrs = []
    for attr in attrLs:
        cmds.addAttr(grp, ln = attr, at = 'double', dv = 0, keyable = True, min = -10, max = 10)
        addedAttrs.append('%s.%s' %(grp, attr))

    return addedAttrs


def sdkTexCtrlAttr(drvrs, drvns):
    drvrVals = [-10, 0 ,10]
    drvnVals = [-0.45, 0, 0.45]
    drvnAttrs = ['translateFrameV', 'translateFrameU', 'offsetV', 'offsetU']

    for drvr in drvrs:
        for drvn in drvns:
            if 'eyeballUpDown' in drvr:
                cmds.setDrivenKeyframe('%s.%s' %(drvn, drvnAttrs[0]), cd = drvr, dv = drvrVals[0] , v = drvnVals[0])
                cmds.setDrivenKeyframe('%s.%s' %(drvn, drvnAttrs[0]), cd = drvr, dv = drvrVals[1] , v = drvnVals[1])
                cmds.setDrivenKeyframe('%s.%s' %(drvn, drvnAttrs[0]), cd = drvr, dv = drvrVals[2] , v = drvnVals[2])
            elif 'eyeballLfRt' in drvr:
                cmds.setDrivenKeyframe('%s.%s' %(drvn, drvnAttrs[1]), cd = drvr, dv = drvrVals[0] , v = drvnVals[0])
                cmds.setDrivenKeyframe('%s.%s' %(drvn, drvnAttrs[1]), cd = drvr, dv = drvrVals[1] , v = drvnVals[1])
                cmds.setDrivenKeyframe('%s.%s' %(drvn, drvnAttrs[1]), cd = drvr, dv = drvrVals[2] , v = drvnVals[2])
            elif 'largeSpecUpDown' in drvr and 'large' in drvn:
                cmds.setDrivenKeyframe('%s.%s' %(drvn, drvnAttrs[2]), cd = drvr, dv = drvrVals[0] , v = -drvnVals[0])
                cmds.setDrivenKeyframe('%s.%s' %(drvn, drvnAttrs[2]), cd = drvr, dv = drvrVals[1] , v = -drvnVals[1])
                cmds.setDrivenKeyframe('%s.%s' %(drvn, drvnAttrs[2]), cd = drvr, dv = drvrVals[2] , v = -drvnVals[2])
            elif 'largeSpecLfRt' in drvr and 'large' in drvn:
                cmds.setDrivenKeyframe('%s.%s' %(drvn, drvnAttrs[3]), cd = drvr, dv = drvrVals[0] , v = -drvnVals[0])
                cmds.setDrivenKeyframe('%s.%s' %(drvn, drvnAttrs[3]), cd = drvr, dv = drvrVals[1] , v = -drvnVals[1])
                cmds.setDrivenKeyframe('%s.%s' %(drvn, drvnAttrs[3]), cd = drvr, dv = drvrVals[2] , v = -drvnVals[2])
            elif 'smallSpecUpDown' in drvr and 'small' in drvn:
                cmds.setDrivenKeyframe('%s.%s' %(drvn, drvnAttrs[2]), cd = drvr, dv = drvrVals[0] , v = -drvnVals[0])
                cmds.setDrivenKeyframe('%s.%s' %(drvn, drvnAttrs[2]), cd = drvr, dv = drvrVals[1] , v = -drvnVals[1])
                cmds.setDrivenKeyframe('%s.%s' %(drvn, drvnAttrs[2]), cd = drvr, dv = drvrVals[2] , v = -drvnVals[2])
            elif 'smallSpecLfRt' in drvr and 'small' in drvn:
                cmds.setDrivenKeyframe('%s.%s' %(drvn, drvnAttrs[3]), cd = drvr, dv = drvrVals[0] , v = -drvnVals[0])
                cmds.setDrivenKeyframe('%s.%s' %(drvn, drvnAttrs[3]), cd = drvr, dv = drvrVals[1] , v = -drvnVals[1])
                cmds.setDrivenKeyframe('%s.%s' %(drvn, drvnAttrs[3]), cd = drvr, dv = drvrVals[2] , v = -drvnVals[2])



# Connect A64 Eye Texture Control to Advanced Skeleton Rig #

# Add attributes to 'AimEye_M' control
attrLs = ['lfLargeSpecUpDown', 'rtLargeSpecUpDown', 'lfLargeSpecLfRt', 'rtLargeSpecLfRt', 'lfSmallSpecUpDown', 'rtSmallSpecUpDown', 'lfSmallSpecLfRt', 'rtSmallSpecLfRt']

addedAttrs = []
for attr in attrLs:
    cmds.addAttr('AimEye_M', ln = attr, at = 'double', dv = 0, keyable = True, min = -10, max = 10)
    addedAttrs.append('%s.%s' %('AimEye_M', attr))

# SDK
prefixLs = ["_L", "_R"]
for prefix in prefixLs:
	cmds.setDrivenKeyframe("eyeball%s_GRP.eyeballUpDown" %prefix, cd = "Eye%s.rz" %prefix, dv = -45, v = -20)
	cmds.setDrivenKeyframe("eyeball%s_GRP.eyeballUpDown" %prefix, cd = "Eye%s.rz" %prefix, dv = 0, v = 0)
	cmds.setDrivenKeyframe("eyeball%s_GRP.eyeballUpDown" %prefix, cd = "Eye%s.rz" %prefix, dv = 20, v = 10)

	cmds.setDrivenKeyframe("eyeball%s_GRP.eyeballLfRt" %prefix, cd = "Eye%s.ry" %prefix, dv = -45, v = -10)
	cmds.setDrivenKeyframe("eyeball%s_GRP.eyeballLfRt" %prefix, cd = "Eye%s.ry" %prefix, dv = 0, v = 0)
	cmds.setDrivenKeyframe("eyeball%s_GRP.eyeballLfRt" %prefix, cd = "Eye%s.ry" %prefix, dv = 50, v = 10)


# Parent each joint to the duplicated base joint
selList = cmds.ls(sl = True)
baseJntSrc = selList.pop(-1)
for sel in selList:
	prntGrp = cmds.listRelatives(sel, p = True)[0]
	dupBaseJntSrc = cmds.duplicate(baseJntSrc, n = sel + '_base')[0]
	cmds.parent(sel, dupBaseJntSrc)





















# Mirror Facial Rig 'lf_ Locators' to the 'rt_ Locators' for Each Keyframe #
import re

srchStr = 'lf_'
rplcStr = 'rt_'

startFrame = 11
endFrame = 500
interval = 20
cmds.currentTime(startFrame)

while startFrame <= endFrame:
	lfFacialLocLs = cmds.ls(sl = True)
	for lfFacialLoc in lfFacialLocLs:
		trg = re.sub(srchStr, rplcStr, lfFacialLoc)
	
		selTr = cmds.getAttr('%s.translate' %(lfFacialLoc))[0]
		selRo = cmds.getAttr('%s.rotate' %(lfFacialLoc))[0]
		selSc = cmds.getAttr('%s.scale' %(lfFacialLoc))[0]
	
		selTr = (-selTr[0], selTr[1], selTr[2])
		selRo = (selRo[0], -selRo[1], -selRo[2])
		selSc = (selSc[0], selSc[1], selSc[2])
	
		cmds.setAttr('%s.translate' %(trg), *selTr)
		cmds.setAttr('%s.rotate' %(trg), *selRo)
		cmds.setAttr('%s.scale' %(trg), *selSc)
	
	# Go to the next expression frame
	startFrame += interval
	cmds.currentTime(startFrame, e = True)
cmds.currentTime(1)


### Extract Facial List from the Facial Rig ###
import tak_lib
# set the facialList
facialFullList = ['eyebrow_down', 'eyebrow_up', 'eyebrow_angry', 'eyebrow_sad', 'eyebrow_furrow',
'eyelid_blink', 'eyelid_big', 'eyelid_smile', 'eyelid_angry', 'eyelid_sad',
'cheek_puff', 'cheek_suck',
'nose_up', 'nose_down', 'nose_big', 'nose_sneer',
'lip_smile', 'lip_frown', 'lip_wide', 'lip_narrow', 'lip_openSmile', 'lip_openSmileBig', 'lip_angry', 'lip_angryBig', 'lipSync_A', 'lipSync_E', 'lipSync_I', 'lipSync_O', 'lipSync_U']

facialLs = ['eyebrow_down', 'eyebrow_up', 'eyebrow_angry', 'eyebrow_sad',
'eyelid_blink', 'eyelid_smile', 'eyelid_angry', 'eyelid_sad', 'eyelid_big',
'lip_wide', 'lip_narrow', 'lip_smile', 'lip_frown', 'lipSync_A', 'lipSync_E', 'lipSync_I', 'lipSync_O',
]

# select the facial rig group
rigGeoGrp = cmds.ls(sl = True)

startFrame = 11
cmds.currentTime(startFrame, e = True)

# extract facial list
for facial in facialLs:
    cmds.duplicate(rigGeoGrp[0], n = facial, rc = True)

    # Delete base geometries
    dupFacialChlds = cmds.listRelatives(facial, path = True, type = 'transform')
    for chld in dupFacialChlds:
    	if 'Base' in chld:
    		cmds.delete(chld)

    # Go to the next expression frame
    startFrame += 20
    cmds.currentTime(startFrame, e = True)





# Connect Facial Control Attributes to the Facial Blend Shape #
import re

facialCtrlLs = cmds.ls(sl = True)
facialBsName = 'facial_bs'

for facialCtrl in facialCtrlLs:
	facialAttrLs = cmds.listAttr(facialCtrl, keyable = True)
	for facialAttr in facialAttrLs:
		facialBsTrgName = re.sub(r'ctrl', facialAttr, facialCtrl)
		
		if cmds.objExists(facialBsName + '.' + facialBsTrgName):
			try:
				cmds.connectAttr(facialCtrl + '.' + facialAttr, facialBsName + '.' + facialBsTrgName, f = True)
			except:
				pass
		
		if 'lip' in facialCtrl:
			facialBsTrgName = re.sub(r'ctrl', facialAttr, facialCtrl)
			if 'lip_lf' in facialBsTrgName:
				facialBsTrgName = re.sub(r'lip_lf', 'lf_lip', facialBsTrgName)
			elif 'lip_rt' in facialBsTrgName:
				facialBsTrgName = re.sub(r'lip_rt', 'rt_lip', facialBsTrgName)
			
			if cmds.objExists(facialBsName + '.' + facialBsTrgName):
				try:
					cmds.connectAttr(facialCtrl + '.' + facialAttr, facialBsName + '.' + facialBsTrgName, f = True)
				except:
					pass





# Extract Facial Targets with Selected Controls #
facialCtrlLs = cmds.ls(sl = True)
facialGrp = 'wrap_head_grp'

for ctrl in facialCtrlLs:
	attrLs = cmds.listAttr(ctrl, keyable = True)
	trgNamePrefix = ctrl.rsplit('_ctrl')[0]
	for attr in attrLs:
		try:
			cmds.setAttr('%s.%s' %(ctrl, attr), 1)
			cmds.duplicate(facialGrp, rr = True, renameChildren = True, n = trgNamePrefix + '_' + attr)
			cmds.setAttr('%s.%s' %(ctrl, attr), 0)
		except:
			pass





# Extract Facial Targets from Blendshape #
bsNode = 'blendShape1'
trgLs = cmds.listAttr(bsNode + '.w', multi = True)
facialGrp = 'src_head_grp'

for trg in trgLs:
	cmds.setAttr(bsNode + '.' + trg, 1)
	cmds.duplicate(facialGrp, renameChildren = True, n = trg)
	cmds.setAttr(bsNode + '.' + trg, 0)





# Duplicate Source Facial Group #
facialNeedList = ['eyebrow_down', 'eyebrow_up', 'eyebrow_angry',
'eyelid_big', 'eyelid_smile', 'eyelid_angry', 
'lip_smile', 'lip_frown', 'lip_wide', 'lip_narrow', 'lip_openSmile', 'lip_angry', 'lip_angryBig', 'lipSync_I', 'lipSync_O']

facialSrcGrp = cmds.ls(sl = True)

for item in facialNeedList:
	cmds.duplicate(facialSrcGrp, n = item, renameChildren = True)


lod01FacialNeedList = ['eyebrow_angry', 'eyebrow_sad',
'eyelid_blink',
'lip_smile', 'lip_frown']

facialSrcGrp = cmds.ls(sl = True)

for item in lod01FacialNeedList:
	cmds.duplicate(facialSrcGrp, n = item, renameChildren = True)





# Clean Up Blend Targets #
selLs = cmds.ls(sl = True)

for sel in selLs:
	cmds. delete(ch = True)
	
	for child in cmds.listRelatives(sel, ad = True):
		if 'Base' in child:
			cmds.delete(child)
			print child



###################################################################################################################


# Locator zero group scaleX set to -1 #
locators = pm.ls(sl=True)
for locator in locators:
	locChild = locator.getChildren(type='transform')[0]
	locChild.setParent(world=True)

	zeroGrpName = '%s_zero' % locator.name()
	pm.setAttr('%s.scaleX' % zeroGrpName, -1)

	locChild.setParent(locator)


# Mirror zero group #
zeroGrps = pm.ls(sl=True)
searchStr = 'lf_'
replaceStr = 'rt_'

for zeroGrp in zeroGrps:
	zeroGrpTrans = zeroGrp.getTranslation()
	zeroGrpRotation = zeroGrp.getRotation()
	zeroGrpScale = zeroGrp.getScale()

	otherSideZeroGrpName = zeroGrp.replace(searchStr, replaceStr)
	otherSideZeroGrp = pm.PyNode(otherSideZeroGrpName)

	otherSideZeroGrp.setTranslation([-zeroGrpTrans.x, zeroGrpTrans.y, zeroGrpTrans.z])
	otherSideZeroGrp.setRotation([zeroGrpRotation.x, -zeroGrpRotation.y, -zeroGrpRotation.z])
	otherSideZeroGrp.setScale([-zeroGrpScale[0], zeroGrpScale[1], zeroGrpScale[2]])



# Eyelid #

# Select eyelid joint and base joint
selList = cmds.ls(sl = True)
baseJntSrc = selList.pop(-1)
ikhs = []
for sel in selList:
	dupBaseJntSrc = cmds.duplicate(baseJntSrc, n = sel + '_base')[0]
	cmds.parent(sel, dupBaseJntSrc)
	ikh = cmds.ikHandle(sj=dupBaseJntSrc, ee=sel, solver='ikSCsolver', n=sel+'_ikh')
	ikhs.append(ikh)

select(ikhs, r=True)




# Sticky Lip #

# Distribute constraint weight #
selJnts = sorted(pm.ls(sl=True), reverse=True)
segment = len(selJnts)-1
fullWeight = 1.0
increment = fullWeight/len(selJnts)

weight = 1
for jnt in selJnts:
	weight -= increment
	parentConstraintNode = jnt.getChildren()[0]
	parentConstraintNode.Jaw_MW1.set(weight)

# Copy left constraint weight to right #
selJnts = pm.ls(sl=True)
for jnt in selJnts:
	parentConstraintNode = jnt.getChildren()[0]
	weightList = parentConstraintNode.getWeightAliasList()
	for weight in weightList:
		val = weight.get()
		oppositeWeight = pm.PyNode(weight.name().replace('lf_', 'rt_'))
		oppositeWeight.set(val)

# Distribute SDK end value #
selStickyJnts = pm.ls(os=True)
maxValue = 10.0
increment = maxValue / len(selStickyJnts)
zipValue = 0
for jnt in selStickyJnts:
	parentConst = jnt.getChildren()[0]
	weightList = parentConst.getWeightAliasList()
	zipValue += increment
	for weight in weightList:
		animCurve = weight.connections(type='animCurve')[0]
		animCurve.setUnitlessInput(1, zipValue)
