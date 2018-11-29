import psycopg2
from psycopg2.pool import ThreadedConnectionPool
import threading
import thelogger as l
import config.config as c
import credentials as cr

ASUser, ASPassword = cr.getcreds(c.ALARMCREDDIR)
class AlarmPoster(object):
    def __init__(self, alarmhost=None, psql_database=None):
        self.host = alarmhost
        self.psql_db = psql_database
        self.heart_is_beating = False
        self.ASUser = None
        self.ASPassword = None
        self.pool = None
        self.logger = l.get_logger(__name__)

    def getAlarmDBCredentials(self,alarmcreddir=None):
        '''Given a filepath, return the username and password associated
        with the file'''
        if alarmcreddir is None:
            print("Please provide an alarm credentials file path")
            return
        self.ASUser, self.ASPassword = cr.getcreds(self.alarmcreddir)

    def startConnPool(self):
        '''Using the set host, database, and username/password, Start
        a connection pool for alarm posting'''
        self.logger.info("Starting connection pool for alarms database")
        self.pool = ThreadedConnectionPool(1,10, host=self.host, 
                database=self.psql_db, user=ASUser, password=ASPassword)

    def post_alarm(self,alarm_id):
        """
        Posts an alarm to the database for an alarm with a given id.
    
        Returns None if there was an error or the alarm was already active.
        If the alarm is successfully posted it returns the unique id of the
        alarm that was posted.
        """
    
        result = None
    
        try:
            conn = self.pool.getconn()
        except psycopg2.Error as e:
            #if the database is down we just print the error
            self.logger.exeption(str(e))
            print(str(e))     
        else:
            #we have a connection
            try:
                with conn:
                    with conn.cursor() as curs:
                        curs.execute("SELECT * FROM post_alarm(%i)" % alarm_id)
                        result = curs.fetchone()[0]
            except psycopg2.Error as e:
                #who knows what went wrong?  Just print the error
                self.logger.exception(str(e))
                print(str(e))
                #close the connection since it's possible the database
                #is down, so we don't want to use this connection again
                conn.close()
            
            self.pool.putconn(conn)
        return result
    
    def clear_alarm(self,alarm_id):
        """
        Clears an alarm from the alarm server for an alarm with a given id.
    
        Returns None if there was an error or the alarm was already active.
        If the alarm is successfully cleared it returns the unique id of the
        alarm that was cleared.
        """
    
        result = None
    
        try:
            conn = self.pool.getconn()
        except psycopg2.Error as e:
            #if the database is down we just print the error
            self.logger.exception(str(e))
        else:
            #we have a connection
            try:
                with conn:
                    with conn.cursor() as curs:
                        curs.execute("SELECT * FROM clear_alarm(%i)" % alarm_id)
                        result = curs.fetchone()[0]
            except psycopg2.Error as e:
                #who knows what went wrong?  Just print the error
                self.logger.exception(str(e))
                #close the connection since it's possible the database
                #is down, so we don't want to use this connection again
                conn.close()
            
            self.pool.putconn(conn)
        return result
    
    def post_heartbeat(self, name, beat_interval=10):
        """
        Recursive function that posts a heartbeat to the database every given seconds.
        Start this once when you run your main script.
        See stackoverflow.com/questions/3393612
        """
        if not self.heart_is_beating:
            self.logger.info("Starting alarm server connection heartbeat")
        try:
            conn = self.pool.getconn()
        except psycopg2.Error as e:
            #if the database is down we just print the error
            self.logger.exception(str(e))
        else:
            #we have a connection
            try:
                with conn:
                    with conn.cursor() as curs:
                        curs.execute("SELECT * FROM post_heartbeat('%s')" % name)
            except psycopg2.Error as e:
                #who knows what went wrong; just print the error
                self.logger.exeption(str(e))
                #close the connection since it's possible the database
                #is down, so we don't want to reuse this connection
                conn.close()
            self.pool.putconn(conn)
        
        t = threading.Timer(beat_interval, self.post_heartbeat, [name])
        t.daemon = True
        t.start()
        self.heart_is_beating = True
    
