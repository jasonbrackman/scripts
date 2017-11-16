'''
Author: Sang-tak Lee
Contact: chst27@gmail.com

Description:
This script will create left/right blendshape target from source.

Usage:
1. Copy this script and paste in your scripts folder.

2. In maya python tab, run following code.
import tak_LRTarget
reload(tak_LRTarget)
tak_LRTarget.UI()
'''

import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
from functools import partial
import re


def UI():
    winName = 'LRBTWin'
    if cmds.window(winName, exists = True): 
        cmds.deleteUI(winName)
    cmds.window(winName, title = 'L/R Blend Shape Target')
    
    cmds.formLayout('mainForm', nd = 100)
    
    cmds.tabLayout('mainTab', tv = False)
    cmds.tabLayout('subTab', tv = False, scrollable = True)
    
    cmds.columnLayout('mainColLay', adj = True, h = 280)
    cmds.textFieldButtonGrp('baseTexFiel', label = 'Base: ', bl = 'Load Sel', columnWidth = [(1, 50), (2, 150)], bc = partial(loadSel, 'baseTexFiel'))
    cmds.rowColumnLayout('trgRowColLay', numberOfColumns = 3, columnWidth = [(1, 52), (2, 150), (3, 52)])
    cmds.text(label = 'Targets:')
    cmds.textScrollList('trgTexScrList', h = 100)
    cmds.button(label = 'Load Sel', h = 5, c = loadSel)
    '''cmds.textFieldButtonGrp('trgTexFiel', label = 'Target: ', bl = 'Load Sel', columnWidth = [(1, 50), (2, 150)], bc = partial(loadSel, 'trgTexFiel'))'''
    cmds.setParent('mainColLay')

    cmds.separator(h = 10, style = 'in')
    
    cmds.text(label = 'If error in dense area, decrease value else if error in wide area, increase value about +-0.00##', wordWrap = True, align = 'left')
    cmds.rowColumnLayout(numberOfColumns = 2, columnWidth= [(1, 152), (2, 45)], columnAttach = [(1, 'right', 1)])
    cmds.text(label = 'Symmetry Vertex Tolerance: ')
    cmds.floatField('symVtxTolTexFiel', minValue=0, maxValue=1, value=0.002)
    cmds.setParent('mainColLay')

    cmds.rowColumnLayout(numberOfColumns = 3, columnWidth= [(1, 90), (2, 30)], columnAttach = [(1, 'right', 1)])
    cmds.text(label = 'Center Fall Off: ')
    cmds.intField('taperintFiel', minValue=0, maxValue = 100, value=10)
    cmds.text(label = '%')
    cmds.setParent('mainColLay')

    cmds.separator(h = 10, style = 'in')

    cmds.rowColumnLayout(numberOfColumns = 3, columnWidth = [(1, 70), (2, 50), (3, 50)], columnAttach = [(1, 'right', 1)])
    cmds.text(label = 'L/R Prefix: ')
    cmds.textField('lPreTexField', text = 'lf_')
    cmds.textField('rPreTexField', text = 'rt_')
    cmds.setParent('mainColLay')
    
    cmds.rowColumnLayout(numberOfColumns = 3, columnWidth = [(1, 70), (2, 50), (3, 50)], columnAttach = [(1, 'right', 1)])
    cmds.text(label = 'L/R Suffix: ')
    cmds.textField('lSufTexField', text = '')
    cmds.textField('rSufTexField', text = '')
    cmds.setParent('mainColLay')
        
    # go out to the mainForm layout
    cmds.setParent('mainForm')
    
    cmds.button('appButton', label = 'Create L/R', w = 90, c = main)
    cmds.button('flipBtn', label = 'Create Flip', c = flip)
    cmds.button('recoverButton', label = 'Recover Freezed', w = 90, c = recoverFrzedTrg)
    
    cmds.formLayout('mainForm', e = True, 
                    attachForm = [('mainTab', 'top', 5), ('mainTab', 'left', 5), ('mainTab', 'right', 5), ('appButton', 'bottom', 5), ('appButton', 'left', 5), ('flipBtn', 'bottom', 5), ('recoverButton', 'bottom', 5), ('recoverButton', 'right', 5)],
                    attachPosition = [],
                    attachControl = [('mainTab', 'bottom', 5, 'appButton'), ('flipBtn', 'left', 5, 'appButton'), ('flipBtn', 'right', 5, 'recoverButton')])
    
    cmds.window(winName, edit = True, w = 290, h = 340)
    cmds.showWindow(winName)
    
def loadSel(widgetName):
    sel = cmds.ls(sl = True)
    try:
        cmds.textFieldButtonGrp(widgetName, e = True, text = sel[0])
    except:
        if cmds.textScrollList('trgTexScrList', q = True, allItems = True):
            cmds.textScrollList('trgTexScrList', e = True, removeAll = True)
        cmds.textScrollList('trgTexScrList', e = True, append = sel)

def close(winName, *args):
    cmds.deleteUI(winName)


def main(*args):
    # get data
    baseName = cmds.textFieldButtonGrp('baseTexFiel', q = True, text = True)
    targetList = cmds.textScrollList('trgTexScrList', q = True, allItems = True)
    lPrefix = cmds.textField('lPreTexField', q = True, text = True)
    rPrefix = cmds.textField('rPreTexField', q = True, text = True)
    lSuffix = cmds.textField('lSufTexField', q = True, text = True)
    rSuffix = cmds.textField('rSufTexField', q = True, text = True)
    centerFallOff = cmds.intField('taperintFiel', q = True, v = True) * 0.01
    maxVtxX = getMaxXPos(baseName)
    fallOffRange = (maxVtxX * centerFallOff) * 2

    for targetName in targetList:
        targetPos = cmds.xform(targetName, q = True, ws = True, t = True)
        boundingBox = cmds.exactWorldBoundingBox(targetName)
        LRDist = boundingBox[3] - boundingBox[0]
        
        # create left side blend target
        lBlendTarget = cmds.duplicate(baseName, n = lPrefix + targetName + lSuffix, rr = True, renameChildren = True)
        # if not in world in outliner parent to the world
        if cmds.listRelatives(lBlendTarget[0], p = True):
            cmds.parent(lBlendTarget[0], world = True)
        # unlock attributes
        attrList = ['translateX', 'translateY', 'translateZ']
        for attr in attrList:
            cmds.setAttr(lBlendTarget[0] + '.' + str(attr), lock = False)
        # move to target's left side
        cmds.xform(lBlendTarget, ws = True, t = ((targetPos[0] + LRDist), targetPos[1], targetPos[2]))

        # create right side belnd target
        rBlendTarget = cmds.duplicate(baseName, n = rPrefix + targetName + rSuffix, rr = True, renameChildren = True)
        # if not in world in outliner parent to the world
        if cmds.listRelatives(rBlendTarget[0], p = True):
            cmds.parent(rBlendTarget[0], world = True)
        # unlock attributes
        for attr in attrList:
                cmds.setAttr(rBlendTarget[0] + '.' + str(attr), lock = False)
        # move to target's right side
        cmds.xform(rBlendTarget, ws = True, t = ((targetPos[0] - LRDist), targetPos[1], targetPos[2]))

        # get child geometry list
        baseChildList = cmds.listRelatives(baseName, allDescendents = True, type = 'transform')
        # in case base is not group
        if not baseChildList:
            # initialize list variables
            baseChildList = []
            targetChildList = []
            lTargetChildList = []
            rTargetChildList = []

            baseChildList.append(baseName)
            targetChildList.append(targetName)
            lTargetChildList.append(lBlendTarget[0])
            rTargetChildList.append(rBlendTarget[0])
        else:
            baseChildList = removeGrp(baseChildList)

            targetChildList = cmds.listRelatives(targetName, allDescendents = True, type = 'transform')
            targetChildList = removeGrp(targetChildList)

            lTargetChildList = cmds.listRelatives(lBlendTarget, allDescendents = True, type = 'transform')
            lTargetChildList = removeGrp(lTargetChildList)

            rTargetChildList = cmds.listRelatives(rBlendTarget, allDescendents = True, type = 'transform') 
            rTargetChildList = removeGrp(rTargetChildList)
        
        # vector calculation for each geometry
        for x in xrange(len(baseChildList)):
            # get symmetrical matching vertex data
            symVtxDic, cVtxList = matchSymVtx(baseChildList[x])

            for lVtxIndex in symVtxDic.keys():
                trgVtxPos = cmds.pointPosition('%s.vtx[%d]' %(targetChildList[x], lVtxIndex), local = True)
                baseVtxPos = cmds.pointPosition('%s.vtx[%d]' %(baseChildList[x], lVtxIndex), local = True)

                trgVtxVec = OpenMaya.MVector(*trgVtxPos)
                baseVtxVec = OpenMaya.MVector(*baseVtxPos)
                moveVec = trgVtxVec - baseVtxVec
                
                # if vertex didn't move, skip caculation
                if moveVec.length() == 0:
                    continue

                # weight value calculation
                weightVal = 0.5 + (baseVtxVec.x / fallOffRange)
                if weightVal >= 1:
                    weightVal = 1
                symWeightVal = 1 - weightVal

                
                lTrgVtxVec = baseVtxVec
                # if 0 < abs(lTrgVtxVec.x) <= fallOffRange:
                lMoveVec = moveVec * weightVal
                # elif lTrgVtxVec.x > fallOffRange:
                #     lMoveVec = moveVec * 1
                # final left side vertex position
                finalVec = lTrgVtxVec + lMoveVec

                # assign to the left blend target
                cmds.xform('%s.vtx[%d]' %(lTargetChildList[x], lVtxIndex), os = True, t = (finalVec.x, finalVec.y, finalVec.z))
                # assign to the right blend target's symmetry vertex
                cmds.xform('%s.vtx[%d]' %(rTargetChildList[x], symVtxDic[lVtxIndex]), os = True, t = (-finalVec.x, finalVec.y, finalVec.z))

                # assign to the symmetry vertex
                symVtxPos = cmds.pointPosition('%s.vtx[%d]' %(baseChildList[x], symVtxDic[lVtxIndex]), local = True)
                symVtxVec = OpenMaya.MVector(*symVtxPos)

                if 0 < abs(symVtxVec.x) <= fallOffRange:
                    symMoveVec = moveVec * symWeightVal
                    symFinalVec = [(symVtxVec.x + -symMoveVec.x), (symVtxVec.y + symMoveVec.y), (symVtxVec.z + symMoveVec.z)]

                    # assign to the right blend target
                    cmds.xform('%s.vtx[%d]' %(lTargetChildList[x], symVtxDic[lVtxIndex]), os = True, t = (symFinalVec[0], symFinalVec[1], symFinalVec[2]))
                    # assign to the left blend target's symmetry vertex
                    cmds.xform('%s.vtx[%d]' %(rTargetChildList[x], lVtxIndex), os = True, t = (-symFinalVec[0], symFinalVec[1], symFinalVec[2]))

            # center vertex
            for cVtxIndex in cVtxList:
                trgVtxPos = cmds.pointPosition('%s.vtx[%d]' %(targetChildList[x], cVtxIndex), local = True)
                baseVtxPos = cmds.pointPosition('%s.vtx[%d]' %(baseChildList[x], cVtxIndex), local = True)

                trgVtxVec = OpenMaya.MVector(*trgVtxPos)
                baseVtxVec = OpenMaya.MVector(*baseVtxPos)
                moveVec = trgVtxVec - baseVtxVec
                
                # if vertex didn't move, skip caculation
                if moveVec.length() == 0:
                    continue

                cMoveVec = moveVec * 0.5

                # final center vertex position
                finalVec = baseVtxVec + cMoveVec
                cmds.xform('%s.vtx[%d]' %(lTargetChildList[x], cVtxIndex), os = True, t = (finalVec.x, finalVec.y, finalVec.z))
                cmds.xform('%s.vtx[%d]' %(rTargetChildList[x], cVtxIndex), os = True, t = (finalVec.x, finalVec.y, finalVec.z))

# fuction for remove only transform node in the list
def removeGrp(transformList):
    hasShapeTsfmList = []
    for item in transformList:
        if cmds.listRelatives(item, s = True):
            hasShapeTsfmList.append(item)
    return hasShapeTsfmList

# function for match symmetry vertex
def matchSymVtx(geomtry):
    # get number of vertex
    numOfVtx = cmds.polyEvaluate(geomtry, v = True)

    # get left and right and center vertex list
    lVtxList = []
    rVtxList = []
    cVtxList = []
    symVtxDic = {}

    for i in xrange(numOfVtx):
        vtxPos = cmds.pointPosition('%s.vtx[%d]' %(geomtry, i), local = True)

        # refine raw vtxPos data
        for val in xrange(len(vtxPos)):
            if 'e' in str(vtxPos[val]):
                vtxPos[val] = 0.0
            else:
                vtxPos[val] = round(vtxPos[val], 3)

        if vtxPos[0] > 0:
            lVtxList.append(i)
        elif vtxPos[0] < 0:
            rVtxList.append(i)
        else:
            cVtxList.append(i)
    
    # get symmetry vertex tolerance value for find matching right side symmetry vertex
    symVtxTol = cmds.floatField('symVtxTolTexFiel', q = True, value = True)

    # get symVtxDic
    for lVtxIndex in lVtxList:
        lVtxPos = cmds.pointPosition('%s.vtx[%d]' %(geomtry, lVtxIndex), local = True)
        symVtxPos = -lVtxPos[0], lVtxPos[1], lVtxPos[2]
        symVtxVec = OpenMaya.MVector(*symVtxPos)

        for rVtxIndex in rVtxList:
            rVtxPos = cmds.pointPosition('%s.vtx[%d]' %(geomtry, rVtxIndex), local = True)
            rVtxVec = OpenMaya.MVector(*rVtxPos)

            dist = symVtxVec - rVtxVec

            if dist.length() <= symVtxTol:
                symVtxDic[lVtxIndex] = rVtxIndex
                index = rVtxList.index(rVtxIndex)
                rVtxList.pop(index)
                break

    return symVtxDic, cVtxList


def getMaxXPos(base):
    maxXPos = 0
    baseChildList = cmds.listRelatives(base, allDescendents = True, type = 'transform')
    # in case base is not group
    if not baseChildList:
        baseChildList = []
        baseChildList.append(base)
    else:
        baseChildList = removeGrp(baseChildList)

    for geo in baseChildList:
        numOfVtx = cmds.polyEvaluate(geo, v = True)
        for i in xrange(numOfVtx):
            vtxPos = cmds.pointPosition('{0}.vtx[{1}]'.format(geo, i), local = True)
            if vtxPos[0] > maxXPos:
                maxXPos = vtxPos[0]
    return maxXPos



def flip(*args):


    # get data
    baseName = cmds.textFieldButtonGrp('baseTexFiel', q = True, text = True)
    targetList = cmds.textScrollList('trgTexScrList', q = True, allItems = True)
    lPrefix = cmds.textField('lPreTexField', q = True, text = True)
    rPrefix = cmds.textField('rPreTexField', q = True, text = True)
    lSuffix = cmds.textField('lSufTexField', q = True, text = True)
    rSuffix = cmds.textField('rSufTexField', q = True, text = True)

    for targetName in targetList:
        targetPos = cmds.xform(targetName, q = True, ws = True, t = True)
        boundingBox = cmds.exactWorldBoundingBox(targetName)
        LRDist = boundingBox[3] - boundingBox[0]

        # duplicate and placing target
        if lPrefix and re.search(r'%s' %lPrefix, targetName):
            dupName = re.sub(r'%s' %lPrefix, r'%s' %rPrefix, targetName)
            fliped = cmds.duplicate(targetName, n = dupName, rr = True, renameChildren = True)
            # if not in world in outliner parent to the world
            if cmds.listRelatives(fliped[0], p = True):
                cmds.parent(fliped[0], world = True)
            # move to target's right side
            cmds.xform(fliped, ws = True, t = ((targetPos[0] - LRDist), targetPos[1], targetPos[2]))

        elif rPrefix and re.search(r'%s' %rPrefix, targetName):
            dupName = re.sub(r'%s' %rPrefix, r'%s' %lPrefix, targetName)
            fliped = cmds.duplicate(targetName, n = dupName, rr = True, renameChildren = True)
            # if not in world in outliner parent to the world
            if cmds.listRelatives(fliped[0], p = True):
                cmds.parent(fliped[0], world = True)
            # move to target's right side
            cmds.xform(fliped, ws = True, t = ((targetPos[0] + LRDist), targetPos[1], targetPos[2]))

        elif lSuffix and re.search(r'%s' %lSuffix, targetName):
            dupName = re.sub(r'%s' %lSuffix, r'%s' %rSuffix, targetName)
            fliped = cmds.duplicate(targetName, n = dupName, rr = True, renameChildren = True)
            # if not in world in outliner parent to the world
            if cmds.listRelatives(fliped[0], p = True):
                cmds.parent(fliped[0], world = True)
            # move to target's right side
            cmds.xform(fliped, ws = True, t = ((targetPos[0] - LRDist), targetPos[1], targetPos[2]))

        elif rSuffix and re.search(r'%s' %rSuffix, targetName):
            dupName = re.sub(r'%s' %rSuffix, r'%s' %lSuffix, targetName)
            fliped = cmds.duplicate(targetName, n = dupName, rr = True, renameChildren = True)
            # if not in world in outliner parent to the world
            if cmds.listRelatives(fliped[0], p = True):
                cmds.parent(fliped[0], world = True)
            # move to target's right side
            cmds.xform(fliped, ws = True, t = ((targetPos[0] + LRDist), targetPos[1], targetPos[2]))

        else:
            fliped = cmds.duplicate(targetName, rr = True, renameChildren = True)
            # unlock attributes
            attrList = ['translateX', 'translateY', 'translateZ']
            for attr in attrList:
                cmds.setAttr(fliped[0] + '.' + str(attr), lock = False)

        # get child geometry list
        baseChildList = cmds.listRelatives(baseName, allDescendents = True, type = 'transform')
        # in case base is not group
        if not baseChildList:
            # initialize list variables
            baseChildList = []
            targetChildList = []

            baseChildList.append(baseName)
            targetChildList.append(fliped[0])
        else:
            baseChildList = removeGrp(baseChildList)

            targetChildList = cmds.listRelatives(fliped, allDescendents = True, type = 'transform')
            targetChildList = removeGrp(targetChildList)

        # flip geometry
        for x in xrange(len(baseChildList)):
            # get symmetrical matching vertex data
            symVtxDic, cVtxList = matchSymVtx(baseChildList[x])

            for lVtxIndex in symVtxDic.keys():
                # get left and right vertex position
                lVtxPos = cmds.pointPosition('%s.vtx[%d]' %(targetChildList[x], lVtxIndex), local = True)
                rVtxPos = cmds.pointPosition('%s.vtx[%d]' %(targetChildList[x], symVtxDic[lVtxIndex]), local = True)

                # change lVtxPos and rVtxPos
                lVtxPos, rVtxPos = (-rVtxPos[0], rVtxPos[1], rVtxPos[2]), (-lVtxPos[0], lVtxPos[1], lVtxPos[2])

                # set vertex position
                cmds.xform('%s.vtx[%d]' %(targetChildList[x], lVtxIndex), os = True, t = lVtxPos)
                cmds.xform('%s.vtx[%d]' %(targetChildList[x], symVtxDic[lVtxIndex]), os = True, t = rVtxPos)



def recoverFrzedTrg(*args):
    origFacialGrp = cmds.textFieldButtonGrp('baseTexFiel', q = True, text = True)
    targetList = cmds.textScrollList('trgTexScrList', q = True, allItems = True)

    for frzedFacialGrp in targetList:
        # Cleanup frzedFacialGrp
        cmds.delete(frzedFacialGrp, ch = True)
        cmds.makeIdentity(frzedFacialGrp, apply = True)
        allChlds = cmds.listRelatives(frzedFacialGrp, ad = True, type = 'transform')
        for chld in allChlds:
            if 'Base' in chld:
                cmds.delete(chld)

        # Match original facial group to freezed facial group
        origFacialDupGrp = cmds.duplicate(origFacialGrp, rc = True, rr = True)
        cmds.delete(cmds.parentConstraint(frzedFacialGrp, origFacialDupGrp, mo = False))

        origFacialDupMeshes = cmds.listRelatives(origFacialDupGrp, ad = True, type = 'mesh')
        frzedFacialGrpMeshes = cmds.listRelatives(frzedFacialGrp, ad = True, type = 'mesh')

        for i in xrange(len(origFacialDupMeshes)):
            numOfVtx = cmds.polyEvaluate(origFacialDupMeshes[i], vertex = True)
            for vtxId in xrange(numOfVtx):
                frzedFacialMeshVtxWsPos = cmds.pointPosition(frzedFacialGrpMeshes[i] + '.vtx[' + str(vtxId) + ']', world = True)
                cmds.xform(origFacialDupMeshes[i] + '.vtx[' + str(vtxId) + ']', t = frzedFacialMeshVtxWsPos, ws = True)

        cmds.delete(frzedFacialGrp)
        cmds.rename(origFacialDupGrp, frzedFacialGrp)