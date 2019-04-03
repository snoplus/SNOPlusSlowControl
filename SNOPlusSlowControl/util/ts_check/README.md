#Timestamp checking software for SNO+ Slow Control IOS servers

The following software compares the most recent timestamps in the SNO+ IOS
 and DeltaV couchdbs (couch.ug.snopl.us) to couch.ug.snopl.us's server time.  If the data timestamps are older than thresholds defined, then an alarm is posted to the SNO+ alarm server and an e-mail notification is sent to the SNO+ slow control mailing list.


The main script is check_times.py.

To utilize on another machine/with another couchdb server, change the following in check_times.py:
    - Change the couchdb database names used to connect (current version connects to 'slowcontrol-data-5sec' and 'slowcontrol-data-1min'
    - Change the alarming thresholds as desired
    - Change the alarmIDs that will be sent to the SNO+ alarm server (or your server!)
    - Change the directory where your e-mail list is stored (top of /lib/emailsend.py)
    - Create your own config files that will have usernames and passwords needed for couchdb/alarm server connections
    - Change the hard-coded location of your config file according to your system (do this at the top of lib/getcred.py)

/cronjobs/ios/checkts.sh: an example bash script that can be used to check 
if check_times.py is still running.  If not, it will restart check_times.py using 
python.  You can configure your crontab to run this script regularly to make sure
 the script has not crashed.

SNOPlusSlowControl/SNOPlusSlowControl/log/ts_check.log is the default location for logging
information to be saved.  Log contains info about ts's running (did it lose connection to couchdb?  Was the value type pulled from couchdb bad?  Did the script have to restart?)
