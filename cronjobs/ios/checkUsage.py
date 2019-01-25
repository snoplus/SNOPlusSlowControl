#!/usr/bin/python
# The purpose of this script is to look in 
# checkUsage.txt and email a warning if a
# partition gets too full. So, this should 
# run after (/as a part of) checkUsage.sh.
#TODO: Would be better to have diskUsage.sh's commands run 
#in python using a command line tool, then parse the
#output and handle all alarms here


import sys

if __name__=='__main__':
    usage=[]
    partitions=["sda3","sda4"]
    # ones we are interested in checking
    alarmUsage=[50,80]
    alarm=False
    
    with open(sys.argv[1], 'r') as f:
      for line in f:
        for partition in range(len(partitions)):
          if (line.find(partitions[partition]) != -1):
            percent=line.find('% /')
            if (percent!=-1):
              if (int(line[percent-2:percent])>alarmUsage[partition]):
                alarm=True
    print alarm
