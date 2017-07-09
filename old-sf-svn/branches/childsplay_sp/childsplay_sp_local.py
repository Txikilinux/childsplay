#!/usr/bin/env python
# -*- coding: utf-8 -*-

# DON'T INCLUDE IN A RELEASE
# Only needed to run childsplay_sp from SVN sources to test activities.
# You should also have a latest childsplay_sp release installed normally.

# Copyright (c) 2008 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           childsplay_sp_local
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

print "\n======= Read this ===================================================="
print "This script is only meant for developers to be able to run schoolsplay\n\
from sources.\n\
Don't use this for anything else.\n"

import sys
import subprocess

# first parse commandline options
from SPOptionParser import OParser
# if this doesn't bail out the options are correct and we continue with schoolsplay
op = OParser()
# this will return a class object with the options as attributes  
CMD_Options = op.get_options()
# Add special attribute which will be checked by the core to look if local activities
# should be loaded. This is only done for developing new activities.
CMD_Options.run_local = True
CMD_Options.loglevel = 'debug'

import SPLogging
SPLogging.set_level(CMD_Options.loglevel)
SPLogging.start()

#create logger, configuration of logger was done above
import logging
CPmodule_logger = logging.getLogger("schoolsplay.childsplay_sp_local")
CPmodule_logger.debug("Created schoolsplay loggers")

if CMD_Options.loglevel == 'debug':
    from SPConstants import *
    CPmodule_logger.debug("Paths defined in SPConstants:")
    for v in ['ACTIVITYDATADIR', 'ALPHABETDIR', 'BASEDIR',\
               'DBASEPATH', 'HOMEDIR', 'HOMEIMAGES', 'HOME_DIR_NAME',\
               'LOCALEDIR', 'LOCKFILE', 'OCWBASEDIR','PYTHONCPDIR']:
        CPmodule_logger.debug("%s > %s" % (v, eval(v)))

import utils
# this will return the tuple (lang,rtl=bool)
LANG = utils.set_locale(lang=CMD_Options.lang)

if CMD_Options.admingui:
    # This will not return
    try:
        import gui.AdminGui as AdminGui
        AdminGui.main()
    except Exception,info:
        print "GUI raised an exception"
        print info
        sys.exit(1)
    else:
        sys.exit(0)
        
if not utils._set_lock():
    sys.exit(1)
    
# check if we have sqlalchemy database support.
try:
    import sqlalchemy
except ImportError:
    CPmodule_logger.debug("No sqlalchemy package found, running in anonymousmode")
    CMD_Options.no_login = True   

import SPMainCore

from SPgdm import GDMEscapeKeyException

# start the maincore, we only return here on an exit
CPmodule_logger.debug("Start logging")
CPmodule_logger.debug("commandline options: %s" % CMD_Options)
CPmodule_logger.debug("SPMainCore running from: %s" % SPMainCore)

abort = 0 
while not abort:
    try:
        # there's no support for other resolutions then 800x600
        mcgui = SPMainCore.MainCoreGui(resolution=(800,600),\
                                        options=CMD_Options,\
                                        language=LANG)
    except SPMainCore.MainEscapeKeyException:
        if CMD_Options.no_login:
            CPmodule_logger.info("nologin screen, clean exit")
            # we have no login screen so we exit
            sys.exit(0)
    except GDMEscapeKeyException:
        CPmodule_logger.info("login screen, clean exit")
        break
    except SystemExit,status:
        if str(status) == '0':
            CPmodule_logger.info("systemexit, clean exit")
        else:
            CPmodule_logger.info("systemexit, not a clean exit")
    except Exception,status:        
        CPmodule_logger.exception("unhandled exception in toplevel, traceback follows:")
        abort = 1
    
CPmodule_logger.info("Childsplay stopped.")

if sys.platform == "linux2":
    CPmodule_logger.info("Removing pyc files")
    subprocess.Popen('find . -name "*.pyc" -exec rm {} \;',shell=True )
    


