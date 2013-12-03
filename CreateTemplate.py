# -*- coding: utf-8 -*-

# Copyright (c) 2008-2013 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           CreateTemplate.py
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


#TODO: rewrite this script so that it takes themes in account for the menu location


"""

  This script to create a activity template and to setup various stuff
  like dbase tables and data directories.
  
  The script will ask you a number of questions about the various parts of the
  activity framework.
  Be aware that if you don't understand the questions it is better to go to
  the schoolsplay mailinglist and contact the devs who will explain the
  various possibilities of this script.

  You can quit the script at any time by hitting 'q'

  Be aware that this script alters the contents of the following modules and
  files:
  lib/SPData/menu/default/SP_menu.xml
  SQLTables.py
  
  It creates a template file called <activity name>.py inside /lib, adds a
  directory called <activity name>Data inside /lib and it adds a image file 
  in lib/SPData/themes/default
  
  Be sure to make copies of the files mentioned above because they could become
  corrupt when using this script.
  
"""
try:
    import elementtree.ElementTree as ET
except ImportError:
    print "failed to import elementtree.ElementTree as ET"
    print "trying to import the 2.5 module xml.etree.ElementTree"
    try:
        import xml.etree.ElementTree as ET
    except ImportError:
        print "This script uses 'ElementTree' but it's not installed"
        print "Look for 'python-elementtree' in your GNU/Linux distro and install it"
        print "Windows users should loo at http://effbot.org/downloads/#elementtree"
        sys.exit(1)

print __doc__

import sys,os,time
import shutil

# needed for certain SP modules we import
import SPLogging
SPLogging.set_level('error')
SPLogging.start()
import utils
utils.set_locale()


#---------------- Some functions used internally
def error(text):
    print "=============== ERROR =========================================="
    print "  %s" % text
    print "  Quitting...\n"
    print "================================================================"
    sys.exit(1)

def check_for_q(ans):
    if ans.lower() == 'q':
        print "\nUser has hit 'q'"
        print "Quitting...\n"
        sys.exit(0)

def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for e in elem:
            indent(e, level+1)
            if not e.tail or not e.tail.strip():
                e.tail = i + "  "
        if not e.tail or not e.tail.strip():
            e.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

template_dict = {'name':'',\
            'Name':'',\
            'dev_name':'Joe Haxor',\
            'dev_email':'J.Haxor@blackhat.org',\
            'year': time.strftime("%Y", time.gmtime()),\
            }

data_dict = {'datadirname':'',\
            'tablename':'',\
            'tablecols':[],
            'iconpath':''}

print "For which theme will the activity be created ?"
ans = raw_input("\nGive the theme name: ")
check_for_q(ans)
if not ans:
    error("you must give a theme name for your activity")
theme = ans

# this one is mandatory
print "\n=== Activity name ==="
print "The name of your activity is important because it will also be used\n\
in the activities help text as well as the dbase table name\n\
Be sure you don't pick a name that's currently used for an existing activity\n\
Spaces are not allowed in the name, everything else is allowed."

ans = raw_input("\nGive the name of the activity: ")
check_for_q(ans)
if not ans:
    error("you must give a name for your activity")

#--------------- check to see if the name is in use already.
import sqlalchemy as sqla
from SPConstants import HOMEDIR, DBASE
DBASEPATH = os.path.join(HOMEDIR, theme,DBASE)
print "\nLooking for the schoolsplay dbase in %s" % DBASEPATH

import SPGuiDBModel
dm = SPGuiDBModel.get_datamanager()
tbnames = dm.get_table_names()
print "Found the following names:" 
for tn in tbnames:
    print tn," ",
print ""
if ans in tbnames:
    error("name '%s' is already in use" % ans)

#--------------- Add name to the dicts
template_dict['name'] = ans
template_dict['Name'] = ans.capitalize()
template_dict['datadirname'] = "%sData" % ans.capitalize()
data_dict['datadirname'] = "%sData" % ans.capitalize()
data_dict['tablename'] = ans

#------------- get the menu icon path
print "\n=== Menu icon ==="
print "Every activity must have an image which will serve as an icon in the menu\n\
You should give the full path to your image and this script will copy it to the \n\
correct directory.\n\
If you know that the image is already inside the correct directory and added to\n\
menu xml file then just hit enter.\n\
Be aware that the image must have a size of 72x72 and must be in the png format.\n\
This script doesn't check for the image size or format."
ans = raw_input("\nGive the image path :")
if ans:
    check_for_q(ans)
    if not ans:
        print "Assuming the image is correctly setup"
    elif not os.path.exists(ans):
        error("Path %s doesn't exists" % ans)
data_dict['iconpath'] = ans

#--------------- Get developers name and email
print "\n=== Developers info ==="
print "You will be asked for your name and email address. You should give your\n\
true name and email address as aliasses or fantasy names are for wannabees.\n\
Your email wil only be put inside the copyright notice at the top of the\n\
template." 
ans = raw_input("\nGive your name :")
if ans:
    template_dict['dev_name'] = ans
ans = raw_input("\nGive your email address: ")
if ans:
    template_dict['dev_email'] = ans
    
#-------------- Dbase tables and columns
print "\n=== Database tables and columns ==="
print "You will now be asked a few questions about the kind of dbase table your\n\
activity will use. \n\
This script only supports 'Integer' and 'String' if you need other column types you\n\
should edit the module SQLTables yourself.\n\
Every activity must have a dbase table even if your activity won't\n\
use it the SP core uses a table to store some standard info about your activity.\n\
If you don't want to use additional table columns for your activity just hit\n\
'Enter' when asked about the number of table columns.\n\
When there aren't additional columns given a standard dbase table will be added\n\
to the SQLTables module.\n\
"
ans = raw_input("\nHow many columns do you want to add to the dbase table? : ")
check_for_q(ans)
if ans:
   for i in range(1,int(ans)+1):
        col = raw_input("Give the name of additional column %d: " % i)
        check_for_q(col)
        coltype = raw_input("Give the type for the column [integer or string i/s]: ")
        check_for_q(coltype)
        if coltype == 's':
            stringlen = raw_input("How long should the 'String' field be? [number of characters]: ")
            check_for_q(stringlen)
            data_dict['tablecols'].append((col,'String',stringlen))
        else:
            data_dict['tablecols'].append((col,'Integer',''))

print "\nThat's all"
print "\n=== Generating template and dbase table"
print "These are the values I will use to create/alter the various modules."

print "Data used for the activity template:"
for k,v in template_dict.items():
    print "%s:%s" % (k,v)

print "Data used for the dbase table and directory paths:"  
print "('tablecols' will be empty when no additional columns are given)"
for k,v in data_dict.items():
    if k == 'tablecols':
        print "Tablecols:"
        for t in v:
            print "    name: %s, type: %s, length: %s" % t
    else:
        print "%s:%s" % (k,v)

ans = raw_input("\nAre these correct? [y/n]")
if ans.lower() != 'y':
    print "Restart script to use other values"
    print "Quitting..."
    sys.exit(0)
print "I will now start to generate the various files and dbase tables."
print "There will be various comments printed on teh screen, be sure to read them."
raw_input("-------- Hit any key -------- ")

#-------------- Generating template
import rawtemplate
print "\nGenerate a template file for your activity..."
# check that we don't overwrite an existing file.
if os.path.exists('lib/%s.py' % template_dict['name']):
    error("File called lib/%s.py already exists" % template_dict['name'])
print template_dict
ts = rawtemplate.TemplateString % template_dict

# now the dict values are placed inside the string so we now add the string
# with the "%s" formatting inside it.
# XXX I don't know how to mix dictionary mapping with string formatting
kludge = rawtemplate.KludgeString
first,second = ts.split('@splitpoint@',1)
ts = first + kludge + second

open('lib/%s.py' % template_dict['name'],'w').write(ts)
print "done, module is placed in lib/%s.py" % template_dict['name']

#--------------- Creating data directorie(s)
print "\nCreating the activities data directory... "
os.mkdir('lib/CPData/%s' % data_dict['datadirname'])
print "done, directory is placed in lib/CPData/%s" % data_dict['datadirname']

#---------------- Copying the menu icon and editing the menu file
if not data_dict['iconpath']:
    # assuming icon is already setup
    pass
else:
    icondest = os.path.join('lib/SPData/themes/%s/menuicons' % theme, '%s.icon.png' % template_dict['name'])
    print "\nCopying the icon image from %s to %s..." % (data_dict['iconpath'],icondest)
    shutil.copyfile(data_dict['iconpath'],icondest)
    print "done"

    print "\nI will now add an node in the menu XML file so that SP can use the image\n\
    in the menu.\n\
    ====== IMPORTANT STUFF, READ THIS ===============\n\
    You must edit the 'position' attribute for you menu icon in the XML file\n\
    it is set to '0,0', meaning top left corner.\n\
    If you don't alter the 'position' attribute your menu will be screwed\n\
    You must also place the new node inside a <submenu> node.\n\
    To edit the node start your editor and open 'lib/SPData/themes/default/SP_menu.xml'\n\
    look at the bottom for an entry like this; <menuitem file='%s'.icon.png>.\n\
    Below that there's an entry; <position>0,0</position>\n\
    Change it to the correct position" % template_dict['name']
    print "\nAdding node to SP_menu.xml..."
    tree = ET.parse('lib/SPData/themes/%s/SP_menu.xml' % theme)
    root = tree.getroot()
    node = ET.SubElement(root, 'menuitem')
    node.set('file','%s.icon.png' % template_dict['name'])
    node0 = ET.SubElement(node,'activity')
    node0.text = template_dict['name']
    node1 = ET.SubElement(node,'position')
    node1.text = '0,0'
    indent(tree.getroot())
    #tree.write(sys.stdout)
    #sys.stdout.flush()
    print "I will backup the original SP_menu.xml before making alterations..."
    shutil.copyfile('lib/SPData/themes/%s/SP_menu.xml' % theme,'lib/SPData/themes/%s/SP_menu.xml.back' % theme)
    f = open('lib/SPData/themes/%s/SP_menu.xml' % theme,'w')
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    tree.write(f,'utf-8')
    f.close()
   
#-------------- Editing SQLTables module

import SQLTables
print "\nStarting to alter the module: %s" % SQLTables
print "I will backup the original SQLTables module before making alterations..."

shutil.copyfile('SQLTables.py','SQLTables.py.back')
print "done, placed a copy in SQLTables.py.back"

# we start to split the module in two and insert our table.
sqlmod = open('SQLTables.py','r').read()
first,second = sqlmod.split('@splitpoint@',1)
first += '@splitpoint@\n' # restore splitpoint for future split

if data_dict['tablecols']:
    rows = ["""        self.%(tablename)s = Table('%(tablename)s',metadata,\\""" % data_dict]
    for t in data_dict['tablecols']:
        if t[1] == 'Integer':
            rows.append("""                Column('%s', Integer),\\""" % t[0])
        else:
            rows.append("""                Column('%s', String(%s)),\\""" % (t[0],t[2]))
    rows.append("                    )")
else:
    rows = ["""        self.%(tablename)s = Table('%(tablename)s',metadata)""" % data_dict]
#add the rows to the first part
first += '\n'.join(rows)
# and combine it again
sqlmod = first+second

# now we add our table to the table list inside SQLTables
# for that we need another split.
first,second = sqlmod.rsplit(']',1)
first += ",\\\n"
row = """                        self.%(tablename)s]\n""" % data_dict
# combine it 
sqlmod = first+row+second

# write it to disk
print "Writing a new SQLTables.py module..."
open('SQLTables.py','w').write(sqlmod)
print "done."

print """\nScript finished, have fun coding your activity.
Read the dev docs that are available in this tarball or on the schoolsplay site.
If you need more information or help don't hesitate to contact the schoolsplay
mailinglist or one of the developers.

The template module for your activity is placed inside the 'lib' directory and
the directory you can use to store activity specific data is also placed inside 
'lib'.
"""
 





