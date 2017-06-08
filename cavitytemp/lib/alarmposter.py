
#This file contains classes associated with posting alarms to the
#slowcontrol couchdb.

import alarm_server as al
class AlarmPoster(object):
    #initalize with channeldb and first set of data values
    def __init__(self,channeldb,values):
        self.channeldb = channeldb
        self.values = values
        if self.values["temp_sensors"] == "true":
            self.vtype = "temp_sensors"
            self.alarmdb_url = "slowcontrol-alarms/cavitytemps"
            self.alarmid = 30050
        else:
            self.alarmdb_url = None
        self.currentAlarms = self.buildCurrentAlarmDict()
        self.prevAlarms = None

   def getChannelInfo(self):
        #get channel info specific to the value dictionary given
        chaninfo = None
        for value in self.values:
           if self.values[value] = "true":
               if value in self.channeldb:
                   chaninfo = self.channeldb[value]
        return chaninfo

    #check readings agains alarm thresholds in the channel database
    #if a reading is out of bounds, alarm on it
    def buildCurrentAlarmDict(self):
        chaninfo = self.getChannelInfo()
        #if we have the channel info, start checking thresholds
        #FIXME: Be more clever with the db names to generalize this code
        alarm_dict = {self.vtype: {}}
        for entry in chaninfo:
            sensorname = "Sensor_"+str(entry["id"])
            threshdict = {}
            alarmtypes = ["lo","lolo","hi","hihi"]
            for altype in alarmtypes:
                threshdict[altype] = entry[altype]
            reading = self.values[sensorname]
            if ((reading < threshdict["lo"]) or (reading > threshdict["hi"]):
                alarm_dict[self.vtype][sensorname]=reading
        return alarm_dict

    def postAlarms(self):
        #If there is a cavity temp sensor alarm, post it and save to the
        #Couch alarms dictionary
        alarm_dict = self.buildAlarmDict()
        if alarm_dict[self.vtype]:
            al.post_alarm(self.alarm_id)
            cu.saveCTAlarms(alarm_dict)
        #if no alarming values this or last time, just return
        elif self.currentAlarms == self.prevAlarms:
            return
        #here, there's no current alarms but is different than our previous alarms.
        #Clear alarms out at alarm server
        else:
            al.clear_alarm(self.alarm_id) 
