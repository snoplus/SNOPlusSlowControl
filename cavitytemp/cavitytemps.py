#This script uses the Digital Temperature Sensor installed in Noel's
#Directory to read out the string of temperature sensors in the SNO+
#Cavity.  These values are then sent to the SNO+ couchDB where slow
#control data is saved.
#Written by: Teal Pershing
#Last Updated: 03/20/2017

import subprocess
import lib.couchutils as cu
import time

def getReading():
    timedelay = '1'
    numreads = '1'  #Set to zero to forever loop
    sport = '/dev/ttyUSB0' #Location of serial port
    logfile = '/home/uwslowcontrol/pi_db/log/ctemplog.log &'
    comm = ['digitemp_DS9097U','-i','-a','-d',timedelay,
        '-n',numreads,'-s',sport] #-l logfile
    #This is deprecated!  But we're stuck at 2.6.6 so...
    tempreading = subprocess.Popen(comm, stdout=subprocess.PIPE).communicate()[0]
    return tempreading

#Takes in result from getReading and parses for couchDB saving
#Also adds timestamp to the document being saved
class TempReader(object):
    def __init__(self, readstring):
        self.rawread = readstring
        self.readingdict = {}

        self.settime()


    def parsevalues(self):
        print("Theparse") 

    def settime(self):
        self.readingdict["timestamp"] = int(time.time())           

if __name__ == "__main__":
    rawread = getReading()
    reader = TempReader(rawread)
    f = open("TempReadings.txt")
    f.write(reading)
    f.close()
