#After the self.pi_list is parsed like a couchdb entry, this class is
#responsible for checking the Current values against alarm threhsolds.
#Uses an instance of the alarmserver.py class, as well as the couchdb utils,
#to post alarms and update the alarms database

#FIXME: need logging added.  Will also want to add in an alarmposter instance?
# Or have it done in main, and pass returns to the AlarmPoster from returns on
#methods?
import timeconverts as tc
import thelogger as l
import mail as m
import time

class IOSAlarmHandler(object):
    '''This class is responsible for checking PIDB data against the
    alarm thresholds in the channel database, and updating the alarms
    dictionary.  This class also contains methods for using the given
    couchutils class to update the alarms in the alarms database.'''
    def __init__(self,CouchConn,AlarmPoster,ios_num):
        self.ios_num = ios_num
        self.AlarmPoster = AlarmPoster
        self.logger = l.get_logger(__name__)

    #Compares pi_data to channeldb alarm parameters
    def checkThresholdAlarms(self,ios_data, channeldb, alarms,version):
        prev_alarms = alarms
        alarm_states = {}
        alarms_dict = {}
        alarms_dict["timestamp"] = int(time.time())
        alarms_dict["sudbury_time"] = tc.unix_to_human(alarms_dict["timestamp"])
        alarms_dict["version"] = version
        alarms_dict["ios"] = self.ios_num
        for card_map in channeldb["cards"]:
            card_name = card_map["card"]
            if card_map["card_model"]=="ios408":
                numChannels=1
            else:
                numChannels = len(card_map["channels"])
                while (card_map["channels"][numChannels-1]["type"]=="spare" and numChannels!=0):
                    numChannels = numChannels - 1
            alarms[card_name] = [0]*numChannels
            alarms_dict[card_name] = []
            for channel in range(numChannels):
                chn_voltage = ios_data[card_name]["voltages"][channel]
                chn_thresholds = card_map["channels"][channel]
                isEnabled = 0
                try:
                    isEnabled = chn_thresholds["isEnabled"]
                except:
                    isEnabled = 0
                if isEnabled>0:
                    if chn_voltage<chn_thresholds["lolo"] or chn_voltage>chn_thresholds["hihi"]:
                        alarms[card_name][channel] = 2
                    elif chn_voltage<chn_thresholds["lo"] or chn_voltage>chn_thresholds["hi"]:
                        alarms[card_name][channel] = 1
                isAlarm = 0
                this_alarm ={}
                if prev_alarms:
                    if alarms[card_name][channel]>0 and prev_alarms[card_name][channel]>0:
                        isAlarm = 1
                        if alarms[card_name][channel]==1:
                            this_alarm["reason"] = "alarm"
                        if alarms[card_name][channel]==2:
                            this_alarm["reason"] = "action"
                if isAlarm>0:
                    this_alarm["channel"] = channel
                    this_alarm["voltage"] = chn_voltage
                    this_alarm.update(chn_thresholds)
                    del this_alarm["isEnabled"]
                    del this_alarm["multiplier"]
                    alarms_dict[card_name].append(this_alarm)
        return alarms, alarms_dict

    
    #Clears all alarms for all entries in the channel database 
    def clearAllAlarms(self,channeldb):
        for card_map in channeldb["cards"]:
            for channel in card_map["channels"]:
                channel_id = None
                try:
                    channel_id = channel["alarmid"]
                except KeyError:
                    #Entry does not have an alarmid. Ignore
                    pass
                if channel_id is not None:
                    self.AlarmPoster.clear_alarm(channel_id)       
    
    #Posts any alarms to the Alarm Server, clears items no longer alarming
    def postAlarmServerAlarms(self,alarms_dict,alarms_last,cardsHW):
        #only check alarms_dict entries associated with databases
        nowalarming = []
        card_list = list(cardsHW)
	print("CURRENT ALARMS LAST: " + str(alarms_last))
        for card in card_list:
            for item in reversed(alarms_dict[card]):
                #First, post alarms for all items in alarm dictionary
                if (item["reason"] == "action") or (item["reason"] == "alarm"):
                    self.AlarmPoster.post_alarm(item["alarmid"])
                    nowalarming.append(item["alarmid"])
    
            #Now, clear out alarms that were alarming but are no longer alarming
            for item in reversed(alarms_last[card]):
    	        if (item["reason"] == "action") or (item["reason"] == "alarm"):
                        if item["alarmid"] not in nowalarming:
                            self.AlarmPoster.clear_alarm(item["alarmid"])

    
    #Sends alarms email
    def sendAlarmsEmail(self,alarms_dict,alarms_last,channeldb, recipients_filename):
        title = "IOS Alarms at " + str(alarms_dict["sudbury_time"]) + "\n\n"
        old_list = []
        new_list = []
        new_alarm_dict = {}
        for card_map in channeldb["cards"]:
            name = card_map["card"]
            if alarms_last != {}:
                 for alarm_num in range(len(alarms_last[name])):
                      channel_id = str(alarms_last[name][alarm_num]["id"])
                      channel_type = str(alarms_last[name][alarm_num]["type"])
                      channel_signal = str(alarms_last[name][alarm_num]["signal"])
                      old_list.append(channel_type+"-"+channel_id+" ("+channel_signal+")")
            for alarm_num in range(len(alarms_dict[name])):
                reason = alarms_dict[name][alarm_num]["reason"]
                if reason!="off":
                    try:
                        channel_id = str(alarms_dict[name][alarm_num]["id"])
                        channel_type = str(alarms_dict[name][alarm_num]["type"])
                        channel_signal = str(alarms_dict[name][alarm_num]["signal"])
                        new_list.append(channel_type+"-"+channel_id+" ("+channel_signal+")")
                        msg = channel_type + "-" + channel_id + " (" + channel_signal + ")\n"
                        unit = alarms_dict[name][alarm_num]["unit"]
                        hi = "hi"
                        lo = "lo"
                        if reason =="action":
                            hi = "hihi"
                            lo = "lolo"
                        msg = msg + "Signal: " + str(alarms_dict[name][alarm_num]["voltage"]) + " " + unit
                        msg = msg + " outside " + reason + " limits of " + str(alarms_dict[name][alarm_num][lo]) + " " + unit
                        msg = msg + " to " + str(alarms_dict[name][alarm_num][hi]) + " " + unit + "\n\n"
                        new_alarm_dict[channel_type+"-"+channel_id+" ("+channel_signal+")"] = msg
                    except:
                        pass
        constant_alarms = set(old_list) & set(new_list)
        new_alarms = set(new_list) - set(old_list)
        no_longer_alarms = set(old_list) - set(new_list)
        super_msg = title
        if new_alarms != set([]):
             super_msg = super_msg + "New Alarms:" + "\n\n"
             for x in new_alarms:
                  super_msg = super_msg + new_alarm_dict[x]
        if super_msg != title:
            m.sendMail("Alarms at " + str(alarms_dict["sudbury_time"]), super_msg,recipients_filename)

class IOSRackAlarmHandler(IOSAlarmHandler):
    '''This class has the same base alarm handling capabilities as IOSAlarmHandler,
       plus additional methods for managing alarms associated with a rack.'''
    
    def __init__(self,CouchConn,AlarmPoster,ios_num): 
	super(IOSRackAlarmHandler,self).__init__(CouchConn,AlarmPoster,ios_num)

    def getLowVoltList(self, ios_data, channeldb, threshold = 1.5):
        racklowvoltnums = [0,0,0,0,0,0,0,0,0,0,0,0,0] # SNO+ has eleven PMT racks + 1 timing rack
        for card_map in channeldb["cards"]:
            card_name = card_map["card"]
            if card_map["card_model"]=="ios408":
                numChannels=1
            else:
                numChannels = len(card_map["channels"])
                while (card_map["channels"][numChannels-1]["type"]=="spare" and numChannels!=0):
                    numChannels = numChannels - 1
            #FIXME: rather than hardcode racklowvoltnums, have a for loop that goes through
            #channels and finds the number of racks
            for channel in range(numChannels):
                chn_voltage = ios_data[card_name]["voltages"][channel]
    	        chn_thresholds = card_map["channels"][channel]
    	        #Build the lowvolt_list: increments a rack's # low voltages by 1 for each voltage below 1.5 volts
    	        if chn_thresholds["type"] == "rack":
    	            if abs(chn_voltage) < threshold : 
    	                racknum = int(chn_thresholds["id"])
    	                racklowvoltnums[racknum-1]+=1
    	        elif chn_thresholds["type"] == "timing rack":
    	            if abs(chn_voltage) < threshold :
    	                racknum = 12
                        racklowvoltnums[racknum-1]+=1
        return racklowvoltnums

    def disableOffRackAlarms(self, lowvolt_list, alarms_dict, HWDict, onracks, IBootPwr):
        alarms_dict["DetectorServer_Conn"] = "OK"
        alarms_dict["IBoot3Power"] = "ON"
        card_list = list(HWDict)
	allrackvlow_list = []
	offrack_list = []
	#see if a rack had five voltages that are less than the "offrack" value in the channeldb.  If so, add
	#the rack's number to allrackvlow_list
	for entry in range(0,12):
		if lowvolt_list[entry] == 5:
		  	racknum = entry + 1
			allrackvlow_list.append(racknum)
	#If a rack is in the all V low list, check if the ADAMs have it shut off.  add to offrack_list if both true.
	if IBootPwr == 0 :
		alarms_dict["IBoot3Power"] = "OFF"
	offrack_list=self._TrueOffList(onracks, allrackvlow_list)
	#Set the rack statuses in alarms_dict to "off".
	if offrack_list == 'none':
		self.logger.info('IOSRackAlarmHandler: No offracks list built was built. set alarms_dict server connection to bad.')
		alarms_dict["DetectorServer_Conn"] = "NONE"
	else:
	  	for card in card_list:
			for item in reversed(alarms_dict[card]):
				type = item["type"]
				id = item["id"]
				if type == "rack":
					if id in offrack_list:
						item["reason"]="off"
				if type == "timing rack":
					if 12 in offrack_list:
						item["reason"]="off"
				if type == "MTCD":
				  	if 12 in offrack_list:
					  	item["reason"]="off"
	return alarms_dict

	def _TrueOffList(self,AdamReply, lowvolt_list):
		'''Function takes in a 16-bit Adam reply of which racks are powered,
                    compares to a list of low voltage reading numbers on each rack
                      If there's a match, the rack number is added to the returned offrack_list.'''
	  	Adamsoffracks = []
		offrack_list = []
		#0's in the AdamReply correspond to off racks. If zero, put the rack's ID in Adamsoffracks
		#[::-1] is some trickery to reverse the adam reply for easier reading.
		if AdamReply == 'none':
			offrack_list='none'
		else:
			i=0
			for bit in str(AdamReply)[::-1]:
			  	if bit == '0' and i<12:
					Adamsoffracks.append(i+1)
				i=i+1
			for item in lowvolt_list:
				if item in Adamsoffracks:
					offrack_list.append(item)
		return offrack_list
