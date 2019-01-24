#!/usr/bin/python
# Deletes old docs from slowcontrol-data-5sec to preserve disk space
# June 12 2013 Tim Major

import json, httplib2, couchdb, string, time, re
import os
import smtplib
import socket
import mimetypes
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText

#Used to pull connection information from config directory
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

#Connection info for couchdb and slow control-specific couchdbs
couchuser, couchpassword = getcreds("/home/slowcontroller/config/couchcred.conf")
SCcouchuser, SCcouchpassword = getcreds("/home/slowcontroller/config/SCcouchcred.conf")

localcouch = couchdb.Server()
localcouch.resource.credentials = (SCcouchuser, SCcouchpassword)
snopluscouch = couchdb.Server('http://couch.snopl.us')
snopluscouch.resource.credentials = (couchuser, couchpassword)

ios =  int(socket.gethostname()[3])
period = 5

recipientfile=open("/home/slowcontroller/SNOPlusSlowControl/SNOPlusSlowControl/DB/emailList.txt","r")
recipients = recipientfile.readlines();

def connectToLocalDB(dbName):
    status = "ok"
    db = {}
    try:
        db = localcouch[dbName]
    except:
        print "Failed to connect to local " + dbName
        status = "bad"
    return status, db


def connectToSnoplusDB(dbName):
    status = "ok"
    db = {}
    try:
        db = snopluscouch[dbName]
    except:
        print "Failed to connect to couch.snopl.us " + dbName
        status = "bad"
    return status, db


def checkUsage():
    usage = -1
    percent = -1
    with open('/home/slowcontroller/diskUsage.txt', 'r') as f:
        for line in f:
            if (line.find('sda3') != -1):
                percent=line.find('% /')
                if (percent!=-1):
                    usage = int(line[percent-2:percent])
    return usage

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
        #msg['To'] = "alarmslist"
        msg['To'] = recipients
        mailServer.sendmail(gmailUser, recipients, msg.as_string())
        mailServer.close()
    except:
        pass
    return   

#sendMail("Slow control failed to connect DB","Slow control could not connect to DB on snotpenn01 for the last " + time + " seconds")
#Check that most recent doc on snotpenn is the same as and time is not more than 1 minute off otherwise send email.



def checkIfOkay(localdb5secStatus,localdb5sec,snoplusdb5secStatus,snoplusdb5sec):
    message=""
    okayToDelete=True
    minMonthsToKeep = 2
    minNumberOfDocs = 30 * 24 * 60 * 12 * minMonthsToKeep
    maxqueryresults = localdb5sec.view("slowcontrol-data-5sec/recent"+str(ios),descending=True,limit=10)
    minqueryresults = localdb5sec.view("slowcontrol-data-5sec/recent"+str(ios),limit=10)
    if localdb5secStatus is "ok":
        message += "connected local\n"
    else: 
        okayToDelete=False

    if snoplusdb5secStatus is "ok":
        message += "connected snoplus\n"
    else:
        okayToDelete=False

    usage = checkUsage()
    message += "usage is " + str(usage) + "\n"
    if (usage < 10):
        okayToDelete=False

    if okayToDelete:
        maxqueryresults = localdb5sec.view("slowcontrol-data-5sec/recent"+str(ios),descending=True,limit=10)
        minqueryresults = localdb5sec.view("slowcontrol-data-5sec/recent"+str(ios),limit=1)
        if (maxqueryresults.total_rows < minNumberOfDocs ):
            message += "Only " + str( maxqueryresults.total_rows ) + " docs.  Not enough docs to justify deleting any! \n"
            okayToDelete=False 
        try:
            snoplusdb5sec[maxqueryresults.rows[9].id]
        except:
            message += "Recent document not on couch.snopl.us!\n"
            okayToDelete=False

        try:
            snoplusdb5sec[minqueryresults.rows[0].id]
        except:
            message+= "Oldest document not on couch.snopl.us!\n"
            okayToDelete=False
#        try:
#            oneminqueryresults = localdb1min.view("slowcontrol-data-1min/recent"+str(ios),startkey=(minqueryresults.rows[0].key-60),limit=1)
#            if (len(oneminqueryresults.rows)!=0):
#                message += "One-min summary data: check."
#            else:
#                message += "No one-min summary data!"
#                okayToDelete=False
#        except:
#            message += "Trouble with 1min database"
#            okayToDelete=False
        
    return okayToDelete, message

if __name__=="__main__":
    # ioserver connection
    conn_ioserver1 = httplib2.Http(".cache")
    localdb5secStatus, localdb5sec=connectToLocalDB("slowcontrol-data-5sec")
    snoplusdb5secStatus, snoplusdb5sec = connectToSnoplusDB("slowcontrol-data-5sec")
    
    # One test deletion
    okayToDelete, message = checkIfOkay(localdb5secStatus,localdb5sec,snoplusdb5secStatus,snoplusdb5sec)
    #print okayToDelete
    #print message
    
    minqueryresults = localdb5sec.view("slowcontrol-data-5sec/recent"+str(ios),limit=10)
    
    if okayToDelete:
        try:
            localdb5sec.delete(minqueryresults.rows[0].value)
            message+= "Deleting...\n"
        except:
            message+= "Deletion failed.\n"
            okayToDelete=False
        #Time for deletion to propagate, which it shouldn't.
    deletions=0
    if okayToDelete:
        message+= "Sleeping..."
        time.sleep(30)
        try:
            snoplusdb5sec[minqueryresults.rows[0].id]
            deletions+=1
        except:
            message+= "!!!!!!Deletion propagated to couch.snopl.us!!!!!!\n"
            sendMail("IOS "+ str(ios) +" Deletion error!", message)
            okayToDelete=False
        message+= "Done"
    
    #Delete the rest
    while okayToDelete:
        queryresults = localdb5sec.view("slowcontrol-data-5sec/recent"+str(ios),limit=100)
        if (len(queryresults.rows) > 0):
            for i in queryresults.rows:
                localdb5sec.delete(i.value)
                deletions+=1
        okayToDelete, message = checkIfOkay(localdb5secStatus,localdb5sec,snoplusdb5secStatus,snoplusdb5sec)
    
    print okayToDelete
    print message
    print str(deletions) + " deletions"
    sendMail("IOS "+ str(ios) +" Deletion status", message + str(deletions)+ "deletions")
