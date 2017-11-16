'''
Header
    Toolname:    Copy Set Driven Key
    Author:      Sang-tak Lee
    Contact:     chst27@nate.com
    Website:    http://blog.naver.com/chst27

________________________________________________________________
Description:
    
    Install:
        1. Place tak_copySDK.py into your maya scripts folder.
           e.g., C:\Users\Documents\maya\scripts
        
                
    Usage:
		in the python tab,
		
        import tak_copySDK
        tak_copySDK.UI()

_________________________________________________________________
Feedback:
    Bugs, questions and suggestions to chst27@nate.com
'''


import maya.cmds as cmds
from functools import partial

def UI():
	# check the window existing
	if cmds.window('mirSdkWin', exists = True): cmds.deleteUI('mirSdkWin')
	
	# create the window
	cmds.window('mirSdkWin', title = 'Copy Set Driven Key', w = 475, h = 155, sizeable = False)
	
	# set the top main layout
	cmds.columnLayout()
	
	# using tabLayout for the frame 
	cmds.tabLayout(tv = False, w = 460, h = 115)
	cmds.tabLayout(tv = False, scr = True, w = 450, h = 105)
	
	# controls to get data in columnLayout
	cmds.columnLayout()
	cmds.textFieldButtonGrp('srcDrvnObjBtnGrp', label = 'Source Driven Object: ', text = '', buttonLabel = 'Load Sel')
	cmds.textFieldButtonGrp('trgDrvnObjBtnGrp', label = 'Target Driven Object: ', text = '', buttonLabel = 'Load Sel')
	cmds.textFieldButtonGrp('trgDrvrObjBtnGrp', label = 'Driver of the Target: ', text = '', buttonLabel = 'Load Sel')
	cmds.checkBoxGrp('mirChkBox', numberOfCheckBoxes = 2, columnWidth = [(2, 70)], label = 'Mirror: ', label1 = 'Driver', label2 = 'Driven')
	
	# back to the main layout
	cmds.setParent(top = True)
	
	# 'apply', 'close' button in formLayout
	fl = cmds.formLayout(nd = 100, w = 460, h = 32)
	apB = cmds.button(label = 'Apply', c = mirSDK)
	clB = cmds.button(label = 'Close', c = closeWin)
	
	cmds.formLayout(fl, e = True,
	attachForm = [(apB, 'left', 5), (apB, 'bottom', 5), (clB, 'right', 5), (clB, 'bottom', 5)],
	attachPosition = [(apB, 'right', 2.5, 50), (clB, 'left', 2.5, 50)],
	attachNone = [(apB, 'top'), (clB, 'top')]
	)
	
	# callbacks
	cmds.textFieldButtonGrp('srcDrvnObjBtnGrp', e = True, bc = partial(loadSelIntoBtnGrp, 'srcDrvnObjBtnGrp'))
	cmds.textFieldButtonGrp('trgDrvnObjBtnGrp', e = True, bc = partial(loadSelIntoBtnGrp, 'trgDrvnObjBtnGrp'))
	cmds.textFieldButtonGrp('trgDrvrObjBtnGrp', e = True, bc = partial(loadSelIntoBtnGrp, 'trgDrvrObjBtnGrp'))
	
	cmds.showWindow('mirSdkWin')

# load the selected object into the specified buttonGrp	
def loadSelIntoBtnGrp(buttonGrp):
    sel = cmds.ls(sl = True)
    cmds.textFieldButtonGrp(buttonGrp, e = True, text = sel[0])
	
# main funtion
def mirSDK(*args):
	# get the items
	sDriven = cmds.textFieldButtonGrp('srcDrvnObjBtnGrp', q = True, text = True)
	tDriven = cmds.textFieldButtonGrp('trgDrvnObjBtnGrp', q = True, text = True)
	tDriver = cmds.textFieldButtonGrp('trgDrvrObjBtnGrp', q = True, text = True)

	if cmds.checkBoxGrp('mirChkBox', q = True, v1 = True): 
		drvrMirVal = -1
	else: 
		drvrMirVal = 1
	if cmds.checkBoxGrp('mirChkBox', q = True, v2 = True): 
		drvnMirVal = -1
	else: 
		drvnMirVal = 1

	# get source data
	driverAttr = cmds.setDrivenKeyframe(sDriven, q=True, cd=True)[0].split('.')[-1]
	rawDrivenAttrs = cmds.setDrivenKeyframe(sDriven, q=True, dn=True)
	for rawDrivenAttr in rawDrivenAttrs:
		attr = rawDrivenAttr.split('.')[-1]
		drvrVals = cmds.keyframe(rawDrivenAttr, q = True, fc = True)
		drvnVals = cmds.keyframe(rawDrivenAttr, q = True, vc = True)

		for i in xrange(len(drvrVals)):
			cmds.setDrivenKeyframe('%s.%s' %(tDriven, attr), cd = '%s.%s' %(tDriver,driverAttr), dv = drvrVals[i]  * drvrMirVal , v = drvnVals[i] * drvnMirVal)
		
# close the window funtion
def closeWin(*args):
	cmds.deleteUI('mirSdkWin')