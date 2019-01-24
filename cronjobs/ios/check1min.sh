#!/bin/sh
HOMEDIR=/home/slowcontroller
ONEMINLOC=/SNOPlusSlowControl/SNOPlusSlowControl/util/ios_1_15_min/1min.py
ONE15LOG=/SNOPlusSlowControl/SNOPlusSlowControl/log/onefifteenmin.log


RUNNING=`ps -ef | grep 1min | grep /usr/bin/python`
if [ "$RUNNING" == "" ]
then
  echo "1min script is not running on `hostname`!"
  python ${HOMEDIR}${ONEMINLOC} &
  SUBJECT="1min script restarted on `hostname`"
  MESSAGE="1min script restarted at `date` as `ps -ef | grep poll | grep \usr`"
  echo $MESSAGE | cat >> ${HOMEDIR}${ONEFIFTEENLOG}
  echo "1min script is started on `hostname`."
else
  echo "1min script is running on `hostname`."
fi
