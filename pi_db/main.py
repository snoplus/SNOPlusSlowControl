#!/usr/bin/env python
#Original scripts by: Luke Kippenbrock on 23 April 2015
#Alarm server features by: Teal Pershing, 28 July 2016
#Restructured into classes/libraries by: Teal Pershing, 28 Oct 2018

from suds.client import Client
from suds.sudsobject import asdict
import datetime, time, calendar, math, re
import sys,logging, pprint
import socket
import traceback
import couchdb
import smtplib
import mimetypes
import urllib2
import httplib

import lib.credentials as cr
import channelDB.pilist as pl


LOG_FILENAME = '/home/uwslowcontrol/pi_db/log/pilog.log' #logfile source

ALARMCREDDIR = "/home/uwslowcontrol/config/alascred.conf"
ALARMHOST = "dbug"
ALARMDBNAME = "detector"

PILIST = pl.pi_list
GETRECENTLIST = pl.getrecent_list

#Connection info for couchdb
couch = couchdb.Server('http://couch.snopl.us')
couchuser, couchpassword = getcreds("/home/uwslowcontrol/config/couchcred.conf")
couch.resource.credentials = (couchuser, couchpassword)
couch.resource.session.timeout = 15

#PI database information
#TODO: think these are only used in getting the PI DB information.
#Let's make a class for this.
timeseries_url = 'http://pi.snolab.ca/PIWebServices/PITimeSeries.svc?wsdl'
try:
    timeseries_client = Client(timeseries_url)
except urllib2.URLError:
    logging.info("Unable to connect to PI database.  Check status of pi_" +\
    "db at SNOLAB.")
    raise

piarcdatarequest = timeseries_client.factory.create('PIArcDataRequest')


