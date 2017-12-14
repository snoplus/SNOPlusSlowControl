#!/usr/bin/env python
#Luke Kippenbrock on 23 April 2015
#Alarm server features by: Teal Pershing, 28 July 2016

from suds.client import Client
from suds.sudsobject import asdict
import datetime, time, calendar, math, re
import sys,logging, pprint
import socket
import traceback
import couchdb
import smtplib
import mimetypes
import urllib2
import httplib
from email import utils
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
import threading
import psycopg2
from psycopg2.pool import ThreadedConnectionPool

LOG_FILENAME = '/home/uwslowcontrol/pi_db/log/pi_db.log' #logfile source

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


# ---------------BEGIN ALARM SERVER FUNCTIONS--------------------#
ASUser, ASPassword = getcreds("/home/uwslowcontrol/config/alascred.conf")
pool = ThreadedConnectionPool(1,10, host='dbug', database='detector', user=ASUser, password=ASPassword)

def post_alarm(alarm_id):
    """
    Posts an alarm to the database for an alarm with a given id.

    Returns None if there was an error or the alarm was already active.
    If the alarm is successfully posted it returns the unique id of the
    alarm that was posted.
    """

    result = None

    try:
        conn = pool.getconn()
    except psycopg2.Error as e:
        #if the database is down we just print the error
        logging.exeption(str(e))
        print(str(e))     
    else:
        #we have a connection
        try:
            with conn:
                with conn.cursor() as curs:
                    curs.execute("SELECT * FROM post_alarm(%i)" % alarm_id)
                    result = curs.fetchone()[0]
        except psycopg2.Error as e:
            #who knows what went wrong?  Just print the error
            logging.exception(str(e))
            print(str(e))
            #close the connection since it's possible the database
            #is down, so we don't want to use this connection again
            conn.close()
        
        pool.putconn(conn)
    return result

def clear_alarm(alarm_id):
    """
    Clears an alarm from the alarm server for an alarm with a given id.

    Returns None if there was an error or the alarm was already active.
    If the alarm is successfully cleared it returns the unique id of the
    alarm that was cleared.
    """

    result = None

    try:
        conn = pool.getconn()
    except psycopg2.Error as e:
        #if the database is down we just print the error
        logging.exception(str(e))
    else:
        #we have a connection
        try:
            with conn:
                with conn.cursor() as curs:
                    curs.execute("SELECT * FROM clear_alarm(%i)" % alarm_id)
                    result = curs.fetchone()[0]
        except psycopg2.Error as e:
            #who knows what went wrong?  Just print the error
            logging.exception(str(e))
            #close the connection since it's possible the database
            #is down, so we don't want to use this connection again
            conn.close()
        
        pool.putconn(conn)
    return result

def post_heartbeat(name):
    """
    Recursive function that posts a heartbeat to the database every 10 seconds.
    Started once when you run your script.
    See stackoverflow.com/questions/3393612
    """
    try:
        conn = pool.getconn()
    except psycopg2.Error as e:
        #if the database is down we just print the error
        logging.exception(str(e))
    else:
        #we have a connection
        try:
            with conn:
                with conn.cursor() as curs:
                    curs.execute("SELECT * FROM post_heartbeat('%s')" % name)
        except psycopg2.Error as e:
            #who knows what went wrong; just print the error
            logging.exeption(str(e))
            #close the connection since it's possible the database
            #is down, so we don't want to reuse this connection
            conn.close()
        pool.putconn(conn)
    
    t = threading.Timer(10, post_heartbeat, [name])
    t.daemon = True
    t.start()

#------------END ALARM SERVER FUNCTIONS-------------------#


gmailUser, gmailPassword = getcreds("/home/uwslowcontrol/config/gmailcred.conf")
recipientfile = open("/home/uwslowcontrol/pi_db/emailList.txt","r")
recipients = recipientfile.readlines(); 

version = 10
pi_address = "pi:\\\\pi.snolab.ca\\"

#DeltaV channels and specifications
pi_list =[{"dbname":"UPW_plant_temp","channels":[1],"address":"DeltaV_311-TIT-146/AI1/PV.CV","method":1},\
              {"dbname":"cavity_water_level","channels":[1],"address":"DeltaV_311-PT087/SCLR1/OUT.CV","method":1},\
              {"dbname":"holddown_rope","channels":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20],"address":"DeltaV_HDLC-AI-%02d/AI1/PV.CV","method":2},\
              {"dbname":"holdup_rope","channels":[1,2,3,4,5,6,7,8,9,10],"address":"DeltaV_AVLC-AI-%02d/AI1/PV.CV","method":2},\
              {"dbname":"equator_monitor","channels":[2,4,7,9],"address":"DeltaV_AVEQ-%02d/ALM1/PV.CV","method":2},\
              {"dbname":"cover_gas","channels":[1,2,3,4,5],"address":"DeltaV_UI_CG_%s/AI1/PV.CV","appendage":["UPPERBAG","MIDDLEBAG","LOWERBAG","O2","PT"],"method":3},\
              {"dbname":"AV_direction","channels":[1,2,3],"address":"DeltaV_AVDIR%d/ALM1/PV.CV","method":2},\
              {"dbname":"AV_height","channels":[1],"address":"DeltaV_AV-HEIGHT/ALM1/PV.CV","method":1},\
              {"dbname":"AV_buoyant_force","channels":[1],"address":"DeltaV_AV_CALCS/AV_BUOYANT_FORCE/PV.CV","method":1},\
              {"dbname":"AV_inner_weight","channels":[1],"address":"DeltaV_AV_CALCS/AV_INNER_WEIGHT/PV.CV","method":1},\
              {"dbname":"AV_total_force","channels":[1],"address":"DeltaV_AV_CALCS/AV_TOTAL_FORCE/PV.CV","method":1},\
              {"dbname":"creep","channels":[1],"address":"DeltaV_AV_CALCS/CREEP/PV.CV","method":1},\
              {"dbname":"hooke_law_psn","channels":[1],"address":"DeltaV_AV_CALCS/HOOKE_LAW_PSN/PV.CV","method":1},\
              {"dbname":"zerocreep_exp_dn","channels":[1],"address":"DeltaV_AV_CALCS/ZEROCREEP_EXP_DN/PV.CV","method":1},\
              {"dbname":"zerocreep_exp_up","channels":[1],"address":"DeltaV_AV_CALCS/ZEROCREEP_EXP_UP/PV.CV","method":1},\
              {"dbname":"down_torque_x","channels":[1],"address":"DeltaV_AV_CALCS_2/DOWN_TORQUE_X.CV","method":1},\
              {"dbname":"down_torque_y","channels":[1],"address":"DeltaV_AV_CALCS_2/DOWN_TORQUE_Y.CV","method":1},\
              {"dbname":"upward_torque_x","channels":[1],"address":"DeltaV_AV_CALCS_2/UPWARD_TORQUE_X.CV","method":1},\
              {"dbname":"upward_torque_y","channels":[1],"address":"DeltaV_AV_CALCS_2/UPWARD_TORQUE_Y.CV","method":1},\
              {"dbname":"cavity_bubbler","channels":[1],"address":"DeltaV_311-PT087/AI1/PV.CV","method":1},\
              {"dbname":"AV_inside_bubbler","channels":[1],"address":"DeltaV_321-PT410/AI1/PV.CV","method":1},\
              {"dbname":"AV_outside_bubbler","channels":[1],"address":"DeltaV_321-PT411/AI1/PV.CV","method":1},\
              {"dbname":"control_room_temp","channels":[1],"address":"BACnet_682100_SNO_AHU2_CTRL_RMT_TL Archive","method":1},\
              {"dbname":"deck_humidity","channels":[1],"address":"BACnet_682100_SNO_AHU2_DEC_RH_TL Archive","method":1},\
              {"dbname":"deck_temp","channels":[1],"address":"BACnet_682100_SNO_AHU2_DECK_RMT_TL Archive","method":1},\
              {"dbname":"AVsensorRope","channels":[1,2,3,4,5,6,7],"address":"DeltaV_SENSE_ROPE_%s/CALC1/OUT1.CV","appendage":["A","B","C","D","E","F","G"],"method":3},\
              {"dbname":"CavityRecircValveIsOpen","channels":[1,2,3,4],"address":"DeltaV_V-%s/DO1/PV_D.CV","appendage":["174","175","176","178-179"],"method":3},\
              {"dbname":"AVRecircValveIsOpen","channels":[1,2],"address":"DeltaV_V-%s/DO1/PV_D.CV","appendage":["754","755"],"method":3},\
              {"dbname":"AVneck","channels":[1,2,3,4,5,6],"address":"DeltaV_SENSE_CALCS/CALC1/OUT%s.CV","appendage":["1","2","3","4","5","6"],"method":3},\
              {"dbname":"P15IsRunning","channels":[1],"address":"DeltaV_311-P15/P15_RUNNING/PV_D.CV","method":1},\
              {"dbname":"AV_dP","channels":[1],"address":"DeltaV_321-DPT002/SCLR1/OUT.CV","method":1}]
#              {"dbname":"BAC","channels":[1,2,3],"address":"BACNet_682100_SNO_AHU2_%s_TL Archive","appendage":["CTRL_RMT","DEC_RH","DECK_RMT"],"method":3}]
#Any dbs not in this list will search for new data in the most recent minute according to now's time
#Any dbs in this list grab the most recent data point in the PI server
getrecent_list = ["deck_humidity","deck_temp","control_room_temp","cover_gas","equator_monitor","AVsensorRope","AVneck",\
        "CavityRecircValveIsOpen","AVRecircValveIsOpen","P15IsRunning"]

#Connection info for couchdb
couch = couchdb.Server('http://couch.snopl.us')
couchuser, couchpassword = getcreds("/home/uwslowcontrol/config/couchcred.conf")
couch.resource.credentials = (couchuser, couchpassword)
couch.resource.session.timeout = 15

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
	msg['To'] = "alarmslist"
	mailServer.sendmail(gmailUser, recipients, msg.as_string())
	mailServer.close()
    except:
        pass
    return 


#Allows one to connect to a couchdb
def connectToDB(dbName):
    status = "ok"
    db = {}
    numtries = 0
    while numtries < 3:
        try:
           db = couch[dbName]
           break
        except socket.error, exc:
            print "Failed to connect to " + dbName
            logging.exception("Failed to connect to " + dbName)
            numtries += 1
            logging.info("At try " + str(numtries) + ". Trying again..")
            time.sleep(1)
            status = "bad"
            continue
        except httplib.INTERNAL_SERVER_ERROR:
            print "Failed to connect to " + dbName
            logging.exception("Server error: Failed to connect to " + dbName)
            numtries += 1
            logging.info("At try " + str(numtries) + ". Trying again..")
            time.sleep(1)
            status = "bad"
            continue
    return status, db


#Gets most recent timestamp from db
def starter():
    db1minStatus, db1min = connectToDB("slowcontrol-data-1min")
    if db1minStatus is "ok":
        queryresults =  db1min.view("slowcontrol-data-1min/pi_db",descending=True,limit=1) 
    try:
        latest_time = int(queryresults.rows[0].value["timestamp"])
    except:
        latest_time = 1326899640
    return latest_time


#Finds the "minute" of a Unix timestamp                                  
def unix_minute(unix_time):
    unix_minute = int(math.floor(unix_time/60.))
    return unix_minute


#Converts unix timestamp to human readable local time (Sudbury time)
def unix_to_human(unix_time):
    human_time = utils.formatdate(unix_time, localtime=True)
    return human_time


# Converts UTC-5 date-time to unix timestamp
def dmy_to_unix(dmy_time):
    unix_time = "%s" % dmy_time
    unix_time = unix_time[0:18]
    unix_time = int(calendar.timegm(time.strptime(unix_time, '%Y-%m-%d %H:%M:%S')))
    return unix_time


#Converts unix timestamp to UTC-5 date-time
def unix_to_dmy(unix_time):
    dmy_time = datetime.datetime.utcfromtimestamp(unix_time)
    return dmy_time

# --------- Logger configuration ----------- #
logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO, \
    format='%(asctime)s %(message)s')
logging.info('PI_DB SCRIPT INITIALIZING...')

#Define what we want our system exception hook to do at an
#uncaught exception
def UE_handler(exec_type, value, tb):
    logging.exception("Uncaught exception: {0}".format(str(value)))
    logging.exception("Error type: " + str(exec_type))
    logging.exception("Traceback: " + str(traceback.format_tb(tb)))

#At an uncaught exception, run our handler
sys.excepthook = UE_handler

# --------- END Logger configuration -------- #

#PI database information
timeseries_url = 'http://pi.snolab.ca/PIWebServices/PITimeSeries.svc?wsdl'
try:
    timeseries_client = Client(timeseries_url)
except urllib2.URLError:
    logging.info("Unable to connect to PI database.  Check status of pi_" +\
    "db at SNOLAB.")
    raise

piarcdatarequest = timeseries_client.factory.create('PIArcDataRequest')

#For a channel, gets the most recent datapoint from the database 
def get_pi_snapshot(machine_index,address,channel_number):
    method = pi_list[machine_index]["method"]
    if method==1:
        thepath = address
    if method==2:
        thepath = address % (channel_number)
    if method==3:
        thepath = address % (pi_list[machine_index]["appendage"][channel_number-1])
    requests = timeseries_client.factory.create('ArrayOfString')
    requests.string.append(str(thepath))
    try:
        returned_arcdata = timeseries_client.service.GetPISnapshotData(requests)                                                
    except:
        logging.exception("Issue Querying PI Server.  In except loop, trying again..")
        returned_arcdata = timeseries_client.service.GetPISnapshotData(requests)                                                
    return returned_arcdata

#For a channel, gets values and timestamps from start_time to end_time 
def get_pi(start_time,end_time,machine_index,address,channel_number):
    piarcdatarequest.TimeRange.Start = start_time
    piarcdatarequest.TimeRange.End = end_time
    piarcdatarequest.PIArcManner._NumValues = '6000'
    method = pi_list[machine_index]["method"]
    if method==1:
        piarcdatarequest.Path = address
    if method==2:
        piarcdatarequest.Path = address % (channel_number)
    if method==3:
        piarcdatarequest.Path = address % (pi_list[machine_index]["appendage"][channel_number-1])
    requests = timeseries_client.factory.create('ArrayOfPIArcDataRequest')
    requests.PIArcDataRequest = [piarcdatarequest]
    try:
        returned_arcdata = timeseries_client.service.GetPIArchiveData(requests)                                                
    except:
        logging.exception("Issue querying PI server.  In except loop, trying again..")
        returned_arcdata = timeseries_client.service.GetPIArchiveData(requests)                                                
    return returned_arcdata


#For each channel, reorganizes and stores values and timestamps in a dict
def getValues(start_time,end_time,pi_list):
    rawdata = pi_list
    for machine_index, machine in enumerate(pi_list):
        dbname = machine["dbname"]
        address = machine["address"]
        channel_numbers_list = machine["channels"]
        machine["data"] = []
        if dbname in getrecent_list:
            for channel_number in channel_numbers_list:
                machine["data"].append(get_pi_snapshot(machine_index,pi_address+address,channel_number))    
        else:
            for channel_number in channel_numbers_list:
                machine["data"].append(get_pi(start_time,end_time,machine_index,pi_address+address,channel_number))    
    return rawdata


#Takes rawdata and puts it in couchdb format
def ManipulateData(start_time,end_time,rawdata):
    start_minute = unix_minute(start_time)
    time_bins = unix_minute(end_time)-start_minute
    pi_data = []
    data_format = {"timestamp":"N/A","sudbury_time":"N/A","version":version,"pi_db":"true"}
    for machine in pi_list:
        data_format[machine["dbname"]] = {"values":["N/A"]*len(machine["channels"])}
    pi_data.append(data_format)
    for ropetype_index, ropetype in enumerate(rawdata):
        for rope_number, rope_data in enumerate(ropetype["data"]):
            realrope = rope_data.TimeSeries[0]
            if realrope.TimedValues != None:
                 for timestep in realrope.TimedValues[0]:
                      #This if makes setting the timestamp of the document specific to
                      #Datapoints that don't just grab the most recent point in a database
                      #It's silly to set the timestamp at every entry, but I'll leave it 
                      if pi_list[ropetype_index]["dbname"] not in getrecent_list:
                          timestamp_minute = unix_minute(dmy_to_unix(timestep._Time))
                          timestamp = (timestamp_minute)*60
                          #print index, timestamp, timestep._Time
                          try:
                              pi_data[0]["timestamp"] = timestamp
                              pi_data[0]["sudbury_time"] = unix_to_human(timestamp)
                          except:
                              pass
                      try:
                          chan_value = timestep.value
                          val = float(chan_value)
                          pi_data[0][pi_list[ropetype_index]["dbname"]]["values"][rope_number] = val
                      except:
                          #FIXME: One of the cover gas lines is disabled. floods log
                          if str(pi_list[ropetype_index]["dbname"]) != "cover_gas":
                              logging.info("There was an issue getting a channel value for: " + \
                                     str(pi_list[ropetype_index]["dbname"]) + ".  Leaving as N/A")
    return pi_data


#Puts elements of dict in couchdb
def saveValues(data):
    dbDataStatus, dbData = connectToDB("slowcontrol-data-1min")
    if dbDataStatus is "ok":
        for element in data:
            if element["timestamp"]!="N/A":
                counter = 0
                while counter < 3:
    		    try:
                        dbData.save(element)
                        return
		    except socket.error, exc:
		        logging.exception("FAILED TO SAVE 1 MIN ENTRY" + \
		        "FOR THIS MINUTE.  ERROR: " + str(exc))
                        logging.exception("SLEEP, TRY AGAIN...")
                        time.sleep(1)
                        counter += 1
                        dbDataStatus, dbData = connectToDB("slowcontrol-data-1min")
                        continue
                logging.exception("TRIED TO SAVE 1 MIN DATA THREE TIMES AND FAILED." + \
                        "There was data; just couldn't connect to couchdb.")
                 


#Connects to channeldb to get alarm parameters
def getChannelParameters(channeldb_last):                                                                         
    channeldb = {}                                                                                    
    counter = 0
    dbParStatus, dbPar = connectToDB("slowcontrol-channeldb")                                       
    if dbParStatus is "ok":
        while counter < 3:                                                                         
            try:
                queryresults =  dbPar.view("slowcontrol/recent",descending=True,limit=1)                    
                channeldb = queryresults.rows[0].value
                return channeldb
            except socket.error, exc:
                logging.exception("Failed to view channeldb database." + \
                    "sleeping, trying again... ERR: " + str(exc))
                time.sleep(1)
                counter += 1
                dbParStatus, dbPar = connectToDB("slowcontrol-channeldb")
                continue
    else:
        logging.exception("IN getChannelParameters: could not connect" + \
            " to slowcontrol-channeldb. returning last channeldb dict.")
    return channeldb_last
   


#Compares pi_data to channeldb alarm parameters
def checkThresholdAlarms(pi_data, channeldb, alarms):
    alarms_last = alarms
    alarms = {}
    alarms_dict = {}
    alarms_dict["timestamp"] = int(time.time())
    alarms_dict["sudbury_time"] = unix_to_human(alarms_dict["timestamp"])
    alarms_dict["version"] = version
    for name in pi_list:
        alarms[name["dbname"]] = [0]*len(name["channels"])
        alarms_dict[name["dbname"]] = []
    for channel in channeldb["deltav"]:
        dbname = channel["type"]
        chn_number = channel["id"]-1
        chn_value = pi_data[dbname]["values"][chn_number]
        isEnabled = 0
        try:
            isEnabled = channel["isEnabled"]
        except:
            isEnabled = 0
        if isEnabled>0:
            if chn_value<channel["lolo"] or chn_value>channel["hihi"]:
                alarms[dbname][chn_number] = 2
            elif chn_value<channel["lo"] or chn_value>channel["hi"]:
                alarms[dbname][chn_number] = 1
            if chn_value =="N/A":
                alarms[dbname][chn_number] = 0
        isAlarm = 0
        this_alarm ={}
        if alarms_last:
            if alarms[dbname][chn_number]>0 and alarms_last[dbname][chn_number]>0:
                isAlarm = 1
                if alarms[dbname][chn_number]==1:
                    this_alarm["reason"] = "alarm"
                if alarms[dbname][chn_number]==2:
                    this_alarm["reason"] = "action"
        if isAlarm>0:
            this_alarm["channel"] = chn_number
            this_alarm["value"] = chn_value
            this_alarm.update(channel)
            del this_alarm["isEnabled"]
            del this_alarm["multiplier"]
            alarms_dict[dbname].append(this_alarm)
    return alarms, alarms_dict

#Posts any rope alarms to the Alarm Server, clears items no longer alarming
def PostAlarmServerAlarms(alarms_dict,alarms_last):
    #only check alarms_dict entries associated with databases
    nowalarming = []    
    aldict_entries = []
    for item in pi_list:
        aldict_entries.append(item["dbname"])
    for entry in aldict_entries:
        for channel in alarms_dict[entry]:
 	    if (channel["reason"] == "action") or (channel["reason"] == "alarm"):
	       post_alarm(channel["alarmid"])
               nowalarming.append(channel["alarmid"])
    #If the detector item has no alarms, clear alarms on that component
    counter = 0
    while counter < 3:
        try:
    	    for entry in aldict_entries:
                for channel in alarms_last[entry]:
                    if channel["alarmid"] not in nowalarming:
                        clear_alarm(channel["alarmid"])
            return
        except:
            logging.info("Alarms Last likely empty from a connection error." + \
                 " Trying to get Aarms last from database...")
            counter+=1
            alarms_last = getPastAlarms()
            continue
    logging.exception("Could not clear alarms because could not" + \
           "Access the last alarms from couchdb.") 
    


def getPastAlarms():
    """
    Pull the most recent alarms from the database.  Use these for initial
    posting/clearing of alarms from alarm server.
    """
    dbStatus, db = connectToDB("slowcontrol-alarms")
    if dbStatus is "ok":
        counter = 0
        while counter < 3:
            try:
                queryresults =  db.view("slowcontrol-alarms/pi_db",descending=True,limit=1)
                num_rows = queryresults.total_rows
            except socket.error,exc:
                logging.exception("IN getPastAlarms: Failed to view database" + \
                    "for past alarms.  Re-try connection.")
                counter += 1
                time.sleep(1)
                dbStatus, db = connectToDB("slowcontrol-alarms")
                continue
            break
        if num_rows>0:
            alarms_in_db = queryresults.rows[0].value
	else:
	    print("Could not get most recent alarms in DB.  Continuing..")
            alarms_in_db = {}
    else:
        logging.exeption("IN getPastAlarms(): could not connect to" + \
            "couchDB slowcontrol-alarms/pi_db database.")
        print("could not connect to couchDB alarm database.")
	alarms_in_db = {}
    return alarms_in_db


#Saves alarms_dict to alarms db
def saveAlarms(alarms_dict,alarms_last,channeldb):
    dbStatus, db = connectToDB("slowcontrol-alarms")
    if dbStatus is "ok":
        counter = 0
        while counter < 3:
            try:
                queryresults =  db.view("slowcontrol-alarms/pi_db",descending=True,limit=1)
                num_rows = queryresults.total_rows
            except socket.error,exc:
                logging.exception("IN saveAlarms: Failed to view database" + \
                    "for past alarms.  Re-try connection.")
                counter += 1
                time.sleep(1)
                dbStatus, db = connectToDB("slowcontrol-alarms")
                continue
            break
        if num_rows>0:
            alarms_in_db = queryresults.rows[0].value
            match = 1
            for channel in channeldb["deltav"]:
                dbname = channel["type"]
                try:
                    if len(alarms_dict[dbname]) == len(alarms_in_db[dbname]):
                        for alarm_num in range(len(alarms_in_db[dbname])):
                            if (alarms_dict[dbname][alarm_num]["channel"]!=alarms_in_db[dbname][alarm_num]["channel"] or 
                                alarms_dict[dbname][alarm_num]["reason"]!=alarms_in_db[dbname][alarm_num]["reason"]):
                                match = 0
                    else:
                        match = 0
                except:
                    match = 0
            if match==0:
		try:
                    db.save(alarms_dict)
		except socket.error, exc:
		    logging.exception("FAILED TO SAVE ALARMS DICT ENTRY" + \
		    "FOR THIS MINUTE.  ERROR: " + str(exc))
		    logging.exception("ALARM ENTRY: " + str(alarms_dict))
                printAlarms(alarms_dict,alarms_last)
        else:
	    try:
                db.save(alarms_dict)
	    except socket.error, exc:
	        logging.exception("FAILED TO SAVE ALARMS DICT ENTRY" + \
		    "FOR THIS MINUTE.  ERROR: " + str(exc))
		logging.exception("ALARM ENTRY: " + str(alarms_dict))
            printAlarms(alarms_dict,alarms_last)

#Sends alarms email
def printAlarms(alarms_dict,alarms_last):
    title = "DeltaV Alarms at " + time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(alarms_dict["timestamp"])) + "\n\n"
    old_list = []
    new_list = []
    new_alarm_dict = {}
    for machine in pi_list:
        dbname = machine["dbname"]
        if alarms_last != {}:
             for alarm_num in range(len(alarms_last[dbname])):
                  channel_id = str(alarms_last[dbname][alarm_num]["id"])
                  channel_type = str(alarms_last[dbname][alarm_num]["type"]) 
                  channel_signal = str(alarms_last[dbname][alarm_num]["signal"])
                  old_list.append(channel_type+"-"+channel_id+" ("+channel_signal+")")
        for alarm_num in range(len(alarms_dict[dbname])):
             channel_id = str(alarms_dict[dbname][alarm_num]["id"])
             channel_type = str(alarms_dict[dbname][alarm_num]["type"]) 
             channel_signal = str(alarms_dict[dbname][alarm_num]["signal"])
             new_list.append(channel_type+"-"+channel_id+" ("+channel_signal+")")
             msg = channel_type + "-" + channel_id + " (" + channel_signal + ")\n"
             unit = alarms_dict[dbname][alarm_num]["unit"]
             reason = alarms_dict[dbname][alarm_num]["reason"]
             hi = "hi"
             lo = "lo"
             if reason =="action":
                  hi = "hihi"
                  lo = "lolo"
             msg = msg + "Signal: " + str(alarms_dict[dbname][alarm_num]["value"]) + " " + unit
             msg = msg + " outside " + reason + " limits of " + str(alarms_dict[dbname][alarm_num][lo]) + " " + unit
             msg = msg + " to " + str(alarms_dict[dbname][alarm_num][hi]) + " " + unit + "\n\n"
             new_alarm_dict[channel_type+"-"+channel_id+" ("+channel_signal+")"] = msg
    constant_alarms = set(old_list) & set(new_list)
    new_alarms = set(new_list) - set(old_list)
    no_longer_alarms = set(old_list) - set(new_list)
    super_msg = title
    if new_alarms != set([]):
         super_msg = super_msg + "New Alarms:" + "\n\n"
         for x in new_alarms:
              super_msg = super_msg + new_alarm_dict[x]
    if no_longer_alarms != set([]):
         super_msg = super_msg + "No longer Alarms:" + "\n\n"
         for z in no_longer_alarms:
              super_msg = super_msg + z + "\n\n"
    if constant_alarms != set([]):
         super_msg = super_msg + "Constant Alarms:" + "\n\n"
         for y in constant_alarms:
              super_msg = super_msg + new_alarm_dict[y]
    if super_msg != title:
         sendMail("Alarms at " + time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(alarms_dict["timestamp"])), super_msg)


#Actual code
#------------------------------------------------------------------------------------------------------------

delay = 5  #in minutes 
poll_time = (unix_minute(time.time())-delay)*60
wait_time = 60 # in seconds
pollrange = 60 # in seconds; indicates time past "poll_time" that will be probed in the PI Database


#define alarm structures
alarms = {}
alarms_dict = {}
alarms_last = {}
previous_new_alarms = []
previous_no_longer_alarms = []

#Start Alarm Server Heartbeat daemon
post_heartbeat('MinardSC')

#Start by knowing the alarms status in the most recent database entry
alarms_last = getPastAlarms()

#Initial init of channeldb
channeldb_last = {}


#script loop
while(1):
    endpoll_time = poll_time+pollrange
    rawdata = getValues(poll_time,endpoll_time,pi_list)
    pi_data = ManipulateData(poll_time,endpoll_time,rawdata)
    #print pi_data
    saveValues(pi_data)
    channeldb = getChannelParameters(channeldb_last)
    for timeslot in pi_data:
        alarms, alarms_dict = checkThresholdAlarms(timeslot,channeldb,alarms)
        PostAlarmServerAlarms(alarms_dict, alarms_last)
	saveAlarms(alarms_dict,alarms_last,channeldb)
    alarms_last = alarms_dict
    if channeldb is not None:
        channeldb_last = channeldb
    offset = (time.time()- delay*60) - (poll_time + wait_time) #if time taken to grab data >60 seconds, no waiting; just go to the next data set!
    if offset<0:
        time.sleep(wait_time)
    poll_time = (unix_minute(time.time())-delay)*60
