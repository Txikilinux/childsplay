# Copyright (c) 2010 stas zytkiewicz stas.zytkiewicz@schoolsplay.org
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 of the GNU General Public License
# as published by the Free Software Foundation.  A copy of this license should
# be included in the file GPL-3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

# provides a logging object
# All modules get the same logger so this must called asap

### example "application" code to use in your module
##import logging
##module_logger = logging.getLogger("childsplay.<name of your module>")
##logger.debug("debug message")
##logger.info("info message")
##logger.warn("warn message")
##logger.error("error message")
##logger.critical("critical message")
##logger.exception("exception message")

import os
from SPConstants import HOMEDIR
LOGPATH = os.path.join(HOMEDIR, "childsplay.log")

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
    logger = logging.getLogger("childsplay")
    logger.setLevel(CONSOLELOGLEVEL)
    sqla_logger = logging.getLogger("sqlalchemy")
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
    sqla_logger.addHandler(fh)
    logger.info("File logger created: %s" % LOGPATH)
    
    # test
    module_logger = logging.getLogger("childsplay.SPLogging")
    module_logger.info("logger created, start logging")
    import Version
    module_logger.info("Starting childsplay version: %s" % Version.version)
    
