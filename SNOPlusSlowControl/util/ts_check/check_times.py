from __future__ import print_function
import couchdb
import sys
import string, calendar, time, urllib2, base64
import lib.config.tsconfig as c
import lib.alarm_server as als
import lib.getcreds as gc
import lib.emailsend as es
import lib.couchutils
import lib.TimestampComparer
import lib.functions as f

from email import utils
import logging

#TO DOS:
# - Want to post the timestamps to the slowcontrol-alarms and create a
#new view?



#HARD-CODED: OLD TIMES WOULD NEED TO BE CHANGED IN WEBPAGE CODE SEPARATELY
#FIXME : HAVE THESE NUMBERS BE PULLED FROM AN ENTRY IN THE COUCHDB


#Logging implementation
logging.basicConfig(filename=c.LOG_FILENAME,level=logging.INFO, \
    format='%(asctime)s %(message)s')

logging.info("TS_CHECK STARTED AGAIN")

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
snopluscouch = couchdb.Server('http://couch.snopl.us')
snopluscouch.resource.credentials = (snopluscouchuser, snopluscouchpw)


if __name__ == '__main__':
    try:
        Doc_ages_last = {}
        Doc_ages = {}

        #Do an initial poll and just set Doc_ages and Doc_ages_last equal on
        #first iteration
        for IOSnum in c.IOS_NUMBERS:
            Doc_ages["IOS " + str(IOSnum)] = f.getIOSDocAge(IOSnum)
        Doc_ages["DeltaV"] = f.getDeltaVDocAge()
	Doc_ages["CavityTemps"] = f.getCavityTempsDocAge()
        Doc_ages_last = Doc_ages


        #clear any old alarms on init
        als.clear_alarm(c.IOS_OLD_ALARMID)
        als.clear_alarm(c.DELTAV_OLD_ALARMID)
        als.clear_alarm(c.CTEMPS_OLD_ALARMID)

        #begin polling loop
        while True:
            #Get the age of the most recent IOS and DeltaV documents on
	    #couch.ug relative to couch.ug's time
            Doc_ages = {}
            for IOSnum in c.IOS_NUMBERS:
                Doc_ages["IOS " + str(IOSnum)] = f.getIOSDocAge(IOSnum)
	    Doc_ages["DeltaV"] = f.getDeltaVDocAge()
    	    Doc_ages["CavityTemps"] = f.getCavityTempsDocAge()
            #Get the timestamp and date when timestamps were checked

            Doc_ages["timestamp"] = int(time.time())
	    Doc_ages["date"] = unix_to_human(time.time())

           	#Post/clear alarms for any documents that are old/no longer old
    	    #(alarms are posted to alarm server and emailed to slowcontrol
	    #mailing list)
            for IOSnum in c.IOS_NUMBERS:
                if Doc_ages["IOS " + str(IOSnum)] is not 'unknown':
		    if Doc_ages_last["IOS " + str(IOSnum)] is 'unknown':
    	                if (Doc_ages["IOS " + str(IOSnum)] < c.IOS_OLD_THRESH):
			    als.clear_alarm(c.IOS_OLD_ALARMID)
                        if Doc_ages["IOS " + str(IOSnum)] > c.IOS_OLD_THRESH:
    	                    als.post_alarm(c.IOS_OLD_ALARMID)
          		    es.sendTSAlarmEmail(Doc_ages['date'],IOSnum)
    	            else:
    	                if ((Doc_ages["IOS " + str(IOSnum)] < c.IOS_OLD_THRESH) and \
    		            (Doc_ages_last["IOS " + str(IOSnum)] > c.IOS_OLD_THRESH)):
    	                    als.clear_alarm(c.IOS_OLD_ALARMID)
                            es.sendTSClearEmail(Doc_ages['date'],IOSnum)
                        if Doc_ages["IOS " + str(IOSnum)] > c.IOS_OLD_THRESH:
    	                    als.post_alarm(c.IOS_OLD_ALARMID)
    	                if ((Doc_ages["IOS " + str(IOSnum)] > c.IOS_OLD_THRESH) and \
    		            (Doc_ages_last["IOS " + str(IOSnum)] <= c.IOS_OLD_THRESH)):
          		    es.sendTSAlarmEmail(Doc_ages['date'],IOSnum)
                else:
		    logging.info("IOS " + str(IOSnum) + "has an uknown")
		    logging.info("timestamp.  Printing out stuff.")
		    logging.info("Doc_ages of IOS"+str(IOSnum)+": "+str(Doc_ages["IOS " + str(IOSnum)]))
		    logging.info("Doc_ages_last of IOS"+str(IOSnum)+": "+str(Doc_ages_last["IOS "+str(IOSnum)]))
		
    	    if Doc_ages["DeltaV"] is not 'unknown':
	        if Doc_ages_last["DeltaV"] is 'unknown':
                    if Doc_ages["DeltaV"] > c.DELTAV_OLD_THRESH:
		        als.post_alarm(c.DELTAV_OLD_ALARMID)
			es.sendTSAlarmEmail_DV(Doc_ages['date'])
	            if Doc_ages["DeltaV"] <= c.DELTAV_OLD_THRESH:
		        als.clear_alarm(c.DELTAV_OLD_ALARMID)
		else:
    	            if Doc_ages["DeltaV"] > c.DELTAV_OLD_THRESH:
    		        als.post_alarm(c.DELTAV_OLD_ALARMID)
    	            if ((Doc_ages["DeltaV"] > c.DELTAV_OLD_THRESH) and \
    		        (Doc_ages_last["DeltaV"] <= c.DELTAV_OLD_THRESH)):
                        es.sendTSAlarmEmail_DV(Doc_ages['date'])
                    if ((Doc_ages["DeltaV"] < c.DELTAV_OLD_THRESH) and \
    		        (Doc_ages_last["DeltaV"] > c.DELTAV_OLD_THRESH)):
    		        als.clear_alarm(c.DELTAV_OLD_ALARMID)
                        es.sendTSClearEmail_DV(Doc_ages['date'])

    	    if Doc_ages["CavityTemps"] is not 'unknown':
	        if Doc_ages_last["CavityTemps"] is 'unknown':
                    if Doc_ages["CavityTemps"] > c.CTEMPS_OLD_THRESH:
		        als.post_alarm(c.CTEMPS_OLD_ALARMID)
			es.sendTSAlarmEmail_CT(Doc_ages['date'])
	            if Doc_ages["CavityTemps"] <= c.CTEMPS_OLD_THRESH:
		        als.clear_alarm(c.CTEMPS_OLD_ALARMID)
		else:
    	            if Doc_ages["CavityTemps"] > c.CTEMPS_OLD_THRESH:
    		        als.post_alarm(c.CTEMPS_OLD_ALARMID)
    	                #Rare case where timestamp is old at startup
			if Doc_ages["CavityTemps"] == Doc_ages_last["CavityTemps"]:
		            es.sendTSAlarmEmail_CT(Doc_ages['date']) 
		        elif Doc_ages_last["CavityTemps"] <= c.CTEMPS_OLD_THRESH:
                            es.sendTSAlarmEmail_CT(Doc_ages['date'])
                    if ((Doc_ages["CavityTemps"] < c.CTEMPS_OLD_THRESH) and \
    		        (Doc_ages_last["CavityTemps"] > c.CTEMPS_OLD_THRESH)):
    		        als.clear_alarm(c.CTEMPS_OLD_ALARMID)
                        es.sendTSClearEmail_CT(Doc_ages['date'])
    
            Doc_ages_last = Doc_ages
            time.sleep(c.period)
    except StandardError as e:
        logging.exception("Uncaught exception: {0}".format(str(e)))
	raise
