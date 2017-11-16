import maya.cmds as cmds

# check the dock existing
if cmds.dockControl("dockOutliner", q = True, exists = True): 
	cmds.deleteUI("dockOutliner")  

cmds.window('dockOutl')

cmds.frameLayout(labelVisible = False)
panel = cmds.outlinerPanel()
outliner = cmds.outlinerPanel(panel, query = True, outlinerEditor = True)
cmds.outlinerEditor(outliner, edit = True, mainListConnection = 'worldList', selectionConnection = 'modelList', showShapes = False, showReferenceNodes = True, showReferenceMembers = False, showAttributes = False, showConnected = False, showAnimCurvesOnly = False, autoExpand = False, showDagOnly = True, ignoreDagHierarchy = False, expandConnections = False, showCompounds = True, showNumericAttrsOnly = False, highlightActive = True, autoSelectNewObjects = False, doNotSelectNewObjects = False, transmitFilters = False, showSetMembers = True, setFilter = 'defaultSetFilter')

cmds.showWindow('dockOutl')

# make dockable
allowedAreas = ['right', 'left']
cmds.dockControl('dockOutliner', label = "Outliner", area='left', content = 'dockOutl', allowedArea = allowedAreas)    
cmds.dockControl('dockOutliner', e = True, w = 330, h = 420)