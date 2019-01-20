#!/bin/sh
# This script checks the current disk usage,
# then writes it to diskUsage.txt.  It then
# checks that the usage is not above a 
# maximum value (like 70%), and if it is,
# it sends an email.

echo "At `date` the disk usage is" | cat > /home/slowcontroller/diskUsage.txt
df | cat >> /home/slowcontroller/diskUsage.txt 
ALARM=`python /home/slowcontroller/checkUsage.py /home/slowcontroller/diskUsage.txt`

if [ $ALARM == "True" ]
then
  python /home/slowcontroller/sendEmail.py "IOS `hostname` at storage warning limit" "`cat /home/slowcontroller/diskUsage.txt`"   
  echo "Sending warning... IOS at storage warning limit"
fi

if [ $ALARM == "False" ]
then
  echo "Disk usage under warning limit"
fi
