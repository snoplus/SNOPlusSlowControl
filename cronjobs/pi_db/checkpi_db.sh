#!/bin/bash
#To get mail and see errors when trying to run pi_db.py from this, 
#Remove MAILTO='' in the cronjob
MAILTO=""

#Modify the home directory (where SNOPlusSlowControl lives) to use on your machine
HOMEDIR=/home/uwslowcontrol
PIDBSCRIPTLOC=/SNOPlusSlowControl/SNOPlusSlowControl/main_pidb.py
PIDBLOGLOC=/SNOPlusSlowControl/SNOPlusSlowControl/log/mainlog.log

RUNNING=`ps -ef | grep pi_db.py | grep python`
if [ "$RUNNING" == "" ]
then
  echo "pi_db script is not running on `hostname`!"
  python ${HOMEDIR}${PIDBSCRIPTLOC} &
  SUBJECT="pi_db script restarted on `hostname`"
  MESSAGE="pi_db script restarted at `date` as `ps -ef | grep pi_db`"
  echo $MESSAGE | cat >> ${HOMEDIR}${PIDBLOGLOC} 
  echo "pi_db script is started on `hostname`."
else
  echo "pi_db script is running on `hostname`."
fi
