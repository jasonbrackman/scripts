import maya.cmds as cmds

def tmpFunc():
	# set nHair clumpScale
	hairSystemList = cmds.ls(sl = True)
	for hairSystem in hairSystemList:
		cmds.setAttr('%s.clumpWidthScale[1].clumpWidthScale_Position' %hairSystem, 1)
		cmds.setAttr('%s.clumpWidthScale[1].clumpWidthScale_FloatValue' %hairSystem, 1)


	### Set Pin Number of Hair Constraint ###
	# get hair constraint list
	hairConsts = cmds.listRelatives(c = True, type = 'transform')
	pin = 0
	# print hairConstraint name and pin number
	for hConst in hairConsts:
			if 'Constraint' in hConst: continue
			print 'connectHairConstraint ' + hConst, str(pin) + ';'
			pin += 1


	### Select Hair Chain Skin Joints ###
	cmds.select(cl = True)
	cmds.select('*skirt*_Ik*_jnt', add = True)
	cmds.select('*skirt*_bakeOut?_jnt', add = True)


	# Select Hairsystem Shape #
	cmds.select('wing*_Line_hairSystemShape')


	# Set to 0 for '_ctr#_zero' group of selected hair block
	selHairBlock = cmds.ls(sl = True)[0]
	prefix = selHairBlock.split('_Block')[0]
	attrList = ['rotateX', 'rotateY', 'rotateZ']
	for i in range(1, 10, 1):
		for attr in attrList:
			try:
				cmds.setAttr('%s.%s' %('%s_ctr%i_zero' %(prefix, i), attr), 0)
			except:
				break


	# Transfer rotate value of 'hair#_ctr#_crv' attributes to the '_zero group' for selected hair block.
	selList = cmds.ls(sl = True)
	attrList = ['rotateX', 'rotateY', 'rotateZ']
	for sel in selList:
		prefix = sel.split('_Block')[0]
		for i in range(1, 10, 1):
			for attr in attrList:
				try:
					crvAttrVal = cmds.getAttr('%s.%s' %('%s_ctr%i_crv' %(prefix, i), attr))
					if crvAttrVal == 0:
						continue
					else:
						zeroAttrVal = cmds.getAttr('%s.%s' %('%s_ctr%i_zero' %(prefix, i), attr))
						setAttrVal = zeroAttrVal + crvAttrVal
						cmds.setAttr('%s.%s' %('%s_ctr%i_zero' %(prefix, i), attr), setAttrVal)
						cmds.setAttr('%s.%s' %('%s_ctr%i_crv' %(prefix, i), attr), 0)
				except:
					break


	### Set to Static and Turn Off Use Nucleus Solver ###
	selLs = [x for x in cmds.ls(sl = True) if cmds.nodeType(x) == 'hairSystem']
	for sel in selLs:
		cmds.setAttr('%s.active' %sel, False)
		cmds.setAttr('%s.simulationMethod' %sel, 1)


	# Transfer translate and rotate value to parent group for moved controls'
	ctrlLs = cmds.ls(sl = True)
	attrList = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']
	for ctrl in ctrlLs:
		# Get parent gorup
		prntGrp = cmds.listRelatives(ctrl, p = True)[0]
		for attr in attrList:
			# Get control's attribute value
			attrVal = cmds.getAttr('%s.%s' %(ctrl, attr))
			
			# If control's attribute value is default value then skip
			if attrVal == 0.0:
				continue
			else:
				# Get parent group value and add control attribute value
				prntAttrVal = cmds.getAttr('%s.%s' %(prntGrp, attr))
				attrVal = prntAttrVal + attrVal
				# Set parent group value
				cmds.setAttr('%s.%s' %(prntGrp, attr), attrVal)
				# Set 0 value for control
				cmds.setAttr('%s.%s' %(ctrl, attr), 0)


	# Hair Width Scale #
	hairSysShps = cmds.ls(sl = True)
	for hairSysShp in hairSysShps:
		cmds.setAttr("%s.hairWidthScale[0].hairWidthScale_FloatValue" %hairSysShp, 200)
		cmds.setAttr("%s.hairWidthScale[1].hairWidthScale_FloatValue" %hairSysShp, 200)





# Set Default Value for Hair Chain Attributes #
def setHairChainDefaultValue():
	hairChainBlockGrps = cmds.ls(sl = True)
	for grp in hairChainBlockGrps:
		hairChainName = grp.rsplit('_Block_GRP')[0]
		
		# Set nucleus attributes.
		nucName = hairChainName + '_nucleus'
		cmds.setAttr('%s.spaceScale' %nucName, 1)
		
		# Set endCtr attributes.
		cmds.select('%s*_ctrEnd_crv' %hairChainName, r = True)
		endCtrLs = cmds.ls(sl = True, type = 'transform')
		for endCtr in endCtrLs:
			cmds.setAttr('%s.waveSize' %endCtr, 0.25)
			cmds.setAttr('%s.Damp' %endCtr, 0.1)
			cmds.setAttr('%s.Friction' %endCtr, 0.1)
			cmds.setAttr('%s.startCurveAttract' %endCtr, 0.25)
			cmds.setAttr('%s.bendResistance' %endCtr, 5)
		
			# Set hair system attributes.
			hairSysName = endCtr.rsplit('_ctrEnd_crv')[0] + '_hairSystemShape'
			cmds.setAttr('%s.stretchResistance' %hairSysName, 200)
			cmds.setAttr('%s.compressionResistance' %hairSysName, 200)
			cmds.setAttr("%s.hairWidthScale[0].hairWidthScale_FloatValue" %hairSysName, 200)
			cmds.setAttr("%s.hairWidthScale[1].hairWidthScale_FloatValue" %hairSysName, 200)

			# Set sine deformer attributes.
			ikCrvName = endCtr.rsplit('_ctrEnd_crv')[0] + '_splineIKCurveShape'
			sine = cmds.listConnections(ikCrvName, s = True, d = False, type = 'nonLinear')[0]
			cmds.setAttr('%s.wavelength' %sine, 3)

setHairChainDefaultValue()





# Hairsystem HiarWidthScale #
hairSystems = cmds.ls(sl = True)

startHairWidth = 300
endHairWidth = 400

for hairSystem in hairSystems:
	cmds.setAttr(hairSystem + '.hairWidthScale[0].hairWidthScale_FloatValue', startHairWidth)
	cmds.setAttr(hairSystem + '.hairWidthScale[1].hairWidthScale_FloatValue', endHairWidth)
