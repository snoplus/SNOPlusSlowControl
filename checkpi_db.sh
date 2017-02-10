#!/bin/bash
#To get mail and see errors when trying to run pi_db.py from this, 
#Remove MAILTO='' in the cronjob
MAILTO=""
RUNNING=`ps -ef | grep pi_db.py | grep python`
if [ "$RUNNING" == "" ]
then
  echo "pi_db script is not running on `hostname`!"
  python /home/uwslowcontrol/pi_db/pi_db.py &
  SUBJECT="pi_db script restarted on `hostname`"
  MESSAGE="pi_db script restarted at `date` as `ps -ef | grep pi_db`"
  python ~/pi_db/sendEmail.py "$SUBJECT" "$MESSAGE"
  echo $MESSAGE | cat >> ~/pi_db/errorlog.txt
  echo "pi_db script is started on `hostname`."
else
  echo "pi_db script is running on `hostname`."
fi
