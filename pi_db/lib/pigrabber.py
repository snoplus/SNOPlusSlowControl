import urllib2
from suds.client import Client
from suds.sudsobject import asdict

#PI database information
#TODO: think these are only used in getting the PI DB information.
#Let's make a class for this.  Inputs will be:
#  - the pi_list
#  - The timeseries_url; have it put in in a method
#  - Method that connects the timeseries client

timeseries_url = c.timeseries_url
try:
    timeseries_client = Client(timeseries_url)
except urllib2.URLError:
    logging.info("Unable to connect to PI database.  Check status of pi_" +\
    "db at SNOLAB.")
    raise

piarcdatarequest = timeseries_client.factory.create('PIArcDataRequest')


#For a channel, gets the most recent datapoint from the database 
def get_pi_snapshot(machine_index,address,channel_number):
    method = pi_list[machine_index]["method"]
    if method==1:
        thepath = address
    if method==2:
        thepath = address % (channel_number)
    if method==3:
        thepath = address % (pi_list[machine_index]["appendage"][channel_number-1])
    requests = timeseries_client.factory.create('ArrayOfString')
    requests.string.append(str(thepath))
    try:
        returned_arcdata = timeseries_client.service.GetPISnapshotData(requests)                                                
    except:
        logging.exception("Issue Querying PI Server.  In except loop, trying again..")
        returned_arcdata = timeseries_client.service.GetPISnapshotData(requests)                                                
    return returned_arcdata

#For a channel, gets values and timestamps from start_time to end_time 
def get_pi(start_time,end_time,machine_index,address,channel_number):
    piarcdatarequest.TimeRange.Start = start_time
    piarcdatarequest.TimeRange.End = end_time
    piarcdatarequest.PIArcManner._NumValues = '6000'
    method = pi_list[machine_index]["method"]
    if method==1:
        piarcdatarequest.Path = address
    if method==2:
        piarcdatarequest.Path = address % (channel_number)
    if method==3:
        piarcdatarequest.Path = address % (pi_list[machine_index]["appendage"][channel_number-1])
    requests = timeseries_client.factory.create('ArrayOfPIArcDataRequest')
    requests.PIArcDataRequest = [piarcdatarequest]
    try:
        returned_arcdata = timeseries_client.service.GetPIArchiveData(requests)                                                
    except:
        logging.exception("Issue querying PI server.  In except loop, trying again..")
        returned_arcdata = timeseries_client.service.GetPIArchiveData(requests)                                                
    return returned_arcdata


#For each channel, reorganizes and stores values and timestamps in a dict
def getValues(start_time,end_time,pi_list):
    rawdata = pi_list
    for machine_index, machine in enumerate(pi_list):
        dbname = machine["dbname"]
        address = machine["address"]
        channel_numbers_list = machine["channels"]
        machine["data"] = []
        if dbname in getrecent_list:
            for channel_number in channel_numbers_list:
                machine["data"].append(get_pi_snapshot(machine_index,pi_address+address,channel_number))    
        else:
            for channel_number in channel_numbers_list:
                machine["data"].append(get_pi(start_time,end_time,machine_index,pi_address+address,channel_number))    
    return rawdata

#Takes rawdata and puts it in couchdb format
def ManipulateData(start_time,end_time,rawdata):
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
                              logging.info("There was an issue getting a channel value for: " + \
                                     str(pi_list[readtype_index]["dbname"]) +  ".  Leaving as N/A")
    return pi_data

