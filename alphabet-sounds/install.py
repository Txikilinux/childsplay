# -*- coding: utf-8 -*-

# Copyright (c) 2007-2008 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           install.py
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

## used to install alphabeth sounds in the proper schoolsplay location 

import sys,os,shutil

#------ check for schoolsplay or childsplay_sp
try:
    from childsplay_sp import SPConstants
    from childsplay_sp.utils import import_module
except ImportError,info:
    print info
    print "Failled to locate childsplay_sp, check your installation"
    print "Exit..."
    sys.exit(1)

# construct paths
lang = import_module('version.py').LANGUAGE
destdir = os.path.join(SPConstants.ALPHABETDIR,lang)

# Start installing
if os.path.exists(destdir):
    print "Found an old alphabet directory: %s, removing it..." % destdir,
    shutil.rmtree(destdir)
    print " done"
print "Install module in %s..." % destdir,
shutil.copytree(os.path.join('AlphabetSounds',lang),destdir)
print " done"

# install flashcard soundfiles is we have any
if not os.path.exists("FlashCardsSounds"):
    print "Instalation finished"
    sys.exit(0)

destdir = os.path.join(SPConstants.ACTIVITYDATADIR,"CPData","FlashcardsData", "names", lang)
if os.path.exists(destdir):
    shutil.rmtree(destdir)

print "install flashcardsounds in %s..." % destdir, 
shutil.copytree(os.path.join('FlashCardSounds', lang),destdir)

print "done"
print "Instalation finished"

