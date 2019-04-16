IOS_NUMBERS = [1,2,3,4]     #IOSes currently active
IOS_OLD_THRESH = 50         #Age at which IOS timestmaps alarms are sent
IOS_OLD_ALARMID = 30036     #Alarm ID (defined in SNO+ alarm server DB)
DELTAV_OLD_THRESH = 660     #Age at which DeltaV TS alarms are sent
DELTAV_OLD_ALARMID = 30037  #Alarm ID (defined in SNO+ alarm server DB)
NOCOUCHCONN_ID = 30038      #Alarm ID for no connection to couch.ug
CTEMPS_OLD_THRESH = 3600     #Age at which CavityTemp TS alarms are sent
CTEMPS_OLD_ALARMID = 30039  #Alarm ID for the temperature values being old
period = 5                  #Time between each data collection loop

HOMEDIR='/home/slowcontroller' #Directory where SNOPlusSlowControl lives
LOGDIR='/SNOPlusSlowControl/SNOPlusSlowControl/log/timestamp_check.log' #logfile source
LOG_FILENAME = HOMEDIR+LOGDIR

