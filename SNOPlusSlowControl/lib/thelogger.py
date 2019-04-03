import config.logconfig as lc
import sys,logging
import traceback

def UE_handler(exec_type, value, tb):
    logging.exception("Uncaught exception: {0}".format(str(value)))
    logging.exception("Error type: " + str(exec_type))
    logging.exception("Traceback: " + str(traceback.format_tb(tb)))


def get_logger(name):
    logging.basicConfig(filename=lc.LOG_FILENAME,level=lc.LOG_LEVEL, 
            format=lc.LOG_FORMAT,filemode='a')
    console = logging.StreamHandler()
    console.setLevel(lc.LOG_LEVEL)
    console.setFormatter(logging.Formatter(lc.LOG_FORMAT))
    logging.getLogger(name).addHandler(console)
    return logging.getLogger(name)

