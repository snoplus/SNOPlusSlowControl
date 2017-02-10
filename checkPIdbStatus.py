#!/usr/bin/env python
from suds.client import Client
from suds.sudsobject import asdict
import datetime, time, calendar, math
import logging, pprint
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

recipientfile = open("emailList.txt","r")             
recipients = recipientfile.readlines(); 


#Sends an email
def sendMail(subject, text):
    try:
        msg = MIMEMultipart()
	msg['From'] = gmailUser
	msg['Subject'] = subject
	msg.attach(MIMEText(text))
	mailServer = smtplib.SMTP('smtp.gmail.com', 587)
	mailServer.ehlo()
	mailServer.starttls()
	mailServer.ehlo()
	mailServer.login(gmailUser, gmailPassword)
	msg['To'] = "tjpershing@ucdavis.edu"
        mailServer.sendmail(gmailUser, recipients, msg.as_string())
	mailServer.close()
    except:
        pass
    return 


# Converts UTC-5 date-time to unix timestamp
def dmy_to_unix(timely):
    tiempo = "%s" % timely
    tiempo = tiempo[0:18]
    tiempo = int(calendar.timegm(time.strptime(tiempo, '%Y-%m-%d %H:%M:%S')))+5*3600
    return tiempo

#gets latest timestamp from PI database
def getLatestTimestamp():
    logging.basicConfig(level=logging.INFO)
    timeseries_url = 'http://pi.snolab.ca/PIWebServices/PITimeSeries.svc?wsdl'
    timeseries_client = Client(timeseries_url)
    piarcdatarequest = timeseries_client.factory.create('PIArcDataRequest')
    current_avlc_total_paths = timeseries_client.factory.create('ArrayOfString')
    current_avlc_total_paths.string.append('pi:\\\\pi.snolab.ca\\DeltaV_AVLC-AI-02/AI1/PV.CV')
    snapshot = timeseries_client.service.GetPISnapshotData(current_avlc_total_paths)
    timestamp = snapshot.TimeSeries[0].TimedValues[0][0]._Time
    return timestamp

timestamp = getLatestTimestamp()
latest_time = dmy_to_unix(timestamp)
current_time = time.time()
difference = current_time-latest_time
minutes = difference/60
if minutes>60:
    subject = "PI database is not up to date!"
    body = "PI database has not been updated since "+str(timestamp)+"\n\n"
    body = body + "It is now "+str(minutes)+" minutes behind the present time."
    sendMail(subject,body)
