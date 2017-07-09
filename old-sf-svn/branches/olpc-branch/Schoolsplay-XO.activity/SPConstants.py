# -*- coding: utf-8 -*-

# Copyright (c) 2006 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
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

     
## paths ##
import SPBasePaths
import sys,os
import logging
module_logger = logging.getLogger("schoolsplay.SPConstants")

# The base of the schoolsplay installation, only used on win98?
BASEDIR = SPBasePaths.BASEDIR
# here are the activities data directories installed
ACTIVITYDATADIR = SPBasePaths.SHARELIBDATADIR
# gettext mo files location
LOCALEDIR = SPBasePaths.LOCALEDIR
# Users sp dir
HOME_DIR_NAME = '.schoolsplay.rc'
# Name of the SQLite dbase
DBASE = 'cr_sp.db'

HOMEDIR = SPBasePaths.HOMEDIR
#HOMEDIR = '/home/stas'
if not os.path.exists(HOMEDIR):
    os.makedirs(HOMEDIR)
    
DBASEPATH = os.path.join(HOMEDIR,DBASE)       

# set font path and fontsize
TTFSIZE = 19# used for default ttf
TTF = os.path.join(ACTIVITYDATADIR,'SPData','DejaVuSansCondensed-Bold.ttf')
if os.path.exists(TTF):
    # default size for DejaVuSansCondensed
    TTFSIZE = 12
  
##  flags ##
MONITOR = None # Special monitor plugin, optional, future use
RCFILES = None # Can we use configuration files
SPLASH = True # do we want a splash  
helptext = "Not much help here yet, look at the manpage and docs."

# colors
RED = '#FF0000'
GREEN = '#00FF00'
BLUE = '#0000FF'
YELLOW = '#FFFF00'
WHITE = '#FFFFFF'
BLACK = '#000000'
GTKGRAY = '#D6D6D6'
GRAY = '#AAAAAA'
DARK_GRAY = '#646464'
LIGHT_GRAY = '#B4B4B4'
GOLD = '#F5CB54'
# coords for core buttons, button is 82x82
CORE_BUTTONS_XCOORDS = range(6,790,88)

## fribidi support. Used for RTL locales
# This is to signal that we running under a RTL locale like Hebrew or Arabic
# Only Hebrew is supported until now
try:
    import pyfribidi# only needed for RTL languages
except ImportError:
    module_logger.info("I can't find pyfribidi. It's only needed in a RTL env.")
    pyfribidi = None

LOCALE_RTL = None

# Hash tables used to provide different keyboard layouts for RTL languages
# and Russian.
# See the 'map_keys' function on possible usage.
he_key_map={
u'Q':u'/',
u'W':u'\'',
u'E':u'ק',
u'R':u'ר',
u'T':u'א',
u'Y':u'ט',
u'U':u'ו',
u'I':u'ן',
u'O':u'ם',
u'P':u'פ',
u'[':u']',
u']':u'[',
u'A':u'ש',
u'S':u'ד',
u'D':u'ג',
u'F':u'כ',
u'G':u'ע',
u'H':u'י',
u'J':u'ח',
u'K':u'ל',
u'L':u'ך',
u';':u'ף',
u'\'':u',',
u'Z':u'ז',
u'X':u'ס',
u'C':u'ב',
u'V':u'ה',
u'B':u'נ',
u'N':u'מ',
u'M':u'צ',
u',':u'ת',
u'.':u'ץ',
u'/':u'.'
}

ar_key_map={
u'Q':u'ض',
u'W':u'ص',
u'E':u'ث',
u'R':u'ق',
u'T':u'ف',
u'Y':u'غ',
u'U':u'ع',
u'I':u'ه',
u'O':u'خ',
u'P':u'ح',
u'[':u'ج',
u']':u'د',
u'A':u'ش',
u'S':u'س',
u'D':u'ي',
u'F':u'ب',
u'G':u'ل',
u'H':u'ا',
u'J':u'ت',
u'K':u'ن',
u'L':u'م',
u';':u'ك',
u'\'':u'ط',
u'Z':u'<',
u'X':u'ئ',
u'C':u'ء',
u'V':u'ؤ',
u'B':u'ر',
u'N':u'ﻻ',
u'M':u'ى',
u',':u'ة',
u'.':u'و',
u'/':u'ز'
}

ru_key_map={
u'Q':u'й',
u'W':u'ц',
u'E':u'у',
u'R':u'к',
u'T':u'е',
u'Y':u'н',
u'U':u'г',
u'I':u'ш',
u'O':u'щ',
u'P':u'з',
u'[':u'х',
u']':u'ъ',
u'A':u'ф',
u'S':u'ы',
u'D':u'в',
u'F':u'а',
u'G':u'п',
u'H':u'р',
u'J':u'о',
u'K':u'л',
u'L':u'д',
u';':u'ж',
u'\'':u'э',
u'Z':u'я',
u'X':u'ч',
u'C':u'с',
u'V':u'м',
u'B':u'и',
u'N':u'т',
u'M':u'ь',
u',':u'б',
u'.':u'ю',
u'/':u'.'
}







