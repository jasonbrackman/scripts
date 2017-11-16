# coding: utf-8

import maya.cmds as cmds
import os
import re
from functools import partial

def UI():
    #check to see if our window exists
    if cmds.window("pororoSceneBuilder",exists=1):
        cmds. deleteUI("pororoSceneBuilder")
    
    #create our window        
    window = cmds.window("pororoSceneBuilder",title = "pororo Scene Builder",w = 300,h = 320,mnb = 0,mxb = 0,sizeable = 0)

    tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
    child1 = cmds.columnLayout(w = 300, h = 300)
    
    #create episode
    episodes =  cmds.optionMenu("episodes",w=290,label = "Choose episode :            ",cc=  work)
    populateEpisode()
    
    #create light set option menu
    cmds.separator(h = 15)
    lightSetOptionMenu = cmds.optionMenu("lightSetOptionMenu",w=290,label = "Choose a Light Set:        ",cc=populatelightMayafile)
    
    #populate the light set option menu
    populateLightSet()
    
    
    #create light ma option menu
    cmds.separator(h = 15)
    lightMaOptionMenu = cmds.optionMenu("lightMaOptionMenu",w = 290, label = "Choose a  LD maya file:  ")    
    
    #populate light ma option menu
    populatelightMayafile()    
    
        
    #create aniCutNo option menu
    cmds.separator(h = 15)
    aniCutNoOptionMenu = cmds.optionMenu("aniCutNoOptionMenu",w = 290, label = "Choose a ANI cut No.:    ",cc=populateAniMayafile)
    #populate the light set option menu
    populateAniCutNo()
    
    #create aniMayaFile option menu
    cmds.separator(h = 15)
    aniMayaFileOptionMenu = cmds.optionMenu("aniMayaFileOptionMenu",w = 290, label = "Choose a ANI maya file: ")
    
    #populate the light set option menu
    populateAniMayafile()
    
    
    #create build button
    cmds.separator(h = 15)
    cmds.button(label = "Build",w =290 , h = 50,c=load)
	
	#create  set frame button
    cmds.separator(h = 15)
    cmds.button(label = "set frame range",w =290 , h = 50,c=setframe)
    cmds.setParent( '..' )
       
    child2 = cmds.rowColumnLayout(numberOfColumns=2)
    cmds.button()
    cmds.button()
    cmds.button()
    cmds.setParent( '..' )
    
    cmds.tabLayout( tabs, edit=True, tabLabel=((child1, 'Step One'), (child2, 'Step Two')) )
    
    #show window
    cmds.showWindow(window)
    
def populateEpisode(*args):
    projectPath = "T:/Pororo/Season06/Animation/"
    projects = os.listdir(projectPath)
    for episode in projects:
        cmds.menuItem(label = episode,parent = "episodes")  


def populateLightSet(*args):
    projectPath = "X:/Pororo/Season06/EP00/Lighting/"
    projects = os.listdir(projectPath)
    for project in projects:
        cmds.menuItem(label = project,parent = "lightSetOptionMenu")  


def populatelightMayafile(*args):
    menuItems = cmds.optionMenu("lightMaOptionMenu",q = 1, itemListLong = 1)
    if menuItems != None:
        for item in menuItems:
            cmds.deleteUI(item)
            
    selectedProject = cmds.optionMenu("lightSetOptionMenu",q = 1 , v = 1)
    projectPath = "X:/Pororo/Season06/EP00/Lighting/"+ selectedProject + "/src/" 
    files = os.listdir(projectPath)
    characters = []
    for file in files:
        if file.rpartition(".")[2] == "mb" or file.rpartition(".")[2] =="ma":
            characters.append(file)
    for character in characters:
        niceName = character.rpartition(".")[0]
        cmds.menuItem(label = niceName, parent = "lightMaOptionMenu")
        
def populateAniCutNo(*args):
    menuItems = cmds.optionMenu("aniCutNoOptionMenu",q = 1, itemListLong = 1)
    if menuItems != None:
        for item in menuItems:
            cmds.deleteUI(item)
            
    episode = cmds.optionMenu("episodes",q = 1 , v = 1)  
    projectPath = "T:/Pororo/Season06/Animation/"+episode    
    projects = os.listdir(projectPath)
    for project in projects:
        cmds.menuItem(label = project,parent = "aniCutNoOptionMenu")  


def populateAniMayafile(*args):
    menuItems = cmds.optionMenu("aniMayaFileOptionMenu",q = 1, itemListLong = 1)
    if menuItems != None:
        for item in menuItems:
            cmds.deleteUI(item)
    
    episode = cmds.optionMenu("episodes",q = 1 , v = 1)          
    selectedProject = cmds.optionMenu("aniCutNoOptionMenu",q = 1 , v = 1)
    projectPath = "T:/Pororo/Season06/Animation/" + episode + "/" + selectedProject + "/src/"
    files = os.listdir(projectPath)
    
    characters = []
    for file in files:
        if file.rpartition(".")[2] == "mb" or file.rpartition(".")[2] =="ma":
            characters.append(file)
    for character in characters:
        niceName = character.rpartition(".")[0]
        cmds.menuItem(label = niceName, parent = "aniMayaFileOptionMenu")        

        
def load(*args):
    selectedlightSet = cmds.optionMenu("lightSetOptionMenu",q = 1 , v = 1)
    lightPath = "X:/Pororo/Season06/EP00/Lighting/"+ selectedlightSet + "/src/" 
    selectedLightMayaFile = cmds.optionMenu("lightMaOptionMenu",q=1,v=1)
    ltFileName = lightPath + selectedLightMayaFile + ".mb"
    cmds.file(ltFileName,open =1, force =1, prompt = 0)
    print "opening file" + ltFileName
    
    
    episode = cmds.optionMenu("episodes",q = 1 , v = 1)          
    selectedaniCutNo = cmds.optionMenu("aniCutNoOptionMenu",q = 1 , v = 1)
    aniPath = "T:/Pororo/Season06/Animation/" + episode + "/" + selectedaniCutNo + "/src/"
    selectedAniMayaFile = cmds.optionMenu("aniMayaFileOptionMenu",q=1,v=1)
    aniFileName = aniPath + selectedAniMayaFile + ".ma"
    cmds.file(aniFileName,r=1, dr=1,ns = selectedAniMayaFile)   
    
    print "opening file" + aniFileName    
	
	
def setframe(*args):
	#check renderer
	if cmds.getAttr('defaultRenderGlobals.ren') != 'arnold':
		cmds.setAttr('defaultRenderGlobals.ren', 'arnold', type='string')
	
	cameras = cmds.ls(cameras = 1)
	transforms = cmds.listRelatives(cameras, parent=1)
	for t in transforms:
		if "main" in t:
			cutNo = t.split("_")[1]
			frames = re.findall(r'\d+_\d+', t)[0]
			startFrames = frames.partition("_")[0]
			endFrames = frames.partition("_")[2]
			
	imageFilePrefix=cmds.getAttr("defaultRenderGlobals.imageFilePrefix")
	cmds.setAttr("defaultRenderGlobals.imageFilePrefix",imageFilePrefix.replace(imageFilePrefix.split("/")[0],cutNo),type="string")
	cmds.editRenderLayerGlobals( currentRenderLayer='defaultRenderLayer' )    	
	cmds.playbackOptions(minTime= startFrames,maxTime = endFrames)
	cmds.setAttr("defaultRenderGlobals.startFrame", startFrames)
	cmds.setAttr("defaultRenderGlobals.endFrame", endFrames)
	cmds.editRenderLayerGlobals( currentRenderLayer='defaultRenderLayer' )
	
def work(*args):
	populateAniCutNo(*args)
	populateAniMayafile(*args)


'''
Build 버튼을 누르면, 일단 씬을 .ma 파일로 저장하고, 
.ma 파일을 읽어들여서 편집해서 Reference 경로를 입력해서 다시 쓴다음,
Open으로 파일을 연다.
'''