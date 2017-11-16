import maya.cmds as cmds

### creat and assign lod02 shader ###
def lamWithTex():
	selList = cmds.ls( sl=True )
	texList = cmds.ls( tex=True )
	
	# declare variables
	global shaderDict
	global origShaderList
	global lod02ShaderList
	availableTexs = []
	shaderDict = {}
	origShaderList = []
	lod02ShaderList = []
	noTexList = []

	for x in selList:
		# query color texture files including selected object name	
		for i in texList:     
			if x in i and 'col' in i:
				availableTexs.append(i)
		
		# query original shader
		shapeName = cmds.ls( x, s=True, dag=True )
		sgName = cmds.listConnections( shapeName, d=True, type="shadingEngine" )
		origShaderName = cmds.ls(cmds.listConnections( sgName ), materials=True )
		
		# if available textrue exists, create and assign lod02 material to x
		if len(availableTexs) >= 1:
			shaderName = cmds.shadingNode( 'lambert', n='lod02_%s_mat' %x, asShader=True )
			cmds.connectAttr( '%s.outColor' %str(availableTexs[0]), (shaderName + '.color'), force=True )
			cmds.select( x )
			cmds.hyperShade( assign=shaderName )
		
		# if x has no color texture file, append to the noTexList
		elif len(availableTexs) < 1:
			noTexList.append(x)
		
		# reset the color texture list for next x
		availableTexs = []
	
	# select objects that is not assigned file texture
	print ('=' * 100)
	cmds.select(cl = True)
	for each in noTexList:
		cmds.select(each, add = True)
		print("%s  is not assigned file texture." %each)
	print ('=' * 100)