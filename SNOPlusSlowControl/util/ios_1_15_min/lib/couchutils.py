from __future__ import print_function
import credentials as cr
import couchdb
import sys

#Connects to db
def connectToDB(couchServer, dbName):
    status = "ok"
    db = {}
    try:
        db = couchServer[dbName]
    except:
        print("Failed to connect to " + dbName, file=sys.stderr)  
        status = "bad"
    return status, db

def get_latest_time(timetype,ios,couchServer):
    if timetype=="onemin":
        db1minStatus, db1min = connectToDB(couchServer,"slowcontrol-data-1min")
        if db1minStatus is "ok":
            queryresults =  db1min.view("slowcontrol-data-1min/recent"+str(ios),descending=True,limit=1)
    elif timetype=="fifteenmin":
        db1minStatus, db1min = connectToDB(couchServer,"slowcontrol-data-15min")
        if db1minStatus is "ok":
            queryresults =  db1min.view("slowcontrol-data-15min/recent"+str(ios),descending=True,limit=1)
    elif timetype=="fivesec":
        db5secStatus, db5sec = connectToDB(couchServer,"slowcontrol-data-5sec")
        if db5secStatus is "ok":
            queryresults =  db5sec.view("slowcontrol-data-5sec/recent"+str(ios),descending=True,limit=1)
    try:
        latest_time = queryresults.rows[0].value["timestamp"]
    except:
        print("LATEST TIME NOT AVAILABLE FOR DB " + timetype + "RETURNING"+\
	    " MINUS ONE")
	latest_time = -1
    return latest_time

#Gets all documents with timestamp that lie within minute after latest_1min_time
def getDocuments(latest_time,time_interval,ios,couchServer):
    next_time = latest_time + time_interval
    db5secStatus, db5sec = connectToDB(couchServer,"slowcontrol-data-5sec")
    if db5secStatus is "ok":
        queryresults = db5sec.view("slowcontrol-data-5sec/recent"+str(ios), startkey=next_time, endkey=next_time + time_interval - 1, ascending=True)
    documents = []
    for doc in queryresults.rows:
        documents.append(doc.value)
    return documents

#Saves the summary document to the 1min  or 15min db
def saveVoltages(ios_data,mintype,couchServer):
    if mintype=="onemin":
        dbDataStatus, dbData = connectToDB(couchServer,"slowcontrol-data-1min")
        if dbDataStatus is "ok":
            dbData.save(ios_data)
    elif mintype=="fifteenmin":
        dbDataStatus, dbData = connectToDB(couchServer,"slowcontrol-data-15min")
        if dbDataStatus is "ok":
            dbData.save(ios_data)

