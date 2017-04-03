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
    def __init__(self, rawreadlines):
        self.rawreadlines = rawreadlines
        self.readingdict = {"cavitytemps":"true"}



    def parseTemps(self):
        sensorlines = self.getSensorLines()
        for line in sensorlines:
            for j, entry in enumerate(line):
                if entry == "Sensor":
                    key = line[j] + " " + line[j+1]
                    val = float(line[j+3])
                    self.readingdict[key] = val


    #Return only the lines in rawread that have sensor readings
    def getSensorLines(self):
        valuelines = []
        for line in self.rawreadlines:
            if line.find('Sensor') != -1:
                sline = line.split(" ")
                valuelines.append(sline)
        return valuelines

    def show(self):
        print("Current dictionary to push to couchdb: \n")
        print(self.readingdict)

    def settime(self):
        self.readingdict["timestamp"] = int(time.time())           

if __name__ == "__main__":
    while True:
        rawread = getReading()
        rawread = rawread.splitlines()
#        f = open("TempReadings.txt","r")
#        rawread = f.readlines()
        reader = TempReader(rawread)
        reader.settime()
        reader.parseTemps()

        f = open("TempReadings.txt","a")
        f.write("\n")
        towrite = "".join(rawread)
        f.write(towrite)
        f.close()

        #save the dictionary to couchDB
        cu.saveValuesToCT(reader.readingdict)
        print("IIIIITS SLEEPIN TIME~")
        time.sleep(360)
