
# -*- coding: utf-8 -*-

# Copyright (c) 2009 Stas Zytkiewicz stas.zytkiewicz@gmail.com
#
#           act_sub_1.py
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

#create logger, logger was setup in SPLogging
import logging

# standard modules you probably need
import os,sys,random,time

import utils
from SPConstants import *

import gtk,pango

# SimpleGladeApp turns a glade file into a GTK app
from SimpleGladeApp import SimpleGladeApp

import act_add_1
from act_add_1 import ExercisesTable

# containers that can be used globally to store stuff
class Img:
    pass
class Snd:
    pass

class Activity(act_add_1.Activity):
    """  Base class mandatory for any SP activty.
    The activity is started by instancing this class by the core.
    This class must at least provide the following methods.
    start (self) called by the core before calling loop.
    next_level (self,level) called by the core when the user changes levels.
    helptitle (self) must return the title of the game can be localized.
    help (self) must return a list of strings describing the activty.
    name (self) must provide the activty name in english, not localized in lowercase.
  """

    def __init__(self,SPGoodies):
        """SPGoodies is a class object that SP sets up and will contain references
        to objects, callback methods and observers
        TODO: add more explaination"""
        act_add_1.Activity.__init__(self, SPGoodies)
        self.logger =  logging.getLogger("schoolsplay.act_sub_1.Activity")
        self.logger.debug("Activity started")
        self.kindstring = "-"

    def _numbersrange_observer(self,range,on_off):
        # When the user changes the numberrange we will quit this activity and
        # restart the current level with a new numberrange
        self.SPG.tellcore_restart_level(store_db=True)

    def get_helptitle(self):
        """Mandatory method"""
        return _("Subtract numbers")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "act_sub_1"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),
        _("Subtract the numbers."), 
        _("Empty solutions are considered wrong solutions."),
        " ",
        _("Author: Stas Zytkiewicz")]

        return text 
    
    def get_helptip(self):
        """Mandatory method, when no tips available returns an empty list"""
        return []
