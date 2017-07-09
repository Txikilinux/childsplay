# -*- coding: utf-8 -*-

# Copyright (c) 2006-2010 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           SPConstants.py
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

# Set the NoGtk constants to True if you don't want to use gtk stuff.
NoGtk = False
QUIZPAUSE = 1500
# DON'T CHANGE ANYTHING BELOW THIS LINE !!!!
# If you want to change the paths, change SPBasePaths.py

import sys

import SPBasePaths
import logging
import os
import time
SPCmodule_logger = logging.getLogger("schoolsplay.SPConstants")

#module_logger.debug("Contents of os.environ: %s" % os.environ)
#module_logger.debug("Contents of sys.argv %s " % sys.argv)

from SPColors import *

# Import keymaps as they are now in a seperate module.
from SPKeyMaps import KeyMaps

# Which themes do we have?
SUPPORTEDTHEMES = ['default', 'childsplay','cognitionplay', 'seniorplay', \
                    'mpt', 'braintrainer']
# Which keymaps do we have?
SUPPORTEDKEYMAPS = KeyMaps.supportedmaps
# The base of the schoolsplay installation, only used on win98?
BASEDIR = SPBasePaths.BASEDIR
# here are the activities data directories installed
ACTIVITYDATADIR = SPBasePaths.SHARELIBDATADIR
# gettext mo files location
LOCALEDIR = SPBasePaths.LOCALEDIR
# Localized soundfiles
ALPHABETDIR = SPBasePaths.ALPHABETDIR
if not os.path.exists(ALPHABETDIR):
    ALPHABETDIR = os.path.join(BASEDIR, 'alphabetsounds')
# Path to the childsplay_sp python modules
PYTHONCPDIR = SPBasePaths.PYTHONCPDIR
# Path to the ocempgui base directory needed by the included ocempgui
OCWBASEDIR = os.path.join(PYTHONCPDIR, 'ocempgui')

GUITHEMESPATH = os.path.join(ACTIVITYDATADIR, 'SPData', 'gui','themes')
DEFAULTGUITHEMESPATH = os.path.join(GUITHEMESPATH,'default')

THEMESPATH = os.path.join(ACTIVITYDATADIR, 'SPData', 'themes')
DEFAULTTHEMESPATH = os.path.join(THEMESPATH,'default')

CORESOUNDSDIR = os.path.join(ACTIVITYDATADIR, 'SPData', 'base', 'sounds')

# Users sp dir
HOME_DIR_NAME = '.schoolsplay.rc'
# Name of the SQLite dbase
DBASE = 'sen_sp.db'

# language
LANG = 'en'
LOCALE_RTL = None

# Check if there's a schoolsplay dir in the home directory
if sys.platform == 'win32':
    PLATFORM = 'win32'
    try:
        HOMEDIR = os.path.join(os.environ['HOMEDRIVE'], os.environ['HOMEPATH'], HOME_DIR_NAME)
    except:
        # for win 98 ??
        HOMEDIR = os.path.join(BASEDIR, HOME_DIR_NAME)
        if not os.path.exists(HOMEDIR):
            os.makedirs(HOMEDIR) 
else:
    PLATFORM = 'All your platform are belong to us'
    try:
        HOMEDIR = os.path.join(os.environ['HOME'], HOME_DIR_NAME)
    except KeyError, info:
        print info
        HOMEDIR = os.path.abspath(sys.path[0])
        
PSYCOPATH = os.path.join(HOMEDIR, 'schoolsplay_psyco.log')
DBASEPATH = os.path.join(HOMEDIR, DBASE)
# lockfile path used to set a lock to prevent multiple instances of childsplay
LOCKFILE = os.path.join(HOMEDIR, '.splock')
HOMEIMAGES = os.path.join(HOMEDIR, 'my_images')
# Create a schoolsplay directory and subdirectories.
if not os.path.exists(HOMEDIR):
    os.makedirs(HOMEDIR)
for name in SUPPORTEDTHEMES:
    p = os.path.join(HOMEDIR, name)
    if not os.path.exists(p):
        os.makedirs(p)

# set font path and fontsize
TTFSIZE = 19# used for default ttf
TTF = os.path.join(ACTIVITYDATADIR, 'SPData', 'base', 'arial.ttf')
TTFBOLD = os.path.join(ACTIVITYDATADIR, 'SPData', 'base','DejaVuSansCondensed-Bold.ttf')
if os.path.exists(TTF):
    # default size for DejaVuSansCondensed
    TTFSIZE = 12

# These are for the pango fonts
P_TTFSIZE = 11
P_TTF = 'arial' #'bookman'

#[6, 94, 182, 270, 358, 446, 534, 622, 710]
CORE_BUTTONS_XCOORDS = range(6, 790, 88)

SPLC_TIMESTAMP = time.strftime("%y-%m-%d_%H-%M-%S", time.localtime())



