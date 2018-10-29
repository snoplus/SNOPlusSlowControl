import config.config as c
import sys,logging

#Set the logging information used in all other programs
LOG_FILENAME = c.LOG_FILENAME

def get_logger(name):
    logformat='%(asctime)s %(name)8s %(levelname)5s %(message)s')
    logging.basicConfig(filename=c.LOG_FILENAME,level=logging.INFO, 
            format=logformat,filemode='w')
    console = logging.StreamHandler()
    consel.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(log_format))
    logging.getLogger(name).addHandler(console)
    return logging.getLogger(name)

