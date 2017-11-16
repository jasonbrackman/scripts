#!/bin/env python
 ###############################################################################
 #
 #  Copying weight by txt file maya python scripts. Copyleft (c) 2013 Jon Hwang
 #
 #    $HeadURL: $
 #    $Revision: $ 2
 #    $Author:  $ Jonghwan Hwang
 #    $Date: $ 2013 - 08 - 13
 #
 ###############################################################################
"""
This script is used to save skin value as a txt file

usage : 
	
	1. Select all the vertex from the skinned mesh first##########
	2. This will print out name of joints attached to the skinned mesh
		
		CopyWeightByTxt.joint()
		CopyWeightByTxt.vertex()
	
	3. You can detach skin and modify joint location###########
	
	4. Skin back with the joints printed out in before, 
		select all the vertexes and run next
		
		CopyWeightByTxt.paste()

"""

import maya.cmds as cmds
import string
import sys
import os


class CopyWeightByTxt(object):
	# Defining path for saved txt file
	FILE_NAME = 'skinvalue.txt'
	HOME = os.path.expanduser('~')               
	PATH = os.path.join(HOME, FILE_NAME) 
	
	# Defining class member
	name_joint = None                            
	name_skincluster = None                      
	name_splited_vertex = None                   
	number_of_vertex = None                        
	 
	@classmethod
	def joint(cls):
		''' Getting joints from the selected mesh '''
		
		# Getting selected mesh
		poly = cmds.ls(sl=True)                
		
		# Getting joint from skinned mesh
		try :
			cls.name_skincluster = cmds.skinCluster(poly, q=True, dt=True)
			cls.name_skincluster = cls.name_skincluster[-1][0:-7]
			cls.name_joint = cmds.skinCluster(poly, q=True, inf=True)
			print cls.name_joint                 
		
		# Check if proper mesh is selected
		except :
			print "please select skinned mesh"
	
	@classmethod	
	def vertex(cls):
		''' Getting vertax info and saves weights into txt file '''
		
		# Getting selected vertex
		vertex = cmds.ls(sl=True)              
		splited_vertex = string.split(vertex[0], ':')
		cls.number_of_vertex = int(splited_vertex[-1][0:-1]) + 1
		cls.name_splited_vertex = string.split(vertex[0], '[')	
		
		# Getting skin value from selected vertexes	and write txt file	
		txtFile = open(cls.PATH, 'w')
		for vertexIndex in range(cls.number_of_vertex):
			transformValue = []
			for joint in cls.name_joint:
				tvTemp = cmds.skinPercent(cls.name_skincluster,'%s[%s]' 
							%(cls.name_splited_vertex[0], vertexIndex), 
							transform='%s' %joint, query=True 
							)
				transformValue.append(tvTemp)
			txtFile.write('%s\n' %transformValue)
		txtFile.close()
		print "Finished writing txt file at %s" %cls.PATH
	
	@classmethod
	def paste(cls):	
		''' Read txt file and paste weight '''		
		
		# Read File
		txtFile = open(cls.PATH)
		skinValue = txtFile.readline()
		transformValuePaste = ''
		
		# Redefining skincluster to be safe from naming conflict
		poly = cmds.ls(sl=True)
		cls.name_skincluster = cmds.skinCluster(poly, q=True, dt=True)
		cls.name_skincluster = cls.name_skincluster[-1][0:-7]

		# Making array of transform value from txt		
		vertexIndex = 0
		while(vertexIndex < cls.number_of_vertex):
			skinValue = string.split(skinValue[1:-2], ',')			
			transformValuePaste = []
			for jointIndex in range(len(cls.name_joint)):
				skinValueFloat = float(skinValue[jointIndex])
				jointName = str(cls.name_joint[jointIndex])
				tvTemp = [jointName, skinValueFloat]
				transformValuePaste.append(tvTemp)
			
			# Assigning skin value to the mesh 
			cmds.skinPercent(cls.name_skincluster, '%s[%s]' 
							%(cls.name_splited_vertex[0], vertexIndex), 
							transformValue = transformValuePaste
							)
							
			skinValue = txtFile.readline()
			vertexIndex = vertexIndex + 1
		print "Finished transferring skin weight from %s" %cls.PATH
		
'''#example

from copySkinWeight import *

CopyWeightByTxt.joint()

CopyWeightByTxt.vertex()

CopyWeightByTxt.paste()


x = [u'MiddleFinger3_R', u'MiddleFinger2_R', u'MiddleFinger1_R', u'ThumbFinger3_R', u'ThumbFinger2_R', u'ThumbFinger1_R', u'IndexFinger3_R', u'Eye_R', u'Jaw_M', u'Head_M', u'Neck_M', u'Chest_M', u'BackB_M', u'BackA_M', u'Root_M', u'ElbowPart1_R', u'ElbowPart2_R', u'ShoulderPart1_R', u'ShoulderPart2_R', u'NeckPart1_M', u'NeckPart2_M', u'IndexFinger1_L', u'PinkyFinger3_L', u'PinkyFinger2_L', u'PinkyFinger1_L', u'RingFinger3_L', u'RingFinger2_L', u'RingFinger1_L', u'Cup_L', u'Wrist_L', u'ElbowPart1_L', u'ElbowPart2_L', u'ShoulderPart1_L', u'ShoulderPart2_L', u'Elbow_L', u'Shoulder_L', u'Scapula_L', u'Eye_L', u'MiddleFinger3_L', u'MiddleFinger2_L', u'MiddleFinger1_L', u'ThumbFinger3_L', u'ThumbFinger2_L', u'ThumbFinger1_L', u'IndexFinger3_L', u'IndexFinger2_L', u'IndexFinger2_R', u'IndexFinger1_R', u'PinkyFinger3_R', u'PinkyFinger2_R', u'PinkyFinger1_R', u'RingFinger3_R', u'RingFinger2_R', u'RingFinger1_R', u'Cup_R', u'Wrist_R', u'Elbow_R', u'Shoulder_R', u'Scapula_R', u'BackA_M_50', u'BackB_M_50', u'Chest_M_50', u'Cup_L_50', u'Cup_R_50', u'Elbow_L_50', u'Elbow_R_50', u'Eye_L_50', u'Eye_R_50', u'Head_M_50', u'IndexFinger1_L_50', u'IndexFinger1_R_50', u'IndexFinger2_L_50', u'IndexFinger2_R_50', u'IndexFinger3_L_50', u'IndexFinger3_R_50', u'Jaw_M_50', u'MiddleFinger1_L_50', u'MiddleFinger1_R_50', u'MiddleFinger2_L_50', u'MiddleFinger2_R_50', u'MiddleFinger3_L_50', u'MiddleFinger3_R_50', u'Neck_M_50', u'PinkyFinger1_L_50', u'PinkyFinger1_R_50', u'PinkyFinger2_L_50', u'PinkyFinger2_R_50', u'PinkyFinger3_L_50', u'PinkyFinger3_R_50', u'RingFinger1_L_50', u'RingFinger1_R_50', u'RingFinger2_L_50', u'RingFinger2_R_50', u'RingFinger3_L_50', u'RingFinger3_R_50', u'Scapula_L_50', u'Scapula_R_50', u'Shoulder_L_50', u'Shoulder_R_50', u'ThumbFinger1_L_50', u'ThumbFinger1_R_50', u'ThumbFinger2_L_50', u'ThumbFinger2_R_50', u'ThumbFinger3_L_50', u'ThumbFinger3_R_50', u'Wrist_L_50', u'Wrist_R_50', u'fin1_Root_Line1_Out', u'fin1_Root_Line1_IKSkin', u'fin1_Root_Line2_Bake_Out', u'fin1_Root_Line3_IKSkin', u'fin1_Root_Line3_Bake_Out', u'fin1_Root_Line5_IKSkin', u'fin1_Root_Line4_Bake_Out', u'fin1_Root_Line7_IKSkin', u'fin1_Root_Line5_Bake_Out', u'fin0_Root_Line1_Out', u'fin0_Root_Line1_IKSkin', u'fin0_Root_Line2_Bake_Out', u'fin0_Root_Line3_IKSkin', u'fin0_Root_Line3_Bake_Out', u'fin0_Root_Line5_IKSkin', u'fin0_Root_Line4_Bake_Out', u'fin0_Root_Line7_IKSkin', u'fin0_Root_Line5_Bake_Out', u'breast0_Root_Line1_Out', u'breast0_Root_Line1_IKSkin', u'breast0_Root_Line2_Bake_Out', u'breast0_Root_Line3_IKSkin', u'breast0_Root_Line3_Bake_Out', u'breast0_Root_Line5_IKSkin', u'breast0_Root_Line4_Bake_Out', u'breast0_Root_Line7_IKSkin', u'breast0_Root_Line5_Bake_Out', u'breast1_Root_Line1_Out', u'breast1_Root_Line1_IKSkin', u'breast1_Root_Line2_Bake_Out', u'breast1_Root_Line3_IKSkin', u'breast1_Root_Line3_Bake_Out', u'breast1_Root_Line5_IKSkin', u'breast1_Root_Line4_Bake_Out', u'breast1_Root_Line7_IKSkin', u'breast1_Root_Line5_Bake_Out']

for each in x:
    cmds.select(each, add=True)
'''





