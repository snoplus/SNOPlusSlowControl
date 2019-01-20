#Functions utilized to connect to the SNO+ alarm server.

import psycopg2 
from psycopg2.pool import ThreadedConnectionPool
import getcreds as gc

#connection info for alarm server
alarmUser, alarmPassword = gc.getcreds("/home/uwslowcontrol/config/alascred.conf")

pool = ThreadedConnectionPool(1,10, host='dbug.sp.snolab.ca', database='detector', user=alarmUser, password=alarmPassword)

def post_alarm(alarm_id):
    """
    Posts an alarm to the database for an alarm with a given id.

    Returns None if there was an error or the alarm was already active.
    If the alarm is successfully posted it returns the unique id of the
    alarm that was posted.
    """

    result = None

    try:
        conn = pool.getconn()
    except psycopg2.Error as e:
        #if the database is down we just print the error
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
            print(str(e))
            #close the connection since it's possible the database
            #is down, so we don't want to use this connection again
            conn.close()
        
        pool.putconn(conn)
    return result

def clear_alarm(alarm_id):
    """
    Clears an alarm to the database for an alarm with a given id.

    Returns None if there was an error or the alarm is already cleared.
    If the alarm is successfully cleared it returns the unique id of the
    alarm that was cleared.
    """

    result = None

    try:
        conn = pool.getconn()
    except psycopg2.Error as e:
        #if the database is down we just print the error
        print(str(e))
    else:
        #we have a connection
        try:
            with conn:
                with conn.cursor() as curs:
                    curs.execute("SELECT * FROM clear_alarm(%i)" % alarm_id)
                    result = curs.fetchone()[0]
        except psycopg2.Error as e:
            #who knows what went wrong?  Just print the error
            print(str(e))
            #close the connection since it's possible the database
            #is down, so we don't want to use this connection again
            conn.close()
        
        pool.putconn(conn)

    return result

