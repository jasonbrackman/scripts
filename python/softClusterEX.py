'''
Header
    Toolname:    Soft Cluster EX
    Author:      Webber Huang
    Contact:     xracz.fx@gmail.com
    Homepage:    http://riggingtd.com
    Version:     1.02
    Requires:    Maya 2011 x64 or above
    Platform:    Windows 64bit, Mac OS X

______________________________________________
Description:
    Soft Cluster EX is a python and c++ based tool for converting soft selection to
    cluster, supports common types of deformable geometry(e.g. polygon,nurbs,subdiv
    and lattice) with a lot of advance features.
    
    Install:
        1. Place softSelectionQuery_<Version>-<Bit>.mll(or bundle) into your maya plugin path.
           e.g., C:/Program Files/Autodesk/Maya<Version>/bin/plug-ins/
        
        2. Place softClusterEX.py into your maya script path.
           e.g., C:/Users/YourUsername/Documents/maya/scripts/
        
    Usage:
        import softClusterEX
        softClusterEX.GUI()

    Features:
        General functionality:
        - user friendly UI, easy to understand
        - supports create cluster from polygon, nurbsSurface, nurbsCurve, subdiv and lattice
        - all types can be toggled on/off from UI
        - supports create cluster from multi objects of different type
        - change falloff mode
        - supports exclude influenced objects when in Global falloff mode
        - supports duplicate name objects

        Command line:
        - The core function of this tool come from the custom command "softSelectionQuery",
          you can use it to implement your own tools.
        
        - Synopsis: softSelectionQuery [flags] [String...]
          Flags:
            -ant -apiNodeTypes:                       return api type name of influenced objects
            -ap -allPaths:                            return partial paths to nodes in DAG
            -c -count:                                return count of influenced objects
            -cmp -components:                         return components of influenced objects
            -exo -excludeObjects  String (multi-use): set exclude objects
            -l -long:                                 return full path names for Dag objects
            -n -names:                                return names for Dag objects
            -nt -nodeTypes:                           return type names of influenced objects
            -s -shapeNames:                           return shape names of influenced objects
            -sap -shapeAllPaths:                      return partial paths to shape nodes in DAG
            -sl -shapeLong:                           return full path names for shapes 
            -t -types           String (multi-use):   set support types
            -w -weights:                              return weights of influenced components

______________________________________________
License:

Soft Cluster EX is released under a BSD-style license

Copyright (c) 2013, Webber Huang. 
All Rights Reserved.

Redistribution and use in source and binary forms, with or without modification, 
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, 
   this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, 
   this list of conditions and the following disclaimer in the documentation 
   and/or other materials provided with the distribution.

3. The name of the author may not be used to endorse or promote products 
   derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY WEBBER HUANG "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, 
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS 
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY 
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR 
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER 
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY 
WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

______________________________________________
Update Log:
    2013-10-27: v1.02 by Webber Huang
      - Compiled softSelectionQuery plugin for OS X, mac user can play with it

    2013-10-09: v1.01 by Webber Huang
      - Issue of plugin loading failed,i re-compile all softSelectionQuery_<Version>-<Bit>.mll
        with vs2008 to maintain maximum compatibility

    2013-09-30: v1.00 by Webber Huang
      - Initial release

______________________________________________
Todo:
    - performance improve when operate on high-res geometry
    - supports exclude objects by groups
    - supports convert cluster and joint into each other

______________________________________________
Feedback:
    Bugs, questions and suggestions to xracz.fx@gmail.com
'''


import maya.cmds as cmd
import maya.mel as mel
import maya.OpenMaya as om

__VERSION__ = 1.02
__SUPPORTTYPE_LABEL__ = {'mesh': 'Polygon',
                         'nurbsSurface': 'Nurbs Surface',
                         'nurbsCurve': 'Nurbs Curve',
                         'subdiv': 'Subdivision',
                         'lattice': 'Lattice'}

# load softSelectionQuery plugin
mayaVersion = cmd.about(v=1).split(' ')

if cmd.about(os=1) == 'win64':
    if int(mayaVersion[0]) < 2014:
        pluginName = 'softSelectionQuery_%s-%s.mll' % (mayaVersion[0], mayaVersion[1])
    else:
        pluginName = 'softSelectionQuery_%s-x64.mll' % mayaVersion[0]
elif cmd.about(os=1) == 'mac':
    pluginName = 'softSelectionQuery_%s.bundle' % mayaVersion[0]
else:
    cmd.error('Soft Cluster EX is available for 64bit version of Autodesk Maya 2011 or above under Windows 64bit and Mac OS X!')

if not cmd.pluginInfo(pluginName, q=True, l=True ):
    cmd.loadPlugin(pluginName)

# 
def repositionCluster(clusterHandle, position):
    cmd.xform(clusterHandle, a=True, ws=True, piv=(position[0], position[1], position[2]))
    clusterShape = cmd.listRelatives(clusterHandle, c=True, s=True)
    cmd.setAttr(clusterShape[0] + '.origin', position[0], position[1], position[2])

#
def createSoftCluster(excludeObjs=None, supportTypes=None):
    # determind select objects
    initSel = cmd.ls(sl=1, ap=1, st=1)
    firstSelObj, firstSelType = initSel[0], initSel[1]

    if firstSelType == 'transform':
        object = firstSelObj
    elif firstSelType in ['float3', 'double3']:
        object = cmd.listRelatives(cmd.listRelatives(p=True, f=1), p=True, f=1)[0]
    else:
        cmd.error('Selected objects Unsupported!')
        return

    # query manipulator's position
    cmd.setToolTo('Move')
    currentMoveMode = cmd.manipMoveContext('Move', q=True, m=True)
    cmd.manipMoveContext('Move', e=True, m=0)
    position = cmd.manipMoveContext('Move', q=True, p=True)
    cmd.manipMoveContext('Move', e=True, m=currentMoveMode)

    # query influenced elements and correspond weights
    elements = cmd.softSelectionQuery(cmp=1, exo=excludeObjs, t=supportTypes)
    weights = cmd.softSelectionQuery(w=1, exo=excludeObjs, t=supportTypes)

    # create cluster with elements and set weights
    try:
        clusterNode, clusterHandle = cmd.cluster(elements, n='%s_softCluster' % object.split('|')[-1])
    except:
        cmd.error('Selected objects Unsupported!')
        return

    for i in xrange(len(elements)):
        cmd.percent(clusterNode, elements[i], v=weights[i])

    repositionCluster(clusterHandle, position)

    return clusterNode, clusterHandle


########################################################################
class GUI(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(GUI, self).__init__()

        self.title = 'Soft Cluster EX'
        self.window = 'softClusterEXWin'
        self.supportTypeCB = []
        self.checkAllCB = ''
        self.excludeScrollList = ''
        self.falloffModeOption = ''
        self.excludeItems = ''
        
        self.initial()


    #----------------------------------------------------------------------
    def initial(self):
        """"""
        if cmd.window(self.window, ex=1):
            cmd.deleteUI(self.window)
        cmd.window(self.window, t='%s v%.2f' % (self.title, __VERSION__), s=0)
        
        # setup layout and ui elements
        cmd.columnLayout(adj=1, rowSpacing=4, columnAttach=('both', 4))

        cmd.separator( style='none' )

        cmd.columnLayout(adj=1, columnAlign='left')
        cmd.frameLayout( l='Options:', borderStyle='etchedIn', collapse=True, collapsable=True)
        cmd.frameLayout( l='Support Types:', borderStyle='etchedOut', collapse=False, collapsable=False)
        cmd.rowColumnLayout(numberOfRows=2)
        self.installSupportTypeCheckbox()
        cmd.setParent( '..' )
        cmd.setParent( '..' )

        self.installFalloffOption()
        cmd.setParent( '..' )
        cmd.setParent( '..' )

        cmd.frameLayout( l='Exclude Objects:', borderStyle='etchedIn', collapsable=True)
        self.installExcludeObjectsList()
        cmd.setParent( '..' )

        createBtn = cmd.button(l='Create', c=lambda *args: self.createSoftClusterCmd())
        cmd.separator( style='none' )
        cmd.setParent( '..' )
        cmd.showWindow(self.window)


    #----------------------------------------------------------------------
    def installSupportTypeCheckbox(self):
        """"""
        for typeName in __SUPPORTTYPE_LABEL__:
            self.supportTypeCB.append(cmd.checkBox(l='%s' % __SUPPORTTYPE_LABEL__[typeName]))
            cmd.checkBox(self.supportTypeCB[-1], e=1, cc=lambda *args: self.toggleAllCB())

        self.checkAllCB = cmd.checkBox( l='All', cc=lambda *args: self.toggleAllSupportTypesCB())

        self.setDefaultSupportTypes()

    #----------------------------------------------------------------------
    def installFalloffOption(self):
        """"""
        self.falloffModeOption = cmd.optionMenu(l='Falloff Mode:', cc=lambda *args: self.changeFalloffMode())
        cmd.menuItem( l='Volume' )
        cmd.menuItem( l='Surface' )
        cmd.menuItem( l='Global' )
        self.setDefaultFalloffMode()
    
    #----------------------------------------------------------------------
    def installExcludeObjectsList(self):
        """"""
        self.excludeScrollList = cmd.textScrollList(allowMultiSelection=True)
        cmd.popupMenu()
        cmd.menuItem(l='Add', c=lambda *args: self.addExcludeObjectsCmd())
        cmd.menuItem(l='Delete', c=lambda *args: self.deleteExcludeObjectsCmd())
        cmd.menuItem(l='Clear', c=lambda *args: self.clearExcludeObjectsCmd())        

    #----------------------------------------------------------------------
    def addExcludeObjectsCmd(self):
        """"""
        sel = cmd.ls(sl=1, ap=1)
        self.excludeItems = cmd.textScrollList(self.excludeScrollList, q=1, ai=1)

        for obj in sel:
            if not self.excludeItems:
                cmd.textScrollList(self.excludeScrollList, e=1, a=obj)
            elif not obj in self.excludeItems:
                cmd.textScrollList(self.excludeScrollList, e=1, a=obj)

    #----------------------------------------------------------------------
    def clearExcludeObjectsCmd(self):
        """"""
        cmd.textScrollList(self.excludeScrollList, e=1, ra=1)

    #----------------------------------------------------------------------
    def deleteExcludeObjectsCmd(self):
        """"""
        selItems = cmd.textScrollList(self.excludeScrollList, q=1, si=1)
        cmd.textScrollList(self.excludeScrollList, e=1, ri=selItems)

    #----------------------------------------------------------------------
    def createSoftClusterCmd(self):
        """"""
        self.excludeItems = cmd.textScrollList(self.excludeScrollList, q=1, ai=1)

        supportTypes = []
        for typeCB, typeName in zip(self.supportTypeCB, __SUPPORTTYPE_LABEL__):
            if cmd.checkBox(typeCB, q=1, v=1):
                supportTypes.append(typeName)

        if not supportTypes:
            cmd.error('Please check at least one support type!')
        
        clusterNode, clusterHandle = createSoftCluster(self.excludeItems, supportTypes)
        return clusterNode, clusterHandle

    #----------------------------------------------------------------------
    def changeFalloffMode(self):
        """"""
        selIndex = cmd.optionMenu(self.falloffModeOption, q=1, sl=1) - 1
        cmd.softSelect(ssf=selIndex)

    #----------------------------------------------------------------------
    def setDefaultFalloffMode(self):
        """"""
        cmd.optionMenu(self.falloffModeOption, e=1, sl=2)
        cmd.softSelect(ssf=1)

    #----------------------------------------------------------------------
    def setDefaultSupportTypes(self):
        """"""
        for typeCB in self.supportTypeCB:
            cmd.checkBox(typeCB, e=1, v=1)

        cmd.checkBox(self.checkAllCB, e=1, v=1)

    #----------------------------------------------------------------------
    def toggleAllSupportTypesCB(self):
        """"""
        checkAll = cmd.checkBox(self.checkAllCB, q=1, v=1)
        for typeCB in self.supportTypeCB:
            cmd.checkBox(typeCB, e=1, v=checkAll)

    #----------------------------------------------------------------------
    def toggleAllCB(self):
        """"""
        enableAll = True
        for typeCB in self.supportTypeCB:
            if not cmd.checkBox(typeCB, q=1, v=1):
                enableAll = False
                break

        cmd.checkBox(self.checkAllCB, e=1, v=enableAll)