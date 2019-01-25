#!/bin/sh
HOMEDIR=/home/slowcontroller
FIFTEENMINLOC=/SNOPlusSlowControl/SNOPlusSlowControl/util/ios_1_15_min/15min.py
ONEFIFTEENLOG=/SNOPlusSlowControl/SNOPlusSlowControl/log/onefifteenmin.log

RUNNING=`ps -ef | grep 15min | grep /usr/bin/python`
if [ "$RUNNING" == "" ]
then
  echo "15min script is not running on `hostname`!"
  python ${HOMEDIR}${FIFTEENMINLOC} &
  SUBJECT="15min script restarted on `hostname`"
  MESSAGE="15min script restarted at `date` as `ps -ef | grep poll | grep \usr`"
  echo $MESSAGE | cat >> ${HOMEDIR}${ONEFIFTEENLOG}
  echo "15min script is started on `hostname`."
else
  echo "15min script is running on `hostname`."
fi
