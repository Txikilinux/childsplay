# -*- coding: utf-8 -*-

# Copyright (c) 2007-2010 Stas Zykiewicz <stas.zytkiewicz@schoolsplay.org>
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

#class SPCheckPass(object):
#    Login = _(\
#"If you start the GUI for the first time there's no\
# username and password set so you should just hit the 'Login' button.\n\
# You will get a warning message telling you to set as soon as possible\
# a username and password.\nYou can set a username and password in the GUI.\n\
# Go to 'Settings' -> 'Set password'.")
#     
#    TopLevel = _(\
#"Failed to get the dbase data, try to run childsplay_sp first to setup the dbase")

#class SPgdm(object):
#    _info_button_callback = _(\
#"Give your login name in the box and hit the login button.\
# Alternatively you can just hit the login button and run Childsplay_sp in\
# anonymous mode.")

class DataManager(object):
    _replace_dbase = _(\
"There was an error in the database this can be caused by many things\
 but most of the time it's caused by the fact that your version of the database\
 doesn't match the version of the program.\
 I will backup your original database and then replace it with a new one.\
 The original database is now called sp.db_back and it's placed in %s" % HOMEDIR)

    default_group_1 = _("Default group 1")
    default_group_2 = _("Default group 2")
    #default_user_1 = _("Default user 1")
    
class Nosound(object):
    ActivityStart = _(\
"It seems that we cannot use the sound card right now and because this activity\
 is all about sound, we just quit.\
 This problem can also be caused by another application which uses the\
 soundcard right now.")

class Act_ichanger(object):
    box1 = _(\
"""Memorize the pictures.

One of these pictures will be replaced by a new picture.

Touch the 'Start' button to begin the game.""")
    box2 = _(\
"""

Touch the changed picture.""")

    box3 = _(\
"""

Touch the 'Play' button to continue the game.""")
    
#class AdminGui(object):
#    on_button_help = _(\
#"This database table holds the values used when displaying the results graph in an activity.\n\
#The column 'MU-value' holds an integer between 0 and 10 indicating the average score.(the dark blue line).\n\
#The column 'SIGMA-value' holds an integer between 0 an 100 indicating the standard\
# deviation in percentage, probably always 50. (the light blue box)\n\n\
#Click on the row you want to alter and then click on the field you wish to edit.\n\
#You cannot edit the 'Activity name' field.\n\
#Use the 'Save' button to store the changes in the database.")


#class ToolTipText(object):
#    """The names of the attributes must be the same as the activity module names.
#    String must conform to the following syntax:
#    <Proper english name> <comma> <the word 'difficulty'><semi colon><space><number of 'stars' eg '*'
#    """
#    memory = _("Memory, difficulty: */**")
#    electro_sp = _("Association, difficulty: **/***")
#    findit_sp = _("Spot the differences, difficulty:*/**")
#    simon_sp = _("Repeat sound sequence, difficulty:*/***")
#
#    def get_tooltip(self, name):
#        """Returns the tooltip string or when it can't be found the activity name
#        is returnt."""
#        try:
#            attr = getattr(self, name)
#        except AttributeError:
#            s = name
#        else:
#            s = attr
#        return s

class ActivityMenuText(object):
    """These strings are used by the SPMenu module to set additional text for 
    the menu icons. This is only used when the xml attribute text is set to True
    in the menu xml. The attributes must be the name of the module."""
    usermanagement = _("Usermanagement")
    groupmanagement = _("Groupmanagement")
    dt_sequence_manual = _("Daily training sequence")
    picimport = _("Picture import")
    change_pass = _("Change password")
    change_pass_admin = _("Change password")
    update_btp = _("Update BrainTrainerPlus")
    gamemanagement = _("Gamemanagement")
    zorgenquete = "Zorg enquette"
    language_select = _("Select Language")
    settings_op = _("Settings")
    settings_adm = _("Settings")
    content_import = _("Content import")
    

class ActivityType(object):
    """These type strings are placed here so that the gettext can pick them
    up and place them in the pofile
    They are not used in the program. Perhaps in the future."""
    MemoryType = _("Memory")
    MathType = _("Math")
    PuzzleType = _("Puzzle")
    KeyboardtrainingType = _("Keyboardtraining")
    MousetrainingType = _("Mousetraining")
    LanguageType = _("Language")
    AlphabetType = _("Alphabet")
    FunType = _("Fun")
    MiscellaneousType = _("Miscellaneous")
    
    
    
    
    
