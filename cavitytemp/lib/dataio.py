#Functions for grabbing temperature data from either a log file or
#directly from the sensor
import linecache
import subprocess

#Sends command to temp reader, returns raw read data
def getReading():
    timedelay = '1'
    numreads = '1'  #Set to zero to forever loop
    sport = '/dev/ttyUSB0' #Location of serial port
    comm = ['digitemp_DS9097U','-i','-a','-d',timedelay,
        '-n',numreads,'-s',sport]
    #This is deprecated!  But we're stuck at 2.6.6 so...
    tempreading = subprocess.Popen(comm, stdout=subprocess.PIPE).communicate()[0]
    print(tempreading)
    return tempreading

def getFileTail(filename, numlines):
    #for a given file, get the last numlines in the file
    with open(filename, 'r') as f:
        for i, l in enumerate(f):
            pass
    flength = i
    firstline = flength - numlines
    data = []
    for l in range(firstline,flength):
        dline = linecache.getline(filename,l)
        data.append(dline)
    return data
    

#Save readings to text file for Noel
def WriteReadToLog(TempReader):
    SensorReads = TempReader.getSensorLines()
    if SensorReads is not None:
        f = open("TempReadings.log","a")
        f.write("\n")
        for sensorline in SensorReads:
            combinedline = " ".join(sensorline)
            f.write(combinedline + "\n")
        f.close()


