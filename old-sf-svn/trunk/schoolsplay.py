#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2008 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           schoolsplay.py
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

import sys

# ignore warnings as it isn't useful for the user to see them.
# At this moment, release 1.3, the gtk builder in SimpleGladeApp raises warnings
# and sqlalchemy is also a DeprecationWarning generator.
import warnings
warnings.simplefilter("ignore")

# first parse commandline options
from SPOptionParser import OParser
# if this doesn't bail out the options are correct and we continue with schoolsplay
op = OParser()
# this will return a class object with the options as attributes 
# OLPC: set default options in the OParser class as we don't have cmd line options
CMD_Options = op.get_options()

if not CMD_Options.bundle_id:# are we not on a XO?
    import SPLogging
    SPLogging.set_level(CMD_Options.loglevel)
    SPLogging.start()
    
import logging
module_logger = logging.getLogger("schoolsplay")

# check dependencies
try:
    import sqlalchemy
except ImportError:
    module_logger.error("No sqlalchemy package found, stopping.")
    sys.exit(1)

try:
    import gtk
except ImportError:
    module_logger.error("No gtk package found, stopping.")
    sys.exit(1)
if gtk.gtk_version[1] <= 14:
    module_logger.error('Found python-GTK version: %s.%s.%s' % gtk.gtk_version)
    module_logger.error('Please upgrade your python-GTK to 2.15 or higher')
    sys.exit(1)
    
try:
    import pygtk
except ImportError:
    module_logger.error("No pygtk package found, stopping.")
    sys.exit(1)

import SPVersion
module_logger.info("%s" % SPVersion.gtkversion)
module_logger.info("%s" % SPVersion.pygtkversion)
module_logger.info("%s" % SPVersion.sqlversion)

# needed for some modules
sys.path.append('')

if CMD_Options.admingui:
    #start admingui
    sys.path.append('gui')
    try:
        import AdminGui
        AdminGui.main()
    except Exception,info:
        module_logger.exception("GUI raised an exception")
        sys.exit(1)
    else:
        sys.exit(0)

import utils
# this will return the tuple (lang,rtl=bool)
LANG = utils.set_locale(lang=CMD_Options.lang)

import SPMainCore
from SPgdm import GDMEscapeKeyException

# start the maincore, we only return here on an exit
module_logger.debug("Start logging")
module_logger.debug("commandline options: %s" % CMD_Options) 

class Observer:
    """Class which is used to start and stop the GUI, gtk mainloop, and is
    passed around the various objects.
    this differs from the childsplay ipc which uses exceptions to send signals
    to start or stop. GTK caches all exceptions so we use a class object as a
    observer which takes care of starting and stopping.
    Activities shouldn't use this class but use the SPGoodies object which
    provides abstract methods to this class."""  
    def __init__(self,parent=None):
        self.logger = logging.getLogger("schoolsplay.Observer")
        self.parent = parent
    def start_gui(self):
        if CMD_Options.bundle_id: # are we on a XO?
            self.mcgui = SPMainCore.MainCoreGuiXO(self.parent,\
                                        options=CMD_Options,\
                                        language=LANG,\
                                        observer=self)
        else:
            self.mcgui = SPMainCore.MainCoreGui(self.parent,\
                                        options=CMD_Options,\
                                        language=LANG,\
                                        observer=self)
        self.mcgui.start()
    def restart_gui(self):
        self.logger.info("clean exit, restarting...")
        self.mcgui.stop()
        self.start_gui()
    def stop_gui(self):
        self.logger.info("clean exit, stopping...")
        try:
            self.mcgui.stop()
        except AttributeError,info:
            if hasattr(self, 'mcgui'):# otherwise it's expected :-)
               self.logger.exception("Failed to stop GUI")
               
    def error_stop(self):
        self.logger.exception("unhandled exception in toplevel, traceback follows:")
        try:
            self.mcgui.stop()
        except:
            sys.exit(1)

if __name__ == '__main__':
    obs = Observer()
    obs.start_gui()

########## Profiling code ###########
##    import hotshot,hotshot.stats
##
##    prof = hotshot.Profile("sp_cr.prof")
##    prof.runcall(main)
##    prof.close()
##    print "stops"
##    
##    stats = hotshot.stats.load("sp_cr.prof")
##    stats.strip_dirs()
##    stats.sort_stats('time', 'calls')
##    stats.print_stats(20)

##    ############ Debugger code ########
##    import pdb
##    pdb.runcall(main)



