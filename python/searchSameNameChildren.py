#-*- coding: euc-kr -*-

import maya.cmds as cmds

def findItem(selObj=None): #---------------------- Main Def ------------------------------
    sceneObjList = cmds.ls()                 #�� �� �����ϴ� ������Ʈ���� ���� �̸��� �����ϴ�
    sameNameList = []                        #������Ʈ���� Ǯ�佺 �̸��� ��½����ݴϴ�.
    targetNameList = []                      #Ư�� ������Ʈ���� ����Ʈ�� selObj �׸� �־��ְ�
    for i in sceneObjList:                   #Ư�� ������Ʈ�� ����Ʈ���� ������ �̸����� ������
        if len(i.split('|')) > 1:            #�� �̸����� Ǯ�н��� ��½����ݴϴ�.
            sameNameList.append(i)
    
    if selObj != None:
        for target in selObj:
            getOlny = target.split('|')
            onlyName = getOlny[len(getOlny)-1]
            targetNameList.append(onlyName)
        
        currentList = []
        targetNameList = list(set(targetNameList))
        for targetName in targetNameList:
            for sameName in sameNameList:
                getOnly = sameName.split('|')
                onlyName = getOnly[len(getOnly)-1]
                if onlyName == targetName:
                    currentList.append(sameName)
        return currentList
    else: 
        return sameNameList#-------------------------------- End Main Def --------------------------------
        
def quickNamingDef(selectItem,name,startNum,interval):#---------------------- Sub Def ------------------------------
    list_temp = []                                    # ������Ʈ�� �ڽ� ������Ʈ�� �̸��� unique�� �ƴҰ��
    list_temp.extend(selectItem)                      # �θ��̸��� rename�ҽÿ� �ڽ��� �̸����� �ٲ�� ��찡 �ֱ⶧����
    list_temp.sort()                                  # ������ ������Ʈ ������� �������� �ϰ� �Ǹ� ������ �߻��� �� �ֽ��ϴ�.
    list_temp.reverse()                               # �׷��⶧���� ���� ���������� �ִ� ������Ʈ���� ������� �������ؾ��մϴ�.
    list_count =[]                                    # �׷��鼭�� rename�ÿ� ������ ������� �ѹ����� �ϱ����ؼ�
    for i in list_temp:                               # �̿Ͱ��� ������� ��ũ������ �߽��ϴ�.
        for j in selectItem:
            if i == j:
                list_count.append(selectItem.index(j))
                break
    tempName_list = []
    tempName = ''
    for i in list_temp:
        tempName = "tempName_quickNaming"
        j = 0
        while cmds.ls(tempName+'*') == None:
            tempName = "tempName_quickNaming"+str(j)+"_"
            j += 1
        tempName_list.append( cmds.rename( i,'%s%s' % (tempName,list_temp.index(i))) )
    renameList = []
    for i in tempName_list:
        cuCount = list_count[tempName_list.index(i)]
        renameList.append(cmds.rename(i,'%s%s' % ( name , cuCount + startNum + cuCount*(interval-1))))#----------End Sub Def-------------
    renameList.sort()
    return renameList

class surchSameName_gui:#----------------------------- Main GUI---------------------------------------------
    def __init__(self):
        if cmds.window('surchingSameName_window',exists=1):
            cmds.deleteUI('surchingSameName_window',wnd=1)
        cmds.window('surchingSameName_window', title='Surch Same Name Children',wh=[300,100])
        cmds.showWindow('surchingSameName_window')
        self.topLayout = cmds.formLayout('ssn_top',nd=100)
        self.row1 = cmds.rowColumnLayout('row1',nc=1,w=170)
        self.findAll = cmds.button(h=26,l='Surch All',c=self.findAllCmd ); cmds.text(l='',h=5)
        self.findSelection = cmds.button(h=26, l='Surch Selection',c=self.findSelectionCmd ); cmds.text(l='',h=5)
        self.appendSelection = cmds.button(h=26, l='Append Selection', c=self.appendSelectionCmd ); cmds.text( l='',h=5)
        self.checkList = cmds.button(h=26, l='Check Selected Item In List', c=self.checkListCmd ); cmds.text( l='',h=5)
        self.checkListText = cmds.text( l ='' ,h=25,bgc=[.2,.2,.2]); cmds.text( l='',h=5)
        self.loadHierarchy = cmds.button(h=26, l='Load Hierarchy', c=self.loadHierCmd )
        cmds.setParent(self.topLayout)
        cmds.scrollLayout('scroll1')
        cmds.rowColumnLayout( nc=1, w=140)
        cmds.text( l = '  Top Unique Name:', al = 'left' ,h=25)
        self.topParent = cmds.text( l ='', al = 'left' ,bgc = [.5,.5,.5] )
        cmds.text( l = '  Current Name:' , al='left' ,h=25)
        self.cuSelection = cmds.text( l='', al = 'left' ,bgc = [.5,.5,.5] )
        cmds.setParent(self.topLayout)
        self.rename = cmds.rowColumnLayout(nc=1,cw=[(1,170)], vis = 1, h = 80)
        cmds.text( l = '  rename:', al= 'left', h=24)
        self.rename_tf = cmds.textField( h=24 )
        cmds.button(l = 'rename', c=self.renameButtonCmd, h=24)
        cmds.setParent(self.topLayout)
        
        self.textList = cmds.textScrollList('ssnc_scl',ams=1,sc=self.selectedCmd ); self.selectList = []#------����Ʈ���� ������ ������� 
        self.popup = cmds.popupMenu()                                                                   #      scene������ �����ϱ����� ����Ʈ�Դϴ�.
        self.menuitem = cmds.menuItem( l = '                 ', c= self.loadRename )
        
        cmds.formLayout('ssn_top',e=1,
                af=[('row1','top',5),('row1','left',5),('ssnc_scl','right',5),('ssnc_scl','top',5),('ssnc_scl','bottom',5),
                    ('scroll1','left',5),(self.rename,'left',5),(self.rename,'bottom',5)],
                ac=[('ssnc_scl','left',5,'row1'),
                    ('scroll1','top',5,'row1'),('scroll1','right',5,'ssnc_scl'),
                    ('scroll1','bottom',5,self.rename),(self.rename,'right',5,'ssnc_scl')] )
        cmds.window('surchingSameName_window',e=1,wh=(470, 390))
    
    def findAllCmd(self,*args):
        self.applyItem( findItem() )
        
    def findSelectionCmd(self,*args):
        self.applyItem( findItem( cmds.ls(sl=1) ) )
        self.selList_inSel()
                         
    def appendSelectionCmd(self,*args):
        self.applyItem( findItem( cmds.ls(sl=1) ),1 )
        self.selList_inSel()
                
    def applyItem( self, itemList ,add=False):
        if add == False:
            cmds.textScrollList( self.textList,e=1,ra=1)
            for i in itemList:
                cmds.textScrollList( self.textList,e=1,append = i )
        else:
            for i in itemList:
                allItem = cmds.textScrollList( self.textList,q=1,ai=1 )
                appendAble = True
                if allItem:
                    for j in allItem:
                        if i == j:
                            appendAble = False
                if appendAble:
                    cmds.textScrollList( self.textList,e=1,append = i )
    
    def selList_inSel(self):
        selObj = cmds.ls(sl=1)
        allItem = cmds.textScrollList( self.textList,q=1,ai=1)
        cmds.textScrollList( self.textList,e=1,da=1)
        if allItem:
            for i in allItem:
                for j in selObj:
                    if i == j:cmds.textScrollList( self.textList,e=1,si=j)
    
    def checkListCmd(self, *args):
        selObj = cmds.ls(sl=1);
        inList = cmds.textScrollList(self.textList,q=1,ai=1)
        cmds.textScrollList(self.textList,e=1,da=1)
        matchList = []; unMatchList = selObj
        if inList:
            for i in inList:
                for j in selObj:
                    if i == j:cmds.textScrollList(self.textList,e=1,si=j); matchList.append(j)
        for i in matchList:
            unMatchList.remove(i)
                
        if matchList:
            if unMatchList:cmds.select(unMatchList,d=1)
            cmds.text(self.checkListText,e=1, l='%s Item In List' % len(matchList) )
        else:
            cmds.text(self.checkListText,e=1, l='No Item In List')
    
    def loadHierCmd(self, *args):
        selObj = cmds.ls(sl=1)[0]
        cmds.select(selObj); cmds.select(hi=1)
        selObjs = cmds.ls(sl=1)
        cmds.textScrollList(self.textList,e=1,ra=1)
        for i in selObjs:
            cmds.textScrollList(self.textList,e=1,append=i)
            cmds.textScrollList(self.textList,e=1,si=i)

    def renameButtonCmd(self,*args):
        allList = cmds.textScrollList(self.textList,q=1,ai=1)
        selectItem = cmds.textScrollList(self.textList,q=1,si=1)[0]
        self.renameText = cmds.textField(self.rename_tf,q=1,tx=1)
        findExists = findItem([self.renameText])
        findExists.extend(cmds.ls(self.renameText))
        if findExists:
            self.findExsitsWindow = cmds.window()
            cmds.showWindow(self.findExsitsWindow)
            cmds.rowColumnLayout(nc=1)
            cmds.text(l = '"%s"�� �̹� �����ϴ� �̸��Դϴ�. \n ����Ͻðڽ��ϱ�?' % str(self.renameText) )
            cmds.rowColumnLayout(nc=2)
            cmds.button(l='Apply',c=self.applyFindExWindow);cmds.button(l='Close',c=self.closeFindExWindow)
            cmds.window(self.findExsitsWindow,e=1,wh=(10,10),rtf=1)
        else:
            if self.renameText != '':
                allItem = cmds.textScrollList(self.textList,q=1,ai=1)
                cmds.select(allItem)
                renamedText = cmds.rename(selectItem, self.renameText)
                selectTemp = cmds.ls(sl=1)
                cmds.textScrollList(self.textList,e=1,ra=1)
                for i in selectTemp:
                    cmds.textScrollList(self.textList,e=1,append=i)
                cmds.select(cl=1)
                for i in range(len(allItem)):
                    if allItem[i] != selectTemp[i]:
                        cmds.textScrollList(self.textList,e=1,si=selectTemp[i])
                cmds.select(self.renameText)
    def applyFindExWindow(self,*args):
        allList = cmds.textScrollList(self.textList,q=1,ai=1)
        selItem = cmds.ls(sl=1)[0]
        cmds.select(allList)
        cuItem = cmds.rename(selItem,self.renameText)
        selectTemp = cmds.ls(sl=1)
        cmds.textScrollList(self.textList,e=1,ra=1)
        for i in selectTemp:
            cmds.textScrollList(self.textList,e=1,append=i )
        for i in range(len(allList)):
            if allList[i] != selectTemp[i]: cmds.textScrollList(self.textList,e=1,si=selectTemp[i] )
        cmds.select(cuItem)
        cmds.deleteUI(self.findExsitsWindow, wnd=1)
    def closeFindExWindow(self,*args):
        cmds.deleteUI(self.findExsitsWindow, wnd=1)
              
    def selectedCmd(self,*args):
        beforeList = [] #--------------------------------------------------------------------------------------------
        beforeList.extend(self.selectList); self.selectList = []      #����Ʈ���� ������ ������� scene�󿡼��� ������ �ϱ����ؼ�
        newList = cmds.textScrollList(self.textList,q=1,si=1)         #�� ������ ������ ���ƽ��ϴ�.
        tempList = []
        if beforeList: 
            for i in beforeList:
                for j in newList:
                    if j == i: tempList.append(j)
            newObjectList = []
            for i in newList:
                if tempList.count(i)==0: newObjectList.append(i)
            tempList += newObjectList
            self.selectList += tempList#------------------------------------------------------------------------------
            cmds.select(self.selectList)
        else:cmds.select(newList); self.selectList+=newList
        topObjList = []
        cuObjList = []
        for obj in self.selectList:
            splitObj = obj.split('|')
            topObjList.append( splitObj[0] )
            cuObjList.append( splitObj[ len(splitObj)-1 ] )
        topText = '  ' + '\n  '.join(topObjList)
        cuText = '  ' + '\n  '.join(cuObjList)
        cmds.text(self.topParent,e=1,l=topText)
        cmds.text(self.cuSelection,e=1,l=cuText)
        if len(self.selectList) == 1: 
            cmds.rowColumnLayout(self.rename, e=1, vis=1, h = 80)
            cmds.menuItem(self.menuitem,e=1,l='                 ')
        else: 
            cmds.rowColumnLayout(self.rename, e=1, vis=0, h = 1)
            cmds.menuItem(self.menuitem,e=1,l='Load Quick Naming')
        
    def loadRename(self, *args):
        if cmds.menuItem(self.menuitem,q=1,l=1) == 'Load Quick Naming':
            self.sub2 = quickNaming_gui()
        else:
            cmds.textScrollList(self.textList, e=1, ra=1) #------------------------------------------End Main GUI------------------
        
surchSameName = surchSameName_gui()
class quickNaming_gui():#----------------------------- Sub GUI---------------------------------------------
    def __init__(self):
        if (cmds.window('quick_naming_mel',exists = 1)):
            cmds.deleteUI('quick_naming_mel')
    
        self.window = cmds.window('quick_naming_mel',title = 'Quick Nameing', wh = (300,100), rtf = 1)
        cmds.showWindow('quick_naming_mel')
        self.topLayOut = cmds.columnLayout()
        
        cmds.rowColumnLayout(nc = 2, cw = [(1,100),(2,200)])
        cmds.text(l = '    Name Main  :',h = 25)
        self.textF = cmds.textField()
        cmds.setParent(self.topLayOut)
        cmds.text(l = '' , h = 5)
        
        cmds.rowColumnLayout(nc = 3, cw = [(1,30),(2,160),(3,50)])
        cmds.text(l = ' ')
        self.cb_Start = cmds.checkBox(l = 'Edit Start Number', v = 0,
             onc = self.cb_startOn_commemd, ofc = self.cb_startOff_commemd )
        self.intF_start = cmds.intField( en = 0, v = 0)
        cmds.text(l = ' ')
        self.cb_interval = cmds.checkBox(l = 'Edit Interval', v = 0 ,
            onc = self.cb_intervalOn_commemd, ofc = self.cb_intervalOff_commemd )
        self.intF_interval = cmds.intField( en = 0, v = 1,minValue = 1)
        cmds.setParent(self.topLayOut)
        cmds.text(l = '', h = 5)
        
        cmds.rowColumnLayout(nc = 3, cw = [(1,150),(2,150)])
        cmds.button(l = 'Apply', h = 25, 
                c =self.main_commend )
        cmds.button(l = 'Close',h = 25, c =self.delUI)
        cmds.window(self.window, e=1, wh = (304,108) )
    
    def cb_startOn_commemd(self,*args):
        cmds.intField(self.intF_start, e = 1, en = 1)
        
    def cb_startOff_commemd(self,*args):
        cmds.intField(self.intF_start,e = 1, en = 0, v=0 )
   
    def cb_intervalOn_commemd(self,*args):
        cmds.intField(self.intF_interval, e = 1, en = 1)
    
    def cb_intervalOff_commemd(self,*args):
        cmds.intField(self.intF_interval, e = 1, en = 0, v=0 )
            
    def main_commend(self,*args):
        selectItem = cmds.ls(sl=1)
        name = cmds.textField(self.textF,q=1,tx=1)
        startNum = cmds.intField(self.intF_start,q=1,v=1)
        interval = cmds.intField(self.intF_interval,q=1,v=1)
        allItem = cmds.textScrollList('ssnc_scl', q=1, ai=1)
        cmds.select(allItem)
        renameItem = quickNamingDef(selectItem,name,startNum,interval)
        selectTemp = cmds.ls(sl=1)
        cmds.textScrollList('ssnc_scl', e=1, ra=1)
        for i in selectTemp:
            cmds.textScrollList('ssnc_scl',e=1,append=i )
        for i in range(len(allItem)):
            if allItem[i] != selectTemp[i]:cmds.textScrollList('ssnc_scl',e=1,si=selectTemp[i] )
        cmds.select(renameItem)
        cmds.deleteUI(self.window, wnd=1)
    
    def delUI(self,*args): cmds.deleteUI(self.window,wnd=1)#---------------End Sub GUI----------------------------