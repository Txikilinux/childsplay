#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           seniorplay
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

import sys, os, shlex, glob,shutil
sys.path.insert(0, "..")

if len(sys.argv) > 2:
    if sys.argv[1] == '--plainversion':
        from SPVersion import version
        print version
        if os.path.exists('/data/userdata/.schoolsplay.rc/tmp'):# btp production only
            shutil.rmtree('/data/userdata/.schoolsplay.rc/tmp',True)
        sys.exit(0)
    # construct proper restart command if we need to restart
    prog = "python %s " % os.path.join(os.getcwd(), " ".join(sys.argv))

import subprocess
#import gc
#gc.set_debug(gc.DEBUG_COLLECTABLE | gc.DEBUG_UNCOLLECTABLE | gc.DEBUG_INSTANCES | gc.DEBUG_OBJECTS)
# first parse commandline options
from SPOptionParser import OParser
# if this doesn't bail out the options are correct and we continue with schoolsplay

op = OParser()
# this will return a class object with the options as attributes  
CMD_Options = op.get_options()

######## Here we add options for debugging #####
### Must be removed or at least discussed before release #####
#CMD_Options.loglevel = 'debug'
# TODO: remove this when the login is using SPWidgets iso ocempgui
#CMD_Options.no_login = True
#if not CMD_Options.user:
#    CMD_Options.user = 'BT_user'
#CMD_Options.nocountdown = True

import SPLogging
SPLogging.set_level(CMD_Options.loglevel)
SPLogging.start()

#create logger, configuration of logger was done above
import logging
CPmodule_logger = logging.getLogger("schoolsplay.seniorplay")
CPmodule_logger.debug("Created schoolsplay loggers")

try:
    import sqlalchemy as sqla
except ImportError:
    CPmodule_logger.exception("No sqlalchemy package found")
    sys.exit(1)
else:
    if sqla.__version__ < '0.5.8':
        CPmodule_logger.error("Found sqlalchemy version %s" % sqla.__version__)
        CPmodule_logger.error("Your version of sqlalchemy is to old, please upgrade to version >= 0.6")
        sys.exit(1)
    CPmodule_logger.debug("using sqlalchemy %s" % sqla.__version__)
try:
    import sqlalchemy.exceptions as sqlae
except ImportError:
    from sqlalchemy import exc as sqlae
import sqlalchemy.orm as sqlorm

import time
import datetime

#CPmodule_logger.info("IMPORTANT READ THE FOLLOWING LINES")
#CPmodule_logger.info("For debugging purposes we run with some cmdline options hardcoded.")
#CPmodule_logger.info("These must be removed before releasing this to the real world")
#CPmodule_logger.info("Look at the top of this module for these options")
from SPConstants import *
if CMD_Options.loglevel == 'debug':
    CPmodule_logger.debug("Paths defined in SPConstants:")
    for v in ['ACTIVITYDATADIR', 'ALPHABETDIR', 'BASEDIR',\
               'DBASEPATH', 'HOMEDIR', 'HOMEIMAGES', 'HOME_DIR_NAME',\
               'LOCALEDIR', 'LOCKFILE']:
        CPmodule_logger.debug("%s > %s" % (v, eval(v)))

# Rudimentary language check, when it fails it sets the cmdline option to C                                                                                 
# which is available on every proper GNU/Linux system. We don't have yet a dbase 
# connection at this stage so we just check if the locale is properly formed.
# We don't care about windows of course that system locale handling sucks anyway.
loc = CMD_Options.lang
if loc.find('_') == -1 or loc.upper().find('utf8') == -1:
    pass
    
# Make sure we have xml files in a writeable place    
for name in SUPPORTEDTHEMES:
    p = os.path.join(HOMEDIR, name)
    if not os.path.exists(p):
        os.makedirs(p)
    orgxmlfiles = glob.glob(os.path.join(THEMESPATH, name, '*.xml'))
    if not orgxmlfiles:
        continue
    existingxmlfiles = os.listdir(p)
    for f in  XML_FILES_WE_MUST_HAVE:
        if f not in existingxmlfiles and os.path.exists(os.path.join(THEMESPATH, name, f)):
            shutil.copy(os.path.join(THEMESPATH, name, f), p)

# We also want to have the default photo albums in a writable location
p = os.path.join(HOMEDIR, 'braintrainer', 'DefaultAlbums')
if not os.path.exists(p):
    os.makedirs(p)
orgalbums = [a for a in glob.glob(os.path.join(ACTDATADIR, 'PhotoalbumData', '*_Album_*')) if os.path.isdir(a)]
existingxmlfiles = os.listdir(p)
for f in orgalbums:
    if os.path.basename(f) not in existingxmlfiles and os.path.exists(f):
        shutil.copytree(f, os.path.join(p, os.path.basename(f)))

# if we want to use an sqlite content dbase we must make sure the default one is in the proper location.
#p = os.path.join(HOMEDIR, CMD_Options.theme, CONTENTDBASE)
#if not os.path.exists(p):
#    shutil.copy('btp_content.db', p)    
                        
import pygame
## set a bigger buffer, seems that on win XP in conjuction with certain hardware
## the playback of sound is scrambled with the "normal" 1024 buffer.
###  XXXX this still sucks, signed or unsigned that's the question :-(
pygame.mixer.pre_init(22050, -16, 2, 2048)
pygame.init()

import utils
# this will return the tuple (lang,rtl=bool)
LANG = utils.set_locale(lang=CMD_Options.lang)

if CMD_Options.checklog:
    try:
        import SPlogCheck
    except (ImportError, utils.SPError):
        sys.exit(1)
    except utils.MyError:
        sys.exit(1)
    sys.exit(0)

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
    
import SPMainCore

from SPgdm import GDMEscapeKeyException

# start the maincore, we only return here on an exit
CPmodule_logger.debug("Start logging")
CPmodule_logger.debug("commandline options: %s" % CMD_Options)
CPmodule_logger.debug("SPMainCore running from: %s" % SPMainCore)

from SPDataManagerCreateDbase import DbaseMaker
DEBUG = False
try:
    #This will setup the dbases and ORMS
    dbm = DbaseMaker(CMD_Options.theme, debug_sql=DEBUG)            
except (AttributeError, sqlae.SQLAlchemyError, utils.MyError), info:
    CPmodule_logger.exception("Failed to start the DBase, %s" % info)
    raise utils.MyError, info

mainscreen = None
abort = 0 
tellcore_error = False 
while not abort:
    restartme = False
    try:
        if not tellcore_error:
            # query for a session id
            try:
                orm = dbm.get_all_orms()['stats_session']
                content_engine, user_engine = dbm.get_engines()
                session = sqlorm.sessionmaker(bind=user_engine)()
            except Exception, info:
                CPmodule_logger.exception("Failed to get orm for stats_session: %s" % info)
                abort = True
                break
        orm = orm(datetime=datetime.datetime.now())
        session.add(orm)
        session.commit()
        orm = dbm.get_all_orms()['stats_session']
        result = session.query(orm).all()[-1]
        session_id = result.ID
        session.close()
        # there's no support for other resolutions then 800x600
        mcgui = SPMainCore.MainCoreGui(resolution=(800,600),\
                                        options=CMD_Options, dbmaker = dbm,\
                                        mainscr=mainscreen, error=tellcore_error, \
                                        session_id=session_id)
        mainscreen = mcgui.get_mainscreen()
        mcgui.start()
    except SPMainCore.MainEscapeKeyException:
        CPmodule_logger.info("User hits exit/escape...")
        tellcore_error = False 
        if CMD_Options.no_login or CMD_Options.user:
            # we have no login screen or the user was passed as a cmdline option so we exit
            #sys.exit(0)
            abort = True
            CPmodule_logger.info("nologin screen, clean exit")
        elif CMD_Options.theme == 'childsplay':
            CPmodule_logger.info("Theme is childsplay, clean exit")
            abort = True
        else:
            CPmodule_logger.info("restarting core.")
            restartme = True
    except GDMEscapeKeyException:
        CPmodule_logger.info("login screen, clean exit")
        tellcore_error = False 
        break
    except utils.RestartMeException:
        CPmodule_logger.info("GIT pull occurred, need to restart myself.")
        restartme = True
        abort = True
        tellcore_error = False 
    except (SystemExit, utils.StopmeException),status:
        if str(status) == '0':
            CPmodule_logger.info("systemexit, clean exit")
            abort = True
        else:
            CPmodule_logger.info("systemexit, not a clean exit")
            CPmodule_logger.info("restarting core.")
            tellcore_error = True 
            mcgui.call_foreign_observers()
    except utils.SPError, info:
        CPmodule_logger.error("Unrecoverable error, not a clean exit")
        CPmodule_logger.info("restarting core.")
        tellcore_error = True
        mcgui.call_foreign_observers()
    except Exception,status:        
        CPmodule_logger.exception("unhandled exception in toplevel, traceback follows:")
        CPmodule_logger.info("restarting core.")
        tellcore_error = True
        mcgui.call_foreign_observers()
try:
    mcgui.activity.stop_timer()
except Exception, info:
    CPmodule_logger.warning("Failed to stop activity timers")
    
CPmodule_logger.info("Seniorplay stopped.")

#from SPWidgets import Dialog
#
#try:
#    import SPlogCheck
#except (ImportError, utils.SPError):
#    text = _("Failed to parse the logfile, please contact the developers.\nMessage was: %s" % info)
#    dlg = Dialog(text, buttons=[_('OK')], title=_('Warning !'))
#    dlg.run()
#except utils.MyError, info:
#    text = "%s" % info
#    #dlg.run()
CPmodule_logger.debug("quiting pygame and waiting 0.5 seconds.")
pygame.quit()
time.sleep(0.5)
#if sys.platform == "linux2":
#    CPmodule_logger.info("Removing pyc files")
#    subprocess.Popen('find . -name "*.pyc" -exec rm {} \;',shell=True )

# BT+ specific stuff
if CMD_Options.theme == 'braintrainer' and restartme:
    restartme = False
    CPmodule_logger.info("respawing with :%s" % prog)
    pid = subprocess.Popen(prog, shell=True).pid
    CPmodule_logger.debug("launched Control Panel with pid %s" % pid)
    sys.exit()
