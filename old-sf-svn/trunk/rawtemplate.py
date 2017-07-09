TemplateString = \
'''
# -*- coding: utf-8 -*-

# Copyright (c) %(year)s %(dev_name)s %(dev_email)s
#
#           %(name)s.py
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
    helptitle (self) must return the title of the game can be localized.
    help (self) must return a list of strings describing the activty.
    name (self) must provide the activty name in english, not localized in lowercase.
  """

    def __init__(self,SPGoodies):
        """SPGoodies is a class object that SP sets up and will contain references
        to objects, callback methods and observers
        TODO: add more explaination"""
        self.logger =  logging.getLogger("schoolsplay.%(name)s.Activity")
        self.logger.debug("Activity started")
        self.SPG = SPGoodies
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CRData','%(datadirname)s')
        
        # The frame received from the core will be our "parent window" 
        # The core will remove us when were finished.
        self.parentframe = self.SPG.get_parent()
        # we use an alignment to center our toplevel activity widget in the parentframe
        self.mainalignment = gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0.5, yscale=0.5)
        self.parentframe.add(self.mainalignment)
        
        # TESTCODE remove these two lines in a real activity
        self.mainalignment.add(gtk.Label("TEST LABEL"))
        self.mainalignment.show_all()
        
        # get a reference to the topbar with the 'numberrange' and thumbs button.
        # We need it to get the numberrange which will be used for the exercise
        # and we also want to be notified when the user hits the thumbs button.
        # This will probably be boilerplate code for any activity.
        self.topbar = self.SPG.get_topbar()
        # Be aware that calling 'set_sensitive_toggles' will emits a GTK 'toggled'
        # signal by the topbar and if you have registered any observers they will
        # be called.
        # That's why we call 'set_sensitive_toggles' BEFORE 'register_*_observer'.
        # If we don't the observers will be called while they are not properly setup yet
        self.topbar.set_sensitive_toggles((1,1,1,1))
        self.topbar.register_numbersrangebut_observer(self._numbersrange_observer)
        self.topbar.register_solutionbut_observer(self._solutionbut_observer)
                        
    def _numbersrange_observer(self,range,on_off):
        # When the user changes the numberrange we will quit this activity and
        # restart the current level with a new numberrange
        self.SPG.tellcore_restart_level(store_db=True)

    def _solutionbut_observer(self):
        self.logger.debug("_solutionbut_observer called")

    def get_helptitle(self):
        """Mandatory method"""
        return _("%(Name)s")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "%(name)s"
    
    def get_levelscount(self):
        """Mandatory method, must return an iteger indicating the number of levels."""
        return 4
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),
        _(""),
        " ",
        _("Author : %(dev_name)s")]
        return text 
    
    def get_helptip(self):
        """Mandatory method, when no tips available returns an empty list"""
        return []
        
    def get_helptype(self):
        """Mandatory method, you must set an type"""
        # Possible types are: Memory, Math, Puzzle, Keyboardtraining, Mousetraining
        #                     Language, Alphabet, Fun, Miscellaneous
        return _("Miscellaneous")
        
    @splitpoint@
    
    def start(self):
        """Mandatory method."""
        pass
    
    def stop(self):
        """Mandatory method, called by the core when the activity is finished.
        Used to stop any threads started by this object."""
        pass

    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        if level > self.get_levelscount():
            return False
        return True
    
    def post_next_level(self):
        """Mandatory method.
        This is called by the core after 'next_level' *and* after the 321 count.
        You should place stuff in here that run in a seperate thread like sound play."""
        pass 
        
    def get_score(self,timespend):
        """Mandatory method.
        @timespend is the time spend inside the level as it's calculated
        by the core.
        returns the score value for the past level.
        return None if no score value is used"""
        m,s = timespend.split(':')
        seconds = int(m)*60 + int(s)
        
'''

KludgeString =\
'''
    def get_helplevels(self):
        """Mandatory method, must return a string with the number of levels
        in the follwing format:
        _("This level has %s levels") % number-of-levels"""
        return _("This activity has %s levels") % self.get_levelscount()
'''