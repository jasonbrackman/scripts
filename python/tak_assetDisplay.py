'''
Author: Sang-tak Lee
Contact: chst27@gmail.com

Description:
This script is for control display of assets in the scene.

Requirement:
tak_logging.py

Usage:
Place tak_assetDisplay.py in your scripts folder.

tak_assetDisplay
reload(tak_assetDisplay)
tak_assetDisplay.UI()

Update Note:
2014-07-08 v1.0
1st release

2014-07-09 v1.1
Remove shading mode and lod section

2014-07-23 v1.2
Check if reference is loaded.
'''

import maya.cmds as cmds
import maya.mel as mel
import tak_logging
import re

# create logger for debugging
logger = tak_logging.Logger()
logger.setLevel('WARNING')

# main UI
def UI():
    winName = 'assetDispWin'
    if cmds.window(winName, exists = True):
        cmds.deleteUI(winName)
                    
    cmds.window(winName, title = 'Asset Display UI')
        
    cmds.menuBarLayout()
    cmds.menu(label = 'Option')
    cmds.menuItem(label = 'Reset', c = reset)    
            
    cmds.tabLayout(tv = False)
    
    cmds.columnLayout('mainColLayout', adj = True)
     
    # add categorys to the main UI
    addFrameLayout('Character')
    addFrameLayout('BG')
    addFrameLayout('Prop')
    
    # get asset information
    assetInfos = getAssetInfo()       
    
    # variables for check if is categorys
    isChar = None
    isBG = None
    isProp = None
    
    # get refrence node list in the scene
    refNodeList = cmds.ls(references = True)
    
    # lists for asset objects
    chaAssetWidgetObjs = []
    bgAssetWidgetObjs = []
    propAssetWidgetObjs = []
    
    # main iterator
    for refNode in refNodeList:
        logger.debug('reference node: %s ' %refNode)
        
        # check if reference current state is loaded
        if not cmds.referenceQuery(refNode, il = True):
            continue
        
        # set up display layer for each asset
        try:
            displayLayerName = putIntoLayer(assetInfos[refNode][1])
        except:
            continue
        # append displayLayerName to assetInfos
        assetInfos[refNode].append(displayLayerName)
        
        # create asset widget object
        assetWidgetObj = AssetWidget(refNode, assetInfos)
        
        # decide parent layout for asset widget object and check if is categorys and append to proper asset object list
        if assetInfos[refNode][2] == 'cha':
            parentLayout = 'CharacterFrame'
            isChar = True
            chaAssetWidgetObjs.append(assetWidgetObj)
        elif assetInfos[refNode][2] == 'set':
            parentLayout = 'BGFrame'
            isBG = True
            bgAssetWidgetObjs.append(assetWidgetObj)
        elif assetInfos[refNode][2] == 'prp':
            parentLayout = 'PropFrame'
            isProp = True
            propAssetWidgetObjs.append(assetWidgetObj)
        elif assetInfos[refNode][2] == 'wep':
            parentLayout = 'PropFrame'
            isProp = True
            propAssetWidgetObjs.append(assetWidgetObj)
        elif assetInfos[refNode][2] == 'veh':
            parentLayout = 'PropFrame'
            isProp = True
            propAssetWidgetObjs.append(assetWidgetObj)
        # end if
        
        logger.debug('parent layout: %s' %parentLayout)
        
        # create layout and parent to the proper category
        assetWidgetObj.widget(parentLayout)
    # end for
    
    logger.debug('Character asset widget objects: %s' %chaAssetWidgetObjs)
    logger.debug('BG asset widget objects: %s' %bgAssetWidgetObjs)
    logger.debug('Prop asset widget objects: %s' %propAssetWidgetObjs)
    
    # add master controls for each category
    categorys = ['Character', 'BG', 'Prop']
    for category in categorys:
        # set proper assetWidgetObjs
        if category == 'Character':
            assetWidgetObjs = chaAssetWidgetObjs
        elif category == 'BG':
            assetWidgetObjs = bgAssetWidgetObjs
        elif category == 'Prop':
            assetWidgetObjs = propAssetWidgetObjs
        
        # create master control object passing category and assetWidgetObjs     
        masterConObj = MasterCon(category, assetWidgetObjs)
        masterConObj.addMasterCon()
         
    # print final asset info
    logger.info('assetInfos: %s' %(assetInfos))
        
    # if nothing in the category, hide category
    if isChar == None:
        cmds.frameLayout('CharacterFrame', e = True, vis = False)
    if isBG == None:
        cmds.frameLayout('BGFrame', e = True, vis = False)
    if isProp == None:
        cmds.frameLayout('PropFrame', e = True, vis = False)
    # end if    
       
    # show window
    cmds.window(winName, e = True, w = 450, h = 300, sizeable = True)
    cmds.showWindow(winName)
     
def addFrameLayout(categoryName):
    cmds.frameLayout(categoryName + 'Frame', label = categoryName, cll = True, marginHeight = 10)
    
    cmds.rowColumnLayout(numberOfColumns = 6, 
                         columnWidth = [(1, 100), (2, 60), (3, 60), (4, 60), (5, 60), (6, 100)], 
                         columnAttach = [(1, 'left', 10), (6, 'right', 15)])
    
    cmds.text(label = 'Asset')
    cmds.text(label = 'Geometry')
    cmds.text(label = 'Texture')
    cmds.text(label = 'Main Con')
    cmds.text(label = 'Extra Con')
    cmds.text(label = 'Geometry Type')
    
    # parent rowColumnLayout to the frameLayout
    cmds.setParent(categoryName + 'Frame')
    
    cmds.separator(style = 'in')
    
    # dummy layout for master controls
    cmds.columnLayout(categoryName + 'MasterConLay', rowSpacing = 0, adj = True)
    
    # parent frameLayout to the main column layout
    cmds.setParent('mainColLayout')        

def getAssetInfo():
    # get namespace and reference file name of assets in the scene
    referenceNodeList = cmds.ls(references = True)
    assetInfos = {}
    for refNode in referenceNodeList:
        logger.debug('reference node: %s' %refNode)
        try:
            refFileName = cmds.referenceQuery(refNode, filename = True)
        except:
            continue
        logger.debug('reference file name: %s' %refFileName)
        if not 'Asset' in refFileName:
            continue
        assetName = refNode.split('_')[0]
        logger.debug('asset name: %s' %assetName)
        try:
            namespace = cmds.referenceQuery(refNode, namespace = True, shortName = True)
            logger.debug('namespace: %s' %namespace)
        except:
            continue
        assetCategory = re.search(r'.*Asset/(.*?)/', refFileName).group(1)
        logger.debug('asset category: %s' %assetCategory)
        assetInfos[refNode] = [assetName, namespace, assetCategory]
    return assetInfos

def putIntoLayer(namespace):
    # if not exists display layer, set up
    if not cmds.objExists('%s:displayLayer' %namespace):        
        # create display layer node
        displayLayerName = cmds.createNode('displayLayer', n = '%s:displayLayer' %namespace)    
        # put meshes into the layer
        cmds.select('%s:root' %namespace, r = True)
        meshes = cmds.listRelatives(ad = True, type = 'mesh', fullPath = True)
        cmds.editDisplayLayerMembers(displayLayerName, meshes)
        # set initial display type to reference
        cmds.setAttr('%s:displayLayer.displayType' %namespace, 0)
    # else already exists, define display layer name
    else:
        displayLayerName = '%s:displayLayer' %namespace
    
    cmds.select(cl = True)
    return displayLayerName
    
class AssetWidget:
    # initializing attributes
    def __init__(self, refNode, assetInfos):
        self.assetName = assetInfos[refNode][0]
        self.namespace = assetInfos[refNode][1]
        self.category = assetInfos[refNode][2]
        self.displayLayer = assetInfos[refNode][3]

    # create widget and add to the window    
    def widget(self, parentLayout):
        cmds.rowColumnLayout(self.namespace + 'RowColLay', numberOfColumns = 6, 
                             columnWidth = [(1, 100), (2, 60), (3, 60), (4, 60), (5, 60), (6, 100)], 
                             columnAttach = [(1, 'left', 10), (2, 'left', 20), (3, 'left', 20), (4, 'left', 20),(5, 'left', 20), (6, 'both', 10)], 
                             parent = parentLayout)
        
        self.namespaceChkBox = cmds.checkBox(label = self.namespace, onc = self.showAll, ofc = self.hideAll, v = True)
        cmds.popupMenu()
        self.textPopup = cmds.menuItem(label = 'Select for Framing', c = self.textPopupCommand)
        '''self.hideAllMenuItem = cmds.menuItem(label = 'Hide All', c = self.hideAll)
        self.showAllMenuItem = cmds.menuItem(label = 'Show All', c = self.showAll)'''
        self.geoChkBox = cmds.checkBox(label = '', onc = self.geoChkBoxOnCommand, ofc = self.geoChkBoxOffCommand)
        self.texChkBox = cmds.checkBox(label = '', onc = self.texChkBoxOnCommand, ofc = self.texChkBoxOffCommand)
        self.mainConChkBox = cmds.checkBox(label = '', onc = self.mainConVisOn, ofc = self.mainConVisOff)
        self.extraConChkBox = cmds.checkBox(label = '', onc = self.extraConVisOn, ofc = self.extraConVisOff)
        self.geoTypeOptMenu = cmds.optionMenu(cc = self.geoType)
        cmds.menuItem(label = 'Normal')
        cmds.menuItem(label = 'Template')
        cmds.menuItem(label = 'Reference')        
     
        # query display status and preset option state
        # geometry visibility state
        if cmds.getAttr('%s.visibility' %self.displayLayer) == True:
            cmds.checkBox(self.geoChkBox, e = True, v = True)
        elif cmds.getAttr('%s.visibility' %self.displayLayer) == False:
            cmds.checkBox(self.geoChkBox, e = True, v = False)
            
        # texture visibility state
        if cmds.getAttr('%s.texturing' %self.displayLayer) == True:
            cmds.checkBox(self.texChkBox, e = True, v = True)
        elif cmds.getAttr('%s.texturing' %self.displayLayer) == False:
            cmds.checkBox(self.texChkBox, e = True, v = False)
            
        # main control visibility state
        if cmds.objExists('%s:Main' %self.namespace) == False:
            cmds.checkBox(self.mainConChkBox, e = True, vis = False)
        else:
            if self.category in ['cha', 'veh', 'prp']:
                if cmds.getAttr('%s:Main.visibility' %self.namespace) == True:
                    cmds.checkBox(self.mainConChkBox, e = True, v = True)
                elif cmds.getAttr('%s:Main.visibility' %self.namespace) == False:
                    cmds.checkBox(self.mainConChkBox, e = True, v = False)
            elif self.category in ['wep']:
                if cmds.getAttr('%s:cc_all.visibility' %self.namespace) == True:
                    cmds.checkBox(self.mainConChkBox, e = True, v = True)
                elif cmds.getAttr('%s:cc_all.visibility' %self.namespace) == False:
                    cmds.checkBox(self.mainConChkBox, e = True, v = False)
            
        # extra control visibility state
        if cmds.objExists('%s:Sub.extraControlVis' %self.namespace):
            if cmds.getAttr('%s:Sub.extraControlVis' %self.namespace) == True:
                cmds.checkBox(self.extraConChkBox, e = True, v = True)
            elif cmds.getAttr('%s:Sub.extraControlVis' %self.namespace) == False:
                cmds.checkBox(self.extraConChkBox, e = True, v = False)        
        elif not cmds.objExists('%s:Sub.extraControlVis' %self.namespace):
            cmds.checkBox(self.extraConChkBox, e = True, vis = False)
            
        # geometry type state
        if cmds.getAttr('%s.displayType' %self.displayLayer) == 0:
            cmds.optionMenu(self.geoTypeOptMenu, e = True, v = 'Normal')
        if cmds.getAttr('%s.displayType' %self.displayLayer) == 1:
            cmds.optionMenu(self.geoTypeOptMenu, e = True, v = 'Template')            
        if cmds.getAttr('%s.displayType' %self.displayLayer) == 2:
            cmds.optionMenu(self.geoTypeOptMenu, e = True, v = 'Reference')
            
            
    # commands for ui            
    def geoChkBoxOnCommand(self, *args):
        cmds.setAttr('%s.visibility' %self.displayLayer, True)
    def geoChkBoxOffCommand(self, *args):
        cmds.setAttr('%s.visibility' %self.displayLayer, False)
        
    def texChkBoxOnCommand(self, *args):
        cmds.setAttr('%s.texturing' %self.displayLayer, True)
    def texChkBoxOffCommand(self, *args):
        cmds.setAttr('%s.texturing' %self.displayLayer, False)   
        
    def textPopupCommand(self, *args):
        if cmds.objExists('%s:Center_M' %self.namespace):
            cmds.select('%s:Center_M' %self.namespace, r = True)
        else:
            cmds.select('%s:root' %self.namespace, r = True)
        '''mel.eval('FrameSelected;')
        cmds.select(cl = True)'''
        
    def hideAll(self, *args):
        try:
            self.geoChkBoxOffCommand()
            cmds.checkBox(self.geoChkBox, e = True, v = False)
            self.mainConVisOff()
            cmds.checkBox(self.mainConChkBox, e = True, v = False)
            self.extraConVisOff()
            cmds.checkBox(self.extraConChkBox, e = True, v = False)
        except:
            pass
    def showAll(self, *args):
        try:
            self.geoChkBoxOnCommand()
            cmds.checkBox(self.geoChkBox, e = True, v = True)
            self.mainConVisOn()
            cmds.checkBox(self.mainConChkBox, e = True, v = True)
            self.extraConVisOn()
            cmds.checkBox(self.extraConChkBox, e = True, v = True)
        except:
            pass

    def mainConVisOn(self, *args):
        try:
            cmds.setAttr('%s:Main.visibility' %self.namespace, True)
        except:
            cmds.setAttr('%s:cc_all.visibility' %self.namespace, True)
    def mainConVisOff(self, *args):
        try:
            cmds.setAttr('%s:Main.visibility' %self.namespace, False)
        except:
            cmds.setAttr('%s:cc_all.visibility' %self.namespace, False)
        
    def extraConVisOn(self, *args):
        cmds.setAttr('%s:Sub.extraControlVis' %self.namespace, True)
    def extraConVisOff(self, *args):
        cmds.setAttr('%s:Sub.extraControlVis' %self.namespace, False)        
        
    def geoType(self, *args):
        optStatus = cmds.optionMenu(self.geoTypeOptMenu, q = True, v = True)
        if optStatus == 'Normal':
            cmds.setAttr('%s.displayType' %self.displayLayer, 0)
        if optStatus == 'Template':
            cmds.setAttr('%s.displayType' %self.displayLayer, 1)        
        if optStatus == 'Reference':
            cmds.setAttr('%s.displayType' %self.displayLayer, 2)            
            
class MasterCon:
    # initialize data
    def __init__(self, categoryName, assetWidgetObjs):
        self.assetWidgetObjs = assetWidgetObjs
        self.categoryName = categoryName
        
    def addMasterCon(self):
        cmds.rowColumnLayout(numberOfColumns = 6, 
                             columnWidth = [(1, 100), (2, 60), (3, 60), (4, 60), (5, 60), (6, 100)], 
                             columnAttach = [(1, 'left', 10), (2, 'left', 20), (3, 'left', 20), (4, 'left', 20), (5, 'left', 20), (6, 'both', 10)], 
                             parent = self.categoryName + 'MasterConLay')
        
        cmds.checkBox(label = '', onc = self.allDisOn, ofc = self.allDisOff, v = True)
        self.geoChkBox = cmds.checkBox(label = '', v = True, onc = self.geoChkBoxOnCommand, ofc = self.geoChkBoxOffCommand)
        self.texChkBox = cmds.checkBox(label = '', v = True, onc = self.texChkBoxOnCommand, ofc = self.texChkBoxOffCommand)
        self.mainConChkBox = cmds.checkBox(label = '', v = True, onc = self.mainConVisOn, ofc = self.mainConVisOff)
        self.extraConChkBox = cmds.checkBox(label = '', v = True, onc = self.extraConVisOn, ofc = self.extraConVisOff)
        self.geoTypeOptMenu = cmds.optionMenu(cc = self.geoType)
        cmds.menuItem(label = 'Normal')
        cmds.menuItem(label = 'Template')
        cmds.menuItem(label = 'Reference')
        
        '''cmds.separator(h = 15, style = 'in', parent = self.categoryName + 'MasterConLay')'''
        
        # set initial state
        cmds.optionMenu(self.geoTypeOptMenu, e = True, v = 'Normal')
        
    # commands for ui            
    def geoChkBoxOnCommand(self, *args):
        for assetWidget in self.assetWidgetObjs:
            assetWidget.geoChkBoxOnCommand()
            cmds.checkBox(assetWidget.geoChkBox, e = True, v = True)
    def geoChkBoxOffCommand(self, *args):
        for assetWidget in self.assetWidgetObjs:
            assetWidget.geoChkBoxOffCommand()
            cmds.checkBox(assetWidget.geoChkBox, e = True, v = False)
       
    def texChkBoxOnCommand(self, *args):
        for assetWidget in self.assetWidgetObjs:
            assetWidget.texChkBoxOnCommand()
            cmds.checkBox(assetWidget.texChkBox, e = True, v = True)
    def texChkBoxOffCommand(self, *args):
        for assetWidget in self.assetWidgetObjs:
            assetWidget.texChkBoxOffCommand()
            cmds.checkBox(assetWidget.texChkBox, e = True, v = False)

    def mainConVisOn(self, *args):
        for assetWidget in self.assetWidgetObjs:
            try:
                assetWidget.mainConVisOn()
                cmds.checkBox(assetWidget.mainConChkBox, e = True, v = True)
            except:
                pass
    def mainConVisOff(self, *args):
        for assetWidget in self.assetWidgetObjs:
            try:
                assetWidget.mainConVisOff()
                cmds.checkBox(assetWidget.mainConChkBox, e = True, v = False)
            except:
                pass
        
    def extraConVisOn(self, *args):
        for assetWidget in self.assetWidgetObjs:
            try:
                assetWidget.extraConVisOn()
                cmds.checkBox(assetWidget.extraConChkBox, e = True, v = True)
            except:
                pass
    def extraConVisOff(self, *args):
        for assetWidget in self.assetWidgetObjs:
            try:
                assetWidget.extraConVisOff()
                cmds.checkBox(assetWidget.extraConChkBox, e = True, v = False)
            except:
                pass
 
    def geoType(self, *args):
        optStatus = cmds.optionMenu(self.geoTypeOptMenu, q = True, v = True)
        if optStatus == 'Normal':
            for assetWidget in self.assetWidgetObjs:
                cmds.optionMenu(assetWidget.geoTypeOptMenu, e = True, v = 'Normal')
                assetWidget.geoType()
        if optStatus == 'Template':
            for assetWidget in self.assetWidgetObjs:
                cmds.optionMenu(assetWidget.geoTypeOptMenu, e = True, v = 'Template')
                assetWidget.geoType()
        if optStatus == 'Reference':
            for assetWidget in self.assetWidgetObjs:
                cmds.optionMenu(assetWidget.geoTypeOptMenu, e = True, v = 'Reference')
                assetWidget.geoType()
                
    def allDisOn(self, *args):
        for assetWidget in self.assetWidgetObjs:
            assetWidget.showAll()
            cmds.checkBox(assetWidget.namespaceChkBox, e = True, v = True)
        
    def allDisOff(self, *args):
        for assetWidget in self.assetWidgetObjs:
            assetWidget.hideAll()
            cmds.checkBox(assetWidget.namespaceChkBox, e = True, v = False)
            
def reset(*args):
    assetInfos = getAssetInfo()
    referenceNodeList = cmds.ls(references = True)
    for refNode in referenceNodeList:
        try:
            cmds.delete('%s:displayLayer' %assetInfos[refNode][1])
        except:
            pass
    UI()