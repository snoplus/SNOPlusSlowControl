#Class for controlling the racks on deck
import mail as m

class RackController(object):
    '''This class contains methods for getting data from, and sending
    commands to, the ADAM for rack monitoring/control.'''
    def __init__(self,detserverhost,detserverport):
        print("INITIALIZING RACK CONTROLLER/MANAGER")
        self.logger = l.get_logger(__name__)
        self.hostdns = detserverhost
        self.hostport = detserverport
	self.counters = self._initCounters()

    def setHostDNS(self,dns):
        '''Set the host IP/DNS that is used in any connection made'''
        self.hostdns = dns

    def setHostPort(self,port):
        '''Set the host IP/DNS that is used in any connection made'''
        self.hostport = port

    def _connectToDetServer(self):
        status = "ok"
        DSsocket=redis.Connection(host=self.hostdns, port=self.hostport, socket_connect_timeout=15.0, retry_on_timeout=True)
        try:
          	DSsocket._connect()
    	DSsocket.on_connect()
        except:
            print("Failed to connect to Detector Server", file=sys.stderr)
    	status = "bad"
        return status, DSsocket

    def ShutDownRack(self,racknum):
        #Sends the command to the detector server to shut down the given rack number
        status, sock=self._connectToDetServer()
        if status == "ok":
    	#Now try sending the shutdown command, with the rack number passed in.  We only try again if
    	#we get a response error, which is associated with timeouts.
    	while True:
    		try:
    			sock.send_command("PowerOffRacks "+str(racknum))
    			reply=sock.read_response()
    		except redis.ResponseError:
    			self.logging.info("ShutDownRack in RackController: Recieved a response error.  May be a timeout issue. Sleeping 1 sec, Trying again...")
    			time.sleep(5)
    			continue
    		break
    	if reply == "OK":
    		self.logging.info("RackController: RACK NO. "+str(racknum)+" HAS BEEN POWERED DOWN.")
    	else:
    		self.logging.info("RackController: Reply from rack was not OK.  Shutdown may have failed.")
    	sock.disconnect()
        return

    def ShutDownTimingRack(self):
        status, sock=self._connectToDetServer()
        if status == "ok":
    	#Now try sending the shutdown command for the timing rack.  We only try again if
    	#we get a response error, which is associated with timeouts.
    	while True:
    		try:
    			sock.send_command("PowerOffTimingRack")
    			reply=sock.read_response()
    		except redis.ResponseError:
    			self.logging.info("ShutDownTimingRack in RackController: Recieved a response error.  May be a timeout issue. Sleeping 1 sec, Trying again...")
    			time.sleep(8)
    			continue
    		break
    	if reply == "OK":
    		self.logging.info("RackController: THE TIMING RACK HAS BEEN POWERED DOWN.")
    	else:
    		self.logging.info("RackController: Reply from rack was not OK.  Shutdown may have failed.")
    	sock.disconnect()
        return

	def GetPoweredRacks(self):
		'''Find out what SNO racks are on.  Returns a 16 bit binary string,
		 1's indicate powered racks. Racks 1-6 are in the first 8 bits, 
		racks 7-11 and the timing rack are in bits 8-13 on last 8 bits.'''

		counter=0
		while True:
			status, sock=self._connectToDetServer()
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

	###Begin functions for counting down to rack shutdowns###
	def _initCounters(self):
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
	
	def UpdateShutdownCounters(self, alarms_dict, cardsHW):
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
				for c in self.counters:
					if c[0] == racknum:
				    		if c[1] in action_dict[racknum]:
							c[2]+=1	
							print("Counter initiated for rack " + str(c[0]) + ", voltage " + c[1] + " is currently at " + str(c[2]) + ". Rack panic down will commence when counter reaches 20. Rack shutdown commences when counter reaches 420.")
						elif c[1] not in action_dict[racknum]:
						  	c[2] = 0
			
	def initiateShutdownMessages(self,warning_time=20, action_time=420,reccipients):
		'''Based on current count time for a rack having an alarming voltage,
                send warning notifications for an upcoming shutdown, and send a message
                indicating a real shutdown would have occured'''
		for c in self.counters:
			if c[0] < 12 and c[2] == warning_time :
				self._printout(str(alarms_dict["sudbury_time"]),c[0],c[1],recipients)
			elif c[0] < 12 and c[2] > action_time :
			  	self._printOffout(str(alarms_dict["sudbury_time"]),c[0],c[1],recipients)
			  	c[2] = 0
			elif c[0] == 12 and c[2] == warning_time :
		  		self._printTiming(str(alarms_dict["sudbury_time"]),c[1],recipients)
			elif c[0] == 12 and c[2] > action_time :
			  	self._printOffTiming(str(alarms_dict["sudbury_time"]),c[1],recipients)
				c[2] = 0
		return	
	def _printout(self.alarmtime,racknum,voltage,recipients_list):
		msg = 'At: ' + alarmtime + ': Rack panicdown would have fired (No actual shutdown initiated)'
		title =  'Rack ' + str(racknum) + 's panic down action would have activated'
		m.sendMail(msg, title,recipients_list)
		self.logging.info("RackController: " + msg + title)
		return
	
	def _printTiming(self,alarmtime,voltage,recipients_list):
		msg = 'At: ' + alarmtime +': Timing Rack panicdown would have fired (No actual shutdown initiated)'
		title = 'Timing rack panic down would have activated'
		m.sendMail(msg, title,recipients_list)
		self.logging.info("RackController: " + msg + title)
		return
	
	def _printOffout(self,alarmtime,racknum,voltage,recipients_list):
		msg = 'At:' + alarmtime + ': Rack shutdown would have fired (No actual shutdown initiated)'
		title =  'Rack ' + str(racknum) + 's full shutdown action would have activated'
		m.sendMail(msg, title,recipients_list)
		self.logging.info("RackController: " + msg + title)
		return
	
	def _printOffTiming(self,alarmtime,voltage,recipients_list):
		msg =   'At:' + alarmtime + ': Timing Rack shutdown would have fired (No actual shutdown initiated)'
		title = 'Timing rack shutdown down would have activated' 
		m.sendMail(msg,title,recipients_list)
		self.logging.info("RackController: " + msg + title)
		return
	
