'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date: 12/22/2015

Description:
Custom shelf tool to organize shelf buttons more efficiently.

Usage:
import tak_tools_lite
reload(tak_tools_lite)
tak_tools_lite.UI()
'''

# import modules
import maya.cmds as cmds
import maya.mel as mel
import re
from functools import partial
import os

toolFilePath = 'D:/Tak/Program_Presets/tak_maya_preset/prefs/scripts/python/tak_tools_lite.py'
iconsFolder = 'D:/Tak/Program_Presets/tak_maya_preset/prefs/icons'

# track selection order on
cmds.selectPref(tso = True)

# Script job for reload tak_tools_lite when new scene opened
cmds.scriptJob(runOnce = True, event = ['NewSceneOpened', 'import tak_tools_lite\nreload(tak_tools_lite)\ntak_tools_lite.UI()'])

def UI():
    # check the dock existing
    if cmds.dockControl("tTDock", q = True, exists = True): cmds.deleteUI("tTDock")  

    # create window
    if cmds.window('takToolWin', exists = True):
        cmds.deleteUI('takToolWin')
    cmds.window('takToolWin', title = 'Tak Tools', menuBar = True, mnb = False, mxb = False)

    # Menu
    cmds.menu('fileMenu', label = 'File', p = 'takToolWin')
    cmds.menuItem(label = 'Save Tools', c = saveTools, p = 'fileMenu')

    cmds.menu('editMenu', label = 'Edit', p = 'takToolWin')
    cmds.menuItem(label = 'Add Tool', c = addToolUi, p = 'editMenu')

    cmds.paneLayout('mainPaneLo', configuration = 'horizontal2', paneSize = [(2, 63, 37)])

    cmds.formLayout('mainFormLo', p = 'mainPaneLo')

    # Common Tools section Start
    cmds.tabLayout('cmnToolTabLo', tv = False, p = 'mainFormLo')
    cmds.shelfLayout('Common', h = (36.5 * 4), parent = 'cmnToolTabLo')
    cmds.shelfButton(annotation = 'History', width = 35, height = 35, imageOverlayLabel = 'Hist', image1 = 'menuIconEdit.png', command = 'DeleteHistory', sourceType = 'mel')

    # Common Tools Section End

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
    # Rigging_Display Shelf Start
    cmds.shelfLayout('Rigging_Display', h = (41 * 1), p = 'riggingDisplayFrameLo')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = 'Hist', image1 = 'menuIconEdit.png', command = 'DeleteHistory', sourceType = 'mel')

    # Rigging_Display Shelf End

    cmds.frameLayout('riggingEditMdlFrameLo', label = 'Edit Model', collapse = False, collapsable = True, p = 'riggingScrLo')
    cmds.shelfLayout('Rigging_Edit_Model', h = (38 * 2), p = 'riggingEditMdlFrameLo')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = 'Hist', image1 = 'menuIconEdit.png', command = 'DeleteHistory', sourceType = 'mel')

    cmds.frameLayout('riggingBuildFrameLo', label = 'Build', collapse = False, collapsable = True, p = 'riggingScrLo')
    cmds.shelfLayout('Rigging_Build', h = (36.5 * 5), p = 'riggingBuildFrameLo')
    cmds.shelfButton(annotation = '', width = 35, height = 35, imageOverlayLabel = 'Hist', image1 = 'menuIconEdit.png', command = 'DeleteHistory', sourceType = 'mel')

    cmds.frameLayout('riggingSkinFrameLo', label = 'Skin Weights', collapse = False, collapsable = True, p = 'riggingScrLo')
    cmds.shelfLayout('Rigging_Skin_Weights', h = (40 * 2), p = 'riggingSkinFrameLo')

    cmds.frameLayout('riggingExtraFrameLo', label = 'Extra Tools', collapse = False, collapsable = True, p = 'riggingScrLo')
    cmds.shelfLayout('Rigging_Extra_Tools', h = (40 * 2), p = 'riggingExtraFrameLo')





    # animation tab
    cmds.scrollLayout('aniScrLo', childResizable = True, p = 'AnimationFormLo')
    cmds.formLayout('AnimationFormLo', e = True, attachForm = [('aniScrLo', 'top', 0), ('aniScrLo', 'bottom', 0), ('aniScrLo', 'left', 0), ('aniScrLo', 'right', 0)])
    cmds.frameLayout('aniCtrlSelFrameLo', label = 'Control Select', collapse = False, collapsable = True, p = 'aniScrLo')
    cmds.shelfLayout('Animation_Control_Select', h = 41, p = 'aniCtrlSelFrameLo')

    cmds.frameLayout('aniDisplayFrameLo', label = 'Display', collapse = False, collapsable = True, p = 'aniScrLo')
    cmds.shelfLayout('Animation_Display', h = 41, p = 'aniDisplayFrameLo')

    cmds.frameLayout('aniCrvFrameLo', label = 'Animation Curve', collapse = False, collapsable = True, p = 'aniScrLo')
    cmds.shelfLayout('Animation_Animation_Curve', h = 41, p = 'aniCrvFrameLo')

    cmds.frameLayout('aniPoseFrameLo', label = 'Pose', collapse = False, collapsable = True, p = 'aniScrLo')
    cmds.shelfLayout('Animation_Pose', h = 41, p = 'aniPoseFrameLo')


    cmds.frameLayout('aniRefineShapeFrameLo', label = 'Refine Shape', collapse = False, collapsable = True, p = 'aniScrLo')
    cmds.shelfLayout('Animation_Refine_Shape', h = 41, p = 'aniRefineShapeFrameLo')

    cmds.frameLayout('aniExtraFrameLo', label = 'Extra Tools', collapse = False, collapsable = True, p = 'aniScrLo')
    cmds.shelfLayout('Animation_Extra_Tools', h = 41, p = 'aniExtraFrameLo')





    # modeling tab
    cmds.scrollLayout('mdlScrLo', childResizable = True, p = 'ModelingFormLo')
    cmds.formLayout('ModelingFormLo', e = True, attachForm = [('mdlScrLo', 'top', 0), ('mdlScrLo', 'bottom', 0), ('mdlScrLo', 'left', 0), ('mdlScrLo', 'right', 0)])
    cmds.frameLayout('mdlDisplayFrameLo', label = 'Display', collapse = False, collapsable = True, p = 'mdlScrLo')
    cmds.shelfLayout('Modeling_Display', h = (41 * 1), p = 'mdlDisplayFrameLo')

    cmds.frameLayout('mdlSelFrameLo', label = 'Selection', collapse = False, collapsable = True, p = 'mdlScrLo')
    cmds.shelfLayout('Modeling_Selection', h = 41, p = 'mdlSelFrameLo')

    cmds.frameLayout('mdlEditCpntFrameLo', label = 'Edit Component', collapse = False, collapsable = True, p = 'mdlScrLo')
    cmds.shelfLayout('Modeling_Edit_Component', h = (38 * 2), p = 'mdlEditCpntFrameLo')

    cmds.frameLayout('mdlEditGeoFrameLo', label = 'Edit Mesh', collapse = False, collapsable = True, p = 'mdlScrLo')
    cmds.shelfLayout('Modeling_Edit_Mesh', h = (38 * 3), p = 'mdlEditGeoFrameLo')

    cmds.frameLayout('mdlMatFrameLo', label = 'Material', collapse = False, collapsable = True, p = 'mdlScrLo')
    cmds.shelfLayout('Modeling_Material', h = 41, p = 'mdlMatFrameLo')

    cmds.frameLayout('mdlAppFrameLo', label = 'Extra Tools', collapse = False, collapsable = True, p = 'mdlScrLo')
    cmds.shelfLayout('Modeling_Extra_Tools', h = (38 * 2), p = 'mdlAppFrameLo')






    # misc tab
    cmds.scrollLayout('miscScrLo', childResizable = True, p = 'MiscFormLo')
    cmds.formLayout('MiscFormLo', e = True, attachForm = [('miscScrLo', 'top', 0), ('miscScrLo', 'bottom', 0), ('miscScrLo', 'left', 0), ('miscScrLo', 'right', 0)])
    cmds.frameLayout('miscFrameLo', label = 'Misc', collapsable = True, p = 'miscScrLo')
    cmds.shelfLayout('Misc_Misc', h = (41 * 2), p = 'miscFrameLo')
 
    cmds.frameLayout('tempFrameLo', label = 'Temp', collapsable = True, p = 'miscScrLo')
    cmds.shelfLayout('Misc_Temp', h = (41 * 2), p = 'tempFrameLo')
    



    # Ouliner
    cmds.frameLayout('olFrameLo', labelVisible = False, p = 'mainPaneLo')
    panel = cmds.outlinerPanel()
    outliner = cmds.outlinerPanel(panel, query = True, outlinerEditor = True)
    cmds.outlinerEditor(outliner, edit = True, mainListConnection = 'worldList', selectionConnection = 'modelList', showShapes = False, showReferenceNodes = True, showReferenceMembers = False, showAttributes = False, showConnected = False, showAnimCurvesOnly = False, autoExpand = False, showDagOnly = True, ignoreDagHierarchy = False, expandConnections = False, showCompounds = True, showNumericAttrsOnly = False, highlightActive = True, autoSelectNewObjects = False, doNotSelectNewObjects = False, transmitFilters = False, showSetMembers = True, setFilter = 'defaultSetFilter')





    # make dockable
    allowedAreas = ['right', 'left']
    cmds.dockControl('tTDock', label = "Tak Tools", area='left', content = 'takToolWin', allowedArea = allowedAreas)







shelfList = ['Common', 
'Rigging_Display', 'Rigging_Edit_Model', 'Rigging_Build', 'Rigging_Skin_Weights', 'Rigging_Extra_Tools', 
'Animation_Control_Select', 'Animation_Display', 'Animation_Animation_Curve', 'Animation_Pose', 'Animation_Refine_Shape', 'Animation_Extra_Tools', 
'Modeling_Display', 'Modeling_Selection', 'Modeling_Edit_Component', 'Modeling_Edit_Mesh', 'Modeling_Material', 'Modeling_Extra_Tools', 
'Misc_Misc', 'Misc_Temp']


def saveTools(*args):
    '''
    Save tak_tools with current state.
    '''
    # Read tool file
    fR = open(toolFilePath, 'r')
    contents = fR.read()
    fR.close()

    # Get shelf buttons for each shelfLayout
    for shelf in shelfList:
        btns = getBtns(shelf)

        curBtnCodes = ''

        # Get shelf button code for each shelf button
        if btns:
            for btn in btns:
                shelfBtnCode = getBtnInfo(btn)
                curBtnCodes += shelfBtnCode + '\n'

            # Find code block that related with specific shelf in contents
            codeBlock = re.search(r'.*%s.*\n((\s+cmds\.shelfButton.*\n){0,100})' %shelf, contents).group(1)

            if codeBlock:
                # Replace prior button codes to current shelf button codes in contents
                contents = contents.replace(codeBlock, curBtnCodes)
            else:
                codeBlock = re.search(r'\s+.+%s.+\n' %shelf, contents).group(0)

                # Replace prior button codes to current shelf button codes in contents
                contents = contents.replace(codeBlock, codeBlock + curBtnCodes)

        else:
            codeBlock = re.search(r'\s+.+%s.+\n' %shelf, contents).group(0)
            print codeBlock

            # Replace prior button codes to current shelf button codes in contents
            contents = contents.replace(codeBlock, codeBlock + '')

    # Save tool file
    fW = open(toolFilePath, 'w')
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
    for shelf in shelfList:
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
    iconImgPath = cmds.fileDialog2(fileMode = 1, caption = 'Select a Image', startingDirectory = iconsFolder)
    if iconImgPath:
        iconName = os.path.basename(iconImgPath[0])
        cmds.textFieldButtonGrp(widgetName, e = True, text = iconName)