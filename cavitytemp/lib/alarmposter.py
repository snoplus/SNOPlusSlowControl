
#This file contains classes associated with posting alarms to the
#slowcontrol couchdb.

import alarm_server as al

class AlarmPoster(object):
    #initalize with channeldb 
    def __init__(self,channeldb,datatype):
        self.channeldb = channeldb
        self.currentValues = None
        if datatype == "temp_sensors":
            self.vtype = "temp_sensors"
            self.alarmdb_url = "slowcontrol-alarms/cavitytemps"
            self.alarmid = 30040
        else:
            self.alarmdb_url = None
            self.alarmid = None
            self.vtype = None
        self.currentAlarms = None
        self.prevAlarms = None

    def __getChannelInfo(self):
        #get channel info specific to the value dictionary given
        chaninfo = None
        for value in self.currentValues:
           if self.currentValues[value] == "true":
               if value in self.channeldb:
                   chaninfo = self.channeldb[value]
        return chaninfo

    #check readings agains alarm thresholds in the channel database
    #if a reading is out of bounds, alarm on it
    def __buildCurrentAlarmDict(self):
        chaninfo = self.__getChannelInfo()
        #if we have the channel info, start checking thresholds
        #FIXME: Be more clever with the db names to generalize this code
        alarm_dict = {"temp_sensors": "true", self.vtype: {}}
        for entry in chaninfo:
            sensorname = "Sensor_"+str(entry["id"])
            threshdict = {}
            alarmtypes = ["lo","lolo","hi","hihi"]
            for altype in alarmtypes:
                threshdict[altype] = entry[altype]
            threshdict["isEnabled"] = entry["isEnabled"]
            reading = self.currentValues[sensorname]
            #add this channel's value to the alarm dictionary if outside
            #alarm threshold and is enabled
            if not (threshdict["lo"] <= reading <= threshdict["hi"]):
                if threshdict["isEnabled"] != 0:
                    alarm_dict[self.vtype][sensorname]=reading
        return alarm_dict

    def setCurrentChanneldb(self,newchandb):
        self.channeldb = newchandb

    def postAlarms(self):
        #If there is a cavity temp sensor alarm, post it and save to the
        #Couch alarms dictionary
        alarm_dict = self.__buildCurrentAlarmDict()
        if alarm_dict[self.vtype]:
            #al.post_alarm(self.alarm_id)
            print("in alarm found statement!")
            cu.saveCTAlarms(alarm_dict)
        #if no alarming values but different than last dict, clear alarms
        elif self.currentAlarms != self.prevAlarms:
            al.clear_alarm(self.alarm_id)
        #alarms updated: Set your previous alarms to be the current alarms
        self.prevAlarms = self.currentAlarms

if __name__ == "__main__":
    print("NO MAIN CALL RUN DEFINED YET")
