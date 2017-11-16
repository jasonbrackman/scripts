import os
import sys
import maya.cmds as cmds
import maya.mel as mel

class followingControl(object):
	"""
		Create cluster/rivet face controls. Method described by Eric Miller in Maya Techniques - Hyper Real Face Setup class.
	"""	
	def __init__(self):
		self.buildGUI()

	def buildGUI(self,*args):
		if(cmds.window("followCntWin",exists=True)):
			cmds.deleteUI("followCntWin",window=True)

		win = cmds.window("followCntWin",title="Follow Control Setup v1.1",rtf=True)

		cmds.columnLayout(adjustableColumn=True)
		cmds.frameLayout(l='Step 1: Set up rivet and name control',cl=False,cll=False,w=500)
		cmds.columnLayout(adjustableColumn=True)

		self.nameField = cmds.textFieldGrp(label="Control Name:",text="control1")
		cmds.text("Select two edges.",font='boldLabelFont')
		cmds.rowLayout(nc=1,adj=1)
		cmds.button(label="\t\t\t\t\t\t>>>> Create Control <<<<",c=self.createRivet,al='center')
		cmds.setParent('..')

		cmds.setParent('..')
		cmds.setParent('..')

		cmds.frameLayout(l='Step 2: Finalize Control',cl=False,cll=False,w=500)
		cmds.columnLayout(columnAttach=('both', 5),adjustableColumn=True)

		self.controlField = cmds.textFieldButtonGrp(label="Control:",bl="Load",bc=self.loadControl,text="")
		self.rivetField = cmds.textFieldButtonGrp(label="Rivet:",bl="Load",bc=self.loadRivet,text="")
		self.jointField = cmds.textFieldButtonGrp(label="Constrain to (Optional):",bl="Load",bc=self.loadJoint,text="")
		cmds.text(' ')
		
		cmds.text("Select vertices to influence.",font='boldLabelFont')

		cmds.rowLayout(nc=1,adj=1)
		cmds.button(label="\t\t\t\t\t\t>>>> Connect Control <<<<",c=self.setupControl,al='center')
		cmds.setParent('..')

		cmds.setParent('..')
		cmds.setParent('..')

		cmds.showWindow(win)	

	def createRivet(self,*args):
		"""
		With two edges selected by user, create the rivet and control.
		"""
		cnt = cmds.textFieldGrp(self.nameField,q=True,text=True)
		edges = cmds.ls(sl=True,fl=True)

		# Make sure two edges selected
		if len(edges) != 2:
			raise Exception('Must have two edges selected.')

		# Ensure control does not exists
		if cmds.objExists(cnt):
			raise Exception('Name for follow control is not unique.')

		# Create rivet
		try:
			cmds.select(edges,r=True)
			rivet = mel.eval('rivet')
		except Exception,e:
			raise Exception(e)
		#Rename the rivet
		try:
			cmds.rename(rivet,cnt+'_rivet')
			rivet = cnt+'_rivet'
		except Exception,e:
			print 'Error: ',e
			raise Exception( 'Failed to rename rivet.')

		# Create controller
		try:
			self.createController(cnt)
		except Exception,e:
			print 'Error: ',e
			raise Exception('Failed to create controller: %s'%cnt)

		# Load part 2 GUI fields with created objects
		cmds.textFieldButtonGrp(self.controlField,e=True,text=cnt)
		cmds.textFieldButtonGrp(self.rivetField,e=True,text=rivet)

		# Snap controller to rivet and zero/orient to world
		temp = cmds.pointConstraint(rivet,cnt,mo=False)
		cmds.delete(temp)
		cmds.makeIdentity(cnt,apply=True,t=True,r=True,s=True,n=True)

		# Hide rivet shape visibility
		cmds.setAttr('%sShape.visibility'%rivet,0)

	def setupControl(self,*args):
		#Load variables
		name = cmds.textFieldGrp(self.nameField,q=True,text=True)
		control = cmds.textFieldButtonGrp(self.controlField,q=True,text=True)
		rivet = cmds.textFieldButtonGrp(self.rivetField,q=True,text=True)
		constObj = cmds.textFieldButtonGrp(self.jointField,q=True,text=True)


		#Load selection
		verts = cmds.ls(sl=True,fl=True)

		#Create Cluster
		clusterName,clusterHandle = cmds.cluster(rel=True,n=name+'_clstr')

		#Delete Rivet's aim constraint because it causes flipping if the rivets lofted nurbs plane flips.
		#Add parent constraint to object.(constObj)
		"""
		try:
			temp = cmds.listConnections(rivet)
			cmds.delete(temp[1])
		except:
			# No constraint to delete on rivet
			pass
		"""
		#Rivet WS location
		rivetLocation = cmds.xform(rivet,q=True,ws=True,t=True)

		#Snap Cluster pivots to rivetLocation
		self.move(clusterHandle, rivetLocation,t=False,sp=True,rp=True)

		#Snap Controls pivots to rivetLocation
		self.move(control, rivetLocation,t=False,sp=True,rp=True)

		#Group Cluster
		clusterGrp = cmds.group(clusterHandle)
		clusterGrp = cmds.rename(clusterGrp, name + 'Cluster_' + clusterHandle)

		#Create over ride group
		or_grp = cmds.group(em=True,name=name+"OR1") 
		or2_grp = cmds.group(em=True,name=name+"OR2") 

		#Parent override group to rivet
		cmds.parent(or_grp,or2_grp)  
		cmds.parent(or2_grp,rivet)   

		#Freeze transforms on override group
		cmds.makeIdentity(or_grp,apply=True,t=True,r=True,s=True,n=True)

		#Zero Control
		zeroNode = cmds.group(em=True,n=name + "nullGrp")

		pos = cmds.xform( control, q=1, ws=True, t=1)
		cmds.xform( zeroNode, ws=True, t=[pos[0], pos[1], pos[2]]) 

		rot = cmds.xform( control, q=1, ws=True, ro=1)
		cmds.xform( zeroNode, ws=True, ro=[rot[0], rot[1], rot[2]]) 

		scale = cmds.xform( control, q=1, r=1, s=1)
		cmds.xform( zeroNode, ws=True, s=[scale[0], scale[1], scale[2]])		

		#Snap zeroNode pivot to control
		controlLocation = cmds.xform(control,q=True,ws=True,rp=True)
		self.move(zeroNode, controlLocation, t=False, sp=True, rp=True)

		#parent control to OverRide group
		cmds.parent(control, zeroNode, a=True)		
		cmds.parent(zeroNode,or_grp)

		#Connect control t,r,s to cluster, then hide the cluster and rivet group 
		cmds.connectAttr(control + ".translate", clusterHandle + ".translate")
		cmds.connectAttr(control + ".rotate", clusterHandle + ".rotate")
		cmds.connectAttr(control + ".scale", clusterHandle + ".scale")		

		#Create utility node and negate double transform
		#by reversing the transformation of or_grp <---- Cause of double transforms
		mdNode = cmds.createNode("multiplyDivide")
		nodeName = name + "_MD"
		cmds.rename(mdNode,nodeName)
		mdNode = nodeName

		#Unparent control
		cmds.parent(zeroNode,w=True)

		#Set up the MD node
		cmds.setAttr( "%s.input2X"%mdNode, -1)
		cmds.setAttr( "%s.input2Y"%mdNode, -1)
		cmds.setAttr( "%s.input2Z"%mdNode, -1)

		#Connect the nodes
		# control ---> mdNode
		cmds.connectAttr("%s.translateX"%control,"%s.input1X"%mdNode,f=True)
		cmds.connectAttr("%s.translateY"%control,"%s.input1Y"%mdNode,f=True)
		cmds.connectAttr("%s.translateZ"%control,"%s.input1Z"%mdNode,f=True)

		#mdNode ---> or_grp
		cmds.connectAttr("%s.outputX"%mdNode,"%s.translateX"%or_grp,f=True)
		cmds.connectAttr("%s.outputY"%mdNode,"%s.translateY"%or_grp,f=True)
		cmds.connectAttr("%s.outputZ"%mdNode,"%s.translateZ"%or_grp,f=True)

		#Reparent control
		cmds.parent(zeroNode,or_grp)

		#Get mesh name 
		# ex. "meshName.vtx[35]"
		mesh = verts[0].split('.')[0]

		#Get meshDeformer
		meshDeformer = None
		try:
			meshDeformer = mel.eval('findRelatedSkinCluster("%s");'%mesh)
		except:
			pass
		"""
		history = cmds.listHistory(mesh)  
		for each in history:
			#print " History: " + each
			if("skinCluster" in str(each)):
				#Possible match for meshDeformer
				if("Group" not in str(each)):
					meshDeformer = each
			if("cMuscleSystem" in str(each)):
				if("Group" not in str(each)):
					meshDeformer = each
		"""
		#Reorder deformer nodes
		if meshDeformer:
			#Move cluster + meshDeformer to top of deformer stack
			cmds.reorderDeformers(clusterHandle,meshDeformer,mesh)

			#Move meshDeformer to top of deformer stack
			cmds.reorderDeformers(meshDeformer,clusterHandle,mesh)

		#Create final group
		topGrp = cmds.group(em=True,name=name+"_followCnt_grp")
		cmds.parent(clusterGrp,rivet,topGrp)

		#Orient constrain rivet to constrain object
		if constObj:
			cmds.orientConstraint(constObj,rivet,mo=True)

		#Hide cluster grp
		cmds.setAttr(clusterGrp + ".visibility",0) 

		#Hide the rivet
		rivetShape = cmds.listRelatives(rivet,shapes=True)
		cmds.setAttr(rivetShape[0] + ".visibility",0)
		
		# Add cluster atttribute to control
		cmds.addAttr(control,ln='cluster',min=0.0,max=1.0,dv=1.0)
		cmds.setAttr('%s.cluster'%control,l=False,k=True)
		
		# Connect it to the deformer
		cmds.connectAttr('%s.cluster'%control,'%s.envelope'%clusterName,f=True)

		#Clear selection
		cmds.select(clear=True)

	def move(self,tgt=None,position=None,t=True,sp=False,rp=False):
		r""" Set tgt translations to values in position. """
		if not tgt: raise Exception('No target specified.')
		if not position: raise Exception('No position specified.')

		if sp:
			try:
				cmds.setAttr('%s.scalePivotX'%tgt,position[0])
				cmds.setAttr('%s.scalePivotY'%tgt,position[1])
				cmds.setAttr('%s.scalePivotZ'%tgt,position[2])
			except Exception,e:
				raise Exception(e)	

		if rp:
			try:
				cmds.setAttr('%s.rotatePivotX'%tgt,position[0])
				cmds.setAttr('%s.rotatePivotY'%tgt,position[1])
				cmds.setAttr('%s.rotatePivotZ'%tgt,position[2])
			except Exception,e:
				raise Exception(e)	

		if t:
			try:
				cmds.setAttr('%s.translateX'%tgt,position[0])
				cmds.setAttr('%s.translateY'%tgt,position[1])
				cmds.setAttr('%s.translateZ'%tgt,position[2])
			except Exception,e:
				raise Exception(e)

	def createController(self,name):
		"""
		Creates controller curve at origin.
		"""
		cnt = mel.eval('createNode transform -n "%s";\n'%name+\
		               'setAttr ".ove" yes;\n'+\
		               'setAttr ".ovc" 15;\n'+\
		               'createNode nurbsCurve -n "%sShape" -p "%s";\n'%(name,name)+\
		               'setAttr -k off ".v";\n'+\
		               'setAttr ".cc" -type "nurbsCurve" \n'+\
		               '1 52 0 no 3 \n'+\
		               '53 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 \n'+\
		               ' 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 \n'+\
		               '53 \n'+\
		               '0 0.074400512458903195 0 \n'+\
		               '0 0.068737145450531487 0.028471811309310452 \n'+\
		               '0 0.052609123163277663 0.052609123163277663 \n'+\
		               '0 0.028471811309310452 0.068737145450531487 \n'+\
		               '0 0 0.074400512458903195 \n'+\
		               '0 -0.028471811309310452 0.068737145450531487 \n'+\
		               '0 -0.052609123163277663 0.052609123163277663 \n'+\
		               '0 -0.068737145450531487 0.028471811309310452 \n'+\
		               '0 -0.074400512458903195 0 \n'+\
		               '0 -0.068737145450531487 -0.028471811309310452 \n'+\
		               '0 -0.052609123163277663 -0.052609123163277663 \n'+\
		               '0 -0.028471811309310452 -0.068737145450531487 \n'+\
		               '0 0 -0.074400512458903195 \n'+\
		               '0 0.028471811309310452 -0.068737145450531487 \n'+\
		               '0 0.052609123163277663 -0.052609123163277663 \n'+\
		               '0 0.068737145450531487 -0.028471811309310452 \n'+\
		               '0 0.074400512458903195 0 \n'+\
		               '0.028471811309310452 0.068737145450531487 0 \n'+\
		               '0.052609123163277663 0.052609123163277663 0 \n'+\
		               '0.068737145450531487 0.028471811309310452 0 \n'+\
		               '0.074400512458903195 0 0 \n'+\
		               '0.068737145450531487 -0.028471811309310452 0 \n'+\
		               '0.052609123163277663 -0.052609123163277663 0 \n'+\
		               '0.028471811309310452 -0.068737145450531487 0 \n'+\
		               '0 -0.074400512458903195 0 \n'+\
		               '-0.028471811309310452 -0.068737145450531487 0 \n'+\
		               '-0.052609123163277663 -0.052609123163277663 0 \n'+\
		               '-0.068737145450531487 -0.028471811309310452 0 \n'+\
		               '-0.074400512458903195 0 0 \n'+\
		               '-0.068737145450531487 0.028471811309310452 0 \n'+\
		               '-0.052609123163277663 0.052609123163277663 0 \n'+\
		               '-0.028471811309310452 0.068737145450531487 0 \n'+\
		               '0 0.074400512458903195 0 \n'+\
		               '0 0.068737145450531487 -0.028471811309310452 \n'+\
		               '0 0.052609123163277663 -0.052609123163277663 \n'+\
		               '0 0.028471811309310452 -0.068737145450531487 \n'+\
		               '0 0 -0.074400512458903195 \n'+\
		               '-0.028471811309310452 0 -0.068737145450531487 \n'+\
		               '-0.052609123163277663 0 -0.052609123163277663 \n'+\
		               '-0.068737145450531487 0 -0.028471811309310452 \n'+\
		               '-0.074400512458903195 0 0 \n'+\
		               '-0.068737145450531487 0 0.028471811309310452 \n'+\
		               '-0.052609123163277663 0 0.052609123163277663 \n'+\
		               '-0.028471811309310452 0 0.068737145450531487 \n'+\
		               '0 0 0.074400512458903195 \n'+\
		               '0.028471811309310452 0 0.068737145450531487 \n'+\
		               '0.052609123163277663 0 0.052609123163277663 \n'+\
		               '0.068737145450531487 0 0.028471811309310452 \n'+\
		               '0.074400512458903195 0 0 \n'+\
		               '0.068737145450531487 0 -0.028471811309310452 \n'+\
		               '0.052609123163277663 0 -0.052609123163277663 \n'+\
		               '0.028471811309310452 0 -0.068737145450531487 \n'+\
		               '0 0 -0.074400512458903195 \n'+\
		               ';')

	def loadControl(self,*args):
		sel = cmds.ls(sl=True)
		cmds.textFieldButtonGrp(self.controlField,e=True,text=sel[0])

	def loadRivet(self,*args):
		sel = cmds.ls(sl=True)
		cmds.textFieldButtonGrp(self.rivetField,e=True,text=sel[0])

	def loadJoint(self,*args):
		sel = cmds.ls(sl=True)
		cmds.textFieldButtonGrp(self.jointField,e=True,text=sel[0])		
