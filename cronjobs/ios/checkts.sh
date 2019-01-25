#!/bin/sh

HOMEDIR=/home/slowcontroller
TSDIR=/SNOPlusSlowControl/SNOPlusSlowControl/util/ts_check/check_times.py
TSLOGLOC=/SNOPlusSlowControl/SNOPlusSlowControl/log/timestamp_check.log

RUNNING=`ps -ef | grep ${HOMEDIR}${TSDIR} | grep python`
if [ "$RUNNING" == "" ]
then
  echo "Timestamp checker is not running on `hostname`!"
  python ${HOMEDIR}${TSDIR} &
  SUBJECT="Timestamp checker restarted on `hostname`"
  MESSAGE="Timestamp checker restarted at `date` as `ps -ef | grep check_times | grep \usr`"
  echo $MESSAGE | cat >> ${HOMEDIR}${TSLOGLOC}
  echo "Timestamp checker is started on `hostname`."
else
  echo "Tiemstamp checker is running on `hostname`."
fi
