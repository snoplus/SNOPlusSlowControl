import logging

#LOCAL LOGGING CONFIGURATIOn
#LOG_FILENAME = '/home/uwslowcontrol/pi_db_2.0/pi_db/pi_db/log/IOS'+str(IOSNUM)+'log.log' #logfile source
LOG_FILENAME = '/home/uwslowcontrol/pi_db_2.0/pi_db/pi_db/log/pilog.log' #logfile source
LOG_FORMAT = '%(asctime)s %(name)8s %(levelname)5s %(message)s'
LOG_LEVEL = logging.INFO

#EMAIL LIST FOR SENDING ALARMS/MESSAGES TO
GMAILCREDS = "/home/uwslowcontrol/config/gmailcred.conf"
EMAIL_RECIPIENTS_FILE = "/home/uwslowcontrol/pi_db_2.0/pi_db/pi_db/emailList.txt"
