SNO+ Slow Control scripts for collecting and storing PI DB data
-------------------------------------------------------------------

The following is a copy of the important scripts used to monitor and store data from the PI_DB in CouchDB.  

/misclib/: directory with miscillaneous libraries that were installed for use
with the pi_db scripts.  Most other dependencies are common python libraries.

/bash_cronjobs/: bash scripts that can be paired with a cronjob to restart
crashed scripts.

The main operating script is pi_db.py.  The script pulls data from the PI DB every minute.  The script uses this data to send alarm notifications to the SNO+ Alarm Server database and Slow Control e-mail list.  The script then stores the alarms and pulled data in CouchDB for usage by the Slow Control interface.
