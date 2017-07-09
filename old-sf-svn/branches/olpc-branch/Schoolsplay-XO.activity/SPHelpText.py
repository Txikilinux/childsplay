# -*- coding: utf-8 -*-

# Copyright (c) 2007 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           SPHelpText.py
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

# This module contains classes that provide larger help text for different parts
# of schoolsplay, including the GUI.
# The objects are arranged in a way that resembles a python package
# For example, to get the text for the GUI SPCheckPass Login frame:
# ht = SPHelpText.SPCheckPass.Login

from SPConstants import HOMEDIR

class SPCheckPass(object):
    Login = _(\
"If you start the GUI for the first time there's no\
 username and password set so you should just hit the 'Login' button.\n\
 You will get a warning message telling you to set as soon as possible\
 a username and password.\nYou can set a username and password in the GUI.\n\
 Go to 'Settings' -> 'Set password'.")
     
    TopLevel = _(\
"Failed to get the dbase data, try to run childsplay_sp first to setup the dbase")

class SPgdm(object):
    _help_button_callback = _(\
"Give your login name in the box and hit the login button.\
 Alternatively you can just hit the login button and run Schoolsplay in\
 anonymous mode.")

class DataManager(object):
    _replace_dbase = _(\
"There was an error in the database this can be caused by many things\
 but most of the time it's caused by the fact that your version of the database\
 doesn't match the version of the program.\
 I will backup your original database and then replace it with a new one.\
 The original database is now called cr_sp.db_back and it's placed in %s" % HOMEDIR)

class AdminGui(object):
    on_button_help = _(\
"This database table holds the values used when displaying the results graph in an activity.\n\
The column 'MU-value' holds an integer between 0 and 10 indicating the average score.(the dark blue line).\n\
The column 'SIGMA-value' holds an integer between 0 an 100 indicating the standard\
 deviation in percentage, probably always 50. (the light blue box)\n\n\
Click on the row you want to alter and then click on the field you wish to edit.\n\
You cannot edit the 'Activity name' field.\n\
Use the 'Save' button to store the changes in the database.")
