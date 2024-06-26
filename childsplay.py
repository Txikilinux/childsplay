#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zykiewicz <stas.zytkiewicz@schoolsplay.org>
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

from SPBasePaths import SHARELIBDATADIR

if len(sys.argv) > 2:
    if sys.argv[1] == '--plainversion':
        from .SPVersion import version
        print ( version )
        if os.path.exists('/data/userdata/.schoolsplay.rc/tmp'):# btp production only
            shutil.rmtree('/data/userdata/.schoolsplay.rc/tmp',True)
        sys.exit(0)
    # construct proper restart command if we need to restart
    prog = "python %s " % os.path.join(os.getcwd(), " ".join(sys.argv))

print ( sys.argv )


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

from . import SPLogging
SPLogging.set_level(CMD_Options.loglevel)
SPLogging.start()

#create logger, configuration of logger was done above
import logging as logger
CPmodule_logger = logger.getLogger("childsplay.childsplay")
CPmodule_logger.debug("Created schoolsplay loggers")

from . import utils

BTPPID = None
BTPSTART = None
try:
    BTPPID = CMD_Options.kill_btp
    BTPSTART = CMD_Options.restart_btp
except AttributeError:
    CPmodule_logger.info("No kill_btp or restart_btp option given")
else:
    if BTPPID and BTPSTART:
        CPmodule_logger.warning("Found BTP pid, killing BTP with pid: %s" % BTPPID)
        subprocess.Popen("kill -9 %s" % BTPPID, shell=True)
        utils._remove_lock()
        BTPSTART = 'cd .. && ' + BTPSTART
    else:
        CPmodule_logger.info("No pid for BTP")

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

import sqlalchemy.orm as sqlorm

import time
import datetime

#CPmodule_logger.info("IMPORTANT READ THE FOLLOWING LINES")
#CPmodule_logger.info("For debugging purposes we run with some cmdline options hardcoded.")
#CPmodule_logger.info("These must be removed before releasing this to the real world")
#CPmodule_logger.info("Look at the top of this module for these options")
from .SPConstants import *
sys.path.insert(0, BASEDIR)
sys.path.insert(0, os.path.join(BASEDIR, 'lib'))

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
name = 'childsplay'
p = os.path.join(HOMEDIR, name)
if not os.path.exists(p):
    os.makedirs(p)
orgxmlfiles = glob.glob(os.path.join(THEMESPATH, name, '*.xml'))
existingxmlfiles = os.listdir(p)
for f in  XML_FILES_WE_MUST_HAVE:
    if f not in existingxmlfiles and os.path.exists(os.path.join(THEMESPATH, name, f)):
        src = os.path.join(THEMESPATH, name, f)
        CPmodule_logger.debug("Copying %s to %s" % (src, p))
        shutil.copy(src, p)

## We also want to have the default photo albums in a writable location
#p = os.path.join(HOMEDIR, 'braintrainer', 'DefaultAlbums')
#if not os.path.exists(p):
#    os.makedirs(p)
#orgalbums = [a for a in glob.glob(os.path.join(ACTDATADIR, 'PhotoalbumData', '*_Album_*')) if os.path.isdir(a)]
#existingxmlfiles = os.listdir(p)
#for f in orgalbums:
#    if os.path.basename(f) not in existingxmlfiles and os.path.exists(f):
#        shutil.copytree(f, os.path.join(p, os.path.basename(f)))

# for childsplay we must make sure we have a content dbase in sqlite3 format present.
# if we want to use an sqlite content dbase we must make sure the default one is in the proper location.
p = os.path.join(HOMEDIR, CMD_Options.theme, CONTENTDBASE)
if not os.path.exists(p):
    if os.path.exists(CONTENTDBASE):
        shutil.copy(CONTENTDBASE, p)
    else:
        shutil.copy(os.path.join(SHARELIBDATADIR, CONTENTDBASE), p)
                        
import pygame
## set a bigger buffer, seems that on win XP in conjuction with certain hardware
## the playback of sound is scrambled with the "normal" 1024 buffer.
###  XXXX this still sucks, signed or unsigned that's the question :-(
pygame.mixer.pre_init(22050, -16, 2, 2048)
pygame.init()

# this will return the tuple (lang,rtl=bool)
LANG = utils.set_locale(lang=CMD_Options.lang)

# display a splash for 3 seconds
start_splash = time.time()
screen = pygame.display.set_mode((700, 200), pygame.NOFRAME)
background = pygame.Surface(screen.get_size())
p = os.path.join(SHARELIBDATADIR, 'SPData/themes/childsplay/cp-btp-splash.png')
backgroundimage = utils.load_image(p)
background.blit(backgroundimage, (0, 0))
screen.blit(background, (0, 0))
pygame.display.update()


if CMD_Options.checklog:
    try:
        from . import SPlogCheck
    except (ImportError, utils.SPError):
        sys.exit(1)
    except utils.MyError:
        sys.exit(1)
    sys.exit(0)
        
if not utils._set_lock():
    sys.exit(1)

from . import SPMainCore

mcgui = None

from .SPgdm import GDMEscapeKeyException

# start the maincore, we only return here on an exit
CPmodule_logger.debug("Start logging")
CPmodule_logger.debug("commandline options: %s" % CMD_Options)
CPmodule_logger.debug("SPMainCore running from: %s" % SPMainCore)

from .SPDataManagerCreateDbase import DbaseMaker
DEBUG = False
try:
    #This will setup the dbases and ORMS
    dbm = DbaseMaker(CMD_Options.theme, debug_sql=DEBUG)            
except ( (AttributeError, sqla.exceptions.SQLAlchemyError, utils.MyError) ):
    CPmodule_logger.exception("Failed to start the DBase, %s")
    raise utils

mainscreen = None
abort = 0 
tellcore_error = False


while not abort:
    abort = True
    restartme = False
    try:
        if not tellcore_error:
            # query for a session id
            try:
                orm = dbm.get_all_orms()['stats_session']
                content_engine, user_engine = dbm.get_engines()
                session = sqlorm.sessionmaker(bind=user_engine)()
            except ( Exception ):
                CPmodule_logger.exception("Failed to get orm for stats_session: %s")
                abort = True
                break
        orm = orm(datetime=datetime.datetime.now())
        session.add(orm)
        session.commit()
        orm = dbm.get_all_orms()['stats_session']
        result = session.query(orm).all()[-1]
        session_id = result.ID
        session.close()
        # there's no support for other resolutions than 800x600
        mcgui = SPMainCore.MainCoreGui(resolution=(800, 600),
                                        options=CMD_Options, dbmaker = dbm,
                                        mainscr=mainscreen, error=tellcore_error,
                                        session_id=session_id, start_splash=start_splash,
                                       language=LANG)
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
    except (SystemExit, utils.StopmeException) as status:
        if str(status) == '0':
            CPmodule_logger.info("systemexit, clean exit")
            abort = True
        else:
            CPmodule_logger.info("systemexit, not a clean exit")
            CPmodule_logger.info("restarting core.")
            tellcore_error = True
            if mcgui is not None:
                mcgui.call_foreign_observers(logger)
    except utils.SPError:
        CPmodule_logger.error("Unrecoverable error, not a clean exit")
        CPmodule_logger.info("restarting core.")
        tellcore_error = True
        if mcgui is not None:
            mcgui.call_foreign_observers(logger)
    except Exception:
        CPmodule_logger.exception("unhandled exception in toplevel, traceback follows:")
        CPmodule_logger.info("restarting core.")
        tellcore_error = True
        if mcgui is not None:
            mcgui.call_foreign_observers(logger)
try:
    mcgui.activity.stop_timer()
except ( Exception ):
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
if (CMD_Options.theme == 'braintrainer' and restartme) or (BTPPID and BTPSTART):
    restartme = False
    CPmodule_logger.info("respawing with :%s" % BTPSTART)
    pid = subprocess.Popen(BTPSTART, shell=True).pid
    CPmodule_logger.debug("launched Control Panel with pid %s" % pid)
    sys.exit()


