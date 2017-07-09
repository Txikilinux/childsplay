# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zytkiewicz stas.zytkiewicz@gmail.com
#
#           quiz_history.py
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
# self.logger =  logging.getLogger("schoolsplay.quiz_history.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("schoolsplay.quiz_history")

# standard modules you probably need
import os,sys
# needed to import quiz
sys.path.insert(0, './lib')

import pygame
from pygame.constants import *

import utils
from SPConstants import *
import SPSpriteUtils
import SPWidgets
import quiz_text

#from SPVirtkeyboard import KeyBoard

from virtnumpad import VirtualNumpad, QuitException
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
        self.logger =  logging.getLogger("schoolsplay.quiz_history.Activity")
        self.logger.info("Activity started")
        quiz_text.Activity.__init__(self, SPGoodies)
        
        # The location of the activities Data dir (override the super class attributes)
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','Quiz_historyData')
        self.background_keyboard = utils.load_image(os.path.join(self.my_datadir,'background_keyboard.png'))
        self.rchash = utils.read_rcfile(os.path.join(self.my_datadir, 'quiz_history.rc'))
        self.rchash['theme'] = self.theme
        lang = self.SPG.get_localesetting()[0][:2]
        self.screenclip = self.SPG.get_screenclip()
        self.blit_pos = self.screenclip.left, self.screenclip.top
        if self.blit_pos[1] == 0:
            y = 10
        else:
            y = 110
        # setup icons fro prelevel
        pos = [(20, 20+y), (240, 20+y), (460, 20+y), \
               (20, 240+y), (240, 240+y), (460, 240+y)]
        self.prelevel_buttons = []
        img = utils.load_image(os.path.join(self.my_datadir, '30s.png'))
        rop =  os.path.join(self.my_datadir, '30s_ro.png')
        if os.path.exists(rop):
            img_ro = utils.load_image(rop)
        else:
            img_ro = None
        but = SPWidgets.TransImgButton(img, img_ro, pos[0], name='30')
        but.connect_callback(self._prelevel_cbf, MOUSEBUTTONDOWN, 30)
        self.prelevel_buttons.append(but)
        
        img = utils.load_image(os.path.join(self.my_datadir, '40s.png'))
        rop =  os.path.join(self.my_datadir, '40s_ro.png')
        if os.path.exists(rop):
            img_ro = utils.load_image(rop)
        else:
            img_ro = None
        but = SPWidgets.TransImgButton(img, img_ro, pos[1], name='40')
        but.connect_callback(self._prelevel_cbf, MOUSEBUTTONDOWN, 40)
        self.prelevel_buttons.append(but)
        
        img = utils.load_image(os.path.join(self.my_datadir, '50s.png'))
        rop = os.path.join(self.my_datadir, '50s_ro.png')
        if os.path.exists(rop):
            img_ro = utils.load_image(rop)
        else:
            img_ro = None
        but = SPWidgets.TransImgButton(img, img_ro, pos[2], name='50')
        but.connect_callback(self._prelevel_cbf, MOUSEBUTTONDOWN, 50)
        self.prelevel_buttons.append(but)
        
        img = utils.load_image(os.path.join(self.my_datadir, '60s.png'))
        rop =  os.path.join(self.my_datadir, '60s_ro.png')
        if os.path.exists(rop):
            img_ro = utils.load_image(rop)
        else:
            img_ro = None
        but = SPWidgets.TransImgButton(img, img_ro, pos[3], name='60')
        but.connect_callback(self._prelevel_cbf, MOUSEBUTTONDOWN, 60)
        self.prelevel_buttons.append(but)
        
        img = utils.load_image(os.path.join(self.my_datadir, '70s.png'))
        rop = os.path.join(self.my_datadir, '70s_ro.png')
        if os.path.exists(rop):
            img_ro = utils.load_image(rop)
        else:
            img_ro = None
        but = SPWidgets.TransImgButton(img, img_ro, pos[4], name='70')
        but.connect_callback(self._prelevel_cbf, MOUSEBUTTONDOWN, 70)
        self.prelevel_buttons.append(but)
        
        img = utils.load_image(os.path.join(self.my_datadir, lang,'age.png'))
        rop =  os.path.join(self.my_datadir, lang, 'age_ro.png')
        if os.path.exists(rop):
            img_ro = utils.load_image(rop)
        else:
            img_ro = None
        but = SPWidgets.TransImgButton(img, img_ro, pos[5], name='age')
        but.connect_callback(self._prelevel_cbf, MOUSEBUTTONDOWN, 'age')
        self.prelevel_buttons.append(but)
        
    def _start_engine(self):
        self.quizengine = quiz_text.Engine(['history'], self.SPG, self.observer)
    
    def start(self):
        """Mandatory method."""
        self._start_engine()
        self.quizengine.set_retry(int(self.rchash[self.theme]['retry']))
        self.SPG.tellcore_set_dice_minimal_level(5)

    def pre_level(self, level):
        """Mandatory method"""
        self.logger.debug("pre_level called with: %s" % level)
        self.SPG.tellcore_disable_level_indicator()
        self.pre_level_flag = True       
        for b in self.prelevel_buttons:
            b.display_sprite()
        self.actives.add(self.prelevel_buttons)    
        return True

    def _prelevel_cbf(self, sprite, event, data):
        self.logger.debug("_prelevel_cbf called with %s" % data)
        kind = data[0]
        for b in self.prelevel_buttons:
            b.erase_sprite()
        self.actives.remove(self.prelevel_buttons) 
        if kind != 'age':
            self.year = kind + 1900
            self.logger.debug("setting year to %s" % self.year)
            return True
        else:
            self.screen.blit(self.background_keyboard, (160,140))
            # short pause to prevent that users who dubbelclick on the menu icon don 't blame me
            # when their second click start enter key at the numpad.
            pygame.time.wait(500) 
            vnp = VirtualNumpad()
            try:
                year = int(vnp.run(self.screen, "", layout=1, quitrect=self.SPG.get_quitbutton_rect()))
            except QuitException:
                self.logger.debug("User hits the exit button in pre_level")
                # this is the only way to quit outside the eventloop
                self.SPG.tellcore_game_end()
            year += 1900
            if not year or year < 1912:
                year = 1912
            if year > 1957:
                year = 1957
            self.year = year + 18
        self.logger.debug("setting year to %s" % self.year)
        return True
        
    def post_next_level(self):
        """Mandatory method.
        This is called once by the core after 'next_level' *and* after the 321 count.
        You should place stuff in here that run in a separate thread like sound play."""
        if self.level == 1:
            self.maxpoints = 2
            self.quizengine.init_exercises(2, 0, 1, self.year)
        else:
            self.maxpoints = 4
            self.quizengine.init_exercises(4, 0, 1, self.year) 
        self.quizengine.next_question()

    def get_helptitle(self):
        """Mandatory method"""
        return _("Quiz history")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "quiz_history"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),
                 _("Answer the quiz questions."), 
        " ",
        _("At the top of the screen, you will see a question from general knowledge question from the selected period."),
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
        return _("This activity has %s levels") % 2

    def loop(self,events):
        """Mandatory method.
        This is the main eventloop called by the core 30 times a minute."""
        # we override the loop in our parent so we must make the proper calls ourselfs
        if not self.pre_level_flag:
            if self.quizengine.loop(events):
                #print "name", self.get_name(), self.level
                self.SPG.tellcore_level_end(store_db=True)
            else:
                if self.levelupcount >= int(self.rchash[self.theme]['autolevel_value']):
                    levelup = 1
                    self.SPG.tellcore_level_end(store_db=True,\
                                                next_level=min(6, self.level + levelup), \
                                                levelup=levelup)
        else:
            for event in events:
                if event.type in (MOUSEBUTTONDOWN, MOUSEMOTION):
                    result = self.actives.update(event)
                    if result:
                        self.logger.debug("loop, got a result and stop this loop")
                        self.SPG.tellcore_pre_level_end()
                        self.pre_level_flag = False
                        self.SPG.tellcore_enable_level_indicator()
                        break
        return 
