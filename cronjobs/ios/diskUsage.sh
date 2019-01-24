#!/bin/sh
# This script checks the current disk usage,
# then writes it to diskUsage.txt.  It then
# checks that the usage is not above a 
# maximum value (like 70%), and if it is,
# it sends an email.
#TODO: Write this in a python script and add the ability to send an alarm to the
# shifting GUI?


HOMEDIR=/home/slowcontroller
DISKUSELOG=/SNOPlusSlowControl/SNOPlusSlowControl/log/IOSdiskUsage.txt

echo "At `date` the disk usage is" | cat > ${HOMEDIR}${DISKUSELOGLOC}
df | cat >> ${HOMEDIR}${DISKUSELOGLOC} 
ALARM=`python /home/slowcontroller/checkUsage.py /home/slowcontroller/diskUsage.txt`

if [ $ALARM == "True" ]
then
  echo "IOS `hostname` at storage warning limit" | cat > ${HOMEDIR}${DISKUSELOGLOC}    
  echo "Sending warning... IOS at storage warning limit"
fi

if [ $ALARM == "False" ]
then
  echo "Disk usage under warning limit"
fi
