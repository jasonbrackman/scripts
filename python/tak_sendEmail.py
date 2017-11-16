'''
Author: Sang-tak Lee
Contact: chst27@gmail.com
Date:

Description:

Install:
'''

import os, smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders

import time
import datetime


host = 'smtp.gmail.com'
from_address = 'stlee@b1ve.com'
from_password = ''
to_address = ''

def send_gmail(to_address, title, text, html, attach):
    title = 'Hello'
    msg=MIMEMultipart('alternative')
    msg['From']=from_address  # <-- 발신자 이름을 바꾸려면 수정하세요. 안적으시면 메일계정이름으로 날아갑니다.
    msg['To']=to_address
    msg['Subject']=title
    msg.attach(MIMEText(text, 'plain'))
    msg.attach(MIMEText(html, 'html'))

    #managing attachment 
    #이하 주석처리된 부분이 메일 첨부파일 발송을 위한 부분입니다. 첨부파일이 필요하시면 수정해서 쓰세요.
    #part=MIMEBase('application','octet-stream')
    #part.set_payload(open(attach, 'rb').read())
    #Encoders.encode_base64(part)
    #part.add_header('Content-Disposition','attachment; filename="%s"' % os.path.basename(attach))
    #msg.attach(part)

    mailServer = smtplib.SMTP(host, 587)
    mailServer.login(from_address, from_password )
    mailServer.sendmail(from_address, to_address, msg.as_string())
    mailServer.close()
    


def mainLoop(): 
    title="메일제목을 쓰세요."
    #attach_file="send_mail.py"  <--------- 첨부파일 명입니다. 없으면 그대로 주석처리 해두세요.

    f = open("text.txt", "r")   #<------ 메일 내용의 Text버전이 들어있는 파일입니다.
    message = f.read()
    f.close()

    f = open("html.html", "r")   #<------ 메일 내용의 HTML버전이 들어있는 파일입니다.
    html = f.read()
    f.close()

    print "Program Ready"
    print "----------------------"
    f = open("list.txt", "r")   # <---- 엔터키로 구분된 메일링 리스트입니다. 메일 주소가 한줄에 하나씩 있어야 합니다.
    emails = f.readlines()
    for email in emails:
        email = email.strip('\r')
        email = email.strip('\n')
        email = email.strip(' ')
        email = email.strip('\t')
        if email == "" :
            continue
        print "[" + str(datetime.datetime.now()) + "] Sending email to " + email + "..."
        send_gmail(email,title,message,html,"")
        print "[" + str(datetime.datetime.now()) + "] Complete... Waiting for 5 seconds."  # 5초마다 보냅니다.
        time.sleep(5)
    print "Mails have just sent. The program is going to end." 


if __name__ == "__main__":
    mainLoop()














    #!/usr/bin/python
# -*- coding:utf-8 -*-

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
from email import Utils
from email.header import Header
import os

smtp_server  = "smtp 서버"
port = smtp 포트번호
userid = "smtp 접속 아이디"
passwd = "smtp 비밀번호"

def send_mail(from_user, to_user, cc_users, subject, text, attach):
        COMMASPACE = ", "
        msg = MIMEMultipart("alternative")
        msg["From"] = from_user
        msg["To"] = to_user
        msg["Cc"] = COMMASPACE.join(cc_users)
        msg["Subject"] = Header(s=subject, charset="utf-8")
        msg["Date"] = Utils.formatdate(localtime = 1)
        msg.attach(MIMEText(text, "html", _charset="utf-8"))

        if (attach != None):
                part = MIMEBase("application", "octet-stream")
                part.set_payload(open(attach, "rb").read())
                Encoders.encode_base64(part)
                part.add_header("Content-Disposition", "attachment; filename=\"%s\"" % os.path.basename(attach))
                msg.attach(part)

        smtp = smtplib.SMTP(smtp_server, port)
        smtp.login(userid, passwd)
        smtp.sendmail(from_user, cc_users, msg.as_string())
        smtp.close()