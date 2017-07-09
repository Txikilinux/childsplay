# provides a logging object
# All modules get the same logger so this must called asap

### example "application" code to use in your module
##import logging
##module_logger = logging.getLogger("schoolsplay.<name of your module>")
##logger.debug("debug message")
##logger.info("info message")
##logger.warn("warn message")
##logger.error("error message")
##logger.critical("critical message")
##logger.exception("exception message")

import os
from SPConstants import HOMEDIR
LOGPATH = os.path.join(HOMEDIR, "schoolsplay.log")
# remove old log
if os.path.exists(LOGPATH):
    try:
        os.remove(LOGPATH)
    except Exception, info:
        print "Failed to remove old log"
        print info
    else:
        print "removed old logpath"
        
# set loglevel, possible values:
# logging.DEBUG
# logging.INFO
# logging.WARNING
# logging.ERROR
# logging.CRITICAL
import logging, logging.handlers

def set_level(level):
    global CONSOLELOGLEVEL, FILELOGLEVEL
    lleveldict = {'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'critical':logging.CRITICAL}
    if not lleveldict.has_key(level):
        print "Invalid loglevel: %s, setting loglevel to 'debug'" % level
        llevel = lleveldict['debug']
    else:
        llevel = lleveldict[level]
    CONSOLELOGLEVEL = llevel
    FILELOGLEVEL = llevel

def start():
    global CONSOLELOGLEVEL, FILELOGLEVEL
    #create logger
    logger = logging.getLogger("schoolsplay")
    logger.setLevel(CONSOLELOGLEVEL)
    #create console handler and set level
    ch = logging.StreamHandler()
    ch.setLevel(CONSOLELOGLEVEL)
    #create file handler and set level
    fh = logging.FileHandler(LOGPATH)
    fh.setLevel(FILELOGLEVEL)
    #create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    #add formatter to ch and fh
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    #add ch and fh to logger
    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.info("File logger created: %s" % LOGPATH)
    
    # test
    module_logger = logging.getLogger("schoolsplay.SPLogging")
    module_logger.info("logger created, start logging")
    import Version
    module_logger.info("Starting childsplay version: %s" % Version.version)
    
