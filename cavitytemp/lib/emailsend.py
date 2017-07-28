#!/usr/bin/python
#Quick script for sending an email to the Slow Control AlarmsList

import sys
import  string, time, re
import os
import smtplib
import mimetypes
import getcreds as gc
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText

#connection info and email list directory for slow control email notification
gmailUser, gmailPassword = gc.getcreds("/home/uwslowcontrol/config/gmailcred.conf")
recipientsList = open("/home/uwslowcontrol/pi_db/emailList.txt","r")
recipients = recipientsList.readlines()

def sendCTAlarmEmail(alarmDate):
    title = "New alarms: " + str(alarmDate) + ", Cavity Temperature Sensor "
    msg = "Alarm triggered at: " + str(alarmDate) + "\n\n"
    msg = msg + "A Cavity temperature sensor is past the lo/hi alarming threshold."
    sendMail(title, msg)

def clearCTAlarmEmail(alarmDate):
    title = "No longer alarms: " + str(alarmDate) + ", Cavity Temperature Sensor "
    msg = "Alarm cleared at: " + str(alarmDate) + "\n\n"
    msg = msg + "There are no longer any alarming cavity temperature sensors."
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
  Message = 'Testing of sending e-mails from CavityTemps Script'
  sendMail(Subject, Message)
