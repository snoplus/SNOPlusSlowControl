SNO+ Slow Control scripts for collecting and storing PI DB and IOS data
-------------------------------------------------------------------

This repository contains all of the slow control scripts and libraries used by the IO servers
and Minard server to collect and store SNO+ detector data on a couch database.


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

/util/: Additional scripts that have been developed for monitoring
other components of the SNO+ detector.  In principle, they could
be integrated to the other main scripts.

By default, the Minard script pulls data from the PI DB every minute, while the IOS script pulls data every 5 seconds.  

Both scripts use their collected data and an AlarmHandler class to post alarm notifications to the SNO+ Alarm Server database and Slow Control e-mail list.  The script then stores the alarms and pulled data in CouchDB for usage by the Slow Control interface.
