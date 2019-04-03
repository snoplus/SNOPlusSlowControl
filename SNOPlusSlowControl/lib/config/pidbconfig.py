DEBUG = False
ALARMCREDDIR = "/home/uwslowcontrol/config/alascred.conf"
ALARMHOST,ALARMDBNAME = "dbug","detector"

TIMESERIESURL = 'http://pi.snolab.ca/PIWebServices/PITimeSeries.svc?wsdl'
PIDBFACTORYNAME = 'PIArcDataRequest'
PIADDRESSBASE = "pi:\\\\pi.snolab.ca\\"
 

COUCHADDRESS = 'http://couch.snopl.us'
COUCHCREDS = "/home/uwslowcontrol/config/couchcred.conf"
CHANNELDBVIEW = 'slowcontrol/recent'
CHANNELDBURL = 'slowcontrol-channeldb'
ONEMINDBURL = "slowcontrol-data-1min"

COUCHALARMDBURL = 'slowcontrol-alarms'
COUCHALARMDBVIEW = 'slowcontrol-alarms/pi_db'

ALARMHEARTBEAT = 'MinardSC'
ALARMBEATINTERVAL = 10
#Delay in minutes for the time you want to poll from PI Database
#Have to hard-code a delay in the times polled from PI DB
#If you don't, will just poll empty values
POLLDELAY = 5  #in minutes 
POLL_WAITTIME = 60 #Time, in seconds, between each poll
POLLRANGE = 60 #Time, in seconds, of PI data grabbed in each snapshot

VERSION = 2.0  #Version release number of this code stamped to saved data
