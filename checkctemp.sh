#!/bin/bash
#To get mail and see errors when trying to cavitytemps.py from this, 
#Remove MAILTO='' in the cronjob
MAILTO=""
RUNNING=`ps -ef | grep cavitytemps.py | grep python`
if [ "$RUNNING" == "" ]
then
  echo "cavitytemps script is not running on `hostname`!"
  cd /home/uwslowcontrol/pi_db/cavitytemp/
  python /home/uwslowcontrol/pi_db/cavitytemp/cavitytemps.py &
  SUBJECT="cavitytemps script restarted on `hostname`"
  MESSAGE="cavitytemps script restarted at `date` as `ps -ef | grep cavitytemps`"
  echo $MESSAGE | cat >> /home/uwslowcontrol/pi_db/log/cavitytemp.log
  echo "cavitytemps script is started on `hostname`."
else
  echo "cavitytemps script is running on `hostname`."
fi
