This script is responsible for grabbing the temperature sensor data
that is stored in a log on Minard.  The data is processed, checked for
any temperatures out of alarming threshold in the channel database,
and then saved to couchDB.  Alarms are also posted to couchDB, as well
as the alarm GUI for shifters.
