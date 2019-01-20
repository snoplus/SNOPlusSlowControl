IOSNUM = 3
DEBUG = True
LOG_FILENAME = '/home/uwslowcontrol/pi_db_2.0/pi_db/pi_db/log/IOS'+str(IOSNUM)+'log.log' #logfile source
ALARMCREDDIR = "/home/uwslowcontrol/config/alascred.conf"
ALARMHOST = "dbug.sp.snolab.ca"
ALARMDBNAME = "detector"

RACKCONTROLHOST = 'minard.sp.snolab.ca'
RACKCONTROLPORT = 8520
LOWVOLTTHRESH = 1.5

DETECTORSERVERHOST="daq1.sp.snolab.ca"
DETECTORSERVERPORT=8520
SOCKET_TIMEOUT=1.0
RETRYONTIMEOUT=True
 
GMAILCREDS = "/home/uwslowcontrol/config/gmailcred.conf"
MAILRECIPIENTLISTFILE = "/home/uwslowcontrol/pi_db_2.0/pi_db/pi_db/emailList.txt"

COUCHADDRESS = "http://localhost:5984/"
COUCHCREDS = "/home/uwslowcontrol/config/couchcred.conf"
IOSCARDCONF = "/home/slowcontroller/hmhj/lib/hmhj_layer1-0.2/priv/cards.conf"
CHANNELDBURL = 'slowcontrol-channeldb'
CHANNELDBVIEW = 'slowcontrol/recent'
FIVESECDBURL = "slowcontrol-data-5sec"
ONEMINDBURL = "slowcontrol-data-1min"

ALARMDBURL = 'slowcontrol-alarms'
ALARMDBVIEW = 'slowcontrol-alarms/recent'+str(c.IOSNUM)

ALARMHEARTBEAT = 'SC_IOS'+str(IOSNUM)
ALARMBEATINTERVAL = 10

POLL_WAITTIME = 5 #Time, in seconds, between each poll
VERSION = 2.0  #Version release number of this code stamped to saved data
