LOG_FILENAME = '/home/uwslowcontrol/pi_db/log/pilog.log' #logfile source
ALARMCREDDIR = "/home/uwslowcontrol/config/alascred.conf"
ALARMHOST = "dbug"
ALARMDBNAME = "detector"
TIMESERIESURL = 'http://pi.snolab.ca/PIWebServices/PITimeSeries.svc?wsdl'
PIDBFACTORYANME = 'PIArcDataRequest'
GMAILCREDS = "/home/uwslowcontrol/config/gmailcred.conf"
MAILRECIPIENTLISTDIR = "/home/uwslowcontrol/pi_db/pi_db/emailList.txt"
COUCHADDRESS = 'http://couch.snopl.us'
COUCHCREDS = "/home/uwslowcontrol/config/couchcred.conf"
CHANNELDBURL = 'slowcontrol-channeldb'
CHANNELDBVIEW = 'slowcontro/recent'
ONEMINDBURL = "slowcontrol-data-1min"
ALARMDBURL = 'slowcontrol-alarms'
ALARMDBVIEW = 'slowcontrol-alarms/pi_db'

ALARMHEARTBEAT = 'MinardSC'
#Delay in minutes for the time you want to poll from PI Database
#Have to hard-code a delay in the times polled from PI DB
#If you don't, will just poll empty values
DELAY = 5  #in minutes 
POLL_WAITTIME = 60 #Time, in seconds, between each poll
POLL_RANGE = 60 #Time, in seconds, of PI data grabbed in each snapshot
