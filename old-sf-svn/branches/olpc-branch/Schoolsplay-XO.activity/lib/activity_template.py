# -*- coding: utf-8 -*-

# Copyright (c) <year> <your name> <your email>
#
#           activity_template.py
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
# replace activity_template in "schoolsplay.activity_template" with the name
# of the activity. Example: activity is called memory -> 
# 
# In your Activity class -> 
# 
# logging.error("I don't understand logger")
# See SP manual for more info 

# standard modules you probably need
import os,sys

import pygame
from pygame.constants import *

import schoolsplay.utils as utils
from schoolsplay.SPConstants import *
import schoolsplay.SPSpriteUtils as SPSpriteUtils

# containers that can be used globally to store stuff
class Img:
    pass
class Snd:
    pass

class Activity:
    """  Base class mandatory for any SP activty.
    The activity is started by instancing this class by the core.
    This class must at least provide the following methods.
    start (self) called by the core before calling loop.
    next_level (self,level) called by the core when the user changes levels.
    loop (self,events) called 40 times a second by the core and should be your 
                      main eventloop.
    helptitle (self) must return the title of the game can be localized.
    help (self) must return a list of strings describing the activty.
    name (self) must provide the activty name in english, not localized in lowercase.
  """

    def __init__(self,SPGoodies):
        """SPGoodies is a class object that SP sets up and will contain references
        to objects, callback methods and observers
        TODO: add more explaination"""
        logging.info("Activity started")
        self.SPG = SPGoodies
        self.screen = self.SPG.get_screen()
        self.backgr = self.SPG.get_background()
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'templateData')
        
        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special CPGroup
        self.actives = SPSpriteUtils.SPInit(self.screen,self.backgr)
        
    def get_helptitle(self):
        """Mandatory method"""
        return _("Activity")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "activity"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity"),
        _(""),
        " ",
        _("Difficulty :  years"),
        " "]

        return text 
    
    def start(self):
        """Mandatory method."""
        pass
    def get_score(self,timespend):
        """Mandatory method.
        @timespend is the time spend inside the level as it's calculated
        by the core.
        returns the score value for the past level.
        return None if no score value is used"""
        m,s = timespend.split(':')
        seconds = int(m)*60 + int(s)
        
    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        pass
    
    def post_next_level(self):
        """Mandatory method.
        This is called by the core after 'next_level' *and* after the 321 count.
        You should place stuff in here that run in a seperate thread like sound play."""
        pass  

    def loop(self,events):
        """Mandatory method
        TODO: Do we need a return value?"""
        for event in events:
            if event.type is MOUSEBUTTONDOWN:
                pass
                # call your objects
        return 
        
