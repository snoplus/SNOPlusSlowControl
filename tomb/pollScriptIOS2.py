#!/usr/bin/python
#to pull data from slow control ios and put it in ioserverdata db

from __future__ import print_function
import sys
import socket
import json, httplib2, couchdb, string, time, re
import os
import redis
import hiredis
import smtplib
import mimetypes
from email import utils
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
import threading
import psycopg2
from psycopg2.pool import ThreadedConnectionPool

ios =  int(socket.gethostname()[3]) 
period = 5

def getcreds(location):
	f = open(location, "rb")
	for line in f:
		if "username" in line:
			user = re.sub("username ", "", line)
			user=user.rstrip()
		if "password" in line:
			pwd = re.sub("password ", "", line)
			pwd=pwd.rstrip()
	return user, pwd

recipientfile=open("/home/slowcontroller/alarmsEmailList.txt","r")
recipients = recipientfile.readlines();
recipient = 'tjpershing@ucdavis.edu'

#Alarm server credentials
alarmUser, alarmPassword = getcreds("/home/slowcontroller/config/alascred.conf")

#Alarmslist g-mail account credentials
gmailUser, gmailPassword = getcreds("/home/slowcontroller/config/gmailcred.conf")

#Connection info for couchdb
couch = couchdb.Server()
couchuser, couchpassword = getcreds("/home/slowcontroller/config/SCcouchcred.conf")
couch.resource.credentials = (couchuser, couchpassword)

def unix_to_human(unix_time):
    human_time = utils.formatdate(unix_time, localtime=True)
    return human_time

def checkCards():
    f = open('/home/slowcontroller/hmhj/lib/hmhj_layer1-0.2/priv/cards.conf', 'r')
    cards = []
    cardDict = {}
    for line in f:
        comma = string.find(line,",")
        key = line[string.find(line,"{")+1:comma]
        value = line[comma+1:string.rfind(line,"}")]
        if key=="cards":
            start = -1
            i = 0
            for char in value:
                if char=="[":
                    start = i
                if char=="," or char=="]":
                    cards.append(value[start+1:i])
                    start = i
                i = i+1
        if key in cards:
            start = string.find(value,"card_type,")
            value = value[start+10:len(value)]
            end = string.find(value,"}")
            cardDict[key] = value[0:end]
    return cardDict



def connectToDB(dbName):
    status = "ok"
    db = {}
    try:
        db = couch[dbName]
    except:
        print("Failed to connect to " + dbName, file=sys.stderr)
        status = "bad"
    return status, db


##---------BEGIN ALARM SERVER POSTING FUNCTIONS-----------##

pool = ThreadedConnectionPool(1,10, host='dbug.sp.snolab.ca', database='detector', user=alarmUser, password=alarmPassword)

def post_alarm(alarm_id):
    """
    Posts an alarm to the database for an alarm with a given id.

    Returns None if there was an error or the alarm was already active.
    If the alarm is successfully posted it returns the unique id of the
    alarm that was posted.
    """

    result = None

    try:
        conn = pool.getconn()
    except psycopg2.Error as e:
        #if the database is down we just print the error
        print(str(e))
    else:
        #we have a connection
        try:
            with conn:
                with conn.cursor() as curs:
                    curs.execute("SELECT * FROM post_alarm(%i)" % alarm_id)
                    result = curs.fetchone()[0]
        except psycopg2.Error as e:
            #who knows what went wrong?  Just print the error
            print(str(e))
            #close the connection since it's possible the database
            #is down, so we don't want to use this connection again
            conn.close()
        
        pool.putconn(conn)
    return result

def clear_alarm(alarm_id):
    """
    Clears an alarm to the database for an alarm with a given id.

    Returns None if there was an error or the alarm is already cleared.
    If the alarm is successfully cleared it returns the unique id of the
    alarm that was cleared.
    """

    result = None

    try:
        conn = pool.getconn()
    except psycopg2.Error as e:
        #if the database is down we just print the error
        print(str(e))
    else:
        #we have a connection
        try:
            with conn:
                with conn.cursor() as curs:
                    curs.execute("SELECT * FROM clear_alarm(%i)" % alarm_id)
                    result = curs.fetchone()[0]
        except psycopg2.Error as e:
            #who knows what went wrong?  Just print the error
            print(str(e))
            #close the connection since it's possible the database
            #is down, so we don't want to use this connection again
            conn.close()
        
        pool.putconn(conn)

    return result

def post_heartbeat(name):
    """
    Recursive function that posts a heartbeat to the database every 10 seconds.

    See stackoverflow.com/questions/3393612
    """
    try:
        conn = pool.getconn()
    except psycopg2.Error as e:
        #if the database is down we just print the error
        print(str(e))
    else:
        #we have a connection
        try:
            with conn:
                with conn.cursor() as curs:
                    curs.execute("SELECT * FROM post_heartbeat('%s')" % name)
        except psycopg2.Error as e:
            #who knows what went wrong; just print the error
            print(str(e))
            #close the connection since it's possible the database
            #is down, so we don't want to reuse this connection
            conn.close()
        pool.putconn(conn)
    
    t = threading.Timer(10, post_heartbeat, [name])
    t.daemon = True
    t.start()

##-------END ALARM SERVER POSTING FUNCTIONS----------##


##-------FUNCTIONS ADDED FOR RACK CONTROL VIA DETECTOR SERVER---------##

def connectToDetServer():
    status = "ok"
    DSsocket=redis.Connection(host="minard.sp.snolab.ca", port=8520, socket_connect_timeout=15.0, retry_on_timeout=True)
    try:
      	DSsocket._connect()
	DSsocket.on_connect()
    except:
        print("Failed to connect to Detector Server", file=sys.stderr)
	status = "bad"
    return status, DSsocket


#Powers down the rack using the connection to the detector server
def ShutDownRack(racknum):
    status, sock=connectToDetServer()
    if status == "ok":
	#Now try sending the shutdown command, with the rack number passed in.  We only try again if
	#we get a response error, which is associated with timeouts.
	while True:
		try:
			sock.send_command("PowerOffRacks "+str(racknum))
			reply=sock.read_response()
		except redis.ResponseError:
			print("Recieved a response error.  May be a timeout issue. Sleeping 1 sec, Trying again...")
			time.sleep(5)
			continue
		break
	if reply == "OK":
		print("RACK NO. "+str(racknum)+" HAS BEEN POWERED DOWN.")
	else:
		print("Reply from rack was not OK.  Shutdown may have failed.")
	sock.disconnect()
    return


def ShutDownTimingRack():
    status, sock=connectToDetServer()
    if status == "ok":
	#Now try sending the shutdown command for the timing rack.  We only try again if
	#we get a response error, which is associated with timeouts.
	while True:
		try:
			sock.send_command("PowerOffTimingRack")
			reply=sock.read_response()
		except redis.ResponseError:
			print("Recieved a response error.  May be a timeout issue. Sleeping 1 sec, Trying again...")
			time.sleep(8)
			continue
		break
	if reply == "OK":
		print("THE TIMING RACK HAS BEEN POWERED DOWN.")
	else:
		print("Reply from rack was not OK.  Shutdown may have failed.")
	sock.disconnect()
    return


#Find out what racks are on.  Returns a 16 bit binary string, 1's indicate powered racks
#Racks 1-6 are in the first 8 bits, racks 7-11 and the timing rack are in bits 8-13 on last 8 bits.

#While loop: Designed to talk with detector server and try connecting
#several times before erroring.  If any connection to the server fails,
#counter increments by 1 and while loop restarts.  If counter reaches 4,
#status is set to bad and you break from the loop.  Any bad statuses reported
#by the detector server set status to bad, and break from while loop.
def GetPoweredRacks():
	counter=0
	while True:
		status, sock=connectToDetServer()
		if counter == 4:
			print("Three connect and/or response errors in a row.  Assuming error.  Continuing polling, but Bail out.")
			status = "error"
			break
		if status == "bad":
			print("No connection to detector server established. sleeping, trying again...")
			time.sleep(3)
			counter+=1
			continue
		if status == "ok":         #we have a connection
		        sock.send_command("ReadIBoot3Main")
			time.sleep(0.5)    #need a short sleep time so the buffer fills with the response
			readcheck = sock.can_read()
			if readcheck:      #the response is readable
				try:
					IBootPwr = sock.read_response()
					if IBootPwr == 0:
						fullbinreply = "{0:016b}".format(0)
					elif IBootPwr < 0 :
					        print("Error with IBoot3. Sleeping, try to get rack info again.")
						time.sleep(3)
						counter+=1
						continue
					elif IBootPwr == 1:
						sock.send_command("ReadRacks")
						time.sleep(0.5)
						reply=sock.read_response()
						binaryreply = "{0:b}".format(reply)
						#Shut down our connection, return adam reply
						fullbinreply = binaryreply.zfill(16)
						sock.disconnect()
				except redis.ResponseError:
			 		print("Recieved a response error. May be a timeout issue.  Disconnect, Sleep 5 sec, Trying again...")
					sock.disconnect()
					time.sleep(3)
					counter+=1
					continue
				break
			if not readcheck:    #Can't read the connection for whatever reason
				print("Could not get a response from IBoot read request. Incrementing counter, trying again....")
				sock.disconnect()
				time.sleep(3)
				counter+=1
				continue
	if status == "error":
		fullbinreply = "none"
		IBootPwr = "none"
	return fullbinreply, IBootPwr 

##----------END DETECTOR SERVER CONNECTION FUNCTIONS---------##

##Function takes in a 16-bit Adam reply of which racks are powered, compares to a list of racks with
##all voltages < 1 volt.  If there's a match, the rack number is added to the offrack_list.	
def TrueOffList(AdamReply, lowvolt_list):
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


def sendMail(subject, text):
    try:
        msg = MIMEMultipart()
        msg['From'] = gmailUser
        msg['Subject'] = subject
        msg.attach(MIMEText(text))
        mailServer = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(gmailUser, gmailPassword)
        msg['To'] = "alarmslist"
        mailServer.sendmail(gmailUser, recipients, msg.as_string())
        mailServer.close()
    except:
        pass
    return


def getChannelParameters():
    ios_map = {}
    dbParStatus, dbPar = connectToDB("slowcontrol-channeldb")
    if dbParStatus is "ok":
        queryresults =  dbPar.view("slowcontrol-channeldb/recent",descending=True,limit=1)
        ios_map = queryresults.rows[0].value["ioss"][ios-1]
    return ios_map

#queries not safe to view not being written

def pollCard(card, cardsHW):
    status = "ok"
    result = {}
    if card in cardsHW:
        try:
            resp,content = conn_ioserver1.request("http://127.0.0.1:8000/data/"+card,"GET")
        except:
            status = "bad"
            print("Error pulling data from IOS" + str(ios) + " card:" + card, file=sys.stderr)
        if status == "ok" and card in content:
            data = json.loads(content)
            result = data[card]
    else:
        print("Error: Attempted polling " + str(card) + " ioserver " + str(ios) + " but this is not listed on the ioserver hmhj/lib/hmhj_layer1-0.2/priv/cards.conf file", file=sys.stderr)
    return result



def getChannelVoltages(ios_map, cardsHW):
    timestamp = int(time.time())
    sudbury_time = unix_to_human(timestamp)
    ios_data = {'ios':ios, 'timestamp':timestamp, 'sudbury_time':sudbury_time}
    for card_map in ios_map["cards"]:
        card_name = card_map["card"]
        cardData = pollCard(card_name, cardsHW)
        numChannels = len(card_map["channels"])
        voltages = ["NA"]*numChannels
        while (card_map["channels"][numChannels-1]["type"]=="spare" and numChannels!=0):
            numChannels = numChannels - 1
            # This counts down from top so we don't waste space saving 
            # data from unused "spare" channels unless they are place-
            # holders between used channels
        cardDict = {}
        for key, value in cardData.iteritems():
            if key=="timestamp":
                if (value - timestamp)>5:
                    msg = "Error: ioserver " + str(ios) + " " + card_name
                    msg = msg + " time (" +  time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(value)) + ")"
                    msg = msg +"is more than 5 seconds ahead of the ioservers time (" + time.strftime("%a, %d %b %Y %H:%M:%S",time.localtime(timestamp)) + ")"
                    sendMail("Timestamp error", msg)
                if (timestamp - value)>5:
                    msg = "Error: ioserver " + str(ios) + " " + card_name
                    msg = msg + " time (" + time.strftime("%a, %d %b %Y %H:%M:%S",time.localtime(value)) + ")"
                    msg = msg + "is more than 5 seconds behind the ioservers time (" + time.strftime("%a, %d %b %Y %H:%M:%S",time.localtime(timestamp)) + ")"
                    sendMail("Timestamp error", msg)
            if key[0:7]=="channel":
                channel = int(key[7:len(key)])
                multiplier = 1
                try:
                    multiplier = card_map["channels"][channel-1]["multiplier"]
                except:
                    multiplier = 1
                voltage = cardData[key]["voltage"]*multiplier
                voltages[channel-1] = voltage
        if card_map["card_model"]=="ios408":
            cardDict['voltages']=voltages[0:1]
        else:
            cardDict['voltages'] = voltages[0:numChannels]
        ios_data[card_name] = cardDict
    return ios_data



def saveVoltages(ios_data):
    dbDataStatus, dbData = connectToDB("slowcontrol-data-5sec")
    if dbDataStatus is "ok":
        dbData.save(ios_data)


#Function: Find racks with all voltages less than 1 volt and signed as
#"off" according to the ADAMs, and then set the rack status to "off".
def DisableOffRackAlarms(lowvolt_list, alarms_dict, cardsHW):
	card_list = list(cardsHW)
	allrackvlow_list = []
	offrack_list = []
	#see if a rack had five voltages that are less than the "offrack" value in the channeldb.  If so, add
	#the rack's number to allrackvlow_list
	for entry in range(0,12):
		if lowvolt_list[entry] == 5:
		  	racknum = entry + 1
			allrackvlow_list.append(racknum)
	#If a rack is in the all V low list, check if the ADAMs have it shut off.  add to offrack_list if both true.
	onracks,IBootPwr = GetPoweredRacks()
	if IBootPwr == 0 :
		alarms_dict["IBoot3Power"] = "OFF"
	offrack_list=TrueOffList(onracks, allrackvlow_list)
	#Set the rack statuses in alarms_dict to "off".
	if offrack_list == 'none':
		print('No offracks list built was built. set alarms_dict server connection to bad.')
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
				#FIXME : ADD IN XL3 TYPE AND CHECKS
				#FOR IF THE RACK IS OFF OR NOT
	return alarms_dict



#Takes takes raw ios data, checks the voltages against thresholds defined
#in the ios map, and adds any out of bounds voltages to an alarms dictionary
def checkThresholdAlarms(ios_data, ios_map, alarms):
    prev_alarms = alarms
    alarms = {}
    alarms_dict = {}
    lowvolt_list = [0,0,0,0,0,0,0,0,0,0,0,0]    #HARD-CODED; SNO+ HAS 11 racks+1 timing rack
    alarms_dict["timestamp"] = int(time.time())
    alarms_dict["sudbury_time"] = unix_to_human(int(time.time()))
    alarms_dict["DetectorServer_Conn"] = "OK"
    alarms_dict["IBoot3Power"] = "ON"
    alarms_dict["ios"] = ios
    for card_map in ios_map["cards"]:
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
	    #Build the lowvolt_list: increments a rack's # low voltages by 1 for each voltage below 1.5 volts
	    if chn_thresholds["type"] == "rack":
		if abs(chn_voltage) < 1.5 :    #FIXME : Make an entry in channeldb for each rack if we want full transparency of what these values are
		    racknum = int(chn_thresholds["id"])
		    lowvolt_list[racknum-1]+=1
	    elif chn_thresholds["type"] == "timing rack":
	        if abs(chn_voltage) < 1.5 :
		    racknum = 12
                    lowvolt_list[racknum-1]+=1
            #Check if an alarm is enabled, and label enabled alarms w/ threshold crossed
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
    #Now, disable rack alarms with all low voltages and indicated as "OFF" by ADAMS
    DisableOffRackAlarms(lowvolt_list, alarms_dict, cardsHW)
    return alarms, alarms_dict


##Function will take in the alarm_dict and search for alarms with the
##"action" type. A counter is added to the shutdown_dict that will power
##down a rack after 10 "action" alarm data points.
##After ten action alarms on any voltage, the ShutDownRack(racknum) function is ran for that rack.

def BuildCountTup():
	counters = [[1, "24V", 0],[1, "-24V", 0],[1, "8V", 0],[1, "5V",
	  0],[1, "-5V", 0],[2, "24V", 0],[2, "-24V", 0],[2, "8V", 0],[2,
	    "5V", 0],[2, "-5V", 0],[3, "24V", 0],[3, "-24V", 0],[3,
	      "8V", 0],[3, "5V", 0],[3, "-5V", 0],[4, "24V", 0],[4,
		"-24V", 0],[4, "8V", 0],[4, "5V", 0],[4, "-5V", 0],[5,
		  "24V", 0],[5, "-24V", 0],[5, "8V", 0],[5, "5V",
	  0],[5, "-5V", 0],[6, "24V", 0],[6, "-24V", 0],[6, "8V", 0],[6,
	    "5V", 0],[6, "-5V", 0],[7, "24V", 0],[7, "-24V", 0],[7,
	      "8V", 0],[7, "5V", 0],[7, "-5V", 0],[8, "24V", 0],[8,
		"-24V", 0],[8, "8V", 0],[8, "5V", 0],[8, "-5V", 0],[9,
		"24V", 0],[9, "-24V", 0],[9, "8V", 0],[9, "5V", 0],[9, "-5V", 0],[10,
		    "24V", 0],[10, "-24V", 0],[10, "8V", 0],[10,
	    "5V", 0],[10, "-5V", 0],[11, "24V", 0],[11, "-24V", 0],[11,
	      "8V", 0],[11, "5V", 0],[11, "-5V", 0],[12, "24V", 0],[12,
		"-24V", 0],[12, "6V", 0],[12, "5V", 0],[12, "-5V", 0]]
	return counters
	#FIXME THIS IS CLEARLY BAD; READ FROM IOS AND BUILD THIS LIST
	#CLEANLY LATER

def UpdateShutdownCounters(alarms_dict,counters, cardsHW):
  	if alarms_dict["DetectorServer_Conn"] == "OK" :
	  	card_list = list(cardsHW)
		action_dict = {}
		for x in range (1,13):
			action_dict[x] = []
		for card in card_list:
			for item in reversed(alarms_dict[card]):
				type = item["type"]
				id = item["id"]
				if type == "rack":
					if item["reason"]=="action":
						action_dict[id].append(item["signal"])
				if type == "timing rack":
					if item["reason"]=="action":
						action_dict[12].append(item["signal"])
						
		for racknum in action_dict:
		  	#increase counters on action items by one
			#REMINDER: Counter object format: (racknum, voltage, count)
			for c in counters:
				if c[0] == racknum:
			    		if c[1] in action_dict[racknum]:
						c[2]+=1	
						print("Counter initiated for rack " + str(c[0]) + ", voltage " + c[1] + " is currently at " + str(c[2]) + ". Rack panic down will commence when counter reaches 20. Rack shutdown commences when counter reaches 420.")
					elif c[1] not in action_dict[racknum]:
					  	c[2] = 0
		for c in counters:
			if c[0] < 12 and c[2] == 20 :
				Printout(str(alarms_dict["sudbury_time"]),c[0],c[1])
			elif c[0] < 12 and c[2] > 420 :
			  	Printoffout(str(alarms_dict["sudbury_time"]),c[0],c[1])
			  	c[2] = 0
			elif c[0] == 12 and c[2] == 20 :
		  		PrintTiming(str(alarms_dict["sudbury_time"]),c[1])
			elif c[0] == 12 and c[2] > 420 :
			  	PrintoffTiming(str(alarms_dict["sudbury_time"]),c[1])
				c[2] = 0
	return	

#>.>;;


def Printout(alarmtime,racknum,voltage):
	sendMail('At: ' + alarmtime + ': Rack panicdown would have fired (No actual shutdown initiated)', 'Rack ' + str(racknum) + 's panic down action would have activated')
	#print("DEBUGGING: Rack panicdown fired for rack " + str(racknum) + ", voltage " + voltage + ".")
	return

def PrintTiming(alarmtime,voltage):
	sendMail('At: ' + alarmtime +': Timing Rack panicdown would have fired (No actual shutdown initiated)','Timing rack panic down would have activated')
	#print("DEBUGGING: Rack panicdown fired for timing rack, voltage " + voltage +".")
	return

def Printoffout(alarmtime,racknum,voltage):
	sendMail('At:' + alarmtime + ': Rack shutdown would have fired (No actual shutdown initiated)', 'Rack ' + str(racknum) + 's full shutdown action would have activated')
	#print("DEBUGGING: Rack shutdown fired for rack " + str(racknum) + ", voltage " + voltage + ".")
	return

def PrintoffTiming(alarmtime,voltage):
	sendMail('At:' + alarmtime + ': Timing Rack shutdown would have fired (No actual shutdown initiated)','Timing rack shutdown down would have activated')
	#print("DEBUGGING: Rack shutdown fired for timing rack, voltage " + voltage +".")
	return


#Takes the current alarms and posts them to the Alarm Server.  Clears
#Items that are no longer alarming
def postAlarmServerAlarms(alarms_dict, alarms_last, cardsHW):
    """
    Takes the current alarms_dict for the IO server and posts
    the alarm's ID to the alarm server.  Also compares
     to the last alarms dictionary and clears resolved alarms.
    """
    if alarms_dict["DetectorServer_Conn"] == "NONE":
        post_alarm(30020)
    elif alarms_dict["DetectorServer_Conn"] == "OK" and alarms_last["DetectorServer_Conn"] == "NONE":
        clear_alarm(30020)
    nowalarming = []
    card_list = list(cardsHW)
    for card in card_list:
        for item in reversed(alarms_dict[card]):
            #First, determine what new alarms you have
            if (item["reason"] == "action") or (item["reason"] == "alarm"):
                nowalarming.append(item["alarmid"])
        #Now, clear out alarms that were alarming but are no longer alarming
        for item in reversed(alarms_last[card]):
	    if (item["reason"] == "action") or (item["reason"] == "alarm"):
                if item["alarmid"] not in nowalarming:
                    clear_alarm(item["alarmid"])
		#if item is old and still alarming, post alarm
		if item["alarmid"] in nowalarming:
		    post_alarm(item["alarmid"])

def getPastAlarms():
    """
    Pull the most recent alarms from the database.  Use these for initial
    posting/clearing of alarms from alarm server.
    """
    dbStatus, db = connectToDB("slowcontrol-alarms")
    if dbStatus is "ok":
        queryresults =  db.view("slowcontrol-alarms/recent"+str(ios),descending=True,limit=1)
        num_rows = queryresults.total_rows
        if num_rows>0:
            alarms_in_db = queryresults.rows[0].value
	else:
	    print("Could not get most recent alarms in DB.  Continuing..")
    else:
        print("could not connect to couchDB alarm database.")
	alarms_in_db = {}
    return alarms_in_db


def saveAlarms(alarms_dict,alarms_last):
    dbStatus, db = connectToDB("slowcontrol-alarms")
    if dbStatus is "ok":
        queryresults =  db.view("slowcontrol-alarms/recent"+str(ios),descending=True,limit=1)
        num_rows = queryresults.total_rows
        if num_rows>0:
            alarms_in_db = queryresults.rows[0].value
            match = 1
	    if (alarms_in_db["DetectorServer_Conn"] != alarms_dict["DetectorServer_Conn"] or alarms_in_db["IBoot3Power"] != alarms_dict["IBoot3Power"]):
                match = 0
            for card_map in ios_map["cards"]:
                card_name = card_map["card"]
                try:
                    if len(alarms_dict[card_name]) == len(alarms_in_db[card_name]):
                        for alarm_num in range(len(alarms_in_db[card_name])):
			    #First, check an alarm isn't already in the DB
                            if (alarms_dict[card_name][alarm_num]["channel"]!=alarms_in_db[card_name][alarm_num]["channel"] or 
                                alarms_dict[card_name][alarm_num]["reason"]!=alarms_in_db[card_name][alarm_num]["reason"]):
			        #For racks only, check if alarm has persisted
				if (alarms_dict[card_name][alarm_num]["type"] == "rack"):
                                    if (alarms_dict[card_name][alarm_num]["channel"]==alarms_last[card_name][alarm_num]["channel"] and
				        alarms_dict[card_name][alarm_num]["reason"]==alarms_last[card_name][alarm_num]["reason"]):
				        match = 0
				#For all others, want to save new alarm
				else:
				    match = 0
                    else:
                        match = 0
                except:
                    match = 0
            if match==0:
                db.save(alarms_dict)
                printAlarms(alarms_dict,alarms_last)
        else:
            db.save(alarms_dict)
            printAlarms(alarms_dict,alarms_last)


def printAlarms(alarms_dict,alarms_last):
    title = "IOS Alarms at " + str(alarms_dict["sudbury_time"]) + "\n\n"
    old_list = []
    new_list = []
    new_alarm_dict = {}
    for card_map in ios_map["cards"]:
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
        sendMail("Alarms at " + str(alarms_dict["sudbury_time"]), super_msg)
	#print("DEBUG MODE: " + super_msg)


def fill1min(alarms_dict):
    db5secStatus, db5sec = connectToDB("slowcontrol-data-5sec")
    db1minStatus, db1min = connectToDB("slowcontrol-data-1min")
    if db1minStatus is "ok":
        queryresults =  db1min.view("slowcontrol-channeldb/recent"+str(ios))
        numrows = queryresults.total_rows
        lastTimestamp = 0
        if numrows>0:
            lastTimestamp = queryresults.rows[numrows-1].key


# ioserver connection
conn_ioserver1 = httplib2.Http(".cache")

#Start IOS2 heartbeat for Alarm Server
post_heartbeat('SC_IOS2')

#grab current card configuration
cardsHW = checkCards()

#define initial dictionaries used for alarm tracking
alarms = {}
alarms_dict = {}
alarms_last = {}
shutdown_counters = BuildCountTup()

#First data collecting loop
ios_map = getChannelParameters()
ios_data = getChannelVoltages(ios_map, cardsHW)
saveVoltages(ios_data)
alarms_last = getPastAlarms()
alarms, alarms_dict = checkThresholdAlarms(ios_data, ios_map, alarms)
UpdateShutdownCounters(alarms_dict,shutdown_counters, cardsHW)
postAlarmServerAlarms(alarms_dict,alarms_last,cardsHW)
alarms_last = alarms_dict

while (1):
    time.sleep(period)

    ios_map = getChannelParameters()
    ios_data = getChannelVoltages(ios_map, cardsHW)
    saveVoltages(ios_data)
    alarms, alarms_dict = checkThresholdAlarms(ios_data, ios_map, alarms)
    UpdateShutdownCounters(alarms_dict,shutdown_counters, cardsHW)
    postAlarmServerAlarms(alarms_dict,alarms_last,cardsHW)
    saveAlarms(alarms_dict,alarms_last)
    alarms_last = alarms_dict

