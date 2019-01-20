#!/bin/sh

RUNNING=`ps -ef | grep 15min | grep /usr/bin/python`
if [ "$RUNNING" == "" ]
then
  echo "15min script is not running on `hostname`!"
  python /home/slowcontroller/15min.py &
  SUBJECT="15min script restarted on `hostname`"
  MESSAGE="15min script restarted at `date` as `ps -ef | grep poll | grep \usr`"
  python /home/slowcontroller/sendEmail.py "$SUBJECT" "$MESSAGE"
  echo $MESSAGE | cat >> /home/slowcontroller/errorlog.txt
  echo "15min script is started on `hostname`."
else
  echo "15min script is running on `hostname`."
fi
