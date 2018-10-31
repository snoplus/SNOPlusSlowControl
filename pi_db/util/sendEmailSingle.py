#!/usr/bin/python
#to pull data from slow control ios and put it in ioserverdata db

import psycopg2
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


gmailUser, gmailPassword = getcreds("/home/uwslowcontrol/config/gmailcred.conf")

recipient = 'tjpershing@ucdavis.edu'
ios = 1
period = 5

#Connection info for couchdb
couch = couchdb.Server('http://couch.snopl.us')
couchuser, couchpassword = getcreds("/home/uwslowcontrol/config/couchcred.conf")
couch.resource.credentials = (couchuser, couchpassword)


def sendMail(subject, text):
    try:
        msg = MIMEMultipart()
        msg['From'] = gmailUser
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(text))
        mailServer = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(gmailUser, gmailPassword)
        mailServer.sendmail(gmailUser, recipient, msg.as_string())
        mailServer.close()
    except:
        pass
    return



conn_ioserver1 = httplib2.Http(".cache")


sendMail(sys.argv[1], sys.argv[2])
