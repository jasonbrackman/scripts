#-*- coding: euc-kr -*-

import maya.cmds as cmds

#---------- window def--------------#
def autoSet_cmd():
    str0 = 'cmds.textField(makeAtna_txf1,e=1,tx=cmds.textField(makeAtna_txf0,q=1,tx=1)+"@_con");'
    str0 += 'cmds.textField(makeAtna_txf2,e=1,tx=cmds.textField(makeAtna_txf0,q=1,tx=1)+"@_info");'
    str0 += 'cmds.textField(makeAtna_txf3,e=1,tx=cmds.textField(makeAtna_txf0,q=1,tx=1)+"@_p")'
    return str0
    
def getAxis():
    rdc0 = cmds.radioCollection(makeAtna_rdc0, q=1, sl=1 )
    label0 = cmds.radioButton(rdc0, q=1, l=1 )
    label0_0 = label0.lower()

    rdc1 = cmds.radioCollection(makeAtna_rdc1, q=1, sl=1 )
    label1 = cmds.radioButton(rdc1, q=1, l=1 )
    label1_0 = label1.lower()
    label1_0 = label1_0.split()[0]
    
    outStr = label0_0+label1_0+'xyz'.replace(label0_0[1]+label1_0,'')
    return outStr

def mainNameQ():
    return cmds.textField(makeAtna_txf0,q=1,tx=1)

def methodQ():
    return cmds.radioButton(makeAtna_radBMeh,q=1,sl=1)

def joint_numberQ():
    return cmds.intField(makeAtna_apIf,q=1,v=1)
  
#---------- window ------------#
if (cmds.window('makeAnntena', ex=1)):
    cmds.deleteUI('makeAnntena', wnd=1 )
cmds.window('makeAnntena', title='Create Joint Based On Curve', widthHeight=(300, 55), rtf=1 )
makeAtn_colLay = cmds.columnLayout()
cmds.text( l='',h=10 )

cmds.rowColumnLayout( nc=3, cw=[(1,120),(2,150)] )
cmds.text( l='     Main Name :  ' ,al='right')
makeAtna_txf0 = cmds.textField(h=22,tx='antenna')
cmds.setParent(makeAtn_colLay)
cmds.text( l='', h=10 )

cmds.rowColumnLayout( nc=4, cw=[(1,120),(2,70),(3,70),(4,70)] )
cmds.text( l='     Aim : ' )
makeAtna_rdc0 = cmds.radioCollection()
makeAtna_X = cmds.radioButton( l=' X', 
    onc='cmds.radioButton(makeAtna_uX,e=1,vis=0);cmds.radioButton(makeAtna_uY,e=1,sl=1)', 
    ofc='cmds.radioButton(makeAtna_uX,e=1,vis=1);cmds.radioButton(makeAtna_uY,e=1,sl=1)', sl=1 )
makeAtna_Y = cmds.radioButton( l=' Y', 
    onc='cmds.radioButton(makeAtna_uY,e=1,vis=0);cmds.radioButton(makeAtna_uZ,e=1,sl=1)', 
    ofc='cmds.radioButton(makeAtna_uY,e=1,vis=1);cmds.radioButton(makeAtna_uZ,e=1,sl=1)' )
makeAtna_Z = cmds.radioButton( l=' Z', 
    onc='cmds.radioButton(makeAtna_uZ,e=1,vis=0);cmds.radioButton(makeAtna_uX,e=1,sl=1)', 
    ofc='cmds.radioButton(makeAtna_uZ,e=1,vis=1);cmds.radioButton(makeAtna_uX,e=1,sl=1)' )
    
cmds.text( l='' )
makeAtna_mX = cmds.radioButton( l='-X', 
    onc='cmds.radioButton(makeAtna_uX,e=1,vis=0);cmds.radioButton(makeAtna_uY,e=1,sl=1)', 
    ofc='cmds.radioButton(makeAtna_uX,e=1,vis=1);cmds.radioButton(makeAtna_uY,e=1,sl=1)' )
makeAtna_mY = cmds.radioButton( l='-Y', 
    onc='cmds.radioButton(makeAtna_uY,e=1,vis=0);cmds.radioButton(makeAtna_uZ,e=1,sl=1)', 
    ofc='cmds.radioButton(makeAtna_uY,e=1,vis=1);cmds.radioButton(makeAtna_uZ,e=1,sl=1)' )
makeAtna_mZ = cmds.radioButton( l='-Z', 
    onc='cmds.radioButton(makeAtna_uZ,e=1,vis=0);cmds.radioButton(makeAtna_uX,e=1,sl=1)', 
    ofc='cmds.radioButton(makeAtna_uZ,e=1,vis=1);cmds.radioButton(makeAtna_uX,e=1,sl=1)' )
cmds.setParent(makeAtn_colLay)

cmds.rowColumnLayout( nc=4, cw=[(1,120),(2,70),(3,70),(4,70)] )
cmds.text( l='     Up : ' )
makeAtna_rdc1 = cmds.radioCollection()
makeAtna_uX = cmds.radioButton( l=' X', vis=0 )
makeAtna_uY = cmds.radioButton( l=' Y', sl=1 )
makeAtna_uZ = cmds.radioButton( l=' Z' )
cmds.setParent( makeAtn_colLay )
cmds.text( l='', h=15 )

cmds.rowColumnLayout( nc=1, cw=[(1,390)] )
cmds.separator()
cmds.setParent( makeAtn_colLay )
cmds.text( l='', h=5 )

cmds.rowColumnLayout( nc=4, cw=[(1,120),(2,100),(3,100),(4,50)] )
cmds.text( l='   Joint Position Method : ' )
cmds.radioCollection()
makeAtna_radBMeh = cmds.radioButton( l=' To Cv Point', sl=1 )
cmds.radioButton( l='Average Point' ,
                  onc='cmds.intField(makeAtna_apIf,e=1,en=1)',
                  ofc='cmds.intField(makeAtna_apIf,e=1,en=0)' )
makeAtna_apIf = cmds.intField( en=0, v=10, min=2 )
cmds.setParent( makeAtn_colLay )
cmds.text( l='', h=15 )

cmds.rowColumnLayout( nc=2, cw=[(1,195),(2,195)] )
cmds.button( l='Create', h=25,
c='creat_anntena_base( cmds.ls(sl=1), mainNameQ(), getAxis(), methodQ(),joint_numberQ()); MakeAntenna_editMore() ' )
cmds.button( l='Close', h=25, c='cmds.deleteUI("makeAnntena", wnd=1 )' )

cmds.showWindow('makeAnntena')

#---------------window2 def----------------#
def MakeAntenna_editMore():
 
 if (cmds.window('antennaComplete', ex=1)):
     cmds.deleteUI('antennaComplete', wnd=1 )
 cmds.window('antennaComplete', title='Edit More', widthHeight=(300, 55), rtf=1 )
 atnaCmpl_colLay = cmds.columnLayout()
 cmds.text( l='' , h=8)
 cmds.rowColumnLayout( nc=2, cw=[(1,120),(2,200)] )
 cmds.text( l='     Number Of Joint :',al='left')
 edMore_isg = cmds.intSliderGrp( 'edMore_isg',f=1,v=len(MakeAtna_returnV[0][1]),min=2,max=20,fmn=2,fmx=100,
                    cw=[(1,50),(2,150)] )
 cmds.setParent(atnaCmpl_colLay)
 cmds.text( l='', h=5 )
 
 cmds.rowColumnLayout( nc=1, cw=[(1,390)] )
 cmds.separator()
 cmds.setParent(atnaCmpl_colLay)
 cmds.text( l='', h=5 )
 
 cmds.rowColumnLayout( nc=4, cw=[(1,100),(2,90),(3,90),(4,90)])
 cmds.text('   Add Attribute :', al='left')
 edMore_cb0 = cmds.checkBox('edMore_cb0', l='Sliding' )
 edMore_cb1 = cmds.checkBox('edMore_cb1', l='Length' )
 edMore_cb2 = cmds.checkBox('edMore_cb2', l='Twist' )
 cmds.setParent(atnaCmpl_colLay)
 cmds.text( l='', h=5 )
 
 cmds.rowColumnLayout( nc=4, cw=[(1,80),(2,80),(3,50),(4,120)])
 cmds.text( l='   Add Items  :', al='left' )
 cmds.checkBox( l='Controler', 
             onc='cmds.intField("atnaCmpl_numCIf",e=1,en=1,v=1);cmds.text("atnaCmpl_numCTx",e=1,en=1)',
             ofc='cmds.intField("atnaCmpl_numCIf",e=1,en=0,v=0);cmds.text("atnaCmpl_numCTx",e=1,en=0)' )
 atnaCmpl_numCIf = cmds.intField( 'atnaCmpl_numCIf',en=0, v=0 )
 atnaCmpl_numCTx = cmds.text('atnaCmpl_numCTx', l='  (Number Of Controler)', al='center', en=0 )
 cmds.setParent( atnaCmpl_colLay )
 cmds.text( l='', h=5 )
 
 cmds.rowColumnLayout( nc=4, cw=[(1,80),(2,80),(3,100),(4,110)] )
 cmds.text( l='' )
 cmds.checkBox( l='Hair System',
             onc='cmds.textField("atnaCmpl_hrTf",e=1,en=1,tx="New");cmds.text("atnaCmpl_hrTx",e=1,en=1)',
             ofc='cmds.textField("atnaCmpl_hrTf",e=1,en=0,tx="");cmds.text("atnaCmpl_hrTx",e=1,en=0)' )
 atnaCmpl_hrTf = cmds.textField( 'atnaCmpl_hrTf', en=0 )
 atnaCmpl_hrTx = cmds.text('atnaCmpl_hrTx', l='(hair System name)',en=0 )
 cmds.setParent( atnaCmpl_colLay )
 cmds.text( l='', h=10 )
 
 cmds.rowColumnLayout( nc=3, cw=[(1,135),(2,120),(3,135)] )
 cmds.button( l='Done', 
 c='completeAntenna(cmds.intSliderGrp("edMore_isg",q=1,v=1),cmds.intField("atnaCmpl_numCIf",q=1,v=1),cmds.textField("atnaCmpl_hrTf",q=1,tx=1),cmds.checkBox("edMore_cb0",q=1,v=1),cmds.checkBox("edMore_cb1",q=1,v=1),cmds.checkBox("edMore_cb2",q=1,v=1))')
 cmds.button( l='On Off Axis', c='turn_axis()')
 cmds.button( l='Close', c='cmds.deleteUI("antennaComplete", wnd=1 )' )
 
 cmds.showWindow('antennaComplete')

#------------- main def ---------------- #
MakeAtna_returnV = []

def creat_anntena_base( selObj, jnt_str, jntOri, jointMethod, num_of_jnt ):
 objectCondition = 0
 for i in range(len(MakeAtna_returnV)):
     del MakeAtna_returnV[0]
 for i in selObj:
     shape = cmds.listRelatives(i,s=1)
     for j in shape:
         if cmds.objectType(j) != 'nurbsCurve':
             objectCondition = 1

 if objectCondition == 1:
     cmds.warning('Select Only Curve Object')
 else:
     returnTotal = []
     for i in selObj:
         returni =[]
         jnt_main_name = jnt_str+str(selObj.index(i))
         info_name = jnt_str +str(selObj.index(i)) + '_info' 
         cmds.setAttr(i+'.visibility',0)
         
         i = cmds.rebuildCurve( i, ch=0, rpo=1, rt=3 ,end=1, kr=2, kcp=1, kep=0, kt=0, tol=0.01 )[0]
         rebuildBase = ''
         if jointMethod==1:
             rebuildBase = cmds.rebuildCurve( i, ch=0, rpo=0, rt=0 ,end=1, kr=2, kcp=1, kep=0, kt=0, d=1, tol=0.01 )[0]
             num_of_jnt = cmds.getAttr(rebuildBase+'.spans') + 1
         else:
             rebuildBase = cmds.rebuildCurve( i, ch=0, rpo=0, rt=0 ,end=1, kr=2, kcp=0, kep=0, kt=0, s=num_of_jnt-1, d=1, tol=0.01 )[0]
             cmds.delete(i)
             i = cmds.rebuildCurve( rebuildBase, ch=0, rpo=0, rt=0 ,end=1, kr=1, kcp=0, kep=0, kt=0, s=0, d=3, tol=0.01 )[0]
             cmds.setAttr( i+'.v', 0)
         returni.append([i])
         returni[0].append(rebuildBase)
                                          
         jntMainLst = []
         for j in range(num_of_jnt):
             cmds.select(d=1)
             jntMainLst.append( cmds.joint(n = (jnt_main_name+'_conJoint'+str(j))) )    
         returni.append(jntMainLst)
             
         xyzDic = { 'x' : [1,0,0], 'y' : [0,1,0], 'z' : [0,0,1] }
         
         aim =  xyzDic[ jntOri[1] ]
         up =  xyzDic[ jntOri[2] ] 
         
         if jntOri[0] == '-':
          for k in range(3):
             aim[k] = aim[k]*(-1)
         
         jntGrpLst = []
         infoLst = []
         crvShp = cmds.listRelatives( rebuildBase, s=1 )[0]
         posLst = []
         for j in jntMainLst:
             index = jntMainLst.index(j)
             j = cmds.group(em=1)
             jntGrpLst.append(j)
             cmds.parent( jntMainLst[index], j )
             info = cmds.createNode( 'pointOnCurveInfo', n=info_name+str(index) )
             infoLst.append(info)
             cmds.connectAttr( crvShp+'.worldSpace[0]', info+'.inputCurve' )
             cmds.connectAttr( info+'.position', j+'.translate' )
             cmds.setAttr( info+'.parameter', jntGrpLst.index(j) )
             posLst.append( cmds.xform(j,q=1,ws=1,piv=1)[:3] )
             jc = cmds.listRelatives( j, c=1, type='joint' )[0]
             if jointMethod == 0:
                  cmds.addAttr( jc, ln='infoPos', sn='ip', at='double', min=0, max=num_of_jnt-1 )
                  cmds.setAttr( jc+'.ip', e=1, k=1 )
                  cmds.setAttr( jc+'.ip', jntGrpLst.index(j) )
                  cmds.setAttr( info+'.parameter', jntGrpLst.index(j) )       
         returni.append(jntGrpLst)
         
         ep = ''
         if jointMethod == 0:
             ep = cmds.curve(ep=posLst)
             cmds.setAttr(ep+'.v',0)
             returni[0].append(ep)
             ep = cmds.rebuildCurve( ep, ch=0, rpo=1, rt=3 ,end=1, kr=2, kcp=1, kep=0, kt=0, tol=0.01 )[0]
             epShape= cmds.listRelatives(ep,s=1)[0]
             for j in infoLst:
                 cmds.connectAttr( epShape+'.worldSpace[0]', j+'.inputCurve',f=1 )
             clusterObj = []
             clusterObj.extend(jntMainLst)
             clusterObj.append(rebuildBase)
             cmds.skinCluster(clusterObj)
         else:
             clusterObj = []
             clusterObj.extend(jntMainLst)
             clusterObj.append(i)
             cmds.skinCluster(clusterObj)
                 
         if jointMethod == 0:
             cmds.tangentConstraint( ep, jntGrpLst[0], aim=aim, u=up, wu=up, wut='scene' )  
         else:
             cmds.tangentConstraint( rebuildBase, jntGrpLst[0], aim=aim, u=up, wu=up, wut='scene' )
                 
         for j in range(1,num_of_jnt):
             if jointMethod == 0:
                 cmds.tangentConstraint( ep, jntGrpLst[j], aim=aim, u=up, wu=up, wut='objectrotation', wuo=jntMainLst[j-1] )  
             else:
                 cmds.tangentConstraint( rebuildBase, jntGrpLst[j], aim=aim, u=up, wu=up, wut='objectrotation', wuo=jntMainLst[j-1] )
                     
         returni.append(infoLst)
         axis = [aim,up]
         returni.append(axis)
         for j in jntMainLst:
             cmds.setAttr( j+'.dla', 1 )
             cmds.setAttr( j+'.jox', 0 )
             cmds.setAttr( j+'.joy', 0 )
             cmds.setAttr( j+'.joz', 0 )
             cmds.setAttr( j+'.tx', lock=1 )
             cmds.setAttr( j+'.ty', lock=1 )
             cmds.setAttr( j+'.tz', lock=1 )
             cmds.setAttr( j+'.r'+jntOri[2], lock=1 )
             cmds.setAttr( j+'.r'+jntOri[3], lock=1 )
         
         
         
         #------------------ expression ----------------#
         if jointMethod == 0:
           cmds.addAttr(rebuildBase,ln='posShp',at='double')
           cmds.setAttr(rebuildBase+'.posShp',e=1,k=1)
           
           sliderAttr = rebuildBase+'.posShp'
         
           exString  = 'float $sRate;\n'
           exString += 'float $ep[];\n'
           exString += 'if (%s >= 0)\n' % sliderAttr
           exString += '{\n'
           exString += '$sRate=%s/%s+1;\n' % (sliderAttr,num_of_jnt)
         
           for j in range(num_of_jnt):
               exString += '$ep[%s]=pow((%s.infoPos/%s),$sRate);\n' % (j,returni[1][j],num_of_jnt-1)
           exString += '}\n'
           exString += 'else\n'
           exString += '{\n'
           exString += '$sRate=1-%s/%s;\n' % (sliderAttr,num_of_jnt)
           for j in range(num_of_jnt):
               exString += '$ep[%s]=1-pow(1-(%s.infoPos/%s),$sRate);\n' % (j,returni[1][j],num_of_jnt-1)
           exString += '}\n'
           for j in range(num_of_jnt):
               exString += '%s.parameter = linstep(0,1,$ep[%s])*%s;\n' % (returni[3][j],j,num_of_jnt-1)

           exName = i+'_jointPosShape'
           cmds.expression(name=exName,s=exString,ae=1,uc='all')
           returni.append(exName)
         
         returnTotal.append(returni)
 
 MakeAtna_returnV.extend(returnTotal)
 
#--------- hair system def
def createHair(hairShape):
    import maya.mel as mel
    if hairShape == '':  
      mel.eval('DynCreateHairMenu MayaWindow|mainHairMenu')
      mel.eval('HairAssignHairSystemMenu MayaWindow|mainHairMenu|hairAssignHairSystemItem')
      returnShape = mel.eval('assignNewHairSystem')
    else:
      returnShape = mel.eval('assignHairSystem %s' % hairShape)

#--------------- Main def2------------------#
completeList = []
def completeAntenna(num_jnt,num_ctr,hairSystem,sliding,length,twist):
  lenComplist = len(completeList)
  for i in range(lenComplist):
     del completeList[0]
  num_crv = len(MakeAtna_returnV) 
  method = ''
  createJntLst = []
    
  #------------------ Get Hair System Type
  hairSys_on = 0
  if hairSystem == 'New':
      hairSys_on = 1
  elif hairSystem == '':
      hairSys_on = 0
  else:
      hairSys_on = -1
      
  for i in cmds.ls(type='hairSystem'):
      if hairSystem == i or hairSystem == cmds.listRelatives(i,p=1)[0]:
          hairSys_on = 2


  if hairSys_on == -1:
    cmds.warning("'%s'는 존제하지 않는 Object입니다." % hairSystem)
  else:      
    
    for i in MakeAtna_returnV: #------choose method
        if len(i) == 6:
            cmds.delete(i[5])#----delete expression
            method = 'avp'
        else:
            method = 'cv'

    getPosShp = 0.0
    if method == 'avp':
       print MakeAtna_returnV[0][0][1], len(MakeAtna_returnV[0][1])
       getPosShp = cmds.getAttr(MakeAtna_returnV[0][0][1]+'.posShp')/len(MakeAtna_returnV[0][1])
       print getPosShp
    
    for i in MakeAtna_returnV:
        aim = i[4][0]
        up = i[4][1]
        mainName = i[1][0].partition('_')[0]
        #--------Set controler joint initial setting 
        for j in i[1]:   
            cmds.setAttr(j+'.tx',l=0)
            cmds.setAttr(j+'.ty',l=0)
            cmds.setAttr(j+'.tz',l=0)
            cmds.setAttr(j+'.rx',l=0)
            cmds.setAttr(j+'.ry',l=0)
            cmds.setAttr(j+'.rz',l=0)
            cmds.setAttr(j+'.dla',0)

            if method == 'avp':
                cmds.deleteAttr(j,at='ip')
            cmds.parent(j,w=1)
            
        for j in i[2]: 
            cmds.delete(j)  #----------------- Delete null group
        
        #----------Set constrainted orient to current orientation    
        for j in range(len(i[1])-1): 
            tempLoc = cmds.spaceLocator()[0]
            tempOri = cmds.orientConstraint(i[1][j],tempLoc)
            cmds.delete(tempOri)
            tempAim = cmds.aimConstraint(i[1][j+1],i[1][j],aim=aim,u=up,wu=up,wut='objectrotation',wuo=tempLoc)
            cmds.delete(tempAim,tempLoc)
            cmds.parent(i[1][j+1],i[1][j])
        
        ##-------- BindCurve And JointCurve Set
        attachJointCurve ='' 
        bindCurve =''
        posShp = 0.0
        conJoint = i[1]
        if method == 'avp':
            dupleObj = cmds.duplicate(i[0][1],n=mainName+'_bindCurve')[0]
            cmds.deleteAttr(dupleObj+'.posShp')
            posShp = cmds.getAttr(i[0][1]+'.posShp')
            attachJointCurve = cmds.rebuildCurve( dupleObj, n=mainName+'_jntAtCurve', ch=1, rpo=0, rt=0 ,end=0, kr=0, kcp=1, kep=0, kt=0, s=0, d=3, tol=0.01 )[0]
            cmds.delete(i[0][0],i[0][1],i[0][2])
            bindCurve = dupleObj
        else:
            dupleObj = cmds.duplicate(i[0][0],n=mainName+'_bindCurve')[0]
            spans = cmds.getAttr(cmds.listRelatives(dupleObj,s=1)[0]+'.spans')
            attachJointCurve = cmds.rebuildCurve( dupleObj, n=mainName+'_jntAtCurve', ch=1, rpo=0, rt=0 ,end=1, kr=0, kcp=0, kep=0, kt=0,s=spans*3, tol=0.01 )[0]
            cmds.delete(i[0][1],i[0][0])
            bindCurve = dupleObj
            
        #--------------- Create Normal Base for Normal Constraint       
        normalBase = cmds.polyPlane(w=1,h=1,sx=1,sy=1,n=mainName+'_normalBase')[0]
        for j in range(1,len(i[1])-1):
            cmds.polyExtrudeEdge(normalBase+'.e['+str(j*3)+']',lty=1)
        cmds.DeleteHistory(normalBase)
        
        def inr(a):
            return (a+1)%3
        def inrb(a):
            return (a+2)%3
        
        axisElse = [0,0,0]  #--------- Get Third Axis
        
        for j in range(3):
            if aim[j] == 1 and up[inr(j)] == 1:
                axisElse[inrb(j)] = 1;
            if aim[j] == 1 and up[inr(j)] == 0:
                axisElse[inr(j)] = -1;
            if aim[j] == -1 and up[inr(j)] == 0:
                axisElse[inr(j)] = 1;
            if aim[j] == -1 and up[inr(j)] == 1:
                axisElse[inrb(j)] = -1;
            print j,inr(j),inrb(j)
        print 'aim     :',aim
        print 'up      :',up
        print 'axisElse:',axisElse

        for j in range(len(i[1])):
            tmLoc = cmds.spaceLocator()
            cmds.parent(tmLoc,conJoint[j])
            cmds.move(axisElse[0],axisElse[1],axisElse[2],tmLoc,ls=1)
            locPos = cmds.xform(tmLoc,q=1,ws=1,piv=1)
            cmds.move(locPos[0],locPos[1],locPos[2],normalBase+'.vtx['+str(j*2+1)+']',ws=1)
            cmds.move(-axisElse[0],-axisElse[1],-axisElse[2],tmLoc,ls=1)
            locPos = cmds.xform(tmLoc,q=1,ws=1,piv=1)
            cmds.move(locPos[0],locPos[1],locPos[2],normalBase+'.vtx['+str(j*2)+']',ws=1)
            cmds.delete(tmLoc)
       
        bindObj = []
        bindObj.append(conJoint[0])
        bindObj.append(normalBase)
        cmds.skinCluster(bindObj)
        bindObj = []
        bindObj.append(conJoint[0])
        bindObj.append(bindCurve)
        cmds.skinCluster(bindObj)
        cmds.setAttr(bindCurve+'.v', 0)
        
        cmds.select(attachJointCurve)
        startHair = ''
        currentHair = ''
        restHair = ''
        if hairSys_on != 0:
          if hairSys_on == 1:
            beforeHair = cmds.ls(type='hairSystem')      
            createHair('')
            afterHair = cmds.ls(type='hairSystem')
            for k in beforeHair:
                afterHair.remove(k)
            hairSystem = afterHair[0]
            hairSys_on = 2
          elif hairSys_on == 2:
            createHair(hairSystem)
          cmds.select(attachJointCurve); import maya.mel as mel ;mel.eval('setSelectedHairCurves "start" "rest"')
          cmds.select(attachJointCurve); mel.eval('convertHairSelection "currentCurves"'); currentHair = cmds.ls(sl=1)[0]
          mel.eval('convertHairSelection "restCurves"'); restHair = cmds.ls(sl=1)[0]
          mel.eval('convertHairSelection "startCurves"'); startHair = cmds.ls(sl=1)[0]; attachJointCurve = currentHair
          mel.eval('displayHairCurves "all" 1'); blendShape1 = cmds.blendShape(startHair,restHair,tc=0)[0]
          cmds.setAttr(blendShape1+'.'+startHair,1)
          
        #---------------- Create Current Joint    
        
        jntPntL = []; jntPntChildL = []; subLocL = []; jntL = []; jntGL = []
        infoL = []; pntInfoL = []; pntRotL = []
        if hairSys_on == 0:
          for j in range(num_jnt):
            cmds.select(d=1)
            jnt = cmds.joint(rad = 2, n=mainName+'_cuJoint'+str(j))
            cmds.setAttr(jnt+'.dla',1)
            cmds.addAttr(jnt,ln='infoPos',sn='ip',at='double',min=0,max=num_jnt-1,dv=j)
            cmds.setAttr(jnt+'.ip',e=1,k=1)
            jntG = cmds.group(jnt,n=jnt+'_p')
            info = cmds.createNode('pointOnCurveInfo', n=mainName+'_info'+str(j))
            subLoc = cmds.spaceLocator(n=mainName+'_subLoc'+str(j))[0]
            cmds.scale(.1,.1,.1,subLoc)
            subLocL.append(subLoc); jntL.append(jnt); jntGL.append(jntG); infoL.append(info)

            cmds.connectAttr(attachJointCurve+'.worldSpace[0]', info+'.inputCurve')
            cmds.pointConstraint(subLoc,jntG)
            normalCon = cmds.normalConstraint(normalBase,jntG,aim=up,u=aim,wut='vector')[0]
            cmds.connectAttr(info+'.tangent',normalCon+'.wu')
            cmds.connectAttr(info+'.position',subLoc+'.translate')
            prRt = 0; sRt = 0; editP = 0
            if posShp >= 0:
                sRt = posShp/num_jnt + 1
                editP = (j/float(num_jnt-1))**sRt
            else:
                sRt = 1-posShp/num_jnt
                editP = 1-abs(j/float(num_jnt-1)-1)**sRt
            import maya.mel as mel
            prRt = mel.eval( 'linstep(0,1,%s)' % editP ) * (num_jnt-1)
            cmds.setAttr(info+'.parameter', prRt/(num_jnt-1))
        else:
          for j in range(num_jnt):
            cmds.select(d=1)
            jnt = cmds.joint(rad = 2, n=mainName+'_cuJoint'+str(j))
            cmds.setAttr(jnt+'.dla',1)
            cmds.addAttr(jnt,ln='infoPos',sn='ip',at='double',min=0,max=num_jnt-1,dv=j)
            cmds.setAttr(jnt+'.ip',e=1,k=1)
            jntG = cmds.group(jnt,n=jnt+'_p')
            info = cmds.createNode('pointOnCurveInfo', n=mainName+'_info'+str(j))
            pntInfo = cmds.createNode('pointOnCurveInfo', n=mainName+'_pntInfo'+str(j))
            cmds.setAttr(info+'.top', 1)
            subLoc = cmds.spaceLocator(n=mainName+'_subLoc'+str(j))[0]; cmds.scale(.1,.1,.1,subLoc)
            jntPntChild = cmds.spaceLocator(n=mainName+'_pntChild'+str(j))[0]
            jntPnt = cmds.group(n=mainName+'_jntPnt'+str(j));
            pntRot= cmds.createNode('plusMinusAverage', n=mainName+'_pntRot'+str(j))
            cmds.connectAttr(jntPntChild+'.rotate', pntRot+'.input3D[0]')
            subLocL.append(subLoc); jntL.append(jnt); jntGL.append(jntG); infoL.append(info)
            jntPntChildL.append(jntPntChild); jntPntL.append(jntPnt); pntInfoL.append(pntInfo); pntRotL.append(pntRot)

            cmds.connectAttr(startHair+'.worldSpace[0]', pntInfo+'.inputCurve')
            cmds.connectAttr(attachJointCurve+'.worldSpace[0]', info+'.inputCurve')
            cmds.pointConstraint(subLoc,jntG)
            normalCon = cmds.normalConstraint(normalBase,jntPntChild,aim=up,u=aim,wut='vector')[0]
            cmds.connectAttr(pntInfo+'.tangent',normalCon+'.wu')
            cmds.connectAttr(info+'.position',subLoc+'.translate')
            cmds.connectAttr(pntInfo+'.position', jntPnt+'.translate')
            prRt = 0; sRt = 0; editP = 0
            if posShp >= 0:
                sRt = posShp/num_jnt + 1
                editP = (j/float(num_jnt-1))**sRt
            else:
                sRt = 1-posShp/num_jnt
                editP = 1-abs(j/float(num_jnt-1)-1)**sRt
            import maya.mel as mel
            prRt = mel.eval( 'linstep(0,1,%s)' % editP ) * (num_jnt-1)
            cmds.setAttr(info+'.parameter', prRt/(num_jnt-1))
            cmds.setAttr(pntInfo+'.parameter', prRt/(num_jnt-1))
            
          normalCon = cmds.normalConstraint(normalBase,jntGL[0],aim=up,u=aim,wut='vector')[0]
          jntPntNormalCon = cmds.normalConstraint(normalBase,jntPntL[0],aim=up,u=aim,wut='vector')[0]
          cmds.connectAttr(infoL[0]+'.tangent',normalCon+'.wu')
          cmds.connectAttr(pntInfoL[0]+'.tangent',jntPntNormalCon+'.wu')
          for j in range(1,num_jnt):
            cmds.tangentConstraint(attachJointCurve,jntGL[j],aim=aim,u=up,wu=up,wut='objectrotation',wuo=jntGL[j-1])
            cmds.tangentConstraint(startHair,jntPntL[j],aim=aim,u=up,wu=up,wut='objectrotation',wuo=jntPntL[j-1])
            
       
        if len(completeList) < len(jntL)*num_crv: completeList.extend(jntL) #------------- Out joint list
        
        #--------------- Grouping
        subLocG = cmds.group(subLocL,n=subLocL[0])
        deformGrp = cmds.group(attachJointCurve,bindCurve,normalBase,subLocG, n=mainName+'_deformGrp')
        cmds.setAttr(deformGrp+'.v', 0 )
        transformGrp = cmds.group(em=1, n=mainName+'_trGrp')
        parentCon = cmds.parentConstraint(conJoint[0],transformGrp )[0]
        cmds.delete(parentCon)
        cmds.parent(jntGL,conJoint[0],transformGrp)
          #------------ Grouping in hairSystem
        if hairSys_on != 0:
          print hairSystem
          jntPntG = cmds.group(jntPntL, n=mainName+'_jntPntG')
          cmds.parent(jntPntG,deformGrp)
        
        #-------------- Attribute Setting
        conJointFirst = conJoint[0]
        conJointSecond = conJoint[1]; cmds.setAttr(conJointSecond+'.template', 1)
        conJointFirst_sliding = conJointFirst + '.sliding'
        conJointFirst_length = conJointFirst + '.scale_length'
        
        if sliding == 1:
         cmds.addAttr(conJointFirst,ln='sliding',at='double')
         cmds.setAttr(conJointFirst_sliding,e=1,k=1)
        if length == 1:
         cmds.addAttr(conJointFirst,ln='scale_length',at='double',min=0,max=num_jnt,dv=num_jnt)
         cmds.setAttr(conJointFirst_length,e=1,k=1)
        
        #----------- Set Expression String   
        exString = 'float $ip[];\n\n'
        for k in range(num_jnt):
            exString += '$ip[%s] = %s/%s;\n' % (k, jntL[k]+'.infoPos',num_jnt-1)
        exString += '\n'
         
        if length == 1:
         exString += 'float $numJnt = %s;\n' % num_jnt
         exString += 'float $length = %s/%s;\n\n' % (conJointFirst_length, num_jnt)
        
        if sliding == 1:
         exString += 'float $ep[];\n'
         exString += 'float $sliding = %s;\n' % conJointFirst_sliding
         exString += 'float $sRate;\n\n'
         exString += 'if($sliding >= 0)\n{\n'
         exString += '$sRate=$sliding/%s+1;\n' % num_jnt
         for k in range(num_jnt):
             exString += '$ep[%s] = pow($ip[%s],$sRate);\n' % (k,k)
         exString += '}\nelse\n{\n'
         exString += '$sRate= 1 - $sliding/%s;\n' % num_jnt
         for k in range(num_jnt):
             exString += '$ep[%s] = 1-pow(1-$ip[%s],$sRate);\n' % (k,k)
         exString += '}\n\n'
         
        if length == 1 and sliding == 1:
         for k in range(num_jnt):
             exString += '%s.parameter = linstep(0,1,$ep[%s])*$length;\n' % (infoL[k], k)
        elif length == 1:
         for k in range(num_jnt):
             exString += '%s.parameter = $ip[%s]*$length;\n' % (infoL[k], k)
        elif sliding == 1:
         for k in range(num_jnt):
             exString += '%s.parameter = linstep(0,1,$ep[%s]);\n' % (infoL[k], k)
        else:
         for k in range(num_jnt):
             exString += '%s.parameter = $ip[%s];\n' % (infoL[k], k)
            
        cmds.expression(s=exString,n=mainName+'_ex') #--------- expression
        
        #-------------- Twist Attr Adding
        
        if hairSys_on != 0:
         if twist == 0:
           for j in range(num_jnt):
             cmds.connectAttr(pntRotL[j]+'.output3D', jntL[j]+'.jo')
             
        if twist == 1:
         cmds.addAttr(conJointFirst,ln='twist',at='double')
         cmds.setAttr(conJointFirst+'.twist',e=1,k=1)
         for j in range(num_jnt):
             cmds.addAttr(jntL[j],ln='twistDetail',at='double',dv=j/float(num_jnt-1)*10)
             cmds.setAttr(jntL[j]+'.twistDetail',e=1,k=1)
             twistMult = cmds.createNode('multiplyDivide',n= jntL[j]+'_twistMult')
             cmds.connectAttr(conJointFirst+'.twist', twistMult+'.input1X')
             cmds.connectAttr(jntL[j]+'.twistDetail', twistMult+'.input2X')
             rAxis = '.jo'
             if aim[0] == 1 or aim[0] == -1:rAxis += 'x'
             if aim[1] == 1 or aim[1] == -1:rAxis += 'y'
             if aim[2] == 1 or aim[2] == -1:rAxis += 'z'
             
             if hairSys_on == 0:
              cmds.connectAttr(twistMult+'.outputX', jntL[j]+rAxis)
             else:
              cmds.connectAttr(twistMult+'.outputX', pntRotL[j]+'.input3D[1].input3D%s' % (rAxis.replace('.jo','')) )
              cmds.connectAttr(pntRotL[j]+'.output3D', jntL[j]+'.jo')

        #-------------- Add Controler 
        ctrer = []; ctrGG = []; ctrSubLocG = []; getPosShp = ''
          
        curveSh = cmds.listRelatives(bindCurve,s=1)[0]
        exString_in =''
        for j in range(num_ctr):
            ctrer.append( cmds.circle(n=mainName+'_ctr'+str(j),normal=aim)[0] )
            cmds.addAttr( ctrer[j], ln='rollS', at='double', min=0,max=num_jnt,dv= num_jnt/2.0)
            cmds.setAttr( ctrer[j]+'.rollS', e=1,k=1)
            cmds.addAttr( ctrer[j], ln='rollE', at='double', min=0,max=num_jnt,dv=j*num_jnt/float(num_ctr))
            cmds.setAttr( ctrer[j]+'.rollE', e=1,k=1)
            ctrG = cmds.group( ctrer[j], n = mainName+'ctrG'+str(j) )
            info = cmds.createNode('pointOnCurveInfo', n=bindCurve+'_info'+str(j))
            cmds.setAttr(info+'.top',1)
            cmds.connectAttr( curveSh+'.worldSpace[0]', info+'.inputCurve')
            cmds.connectAttr( info+'.position', ctrG+'.translate')
            mult = cmds.createNode( 'multiplyDivide', n= mainName+'_ctr_posMult'+str(j) )
            cmds.connectAttr( ctrer[j]+'.rollE', mult+'.input1X')
            cmds.setAttr( mult+'.input2X', 1.0/len(conJoint) )
            cmds.connectAttr( mult+'.outputX',info+'.parameter' )
            subLoc = cmds.spaceLocator( n=mainName+'_ctr_subLoc'+str(j) )[0]
            cmds.connectAttr( info+'.position', subLoc+'.translate' )
            cmds.pointConstraint( subLoc, ctrG )
            normalCon = cmds.normalConstraint( normalBase,ctrG,aim=up,u=aim,wut='vector' )[0]
            cmds.connectAttr( info+'.tangent', normalCon+'.wu')
            
            ctrGG.append(ctrG); ctrSubLocG.append(subLoc)
        if len(ctrGG) != 0: cmds.parent(ctrGG,transformGrp)
        if len(ctrSubLocG) != 0: cmds.parent(ctrSubLocG,deformGrp)
        
        exString  = ''
        rotDirection = ''
        
        for j in range(3):
            if aim[j] == -1:
                rotDirection = '-1*'
            
        for j in range(len(ctrer)):
            exString += 'float $rollE%s = %s.rollE;\n' % (j, ctrer[j])
            exString += 'float $rollS%s = %s.rollS + $rollE%s;\n' % (j, ctrer[j], j)
            exString += 'int $irolE%s = $rollE%s;\n' % (j,j)
            exString += 'int $irolS%s = $rollS%s;\n' % (j,j)
            exString += 'float $rolev%s = $rollE%s - $irolE%s;\n' % (j,j,j)
            exString += 'float $rolsv%s = $rollS%s - $irolS%s;\n\n' % (j,j,j)
            exString += 'float $rx%s = %s%s.rotateX;\n' % (j, rotDirection, ctrer[j])
            exString += 'float $ry%s = %s%s.rotateY;\n' % (j, rotDirection, ctrer[j])
            exString += 'float $rz%s = %s%s.rotateZ;\n\n' % (j, rotDirection, ctrer[j])
            exString += 'float $outRate%s[];\n\n' % j
            exString += 'int $num_jnt%s = %s;\n\n' % (j,len(conJoint))
            exString += 'for($i = 0; $i < $num_jnt%s; $i++)\n{\n' % j
            exString += ' if($rollE%s > $i)\n   $outRate%s[$i] = 0;' % (j,j)
            exString += ' if($rollE%s > $i && $rollE%s < $i+1)\n   $outRate%s[$i] = 1-$rolev%s;\n' % (j,j,j,j)
            exString += ' if($rollE%s <= $i)\n   $outRate%s[$i] = 1;\n\n' % (j,j)
            exString += ' if($rollS%s > $i)\n   $outRate%s[$i] *= 1;\n' % (j,j)
            exString += ' if($rollS%s > $i && $rollS%s < $i+1)\n   $outRate%s[$i] *= $rolsv%s;\n' % (j,j,j,j)
            exString += ' if($rollS%s <= $i)\n   $outRate%s[$i] *= 0;\n}\n\n' % (j,j)
        
        rotList = ['rx','ry','rz']
        
        for rot in rotList:
          for j in range(len(conJoint)):
            ra = rot.replace('r','ra')
            exString += '%s.%s = ' % (conJoint[j],ra)
            for k in range(len(ctrer)):
              if k == len(ctrer)-1:
               exString += '%s*$outRate%s[%s]*$%s%s;\n' % (aim[0]+aim[1]+aim[2],k,j,rot,k)
              else:
               exString += '%s*$outRate%s[%s]*$%s%s+' % (aim[0]+aim[1]+aim[2],k,j,rot,k)
          exString+= '\n'
        
        if len(ctrer) != 0: cmds.expression(s=exString, name = mainName+'_ctrEx')
  cmds.select(cl=1)
        

#--------- Else Def       
def turn_axis():
    for i in completeList:
        if cmds.getAttr(i+'.dla') == 0:
         cmds.setAttr(i+'.dla', 1)
        else:
         cmds.setAttr(i+'.dla', 0)