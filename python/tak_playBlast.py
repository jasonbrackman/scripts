'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Data: 

Description:


Instruction:
'''

import maya.cmds as cmds
import maya.mel as mel

# save existing heads up display state and turn off all existing huds
def saveHUDstate():
	hudOpts = ['selectDetailsVisibility', 'objectDetailsVisibility', 'particleCountVisibility', 'polyCountVisibility', 'animationDetailsVisibility', 'hikDetailsVisibility', 'frameRateVisibility', 'currentFrameVisibility', 'sceneTimecodeVisibility', 'currentContainerVisibility', 'cameraNamesVisibility', 'focalLengthVisibility', 'viewAxisVisibility']
	hudState = {}
	for hudOpt in hudOpts:
		state = mel.eval('optionVar -q %s' %(hudOpt))
		hudState[hudOpt] = state
		if state:
			setHUDopt(hudOpt, 0)

def setHUDopt(hudOpt, state):
	firstCapStr = hudOpt[0].capitalize()
	hudOpt[0] = firstCapStr
	command = 'set' + hudOpt
	mel.eval('%s %s' %(command, state))

# trun on playblast heads up display

# playblast

# back to origin heads up display state




cmds.headsUpDisplay('testHUD', section = 5, block = 1, blockSize = 'small', blockAlignment = 'right', label = 'frame :', command = 'cmds.currentTime(q = True)', dataAlignment = 'left', attachToRefresh = True, vis = True)
cmds.headsUpDisplay('testHUD', remove = True)


playblast  -offscreen 1 -format avi -sound "shot001" -filename "C:/Users/tak/Google 드라이브/Projects/ANIGRAM/ANI_MV/twinkle_twinkle_little_star/Production/Shot/shot001/Animation/TTLS_shot001_ani_v001_stlee.avi" -sequenceTime 0 -clearCache 1 -viewer 1 -showOrnaments 1 -fp 4 -percent 100 -compression "MS-CRAM" -quality 70 -widthHeight 1280 720;