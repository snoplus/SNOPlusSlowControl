import urllib2
import httplib2
from suds.client import Client
from suds.sudsobject import asdict
import json
import time

import timeconverts as tc
import thelogger as l

#LOTS TO DO HERE...

class IOSDataHandler(object):
    '''This class contains methods for getting data from the IOS's local
    storage server and converting them into dictionary
     objects readily loaded into couchDB.'''
    def __init__(self):
        print("INITIALIZING IOS DATA HANDLER")
        self.logger = l.get_logger(__name__)
        self.CardInfoDir = None
        self.HWDict = None
        self.IOServerConn = None

    def connectToIOSServer(self):
        self.IOServerConn = httplib2.Http(".cache")

    def setIOSCardSpecs(self,hardwaredir):
        '''Opens the conf file located in the directory hardwaredir
        located on the IOS.  Returns a dictionary containing information
        on what I/O cards are currently installed in each slot on the IOS.'''
        self.CardInfoDir = hardwaredir
        f = open(hardwaredir, 'r')
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
        self.HWDict = cardDict
        return cardDict
    
    def _pollCard(self, card):
        status = "ok"
        result = {}
        if self.HWDict is None:
            self.logging.exception("You must load your IOS Hardware configuration before polling cards")
        if self.IOServerConn is None:
            self.logging.exception("You must initialize your connection to the IOS server that polls card info")
        if card in self.HWDict:
            try:
                resp,content = self.IOServerConn.request("http://127.0.0.1:8000/data/"+card,"GET")
            except:
                status = "bad"
                self.logger.exception("Error pulling data from IOS" + str(ios) + " card:" + card, file=sys.stderr)
            if status == "ok" and card in content:
                data = json.loads(content)
                result = data[card]
        else:
            self.logging.exception("Error: Attempted polling " + str(card) + " ioserver " + str(ios) + " but this is not listed on the ioserver " + str(self.CardInfoDir) + " file", file=sys.stderr)
        return result

    def getChannelVoltages(ios_map):
        timestamp = int(time.time())
        sudbury_time = unix_to_human(timestamp)
        ios_data = {'ios':ios, 'timestamp':timestamp, 'sudbury_time':sudbury_time}
        for card_map in ios_map["cards"]:
            card_name = card_map["card"]
            cardData = self._pollCard(card_name)
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
                        self.logging.info(msg) 
                    if (timestamp - value)>5:
                        msg = "Error: ioserver " + str(ios) + " " + card_name
                        msg = msg + " time (" + time.strftime("%a, %d %b %Y %H:%M:%S",time.localtime(value)) + ")"
                        msg = msg + "is more than 5 seconds behind the ioservers time (" + time.strftime("%a, %d %b %Y %H:%M:%S",time.localtime(timestamp)) + ")"
			self.logging.info(msg)
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
