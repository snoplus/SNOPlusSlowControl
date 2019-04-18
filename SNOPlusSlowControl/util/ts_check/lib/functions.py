from __future__ import print_function
import couchdb
import sys
import string, calendar, time, urllib2, base64
import lib.config.tsconfig as c
import lib.alarm_server as als
import lib.getcreds as gc
import lib.emailsend as es
import TimestampComparer as ts

from email import utils
import logging

def getCavityTempsDocAge(LatestEntry):
    comparer = ts.TimestampComparer(LatestEntry)
    return comparer.compare()
def getIOSDocAge(IOSnum,LatestEntry):
    comparer = ts.TimestampComparer(LatestEntry)
    return comparer.compare()

def getDeltaVDocAge(LatestEntry):
    #poll the DeltaV database and check the   timestamp
    dvcomparer = ts.TimestampComparer(LatestEntry)
    return dvcomparer.compare()

