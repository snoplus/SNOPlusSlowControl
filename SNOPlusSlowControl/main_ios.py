#!/usr/bin/env python
#Original scripts by: Luke Kippenbrock on 23 April 2015
#Alarm server features by: Teal Pershing, 28 July 2016
#Restructured into classes/libraries by: Teal Pershing, 28 Oct 2018

import datetime, time, calendar, math, re
import sys, pprint
import smtplib
import socket
import json
import os

import lib.timeconverts as tc
import lib.thelogger as l
import lib.alarmserver as als
import lib.ios_alarmhandler as alh
import lib.rackcontroller as rh
import lib.ios_grabber as iosg

import lib.config.iosconfig as c
import lib.config.logconfig as lc
import lib.config.alarmdbconfig as ac

import lib.couchutils as cu
import lib.credentials as cr

#get the pat of this file
path = os.path.dirname(__file__)
pathstring = os.path.abspath(path)
dbpath = os.path.abspath(os.path.join(path,"DB/localcdb.json"))
#At an uncaught exception, run our handler
sys.excepthook = l.UE_handler

#Initialize home logger
logger = l.get_logger(__name__)
logger.info('IOS POLLING SCRIPT INITIALIZING...')

#Quick check that configuration matches number hardware is labeled as
ios_num_inhardware = socket.gethostname()[3]
if int(c.IOSNUM) != int(ios_num_inhardware):
    logger.exception("WARNING: YOUR CONFIG FILE'S IOS NUMBER DOES NOT MATCH THAT IN THE HOSTNAME")
    sys.exit(0)

if __name__ == '__main__':


    #Initialize Alarm poster and get heartbeat going
    AlarmPoster = als.AlarmPoster(alarmhost=ac.ALARMHOST,psql_database=ac.ALARMDBNAME)
    AlarmPoster.startConnPool()
    AlarmPoster.post_heartbeat(c.ALARMHEARTBEAT,beat_interval=c.ALARMBEATINTERVAL)
    
    #Initialize CouchDB connction.  Also get current channeldb
#Connection info for couchdb
    with open(dbpath,"r") as read_file:
        default_channeldb = json.load(read_file)
    ChannelDBConn = cu.CouchDBConn()
    ChannelDBConn.getServerInstance(c.CHDBADDRESS,c.CHDBCREDS)
    CouchConn = cu.IOSCouchConn(c.IOSNUM)
    CouchConn.getServerInstance(c.SCCOUCHADDRESS,c.SCCOUCHCREDS)
    channeldb = ChannelDBConn.getLatestEntry(c.CHANNELDBURL,c.CHANNELDBVIEW)
    channeldb = channeldb.get("ioss",default_channeldb)[c.IOSNUM-1]
    with open(dbpath,"w") as write_file:
        json.dump(channeldb,write_file,sort_keys=True,indent=4)
    logger.info("Main IOS script: GOT LATEST ENTRY OF CHANNELDB")
    if c.DEBUG is True:
        print("FIRST CHANNELDB ENTRY:")
        print(channeldb)
    alarms_dict = CouchConn.getLatestEntry(c.COUCHALARMDBURL,c.COUCHALARMDBVIEW)
    if c.DEBUG is True:
        print("FIRST ALARMS DICTIONARY LOADED FROM COUCHDB:")
        print(alarms_dict)
    
    #Initialize Alarm Handler; uses an AlarmPoster class to post alarms
    #Based on what readings in the PI database are alarming
    AlarmHandler = None
    RackController = None
    if c.IOSNUM==2:
        AlarmHandler =	alh.IOSRackAlarmHandler(CouchConn,AlarmPoster,c.IOSNUM)
        AlarmHandler.clearAllAlarms(channeldb)
        SNORackController = rh.RackController(c.RACKCONTROLHOST,c.RACKCONTROLPORT)
    else:
        AlarmHandler = alh.IOSAlarmHandler(CouchConn,AlarmPoster,c.IOSNUM)
        AlarmHandler.clearAllAlarms(channeldb)
    
    #Initialze the IOS data handler
    IOSDataHandler = iosg.IOSDataHandler(c.IOSNUM)
    cardHardwareConfig = IOSDataHandler.setIOSCardSpecs(c.IOSCARDCONF)
    if c.DEBUG is True:
        print("CARD HARDWARE DICT IS...")
	print(cardHardwareConfig)
    IOSDataHandler.connectToIOSServer()

    #Grab a first set of alarms to compare to upcoming data
    alarms = {}  #Dictionary filled with alarm types for each channel on
                 #each card (warning, action, off, etc.)
    #Have the IOS data handler grab and manipulate data
    ios_data = IOSDataHandler.getChannelVoltages(channeldb)
    alarms, alarms_last = AlarmHandler.checkThresholdAlarms(ios_data,channeldb,alarms,c.VERSION)
    
    while True:
        #Have the IOS data handler grab and manipulate data
        ios_data = IOSDataHandler.getChannelVoltages(channeldb)
        if c.DEBUG is True:
            print("MOST RECENT IOS DATA:")
            print(ios_data)
        #Save the data to our couchDB
        CouchConn.saveEntry(ios_data,c.FIVESECDBURL) #Will be from a couchutil instance
        
        #Check data against alarm thresholds; post alarms if needed
        alarms, alarms_dict = AlarmHandler.checkThresholdAlarms(ios_data,channeldb,alarms,c.VERSION)
        if c.IOSNUM==2:
            #IOS2 also does rack alarm handling!
            onracks, IBootPwr = SNORackController.GetPoweredRacks()
            numlowvolts_perrack = AlarmHandler.getLowVoltList(ios_data,channeldb, threshold=c.LOWVOLTTHRESH)
            alarms_dict = AlarmHandler.disableOffRackAlarms(numlowvolts_perrack,alarms_dict, cardHardwareConfig, onracks, IBootPwr)
            SNORackController.updateShutdownCounters(alarms_dict, cardHardwareConfig)
            if c.DEBUG is True:
                print("CURRENT STATUS OF RACK SHUTDOWN COUNTERS:")
                print(SNORackController.counters)
            SNORackController.initiateShutdownMessages(lc.EMAIL_RECIPIENTS_FILE,warning_time=20, action_time=420) 
        if c.DEBUG is True:
            print("CURRENT ALARMS:")
            print(alarms_dict)
        AlarmHandler.postAlarmServerAlarms(alarms_dict, alarms_last,cardHardwareConfig)
        AlarmHandler.sendAlarmsEmail(alarms_dict, alarms_last,channeldb, lc.EMAIL_RECIPIENTS_FILE)
        
        #Get the lastest channeldb entry in case new alarm thresholds/states were loaded in
        if channeldb is not None:
            channeldb_last = channeldb
        channeldb = ChannelDBConn.getLatestEntry(c.CHANNELDBURL,c.CHANNELDBVIEW)
        channeldb = channeldb["ioss"][c.IOSNUM-1]
        
        with open(dbpath,"w") as write_file:
             json.dump(channeldb,write_file,sort_keys=True,indent=4)
	#Take a break
        alarms_last = alarms_dict
        time.sleep(c.POLL_WAITTIME)
