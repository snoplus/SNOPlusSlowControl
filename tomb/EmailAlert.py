#!/usr/bin/python
#Quick script for sending an email to the Slow Control AlarmsList

import sys
import json, httplib2, couchdb, string, time
import os
import smtplib
import mimetypes
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText


def getcreds(location):
	f = open(location, "rb")
	for line in f:
		if "username" in line:
			user = re.sub("username ", "", line)
			user=user.rstrip()
		if "password" in line:
			pwd = re.sub("password ", "", line)
			pwd=pwd.rstrip()
	return user, pwd

#connection info for slow control email notification
gmailUser, gmailPassword = getcreds("/home/slowcontroller/config/gmailcred.conf")

recipientsList = open("/home/slowcontroller/emailList.txt","r")
recipients = recipientsList.readlines()

def sendMail(subject, text):
    try:
        msg = MIMEMultipart()
        msg['From'] = gmailUser
        msg['Subject'] = subject
        msg.attach(MIMEText(text))
        mailServer = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(gmailUser, gmailPassword)
        msg['To'] = "alarmslist"
        mailServer.sendmail(gmailUser, recipients, msg.as_string())
        mailServer.close()
    except:
        pass
    return


if __name__ == '__main__':
  Subject = 'Software Installation on Slow Control IO Server 4'
  Message = 'I will be installing software on IO Server #4 needed for
  connecting to postgres databases.  The server will be down for approximately an hour during this process (it only reads currents from the  racks,  which are not accurate or high priority measurements now). I will send another e-mail when the update is complete.  Best, ~Teal'
  sendMail(Subject, Message)
