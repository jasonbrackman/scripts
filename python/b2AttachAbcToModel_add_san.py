'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date: 04/20/2016

Description:
This module is a set of additional functions used in "b2AttachAbcToModel_san.mel" script.

Usage:
Copy and paste this script to maya scripts folder.
'''



import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI



class LightlinksAfterAttachAbc():
	
	litLinkDic = {}

	def saveLitLink(self):
		'''
		Save light links information.
		'''

		litLs = cmds.ls(type = 'light')
		if litLs:
			for lit in litLs:
				ilObjLs = cmds.ls(cmds.lightlink(query = True, light = lit), type = 'mesh', long = True) # Get full dag path.
				self.litLinkDic[lit] = ilObjLs

			print '> Light links information: '
			print self.litLinkDic


	def reLinkLight(self):
		'''
		Make light links after attach alembic to model.
		'''

		if self.litLinkDic:
			for lit in self.litLinkDic.keys():
				# Break current light links.
				ilObjLs = cmds.ls(cmds.lightlink(query = True, light = lit), type = 'mesh')
				cmds.lightlink(b = True, light = lit, object = ilObjLs)

				# Get object list linked to light from saved information.
				litLinkObjLs = self.litLinkDic[lit]
				for litLinkObj in litLinkObjLs:
					try:
						# Make light link to each deformed shape assigned blend shape.
						cmds.lightlink(make = True, light = lit, object = litLinkObj.rsplit('|', 1)[0] + '|' + litLinkObj.rsplit('|', 1)[-1].rsplit(':')[-1] + 'Deformed')
					except:
						# If blend shape assigned not yet, keep light linking.
						cmds.lightlink(make = True, light = lit, object = litLinkObj)

			print '> Relink lights job is done.'



class MatAfterAttachAbc():

	renLyrMatInfo = {}

	def saveMatAssignInfo(self):
		'''
		Save materials and assigned objects, faces for each renderLayer.
		'''

		renLyrLs = cmds.ls(type = 'renderLayer')

		for renLyr in renLyrLs:
			# Initilize list variables for each render layer.
			matLs = []
			matAssignTable = []

			# Pass if render layer is default render layer.
			if 'defaultRenderLayer' in renLyr:
				continue
			else:
				try:
					# Select render layer.
					cmds.editRenderLayerGlobals(currentRenderLayer = renLyr)

					# Select visible objects in the active viewport.
					view = OpenMayaUI.M3dView.active3dView()
					OpenMaya.MGlobal.selectFromScreen( 0, 0, view.portWidth(), view.portHeight(), OpenMaya.MGlobal.kReplaceList)
					selLs = cmds.ls(sl = True)
					
					if selLs:
						for sel in selLs:
							# Try to get material for each render layer member.
							shps = cmds.listRelatives(sel, shapes = True, fullPath = True)
							if shps:
								for shp in shps:
									sg = cmds.ls(cmds.listConnections(shp), type = 'shadingEngine')
									mats = cmds.ls(cmds.listConnections(sg), materials = True)
									matLs.extend(mats)
							else:
								pass
					else:
						continue
				except:
					pass
			
			# Make material assigned table.
			for mat in list(set(matLs)):
				cmds.hyperShade(objects = mat)
				matAssignTable.append([mat, cmds.ls(sl = True)])

			self.renLyrMatInfo[renLyr] = matAssignTable

		# Select defaultRenderLayer before import alembic.
		cmds.editRenderLayerGlobals(currentRenderLayer = 'defaultRenderLayer')

		# Result print.
		print '> Material assigned information...'
		for renLyr in self.renLyrMatInfo.keys():
			print renLyr, self.renLyrMatInfo[renLyr]


	def reAssignMat(self):
		'''
		Reassign materials for each render layer with renLyrMatInfo dictionary data.
		'''

		for renLyr in self.renLyrMatInfo.keys():
			try:
				# Select render layer.
				cmds.editRenderLayerGlobals(currentRenderLayer = renLyr)
			
				for matAssignTable in self.renLyrMatInfo[renLyr]:
					mat = matAssignTable[0]
					assignedObjLs = matAssignTable[1]

					if assignedObjLs:
						for assignedObj in assignedObjLs:
							# Convert assigned object name to deformed object.
							if '.f' in assignedObj:
								assignedObj = assignedObj.split('.f')[0].split(':')[-1] + 'ShapeDeformed' + '.f' + assignedObj.split('.f')[-1]
							elif 'Shape' in assignedObj:
								assignedObj = assignedObj.split(':')[-1] + 'Deformed'
								print assignedObj
							# If assignedObj is transform node, skip this.
							else:
								continue

							# Assign the material.
							cmds.select(assignedObj, r = True)
							cmds.hyperShade(assign = mat)
					else:
						pass
			except:
				pass

		print '> Reassign materials job is done.'