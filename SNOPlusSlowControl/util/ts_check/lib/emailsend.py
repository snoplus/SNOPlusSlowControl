#!/usr/bin/python
#Quick script for sending an email to the Slow Control AlarmsList

import sys
import json, httplib2, couchdb, string, time, re
import os
import smtplib
import mimetypes
import getcreds as gc
import config.tsconfig as c
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText

#connection info and email list directory for slow control email notification
gmailUser, gmailPassword = gc.getcreds(c.Gmail_Cred)
recipientsList = open(c.EmailList,"r")
recipients = recipientsList.readlines()

def sendTSAlarmEmail(alarmDate,IOSnum):
    title = "New alarms: " + str(alarmDate) + ", timestamp old for "
    msg = "Alarm triggered at: " + str(alarmDate) + "\n\n"
    title = title + "IOS  " + str(IOSnum) + "\n\n"
    msg = msg + "Timestamp for most recent data from IOS " + str(IOSnum) + \
	    "is older than alarming threshold."
    sendMail(title, msg)

def sendTSAlarmEmail_CT(alarmDate):
    title = "New alarms: " + str(alarmDate) + ", timestamp old for "
    msg = "Alarm triggered at: " + str(alarmDate) + "\n\n"
    DVtitle = "Cavity Temperature Sensors"
    msg = "Timestamp for most recent data from cavity temp. sensors is older " + \
	    "than alarming threshold."
    sendMail(title, msg)

def sendTSAlarmEmail_DV(alarmDate):
    title = "New alarms: " + str(alarmDate) + ", timestamp old for "
    msg = "Alarm triggered at: " + str(alarmDate) + "\n\n"
    DVtitle = "Delta V"
    msg = "Timestamp for most recent data from Delta V is older " + \
	    "than alarming threshold."
    sendMail(title, msg)

def sendTSClearEmail(alarmDate,IOSnum):
    title = "No longer alarms: " + str(alarmDate) + ", timestamp old for "
    msg = "Alarm cleared at: " + str(alarmDate) + "\n\n"
    title = title + "IOS  " + str(IOSnum) + "\n\n"
    msg = msg + "Timestamp for most recent data from IOS " + str(IOSnum) + \
	    "is now below alarming threshold."
    sendMail(title, msg)

def sendTSClearEmail_CT(alarmDate):
    title = "No longer alarms: " + str(alarmDate) + ", timestamp old for "
    msg = "Alarm cleared at: " + str(alarmDate) + "\n\n"
    title = title + "Cavity Temperature Sensors"
    msg = "Timestamp for most recent Cavity Temperature Sensor data is now " + \
	    "below alarming threshold."
    sendMail(title, msg)

def sendTSClearEmail_DV(alarmDate):
    title = "No longer alarms: " + str(alarmDate) + ", timestamp old for "
    msg = "Alarm cleared at: " + str(alarmDate) + "\n\n"
    title = title + "Delta V"
    msg = "Timestamp for most recent data from Delta V is now " + \
	    "below alarming threshold."
    sendMail(title, msg)

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
  Subject = 'Test1'
  Message = 'Testing of sending e-mails on IOS3'
  sendMail(Subject, Message)
