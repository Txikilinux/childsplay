
# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zytkiewicz stas.zytkiewicz@schoolsplay.org
#
#           numbers_sp.py
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

#create logger, logger was setup in SPLogging
import logging
# In your Activity class -> 
# self.logger =  logging.getLogger("childsplay.numbers_sp.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("childsplay.numbers_sp")

# standard modules you probably need
import os,sys
import random
import pygame
from pygame.constants import *

import utils
from SPConstants import *
import SPSpriteUtils
import SPWidgets

class Block(SPSpriteUtils.SPSprite):
    def __init__(self, ID, pos, white_img, white, green_img, red):
        self.ID = ID
        self.white_img = white_img
        self.white = white
        self.green_img = green_img
        self.red = red
        self.current_state = 'show'
        SPSpriteUtils.SPSprite.__init__(self, self.white)
        self.moveto(pos)
        
    def state_show(self):
        self.erase_sprite()
        self.image = self.white_img
        self.current_state = 'show'
        self.display_sprite()
    def state_closed(self):
        self.erase_sprite()
        self.image = self.white
        self.current_state = 'closed'
        self.display_sprite()
    def state_wrong(self):
        self.erase_sprite()
        self.image = self.red
        self.current_state = 'wrong'
        self.display_sprite()
    def state_good(self):
        self.erase_sprite()
        self.image = self.green_img
        self.current_state = 'good'
        self.display_sprite()
        
    def get_id(self):
        return self.ID

class BlockMaster:
    def __init__(self, datadir, actives, goodsnd, wrongsnd, observer):
        self.actives = actives
        self.datadir = datadir
        self.good = goodsnd
        self.wrong = wrongsnd
        self.observer = observer
        self.red = utils.load_image(os.path.join(datadir, 'r.png'))
        self.white = utils.load_image(os.path.join(datadir, 'w.png'))
        self.errors = 0
        self.totalblocks = 0
        
    def init(self, numbers, positions):
        self.totalblocks += len(numbers)
        self.blocklist = []
        for i in numbers:
            wimg = utils.load_image(os.path.join(self.datadir, 'w%s.png' % i))
            gimg = utils.load_image(os.path.join(self.datadir, 'g%s.png' % i))
            b = Block(i, positions[i-1], wimg, self.white, gimg, self.red)
            self.blocklist.append(b)
            b.connect_callback(self._cbf_block, MOUSEBUTTONDOWN, i)
        self.currentID = 1
    
    def show_all(self):
        self.actives.remove(self.blocklist)
        for b in self.blocklist:
            b.state_show()
            
    def close_all(self):
        for b in self.blocklist:
            b.state_closed()
        self.actives.add(self.blocklist)

    def _close_wrongs(self):
        for b in self.blocklist:
            if b.current_state == 'wrong':
                b.state_closed()

    def finished(self):
        return self.blocklist == []

    def get_errors(self):
        return self.errors

    def get_num_blocks(self):
        return self.totalblocks

    def _cbf_block(self, widget, event, data):
        ID = data[0]
        if self.currentID != ID:
            self.errors += 1
            self.wrong.play()
            widget.state_wrong()
            self.observer(-1)
        else:
            self.good.play()
            widget.state_good()
            self.blocklist.remove(widget)
            self.actives.remove(widget)
            self._close_wrongs()
            self.currentID = ID + 1
            self.observer(1)

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
        self.logger =  logging.getLogger("childsplay.numbers_sp.Activity")
        self.logger.info("Activity started")
        self.SPG = SPGoodies
        self.lang = self.SPG.get_localesetting()[0][:2]
        self.scoredisplay = self.SPG.get_scoredisplay()
        self.theme = self.SPG.get_theme()
        self.screen = self.SPG.get_screen()
        self.screenclip = self.SPG.get_screenclip()
        self.blit_pos = self.screenclip.left, self.screenclip.top
        self.orgscreen = pygame.Surface(self.screenclip.size) # we use this to restore the screen
        self.orgscreen.blit(self.screen, (0, 0), self.screenclip)
        self.backgr = self.SPG.get_background()
        # The location of the activities Data dir
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','Numbers_spData')
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.CPdatadir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        # Location of the alphabet sounds dir
        self.absdir = self.SPG.get_absdir_path()# alphabet sounds dir
        self.rchash = utils.read_rcfile(os.path.join(self.my_datadir, 'numbers_sp.rc'))
        self.logger.debug("rchash: " + str(self.rchash))
        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special CPGroup
        self.actives = SPSpriteUtils.SPInit(self.screen,self.backgr)
        
        self.GoodSound=utils.load_sound(os.path.join(self.CPdatadir, 'good.ogg'))
        self.WrongSound=utils.load_sound(os.path.join(self.CPdatadir, 'wrong.ogg'))
        self.Done=utils.load_sound(os.path.join(self.CPdatadir, 'wahoo.wav'))
        
        b = os.path.join(self.CPdatadir, '200px_80px_blue.png')
        b_ro = os.path.join(self.CPdatadir, '200px_80px_black.png')
        self.beginbut = SPWidgets.TransImgButton(b, b_ro, \
                                    (300, 510), fsize=24, text= _("Begin"),\
                                    fcol=WHITE)
        self.beginbut.connect_callback(self._cbf_begin, MOUSEBUTTONDOWN)
        self.cheatbut = SPWidgets.TransImgButton(b, b_ro, \
                                    (300, 510), fsize=24, text= _("Cheat"),\
                                    fcol=WHITE)
        self.cheatbut.connect_callback(self._cbf_cheat, MOUSEBUTTONDOWN)
        self.playfield = utils.load_image(os.path.join(self.my_datadir, "playfield.png")).convert()
        self.playfield_position = (40, 120)
        self.list_pos = []
        r = self.playfield.get_rect()
        x, y = self.playfield_position
        for i in range(((r.w - 10) / 70)):
            for j in range(((r.h - 10) / 70)):
                self.list_pos.append(((i * 70) + x + 10, (j* 70) + y + 10))
                    
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
        self.actives.refresh()

    def get_helptitle(self):
        """Mandatory method"""
        return _("Numbers_sp")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "numbers_sp"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),
        _("You will see various numbers scattered around the screen."),
        " ", 
        _("Look carefully and try to remember their positions on the screen."), 
        _("Then push the 'BEGIN' button. The numbers will disappear."),
        _("Try to find the numbers, in the correct order and from low to high, by touching them on the screen."), 
        " "]
        return text
            
    def get_helptip(self):
        """Mandatory method, when no tips available returns an empty list"""
        return _("Correctness is more important than speed.")
        
    def get_helptype(self):
        """Mandatory method, you must set an type"""
        # Possible types are: Memory, Math, Puzzle, Keyboardtraining, Mousetraining
        #                     Language, Alphabet, Fun, Miscellaneous
        return _("Miscellaneous")
    
    def start(self):
        """Mandatory method."""
        self.AreWeDT = False
        
    def get_helplevels(self):
        """Mandatory method, must return a string with the number of levels
        in the follwing format:
        _("This level has %s levels") % number-of-levels"""
        return _("This activity has %s levels") % 6
    
    def pre_level(self,level):
        """Mandatory method.
        Return True to call the eventloop after this method is called."""
        self.logger.debug("pre_level called with: %s" % level)
        pass
        
    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        self.logger.debug("nextlevel called with: %s" % level)
        self.level = level
        # number of exercises in one level
        if self.AreWeDT:
            self.exercises = 1
        else:
            self.exercises = int(self.rchash[self.theme]['exercises'])
        self.WEcheat = 0
        self.levelrestartcounter = 0
        self.numblocks = 3 + self.level
        self.totalblocks = 0
        self.blocksclicked = 0
        self.BM = BlockMaster(self.my_datadir, self.actives, \
                              self.GoodSound, self.WrongSound, self._observer)
        self.next_exercise()
        return True
        
    def _cbf_begin(self, *args):
        self.beginbut.erase_sprite()
        self.actives.remove(self.beginbut)
        self.cheatbut.display_sprite()
        self.actives.add(self.cheatbut)
        self.BM.close_all()

    def _cbf_cheat(self, *args):
        self.WEcheat += 1
        self.cheatbut.erase_sprite()
        self.actives.remove(self.cheatbut)
        self.beginbut.display_sprite()
        self.actives.add(self.beginbut)
        self.BM.show_all()

    def next_exercise(self):
        if not self.exercises:
            return True
        self.exercises -= 1
        self.levelrestartcounter += 1
        self.cheatbut.erase_sprite()
        self.actives.empty()
        self.actives.add(self.beginbut)
        
        x, y = self.playfield_position
        playfield = utils.load_image(os.path.join(self.my_datadir, "playfield.png")).convert()
        self.screen.blit(playfield, (x, y))
        pygame.display.update()
        self.backgr.blit(playfield, (x, y))
        self.BM.init(range(1, 4 + self.level), random.sample(self.list_pos, self.numblocks))
        self.BM.show_all()
        self.totalblocks += self.numblocks
        self.beginbut.display_sprite()

    def _observer(self, score):
        if score < 0:
            score = score * 10
        else:
            score = score * 15
        self.scoredisplay.increase_score(score)

    def dailytraining_pre_level(self, level):
        """Mandatory method"""
        pass
        
    def dailytraining_next_level(self, level, dbmapper):
        """Mandatory method.
        This should handle the DT logic"""
        self.AreWeDT = True
        self.SPG.tellcore_disable_level_indicator()
        self.next_level(level, dbmapper)
        return True       
        
    def post_next_level(self):
        """Mandatory method.
        This is called once by the core after 'next_level' *and* after the 321 count.
        You should place stuff in here that run in a seperate thread like sound play."""
        pass 
        
    def get_score(self,timespend):
        """Mandatory method.
        @timespend is the time spend inside the level as it's calculated
        by the core.
        returns the score value for the past level.
        return None if no score value is used"""
        # T = Total blocks
        # K = Blocks clicked. (a perfect game K == T)
        # F = Fraction of total result related to points. (maximum result is 10)
        # F1 = Fraction of result related to time
        # C = multiplier
        # S = time spend in seconds
        try:
            T = float(self.totalblocks)
            K = float(self.BM.get_errors() + T + self.WEcheat)
        except AttributeError:
            return None
        m,s = timespend.split(':')
        S = float(int(m)*60 + int(s))
        F = 7.0
        F1 = 3.0
        C = 0.6
        C1 = 2.1
        points = F / max( K / T, 1.0 ) ** C1
        time = F1 / max(S / T , 1.0) ** C
        self.logger.info("@scoredata@ %s level %s T %s K %s S %s points %s time %s" % \
                         (self.get_name(), self.level, T, K, S, points, time))
        score = points + time
        return score
        
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
        for event in events:
            if event.type in (MOUSEBUTTONDOWN, MOUSEMOTION):
                self.actives.update(event)
        if self.BM.finished():
            self.Done.play()
            pygame.time.wait(2000)
            self.clear_screen()
            if self.next_exercise():
                if self.levelrestartcounter >= int(self.rchash[self.theme]['autolevel_value']):
                    levelup = 1
                if self.AreWeDT:
                    self.SPG.tellcore_level_end(level=self.level)
                else:
                    self.SPG.tellcore_level_end(store_db=True, \
                                        level=min(6, self.level), \
                                                    levelup=levelup)
        return 
        
