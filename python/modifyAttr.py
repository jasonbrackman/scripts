'''
Author: Sang-tak Lee
Contact: chst27@gmail.com


'''

def UI():




def modiMinMax(attrName, minVal, maxVal):
	selList = cmds.ls(sl = True)
	for sel in selList:
		cmds.addAttr('%s.%s' %(sel, attrName), e = True, min = minVal, max = maxVal)

def aliasAttr(*args):
	search = cmds.textFieldGrp('srchTxtFldGrp', q = True, text = True)
	replace = cmds.textFieldGrp('rplcTxtFldGrp', q = True, text = True)

	selList = cmds.ls(sl = True)

	for sel in selList:
	    cmds.aliasAttr(replace, '%s.%s' %(sel, search))

# set random value for selected object #
selList = cmds.ls(sl = True)
attrName = 'thickness'
minVal = 10
maxVal = 30
for sel in selList:
    resultVal = random.uniform(minVal, maxVal)
    cmds.setAttr('%s.%s' %(sel, attrName), resultVal)