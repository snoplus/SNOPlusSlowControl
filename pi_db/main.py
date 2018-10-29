#!/usr/bin/env python
#Original scripts by: Luke Kippenbrock on 23 April 2015
#Alarm server features by: Teal Pershing, 28 July 2016
#Restructured into classes/libraries by: Teal Pershing, 28 Oct 2018

import datetime, time, calendar, math, re
import sys,logging, pprint
import socket
import traceback
import couchdb
import smtplib
import mimetypes
import urllib2
import httplib

import lib.config.config as c
import lib.credentials as cr
from lib.log import *
import channelDB.pilist as pl

#Define what we want our system exception hook to do at an
#uncaught exception
def UE_handler(exec_type, value, tb):
    logging.exception("Uncaught exception: {0}".format(str(value)))
    logging.exception("Error type: " + str(exec_type))
    logging.exception("Traceback: " + str(traceback.format_tb(tb)))

#At an uncaught exception, run our handler
sys.excepthook = UE_handler



ALARMCREDDIR = c.ALARMCREDDIR
ALARMHOST = c.ALARMHOST
ALARMDBNAME = c.ALARMDBNAME 

PILIST = pl.pi_list
GETRECENTLIST = pl.getrecent_list

#Connection info for couchdb
couch = couchdb.Server('http://couch.snopl.us')
couchuser, couchpassword = getcreds("/home/uwslowcontrol/config/couchcred.conf")
couch.resource.credentials = (couchuser, couchpassword)
couch.resource.session.timeout = 15


piarcdatarequest = timeseries_client.factory.create('PIArcDataRequest')

logger = get_logger(__name__)
logger.info('PI_DB SCRIPT INITIALIZING...')

#Define what we want our system exception hook to do at an
#uncaught exception
#FIXME: Can we clean this up/pull it out of main?
def UE_handler(exec_type, value, tb):
    logger.exception("Uncaught exception: {0}".format(str(value)))
    logger.exception("Error type: " + str(exec_type))
    logger.exception("Traceback: " + str(traceback.format_tb(tb)))

#At an uncaught exception, run our handler
sys.excepthook = UE_handler

if __name__ == '__main__':
    #A lot to do here.  Need to initialize the couchdb classes,
    #Alarm handlers, and everything.  Then, jump into a while True to
    #go on forever
    while True:
        saveValues(pi_data,c.ONEMINDBURL) #Will be from a couchutil instance

