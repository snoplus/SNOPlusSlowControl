from __future__ import print_function
import couchdb
import sys
import string, calendar, time, urllib2, base64
import lib.config.tsconfig as c
import lib.alarm_server as als
import lib.getcreds as gc
import lib.emailsend as es

from email import utils
import logging


def cavityTempsDocAge():
    status, db = connectToDB('slowcontrol-data-cavitytemps')
    if status=="ok":
        queryresult = db.view('slowcontrol-data-cavitytemps/by_timestamp', \
            descending=True, limit=1)
        recentdoc = queryresult.rows[0].value
        comparer = TimestampComparer(recentdoc)
        return comparer.compare()
    else:
        return 'unknown'

def getIOSDocAge(IOSnum):
    status, db = connectToDB('slowcontrol-data-5sec')
    if status=="ok":
        queryresult = db.view('slowcontrol-data-5sec/recent' + str(IOSnum), \
            descending=True, limit=1)
        recentdoc = queryresult.rows[0].value
        comparer = TimestampComparer(recentdoc)
        return comparer.compare()
    else:
        return 'unknown'

def getDeltaVDocAge():
    #poll the DeltaV database and check the timestamp
    dvstatus, dvdb = connectToDB('slowcontrol-data-1min')
    if dvstatus=='ok':
        dvqueryresult = dvdb.view('slowcontrol-data-1min/pi_db', \
            descending=True, limit=1)
        dvrecentdoc = dvqueryresult.rows[0].value
        dvcomparer = TimestampComparer(dvrecentdoc)
        return dvcomparer.compare()
    else:
        return 'unknown'



