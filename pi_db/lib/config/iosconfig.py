DEBUG = True
LOG_FILENAME = '/home/uwslowcontrol/pi_db_2.0/pi_db/pi_db/log/IOSlog.log' #logfile source
ALARMCREDDIR = "/home/uwslowcontrol/config/alascred.conf"
ALARMHOST = "dbug.sp.snolab.ca"
ALARMDBNAME = "detector"



DETECTORSERVERHOST="daq1.sp.snolab.ca"
DETECTORSERVERPORT=8520
SOCKET_TIMEOUT=1.0
RETRYONTIMEOUT=True
 
GMAILCREDS = "/home/uwslowcontrol/config/gmailcred.conf"
MAILRECIPIENTLISTFILE = "/home/uwslowcontrol/pi_db_2.0/pi_db/pi_db/emailList.txt"
COUCHADDRESS = "http://localhost:5984/"
COUCHCREDS = "/home/uwslowcontrol/config/couchcred.conf"
IOSNUM = 3
IOSCARDSCONF = "/home/slowcontroller/hmhj/lib/hmhj_layer1-0.2/priv/cards.conf"
CHANNELDBURL = 'slowcontrol-channeldb'
CHANNELDBVIEW = 'slowcontrol/recent'
FIVESECDBURL = "slowcontrol-data-5sec"
ONEMINDBURL = "slowcontrol-data-1min"

ALARMDBURL = 'slowcontrol-alarms'
ALARMDBVIEW = 'slowcontrol-alarms/recent'+str(c.IOSNUM)

ALARMHEARTBEAT = 'SC_IOS3'
ALARMBEATINTERVAL = 10
#Delay in minutes for the time you want to poll from PI Database
#Have to hard-code a delay in the times polled from PI DB
#If you don't, will just poll empty values
POLLDELAY = 5  #in minutes 
POLL_WAITTIME = 60 #Time, in seconds, between each poll
POLLRANGE = 60 #Time, in seconds, of PI data grabbed in each snapshot

VERSION = 2.0  #Version release number of this code stamped to saved data
