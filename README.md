SNO+ Slow Control scripts for collecting and storing PI DB and IOS data
-------------------------------------------------------------------

This repository contains all of the slow control scripts and libraries used by the IO servers
and Minard server to collect and store SNO+ detector data on a couch database.


/misclib/: directory with miscillaneous libraries that were installed for use
with the pi_db and ios scripts.  Most other dependencies are common python libraries.

/bash_cronjobs/: bash scripts that can be paired with a cronjob to restart
crashed scripts.

/tomb/: old stuff that is deprecated but I don't have the heart to remove.  

The main operating script is for Minard pi_db/main_pidb.py, which uses the database libraries
contained in lib/.  The same goes for the IO servers and pi_db/main_ios.py.  Names of relevant database URLs, settings for interval
time between polling, and other configurables loaded can be adjusted in
lib/config/config_pidb.py and config_ios.py.  

By default, the Minard script pulls data from the PI DB every minute, while the IOS script pulls data every 5 seconds.  

Both scripts use their collected data and an AlarmHandler class to post alarm notifications to the SNO+ Alarm Server database and Slow Control e-mail list.  The script then stores the alarms and pulled data in CouchDB for usage by the Slow Control interface.
