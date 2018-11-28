#!/usr/bin/env python
#Original scripts by: Luke Kippenbrock on 23 April 2015
#Alarm server features by: Teal Pershing, 28 July 2016
#Restructured into classes/libraries by: Teal Pershing, 28 Oct 2018

import datetime, time, calendar, math, re
import sys, pprint
import smtplib

import lib.pilogger as l
import lib.alarmserver as als
import lib.config.config as c
import lib.couchutils as cu
import lib.credentials as cr
import channelDB.pilist as pl

#At an uncaught exception, run our handler
sys.excepthook = l.UE_handler

#Initialize home logger
logger = l.get_logger(__name__)
logger.info('PI_DB SCRIPT INITIALIZING...')

if __name__ == '__main__':

    #Have to hard-code a delay in the times polled from PI DB
    #If you don't, will just poll empty values
    delay = 5  #in minutes 
    wait_time = 60 # in seconds

    #Initialize Alarm server and get heartbeat going
    AlarmPoster = als.AlarmPoster(alarmhost=c.ALARMHOST,psql_database=c.ALARMDBNAME)
    AlarmPoster.startConnPool()
    AlarmPoster.post_heartbeat(c.ALARMHEARTBEAT,beat_interval=c.ALARMBEATINTERVAL)

    #Initialize CouchDB connction.  Also get current channeldb
    CouchConn = cu.PIDBCouchConn()
    CouchConn.getServerInstance(c.COUCHADDRESS,c.COUCHCREDS)
    channeldb = CouchConn.getLatestEntry(c.CHANNELDBURL,c.CHANNELDBVIEW)
    alarms_dict = CouchConn.getLatestEntry(c.ALARMDBURL,c.ALARMDBVIEW)

    #Initialize Alarm Handler
    AlarmHandler = alh.AlarmHandler(pl.pi_list,CouchConn,AlarmPoster)
    AlarmHandler.clearAllAlarms()

    #Initialze the data handler
    PIDataHandler = pdh.PIDataHandler()
    PIDataHandler.CreateClientConnection(c.TIMESERIESURL,c.PIDBFACTORYNAME)
    PIDataHandler.OpenPIDataRequest()
    
    while True:
        #Set the poll time for loop
        poll_time = (unix_minute(time.time())-c.POLLDELAY)*60
        endpoll_time = poll_time+c.POLLRANGE

        #Have the data handler grab and manipulate data
        rawPIData = PIDataHandler.getValues(poll_time,endpoll_time,pl.pi_list)
        formattedPIData = PIDataHandler.ManipulateData(poll_time,endpoll_time,rawPIData,pl.pi_list)

        #Save the data to our couchDB
        CouchConn.saveValues(formattedPIData,c.ONEMINDBURL) #Will be from a couchutil instance
        
        #Check data against alarm thresholds; post alarms if needed
        alarms_last = alarms_dict
        for timeslot in formattedPIData:
            alarms_dict = AlarmHandler.checkThresholdAlarms(formattedPIData,channeldb,alarms_dict)
            AlarmHandler.postAlarmServerAlarms(alarms_dict, alarms_last)
            AlarmHandler.printAlarms(alarms_dict, alarms_last, c.MAILRECIPIENTLISTDIR)
        
        #Get the lastest channeldb entry in case new alarm thresholds/states were loaded in
        if channeldb is not None:
            channeldb_last = channeldb
        channeldb = CouchConn.getLatestEntry(c.CHANNELDBURL,c.CHANNELDBVIEW)
        
        #if it took >60 seconds to run loop, no waiting; just go to the next data set!
        offset = (time.time()- c.POLLDELAY*60) - (poll_time + c.POLL_WAITTIME)
        if offset<0:
            time.sleep(c.POLL_WAITTIME)
