from __future__ import print_function
import couchdb
import sys
import string, calendar, time, urllib2, base64
import lib.config.tsconfig as c
import lib.alarm_server as als
import lib.getcreds as gc
import lib.emailsend as es
import lib.couchutils

from email import utils
import logging





class TimestampComparer(object):
    def __init__(self, doc):
        self.doc = doc
        self.timestamp = int(self.doc["timestamp"])
        self.couchUGtime = 'none'
        self.getcouchUGTime()

    def compare(self):
        if (self.couchUGtime == 'unknown') or (self.timestamp == 'unknown'):
            logging.warning("ERROR GETTING EITHER THE DOC TIMESTAMP OR" + \
                " SERVER TIME FROM COUCH.UG. CHECK COUCH.UG STATUS.")
            return 'unknown'
        else:
            try:
                result = self.couchUGtime - self.timestamp
                return result
            except(TypeError):
                logging.warning("TIMESTAMP AND COUCH TIME ARE NOT BOTH " + \
                    "INTEGERS.  RETURNING UNKNOWN.")
                return 'unknown'


    def getcouchUGTime(self):
        url = 'http://couch.ug.snopl.us'
        try:
            req = urllib2.Request(url)
            base64string = base64.b64encode("%s:%s" % \
                (snopluscouchuser, snopluscouchpw)).replace('\n', '')
            req.add_header("Authorization", "Basic %s" % base64string)
            ping = urllib2.urlopen(req)
            couchdate = ping.headers.dict['date']
            #convert to unix time
            pattern = str("%a, %d %b %Y %H:%M:%S %Z")
            unixcouchtime = int(calendar.timegm(time.strptime(couchdate, pattern)))
            self.couchUGtime = unixcouchtime
        except:
            logging.warning("ERROR GETTING CURRENT COUCH.UG TIME." + \
                "TIME IS UNKNOWN.")
            self.couchUGtime = 'unknown'



