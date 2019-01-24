#!/bin/bash
#To get mail and see errors when trying to cavitytemps.py from this, 
#Remove MAILTO='' in the cronjob
MAILTO=""

#Modify HOMEDIR to where SNOPlusSlowControl lives on your machine
HOMEDIR=/home/uwslowcontrol
CTEMPLOC=/SNOPlusSlowControl/SNOPlusSlowControl/util/cavitytemp/
CTEMPLOGLOC=/SNOPlusSlowControl/SNOPlusSlowControl/log/cavitytemp.log

RUNNING=`ps -ef | grep cavitytemps.py | grep python`
if [ "$RUNNING" == "" ]
then
  echo "cavitytemps script is not running on `hostname`!"
  python ${HOMEDIR}${CTEMPLOC} &
  SUBJECT="cavitytemps script restarted on `hostname`"
  MESSAGE="cavitytemps script restarted at `date` as `ps -ef | grep cavitytemps`"
  echo $MESSAGE | cat >> ${HOMEDIR}${CTEMPLOGLOC}
  echo "cavitytemps script is started on `hostname`."
else
  echo "cavitytemps script is running on `hostname`."
fi
