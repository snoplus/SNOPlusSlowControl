SNO+ Slow Control scripts for collecting and storing PI DB and IOS data
-------------------------------------------------------------------

This repository contains all of the slow control scripts and libraries used by the IO servers
and Minard server to collect and store SNO+ detector data on a couch database.

######## QUICK INSTALL ONTO MINARD OR AN IOS #############

1. Pull this repository into the home directory on the new IOS or Minard.
2. Make a '/config/' directory in the home directory with the credentials
needed for accessing the slow control e-mail account, alarmdb, and couchdb.  File
contents have the form:

username type_the_username
password type_the_password

3. Enter the ~/SNOPlusSlowControl/SNOPlusSlowControl/lib/config directory and 
modify configurables as needed.  Likely, the only changes you need are to IOSNUM
and any changes to couchdb database or couchdb view names.

4. Install cronjob scripts found in /cronjobs/ on your IOS or Minard account.  These
will run regular checks to see if the slow control scripts have stopped working,
check the local memory and see if there's a risk of filling the drive, etc.

5. Start up the polling with the checkpi_db.sh  or checkPoll.sh bash scripts
found in the /cronjobs/ directory.

######## SUMMARY OF CONTENTS IN EACH DIRECTORY #########

/misclib/: directory with miscillaneous libraries that were installed for use
with the pi_db and ios scripts.  Most other dependencies are common python libraries.

/cronjobs/: bash scripts that can be paired with a cronjob to check
if things are running, and restart them if needed.  You will have
to change the home directory where SNOPlusSlowControl lives in each
of these scripts before using them on your machine.

/tomb/: old stuff that is deprecated but I don't have the heart to remove.  

The main operating scripts is for Minard pi_db/main_pidb.py, which uses the database libraries
contained in SNOPlusSlowControl/lib/.  The same goes for the IO servers and pi_db/main_ios.py.  Names of relevant database URLs, settings for interval
time between polling, and other configurables loaded are adjusted in
lib/config/config_pidb.py and lib/config/config_ios.py. 

/SNOPlusSlowcControl/DB/: Contains dictionaries that instruct main_pidb.py on
what type of data to poll from the PI server.  You will have to add new PI 
server addresses here to expand the data copied from the PI server to the 
SNO+ couch databases.

/util/: Additional scripts that have been developed for monitoring
other components of the SNO+ detector.  In principle, they could
be integrated to the other main scripts.

By default, the Minard script pulls data from the PI DB every minute, while the IOS script pulls data every 5 seconds.  

Both scripts use their collected data and an AlarmHandler class to post alarm notifications to the SNO+ Alarm Server database and Slow Control e-mail list.  The script then stores the alarms and pulled data in CouchDB for usage by the Slow Control interface.

---------------------------
Additional documentation
---------------------------

Slow Control User Guide: https://docs.google.com/document/d/1hlEcSa2YXPLuOA4fwPkK-HFUppobehNU5efvKk64kz0/edit?usp=sharing

SNO+ monitoring and control couchapp webpage: couch.snopl.us/slowcontrol-channeldb/_design/slowcontrol/_show/alarms/
