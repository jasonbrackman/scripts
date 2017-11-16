#-*- coding: euc-kr -*-

import maya.cmds as cmds

#======================================== 함수 설정 =======================================================

def objTOI_commendString():
    cmdString  = 'main_csoc(cmds.textField("objTOI_crvName",q=1,tx=1),'
    cmdString += 'cmds.intField( "objToI_if0",q=1,v=1),'
    cmdString += 'cmds.intField( "objToI_if1",q=1,v=1),'
    cmdString += 'cmds.checkBox("objToI_cb0",q=1,v=1),'
    cmdString += 'cmds.checkBox("objToI_cb1",q=1,v=1),'
    cmdString += 'cmds.checkBox("objToI_cb2",q=1,v=1),'
    cmdString += 'cmds.frameLayout("objToI_fl",q=1,cl=1),'
    cmdString += 'cmds.optionMenuGrp("objToI_omG0",q=1,sl=1),'
    cmdString += 'cmds.optionMenuGrp("objToI_omG1",q=1,sl=1),'
    cmdString += 'cmds.textField("objToI_tf0",q=1,tx=1),'
    cmdString += 'cmds.textField("objToI_tf1",q=1,tx=1),'
    cmdString += 'cmds.intFieldGrp("objToI_ifG0",q=1,v=1),'
    cmdString += 'cmds.intFieldGrp("objToI_ifG1",q=1,v=1),'
    cmdString += 'cmds.intFieldGrp("objToI_ifG2",q=1,v=1))'
    return cmdString

# Rotate Constrint Modify0
def rotateConstraint_modify0(*objects,**option):
    conObj = ''; aimObj = ''; #---------------------------------------------------------------------------
    aimType = ''; wut = 'vector'; wuo = ''; name = '' #    옵션 선언
    aim = [1,0,0]; u = [0,1,0]; wu = [0,1,0]#------------------------------------------------------------
    
    if len(objects) == 0: #------------------------------------------------------------------------
        conObj = cmds.ls(sl=1,tr=1)[0]
        aimObj = cmds.ls(sl=1,tr=1)[1] #        에임 오브젝트와 통제할 오브젝트를 변수에 저장
    else:
        conObj = objects[0]; aimObj = objects[1] #----------------------------------------------------
    for i in option: #---------------------------------------------------------------------------------------------------
        optionType = i; val = option[i]; 
        if optionType == 'aim' or optionType == 'aimVector':
            aim[0] = float(val[0]); aim[1] = float(val[1]); aim[2] = float(val[2])
        if optionType == 'u' or optionType == 'upVector':
            u[0] = float(val[0]); u[1] = float(val[1]); u[2] = float(val[2])                      #각종 옵션값을 사전에서 불러온다
        if optionType == 'wu' or optionType == 'worldUpVector':
            wu[0] = float(val[0]); wu[1] = float(val[1]); wu[2] = float(val[2])
        if optionType == 'atp' or optionType == 'aimType': aimType = val
        if optionType == 'wut' or optionType == 'worldUpType':wut = val;
        if optionType == 'wuo' or optionType == 'worldUpObject':wuo = val
        if optionType == 'n' or optionType == 'name': name = val#--------------------------------------------------------
    
    constraint = ''#------------------------------------------------------------------------------------------------
    if aimType == 'curvetangent':
        if wut == '' or wut == 'vector':
            constraint = cmds.tangentConstraint(conObj,aimObj,aim=aim,u=u)[0]                     #컨스트레인
        elif wut == 'object' or wut == 'objectrotation':
            constraint = cmds.tangentConstraint(conObj,aimObj,aim=aim,u=u,wu=wu,wut=wut,wuo=wuo)[0]
    else:
        if wut == '' or wut == 'vector':
            constraint = cmds.aimConstraint(conObj,aimObj,aim=aim,u=u)[0]
        elif wut == 'object' or wut == 'objectrotation':
            constraint = cmds.aimConstraint(conObj,aimObj,aim=aim,u=u,wu=wu,wut=wut,wuo=wuo)[0]#-----------------------
            
    return constraint
    
# Closist Position Info
def closist_position_info(curveName,selObj,divide,surchCount):
    import maya.mel as mel
    curveInfoL = []
    for i in selObj:
        objG = cmds.group(n=i+'_p',em=1)
        cInfo = cmds.createNode('pointOnCurveInfo', n=i+'_cInfo'); cmds.setAttr(cInfo+'.top', 1)
        cmds.connectAttr(cmds.listRelatives(curveName,c=1)[0]+'.worldSpace[0]',cInfo+'.inputCurve')
        pos0 = cmds.xform(i,q=1,piv=1,ws=1)[:3]
        k=0.0; nr = 1;
        while nr <= surchCount:
            lengthL = []
            for j in range(divide):
              cmds.setAttr(cInfo+'.parameter',k+((1.0/divide)**nr)/2 + j*(1.0/divide)**nr )
              infoPos = cmds.getAttr(cInfo+'.position')[0]
              lengthL.append(mel.eval('mag(<<%s,%s,%s>>-<<%s,%s,%s>>)' %(pos0[0],pos0[1],pos0[2],infoPos[0],infoPos[1],infoPos[2]) ) )
            shortistIndex = 0
            for j in range(1,divide):
              if lengthL[j] <= lengthL[shortistIndex]:
                 shortistIndex = j;
            k =  k + shortistIndex*(1.0/divide)**nr;
            nr += 1
        cmds.setAttr(cInfo+'.parameter',k+((1.0/divide)**nr)/2 );
        curveInfoL.append(cInfo) 
    return curveInfoL
    
#Main
def main_csoc(curveName,*others):  
    divide = others[0]; count = others[1]
    keepPos = others[2]; deleteCon = others[3]
    keepOrient = others[4]; orientConOn = others[5]
    aimtype = ''; uptype = ''
    if others[6] == 1: aimtype = 'curvetangent'
    else: aimtype = 'object'
    if others[7] == 1: uptype = 'vector'
    elif others[7] == 2: uptype = 'object'
    else : uptype = 'objectrotation'
    aimObj = others[8]; upObj = others[9]
    aim = others[10]; up = others[11]; wu = others[12]
    
    obj_p = []
    selObj = cmds.ls(sl=1)
    infoList = closist_position_info(curveName,selObj,divide,count)
    for i in range(len(infoList)):
        obj_p.append( cmds.group(em=1,n = selObj[i]+'_p') )
        cmds.connectAttr(infoList[i]+'.position', obj_p[i]+'.translate')
    if orientConOn == 0:
      for i in range(len(infoList)):
        constraint = rotateConstraint_modify0(aimObj,obj_p[i],aim=aim,u=up,wu=wu,atp=aimtype,wut=uptype,wuo=upObj)
        if deleteCon == 1: cmds.delete(constraint)
    for i in range(len(infoList)):
        cmds.parent(selObj[i],obj_p[i])
        if keepPos != 1: cmds.move(0,0,0,selObj[i],ls=1)
        if keepOrient != 1 and orientConOn == 0: cmds.rotate(0,0,0,selObj[i],os=1)
        if not keepOrient and cmds.objectType(selObj[i]) =='joint':
            cmds.setAttr( selObj[i] +'.jox', 0 )
            cmds.setAttr( selObj[i] +'.joy', 0 )
            cmds.setAttr( selObj[i] +'.joz', 0 )
    if deleteCon == 1: cmds.delete(infoList)
        
#========================================= 윈도우 설정 ===================================================

if (cmds.window('ObjectToCurveInfo', ex=1)): #-----------------------------------------------------------
    cmds.deleteUI('ObjectToCurveInfo', wnd=1 )
cmds.window('ObjectToCurveInfo', title='Connect Selected Object to Curve',      #윈도우 생성
widthHeight=(352, 209), rtf=1 )
cmds.showWindow('ObjectToCurveInfo')                                           
cmds.window('ObjectToCurveInfo',e=1,widthHeight=(352, 209),s=0)#-----------------------------------------

cmds.columnLayout("objToI_top")#-------------------------------------칼럼레이아웃 생성
cmds.text(l='', h=10)#--------------------------------------------------------------

cmds.rowColumnLayout( nc = 2, cw = [(1,120),(2,140)] )#-------------------------------------------------------------------------
cmds.text( l='Target Curve :')
cmds.textField("objTOI_crvName", h=23)
cmds.popupMenu( button=3 )  #---------pop up                         #커브의 이름을 설정
def txQ():
    selObj = cmds.ls(sl=1)
    for obj in selObj:
        if cmds.objectType(cmds.listRelatives(obj,s=1)[0])=="nurbsCurve":
            return obj
cmds.menuItem( l='Load Selected Curve', c='cmds.textField("objTOI_crvName",e=1,tx=txQ())' )
cmds.setParent("objToI_top")
cmds.text( l ='', h=10)#---------------------------------------------------------------------------------------------------------

cmds.rowColumnLayout( nc = 4, cw = [(1,70),(2,60),(3,90),(4,60)])#----------------------------------------------------------------
cmds.text( l ='Divide :')
cmds.intField( "objToI_if0", v=10, min=2, max=100,cc='dValue = cmds.intField( "objToI_if0",q=1,v=1);cValue = cmds.intField( "objToI_if1",q=1,v=1);cmds.text("objTOI_tx0",e=1,l=str(dValue));cmds.text("objTOI_tx1",e=1,l=str(dValue**cValue))' )
cmds.text( l ='Surch Count :')                                    #커브인포 위치의 샘플링 분할수, 분할횟수를 설정하는 텝 설정
cmds.intField( "objToI_if1", v=5, min=1, max=100, cc='dValue = cmds.intField( "objToI_if0",q=1,v=1);cValue = cmds.intField( "objToI_if1",q=1,v=1);cmds.text("objTOI_tx1",e=1,l=str(dValue**cValue))')
cmds.setParent("objToI_top")
cmds.text( l ='', h=10)#-----------------------------------------------------------------------------------------------------------

cmds.rowColumnLayout( nc = 4, cw = [(1,80),(2,40),(3,80),(4,60)])#----------------------------------------------------------------
cmds.text( l ='first Divide:',en=0,al='right' )
cmds.text("objTOI_tx0", l ='10',en=0)
cmds.text( l ='Surch Detail:',en=0,al='right' )                 #커브의 샘플링 분할수를 보여주고, 최종적으로 몇 번 분할한 효과를 보여주는지 보여주는 텝 설정
cmds.text("objTOI_tx1", l ='100000',en=0)
cmds.setParent("objToI_top")
cmds.text( l ='', h=10)#-----------------------------------------------------------------------------------------------------------

cmds.frameLayout("objToI_fl",l="Orient Constraint : (Click To Turn On Constraint)",w=350,cll=1,cl=1, #-----------------------------------------------
     cc ='cmds.frameLayout("objToI_fl",e=1,l="Orient Constraint : OFF");cmds.window("ObjectToCurveInfo",e=1,w=352,h=209)',  #컨스트레인 텝 설정 시작
     ec ='cmds.frameLayout("objToI_fl",e=1,l="Orient Constraint : ON");cmds.window("ObjectToCurveInfo",e=1,w=352,h=346)')
cmds.text( l ='', h=3 )
cmds.rowColumnLayout("objToI_rcl0", nc =2, cw = [(1,215),(2,120)] )
cmds.optionMenuGrp("objToI_omG0", label=' Aim Type : ', cw=[(1, 90),(2,50)], cal=(1,'right') )
cmds.menuItem( label='Curve Tangent', c='cmds.textField("objToI_tf0", e=1,en=1)')
cmds.menuItem( label='Object' )
cmds.textField("objToI_tf0",tx="Aim Object", h=23)
cmds.popupMenu( button=3 , #---------pop up
     pmc='if cmds.optionMenuGrp("objToI_omG0",q=1,sl=1) ==1:cmds.menuItem("objToI_mi0",e=1,l="Load Selected Curve")\nelse:cmds.menuItem("objToI_mi0",e=1,l="Load Selected Object")') 
def loadSelect():return cmds.ls(sl=1,tr=1)[0]
cmds.menuItem("objToI_mi0", l='Load Selected Object', c='if cmds.optionMenuGrp("objToI_omG0",q=1,sl=1)==1:cmds.textField("objToI_tf0",e=1,tx=txQ())\nelse:cmds.textField("objToI_tf0",e=1,tx=loadSelect())')
cmds.optionMenuGrp("objToI_omG1", label=' World Up Type : ', cw=[(1, 90),(2,50)], cal=(1,'right'),
     cc='if cmds.optionMenuGrp("objToI_omG1",q=1,sl=1) != 1:cmds.textField("objToI_tf1",e=1,en=1)\nelse:cmds.textField("objToI_tf1",e=1,en=0)')
cmds.menuItem( label='Vector' )
cmds.menuItem( label='Object Up', c='cmds.textField("objToI_tf0", e=1,en=1)')
cmds.menuItem( label='Object Rotation Up' )
cmds.textField("objToI_tf1",tx="World Up Object", h=23,en=0)  
cmds.popupMenu( button=3 , #---------pop up
     pmc='cmds.menuItem("objToI_mi1",e=1,l="Load Selected Object")') 
cmds.menuItem("objToI_mi1", l='Load Selected Object', c='cmds.textField("objToI_tf1",e=1,tx=loadSelect())' )
cmds.setParent("objToI_fl")

cmds.rowColumnLayout("objToI_rcl1", nc =1, cw = (1,340))
cmds.intFieldGrp("objToI_ifG0", nf=3, l='Aim : ', v1 = 1,v2 = 0, v3 = 0,cal=[(1,'right')],cw=[(1,70)])
cmds.intFieldGrp("objToI_ifG1", nf=3, l='Up : ', v1 = 0,v2 = 1, v3 = 0,cal=[(1,'right')],cw=[(1,70)])
cmds.intFieldGrp("objToI_ifG2", nf=3, l='World Up : ', v1 = 0,v2 = 1, v3 = 0,cal=[(1,'right')],cw=[(1,70)])
cmds.setParent("objToI_fl")

cmds.rowColumnLayout(nc =2, cw = [(1,20),(2,200)])
cmds.text(l='')
cmds.checkBox("objToI_cb2", l='Keep Original Orientation')
cmds.text( l ='', h=5)
cmds.setParent("objToI_top")                                         # 컨스트레인 텝 설정 끝
cmds.text( l ='', h=5)#--------------------------------------------------------------------------------------------------------------

cmds.rowColumnLayout( nc =3, cw = [(1,20),(2,150),(3,150)] )#------------------------------------------------------------------------
cmds.text( l ='')
cmds.checkBox("objToI_cb0", l='Keep Original Tanslation')                                               #기타 옵션들 텝 설정
cmds.checkBox("objToI_cb1", l='Delete Constraint')
cmds.setParent("objToI_top")
cmds.text( l ='', h=5)#---------------------------------------------------------------------------------------------------------------

cmds.rowColumnLayout( nc =2, cw = [(1,175),(2,175)] )#---------------------------------------------------------------------------------
cmds.button( l='Apply',c= objTOI_commendString() )                                              #실행 버튼과 종료버튼 설정
cmds.button( l='Close',c='cmds.deleteUI("Object_to_curve_info", wnd=1 )')#-------------------------------------------------------------