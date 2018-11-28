import config.config as c
import sys,logging
import traceback

#Set the logging information used in all other programs
LOG_FILENAME = c.LOG_FILENAME

def UE_handler(exec_type, value, tb):
    logging.exception("Uncaught exception: {0}".format(str(value)))
    logging.exception("Error type: " + str(exec_type))
    logging.exception("Traceback: " + str(traceback.format_tb(tb)))


def get_logger(name):
    log_format='%(asctime)s %(name)8s %(levelname)5s %(message)s'
    logging.basicConfig(filename=c.LOG_FILENAME,level=logging.INFO, 
            format=log_format,filemode='a')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(log_format))
    logging.getLogger(name).addHandler(console)
    return logging.getLogger(name)

