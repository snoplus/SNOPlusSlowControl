# ------------------ COUCHUTILS ---------------------------#
import time
import couchdb
import re
import sys,logging,socket

CREDENTIALHOME = "/home/uwslowcontrol/config/couchcred.conf"
CLOG_FILENAME = '/home/uwslowcontrol/SNOPlusSlowControl/SNOPlusSlowControl/log/cavitytemp.log' #logfile source
DBNAME = "slowcontrol-data-cavitytemps"
ALARMDB = "slowcontrol-alarms"

# --------- Logger configuration ----------- #
logging.basicConfig(filename=CLOG_FILENAME,level=logging.INFO, \
    format='%(asctime)s %(message)s')
# --------- END Logger configuration -------- #

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

#Connection info for couchdb
couch = couchdb.Server('http://couch.snopl.us')
couchuser, couchpassword = getcreds(CREDENTIALHOME)
couch.resource.credentials = (couchuser, couchpassword)

#Connects to the slow control channeldb and grabs the most recent
#channeldb values.
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
 #Allows one to connect to a couchdb

def connectToDB(dbName):
    status = "ok"
    db = {}
    numtries = 0
    while numtries < 3:
        try:
           db = couch[dbName]
           break
        except:
            print "Failed to connect to " + dbName
            logging.exception("Failed to connect to " + dbName)
            numtries += 1
            logging.info("At try " + str(numtries) + ". Trying again..")
            time.sleep(1)
            status = "bad"
            continue
    return status, db

def saveCTAlarms(alarm_dict):
    dbDataStatus, dbData = connectToDB(ALARMDB)
    if dbDataStatus is "ok":
        if alarm_dict["timestamp"]!="N/A":
            numtries = 0
            while numtries < 3:
                try:
                    dbData.save(alarm_dict)
                    return
	        except socket.error, exc:
	            logging.exception("FAILED TO SAVE ALARM ENTRY" + \
	                "FOR THIS MINUTE.SLEEP, RETRY.")
                    print("FAILED TO SAVE.  DISCONNECTING, TRY AGAIN...")
                    time.sleep(1)
                    dbDataStatus, dbData = connectToDB(ALARMDB)
                    numtries+=1
                    continue
            logging.exception("TRIED 3 TIMES TO SAVE DATA AND FAILED.")
            print("COULD NOT SAVE DATA AFTER THREE TRIES.  WOW")
        else:
            print("Timestamp is invalid.  Check your system time, jeez")

def saveValuesToCT(data):
    dbDataStatus, dbData = connectToDB(DBNAME)
    if dbDataStatus is "ok":
        if data["timestamp"]!="N/A":
            numtries = 0
            while numtries < 3:
                try:
                    dbData.save(data)
                    return
	        except socket.error, exc:
	            logging.exception("FAILED TO SAVE 1 MIN ENTRY" + \
	                "FOR THIS MINUTE.SLEEP, RETRY.")
                    print("FAILED TO SAVE.  DISCONNECTING, TRY AGAIN...")
                    time.sleep(1)
                    dbDataStatus, dbData = connectToDB(DBNAME)
                    numtries+=1
                    continue
            logging.exception("TRIED 3 TIMES TO SAVE DATA AND FAILED.")
            print("COULD NOT SAVE DATA AFTER THREE TRIES.  WOW")
        else:
            print("Timestamp is invalid.  Check your system time, jeez")
#--------------- /COUCHUTILS ------------------------------#
