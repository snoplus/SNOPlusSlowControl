
#This file contains classes associated with posting alarms to the
#slowcontrol couchdb.
from email import utils
import emailsend as es
import couchutils as cu
import alarm_server as al
import time

class AlarmPoster(object):
    #initalize with channeldb 
    def __init__(self,channeldb):
        self.channeldb = channeldb #Current couchdb channeldb
        self.currentValues = None
        self.alarmid = None
        self.vtype = None
        self.currentAlarms = None
        self.prevAlarms = None
        self.sensorkey = None

    def updateCurrentValues(self, currentvals):
        '''Takes in a dictionary with the most recent values from the sensor'''
        self.currentValues = currentvals

    def set_alarmid(self,idnum):
        '''Set the alarm id to be posted'''
        self.alarmid = idnum

    def set_datatype(self,datatype):
        '''Set the type of data (saved into database entry)'''
        self.vtype = datatype

    def set_sensorkey(self,name):
        '''Set the sensor name as is should show up in the data entry
        Will have a "_" with the sensor's id number attached. Need
        This to match keys in the self.currentValues dictionary'''
        self.sensorkey=name

    def _getChannelInfo(self):
        chaninfo = None
        if self.vtype in self.channeldb:
            chaninfo = self.channeldb[self.vtype]
        return chaninfo


    #check readings against alarm thresholds in the channel database
    #if a reading is out of bounds, alarm on it
    def _buildCurrentAlarmDict(self):
        chaninfo = self._getChannelInfo()
        #if we have the channel info for our data, start checking thresholds
        alarm_dict = {self.vtype: "true", "current_alarms": {}}
        timest = int(time.time())
        alarm_dict["timestamp"] = timest          
        #Converts unix timestamp to human readable local time (Sudbury time)
        human_time = utils.formatdate(timest, localtime=True)
        alarm_dict["date"] = human_time
        alarm_dict["alarming_sensors"] = []
        for entry in chaninfo:
            sensorname = str(self.sensorkey)+"_"+str(entry["id"])
            alarm_dict["current_alarms"][sensorname] = {}
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
                    alarm_dict["alarming_sensors"].append(sensorname)
                    alarm_dict["current_alarms"][sensorname]["value"]=reading
                    alarm_dict["current_alarms"][sensorname]["id"] = str(entry["id"])
        return alarm_dict

    def setCurrentChanneldb(self,newchandb):
        '''Set the current channel database dictionary that defines 
        alarm thresholds'''
        self.channeldb = newchandb

    def checkForAlarms(self):
        '''If there is a cavity temp sensor alarm in the current temperature data, 
        post it and save to the couch alarms dictionary on couchDB'''
        self.currentAlarms = self._buildCurrentAlarmDict()
        #if no previous alarms, start by clear alarms
        if self.prevAlarms is None:
            #no alarms,just clear; we don't know what the last alarms were
            al.clear_alarm(self.alarmid)
            if len(self.currentAlarms["alarming_sensors"]) > 0:
                cu.saveCTAlarms(self.currentAlarms)
                es.sendCTAlarmEmail(self.currentAlarms["date"])
                al.post_alarm(self.alarmid)
	elif set(self.currentAlarms["alarming_sensors"]) != set(self.prevAlarms["alarming_sensors"]):
            if len(self.currentAlarms["alarming_sensors"]) == 0:
                al.clear_alarm(self.alarmid)
                cu.saveCTAlarms(self.currentAlarms)
                es.clearCTAlarmEmail(self.currentAlarms["date"])
            else:
                cu.saveCTAlarms(self.currentAlarms)
                es.sendCTAlarmEmail(self.currentAlarms["date"])
                al.post_alarm(self.alarmid)
        #alarms updated: Set your previous alarms to be the current alarms
        self.prevAlarms = self.currentAlarms

if __name__ == "__main__":
    print("NO MAIN CALL RUN DEFINED YET")
