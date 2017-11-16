'''
Author: Sang-tak Lee
Contact: chst27@gmail.com

Description:
This script allow to modify skinned geometry topology.

Requirement:
tak_cleanUpModel
tak_misc

Usage:
1. Copy this script and paste in your scripts folder.

2. In maya python tab, run following code.
import tak_editSkinGeo
reload(tak_editSkinGeo)
eSkinGeoObj = tak_editSkinGeo.EditSkinGeo()
eSkinGeoObj.UI()

'''

import maya.cmds as cmds
import tak_cleanUpModel
import tak_misc
import tak_lib

class EditSkinGeo:

	def UI(self):
		winName = 'ESGWin'
		if cmds.window(winName, exists = True):
			cmds.deleteUI(winName)

		cmds.window(winName, title = 'Edit Skin Geometry UI')
		
		cmds.rowColumnLayout(numberOfColumns = 2)
		cmds.button(w = 100, h = 50, label = 'Edit', c = self.edit)
		cmds.button(w = 100, h = 50, label = 'Done', c = self.done)

		cmds.window(winName, e = True, w = 200, h = 50)
		cmds.showWindow(winName)

	def edit(self, *args):
		# duplicate skin geometry for saving skin weights
		self.skinGeo = cmds.ls(sl = True)[0]
		cmds.duplicate(self.skinGeo, n = 'tempGeo')

		cmds.select('tempGeo', r = True)
		tak_cleanUpModel.delHis()
		tak_cleanUpModel.delInterMediObj()

		cmds.setAttr('%s.visibility' %'tempGeo', False)

		# transfer skin weights from skin geometry to the temporary geometry
		cmds.select(self.skinGeo, r = True)
		cmds.select('tempGeo', add = True)
		tak_misc.TransSkinWeights()

		# clean up skin geometry
		cmds.select(self.skinGeo, r = True)
		tak_cleanUpModel.delHis()
		tak_cleanUpModel.delInterMediObj()

		'''# assign sculpt shader
		if not cmds.objExists('correctiveCorrective_mat'):
		    	shaderName = cmds.shadingNode('lambert', n = 'correctiveCorrective_mat', asShader = True)
		    	cmds.setAttr("%s.color" %shaderName, 0.686, 0.316, 0.121)
		else:
		   	 shaderName = 'correctiveCorrective_mat'
		cmds.select(self.skinGeo, r = True)
		cmds.hyperShade(assign = shaderName)'''

		# show heads up display
		tak_lib.showHUD('editSkinGeoModeDisplay', 'Edit Skin Geometry Mode')

	def done(self, *args):
		# remove heads up display
		cmds.headsUpDisplay('editSkinGeoModeDisplay', remove = True)
		
		# delete history
		cmds.select(self.skinGeo, r = True)
		tak_cleanUpModel.delHis()
		tak_cleanUpModel.delInterMediObj()

		# transfer skin weights from temporary geometry to the original geometry
		cmds.select('tempGeo', r = True)
		cmds.select(self.skinGeo, add = True)
		tak_misc.TransSkinWeights()

		'''# copy original shader
		cmds.select('tempGeo', r = True)
		cmds.select(self.skinGeo, add = True)
		tak_misc.copyMat()'''

		# delete temporary geometry
		cmds.delete('tempGeo')