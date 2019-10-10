#!/usr/bin/env python
#Original scripts by: Luke Kippenbrock on 23 April 2015
#Alarm server features by: Teal Pershing, 28 July 2016
#Restructured into classes/libraries by: Teal Pershing, 28 Oct 2018

import datetime, time, calendar, math, re
import sys, pprint, socket
import smtplib

import lib.timeconverts as tc
import lib.thelogger as l
import lib.alarmserver as als
import lib.pidb_alarmhandler as alh
import lib.pigrabber as pig
import lib.dataconverters as dc

import lib.config.pidbconfig as c
import lib.config.logconfig as lc
import lib.config.alarmdbconfig as ac

import lib.couchutils as cu
import lib.credentials as cr
import DB.pilist as pl

#At an uncaught exception, run our handler
sys.excepthook = l.UE_handler

#Initialize home logger
logger = l.get_logger(__name__)
logger.info('PI_DB SCRIPT INITIALIZING...')

hostname = socket.gethostname()
if hostname != 'minard.sp.snolab.ca':
    logger.exception("main_pidb.py: Attempting to run pidb script off minard.  Exiting")
    sys.exit(0)

if __name__ == '__main__':
    #Initialize Alarm server and get heartbeat going
    AlarmPoster = als.AlarmPoster(alarmhost=ac.ALARMHOST,psql_database=ac.ALARMDBNAME)
    AlarmPoster.startConnPool()
    AlarmPoster.post_heartbeat(c.ALARMHEARTBEAT,beat_interval=c.ALARMBEATINTERVAL)
    #Initialize CouchDB connction.  Also get current channeldb
    CouchConn = cu.PIDBCouchConn()
    CouchConn.getServerInstance(c.COUCHADDRESS,c.COUCHCREDS)
    channeldb = CouchConn.getLatestEntry(c.CHANNELDBURL,c.CHANNELDBVIEW)
    logger.info("main.py: Most recent channel database acquired on startup.")
    if c.DEBUG is True:
        print("Debug mode: FIRST CHANNELDB ENTRY:")
        print(channeldb)
    alarms_dict = CouchConn.getLatestEntry(c.COUCHALARMDBURL,c.COUCHALARMDBVIEW)
    if c.DEBUG is True:
        print("Debug mode: FIRST ALARMS DICTIONARY LOADED FROM COUCHDB:")
        print(alarms_dict)
    
    #Initialize Alarm Handler; uses an AlarmPoster class to post alarms
    #Based on what readings in the PI database are alarming
    PiAlarmHandler = alh.PIAlarmHandler(pl.pi_list,CouchConn,AlarmPoster)
    PiAlarmHandler.clearAllAlarms(channeldb)
    
    #Initialze the data handler
    PIDataHandler = pig.PIDataHandler()
    PIDataHandler.CreateClientConnection(c.TIMESERIESURL,c.PIDBFACTORYNAME)
    PIDataHandler.OpenPIDataRequest()
    PIDataHandler.SetPiBaseAddress(c.PIADDRESSBASE) 
   
    #Initialize the data converter
    DataConverter = dc.PIDataConverter()
    print('Initializing DataConverter')

    while True:
        #Set the poll time for loop
        poll_time = (tc.unix_minute(time.time())-c.POLLDELAY)*60
        endpoll_time = poll_time+c.POLLRANGE

        #Have the data handler grab and manipulate data
        rawPIData = PIDataHandler.getValues(poll_time,endpoll_time,pl.pi_list,pl.getrecent_list)
        formattedPIData = PIDataHandler.ManipulateData(poll_time,endpoll_time,rawPIData,pl.pi_list,pl.getrecent_list,c.VERSION)
        PIDATA = formattedPIData[0].copy()
        Rope = PIDATA['AVsensorRope']['values']
        Nonlin_AVPos = DataConverter.Rope_to_AVPos(Rope)
        formattedPIData[0]['Nonlin_AVPos'] = {}
        
        formattedPIData[0]['Nonlin_AVPos']['values'] = Nonlin_AVPos
        if c.DEBUG is True:
            print("Debug mode: MOST RECENT LOADED PI DATA:")
            print(formattedPIData)
            print("Debug mode: Nonlinear AV Position: ")
            print(Nonlin_AVPos)
        ##Save the data to our couchDB
        #CouchConn.saveEntry(formattedPIData,c.ONEMINDBURL) #Will be from a couchutil instance
        # 
        ##Check data against alarm thresholds; post alarms if needed
        #alarms_last = alarms_dict
        #for timeslot in formattedPIData:
        #    alarms_dict = PiAlarmHandler.checkThresholdAlarms(timeslot,channeldb,alarms_dict,c.VERSION)
        #    if c.DEBUG is True:
        #        print("Debug mode: CURRENT ALARMS:")
        #        print(alarms_dict)
        #    PiAlarmHandler.postAlarmServerAlarms(alarms_dict, alarms_last)
        #    PiAlarmHandler.saveAlarmsToDB(alarms_dict, c.COUCHALARMDBURL,
        #                                  c.COUCHALARMDBVIEW)
        #    PiAlarmHandler.sendAlarmsEmail(alarms_dict, alarms_last, lc.EMAIL_RECIPIENTS_FILE)
        #
        ##Get the lastest channeldb entry in case new alarm thresholds/states were loaded in
        #if channeldb is not None:
        #    channeldb_last = channeldb
        #channeldb = CouchConn.getLatestEntry(c.CHANNELDBURL,c.CHANNELDBVIEW)
        #
        ##if it took >60 seconds to run loop, no waiting; just go to the next data set!
        #offset = (time.time()- c.POLLDELAY*60) - (poll_time + c.POLL_WAITTIME)
        #if c.DEBUG is True:
        #    print("Debug mode:  CURRENT OFFSET FROM PIDB IS "+str(offset)+". GOING TO" +\
        #          " SLEEP MODE if OFFSET<0")
        #if offset<0:
            time.sleep(c.POLL_WAITTIME)
