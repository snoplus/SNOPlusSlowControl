#This script uses the Digital Temperature Sensor installed in Noel's
#Directory to read out the string of temperature sensors in the SNO+
#Cavity.  These values are then sent to the SNO+ couchDB where slow
#control data is saved.
#Written by: Teal Pershing
#Last Updated: 03/20/2017

import lib.dataio as dio
import lib.couchutils as cu
import lib.tempreader as tr
import lib.alarmposter as ap
import logging
import sys, traceback
import time

DEBUG = False
ERR_SLEEPTIME = 60
NONEWDATA_SLEEPTIME = 120
SUCCESS_SLEEPTIME = 360
TEMP_ALARMID = 30040
TEMPERATURE_LOGFILE = '/raid/CavityTemperature/temperature.log'


# --------- Logger configuration ----------- #
CLOG_FILENAME = '/home/uwslowcontrol/SNOPlusSlowControl/SNOPlusSlowControl/log/cavitytemp.log' #logfile source

logging.basicConfig(filename=CLOG_FILENAME,level=logging.INFO, \
    format='%(asctime)s %(message)s')

#Define what we want our system exception hook to do at an
#uncaught exception
def UE_handler(exec_type, value, tb):
    logging.exception("Uncaught exception: {0}".format(str(value)))
    logging.exception("Error type: " + str(exec_type))
    logging.exception("Traceback: " + str(traceback.format_tb(tb)))

#At an uncaught exception, run our handler
sys.excepthook = UE_handler
   
# --------- END Logger configuration -------- #

if __name__ == "__main__":
    numsensors = 30
    channeldb = None
    DATA_LABEL = "temp_sensors"
    channeldb = cu.getChannelParameters(channeldb)
    AlarmControl = ap.AlarmPoster(channeldb)
    AlarmControl.set_alarmid(TEMP_ALARMID)
    AlarmControl.set_datatype(DATA_LABEL)
    AlarmControl.set_sensorkey("Sensor")
    old_logread = None
    while True:
        #Update thresholds in case they were changed on webpage
        channeldb_last = channeldb
        channeldb = cu.getChannelParameters(channeldb_last)
        AlarmControl.setCurrentChanneldb(channeldb)

        #Get the current reading from the sensors
        #rawread = dio.getReading()
        #rawread = rawread.splitlines()

	#Or, read from a log file already being ouptut
        logread = dio.getFileTail(TEMPERATURE_LOGFILE,30)
        if old_logread is not None:
            if logread==old_logread:
                logging.info("No new data in file.  Try again in "+str(NONEWDATA_SLEEPTIME)+" sec.")
                time.sleep(NONEWDATA_SLEEPTIME)
                continue
        reader = tr.TempReader(logread)
        reader.set_dicttype(DATA_LABEL)
        reader.settime(int(time.time()))
        reader.setunit("(C)")
        reader.parseTemps()
        if DEBUG is True:
            reader.show()
        if reader.hasrawvalues == False:
            logging.info("No values grabbed from sensor. Sensor" + \
                " may have been polled by another source at this time.")
            time.sleep(ERR_SLEEPTIME)
            continue
        elif reader.parsed == False:
            #no values to parse, try again in a minute
            logging.info("No values parsed, trying again in 1 min.")
            time.sleep(ERR_SLEEPTIME)
            continue
        else:
            #values parsed. check for values outside threshold and alarm
            print(reader.readingdict)
            AlarmControl.updateCurrentValues(reader.readingdict)
            AlarmControl.checkForAlarms() #Posts alarms if any
            #dio.WriteReadToLog(reader)
            #save the dictionary to couchDB
            cu.saveValuesToCT(reader.readingdict)
            old_logread = logread
            time.sleep(SUCCESS_SLEEPTIME)

