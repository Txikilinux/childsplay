# -*- coding: utf-8 -*-

# Copyright (c) 2011 Rene Dohmen acidjunk@gmail.com
#
#           filewalker.py
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 of the GNU General Public License
# as published by the Free Software Foundation. A copy of this license should
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


####### IMPORTANT READ THIS ####################################################
# This is a script to collect info for the photoalbum                          #
################################################################################

import os, sys, glob

xml_header = """<?xml version="1.0" encoding="utf-8"?>
<album name="Museum in echt 2010" nofPicture="79">"""
xml_footer = """</album>
</xml>"""

xml = xml_header

dirname = "nl_Album_4"
os.chdir(dirname)
matches = glob.glob('*.jpg')
matches.sort()
for fileName in matches:
    #os.system("mv %s %s" % (fileName,fileName[:-4]))
    print "Found: %s" % fileName
    title=raw_input("\nEnter title:")
    text=raw_input("\nEnter text:")
    xmlPart="""\t<photo name="%s">
        <title>%s</title>
        <text>%s</text>
    </photo>""" % (fileName,title,text)
    xml = "%s\n%s" % (xml, xmlPart)
print xml
   




