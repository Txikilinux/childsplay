# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zytkiewicz stas.zytkiewicz@gmail.com
#
#           quiz_picture.py
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
# In your Activity class -> 
# self.logger =  logging.getLogger("schoolsplay.quiz_picture.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("schoolsplay.quiz_picture")

# standard modules you probably need
import os,sys
# needed to import quiz
sys.path.insert(0, './lib')

import pygame
from pygame.constants import *

import utils
from SPConstants import *
import SPSpriteUtils
import quiz_text
# containers that can be used globally to store stuff
class Img:
    pass
class Snd:
    pass

class Activity(quiz_text.Activity):
    """  Base class mandatory for any SP activty.
    The activity is started by instancing this class by the core.
    This class must at least provide the following methods.
    start (self) called by the core before calling 'next_level'.
    post_next_level (self) called once by the core after 'next_level' *and* after the 321 count. 
    next_level (self,level) called by the core when the user changes levels.
    loop (self,events) called 40 times a second by the core and should be your 
                      main eventloop.
    get_helptitle (self) must return the title of the game can be localized.
    get_help (self) must return a list of strings describing the activty.
    get_helptip (self) must return a list of strings or an empty list
    get_name (self) must provide the activty name in english, not localized in lowercase.
    stop_timer (self) must stop any timers if any.
  """

    def __init__(self,SPGoodies):
        """SPGoodies is a class object that SP sets up and will contain references
        to objects, callback methods and observers
        TODO: add more explaination"""
        self.logger =  logging.getLogger("schoolsplay.quiz_picture.Activity")
        self.logger.info("Activity started")
        quiz_text.Activity.__init__(self, SPGoodies)
        
        # The location of the activities Data dir
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','Quiz_pictureData')
        self.rchash = utils.read_rcfile(os.path.join(self.my_datadir, 'quiz_picture.rc'))
        self.rchash['theme'] = self.theme
    
    def _start_engine(self):
        self.quizengine = quiz_text.Engine(['picture'], self.SPG, self.observer)
    
    def start(self):
        """Mandatory method."""
        self._start_engine()
        self.quizengine.set_retry(int(self.rchash[self.theme]['retry']))
        self.SPG.tellcore_set_dice_minimal_level(1)
    
    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        # Your top blit position, this depends on the menubar position 
        self.level = level
        self.levelupcount = 0
        return True
    def post_next_level(self):
        """Mandatory method.
        This is called once by the core after 'next_level' *and* after the 321 count.
        You should place stuff in here that run in a separate thread like sound play."""
        if self.level == 1:
            self.maxpoints = 2
            self.quizengine.init_exercises(2, self.num_questions,1)
        elif self.level == 2:
            self.maxpoints = 4
            self.quizengine.init_exercises(4, self.num_questions, 1) 
        else:
            self.maxpoints = 4
            self.quizengine.init_exercises(4, self.num_questions, self.level) 
        self.quizengine.next_question()
    
    def get_helptitle(self):
        """Mandatory method"""
        return _("Picture Quiz")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "quiz_picture"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),
                _("Answer the quiz questions."), 
        " ",
        _("At the top of the screen, you will see a picture on the screen with a related question."),
        _("Below it are a choice of possible answers.\nTouch the correct answer."), 
        " "]
        return text 
    
    def get_helptip(self):
        """Mandatory method, when no tips available returns an empty list"""
        return ''
        
    def get_helptype(self):
        """Mandatory method, you must set an type"""
        # Possible types are: Memory, Math, Puzzle, Keyboardtraining, Mousetraining
        #                     Language, Alphabet, Fun, Miscellaneous
        return _("Miscellaneous")
    
    
    def get_helplevels(self):
        """Mandatory method, must return a string with the number of levels
        in the follwing format:
        _("This level has %s levels") % number-of-levels"""
        return _("This activity has %s levels") % 6

    def get_score(self,timespend):
        """Mandatory method.
        @timespend is the time spend inside the level as it's calculated
        by the core.
        returns the score value for the past level.
        return None if no score value is used"""
        m,s = timespend.split(':')
        seconds = int(m)*60 + int(s)
    
    def stop_timer(self):
        """You *must* provide a method to stop timers if you use them.
        The SPC will call this just in case and catch the exception in case 
        there's no 'stop_timer' method""" 
        try:
            self.timer.stop()
        except:
            pass

