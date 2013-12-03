# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zytkiewicz stas.zytkiewicz@schoolsplay.org
#
#           quiz.py
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

# Super class for the quiz acts

#create logger, logger was setup in SPLogging
import logging

module_logger = logging.getLogger("childsplay.quiz_knowledge")

# standard modules you probably need
import os,sys

import pygame
from pygame.constants import *

import utils
from SPConstants import *
import SPSpriteUtils

# needed to import quizengine
#sys.path.insert(0, './lib')
from quizengine import Engine

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
        self.logger =  logging.getLogger("childsplay.quiz.Activity")
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
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','Quiz_Data')
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.CPdatadir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        self.rchash = utils.read_rcfile(os.path.join(self.my_datadir, 'quiz.rc'))
        self.rchash['theme'] = self.theme
        self.rchash['lang'] = self.lang
        self.logger.debug("found rc: %s" % self.rchash)
        p = os.path.join(self.CPdatadir,'good_%s.png' % self.lang)
        if not os.path.exists(p):
            p = os.path.join(self.CPdatadir,'thumbs.png')
        self.ThumbsUp = SPSpriteUtils.MySprite(utils.load_image(p))
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.CPdatadir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        # Location of the alphabet sounds dir
        self.absdir = self.SPG.get_absdir_path()# alphabet sounds dir
        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special CPGroup
        self.actives = SPSpriteUtils.SPInit(self.screen,self.backgr)
          
        self.num_questions = int(self.rchash[self.theme]['questions'])
        self.AreWeDT = False
            
    def stop_sound(self):
        """Called by the core when the audio needs to stopped"""
        try:
            self.quizengine.stop_sound()
        except:
            pass
    
    def quiz_voice_changed(self,state):
        """Called by the core when the quiz voice audio setting is changed"""
        self.quizengine.unmute_exer_audio = state
    
    def observer(self, result):
        self.logger.debug("observer called with: %s" % result)
        if result > 0:
            self.levelupcount += 1
            self.score += int(result)
        else:
            self.levelupcount -= 1
        # here we pause between questions
        pygame.time.wait(1000)
        pygame.event.clear()
        
    def clear_screen(self):
        self.screen.blit(self.orgscreen,self.blit_pos)
        self.backgr.blit(self.orgscreen,self.blit_pos)
        pygame.display.update()

    def get_moviepath(self):
        movie = os.path.join(self.my_datadir,'help.avi')
        return movie

    def refresh_sprites(self):
        """Mandatory method, called by the core when the screen is used for blitting
        and the possibility exists that your sprites are affected by it."""
        self.actives.redraw()

    def get_helptitle(self):
        """Mandatory method"""
        return _("Quiz")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "quiz"
    
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
        self.SPG.tellcore_set_dice_minimal_level(1)
    
    def pre_level(self, level):
        """Mandatory method"""
        pass

    def dailytraining_pre_level(self, level):
        """Mandatory method"""
        pass

    def dailytraining_next_level(self, level, dbmapper):
        """Mandatory method.
        This should handle the DT logic"""
        self.AreWeDT = True
        self.num_questions = int(self.rchash[self.theme]['dt_questions'])
        self.next_level(level, dbmapper)
        return True

    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        # TODO: what about the mapper ? we don't put total_questions nor total_wrongs in it
        self.level = level
        self.levelupcount = 1
        self.quizengine.clear()
        self.score = 0# this is score for dbase which are stored per level
        self.dbmapper = dbmapper
        return True
    
    def post_next_level(self):
        """Mandatory method.
        This is called once by the core after 'next_level' *and* after the 321 count.
        You should place stuff in here that run in a separate thread like sound play."""
        self.dbmapper.insert('total_questions', self.num_questions)
        if self.level in (1, 2):
            self.maxpoints = 2
            self.quizengine.init_exercises(2, self.num_questions,self.level, self.AreWeDT)
        else:
            self.maxpoints = 4
            self.quizengine.init_exercises(4, self.num_questions, self.level, self.AreWeDT) 
        self.quizengine.next_question()
        
    def get_score(self,timespend):
        """Mandatory method.
        @timespend is the time spend inside the level as it's calculated
        by the core.
        returns the score value for the past level.
        return None if no score value is used"""
        m,s = timespend.split(':')
        seconds = int(m)*60 + int(s)
        
        N = float(self.num_questions)
        M = float(self.maxpoints)
        P = float(self.score)
        F = 7.0
        F1 = 3.0
        C = 0.2
        S = float(seconds)
        # N = Number of questions
        # M = maximum points per question
        # P = Users result in points
        # F = Fraction of total result related to points. (maximum result is 10)
        # F1 = Fraction of result related to time
        # C = multiplier
        # S = time spend in seconds
        points = max((F/100) * (P/(N*M/100)), 1.0)
        time = min(F1 / ((S/(N*2)) ** C), F1)
        self.logger.info("@scoredata@ %s level %s N %s P %s M %s S %s points %s time %s" %\
                          (self.get_name(),self.level, N, P,M, S, points, time))
        score = points + time
        result = points + time
        return result
    
    def stop_timer(self):
        """You *must* provide a method to stop timers if you use them.
        The SPC will call this just in case and catch the exception in case 
        there's no 'stop_timer' method""" 
        try:
            self.timer.stop()
        except:
            pass
        try:
            self.quizengine.stop_timers()
        except:
            pass

    def loop(self,events):
        """Mandatory method.
        This is the main eventloop called by the core 30 times a minute."""
        if self.quizengine.loop(events):
            #print "name", self.get_name(), self.level        
            if not self.AreWeDT:
                self.clear_screen()
                self.dbmapper.insert('total_wrongs', self.quizengine.get_totalwrongs())
#                self.ThumbsUp.display_sprite((229, 296))
#                pygame.time.wait(1500)
#                self.ThumbsUp.erase_sprite()
                if self.levelupcount >= int(self.rchash[self.theme]['autolevel_value']):
                    levelup = 1
                    self.SPG.tellcore_level_end(store_db=True,\
                                                level=min(6, self.level), \
                                                levelup=levelup)
                else:
                    self.SPG.tellcore_level_end(store_db=True, level=self.level)
            else:
                self.SPG.tellcore_level_end(store_db=False, level=self.level)
            
        return 
        
