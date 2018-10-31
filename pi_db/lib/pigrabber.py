import urllib2
from suds.client import Client
from suds.sudsobject import asdict

#PI database information
#TODO: think these are only used in getting the PI DB information.
#Let's make a class for this.  Inputs will be:
#  - the pi_list
#  - The timeseries_url; have it put in in a method
#  - Method that connects the timeseries client
import logging as l
#FIXME: logging additions

class PIDataHandler(object):
    '''This class contains methods for getting data from SNOLAB's pi database and
    converting it into dictionary objects readily loaded into couchDB.'''
    def __init__(self):
        print("BEGIN THE INIT")
        self.logger = l.get_logger(__name__)
        self.timeseries_client = None
        self.piarcdatarequest = None

    def CreateClientConnection(self,timeseries_url,factory_name):
        '''Given a URL, initializes a timeseries client for requesting data from
        the server connected.'''
    try:
        timeseries_client = Client(timeseries_url)
    except urllib2.URLError:
        self.logger.exception("Unable to connect to PI database.  Check status of pi_" +\
        "db at SNOLAB.")
        raise
    self.timeseries_client = timeseries_client
    
    def OpenPIDataRequest(self):
        '''Opens a timeseries_client factory used to grab each components data
        from the PI database'''
        self.piarcdatarequest = timeseries_client.factory.create('PIArcDataRequest')

    #FIXME: Need to add in those selfs to items defined in the class.
    #For a channel, gets the most recent datapoint from the database 
    def _get_pi_snapshot(self,pi_list_item,item_address,channel_number):
        '''given a pi_list_item and it's address in the SNOLAB PI server, return
        the most recent datapoint from the PI database for the item'''
        if self.timeseries_client is None or self.piarcdatarequest is None:
            print("You must first create your client connection and open a PI Data Request")
            return
        method = pi_list_item["method"]
        if method==1:
            thepath = item_address
        if method==2:
            thepath = item_address % (channel_number)
        if method==3:
            thepath = item_address % (pi_list_item["appendage"][channel_number-1])
        requests = self.timeseries_client.factory.create('ArrayOfString')
        requests.string.append(str(thepath))
        try:
            returned_arcdata = self.timeseries_client.service.GetPISnapshotData(requests)                                                
        except:
            self.logger.exception("Issue Querying PI Server.  In except loop, trying again..")
            returned_arcdata = self.timeseries_client.service.GetPISnapshotData(requests)                                                
        return returned_arcdata
    
    #For a channel, gets values and timestamps from start_time to end_time 
    def _get_pi(start_time,end_time,pi_list_item,item_address,channel_number):
        '''for a given pi_list item and it's address on the SNOLAB PI server,
        return the values and timestamps available in the given time window'''
        if self.timeseries_client is None or self.piarcdatarequest is None:
            print("You must first create your client connection and open a PI Data Request")
            return
        self.piarcdatarequest.TimeRange.Start = start_time
        self.piarcdatarequest.TimeRange.End = end_time
        self.piarcdatarequest.PIArcManner._NumValues = '6000'
        method = pi_list_item["method"]
        if method==1:
            self.piarcdatarequest.Path = item_address
        if method==2:
            self.piarcdatarequest.Path = item_address % (channel_number)
        if method==3:
            self.piarcdatarequest.Path = item_address % (pi_list_item["appendage"][channel_number-1])
        requests = self.timeseries_client.factory.create('ArrayOfPIArcDataRequest')
        requests.PIArcDataRequest = [self.piarcdatarequest]
        try:
            returned_arcdata = self.timeseries_client.service.GetPIArchiveData(requests)                                                
        except:
            self.logger.exception("Issue querying PI server.  In except loop, trying again..")
            returned_arcdata = self.timeseries_client.service.GetPIArchiveData(requests)                                                
        return returned_arcdata
    
    
    #For each channel, reorganizes and stores values and timestamps in a dict
    def getValues(start_time,end_time,pi_list):
        rawdata = pi_list
        for machine_index, machine in enumerate(pi_list):
            dbname = machine["dbname"]
            address = machine["address"]
            channel_numbers_list = machine["channels"]
            machine["data"] = []
            pi_list_item = pi_list[machine_index]
            if dbname in getrecent_list:
                for channel_number in channel_numbers_list:
                    machine["data"].append(self._get_pi_snapshot(pi_list_item,pi_address+address,channel_number))    
            else:
                for channel_number in channel_numbers_list:
                    machine["data"].append(self._get_pi(start_time,end_time,pi_list_item,pi_address+address,channel_number))    
        return rawdata
    
    #Takes rawdata and puts it in couchdb format
    def ManipulateData(start_time,end_time,rawdata,pi_list):
        start_minute = unix_minute(start_time)
        time_bins = unix_minute(end_time)-start_minute
        pi_data = []
        data_format = {"timestamp":"N/A","sudbury_time":"N/A","version":version,"pi_db":"true"}
        for machine in pi_list:
            data_format[machine["dbname"]] = {"values":["N/A"]*len(machine["channels"])}
        pi_data.append(data_format)
        for readtype_index, readtype in enumerate(rawdata):
            for reading_num, read_data in enumerate(readtype["data"]):
                realdata = read_data.TimeSeries[0]
                if realdata.TimedValues != None:
                     for timestep in realdata.TimedValues[0]:
                          #This if makes setting the timestamp of the document specific to
                          #Datapoints that don't just grab the most recent point in a database
                          #It's silly to set the timestamp at every entry, but I'll leave it 
                          if pi_list[readtype_index]["dbname"] not in getrecent_list:
                              timestamp_minute = unix_minute(dmy_to_unix(timestep._Time))
                              timestamp = (timestamp_minute)*60
                              #print index, timestamp, timestep._Time
                              try:
                                  pi_data[0]["timestamp"] = timestamp
                                  pi_data[0]["sudbury_time"] = unix_to_human(timestamp)
                              except:
                                  pass
                          try:
                              chan_value = timestep.value
                              chan_value = str(chan_value.__repr__())   
                              try: 
                                  val = float(chan_value)
                              except ValueError:
                                  val = chan_value
                                  pass
                              pi_data[0][pi_list[readtype_index]["dbname"]]["values"][reading_num] = val
                          except:
                              #FIXME: One of the cover gas lines is disabled. floods log
                              if str(pi_list[readtype_index]["dbname"]) != "cover_gas":
                                  self.logger.info("There was an issue getting a channel value for: " + \
                                         str(pi_list[readtype_index]["dbname"]) +  ".  Leaving as N/A")
        return pi_data

