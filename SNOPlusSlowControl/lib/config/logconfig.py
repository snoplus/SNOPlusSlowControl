from os.path import expanduser
#home = expanduser("~")
home = '/home/slowcontroller'
import logging

#LOCAL LOGGING CONFIGURATIOn
LOG_FILENAME = home + '/SNOPlusSlowControl/SNOPlusSlowControl/log/IOSlog.log' #logfile source assuming homedir install
LOG_FORMAT = '%(asctime)s %(name)8s %(levelname)5s %(message)s'
LOG_LEVEL = logging.INFO

#EMAIL LIST FOR SENDING ALARMS/MESSAGES TO (Assumes homedir install)
GMAILCREDS = home + "/config/gmailcred.conf"
EMAIL_RECIPIENTS_FILE = home + "/SNOPlusSlowControl/SNOPlusSlowControl/DB/emailList.txt"
