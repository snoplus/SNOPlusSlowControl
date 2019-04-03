#!/bin/sh

HOMEDIR=/home/slowcontroller
POLLDIR=/SNOPlusSlowControl/SNOPlusSlowControl/main_ios.py
POLLLOGLOC=/SNOPlusSlowControl/SNOPlusSlowControl/log/IOSlog.log

RUNNING=`ps -ef | grep ${HOMEDIR}${POLLDIR} | grep python`
HMHJRUNNING=`ps -ef | grep hmhj | grep comm_layer`
if [ "$RUNNING" == "" ] && [ "$HMHJRUNNING" != "" ]
then
  echo "Poll script is not running on `hostname`!"
  python ${HOMEDIR}${POLLDIR} &
  SUBJECT="Poll script restarted on `hostname`"
  MESSAGE="Poll script restarted at `date` as `ps -ef | grep poll | grep \usr`"
  echo $MESSAGE | cat >> ${HOMEDIR}${POLLLOGLOC} 
  echo "Poll script is started on `hostname`."
else
  echo "Poll script is running on `hostname`."
fi
