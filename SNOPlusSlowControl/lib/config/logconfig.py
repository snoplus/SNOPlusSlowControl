import logging

#LOCAL LOGGING CONFIGURATIOn
LOG_FILENAME = '/home/uwslowcontrol/SNOPlusSlowControl/SNOPlusSlowControl/log/IOSlog.log' #logfile source on IOSes
#LOG_FILENAME = '/home/uwslowcontrol/SNOPlusSlowControl/SNOPlusSlowControl/log/pilog.log' #logfile source on minard
LOG_FORMAT = '%(asctime)s %(name)8s %(levelname)5s %(message)s'
LOG_LEVEL = logging.INFO

#EMAIL LIST FOR SENDING ALARMS/MESSAGES TO
#GMAILCREDS = "/home/uwslowcontrol/config/gmailcred.conf"
GMAILCREDS = "/home/uwslowcontrol/config/gmailcred.conf"
#EMAIL_RECIPIENTS_FILE = "/home/uwslowcontrol/SNOPlusSlowControl/SNOPlusSlowControl/DB/emailList.txt"
EMAIL_RECIPIENTS_FILE = "/home/uwslowcontrol/SNOPlusSlowControl/SNOPlusSlowControl/DB/emailList.txt"
