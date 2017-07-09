#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2006 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           MakeTarBall.py
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

# make tarball!
from SPVersion import version
import os,sys

#print "run Po2Mo to compile po files"
#os.system('python Po2Mo.py')

print "Looking for pyc files and remove them"
os.system('find ./ -name "*.pyc" -exec rm -v {} \;')

def cleanup(*args):
    """Used by os.path.walk to traverse the tree and remove CVS dirs"""
    if os.path.split(args[1])[1] == ".svn":
        print "Removed: ",args[1]
        os.system('rm -rf %s' % args[1])

filelist = open('filelist', 'r')
folderlist = open('folderlist', 'r')
excludelist = open('excludelist','r')
myFiles = filelist.readlines()
myFolders = folderlist.readlines()
myExclude = excludelist.readlines()
distdir = 'schoolsplay-%s' % version
os.system('mkdir %s' % distdir)

for file in myFiles:
    file = file[:-1]
    if not file: continue
    os.system('cp %s %s' % (file, distdir))

for folder in myFolders:
    folder = folder[:-1]
    if not folder: continue
    os.system('mkdir -v %s/%s' % (distdir, folder))
    os.system('cp -r %s %s' % (folder, distdir))

# removing the svn stuff
os.path.walk('%s' % distdir,cleanup,None)

# remove the files mentioned in the exclude list
for item in myExclude:
    try:
        item = os.path.join(distdir,item)
        print "Exclude -> ",item,
        v = os.system('rm -r %s' % item)
        if not v:
            print "Removed file/dir ->",item
    except OSError,info:
        print "####### ERROR ######\n",info
        sys.exit(1)
# Now the dir tree is clean and ready to be packaged.
# remember we do everything in a copy, 'distdir'        
        
print "\nCreate a GNU/Linux tarball..."
try:
    execString = 'tar -czf %s.tgz %s/' % (distdir, distdir)
    print execString
    os.system(execString)
except Exception,info:
    print info,"\nYou must have the tar package installed"
else:
    print "Done.\n"

print "Create a Windows compatible zipfile..."
#print "Adding the BASEPATH script..."
#os.system('cp -f win32/BASEPATH.py schoolsplay-%s/' % version)
try:
    execString = 'zip -rq %s.zip ./%s' % (distdir, distdir)
    print execString
    os.system(execString)
except Exception,info:
    print info,"\nYou must have the zip package installed."
else:
    print "Done\n"
os.system('rm -rf %s' % distdir)
