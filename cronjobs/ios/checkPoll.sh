#!/bin/sh

RUNNING=`ps -ef | grep poll | grep /usr/bin/python`
HMHJRUNNING=`ps -ef | grep hmhj | grep comm_layer`
if [ "$RUNNING" == "" ] && [ "$HMHJRUNNING" != "" ]
then
  echo "Poll script is not running on `hostname`!"
  python /home/slowcontroller/pollScriptIOS4.py &
  SUBJECT="Poll script restarted on `hostname`"
  MESSAGE="Poll script restarted at `date` as `ps -ef | grep poll | grep \usr`"
  echo $MESSAGE | cat >> /home/slowcontroller/errorlog.txt
  echo "Poll script is started on `hostname`."
  python /home/slowcontroller/sendEmail.py "$SUBJECT" "$MESSAGE" &
else
  echo "Poll script is running on `hostname`."
fi
