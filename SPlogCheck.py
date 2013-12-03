# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zykiewicz <stas.zytkiewicz@schoolsplay.org>
#
#           SPlogCheck.py
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

import os, re, glob
from SPConstants import SPLC_TIMESTAMP, HOMEDIR
FILEPATH = os.path.join(HOMEDIR, "SPErrorLog_" + SPLC_TIMESTAMP +".log")
from SPLogging import LOGPATH
from utils import SPError, MyError

import logging
SPLCmodule_logger = logging.getLogger("childsplay.SPlogCheck")
SPLCmodule_logger.debug("Starting to parse SP log %s for warning messages and higher" % LOGPATH)

oldfiles = glob.glob(os.path.join(HOMEDIR, "SPErrorLog_*"))
oldfiles.sort()
if len(oldfiles) > 20:
    SPLCmodule_logger.warning("Removing older error files")
    for i in range(20, len(oldfiles)):
        try:
            f = oldfiles.pop(0)
            os.remove(f)
        except (IOError, IndexError):
            SPLCmodule_logger.warning("Can't remove file %s" % f)
        else:
            SPLCmodule_logger.warning("removed %s" % f)
            
# Which messages to look for
pattern = re.compile("ERROR|CRITICAL")
lines = []
try:
    f = open(LOGPATH, 'r')
    #f = open('/home/stas/.schoolsplay.rc/test.log', 'r')
    lines = f.readlines()
except IOError:
    SPLCmodule_logger.warning("Can't find the SP logfile ?")
    SPLCmodule_logger.warning("Start schoolsplay with minimal loglevel info to get a logfile.")
    SPLCmodule_logger.warning("Stopping the log parsing.")

if not lines:
    SPLCmodule_logger.warning("The logfile %s hasn't any content ?" % LOGPATH)
    SPLCmodule_logger.warning("Stopping the log parsing.")
    lines =[]
    
notifycaller = False
for line in lines:
    if re.search(pattern, line):
        SPLCmodule_logger.warning("Found error messages in the log file, please contact the developers")
        SPLCmodule_logger.warning("Saving the SP log to %s" % FILEPATH)
        f = open(FILEPATH, 'w')
        f.writelines(lines)
        f.close()
        notifycaller = True
        break
        
if notifycaller:        
    raise MyError, _("Found error messages in the log file, please contact the developers.")



