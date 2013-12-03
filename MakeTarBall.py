#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2006-2008 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
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

ans = raw_input("Are the mo files up to date? [y/n]")
if ans != 'y':
    sys.exit(0)

distdir = 'childsplay-%s' % version
print "looking for old packages"
if os.path.exists('%s.tgz' % distdir):
    print "Removing %s.tgz" % distdir
    os.system('rm %s.tgz' % distdir)
if os.path.exists('%s.zip' % distdir):
    print "Removing %s.zip" % distdir
    os.system('rm %s.zip' % distdir)

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
os.system('mkdir %s' % distdir)

for file in myFiles:
    file = file[:-1]
    if not file or file in myExclude: 
        print 'not copying {0}'.format(file)
        continue
    os.system('cp %s %s' % (file, distdir))

for folder in myFolders:
    folder = folder[:-1]
    if not folder or folder in myExclude: 
        print 'not copying {0}'.format(folder)
        continue
    os.system('mkdir -vp %s/%s' % (distdir, folder))
    os.system('cp -r %s %s' % (folder, distdir))

# removing the svn stuff
os.path.walk('%s' % distdir,cleanup,None)

# remove the files mentioned in the exclude list
for item in myExclude:
    print item
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

#print "Create a Windows compatible zipfile..."
#try:
#    execString = 'zip -rq %s.zip ./%s' % (distdir, distdir)
#    print execString
#    os.system(execString)
#except Exception,info:
#    print info,"\nYou must have the zip package installed."
#else:
#    print "Done\n"
#os.system('rm -rf %s' % distdir)
