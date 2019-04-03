#!/usr/bin/python
#Pulls data from the IOS 5sec database on couch.snopl.us and
#Finds the average, minimum, and maximum values for each 
#channel in the last minute or last 15 minutes.

from __future__ import print_function
import sys
import couchdb, time, math
import lib.credentials as cr
import lib.couchutils as cu
import lib.doccreate as dc
import socket

ios = int(socket.gethostname()[3])

#can only be onemin or fifteenmin.  More could be added
#by adding the correct functions in lib/couchutils, and also
#making the correct databases
timetype = "onemin"

#Connection info for couchdb
couch = couchdb.Server('http://couch.snopl.us')
couchuser, couchpassword = cr.getcreds("/home/slowcontroller/config/couchcred.conf")
couch.resource.credentials = (couchuser, couchpassword)


#Finds the minute (in seconds) of a Unix timestamp          
def unix_minute(unix_time):
    unix_minute = 60*int(math.floor(unix_time/60.))
    return unix_minute

if __name__=='__main__':
    #The start of the actual code
    if timetype=="onemin":
        minutes=1
    if timetype=="fifteenmin":
        minutes=15
    time_interval = minutes*60
    latest_time = cu.get_latest_time(timetype,ios,couch)
    while(1):
        #print latest_1min_time
        latest_5sec_time = cu.get_latest_time("fivesec",ios,couch)
        if latest_time+time_interval > latest_5sec_time:
            time.sleep(time_interval)
	else: 
            documents = cu.getDocuments(latest_time,time_interval,ios,couch)
            ios_data = dc.createDoc(documents,latest_time,time_interval,ios)
            cu.saveVoltages(ios_data,timetype,couch)
            latest_time = latest_time + time_interval
