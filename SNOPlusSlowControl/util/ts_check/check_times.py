from __future__ import print_function
import couchdb
import sys
import string, calendar, time, urllib2, base64
import lib.alarm_server as als
import lib.getcreds as gc
import lib.emailsend as es

from email import utils
import logging

#TO DOS:
# - Want to post the timestamps to the slowcontrol-alarms and create a
#new view?



#HARD-CODED: OLD TIMES WOULD NEED TO BE CHANGED IN WEBPAGE CODE SEPARATELY
#FIXME : HAVE THESE NUMBERS BE PULLED FROM AN ENTRY IN THE COUCHDB

IOS_NUMBERS = [1,2,3,4]     #IOSes currently active
IOS_OLD_THRESH = 50         #Age at which IOS timestmaps alarms are sent
IOS_OLD_ALARMID = 30036     #Alarm ID (defined in SNO+ alarm server DB)
DELTAV_OLD_THRESH = 660     #Age at which DeltaV TS alarms are sent
DELTAV_OLD_ALARMID = 30037  #Alarm ID (defined in SNO+ alarm server DB)
NOCOUCHCONN_ID = 30038      #Alarm ID for no connection to couch.ug
CTEMPS_OLD_THRESH = 3600     #Age at which CavityTemp TS alarms are sent
CTEMPS_OLD_ALARMID = 30039  #Alarm ID for the temperature values being old
period = 5                  #Time between each data collection loop
LOG_FILENAME = '/home/slowcontroller/ts_check/log/ts_check.log' #logfile source

#Logging implementation
logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO, \
    format='%(asctime)s %(message)s')

logging.info("TS_CHECK STARTED AGAIN")

#DOESN'T WORK IN PYTHON 2.6?
#def UE_handler(type, value, tb):
#    logging.exception("Uncaught exception: {0}".format(str(value))
#
#sys.excepthook = UE_handler

def unix_to_human(unix_time):
    human_time = utils.formatdate(unix_time, localtime=True)
    return human_time



#Connection info for IOS's local couchdb
couchuser, couchpassword = gc.getcreds("/home/slowcontroller/config/SCcouchcred.conf")
couch = couchdb.Server()
couch.resource.credentials = (couchuser, couchpassword)


#Connection info for couch.ug
snopluscouchuser, snopluscouchpw = gc.getcreds("/home/slowcontroller/config" + \
    "/couchcred.conf")
snopluscouch = couchdb.Server('http://couch.ug.snopl.us')
snopluscouch.resource.credentials = (snopluscouchuser, snopluscouchpw)

#CONNECTS TO COUCH.UG (REPLACE "snopluscouch" with "couch" for local conn)
def connectToDB(dbName):
    status = "ok"
    db = {}
    counter = 0
    while counter < 3:
        try:
            db = snopluscouch[dbName]
	    return status, db
        except:
            print("Failed to connect to " + dbName + ", sleeping for " + \
	        "2 seconds and trying again.")
            logging.warning("Failed to connect to " + dbName)
            counter += 1
	    time.sleep(2)
	    continue
    print("Failed to connect to " + dbName + "three times.  posting " + \
	"failure to connect to DB alarm.")
    logging.warning("Couldn't connect to DB after three tries.")
    status="bad"
    #als.post_alarm(NOCOUCHCONN_ID)
    return status, db

#Class takes in a couchDB document and compares it's timestmap to the
#current time on couch.ug.snopl.us (where the IOS/DeltaV data is stored)
class TimestampComparer(object):
    def __init__(self, doc):
        self.doc = doc
	self.timestamp = int(self.doc["timestamp"])
	self.couchUGtime = 'none'
	self.getcouchUGTime()

    def compare(self):
        if (self.couchUGtime == 'unknown') or (self.timestamp == 'unknown'):
	    logging.warning("ERROR GETTING EITHER THE DOC TIMESTAMP OR" + \
		" SERVER TIME FROM COUCH.UG. CHECK COUCH.UG STATUS.")
	    return 'unknown'
	else:
            try:
	        result = self.couchUGtime - self.timestamp
	        return result
            except(TypeError):
	        logging.warning("TIMESTAMP AND COUCH TIME ARE NOT BOTH " + \
		    "INTEGERS.  RETURNING UNKNOWN.")
		return 'unknown'
    

    def getcouchUGTime(self):
        url = 'http://couch.ug.snopl.us'
        try:
            req = urllib2.Request(url)
	    base64string = base64.b64encode("%s:%s" % \
		(snopluscouchuser, snopluscouchpw)).replace('\n', '')
	    req.add_header("Authorization", "Basic %s" % base64string)
            ping = urllib2.urlopen(req)
	    couchdate = ping.headers.dict['date']
	    #convert to unix time
            pattern = str("%a, %d %b %Y %H:%M:%S %Z")
	    unixcouchtime = int(calendar.timegm(time.strptime(couchdate, pattern)))
	    self.couchUGtime = unixcouchtime
	except:
	    logging.warning("ERROR GETTING CURRENT COUCH.UG TIME." + \
		"TIME IS UNKNOWN.")
	    self.couchUGtime = 'unknown'


#---FUNCTIONS USING TIMESTAMPCOMPARER CLASS---#
#---------------------------------------------#
def getCavityTempsDocAge():
    status, db = connectToDB('slowcontrol-data-cavitytemps')
    if status=="ok":
        queryresult = db.view('slowcontrol-data-cavitytemps/by_timestamp', \
            descending=True, limit=1)
        recentdoc = queryresult.rows[0].value
        comparer = TimestampComparer(recentdoc)
        return comparer.compare() 
    else:
        return 'unknown'

def getIOSDocAge(IOSnum):
    status, db = connectToDB('slowcontrol-data-5sec')
    if status=="ok":
        queryresult = db.view('slowcontrol-data-5sec/recent' + str(IOSnum), \
            descending=True, limit=1)
        recentdoc = queryresult.rows[0].value
        comparer = TimestampComparer(recentdoc)
        return comparer.compare() 
    else:
        return 'unknown'
	  
def getDeltaVDocAge():
    #poll the DeltaV database and check the timestamp
    dvstatus, dvdb = connectToDB('slowcontrol-data-1min')
    if dvstatus=='ok':
        dvqueryresult = dvdb.view('slowcontrol-data-1min/pi_db', \
            descending=True, limit=1)
        dvrecentdoc = dvqueryresult.rows[0].value
        dvcomparer = TimestampComparer(dvrecentdoc)
        return dvcomparer.compare()
    else:
        return 'unknown'



if __name__ == '__main__':
    try:
        Doc_ages_last = {}
        Doc_ages = {}

        #Do an initial poll and just set Doc_ages and Doc_ages_last equal on
        #first iteration
        for IOSnum in IOS_NUMBERS:
            Doc_ages["IOS " + str(IOSnum)] = getIOSDocAge(IOSnum)
        Doc_ages["DeltaV"] = getDeltaVDocAge()
	Doc_ages["CavityTemps"] = getCavityTempsDocAge()
        Doc_ages_last = Doc_ages


        #clear any old alarms on init
        als.clear_alarm(IOS_OLD_ALARMID)
        als.clear_alarm(DELTAV_OLD_ALARMID)
        als.clear_alarm(CTEMPS_OLD_ALARMID)

        #begin polling loop
        while True:
            #Get the age of the most recent IOS and DeltaV documents on
	    #couch.ug relative to couch.ug's time
            Doc_ages = {}
            for IOSnum in IOS_NUMBERS:
                Doc_ages["IOS " + str(IOSnum)] = getIOSDocAge(IOSnum)
	    Doc_ages["DeltaV"] = getDeltaVDocAge()
    	    Doc_ages["CavityTemps"] = getCavityTempsDocAge()
            #Get the timestamp and date when timestamps were checked

            Doc_ages["timestamp"] = int(time.time())
	    Doc_ages["date"] = unix_to_human(time.time())

           	#Post/clear alarms for any documents that are old/no longer old
    	    #(alarms are posted to alarm server and emailed to slowcontrol
	    #mailing list)
            for IOSnum in IOS_NUMBERS:
                if Doc_ages["IOS " + str(IOSnum)] is not 'unknown':
		    if Doc_ages_last["IOS " + str(IOSnum)] is 'unknown':
    	                if (Doc_ages["IOS " + str(IOSnum)] < IOS_OLD_THRESH):
			    als.clear_alarm(IOS_OLD_ALARMID)
                        if Doc_ages["IOS " + str(IOSnum)] > IOS_OLD_THRESH:
    	                    als.post_alarm(IOS_OLD_ALARMID)
          		    es.sendTSAlarmEmail(Doc_ages['date'],IOSnum)
    	            else:
    	                if ((Doc_ages["IOS " + str(IOSnum)] < IOS_OLD_THRESH) and \
    		            (Doc_ages_last["IOS " + str(IOSnum)] > IOS_OLD_THRESH)):
    	                    als.clear_alarm(IOS_OLD_ALARMID)
                            es.sendTSClearEmail(Doc_ages['date'],IOSnum)
                        if Doc_ages["IOS " + str(IOSnum)] > IOS_OLD_THRESH:
    	                    als.post_alarm(IOS_OLD_ALARMID)
    	                if ((Doc_ages["IOS " + str(IOSnum)] > IOS_OLD_THRESH) and \
    		            (Doc_ages_last["IOS " + str(IOSnum)] <= IOS_OLD_THRESH)):
          		    es.sendTSAlarmEmail(Doc_ages['date'],IOSnum)
                else:
		    logging.info("IOS " + str(IOSnum) + "has an uknown")
		    logging.info("timestamp.  Printing out stuff.")
		    logging.info("Doc_ages of IOS"+str(IOSnum)+": "+str(Doc_ages["IOS " + str(IOSnum)]))
		    logging.info("Doc_ages_last of IOS"+str(IOSnum)+": "+str(Doc_ages_last["IOS "+str(IOSnum)]))
		
    	    if Doc_ages["DeltaV"] is not 'unknown':
	        if Doc_ages_last["DeltaV"] is 'unknown':
                    if Doc_ages["DeltaV"] > DELTAV_OLD_THRESH:
		        als.post_alarm(DELTAV_OLD_ALARMID)
			es.sendTSAlarmEmail_DV(Doc_ages['date'])
	            if Doc_ages["DeltaV"] <= DELTAV_OLD_THRESH:
		        als.clear_alarm(DELTAV_OLD_ALARMID)
		else:
    	            if Doc_ages["DeltaV"] > DELTAV_OLD_THRESH:
    		        als.post_alarm(DELTAV_OLD_ALARMID)
    	            if ((Doc_ages["DeltaV"] > DELTAV_OLD_THRESH) and \
    		        (Doc_ages_last["DeltaV"] <= DELTAV_OLD_THRESH)):
                        es.sendTSAlarmEmail_DV(Doc_ages['date'])
                    if ((Doc_ages["DeltaV"] < DELTAV_OLD_THRESH) and \
    		        (Doc_ages_last["DeltaV"] > DELTAV_OLD_THRESH)):
    		        als.clear_alarm(DELTAV_OLD_ALARMID)
                        es.sendTSClearEmail_DV(Doc_ages['date'])

    	    if Doc_ages["CavityTemps"] is not 'unknown':
	        if Doc_ages_last["CavityTemps"] is 'unknown':
                    if Doc_ages["CavityTemps"] > CTEMPS_OLD_THRESH:
		        als.post_alarm(CTEMPS_OLD_ALARMID)
			es.sendTSAlarmEmail_CT(Doc_ages['date'])
	            if Doc_ages["CavityTemps"] <= CTEMPS_OLD_THRESH:
		        als.clear_alarm(CTEMPS_OLD_ALARMID)
		else:
    	            if Doc_ages["CavityTemps"] > CTEMPS_OLD_THRESH:
    		        als.post_alarm(CTEMPS_OLD_ALARMID)
    	                #Rare case where timestamp is old at startup
			if Doc_ages["CavityTemps"] == Doc_ages_last["CavityTemps"]:
		            es.sendTSAlarmEmail_CT(Doc_ages['date']) 
		        elif Doc_ages_last["CavityTemps"] <= CTEMPS_OLD_THRESH:
                            es.sendTSAlarmEmail_CT(Doc_ages['date'])
                    if ((Doc_ages["CavityTemps"] < CTEMPS_OLD_THRESH) and \
    		        (Doc_ages_last["CavityTemps"] > CTEMPS_OLD_THRESH)):
    		        als.clear_alarm(CTEMPS_OLD_ALARMID)
                        es.sendTSClearEmail_CT(Doc_ages['date'])
    
            Doc_ages_last = Doc_ages
            time.sleep(period)
    except StandardError as e:
        logging.exception("Uncaught exception: {0}".format(str(e)))
	raise
