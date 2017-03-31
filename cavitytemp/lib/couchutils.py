# ------------------ COUCHUTILS ---------------------------#
import couchdb
import sys.logging

CREDENTIALHOME = "/home/uwslowcontrol/config/couchcred.conf"
CLOG_FILENAME = '/home/uwslowcontrol/pi_db/log/cavitytemp.log' #logfile source

# --------- Logger configuration ----------- #
logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO, \
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
            sleep(1)
            status = "bad"
            continue
    return status, db

def saveValues(data):
    dbDataStatus, dbData = connectToDB("slowcontrol-data-1min")
    if dbDataStatus is "ok":
        for element in data:
            if element["timestamp"]!="N/A":
		try:
                    dbData.save(element)
		except socket.error, exc:
		    logging.exception("FAILED TO SAVE 1 MIN ENTRY" + \
		    "FOR THIS MINUTE.  ERROR: " + str(exc))

#--------------- /COUCHUTILS ------------------------------#
