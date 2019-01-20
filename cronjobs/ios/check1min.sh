#!/bin/sh

RUNNING=`ps -ef | grep 1min | grep /usr/bin/python`
if [ "$RUNNING" == "" ]
then
  echo "1min script is not running on `hostname`!"
  python /home/slowcontroller/1min.py &
  SUBJECT="1min script restarted on `hostname`"
  MESSAGE="1min script restarted at `date` as `ps -ef | grep poll | grep \usr`"
  python /home/slowcontroller/sendEmail.py "$SUBJECT" "$MESSAGE"
  echo $MESSAGE | cat >> /home/slowcontroller/errorlog.txt
  echo "1min script is started on `hostname`."
else
  echo "1min script is running on `hostname`."
fi
