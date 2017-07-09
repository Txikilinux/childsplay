# -*- coding: utf-8 -*-

# Copyright (c) 2006-2008 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
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

## The module "SPBasePaths" is created by the installation proces.
        
## paths ##
import sys

import SPBasePaths
import logging
import os
SPCmodule_logger = logging.getLogger("schoolsplay.SPConstants")

#module_logger.debug("Contents of os.environ: %s" % os.environ)
#module_logger.debug("Contents of sys.argv %s " % sys.argv)

# Import keymaps as they are now in a seperate module.
from SPKeyMaps import KeyMaps

# Which themes do we have?
SUPPORTEDTHEMES = ['default', 'cognitionplay']
# Which keymaps do we have?
SUPPORTEDKEYMAPS = KeyMaps.supportedmaps
# The base of the schoolsplay installation, only used on win98?
BASEDIR = SPBasePaths.BASEDIR
# here are the activities data directories installed
ACTIVITYDATADIR = SPBasePaths.SHARELIBDATADIR
# check if we are cognitionplay, the share lib differs.
if 'cognitionplay' in sys.argv[0]:
    ACTIVITYDATADIR = ACTIVITYDATADIR.replace('childsplay_sp', 'cognitionplay')
# gettext mo files location
LOCALEDIR = SPBasePaths.LOCALEDIR
# Localized soundfiles
ALPHABETDIR = SPBasePaths.ALPHABETDIR
# Path to the childsplay_sp python modules
PYTHONCPDIR = SPBasePaths.PYTHONCPDIR
# Path to the ocempgui base directory needed by the included ocempgui
OCWBASEDIR = os.path.join(PYTHONCPDIR, 'ocempgui')
# Users sp dir
HOME_DIR_NAME = '.schoolsplay.rc'
# Name of the SQLite dbase
DBASE = 'cp_sp.db'

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

DBASEPATH = os.path.join(HOMEDIR, DBASE)
# lockfile path used to set a lock to prevent multiple instances of childsplay
LOCKFILE = os.path.join(HOMEDIR, '.splock')
HOMEIMAGES = os.path.join(HOMEDIR, 'my_images')
# Create a schoolsplay directory and a my_images subdirectory.
# The my_images is used by the memory and puzzle activities to let the user
# use his own images images.
if not os.path.exists(HOMEDIR):
    os.makedirs(HOMEDIR)
if not os.path.exists(HOMEIMAGES):
    os.makedirs(HOMEIMAGES)

# set font path and fontsize
TTFSIZE = 19# used for default ttf
TTF = os.path.join(ACTIVITYDATADIR, 'SPData', 'DejaVuSansCondensed-Bold.ttf')
if os.path.exists(TTF):
    # default size for DejaVuSansCondensed
    TTFSIZE = 12
# These are for the pango fonts
P_TTFSIZE = 11
P_TTF = 'sans'

# colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
KOBALT_LIGHT_BLUE = (78, 185, 250)
DARK_BLUE = (0, 0, 127)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (170, 170, 170)
DARK_GREY = (100, 100, 100)
LIGHT_GREY = (220, 220, 220)

# coords for core buttons, button is 82x82
CORE_BUTTONS_XCOORDS = range(6, 790, 88)







