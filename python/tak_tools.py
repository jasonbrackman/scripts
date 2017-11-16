"""
Author: Sang-tak Lee
Contact: chst27@gmail.com
Created: 12/22/2015
Updated: 09/11/2017

Description:
    Custom shelf tool to organize shelf buttons more efficiently.

Usage:
    import tak_tools
    reload(tak_tools)
    tak_tools.UI()
"""


import os
import re
import subprocess
from functools import partial

from maya import cmds
from maya import mel
from maya import OpenMayaUI as omui

import tak_misc

MAYA_VER = cmds.about(version=True)
if int(MAYA_VER) > 2016:    
    from PySide2 import QtWidgets
    from shiboken2 import wrapInstance

# track selection order on
cmds.selectPref(tso = True)

TAK_TOOL_PATH = 'D:/Tak/Program_Presets/tak_maya_preset/prefs/scripts/python/tak_tools.py'
ICON_DIR_PATH = 'D:/Tak/Program_Presets/tak_maya_preset/prefs/icons'

# Refresh tak_tools whenever new scene opened
cmds.scriptJob(event=['NewSceneOpened', 'tak_tools.UI()'])


def UI():
    if cmds.window('takToolWin', exists = True):
        cmds.deleteUI('takToolWin')
    
    cmds.window('takToolWin', title = 'Tak Tools', menuBar = True, mnb = False, mxb = False)

    # Main menu section
    cmds.menu('fileMenu', label = 'File', p = 'takToolWin')
    cmds.menuItem(label = 'Save Tools', c = saveTools, p = 'fileMenu')
    cmds.menu('editMenu', label = 'Edit', p = 'takToolWin')
    cmds.menuItem(label = 'Add Tool', c = addToolUi, p = 'editMenu')

    cmds.paneLayout('mainPaneLo', configuration = 'horizontal2', paneSize = [(2, 63, 37)])

    cmds.formLayout('mainFormLo', p = 'mainPaneLo')

    # common tools section #
    cmds.tabLayout('cmnToolTabLo', tv = False, p = 'mainFormLo')
    cmds.shelfLayout('Common', h = (36.5 * 4), parent = 'cmnToolTabLo')
    cmds.shelfButton(annotation = 'Set maya preference.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'setPref.bmp', command = 'import tak_shotSetUp\nreload(tak_shotSetUp)\ntak_shotSetUp.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'b1Pipeline', width = 35, height = 35, imageOverlayLabel = '', image1 = 'b2Pipeline.bmp', command = 'source "N:/b1Env/maya/2014/scripts/b2Pipeline/b2Pipeline.mel";\nb2Pipeline', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Open with current working directory.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'openCurWorkDir.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.openCWD()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Save as in current working directory.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'saveCurWorkDir.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.saveCWD()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Increment save in current working directory.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'increSave.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.increSave()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Imort with current working directory.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'importCurWorkDir.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.importCWD()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Export selected in current working directory.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'exportCurWorkDir.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.exportCWD()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Select all the children of the current selection', width = 35, height = 35, imageOverlayLabel = 'SH', image1 = 'menuIconEdit.png', command = 'SelectHierarchy', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Delete construction history on the selected object(s)', width = 35, height = 35, imageOverlayLabel = 'Hist', image1 = 'menuIconEdit.png', command = 'DeleteHistory', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Freeze Transformations', width = 35, height = 35, imageOverlayLabel = 'FT', image1 = 'menuIconModify.png', command = 'FreezeTransformations', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Center Pivot', width = 35, height = 35, imageOverlayLabel = 'CP', image1 = 'menuIconModify.png', command = 'CenterPivot', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Delete construction history, unlock normal, unlock attr, delete intermediate shapes, freeze transform', width = 35, height = 35, imageOverlayLabel = '', image1 = 'cleanUpMesh.bmp', command = 'import tak_cleanUpModel\nreload(tak_cleanUpModel)\ntak_cleanUpModel.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Rename with source object.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'renameWithSrc.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.renameWithSrc()', sourceType = 'python')
    cmds.shelfButton(annotation = 'hash renaming', width = 35, height = 35, imageOverlayLabel = '', image1 = 'hashRename.bmp', command = 'source js_hashRenameUI;\njs_hashRenameUI', sourceType = 'mel')
    cmds.shelfButton(annotation = 'rename advanced', width = 35, height = 35, imageOverlayLabel = '', image1 = 'reName.bmp', command = 'source renameAdvanced;\nrenameObjectsUI();', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Sorting outliner', width = 35, height = 35, imageOverlayLabel = '', image1 = 'sortingOutliner.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.sortOutl()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Edit the references for the current scene', width = 35, height = 35, imageOverlayLabel = 'Ref', image1 = 'menuIconWindow.png', command = 'ReferenceEditor', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Namespace Editor', width = 35, height = 35, imageOverlayLabel = 'Name', image1 = 'menuIconWindow.png', command = 'NamespaceEditor', sourceType = 'mel')
    cmds.shelfButton(annotation = 'UV Texture Editor', width = 35, height = 35, imageOverlayLabel = 'UV', image1 = 'menuIconWindow.png', command = 'TextureViewWindow', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Display and edit connections in shading networks', width = 35, height = 35, imageOverlayLabel = 'Mat', image1 = 'menuIconWindow.png', command = 'HypershadeWindow', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Display relationships among nodes in your scene graphically', width = 35, height = 35, imageOverlayLabel = 'Node', image1 = 'menuIconWindow.png', command = 'NodeEditorWindow', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Make connections between object attributes', width = 35, height = 35, imageOverlayLabel = 'CnEd', image1 = 'menuIconWindow.png', command = 'ConnectionEditor', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Attribute Spread Sheet', width = 35, height = 35, imageOverlayLabel = 'SpSh', image1 = 'menuIconWindow.png', command = 'SpreadSheetEditor', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Expression Editor', width = 35, height = 35, imageOverlayLabel = 'Expr', image1 = 'menuIconWindow.png', command = 'ExpressionEditor', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Edit animation curves', width = 35, height = 35, imageOverlayLabel = 'Graph', image1 = 'menuIconWindow.png', command = 'GraphEditor', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = 'CVs', image1 = 'menuIconDisplay.png', command = 'ToggleCVs', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = 'EP', image1 = 'menuIconDisplay.png', command = 'ToggleEditPoints', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = 'Vert', image1 = 'menuIconDisplay.png', command = 'ToggleVertices', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = 'Jnt', image1 = 'menuIconDisplay.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.hideShowViewJnt()', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = 'Crv', image1 = 'menuIconDisplay.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.hideShowViewCrv()', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = 'Poly', image1 = 'menuIconDisplay.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.hideShowViewPoly()', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = 'Mdl', image1 = 'menuIconDisplay.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.hideShowViewMdl()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Object Details', width = 35, height = 35, imageOverlayLabel = 'objDtail', image1 = 'menuIconDisplay.png', command = 'ToggleObjectDetails', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = 'PCount', image1 = 'menuIconDisplay.png', command = 'TogglePolyCount', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Frame Rate', width = 35, height = 35, imageOverlayLabel = 'FRate', image1 = 'menuIconDisplay.png', command = 'ToggleFrameRate', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = 'CFrame', image1 = 'menuIconDisplay.png', command = 'ToggleCurrentFrame', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Camera Names', width = 35, height = 35, imageOverlayLabel = 'Cam', image1 = 'menuIconDisplay.png', command = 'ToggleCameraNames', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Changing current camera view', width = 35, height = 35, imageOverlayLabel = '', image1 = 'orthoView.png', command = 'import tak_orthoView\nreload(tak_orthoView)\ntak_orthoView.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'borderEdge.png', command = 'cmds.polyOptions(r=True, db=True)', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'borderEdgeWidth.png', command = 'ChangeEdgeWidth', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'xRay.bmp', command = '{\n    string $selection[] = `ls -sl`;  \n    \n    for ($cur in $selection){\n        \n        int $result[] = `displaySurface -q -x $cur `;\n        if ( $result[0] )\n            displaySurface -x 0 $cur ;\n        else\n            displaySurface -x 1 $cur ;\n            \n    }    \n}', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'togWire.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.Wire()', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'wireOnOff.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.wireOnOff()', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'useDfltMat.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.useDfltMat()', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'presetMat.bmp', command = 'import tak_matPreset\nreload(tak_matPreset)\ntak_matPreset.MatPreset.ui()', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'jointColor.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.setJntColorUI()', sourceType = 'python')

    cmds.separator('mainSep', h = 10, style = 'in', p = 'mainFormLo')

    # task tools section #
    # create tab
    cmds.tabLayout('taskTabLo', p = 'mainFormLo')
    riggingTab = cmds.formLayout('RiggingFormLo', w = 21 * 21, p = 'taskTabLo')
    aniTab = cmds.formLayout('AnimationFormLo', w = 21 * 21, p = 'taskTabLo')
    modelTab = cmds.formLayout('ModelingFormLo', w = 21 * 21, p = 'taskTabLo')
    miscTab = cmds.formLayout('MiscFormLo', w = 21 * 21, p = 'taskTabLo')
    cmds.tabLayout('taskTabLo', e = True, tabLabel = [(riggingTab, 'Rigging'), (aniTab, 'Animation'), (modelTab, 'Modeling'), (miscTab, 'Misc')])


    # Editing main layout
    cmds.formLayout('mainFormLo', e = True,
        attachForm = [('cmnToolTabLo', 'top', 0), ('cmnToolTabLo', 'left', 0), ('cmnToolTabLo', 'right', 0), ('mainSep', 'left', 0), ('mainSep', 'right', 0), ('taskTabLo', 'left', 0), ('taskTabLo', 'right', 0), ('taskTabLo', 'bottom', 0)],
        attachControl = [('mainSep', 'top', 5, 'cmnToolTabLo'), ('taskTabLo', 'top', 5, 'mainSep')])

    # rigging tab
    cmds.scrollLayout('riggingScrLo', childResizable = True, p = 'RiggingFormLo')
    cmds.formLayout('RiggingFormLo', e = True, attachForm = [('riggingScrLo', 'top', 0), ('riggingScrLo', 'bottom', 0), ('riggingScrLo', 'left', 0), ('riggingScrLo', 'right', 0)])
    cmds.frameLayout('riggingDisplayFrameLo', label = 'Display', collapse = False, collapsable = True, p = 'riggingScrLo')
    cmds.shelfLayout('Rigging_Display', h = (41 * 1), p = 'riggingDisplayFrameLo')
    cmds.shelfButton(annotation = 'toggle -state on -localAxis;', width = 35, height = 35, imageOverlayLabel = 'LRAO', image1 = 'commandButton.png', command = 'toggle -state on -localAxis;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'toggle -state off -localAxis;', width = 35, height = 35, imageOverlayLabel = 'LRAF', image1 = 'commandButton.png', command = 'toggle -state off -localAxis;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Customize the joint scale', width = 35, height = 35, imageOverlayLabel = 'JS', image1 = 'menuIconDisplay.png', command = 'jdsWin', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Change the joint style', width = 35, height = 35, imageOverlayLabel = '', image1 = 'jointStyle.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.drawJntStyle()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Change display type.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'displayType.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.displayType()', sourceType = 'python')

    cmds.frameLayout('riggingEditMdlFrameLo', label = 'Edit Model', collapse = False, collapsable = True, p = 'riggingScrLo')
    cmds.shelfLayout('Rigging_Edit_Model', h = (38 * 2), p = 'riggingEditMdlFrameLo')
    cmds.shelfButton(annotation = 'Create lod02 material and assign to the selected lod02 geometries.', width = 35, height = 35, imageOverlayLabel = 'lod02Mat', image1 = 'pythonFamily.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.lod02Mat()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Duplicate material and assign duplicated material.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'dupMatAssign.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.dupMatAndAssign()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Assign lambert with a selected texture.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'lambertWithSelectedTexture.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.assignLambertWithSelectedTexture()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Assign solid color material with grabed color.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'solColorMat.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.solidColMat()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Assign the material of first selection to the others', width = 35, height = 35, imageOverlayLabel = '', image1 = 'copyMat.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.copyMat()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Copy selected objects texture', width = 35, height = 35, imageOverlayLabel = '', image1 = 'copyTexture.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.copyTexRenameUI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Soften Edge', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polySoftEdge.png', command = 'SoftPolyEdgeElements 1', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Unlock Normals', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyNormalUnlock.png', command = 'polyNormalPerVertex -ufn true', sourceType = 'mel')
    cmds.shelfButton(annotation = "\tCut selected geometry with selected joints.\n\tUsing 'js_cutPlane.mel' script.\n\tSelect first joints and geometry last.", width = 35, height = 35, imageOverlayLabel = '', image1 = 'cutGeoWithJoints.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.cutGeoWithJnts()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Add plane for cutting polygonal geometry', width = 35, height = 35, imageOverlayLabel = '', image1 = 'addPlane.bmp', command = 'source js_cutPlane;\njs_cutPlane_create;\n', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Cut selected object with planes', width = 35, height = 35, imageOverlayLabel = '', image1 = 'cutPlaneDone.bmp', command = 'source js_cutPlane;\njs_cutPlane_cut 1;\n', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Combine the selected polygon objects into one single object to allow operations such as merges or face trims', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyUnite.png', command = 'polyPerformAction polyUnite o 0', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Sculpting brushes.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'SHAPESBrush.png', command = 'SHAPESBrushUI', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Sculpt a geometry object.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'putty.png', command = 'SculptGeometryTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Symmetry or flip geometry.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'abSym.bmp', command = 'abSymMesh', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Assign random color lamber.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'ranColLam.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.ranColLam()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Set smooth level.', width = 35, height = 35, imageOverlayLabel = 'smLevel', image1 = 'pythonFamily.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.setSmoothLevelUI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Copy all uv sets and material from source to target.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'copyUvMat.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.copyUvMat()', sourceType = 'python')
    cmds.shelfButton(annotation = 'File Texture Manager', width = 35, height = 35, imageOverlayLabel = '', image1 = 'texManger.bmp', command = 'FileTextureManager;', sourceType = 'mel')

    cmds.frameLayout('riggingBuildFrameLo', label = 'Build', collapse = False, collapsable = True, p = 'riggingScrLo')
    cmds.shelfLayout('Rigging_Build', h = (36.5 * 4), p = 'riggingBuildFrameLo')
    cmds.shelfButton(annotation = 'Advanced skeleton body setup window.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'AdvancedSkeleton/asBody.png', command = 'source "AdvancedSkeleton/asBody.mel";asBody;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'AdvancedSkeleton5', width = 35, height = 35, imageOverlayLabel = '', image1 = 'C:/Users/stlee/Documents/maya/2015-x64/scripts/AdvancedSkeleton5/AdvancedSkeleton5Files/icons/AS5.png', command = 'source "C:/Users/stlee/Documents/maya/2015-x64/scripts/AdvancedSkeleton5/AdvancedSkeleton5.mel";AdvancedSkeleton5;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'scripts for the advanced skeleton', width = 35, height = 35, imageOverlayLabel = '', image1 = 'toolForAs.bmp', command = 'import toolForAs\nreload(toolForAs)\ntoolForAs.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Click to place joint. Click on existing joint to add to skeleton. Click-Drag to position joint.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'kinJoint.png', command = 'JointTool', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'vertsCenter.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.getVertsCenter()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Create joint to the selected', width = 35, height = 35, imageOverlayLabel = '', image1 = 'siglJoint.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.siglJntUI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'js_splitSelJoint', width = 35, height = 35, imageOverlayLabel = '', image1 = 'splitJoint.bmp', command = 'source js_splitSelJointUI;\njs_splitSelJointUI;\n', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Add Halfway Joint', width = 35, height = 35, imageOverlayLabel = '', image1 = 'kinInsert.xpm', command = 'source js_addHalfJoint;\njs_addHalfJoint', sourceType = 'mel')
    cmds.shelfButton(annotation = 'orientJointOptionItem', width = 35, height = 35, imageOverlayLabel = 'ori', image1 = 'orientJoint.png', command = 'OrientJointOptions', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Comet joint orientation', width = 35, height = 35, imageOverlayLabel = 'cOri', image1 = 'orientJoint.png', command = 'source cometJointOrient; cometJointOrient;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Joint orientation with plane.', width = 35, height = 35, imageOverlayLabel = 'cpOri', image1 = 'orientJoint.png', command = 'import CoplanarJointOrient.CoplanarJointOrient\nCoplanarJointOrient.CoplanarJointOrient.main()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Change Rotate Order On Selected Objects', width = 35, height = 35, imageOverlayLabel = '', image1 = 'rotOrder.bmp', command = 'source js_rotationOrderWin;\njs_rotationOrderWin', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Mirror selected joints', width = 35, height = 35, imageOverlayLabel = '', image1 = 'mirrorJnt.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.mirJntUi()', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'cgmTdTools.png', command = 'import cgmToolbox\nreload(cgmToolbox)\ncgmToolbox.loadTDTools()', sourceType = 'python')
    cmds.shelfButton(annotation = 'b1 hair dynamic tool', width = 35, height = 35, imageOverlayLabel = '', image1 = 'hairChain.bmp', command = 'source IH_buildSpIkChain.mel;\nIH_buildSpIkChain();', sourceType = 'mel')
    cmds.shelfButton(annotation = "Additional functions for the 'IH_buildSpIkChain.mel' script.", width = 35, height = 35, imageOverlayLabel = '', image1 = 'forHairChain.png', command = 'import tak_addFuncForIHBuildSpIkChain\nreload(tak_addFuncForIHBuildSpIkChain)\ntak_addFuncForIHBuildSpIkChain.ui()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Build spline IK/FK for selected curves.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'splineIKFK.png', command = 'import tak_splineIKFK\nreload(tak_splineIKFK)\ntak_splineIKFK.SplineIKFK()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Build ribbon IK/FK.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'ribbonIKFK.png', command = 'import tak_ribbonIKFK\nreload(tak_ribbonIKFK)\ntak_ribbonIKFK.ribbonIKFK()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Add Geo to Selected Skeletons', width = 35, height = 35, imageOverlayLabel = '', image1 = 'addGeo.bmp', command = 'string $tmp[0];\nclear $tmp;\njs_createSkelGeo $tmp;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'js_createStretchSpline', width = 35, height = 35, imageOverlayLabel = '', image1 = 'scaleJoint.bmp', command = 'source js_createStretchSplineUI;\njs_createStretchSplineUI;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Stretchy Ik Creation', width = 35, height = 35, imageOverlayLabel = '', image1 = 'ikStretch.bmp', command = 'source js_createIkStretchUI;\njs_createIkStretchUI', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Create Twisty Segment', width = 35, height = 35, imageOverlayLabel = '', image1 = 'twistySeg.bmp', command = 'source js_createTwistySegmentUI;\njs_createTwistySegmentUI', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Duplicate selected geometry(s) and connect source outMesh to duplicated geometry inMesh.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'cntShpGeo.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.cntShpGeo()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Connect selected attributes from first selected object to second selected object.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'connectAttr.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.cnntAttrs()', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'mulConnectAttr.bmp', command = 'import tak_multiConnectAttr\nreload(tak_multiConnectAttr)\ntak_multiConnectAttr.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Constraint to multiple objects, first select driver then selcet other drivens', width = 35, height = 35, imageOverlayLabel = '', image1 = 'multiConstraint.bmp', command = 'import tak_mulConst\nreload(tak_mulConst)\ntak_mulConst.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Delete constraints on the selected object(s)', width = 35, height = 35, imageOverlayLabel = '', image1 = 'deleteConstraints.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.delCnst()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Set up space switching.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'tak_setupSpaceSwitching.png', command = 'import tak_setupSpaceSwitching\nreload(tak_setupSpaceSwitching)\ntak_setupSpaceSwitching.ui()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Make group', width = 35, height = 35, imageOverlayLabel = '', image1 = 'group.bmp', command = 'import tak_group\nreload(tak_group)\ntak_group.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Make reverse group', width = 35, height = 35, imageOverlayLabel = '', image1 = 'revGroup.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.revGrp()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Make locator group', width = 35, height = 35, imageOverlayLabel = '', image1 = 'locGrp.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.locGrp()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Create control curves', width = 35, height = 35, imageOverlayLabel = '', image1 = 'control.bmp', command = 'import tak_createCtrl\nreload(tak_createCtrl)\ntak_createCtrl.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Create control curves from polygon edges', width = 35, height = 35, imageOverlayLabel = '', image1 = 'ctrlFromEdges.png', command = 'import tak_ctrlFromEdges\nreload(tak_ctrlFromEdges)\ntak_ctrlFromEdges.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Mirror controls', width = 35, height = 35, imageOverlayLabel = '', image1 = 'mirSelCon.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.mirCtrlShapeUi()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Mirror control one to one.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'mirConOneToOne.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.mirConSel()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Mirror selected objects', width = 35, height = 35, imageOverlayLabel = '', image1 = 'mirrorObj.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.mirObjUi()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Connect facial control to locators with set driven key.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'connectFacialLocator.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.cntFacCtrlLocUI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Set driven key options', width = 35, height = 35, imageOverlayLabel = 'Set.', image1 = 'menuIconKeys.png', command = 'SetDrivenKeyOptions', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Copy or mirror set driven keyframes', width = 35, height = 35, imageOverlayLabel = '', image1 = 'tak_copySDK.bmp', command = 'import tak_copyMirrorSDK\nreload(tak_copyMirrorSDK)\ntak_copyMirrorSDK.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Soft Cluster EX', width = 35, height = 35, imageOverlayLabel = '', image1 = 'softClusterEXIcon.png', command = 'import SoftClusterEX\nSoftClusterEX.launch()', sourceType = 'python')
    cmds.shelfButton(annotation = 'cluster on edge loop', width = 35, height = 35, imageOverlayLabel = '', image1 = 'clusterOnEdgeLoop.bmp', command = 'source tak_ClusterOnEdgeLoop;\nClusterOnEdgeLoop;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Auto rigging function for simple props like sword, gun... etc.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'simplePropAutoRigging.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.simplePropAutoRigging()', sourceType = 'python')
    cmds.shelfButton(annotation = "def buildGlobalCtrl():\n\t'''\n\tBuild global control with selected ...", width = 35, height = 35, imageOverlayLabel = 'global', image1 = 'pythonFamily.png', command = "def buildGlobalCtrl():\n\t'''\n\tBuild global control with selected control curve.\n\t'''\n\t\n\tsrcCtrl = cmds.ls(sl = True)[0]\t\n\tglobalCtrls = ['global_A_ctrl', 'global_B_ctrl']\n\t\n\tfor globalCtrl in globalCtrls:\n\t\tcmds.duplicate(srcCtrl, n = globalCtrl)\n\t\tglobalCtrlZero = tak_misc.doGroup(globalCtrl, '_zero')\n\t\tpreCtrlIndex = globalCtrls.index(globalCtrl)-1\n\t\tif preCtrlIndex != -1:\n\t\t\tcmds.parent(globalCtrlZero, globalCtrls[preCtrlIndex])\n\nbuildGlobalCtrl()", sourceType = 'python')

    cmds.frameLayout('riggingDeformationFrameLo', label = 'Deformation', collapse = False, collapsable = True, p = 'riggingScrLo')
    cmds.shelfLayout('Rigging_Deformation', h = (40 * 3), p = 'riggingDeformationFrameLo')
    cmds.shelfButton(annotation = 'Select influence(s).', width = 35, height = 35, imageOverlayLabel = '', image1 = 'selectInfluences.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.selInflu()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Select all the child joints', width = 35, height = 35, imageOverlayLabel = '', image1 = 'selChldJnt.bmp', command = "### Select Joint in Hierarchy ###\njntList = cmds.ls(sl = True, dag = True, type = 'joint')\ncmds.select(jntList)", sourceType = 'python')
    cmds.shelfButton(annotation = 'Select bind joints for selected object and childs.', width = 35, height = 35, imageOverlayLabel = 'SelBndJnt', image1 = 'pythonFamily.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.selBndJnt()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Select surface(s) and a joint.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'smoothSkin.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.smoothSkinBind()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Detach Skin', width = 35, height = 35, imageOverlayLabel = '', image1 = 'detachSkin.png', command = 'DetachSkin', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Deformation Learning Solver', width = 35, height = 35, imageOverlayLabel = '', image1 = 'deltaMush.png', command = 'import DLS\nDLS.launch()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Set skin weights', width = 35, height = 35, imageOverlayLabel = '', image1 = 'skinWeight.png', command = 'import tak_skinWeights\nreload(tak_skinWeights)\ntak_skinWeights.SkinWeights()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Create range of motion for selected object.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'ROM.png', command = 'import tak_ROM\nreload(tak_ROM)\ntak_ROM.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Weight hammer: fix vertices that have bad weights (select them and use the hammer)', width = 35, height = 35, imageOverlayLabel = '', image1 = 'weightHammer.bmp', command = 'weightHammerVerts', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Weight Hammer on Edge Loop', width = 35, height = 35, imageOverlayLabel = '', image1 = 'weightHammerOnEdgeLoop.bmp', command = "### Weight Hammer on Edge Loop ###\ncmds.SelectEdgeLoopSp()\nmel.eval('weightHammerVerts;')", sourceType = 'python')
    cmds.shelfButton(annotation = 'Weight Hammer Brush', width = 35, height = 35, imageOverlayLabel = '', image1 = 'weightHammerBrush.bmp', command = "cmds.artSelectCtx(n = 'weightHammerBrush')\ncmds.setToolTo('weightHammerBrush')\ncmds.artSelectCtx('weightHammerBrush', edit=True, r=1.0, lr=0.01, ual = True, ads = False, bsc = 'select -cl', asc = 'weightHammerVerts')", sourceType = 'python')
    cmds.shelfButton(annotation = 'tf_smoothSkinWeight', width = 35, height = 35, imageOverlayLabel = '', image1 = 'tf_smoothSkin.bmp', command = 'import averageVertexSkinWeightBrush\nreload(averageVertexSkinWeightBrush)\naverageVertexSkinWeightBrush.paint()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Paint skin weights tool options', width = 35, height = 35, imageOverlayLabel = '', image1 = 'paintSkinWeights.png', command = 'ArtPaintSkinWeightsToolOptions', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Select either a single skin or the source and the destination skin.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'mirrorSkinWeight.png', command = 'MirrorSkinWeights', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Select the source surface and the destination surface or component.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'copySkinWeight.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.addInfCopySkin()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Copy skin to closet vertices of target mesh', width = 35, height = 35, imageOverlayLabel = 'SCV', image1 = 'pythonFamily.png', command = 'import tak_lib\n\nselLs = cmds.ls(sl = True)\nclosestVtxs = tak_lib.getClosestVtx()\ncmds.select(selLs[0], closestVtxs, r = True)\ntak_misc.addInfCopySkin()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Add influences. Select influences and geometry.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'addWrapInfluence.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.addInfUI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Remove Influence', width = 35, height = 35, imageOverlayLabel = '', image1 = 'removeWrapInfluence.png', command = 'RemoveInfluence', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Prune Small Weights', width = 35, height = 35, imageOverlayLabel = 'PSW', image1 = 'menuIconSkinning.png', command = 'PruneSmallWeights', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Select the skin and unused joints and influences will be disconnected to improve performance.', width = 35, height = 35, imageOverlayLabel = 'RUI', image1 = 'menuIconSkinning.png', command = 'removeUnusedInfluences;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Save skin weights for selected objects.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'bSkinSaver.png', command = 'import bSkinSaver\nreload(bSkinSaver)\nbSkinSaver.showUI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Save skin weights.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'abWeightLifter.bmp', command = 'source "D:/Tak/Program_Presets/tak_maya_preset/prefs/scripts/mel/abWeightLifter.mel";\nabWeightLifter;', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'LRTarget.bmp', command = 'import tak_LRTarget\nreload(tak_LRTarget)\ntak_LRTarget.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'tak_helperJoint.png', command = 'import tak_helperJoint\nreload(tak_helperJoint)\ntak_helperJoint.ui()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Corrective blend shape tools.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'correctiveBS.png', command = 'import tak_correctiveBS\nreload(tak_correctiveBS)\nposCorObj = tak_correctiveBS.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Shape Editor', width = 35, height = 35, imageOverlayLabel = '', image1 = 'vacantCell.png', command = 'ShapeEditor', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'editSkinGeo.bmp', command = 'import tak_editSkinGeo\nreload(tak_editSkinGeo)\neSkinGeoObj = tak_editSkinGeo.EditSkinGeo()\neSkinGeoObj.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'edgeLoopToVertex.bmp', command = '# Select Edge to Vertex Loop #\ncmds.SelectEdgeLoopSp()\ncmds.ConvertSelectionToVertices()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Select affected vertices by a selected influence', width = 35, height = 35, imageOverlayLabel = '', image1 = 'selAffectedVertex.png', command = 'import tak_misc\nreload(tak_misc)\ninf = cmds.ls(sl=True)[0]\ntak_misc.selAffectedVertex(inf)', sourceType = 'python')

    cmds.frameLayout('riggingExtraFrameLo', label = 'Extra Tools', collapse = False, collapsable = True, p = 'riggingScrLo')
    cmds.shelfLayout('Rigging_Extra_Tools', h = (40 * 2), p = 'riggingExtraFrameLo')
    cmds.shelfButton(annotation = 'makeFolding', width = 35, height = 35, imageOverlayLabel = 'Fold', image1 = 'commandButton.png', command = 'source makeFoldingRig.mel;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'set up auto swim', width = 35, height = 35, imageOverlayLabel = '', image1 = 'autoSwim.bmp', command = 'import tak_autoSwim\nreload(tak_autoSwim)\ntak_autoSwim.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'nCloth set up with skined geometry.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'nClothSetUp.png', command = 'import tak_nClothSetUp\nreload(tak_nClothSetUp)\ntak_nClothSetUp.nClothSetUp()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Allows interaction with objects during playback', width = 35, height = 35, imageOverlayLabel = '', image1 = 'interactivePlayback.png', command = 'InteractivePlayback', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Attach object to curve/surface/polygon', width = 35, height = 35, imageOverlayLabel = '', image1 = 'attachIt.png', command = 'import tak_attachIt\nreload(tak_attachIt)\ntak_attachIt.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Rivet', width = 35, height = 35, imageOverlayLabel = '', image1 = 'rivet.bmp', command = 'rivet;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'djRivet', width = 35, height = 35, imageOverlayLabel = '', image1 = 'djRivet.bmp', command = 'djRivet;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Build sticky lips.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'stickyLips.png', command = 'import tak_stickyLips\nreload(tak_stickyLips)\ntak_stickyLips.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Edit deformer membership.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'editDfmMember.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.editDfmMemberUI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Create locator to keep place for selected items.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'placeHolder.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.plcHldr()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Create curve with selected objects.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'crvFromSels.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.crvFromSelsUi()', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyEdgeToCurves.png', command = 'CreateCurveFromPoly', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Rebuild Curve Options', width = 35, height = 35, imageOverlayLabel = '', image1 = 'rebuildCurve.png', command = 'RebuildCurveOptions', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Key regular interval with selected.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'keyRegularInterval.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.keyRglrInterval()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Arrange in a row layout for selected objects.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'arrangeInARow.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.arrangeInARow()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Arrange in a column layout for selected objects.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'arrangeInAColumn.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.arrangeInAColumn()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Match transform.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'matchTransform.bmp', command = 'import tak_matchTransform\nreload(tak_matchTransform)\ntak_matchTransform.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Match rotate and scale pivot.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'matchPivot.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.matchPivot()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Manage attributes.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'attrManager.png', command = 'import tak_attrManager\nreload(tak_attrManager)\ntak_attrManager.ui()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Grep Rename', width = 35, height = 35, imageOverlayLabel = '', image1 = 'grep_rename.bmp', command = 'source js_grepRenameUI;\njs_grepRenameUI', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Duplicate selected objects with assign unique name.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'dupUniqName.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.dupRenameUI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Duplicate Special', width = 35, height = 35, imageOverlayLabel = 'DupS', image1 = 'menuIconEdit.png', command = 'duplicatePreset(1,1,2,0,0,0,1,0,0,0,0,0,0,0,1,1,1)', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Duplicate selected objects with original state and assign unique name.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'dupNoDefUniqName.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.dupNoDefUniqName()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Clean up rig to publish.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'cleanUpRig.png', command = 'import tak_cleanUpRig\nreload(tak_cleanUpRig)\ntak_cleanUpRig.ui()', sourceType = 'python')


    # animation tab
    cmds.scrollLayout('aniScrLo', childResizable = True, p = 'AnimationFormLo')
    cmds.formLayout('AnimationFormLo', e = True, attachForm = [('aniScrLo', 'top', 0), ('aniScrLo', 'bottom', 0), ('aniScrLo', 'left', 0), ('aniScrLo', 'right', 0)])
    cmds.frameLayout('aniCtrlSelFrameLo', label = 'Control Select', collapse = False, collapsable = True, p = 'aniScrLo')
    cmds.shelfLayout('Animation_Control_Select', h = 41, p = 'aniCtrlSelFrameLo')
    cmds.shelfButton(annotation = 'Save controls selected', width = 35, height = 35, imageOverlayLabel = '', image1 = 'pos2Shelf.bmp', command = 'pose2shelf', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Advanced skeleton selector window.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'AdvancedSkeleton/asBiped.png', command = 'source "AdvancedSkeleton/Selector/biped.mel";asSelectorbiped;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Selector:biped', width = 35, height = 35, imageOverlayLabel = 'AS5', image1 = 'C:/Users/stlee/Documents/maya/2015-x64/scripts/AdvancedSkeleton5/AdvancedSkeleton5Files/icons/asBiped.png', command = 'source "C:/Users/stlee/Documents/maya/2015-x64/scripts/AdvancedSkeleton5//AdvancedSkeleton5Files/Selector/biped.mel";asSelectorbiped;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Selector:face', width = 35, height = 35, imageOverlayLabel = 'AS5', image1 = 'C:/Users/stlee/Documents/maya/2015-x64/scripts/AdvancedSkeleton5/AdvancedSkeleton5Files/icons/asFace.png', command = 'source "C:/Users/stlee/Documents/maya/2015-x64/scripts/AdvancedSkeleton5//AdvancedSkeleton5Files/Selector/face.mel";asSelectorface;', sourceType = 'mel')

    cmds.frameLayout('aniDisplayFrameLo', label = 'Display', collapse = False, collapsable = True, p = 'aniScrLo')
    cmds.shelfLayout('Animation_Display', h = 41, p = 'aniDisplayFrameLo')
    cmds.shelfButton(annotation = 'Convert selected keyframe(s) into breakdown tick(s).', width = 35, height = 35, imageOverlayLabel = 'breakdown', image1 = 'breakdown.png', command = 'keyframe -tds on;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Convert selected keyframe(s) into key tick(s).', width = 35, height = 35, imageOverlayLabel = 'key', image1 = 'key.png', command = 'keyframe -tds off;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Create ouline.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'bhGhostIcon.png', command = 'source bhGhost.mel;\nbhGhost;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Create arc of selection.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'arcTracer.bmp', command = 'import ml_arcTracer\nml_arcTracer.ui()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Select object(s) to generate a motion trail over time.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'motionTrail.png', command = 'doMotionTrail 2 { "snapshot  -motionTrail 1  -increment 1 -startTime `playbackOptions -query -min` -endTime `playbackOptions -query -max`", "1","0","0","1","1","1"}', sourceType = 'mel')

    cmds.frameLayout('aniCrvFrameLo', label = 'Animation Curve', collapse = False, collapsable = True, p = 'aniScrLo')
    cmds.shelfLayout('Animation_Animation_Curve', h = 41, p = 'aniCrvFrameLo')
    cmds.shelfButton(annotation = 'Set default keyframe tangent to the step mode.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'steped.png', command = 'keyTangent -global -itt linear;\nkeyTangent -global -ott step;\n', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Set default keyframe tangent to the spline mode.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'spline.png', command = 'keyTangent -global -itt spline;\nkeyTangent -global -ott spline;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Set default keyframe tangent to the linear mode.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'linear.bmp', command = 'keyTangent -global -itt linear;\nkeyTangent -global -ott linear;\n', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Convert selected animation curve to the cycle mode.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'makeCycle.bmp', command = 'animCurveEditor -edit -displayInfinities true graphEditor1GraphEd;\nsetInfinity -pri cycle;\nsetInfinity -poi cycle;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Convert selected animation curve to the cycle with offset mode.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'cycleOffset.bmp', command = 'animCurveEditor -edit -displayInfinities true graphEditor1GraphEd;\nsetInfinity -pri cycleRelative;\nsetInfinity -poi cycleRelative;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Convert selected animation curve to the linear mode.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'makeLinear.bmp', command = 'animCurveEditor -edit -displayInfinities true graphEditor1GraphEd;\nsetInfinity -pri linear;\nsetInfinity -poi linear;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Convert selected animation curve to the constant mode.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'makeConstant.bmp', command = 'animCurveEditor -edit -displayInfinities false graphEditor1GraphEd;\nsetInfinity -poi constant;\nsetInfinity -pri constant;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Set easy in and easy out.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'easyEase.bmp', command = 'source easyEasyEase.mel;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Static Channels', width = 35, height = 35, imageOverlayLabel = 'SC', image1 = 'menuIconEdit.png', command = 'DeleteAllStaticChannels', sourceType = 'mel')

    cmds.frameLayout('aniPoseFrameLo', label = 'Pose', collapse = False, collapsable = True, p = 'aniScrLo')
    cmds.shelfLayout('Animation_Pose', h = 41, p = 'aniPoseFrameLo')
    cmds.shelfButton(annotation = 'save and load animation', width = 35, height = 35, imageOverlayLabel = '', image1 = 'studio_library.png', command = 'import studiolibrary\nstudiolibrary.main()', sourceType = 'python')
    cmds.shelfButton(annotation = 'tweenMachine', width = 35, height = 35, imageOverlayLabel = '', image1 = 'tweenMachine.xpm', command = 'source tweenMachine.mel;\ntweenMachine;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Mirror selected controls', width = 35, height = 35, imageOverlayLabel = '', image1 = 'mirrorCtrl.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.mirrorCtrlsUI()', sourceType = 'python')


    cmds.frameLayout('aniRefineShapeFrameLo', label = 'Refine Shape', collapse = False, collapsable = True, p = 'aniScrLo')
    cmds.shelfLayout('Animation_Refine_Shape', h = 41, p = 'aniRefineShapeFrameLo')
    cmds.shelfButton(annotation = 'Sculpt a geometry object.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'putty.png', command = 'SculptGeometryTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Sculpting brushes.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'SHAPESBrush.png', command = 'SHAPESBrushUI', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Correct problematic shape of rigged character.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'aniSculpt.bmp', command = 'import tak_aniSculpt\nreload(tak_aniSculpt)\naniSculptObj = tak_aniSculpt.AniSculpt()\naniSculptObj.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Correct problematic shape of animated geometry.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'correctShape.png', command = 'import tak_correctShape\nreload(tak_correctShape)\ntak_correctShape.UI()', sourceType = 'python')

    cmds.frameLayout('aniExtraFrameLo', label = 'Extra Tools', collapse = False, collapsable = True, p = 'aniScrLo')
    cmds.shelfLayout('Animation_Extra_Tools', h = 41, p = 'aniExtraFrameLo')
    cmds.shelfButton(annotation = 'Quicktime playblast with Pdplayer', width = 35, height = 35, imageOverlayLabel = '', image1 = 'playblastMov.png', command = 'source "D:/Tak/Program_Presets/tak_maya_preset/prefs/scripts/mel/makePlayblastMov.mel";\nmakePlayblastMov;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Delete keys and set default value', width = 35, height = 35, imageOverlayLabel = 'dflt', image1 = 'deleteKeys.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.delKeySetDflt()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Delete keys for selected controls', width = 35, height = 35, imageOverlayLabel = '', image1 = 'deleteKeys.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.delKey()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Delete constraints on the selected object(s)', width = 35, height = 35, imageOverlayLabel = '', image1 = 'deleteConstraints.bmp', command = 'DeleteConstraints', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Offset keyframe for selected object(s).', width = 35, height = 35, imageOverlayLabel = '', image1 = 'offsetKey.bmp', command = 'import tak_offsetKeyframe\nreload(tak_offsetKeyframe)\ntak_offsetKeyframe.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Random offset keyframe for selected object(s).', width = 35, height = 35, imageOverlayLabel = '', image1 = 'SMO_RandomOffsetKeysIcon.png', command = 'SMO_RandomOffsetKeys', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Create procedure oscillate animation.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'oscillateMaker.bmp', command = 'import tak_oscillateMaker\nreload(tak_oscillateMaker)\ntak_oscillateMaker.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'b1 nCloth tool', width = 35, height = 35, imageOverlayLabel = '', image1 = 'b1nCloth.bmp', command = 'source "N:/b1Env/maya/2014/scripts/b1Animation/D40clothTool.mel";', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Bake IH_HairChain tool.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'bakeHairChain.png', command = 'IH_BakeHairChain;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Interactive Playback', width = 35, height = 35, imageOverlayLabel = '', image1 = 'interactivePlayback.png', command = 'InteractivePlayback', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Clean up animation scene.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'tak_cleanUpAniScene.png', command = 'import tak_cleanUpAniScene\nreload(tak_cleanUpAniScene)\ntak_cleanUpAniScene.ui()', sourceType = 'python')


    # modeling tab
    cmds.scrollLayout('mdlScrLo', childResizable = True, p = 'ModelingFormLo')
    cmds.formLayout('ModelingFormLo', e = True, attachForm = [('mdlScrLo', 'top', 0), ('mdlScrLo', 'bottom', 0), ('mdlScrLo', 'left', 0), ('mdlScrLo', 'right', 0)])
    cmds.frameLayout('mdlDisplayFrameLo', label = 'Display', collapse = False, collapsable = True, p = 'mdlScrLo')
    cmds.shelfLayout('Modeling_Display', h = (41 * 1), p = 'mdlDisplayFrameLo')
    cmds.shelfButton(annotation = 'Vertex Normals', width = 35, height = 35, imageOverlayLabel = 'VN', image1 = 'menuIconDisplay.png', command = 'ToggleVertexNormalDisplay', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Face Normals', width = 35, height = 35, imageOverlayLabel = 'FN', image1 = 'menuIconDisplay.png', command = 'ToggleFaceNormalDisplay', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Normals Size...', width = 35, height = 35, imageOverlayLabel = 'NS', image1 = 'menuIconDisplay.png', command = 'ChangeNormalSize', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyNormal.png', command = 'ReversePolygonNormals', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polySoftEdge.png', command = 'SoftPolyEdgeElements 1', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyNormalUnlock.png', command = 'polyNormalPerVertex -ufn true', sourceType = 'mel')

    cmds.frameLayout('mdlSelFrameLo', label = 'Selection', collapse = False, collapsable = True, p = 'mdlScrLo')
    cmds.shelfLayout('Modeling_Selection', h = 41, p = 'mdlSelFrameLo')
    cmds.shelfButton(annotation = 'Convert selected components to vertex.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'edgeToVerts.png', command = 'PolySelectConvert 3;', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'selectSkipedEdgeRing.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.selEveryNUI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Selects all parallel edges that form an edge ring based on the current selection', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyConvertToEdgeRing.png', command = 'polySelectSp -ring;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Selects all connected edges that form an edge loop based on the current selection', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyConvertToEdgeLoop.png', command = 'polySelectSp -loop;', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polySelectUsingConstraints.png', command = 'PolygonSelectionConstraints', sourceType = 'mel')

    cmds.frameLayout('mdlEditCpntFrameLo', label = 'Edit Component', collapse = False, collapsable = True, p = 'mdlScrLo')
    cmds.shelfLayout('Modeling_Edit_Component', h = (38 * 3), p = 'mdlEditCpntFrameLo')
    cmds.shelfButton(annotation = 'Snap to X 0 for selected vertex(s).', width = 35, height = 35, imageOverlayLabel = '', image1 = 'zeroVtx.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.zeroVtx()', sourceType = 'python')
    cmds.shelfButton(annotation = "Snap selected vertices to the target geometry's closest border vertex.", width = 35, height = 35, imageOverlayLabel = '', image1 = 'snapToClosestBorderVtx.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.snapToBrdrVtx()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Delete the selected Vertices / Edges.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyDelEdgeVertex.png', command = 'DeletePolyElements;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Collapse the selected edges or faces.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyCollapseEdge.png', command = 'performPolyCollapse 0;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Merge vertices / border edges based on selection.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyMerge.png', command = 'polyMergeVertex  -d 0.001 -am 1 -ch 1;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Interactively select and merge vertices', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyMergeVertex.png', command = 'MergeVertexTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Extrude the selected component', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyExtrudeFacet.png', command = 'performPolyExtrude 0', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Fill Hole', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyCloseBorder.png', command = 'FillHole', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Append to Polygon Tool', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyAppendFacet.png', command = 'setToolTo polyAppendFacetContext ; polyAppendFacetCtx -e -pc `optionVar -q polyKeepFacetsPlanar` polyAppendFacetContext', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Create a bridge between two sets of edges or faces', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyBridge.png', command = 'polyBridgeEdge -ch 1 -divisions 0 -twist 0 -taper 1 -curveType 0 -smoothingAngle 30;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Merge selected edge(s)', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polySewEdge.png', command = 'cmds.polySewEdge(tolerance = 1)', sourceType = 'python')
    cmds.shelfButton(annotation = 'Detach selected edge(s).', width = 35, height = 35, imageOverlayLabel = '', image1 = 'detachEdges.png', command = 'cmds.DetachEdgeComponent()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Multi-Cut Tool', width = 35, height = 35, imageOverlayLabel = '', image1 = 'multiCut_NEX32.png', command = 'dR_multiCutTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Connect Tool', width = 35, height = 35, imageOverlayLabel = '', image1 = 'connect_NEX32.png', command = 'dR_connectTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Split selected edge ring.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polySplitEdgeRing.png', command = 'SplitEdgeRingTool;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Offset Edge Loop Tool', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyDuplicateEdgeLoop.png', command = 'performPolyDuplicateEdge 0', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Convert to edge loop and set edge flow.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'edgeFlow.bmp', command = 'cmds.SelectEdgeLoopSp()\ncmds.polyEditEdgeFlow()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Slide edge loops or paths along their neighbouring edges', width = 35, height = 35, imageOverlayLabel = '', image1 = 'slideEdgeTool.png', command = 'SlideEdgeTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Create a bevel along the selected edges', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyBevel.png', command = 'polyPerformAction "polyBevel -offset 0.5 -offsetAsFraction 1 -autoFit 1 -segments 1 -worldSpace 1 -uvAssignment 1 -fillNgons 1 -mergeVertices 1 -mergeVertexTolerance 0.0001 -smoothingAngle 30 -miteringAngle 180 -angleTolerance 180" e 0', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Chamfer the selected vertices', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyChamfer.png', command = 'polyChamferVtx 1 0.25 0;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Extract the currently selected faces from their shell and shows a manipulator to adjust their offset', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyChipOff.png', command = 'performPolyChipOff 0 0', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Duplicate the currently selected faces in a new shell and shows a manipulator to adjust their offset', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyDuplicateFacet.png', command = 'performPolyChipOff 0 1', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Crease Set Editor...', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyCrease.png', command = 'python "from maya.app.general import creaseSetEditor; creaseSetEditor.showCreaseSetEditor()"', sourceType = 'mel')

    cmds.frameLayout('mdlEditGeoFrameLo', label = 'Edit Mesh', collapse = False, collapsable = True, p = 'mdlScrLo')
    cmds.shelfLayout('Modeling_Edit_Mesh', h = (38 * 3), p = 'mdlEditGeoFrameLo')
    cmds.shelfButton(annotation = 'Clean up mesh before reduce resolution.', width = 35, height = 35, imageOverlayLabel = 'cleanUp', image1 = 'pythonFamily.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.clMeshBeforeReduce()', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'reverseSmooth.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.reverseSmoothUI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Reduce edge loop resolution.', width = 35, height = 35, imageOverlayLabel = 'rdLoop', image1 = 'commandButton.png', command = '{\n\tstring $selEdges[] = `ls -sl`;\n\tstring $buffer[];\n\ttokenize $selEdges[0] "." $buffer;\n\n\tpolySelectEdgesEveryN "edgeRing" 2;\n\tpolySelectSp -loop;\n\tpolySelectSp -loop;\n\tDeletePolyElements;\n\tdelete -ch $buffer[0];\n}', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Reduce edge ring resolution.', width = 35, height = 35, imageOverlayLabel = 'rdRing', image1 = 'commandButton.png', command = '{\n\tstring $selEdges[] = `ls -sl`;\n\tstring $buffer[];\n\ttokenize $selEdges[0] "." $buffer;\n\n\tpolySelectEdgesEveryN "edgeLoop" 2;\n\tpolySelectSp -ring;\n\tpolySelectSp -ring;\n\tperformPolyCollapse 0;\n\tdelete -ch $buffer[0];\n}', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'reduceMesh.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.reduceMesh()', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'delSupportEdges.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.delSupportEdgesUI()', sourceType = 'python')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyReduce.png', command = 'ReducePolygon;', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'edgeRingCollapse.bmp', command = 'polyConvertToRingAndCollapse;', sourceType = 'mel')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = '', image1 = 'deleteEdgeLoop.bmp', command = 'cmds.SelectEdgeLoopSp()\ncmds.SelectEdgeLoopSp()\ncmds.DeleteEdge()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Quad Draw Tool', width = 35, height = 35, imageOverlayLabel = '', image1 = 'quadDraw_NEX32.png', command = 'dR_quadDrawTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Sculpting brushes.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'SHAPESBrush.png', command = 'SHAPESBrushUI', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Sculpt a geometry object.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'putty.png', command = 'SculptGeometryTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Create symmetry mesh on x axis.', width = 35, height = 35, imageOverlayLabel = 'symX', image1 = 'pythonFamily.png', command = "import tak_misc\nreload(tak_misc)\ntak_misc.symmetry('x')", sourceType = 'python')
    cmds.shelfButton(annotation = 'Create symmetry mesh on z axis.', width = 35, height = 35, imageOverlayLabel = 'symZ', image1 = 'pythonFamily.png', command = "import tak_misc\nreload(tak_misc)\ntak_misc.symmetry('z')", sourceType = 'python')
    cmds.shelfButton(annotation = 'Mirror selected object.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'mirrorObj.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.mirObjUi()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Mirror geometry across an axis', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyMirrorGeometry.png', command = 'polyMirrorFace -ws 1  -direction 1 -mergeMode 1 -ch 1 -p 0 0 0 -mt 0.001;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Select edge loops.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'separateGeo.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.sepGeoWithEdge()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Select faces.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'sepGeo.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.sepGeoWithFace()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Combine and merge vertex.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'cbMrgGeo.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.cbMrgGeo()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Combine and rename with parent.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'combineRenameWithParent.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.combineAndRenameWithParentName()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Combine and assign random color.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'combineAndRandomColMat.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.combineAndAssignRandomMat()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Separate the selected polygon object shells or the shells of any selected faces from the object into distinct objects', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polySeparate.png', command = 'SeparatePolygon', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Combine the selected polygon objects into one single object to allow operations such as merges or face trims', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyUnite.png', command = 'polyPerformAction polyUnite o 0', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Add polygons to the selected polygon objects to smooth them', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polySmooth.png', command = 'polyPerformAction "polySmooth  -mth 0 -dv 1 -peh 0 -bnr 1 -c 1 -kb 1 -ksb 1 -khe 0 -kt 1 -kmb 1 -suv 1 -sl 1 -dpe 1 -ps 0.1 -ro 1" f 0', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Instance to Object', width = 35, height = 35, imageOverlayLabel = '', image1 = 'instanceToObject.png', command = 'ConvertInstanceToObject', sourceType = 'mel')

    cmds.frameLayout('mdlMatFrameLo', label = 'Material', collapse = False, collapsable = True, p = 'mdlScrLo')
    cmds.shelfLayout('Modeling_Material', h = 41, p = 'mdlMatFrameLo')
    cmds.shelfButton(annotation = 'Assign the material of first selection to the others', width = 35, height = 35, imageOverlayLabel = '', image1 = 'copyMat.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.copyMat()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Assign random color lamber.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'ranColLam.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.ranColLam()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Assign solid color material with grabed color.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'solColorMat.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.solidColMat()', sourceType = 'python')

    cmds.frameLayout('mdlAppFrameLo', label = 'Extra Tools', collapse = False, collapsable = True, p = 'mdlScrLo')
    cmds.shelfLayout('Modeling_Extra_Tools', h = (38 * 3), p = 'mdlAppFrameLo')
    cmds.shelfButton(annotation = 'Export selected object to ZBrush.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'GoZBrush.xpm', command = 'source GoZBrushFromMaya', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Run topogun.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'topogun.bmp', command = "import subprocess\nsubprocess.Popen('C:\\Program Files\\TopoGun 2 W64\\TopoGun64.exe')", sourceType = 'python')
    cmds.shelfButton(annotation = 'UVLayout', width = 35, height = 35, imageOverlayLabel = '', image1 = 'uvlayout-info.xpm', command = 'uvlayout_open;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Run phothoshop.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'photoshop.bmp', command = "import subprocess\nsubprocess.Popen('C:\\Program Files\\Adobe\\Adobe Photoshop CS6 (64 Bit)\\Photoshop.exe')", sourceType = 'python')
    cmds.shelfButton(annotation = 'Duplicate object along the path', width = 35, height = 35, imageOverlayLabel = '', image1 = 'DupAlongPathToolbox.png', command = 'source DupAlongPathToolbox.mel;DupAlongPathToolbox;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Instance Along Curve', width = 35, height = 35, imageOverlayLabel = 'IAC', image1 = 'menuIconEdit.png', command = 'instanceAlongCurve', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Run spPaint3d.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'spPaint3d.bmp', command = 'spPaint3d', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Create a curve on the grid or live surface specifying control vertices', width = 35, height = 35, imageOverlayLabel = '', image1 = 'curveCV.png', command = 'CVCurveTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Create a curve on the grid or live surface specifying edit points', width = 35, height = 35, imageOverlayLabel = '', image1 = 'curveEP.png', command = 'EPCurveTool', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Rebuild curve options', width = 35, height = 35, imageOverlayLabel = '', image1 = 'rebuildCurve.png', command = 'RebuildCurveOptions', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Polygon Edges to Curve', width = 35, height = 35, imageOverlayLabel = '', image1 = 'polyEdgeToCurves.png', command = 'CreateCurveFromPoly', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Convert nurbs curves to polygon geomtry', width = 35, height = 35, imageOverlayLabel = '', image1 = 'curveToPoly.png', command = 'import tak_curveToPoly\nreload(tak_curveToPoly)\ntak_curveToPoly.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Convert selected curves to polygon stripe.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'crvToStripe.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.crvToPolyStrp()', sourceType = 'python')
    cmds.shelfButton(annotation = 'This script will attempt to Spherify the current selected objects or components.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'spherizeSelection.png', command = 'import spherize\nspherize.sphereizedSelection()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Align into circlular shape for selected edge loop.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'alignCircle.bmp', command = 'source _sort_circle_tool.mel;\n_sort_circle_tool;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Select cut mesh and the mesh want to be craked.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'yd_crackut.bmp', command = 'source yd_crackut.mel;\nyd_crackut;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Crak with slice plane.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'crackMe.bmp', command = 'source crackMe175.mel;\ncrackMe;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Crack uniformly.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'AxCrack.bmp', command = 'source AxCrack.mel;\nAxCrack;', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Flatten geometry into uv space.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'mopKnit.png', command = 'mopKnitOptions', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Loft', width = 35, height = 35, imageOverlayLabel = '', image1 = 'skin.png', command = 'doPerformLoft("1", {"1","1","1","0","3","1","0","1"} )', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Creating hair guide curves from polygon tube.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'hairTools.png', command = 'import hairTools\nreload(hairTools)\nhairTools.hairballUI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Create water drop.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'waterDropGenerator_shelfIcon.png', command = 'import waterDropUI\nreload(waterDropUI)', sourceType = 'python')
    cmds.shelfButton(annotation = 'icPolyScatter;', width = 35, height = 35, imageOverlayLabel = '', image1 = 'icPolyScatter.png', command = 'icPolyScatter;', sourceType = 'mel')


    # misc tab
    cmds.scrollLayout('miscScrLo', childResizable = True, p = 'MiscFormLo')
    cmds.formLayout('MiscFormLo', e = True, attachForm = [('miscScrLo', 'top', 0), ('miscScrLo', 'bottom', 0), ('miscScrLo', 'left', 0), ('miscScrLo', 'right', 0)])
    cmds.frameLayout('miscFrameLo', label = 'Misc', collapsable = True, p = 'miscScrLo')
    cmds.shelfLayout('Misc_Misc', h = (41 * 2), p = 'miscFrameLo')
    cmds.shelfButton(annotation = 'Create folder structure.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'prjFldSet.bmp', command = 'import tak_prjFolderSetup\nreload(tak_prjFolderSetup)\ntak_prjFolderSetup.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Load or reload or delete references.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'fileRef.png', command = 'import tak_fileRef\nreload(tak_fileRef)\ntak_fileRef.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Assign shader to alembic cache with original asset. Select all geometries and run.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'Autoalembicshaderassigntool.bmp', command = 'import alembic_mtl\namtl = alembic_mtl.AssignMtlCtl()\namtl.selectAllCtl()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Rename refrence node and namespace.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'renameRefNode.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.renameRefNode()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Control display of assets in current scene.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'assetDisplay.bmp', command = 'import tak_assetDisplay_release\nreload(tak_assetDisplay_release)\ntak_assetDisplay_release.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Change line width.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'lineWidth.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.lineWidth()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Bake selected camera', width = 35, height = 35, imageOverlayLabel = '', image1 = 'bakeCam.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.bakeCam()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Bake selected camera to use in AE.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'mayaCamToAE.png', command = 'import tak_mayaCamToAE\nreload(tak_mayaCamToAE)\ntak_mayaCamToAE.ui()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Export selected camera for using in 3ds Max.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'mayaCamToMax.png', command = 'import tak_mayaCamToMax\nreload(tak_mayaCamToMax)\ntak_mayaCamToMax.mayaCamToMax()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Create camera following selected object.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'followingCam.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.followingCam()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Create locators per frame with selected object.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'trackingLoc.bmp', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.trackingLoc()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Render viewport.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'ikasRenderView.bmp', command = 'source ikas_renderViewBr', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Attach specular sphere to selected vertex(s) or selected two edges.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'specSphere.png', command = 'import tak_misc\nreload(tak_misc)\ntak_misc.attachSpecSphere()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Batch playblast.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'batchPB.png', command = 'import tak_batchPB\nreload(tak_batchPB)\ntak_batchPB.batchPB()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Switch texture for referenced model or selected objects.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'texSwitcher.png', command = 'import tak_texSwitcher\nreload(tak_texSwitcher)\ntak_texSwitcher.MainUI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Save specific scene information as a file.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'saveSceneInfo.png', command = 'import tak_saveSceneInfo\nreload(tak_saveSceneInfo)\ntak_saveSceneInfo.ui()', sourceType = 'python')
    cmds.shelfButton(annotation = 'ToyCop_HUD', width = 35, height = 35, imageOverlayLabel = '', image1 = 'ToyCop_HUD.png', command = 'source "n:/b1Env/maya/2014/scripts/b1Animation/ToyCop_HUD.mel";', sourceType = 'mel')
    cmds.shelfButton(annotation = 'Save and load render layer set up.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'saveRenderLayer.png', command = 'import tak_saveRenderLayer\nreload(tak_saveRenderLayer)\nrenLyrSaveObj = tak_saveRenderLayer.SaveRenderLayer()\nrenLyrSaveObj.UI()', sourceType = 'python')
    cmds.shelfButton(annotation = 'Edit maya ascii file contents.', width = 35, height = 35, imageOverlayLabel = '', image1 = 'editMayaAscii.png', command = 'import tak_editMayaAsciiFile\nreload(tak_editMayaAsciiFile)\ntak_editMayaAsciiFile.ui()', sourceType = 'python')
    cmds.shelfButton(annotation = 'import rjBakeInstancer\nrjBakeInstancer.show()', width = 35, height = 35, imageOverlayLabel = '', image1 = 'rjBakeInstancer.png', command = 'import rjBakeInstancer\nrjBakeInstancer.show()', sourceType = 'python')

    cmds.frameLayout('tempFrameLo', label = 'Temp', collapsable = True, p = 'miscScrLo')
    cmds.shelfLayout('Misc_Temp', h = (41 * 2), p = 'tempFrameLo')
    cmds.shelfButton(annotation = 'Unlock and Display All Attribute', width = 35, height = 35, imageOverlayLabel = 'unlockAttr', image1 = 'pythonFamily.png', command = '# Unlock and Display All Attribute #\nmel.eval(\'source channelBoxCommand;\')\n\nattrList = [\'translate\', \'rotate\', \'scale\']\naxisList = [\'X\', \'Y\', \'Z\']\nselList = cmds.ls(sl = True)\nfor sel in selList:\n\tfor attr in attrList:\n\t\tfor axis in axisList:\n\t\t\tcmds.setAttr(\'%s.%s%s\' %(sel, attr, axis), keyable = True)\n\t\t\tmel.eval(\'CBunlockAttr "%s.%s%s";\' %(sel, attr, axis))\n\tcmds.setAttr(\'%s.visibility\' %sel, keyable = True)\n\tmel.eval(\'CBunlockAttr "%s.visibility";\' %sel)\n', sourceType = 'python')
    cmds.shelfButton(annotation = 'Turn off ingerit transform.', width = 35, height = 35, imageOverlayLabel = 'offTrsf', image1 = 'pythonFamily.png', command = "# Turn Off Inherit Transform #\nselTrsf = cmds.ls(sl = True, type = 'transform')\n\nfor trsf in selTrsf:\n\tcmds.setAttr('%s.inheritsTransform' %trsf, False)", sourceType = 'python')
    cmds.shelfButton(annotation = 'Turn on inherit transform.', width = 35, height = 35, imageOverlayLabel = 'onTrsf', image1 = 'pythonFamily.png', command = "# On/Off Inherit Transform #\nselTrsf = cmds.ls(sl = True, type = 'transform')\n\nfor trsf in selTrsf:\n\tcmds.setAttr('%s.inheritsTransform' %trsf, True)", sourceType = 'python')
    cmds.shelfButton(annotation = 'Parent constraint geometries matching with advanced skeleton bind joints.', width = 35, height = 35, imageOverlayLabel = 'cL01Geo', image1 = 'pythonFamily.png', command = "asBndJnts = cmds.ls(sl = True)\n\nfor bndJnt in asBndJnts:\n\tif cmds.objExists('lod01_' + bndJnt):\n\t\tcmds.parentConstraint(bndJnt, 'lod01_' + bndJnt, mo = True)\n\telse:\n\t\tpass", sourceType = 'python')
    cmds.shelfButton(annotation = 'Create Lod01 facial list with facial_grp.', width = 35, height = 35, imageOverlayLabel = 'l01FLs', image1 = 'pythonFamily.png', command = "lod01FacialNeedList = ['eyebrow_angry', 'eyebrow_sad',\n'eyelid_blink',\n'lip_smile', 'lip_frown']\n\nfacialSrcGrp = cmds.ls(sl = True)\n\nfor item in lod01FacialNeedList:\n\tcmds.duplicate(facialSrcGrp, n = item, renameChildren = True)", sourceType = 'python')
    cmds.shelfButton(annotation = 'Connect Facial Control Attributes to the "facial_bs".', width = 35, height = 35, imageOverlayLabel = 'cL01F', image1 = 'pythonFamily.png', command = "import re\n\nfacialCtrlLs = cmds.ls(sl = True)\nfacialBsName = 'facial_bs'\n\nfor facialCtrl in facialCtrlLs:\n\tfacialAttrLs = cmds.listAttr(facialCtrl, keyable = True)\n\tfor facialAttr in facialAttrLs:\n\t\tfacialBsTrgName = re.sub(r'ctrl', facialAttr, facialCtrl)\n\t\tif cmds.objExists(facialBsName + '.' + facialBsTrgName):\n\t\t\tcmds.connectAttr(facialCtrl + '.' + facialAttr, facialBsName + '.' + facialBsTrgName, f = True)\n\t\telse:\n\t\t\tcmds.setAttr(facialCtrl + '.' + facialAttr, lock = True)\n\tif 'lip' in facialCtrl:\n\t\tcmds.connectAttr('lip_ctrl.lf_frown', facialBsName + '.lf_lip_frown', f = True)\n\t\tcmds.setAttr('lip_ctrl.lf_frown', lock = False)\n\t\tcmds.connectAttr('lip_ctrl.rt_frown', facialBsName + '.rt_lip_frown', f = True)\n\t\tcmds.setAttr('lip_ctrl.rt_frown', lock = False)\n\t\tcmds.connectAttr('lip_ctrl.lf_smile', facialBsName + '.lf_lip_smile', f = True)\n\t\tcmds.setAttr('lip_ctrl.lf_smile', lock = False)\n\t\tcmds.connectAttr('lip_ctrl.rt_smile', facialBsName + '.rt_lip_smile', f = True)\n\t\tcmds.setAttr('lip_ctrl.rt_smile', lock = False)\n\ncmds.connectAttr('Sub.facialControlVis', 'facial_gui_grp.visibility')\ncmds.parentConstraint('Root_M', 'facial_gui_grp', mo = True)", sourceType = 'python')
    cmds.shelfButton(annotation = '# Match Pivot and Consraint #\nselLs = cmds.ls(sl = True)\ndriver ...', width = 35, height = 35, imageOverlayLabel = 'MPCnst', image1 = 'pythonFamily.png', command = '# Match Pivot and Consraint #\nselLs = cmds.ls(sl = True)\ndriver = selLs[0]\ndriven = selLs[1]\n\n# Match rotate pivot\ndrvrRpPos = cmds.xform(driver, q = True, rp = True, ws = True)\ncmds.xform(driven, rp = drvrRpPos, ws = True)\n\n# Match scale pivot\ndrvrRpPos = cmds.xform(driver, q = True, sp = True, ws = True)\ncmds.xform(driven, sp = drvrRpPos, ws = True)\n\n# Parent constraint\ncmds.parentConstraint(driver, driven, mo = True)', sourceType = 'python')


    # Outliner
    cmds.frameLayout('olFrameLo', labelVisible = False, p = 'mainPaneLo')
    panel = cmds.outlinerPanel()
    outliner = cmds.outlinerPanel(panel, query=True, outlinerEditor=True)
    cmds.outlinerEditor( outliner, edit=True, mainListConnection='worldList', selectionConnection='modelList', showShapes=False, showReferenceNodes=False, showReferenceMembers=False, showAttributes=False, showConnected=False, showAnimCurvesOnly=False, autoExpand=False, showDagOnly=True, ignoreDagHierarchy=False, expandConnections=False, showCompounds=True, showNumericAttrsOnly=False, highlightActive=True, autoSelectNewObjects=False, doNotSelectNewObjects=False, transmitFilters=False, showSetMembers=True, setFilter='defaultSetFilter', ignoreHiddenAttribute=False )

    # Make dockable depend on maya version
    if int(MAYA_VER) <= 2016:
        if cmds.dockControl("tTDock", q = True, exists = True): 
            cmds.deleteUI("tTDock")

        allowedAreas = ['right', 'left']
        cmds.dockControl('tTDock', label = "Tak Tools", area='left', content = 'takToolWin', allowedArea = allowedAreas)

    else:
        workspaceCtrl()


def workspaceCtrl():
    if cmds.workspaceControl('takToolWorkspace', q=True, exists=True):
        cmds.deleteUI('takToolWorkspace')
    cmds.workspaceControl('takToolWorkspace', label='Tak Tools')
    
    workspacePtr = omui.MQtUtil_findControl('takToolWorkspace')
    workspaceWidget = wrapInstance(long(workspacePtr), QtWidgets.QWidget)

    takToolPtr = omui.MQtUtil_findWindow('takToolWin')
    takToolWidget = wrapInstance(long(takToolPtr), QtWidgets.QWidget)

    workspaceWidget.layout().addWidget(takToolWidget)


# Functions Related to Main Menu #
SHELF_LIST = ['Common',
'Rigging_Display', 'Rigging_Edit_Model', 'Rigging_Build', 'Rigging_Deformation', 'Rigging_Extra_Tools',
'Animation_Control_Select', 'Animation_Display', 'Animation_Animation_Curve', 'Animation_Pose', 'Animation_Refine_Shape', 'Animation_Extra_Tools',
'Modeling_Display', 'Modeling_Selection', 'Modeling_Edit_Component', 'Modeling_Edit_Mesh', 'Modeling_Material', 'Modeling_Extra_Tools',
'Misc_Misc', 'Misc_Temp']


def saveTools(*args):
    """
    Save tak_tools with current state.
    """

    # Read tool file
    fR = open(TAK_TOOL_PATH, 'r')
    contents = fR.read()
    fR.close()

    # Get shelf buttons for each shelfLayout
    for shelf in SHELF_LIST:
        btns = getBtns(shelf)

        curBtnCodes = ''

        # Get shelf button code for each shelf button
        for btn in btns:
            shelfBtnCode = getBtnInfo(btn)
            curBtnCodes += shelfBtnCode + '\n'

        # Find code block that related with specific shelf in contents
        codeBlock = re.search(r'.*%s.*\n((\s+cmds.shelfButton.*\n){0,100})' %shelf, contents).group(1)

        # Replace prior button codes to current shelf button codes in contents
        contents = contents.replace(codeBlock, curBtnCodes)

    # Save tool file
    fW = open(TAK_TOOL_PATH, 'w')
    fW.write(contents)
    fW.close()


def getBtns(layout):
    '''
    Query buttons in specific shelf.
    '''
    btns = cmds.shelfLayout(layout, q = True, childArray = True)

    return btns


def getBtnInfo(btn):
    '''
    Get button's source code.
    '''
    ano = cmds.shelfButton(btn, q = True, annotation = True)
    imgLlb = cmds.shelfButton(btn, q = True, imageOverlayLabel = True)
    img1 = cmds.shelfButton(btn, q = True, image1 = True)
    cmd = cmds.shelfButton(btn, q = True, command = True)
    srcType = cmds.shelfButton(btn, q = True, sourceType = True)

    shelfBtnCode = "    cmds.shelfButton(annotation = %s, width = 35, height = 35, imageOverlayLabel = '%s', image1 = '%s', command = %s, sourceType = '%s')" %(repr(str(ano)), imgLlb, img1,  repr(str(cmd)), srcType)

    return shelfBtnCode


def addToolUi(*args):
    '''
    UI for add a new tool to the specific shelf.
    '''

    winName = 'addToolWin'

    # Check if window exists
    if cmds.window(winName, exists = True):
        cmds.deleteUI(winName)

    # Create window
    cmds.window(winName, title = 'Add Tool')

    # Widgets

    cmds.tabLayout(tv = False)

    cmds.columnLayout('mainColLo', adj = True)

    cmds.optionMenu('shlfOptMenu', label = 'Shelf: ')
    for shelf in SHELF_LIST:
        cmds.menuItem(label = shelf, p = 'shlfOptMenu')
    cmds.textFieldGrp('annoTxtFldGrp', columnWidth = [(1, 110), (2, 100)], label = 'Annotation: ')
    cmds.textFieldButtonGrp('imgTxtFldBtnGrp', columnWidth = [(1, 110), (2, 100)], label = 'Image: ', buttonLabel = '...', bc = partial(loadImgPath, 'imgTxtFldBtnGrp'))
    cmds.textFieldGrp('imgOverLblTxtFldGrp', columnWidth = [(1, 110), (2, 100)], label = 'Image Overlay Label: ')
    cmds.textFieldGrp('cmdTxtFldGrp', columnWidth = [(1, 110), (2, 100)], label = 'Command: ')
    cmds.optionMenu('srcTypeOptMenu', label = 'Source Type: ')
    cmds.menuItem(label = 'python', p = 'srcTypeOptMenu')
    cmds.menuItem(label = 'mel', p = 'srcTypeOptMenu')

    cmds.separator(h = 5, style = 'none')

    cmds.button(label = 'Apply', h = 50, c = addTool)

    # Show window
    cmds.window(winName, e = True, w = 100, h = 100)
    cmds.showWindow(winName)


def addTool(*args):
    '''
    Add tool with options.
    '''

    # Get options
    shlf = cmds.optionMenu('shlfOptMenu', q = True, value = True)
    anno = cmds.textFieldGrp('annoTxtFldGrp', q = True, text = True)
    img = cmds.textFieldButtonGrp('imgTxtFldBtnGrp', q = True, text = True)
    imgOverLbl = cmds.textFieldGrp('imgOverLblTxtFldGrp', q = True, text = True)
    cmd = cmds.textFieldGrp('cmdTxtFldGrp', q = True, text = True)
    srcType = cmds.optionMenu('srcTypeOptMenu', q = True, value = True)

    # Set default image when user do not define image
    if not img:
        if srcType == 'mel':
            img = 'commandButton.png'
        elif srcType == 'python':
            img = 'pythonFamily.png'

    # Evaluate command string
    eval("cmds.shelfButton(annotation = %s, width = 35, height = 35, imageOverlayLabel = '%s', image1 = '%s', command = %s, sourceType = '%s', p = '%s')" %(repr(str(anno)), imgOverLbl, img,  repr(str(cmd)), srcType, shlf))

    # Close popup window
    cmds.deleteUI('addToolWin')


def loadImgPath(widgetName, *args):
    iconImgPath = cmds.fileDialog2(fileMode = 1, caption = 'Select a Image', startingDirectory = ICON_DIR_PATH)
    if iconImgPath:
        iconName = os.path.basename(iconImgPath[0])
        cmds.textFieldButtonGrp(widgetName, e = True, text = iconName)
