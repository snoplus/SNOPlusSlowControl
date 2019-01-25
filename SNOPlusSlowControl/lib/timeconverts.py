from email import utils
import datetime, time, calendar, math, re

#Finds the "minute" of a Unix timestamp                                  
def unix_minute(unix_time):
    unix_minute = int(math.floor(unix_time/60.))
    return unix_minute


#Converts unix timestamp to human readable local time (Sudbury time)
def unix_to_human(unix_time):
    human_time = utils.formatdate(unix_time, localtime=True)
    return human_time


# Converts UTC-5 date-time to unix timestamp
def dmy_to_unix(dmy_time):
    unix_time = "%s" % dmy_time
    unix_time = unix_time[0:18]
    unix_time = int(calendar.timegm(time.strptime(unix_time, '%Y-%m-%d %H:%M:%S')))
    return unix_time


#Converts unix timestamp to UTC-5 date-time
def unix_to_dmy(unix_time):
    dmy_time = datetime.datetime.utcfromtimestamp(unix_time)
    return dmy_time

