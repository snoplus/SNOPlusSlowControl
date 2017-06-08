

#Takes in result from getReading and parses for couchDB saving
#Also adds timestamp to the document being saved
class TempReader(object):
    def __init__(self, rawreadlines):
        self.rawreadlines = rawreadlines
        self.hasrawvalues = False
        self.parsed = False
        self.readingdict = {"temp_sensors":"true"}


    #Grabs the sensor number and temperature in celsius
    def parseTemps(self):
        sensorlines = self.getSensorLines()
        if self.hasrawvalues:
            for line in sensorlines:
                for j, entry in enumerate(line):
                    if entry == "Sensor":
                        key = line[j] + "_" + line[j+1]
                        val = float(line[j+3])
                        self.readingdict[key] = val
            self.parsed = True


    #Return only the lines in rawread that have sensor readings
    def getSensorLines(self):
        valuelines = []
        for line in self.rawreadlines:
            if line.find('Sensor') != -1:
                if line.find('Temperature Sensor') != -1:
                    continue
                else:
                    sline = line.split(" ")
                    valuelines.append(sline)
        if valuelines:
            self.hasrawvalues = True
            return valuelines
        else:
            return None

    def show(self):
        print("Current dictionary to push to couchdb: \n")
        print(self.readingdict)

    def settime(self, val):
        self.readingdict["timestamp"] = val          

    def setunit(self, val):
        self.readingdict["temp_units"] = val

