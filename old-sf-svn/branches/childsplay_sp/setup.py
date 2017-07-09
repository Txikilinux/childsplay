#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2006-2007 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           setup.py
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

"""
------------------------------------------------------------------------------
This script will install childsplay on your system.
All the Python modules are installed in the default Python location on your
system, on most GNU/Linux systems that's '/python/site-packages'.
The rest of the modules and files are installed in /usr/local/childsplay_sp.

You can change the non-python install location by altering the variable called
'PREFIX' inside this script.
(Change it only if you understand why you want to change it)
This script also generate a module with all the paths needed by childsplay.

Childsplay is "fun and games" part of the schoolsplay project and uses many
of the schoolsplay modules. See www.schoolsplay.org, for more info.
This means that sometimes it's possible that certain messages speak of
"schoolsplay", you can just read "childsplay" instead.
-------------------------------------------------------------------------------

"""
import os.path
import sys
# we check for the special 'uninstall' option, other options are handled by
# the distutils stuff.

if sys.argv[1] == 'uninstall':
    UNINSTALL = True
    print "\n------------ Uninstalling childsplay ----------------\n"
    print "I'm going to completely remove childsplay from your system."
    ans = raw_input("Hit 'y' to remove childsplay > ")
    if ans.lower() != 'y':
        print "Operation canceled, leaving childsplay intact."
        sys.exit(0)
else:
    UNINSTALL = False
    print __doc__
    raw_input("Hit any key to continue\n")

# Change this if you want to install all the non-python stuff in a different
# location.
PREFIX = '/usr/local'
#PREFIX = '/tmp'

# Don't change anything below this line unless you fully understand why you want
# to make changes.

# This script basically runs from top to bottom.

import Version

try:
    import distutils
except ImportError:
    raise SystemExit, "childsplay requires distutils (Python-dev) to build and install."

from distutils.core import setup

from distutils.sysconfig import get_python_lib

# Check to see if we have an old cp install
try:
    from childsplay_sp import SPBasePaths
except ImportError:
    OLDBASEPATHS = False
else:
    OLDBASEPATHS = SPBasePaths

import os, glob, shutil

### TODO: WINDOWS STUFF IS UNCHECKED, IT MUST BE CHECKED.
def check_for_windows():
    """Check if we are on Windows, if so return the tuple with the version info.
    If not, return None.
    Taken from the python docs:
    Return a tuple containing five components, describing the Windows version 
    currently running. 
    The elements are major, minor, build, platform, and text. text contains a
    string while all other values are integers.
    platform may be one of the following values:
    
    Constant                        Platform
    0 (VER_PLATFORM_WIN32s)         Win32s on Windows 3.1
    1 (VER_PLATFORM_WIN32_WINDOWS)  Windows 95/98/ME
    2 (VER_PLATFORM_WIN32_NT)       Windows NT/2000/XP
    3 (VER_PLATFORM_WIN32_CE)       Windows CE
    """
    print " Checking for Windows version..."
    try:
        winver = sys.getwindowsversion()
    except:
        print " No Windows found, your must be a sensible person."
        return None
    else:
        print " %s found" % winver[4]
        return winver

# from here we setup the non-python stuff and write a module with the paths.
if not UNINSTALL:
    print "\n------------ Installing non-python files ------------\n"
    ARE_WE_WINDOWS = check_for_windows()
    
module = 'SPBasePaths.py'
modulepaths = {'ALPHABETDIR':os.path.join(PREFIX, 'share', 'sp_alphabetsounds')}
#--------------- Remove old SPBasePaths
if os.path.exists(module):
    print "Found an old %s file, removing it..." % module,
    os.remove(module)
    print " done"
modulepaths['BASEDIR'] = os.path.join(PREFIX, 'childsplay_sp')

#-------------- copy activity data dirs
# if there's already a FlashcardsData/names dir we back it up as the user can 
# have localized names files.
# REMINDER: This can cause trouble when the included English names ever changes.
fcd = os.path.join(PREFIX, 'share', 'childsplay_sp', 'CPData', 'FlashcardsData', 'names')
fcd_back = ""
if os.path.exists(fcd):
    print "Found an existing FlashcardsData/names directory used by the Flashcards activity"
    print "It can contain localized soundfiles so I will save it and restore it after the"
    print "new FlashcardsData directory is installed."
    fcd_back = os.path.join(os.getcwd(), 'names_back')
    shutil.copytree(fcd, fcd_back)

dest = os.path.join(PREFIX, 'share', 'childsplay_sp')
if os.path.exists(dest):
    print "Found an old %s directory, removing it..." % dest,
    shutil.rmtree(dest)
    print " done"

if not UNINSTALL:
    dest = os.path.join(PREFIX, 'share', 'childsplay_sp')
    if not os.path.exists(dest):
        print "Creating %s..." % dest,
        os.makedirs(dest)
    modulepaths['SHARELIBDATADIR'] = dest
    print " done"
    
    print "Copy childsplay activity data dirs..."
    src = os.path.join(os.getcwd(), 'lib')
    for sppath in glob.glob(src + os.sep + '*'):
        if os.path.isdir(sppath):
            name = os.path.basename(sppath)
            fdest = os.path.join(dest, name)
            print "copy %s to\n %s" % (sppath, fdest)
            shutil.copytree(sppath, fdest)
    print " done"
    # restore the names if any
    if fcd_back:
        print "restore %s" % fcd
        shutil.rmtree(fcd)
        shutil.copytree(fcd_back, fcd)
        shutil.rmtree(fcd_back)
    
#----------- copy alphabetsounds dir
if UNINSTALL:
    dest = os.path.join(PREFIX, 'share', 'sp_alphabethsounds')
    if os.path.exists(dest):
        print "Found an old %s directory, removing it..." % dest,
        shutil.rmtree(dest)
        print " done"
if not UNINSTALL:
    # special Python2.4 fix as 2.4 shutil doesn't create complete trees
    try:
        os.makedirs(os.path.join(PREFIX, 'share', 'sp_alphabetsounds'))
    except:
        pass
    dest = os.path.join(PREFIX, 'share', 'sp_alphabetsounds', 'en')
    if os.path.exists(dest):
        print "Removing old English alphabetsounds directory"
        shutil.rmtree(dest)
    print " done"

    print "Copy childsplay English alphabetsounds directory..."
    src = os.path.join(os.getcwd(), 'alphabetsounds', 'en')
    print "copy %s to\n %s" % (src, dest)
    shutil.copytree(src, dest)
    print " done"
    
#---------- copy locale  dirs
def cleanup( * args):
    """Used by os.path.walk to traverse the locale tree and remove childsplay mo files."""
    #print "cleanup:",args
    try:
        if 'childsplay_sp.mo' in args[2]:
            fpath = os.path.join(args[1], 'childsplay_sp.mo')
            print "Removed old localization file: %s" % fpath,
            os.remove(fpath)
            print " done"
    except (IndexError, AttributeError):
        # empty LC_MESSAGES directory
        pass
        
def install( * args):
    #print "install:",args
    #if os.path.basename(args[2][0]) == 'childsplay_sp.mo':
    if len(args[2]) > 0 and os.path.basename(args[2][0]) == 'childsplay_sp.mo':
        fpath = os.path.join(args[1], args[2][0])
        dest = os.path.join(args[0], args[1].split('locale' + os.sep)[1])
        print "Install localization file in: %s" % dest,
        #print "copy",fpath,dest
        if not os.path.exists(dest):
            os.makedirs(dest)
        shutil.copy(fpath, dest)
        print " done"
    
src = os.path.join(os.getcwd(), 'locale')
dest = os.path.join(PREFIX, 'share', 'locale')
print dest
if os.path.exists(dest):
    # we must digg through all the locale directories to find any childsplay_sp mo files
    # removing the mo files
    os.path.walk('%s' % dest, cleanup, None)
if not UNINSTALL:
    print "Creating %s..." % dest,
    if not os.path.exists(dest):
        os.makedirs(dest)
    modulepaths['LOCALEDIR'] = dest
    print " done"
    
    print "Copy localization files..."
    os.path.walk('%s' % src, install, dest)

#---------------- copy docs
###### temp code to remove old named schoolsplay
dest = os.path.join(PREFIX, 'share', 'doc', 'schoolsplay')
if os.path.exists(dest):
    print "Found an old %s directory, removing it..." % dest,
    shutil.rmtree(dest)
    print " done"
##################################
src = os.path.join(os.getcwd(), 'doc')
dest = os.path.join(PREFIX, 'share', 'doc', 'childsplay_sp')
if os.path.exists(dest):
    print "Found an old %s directory, removing it..." % dest,
    shutil.rmtree(dest)
    print " done"

if not UNINSTALL:
    print "Creating %s..." % dest,
    os.makedirs(dest)
    modulepaths['DOCDIR'] = dest
    print " done"
    
    print "Copy documentation files..."
    for sppath in glob.glob(src + os.sep + '*'):
        name = os.path.basename(sppath)
        fdest = os.path.join(dest, name)
        print "copy %s to\n %s" % (sppath, fdest)
        if os.path.isdir(sppath):
            shutil.copytree(sppath, fdest)
        else:
            shutil.copy(sppath, fdest)
            
#-------- remove old python modules, if any.
if OLDBASEPATHS:
    pdest = OLDBASEPATHS.PYTHONCPDIR
else:
    pdest = os.path.join(get_python_lib(), 'childsplay_sp')
print "Looking for previous childsplay python install in %s" % pdest
modulepaths['PYTHONCPDIR'] = pdest
if os.path.exists(pdest):
    print "Found old childsplay_sp python package in %s, removing it..." % pdest,
    shutil.rmtree(pdest)
    print " done"

#---------- copy starters
dest = os.path.join(PREFIX, 'bin')
starterpath = os.path.join(dest, 'childsplay_sp')
if os.path.exists(starterpath):
    print "Found an old %s file, removing it..." % starterpath,
    os.remove(starterpath)
    print " done"
starterpath = os.path.join(dest, 'cognitionplay')
if os.path.exists(starterpath):
    print "Found an old %s file, removing it..." % starterpath,
    os.remove(starterpath)
    print " done"
    
if not UNINSTALL:
    print "Install childsplay programs..."
    src = os.path.join(os.getcwd(), 'bin')
    if not os.path.exists(dest):
        print "Creating %s..." % dest
        os.makedirs(dest)
    for sppath in glob.glob(src + os.sep + '*'):
        name = os.path.basename(sppath)
        print "copy %s to\n %s" % (sppath, dest)
        shutil.copy(sppath, dest)
        
# all the uninstalling is done so we check if we should stop now
if UNINSTALL:
    print "childsplay IS REMOVED"
    print "Bye..."
    sys.exit(0)

# check where we will install python stuff, needed for the SPBasePaths file.
if not os.path.exists('/usr/lib/python2.6/site-packages') and os.path.exists('/usr/local/lib/python2.6/dist-packages'):
    print "Not found destination path: %s" % '/usr/local/lib/python2.6/site-packages'
    print "This is a known problem on some Debian based systems like Ubuntu 9.04 and newer."
    print "If your not on a Debian based system, please inform the childsplay developers"
    modulepaths['PYTHONCPDIR'] = '/usr/local/lib/python2.6/dist-packages/childsplay_sp'
    print  "Using %s as the install path" % modulepaths['PYTHONCPDIR']
 
# write the paths module. This file is placed inside the sourcetree and the 
# python installer will also install it.
# Add the path to the childsplay_sp python libs. This is needed when we write
# the starter script.

if ARE_WE_WINDOWS:
    src = os.path.join(os.getcwd(), 'windows', 'SPBasePaths.py')
    dest = os.getcwd()
    shutil.copy(src, dest)
else:
    print "Writing the SPBasePaths module...",
    filelines = ["# AUTO-GENERATED MODULE, DON'T EDIT", \
        "# This module holds all the paths needed for childsplay_sp.\n"]
    for k, v in modulepaths.items():
        filelines.append("%s = '%s'" % (k, v))
    f = open(module, 'w')
    f.write("\n".join(filelines))
    f.close()
    print "done"
# Here we start installing the Python modules
print "\n------------- Installing Python modules ------------------\n"
# add a quiet commandline option to supress all the "compile to" crap
sys.argv.insert(1, '--quiet')

DESCRIPTION = """childsplay is a collection of educational activities and
comes with extensive data collecting and multi user support."""
VERSION = Version.version
print "Installing new childsplay_sp python package..."
print "Installing childsplay_sp ocempgui..."
setup(name="childsplay_sp",
        version=VERSION,
        license="GPL",
        url="http://schoolsplay.sf.net",
        author="Stas Zytkiewicz",
        author_email="stas.zytkiewicz@gmail.com",
        description="Collection of educational activities",
        long_description=DESCRIPTION,
        packages=['childsplay_sp', 'childsplay_sp.gui', 'childsplay_sp.lib', \
            'childsplay_sp.ocempgui', \
            'childsplay_sp.ocempgui.access', 'childsplay_sp.ocempgui.draw', \
            'childsplay_sp.ocempgui.events', 'childsplay_sp.ocempgui.object', \
            'childsplay_sp.ocempgui.widgets', \
            'childsplay_sp.ocempgui.widgets.components', \
            'childsplay_sp.ocempgui.widgets.images', \
            'childsplay_sp.ocempgui.widgets.themes', \
            'childsplay_sp.ocempgui.widgets.themes.default'],
        package_dir={'childsplay_sp':''}
        )

print "All done"


#--------------- Remove generated SPBasePaths
if os.path.exists(module):
    print "\nRemoving from the sourcedir %s ..." % module,
    os.remove(module)
    print "Installation finished"

print "\n====== all done ======"
print "childsplay is installed in %s" % starterpath
print "To start childsplay just type 'childsplay' in a xterm"
print "To see the available commandline options type 'childsplay --help in a xterm\n"
