# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zytkiewicz stas.zytkiewicz@gmail.com
#
#           quiz_text.py
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
# self.logger =  logging.getLogger("schoolsplay.quiz_text.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("schoolsplay.quiz_knowledge")

# standard modules you probably need
import os,sys

import pygame
from pygame.constants import *

import utils
from SPConstants import *
import SPSpriteUtils

# needed to import quizengine
sys.path.insert(0, './lib')
from quizengine import Engine

# containers that can be used globally to store stuff
class Img:
    pass
class Snd:
    pass

class Activity:
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
        self.logger =  logging.getLogger("schoolsplay.quiz_text.Activity")
        self.logger.info("Activity started")
        self.SPG = SPGoodies
        self.lang = self.SPG.get_localesetting()[0][:2]
        self.screen = self.SPG.get_screen()
        self.screenclip = self.SPG.get_screenclip()
        self.blit_pos = self.screenclip.left, self.screenclip.top
        self.logo_pos = (600, 200 + self.blit_pos[1])
        self.theme = self.SPG.get_theme()
        self.orgscreen = pygame.Surface(self.screenclip.size) # we use this to restore the screen
        self.orgscreen.blit(self.screen, (0, 0), self.screenclip)
        self.backgr = self.SPG.get_background()
        # The location of the activities Data dir
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','Quiz_textData')
        self.rchash = utils.read_rcfile(os.path.join(self.my_datadir, 'quiz_text.rc'))
        self.rchash['theme'] = self.theme
        self.rchash['lang'] = self.lang
        self.logger.debug("found rc: %s" % self.rchash)
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.CPdatadir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        # Location of the alphabet sounds dir
        self.absdir = self.SPG.get_absdir_path()# alphabet sounds dir
        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special CPGroup
        self.actives = SPSpriteUtils.SPInit(self.screen,self.backgr)
          
        self.scoredisplay = self.SPG.get_scoredisplay()
        self.num_questions = int(self.rchash[self.theme]['questions'])
        
    
    def _start_engine(self):
        l = [s.strip(' ') for s in self.rchash[self.theme]['contenttypes_%s' % self.lang].split(',')]
        self.quizengine = Engine(l, self.SPG, self.observer, self.rchash)

    def observer(self, result):
        self.logger.debug("observer called with: %s" % result)
        if result > 0:
            self.scoredisplay.increase_score(int(result))
            self.levelupcount += 1
        else:
            if self.levelupcount > 0:
                self.levelupcount -= 1
        # TODO calculate score
        # here we pause between questions
        pygame.time.wait(2000)
        pygame.event.clear()
                    
    def clear_screen(self):
        self.screen.blit(self.orgscreen,self.blit_pos)
        self.backgr.blit(self.orgscreen,self.blit_pos)
        pygame.display.update()

    def refresh_sprites(self):
        """Mandatory method, called by the core when the screen is used for blitting
        and the possibility exists that your sprites are affected by it."""
        self.actives.redraw()

    def get_helptitle(self):
        """Mandatory method"""
        return _("General knowledge Quiz")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "quiz_text"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),
                _("Answer the quiz questions."), 
        " ",
        _("At the top of the screen, you will see a general knowledge question."),
        _("Below it are a choice of possible answers.\nTouch the correct answer."), 
        " "]
        return text 
    
    def get_helptip(self):
        """Mandatory method, when no tips available returns an empty list"""
        return ''
    
    def get_extra_info(self):
        """Optional method to provide extra info to the user by adding it to the 
        help dialog"""
        return _("question id: %s") % self.quizengine.get_question_id()

    def get_helptype(self):
        """Mandatory method, you must set an type"""
        # Possible types are: Memory, Math, Puzzle, Keyboardtraining, Mousetraining
        #                     Language, Alphabet, Fun, Miscellaneous
        return _("Memory")
    
    def get_helplevels(self):
        """Mandatory method, must return a string with the number of levels
        in the follwing format:
        _("This level has %s levels") % number-of-levels"""
        return _("This activity has %s levels") % 6

    def start(self):
        """Mandatory method."""
        self._start_engine()
        self.quizengine.set_retry(int(self.rchash[self.theme]['retry']))
        #self.SPG.tellcore_set_dice_minimal_level(1)
    
    def pre_level(self, level):
        """Mandatory method"""
        pass

    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        self.level = level
        self.levelupcount = 0
        self.quizengine.clear()
        return True
    
    def post_next_level(self):
        """Mandatory method.
        This is called once by the core after 'next_level' *and* after the 321 count.
        You should place stuff in here that run in a separate thread like sound play."""
        if self.level == 1:
            self.maxpoints = 2
            self.quizengine.init_exercises(2, self.num_questions,1)
        else:
            self.maxpoints = 4
            self.quizengine.init_exercises(4, self.num_questions, self.level) 
        self.quizengine.next_question()
        
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

    def loop(self,events):
        """Mandatory method.
        This is the main eventloop called by the core 30 times a minute."""
        if self.quizengine.loop(events):
            #print "name", self.get_name(), self.level
            self.SPG.tellcore_level_end(store_db=True)

#        if self.get_name() == 'quiz_math':
#            if self.levelupcount >= int(self.rchash[self.theme]['autolevel_value']):
#                levelup = 1
#                if self.level < 4:
#                    self.SPG.tellcore_level_end(store_db=True,\
#                                        next_level=min(6, self.level + levelup), \
#                                        levelup=levelup)
#                else:
#                    self.SPG.tellcore_game_end(store_db=True)
#        else:
        if self.levelupcount >= int(self.rchash[self.theme]['autolevel_value']):
            levelup = 1
            self.SPG.tellcore_level_end(store_db=True,\
                                        next_level=min(6, self.level + levelup), \
                                        levelup=levelup)
        else:
            if self.levelupcount >= int(self.rchash[self.theme]['autolevel_value']):
                levelup = 1
                self.SPG.tellcore_level_end(store_db=True,\
                                            next_level=min(6, self.level + levelup), \
                                            levelup=levelup)
            
        return 
        
