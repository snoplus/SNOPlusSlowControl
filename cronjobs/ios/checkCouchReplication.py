#!/usr/bin/python
#This script checks that data stored in the IOS's local couchDB is being
#Replicated to the couch.snopl.us database properly.  If not, an alarm
#E-mail is sent to the slow control alarms list.

from __future__ import print_function
import sys
import socket
import json, httplib2, couchdb, string, time, re
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

#Connection info for couchdb
couchuser, couchpassword = getcreds("/home/slowcontroller/config/couchcred.conf")
SCcouchuser, SCcouchpassword = getcreds("/home/slowcontroller/config/SCcouchcred.conf")
ios =  str(int(socket.gethostname()[3]))


recipientfile=open("/home/slowcontroller/emailList.txt","r")
recipients = recipientfile.readlines();


ios_couch = couchdb.Server()
ios_couch.resource.credentials = (SCcouchuser, SCcouchpassword)
snopl_couch = couchdb.Server('http://couch.snopl.us')
snopl_couch.resource.credentials = (couchuser, couchpassword)


def connectToIosDB(dbName):
    status = "ok"
    db = {}
    try:
        db = ios_couch[dbName]
    except:
        print("Failed to connect to " + dbName, file=sys.stderr)
        status = "bad"
    return status, db

def connectToSnoplDB(dbName):
    status = "ok"
    db = {}
    try:
        db = snopl_couch[dbName]
    except:
        print("Failed to connect to " + dbName, file=sys.stderr)
        status = "bad"
    return status, db


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

def getIosTimestamp():
    dbParStatus, dbPar = connectToIosDB("slowcontrol-data-5sec")
    if dbParStatus is "ok":
        queryresults =  dbPar.view("slowcontrol-data-5sec/recent"+ios,descending=True,limit=1)
        iosTimestamp = queryresults.rows[0].value["timestamp"]
    return iosTimestamp


def getSnoplTimestamp():
    dbParStatus, dbPar = connectToSnoplDB("slowcontrol-data-5sec")
    if dbParStatus is "ok":
        queryresults =  dbPar.view("slowcontrol-data-5sec/recent"+ios,descending=True,limit=1)
        snoplTimestamp = queryresults.rows[0].value["timestamp"]
    return snoplTimestamp



snoplTimestamp = getSnoplTimestamp()
iosTimestamp = getIosTimestamp()
difference = iosTimestamp-snoplTimestamp
minutes = difference/60
if minutes>5:
    subject = "Couch.snopl.us is not up to date with replications!"
    print(subject)
    body = "Couch.snopl.us 5sec data is now "+str(minutes)+" minutes behind IOS "+ios
    sendMail(subject,body)
