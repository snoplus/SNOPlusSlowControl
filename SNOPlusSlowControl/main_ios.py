#!/usr/bin/env python
#Original scripts by: Luke Kippenbrock on 23 April 2015
#Alarm server features by: Teal Pershing, 28 July 2016
#Restructured into classes/libraries by: Teal Pershing, 28 Oct 2018

import datetime, time, calendar, math, re
import sys, pprint
import smtplib

import lib.timeconverts as tc
import lib.thelogger as l
import lib.alarmserver as als
import lib.alarmhandler as alh
import lib.rackhandler as rh
import lib.ios_grabber as iosg
import lib.config.iosconfig as c
import lib.couchutils as cu
import lib.credentials as cr
import channelDB.pilist as pl

#At an uncaught exception, run our handler
sys.excepthook = l.UE_handler

#Initialize home logger
logger = l.get_logger(__name__)
logger.info('IOS POLLING SCRIPT INITIALIZING...')

#Quick check that configuration matches number hardware is labeled as
ios_num_inhardware = socket.gethostname()[3]
if c.IOSNUM != ios_num_inhardware:
    logger.info("WARNING: YOUR CONFIG FILE'S IOS NUMBER DOES NOT MATCH THE LABEL AS GIVEN ON SERVER")

if __name__ == '__main__':


    #Initialize Alarm poster and get heartbeat going
    AlarmPoster = als.AlarmPoster(alarmhost=c.ALARMHOST,psql_database=c.ALARMDBNAME)
    AlarmPoster.startConnPool()
    AlarmPoster.post_heartbeat(c.ALARMHEARTBEAT,beat_interval=c.ALARMBEATINTERVAL)
    
    #Initialize CouchDB connction.  Also get current channeldb
    CouchConn = cu.IOSCouchConn(c.IOSNUM)
    CouchConn.getServerInstance(c.COUCHADDRESS,c.COUCHCREDS)
    channeldb = CouchConn.getLatestEntry(c.CHANNELDBURL,c.CHANNELDBVIEW)
    print("GOT LATEST ENTRY OF CHANNELDB")
    if c.DEBUG is True:
        print("FIRST CHANNELDB ENTRY:")
        print(channeldb)
    alarms_dict = CouchConn.getLatestEntry(c.ALARMDBURL,c.ALARMDBVIEW)
    if c.DEBUG is True:
        print("FIRST ALARMS DICTIONARY LOADED FROM COUCHDB:")
        print(alarms_dict)
    
    #Initialize Alarm Handler; uses an AlarmPoster class to post alarms
    #Based on what readings in the PI database are alarming
    AlarmHandler = None
    RackController = None
    if c.IOSNUM==2:
        AlarmHandler = alh.IOSRackAlarmHandler(CouchConn,AlarmPoster)
        AlarmHandler.clearAllAlarms(channeldb)
        SNORackController = rh.RackController(c.RACKCONTROLHOST,c.RACKCONTROLPORT)
    else:
        AlarmHandler = alh.IOSAlarmHandler(CouchConn,AlarmPoster)
        AlarmHandler.clearAllAlarms(channeldb)
    
    #Initialze the IOS data handler
    IOSDataHandler = iosg.IOSDataHandler()
    cardHardwareConfig = IOSDataHandler.setIOSCardSpecs(c.IOSCARDCONF)
    IOSDataHandler.connectToIOSServer()

    while True:
        #Have the IOS data handler grab and manipulate data
        ios_data = IOSDataHandler.getChannelVoltages(channeldb)
        
        #Save the data to our couchDB
        CouchConn.saveEntry(formattedPIData,c.FIVESECDBURL) #Will be from a couchutil instance
        
        #Check data against alarm thresholds; post alarms if needed
        alarms_last = alarms_dict
        alarms_dict = AlarmHandler.checkThresholdAlarms(ios_data,channeldb,alarms_dict,c.VERSION)
        if c.DEBUG is True:
            print("CURRENT ALARMS:")
            print(alarms_dict)
        if c.IOSNUM==2:
            #IOS2 also does rack alarm handling!
            onracks, IBootPwr = SNORackController.GetPoweredRacks()
            numlowvolts_perrack = AlarmHandler.GetLowVoltList(ios_data,channeldb, threshold=c.LOWVOLTTHRESH)
            alarms_dict = AlarmHandler.DisableOffRackAlarms(numlowvolts_perrack,alarms_dict, cardHardwareConfig, onracks, IBootPwr)
            SNORackController.UpdateShutdownCounters(alarms_dict, cardHardwareConfig)
            SNORackcontroller.initiateShutdownMessages(warning_time=20, action_time=420) 
        AlarmHandler.postAlarmServerAlarms(alarms_dict, alarms_last,cardHardwareConfig)
        AlarmHandler.sendAlarmsEmail(alarms_dict, alarms_last, c.MAILRECIPIENTLISTFILE)
        
        #Get the lastest channeldb entry in case new alarm thresholds/states were loaded in
        if channeldb is not None:
            channeldb_last = channeldb
        channeldb = CouchConn.getLatestEntry(c.CHANNELDBURL,c.CHANNELDBVIEW)
        
        #Take a break
        time.sleep(c.POLL_WAITTIME)
