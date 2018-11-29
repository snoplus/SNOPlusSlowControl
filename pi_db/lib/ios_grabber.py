import urllib2
from suds.client import Client
from suds.sudsobject import asdict

import timeconverts as tc
import thelogger as l

#LOTS TO DO HERE...

class IOSDataHandler(object):
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
        timeseries_client = None
        try:
            timeseries_client = Client(timeseries_url)
        except urllib2.URLError:
            self.logger.exception("Unable to connect to PI database.  Check status of pi_" +\
            "db at SNOLAB.")
            raise
        self.timeseries_client = timeseries_client
    
    
    #For each channel, reorganizes and stores values and timestamps in a dict
    def getValues(self,start_time,end_time,pi_list,getrecent_list):
        rawdata = pi_list
        for machine_index, machine in enumerate(pi_list):
            dbname = machine["dbname"]
            address = machine["address"]
            channel_numbers_list = machine["channels"]
            machine["data"] = []
            pi_list_item = pi_list[machine_index]
            if dbname in getrecent_list:
                for channel_number in channel_numbers_list:
                    machine["data"].append(self._get_pi_snapshot(pi_list_item,self.pi_address_base+address,channel_number))    
            else:
                for channel_number in channel_numbers_list:
                    machine["data"].append(self._get_pi(start_time,end_time,pi_list_item,self.pi_address_base+address,channel_number))    
        return rawdata
    
    #Takes rawdata and puts it in couchdb format
    def ManipulateData(self,start_time,end_time,rawdata,pi_list,getrecent_list,version):
        start_minute = tc.unix_minute(start_time)
        time_bins = tc.unix_minute(end_time)-start_minute
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
                              timestamp_minute = tc.unix_minute(tc.dmy_to_unix(timestep._Time))
                              timestamp = (timestamp_minute)*60
                              #print index, timestamp, timestep._Time
                              try:
                                  pi_data[0]["timestamp"] = timestamp
                                  pi_data[0]["sudbury_time"] = tc.unix_to_human(timestamp)
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

