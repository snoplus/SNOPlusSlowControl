IOSNUM = 2
DEBUG = False
RACKCONTROLHOST = 'minard.sp.snolab.ca'
RACKCONTROLPORT = 8520
LOWVOLTTHRESH = 1.5
#SOCKET_TIMEOUT=15
#RETRYONTIMEOUT=True

CHDBADDRESS = 'http://couch.snopl.us'
CHDBCREDS = "/home/slowcontroller/config/couchcred.conf"
SCCOUCHADDRESS = "http://localhost:5984/" #IOS saves data to their local couchDB & replicated
SCCOUCHCREDS = "/home/slowcontroller/config/SCcouchcred.conf"
IOSCARDCONF = "/home/slowcontroller/hmhj/lib/hmhj_layer1-0.2/priv/cards.conf"
CHANNELDBURL = 'slowcontrol-channeldb'
CHANNELDBVIEW = 'slowcontrol/recent'
FIVESECDBURL = "slowcontrol-data-5sec"
ONEMINDBURL = "slowcontrol-data-1min"

#Slowcontrol couchDB alarm database info
COUCHALARMDBURL = 'slowcontrol-alarms'
COUCHALARMDBVIEW = 'slowcontrol-alarms/recent'+str(IOSNUM)

ALARMHEARTBEAT = 'SC_IOS'+str(IOSNUM)
ALARMBEATINTERVAL = 10

POLL_WAITTIME = 5 #Time, in seconds, between each poll
VERSION = 2.0  #Version release number of this code stamped to saved data
