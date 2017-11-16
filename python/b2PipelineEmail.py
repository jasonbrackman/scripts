# -*- coding: utf-8 -*-
# Import smtplib for the actual sending function
import smtplib
import email

import email.mime.application
from email.header import Header
from email import Encoders

from datetime import datetime
import os
import getpass
import glob


def releaseInfoToEmail(info, snapshots):

    computername = os.environ['COMPUTERNAME']
    splitInfo = info[2].split('/')
    project = splitInfo[1].split('_')[1]
    releaseType = splitInfo[2]
    mdl = splitInfo[5]
    name = splitInfo[4]

    ProjectGrpEmail = project + "_Project@b1ve.com"

################ asset일 경우. ################
    if releaseType == "4.Asset":

        # asset release          
        if len(info) > 6:
            releaseFileSplitInfo = info[6].split('/')             
            subject = '[' + project + ']' + ' [' + mdl + '] ' + name + ' ' + releaseFileSplitInfo[6] + '-' + releaseFileSplitInfo[7] + ' ( published by ' + info[0]  + ' )' 
            
            bodyText = """
Atrist : """ + info[0] + """ 
Timestamp : """ + datetime.now().strftime('%Y-%m-%d, %H:%M:%S') + """ 
Release : """ + info[6] + """ 

Comment : 
"""  + info[5] + """

Develop : """ + info[2] + """ 
 
original SceneFile : """  + info[1] + """
from : """ +  computername + """
""" 
        # asset develop
        else:
            subject = '[' + project + ']' + ' [' + mdl + '] ' + name + ' ' + splitInfo[6] + '-' + splitInfo[7] + ' ( published by b2pipeline.)' 

            bodyText = """
Atrist : """ + info[0] + """ 
Timestamp : """ + datetime.now().strftime('%Y-%m-%d, %H:%M:%S') + """          
Develop : """ + info[2] + """     

Comment : 
"""  + info[5] + """


original SceneFile : """  + info[1] + """
from : """ +  computername + """
"""

################ shot일 경우. ################
    elif splitInfo[2] == "5.Shot":

        # shot release          
        if len(info) > 6:
            releaseFileSplitInfo = info[6].split('/')             
            subject = '[' + project + ']' + ' [' + splitInfo[7] + '] ' + splitInfo[3] + ' ' + name + ' ' + releaseFileSplitInfo[9] + '-' + releaseFileSplitInfo[10] + ' ( published by b2pipeline.)' 

            releasedFileText = "\t"
            releasedFiles = glob.glob(info[6] + '/*.*')
            for releasedFile in releasedFiles:
                if releasedFile.endswith('.abc') or releasedFile.endswith('.ma') or releasedFile.endswith('.editMA') :
                    releasedFileText += releasedFile.split('\\')[-1] + '\n\t'


            bodyText = """
atrist : """ + info[0] + """ 
Timestamp : """ + datetime.now().strftime('%Y-%m-%d, %H:%M:%S') + """ 
release : """ + info[6] + """ 

""" + releasedFileText + """

comment : 
"""  + info[5] + """

   
develop : """ + info[2] + """ 

original SceneFile : """  + info[1] + """
from : """ +  computername + """
"""


        # shot develop
        else:
            subject = '[' + project + ']' + ' [' + splitInfo[7] + '] ' + splitInfo[3] + ' ' + name + ' ' + splitInfo[9] + '-' + splitInfo[10] + ' ( published by b2pipeline.)' 
            bodyText = """
atrist : """ + info[0] + """ 
Timestamp : """ + datetime.now().strftime('%Y-%m-%d, %H:%M:%S') + """          
develop : """ + info[2] + """     

comment : 
"""  + info[5] + """


original SceneFile : """  + info[1] + """
from : """ +  computername + """
"""
    
    # email 로 릴리즈 정보 전달.
    sendEmail( ProjectGrpEmail, subject, bodyText, snapshots )    






def sendEmail( to, subject, body, snapshots ):
    
    print '# Attempting to send notification email'

    # Basic Information
    msg = email.mime.Multipart.MIMEMultipart()    
    msg['Subject']= Header(subject,'euc-kr') # 제목 인코딩
    msg['From'] = 'b1pipeline@b1ve.com'
    msg['To'] = to
    password = 'cgartist'
    
    body = email.mime.Text.MIMEText(body, _charset='euc-kr')

    msg.attach(body)

    # Attachment
    for snapshot in snapshots:        

        endDir = snapshot.split('/')
        filename = endDir[len(endDir)-1]

        fp = open(snapshot,'rb')
        attachment = email.mime.application.MIMEApplication(fp.read())
        fp.close()
        attachment.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(attachment)


    # send via Gmail server
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(msg['From'], password)
    s.sendmail(msg['From'], [msg['To']], msg.as_string())
    s.quit()

    print '# Successfully sent notification eamil'





