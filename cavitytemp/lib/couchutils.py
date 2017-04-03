# ------------------ COUCHUTILS ---------------------------#
import time
import couchdb
import re
import sys,logging,socket

CREDENTIALHOME = "/home/uwslowcontrol/config/couchcred.conf"
CLOG_FILENAME = '/home/uwslowcontrol/pi_db/log/cavitytemp.log' #logfile source
DBNAME = "slowcontrol-data-cavitytemps"

# --------- Logger configuration ----------- #
logging.basicConfig(filename=CLOG_FILENAME,level=logging.INFO, \
    format='%(asctime)s %(message)s')

#Define what we want our system exception hook to do at an
#uncaught exception
#def UE_handler(exec_type, value, tb):
#    logging.exception("Uncaught exception: {0}".format(str(value)))
#    logging.exception("Error type: " + str(exec_type))
#    logging.exception("Traceback: " + str(traceback.format_tb(tb)))

#At an uncaught exception, run our handler
#sys.excepthook = UE_handler

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
