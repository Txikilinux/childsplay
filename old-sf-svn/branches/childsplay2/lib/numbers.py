# -*- coding: utf-8 -*-

# Copyright (c) 2010 chris.formatics.nl
#
#           numbers.py
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
# self.logger =  logging.getLogger("schoolsplay.numbers.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info

module_logger = logging.getLogger("schoolsplay.numbers")

# standard modules you probably need
import os,sys,glob

import pygame
from pygame.constants import *
from random import randint

import utils
from SPConstants import *
import SPSpriteUtils
import SPSpriteUtils as SPSpriteUtils

import SPWidgets

# containers that can be used globally to store stuff
class Img:
    pass
class Snd:
    pass
class Global:
    game_score = 0
    amount_blocks = 0
    counter = 1
    reset_blocks = False
    hint = True
    blocks = []

# Class for the Start/Spiek button
class Button(SPSpriteUtils.SPSprite):
    def __init__(self, datadir, lang):
        self.datadir = datadir
        self.buttonStart = utils.load_image(self.datadir + "/start_%s.png" % lang).convert_alpha()
        self.buttonSpiek = utils.load_image(self.datadir + "/cheat_%s.png" % lang).convert_alpha()
        self.image = self.buttonStart

        SPSpriteUtils.SPSprite.__init__(self,self.image)
        # FIXME: connect to a parent observer
        self.connect_callback(self.callback, event_type=MOUSEBUTTONDOWN)

    def set_default_button(self):
        self.image = self.buttonStart

    # FIXME: remove this global shit and let the parent set the proper state 
    # and update the blocks.
    def callback(self, *args):
        if (Global.hint == True):
            self.image = self.buttonSpiek
            Global.hint = False
        else:
            self.image = self.buttonStart
            Global.hint = True
            if(Global.game_score >= 1):
                Global.game_score -= 1

        for i in range(len(Global.blocks)):
            Global.blocks[i].update_blocks()

class Block(SPSpriteUtils.SPSprite):

    def __init__(self, ID, datadir, goodsound, wrongsound):
        self.id = ID
        self.datadir = datadir
        self.clicked = False
        self.quessed = False
        self.goodsound = goodsound
        self.wrongsound = wrongsound

        # Loading the images needed for blocks
        self.IMG_white = utils.load_image(self.datadir + "/w.png").convert_alpha()
        self.IMG_red = utils.load_image(self.datadir + "/r.png").convert_alpha()
        self.IMG_white_selected = utils.load_image(self.datadir + "/w" + str(self.id) + ".png").convert_alpha()
        self.IMG_green_selected = utils.load_image(self.datadir + "/g" + str(self.id) + ".png").convert_alpha()
        # First image for the block
        self.image = self.IMG_white_selected

        SPSpriteUtils.SPSprite.__init__(self,self.image)
        self.connect_callback(self.callback, event_type=MOUSEBUTTONDOWN)

    # FIXME: the same applies here as above in the Button class
    def update_blocks(self):
        if(self.quessed == True):
            self.image = self.IMG_green_selected
        elif(Global.hint == True):
            self.image = self.IMG_white_selected
        elif(self.clicked == True and self.quessed == False):
            self.image = self.IMG_red
        else:
            self.image = self.IMG_white

    def callback(self, *args):

        if(Global.hint == False):
            Global.blocks_hit += 1
            if(Global.counter == self.id):
                Global.counter += 1
                self.quessed = True
                self.goodsound.play()
                Global.reset_blocks = True
                Global.game_score += 10
                
            elif(self.quessed == False):
                self.wrongsound.play()
                if(Global.game_score >= 20):
                    Global.game_score -= 10
            self.clicked = True
            self.update_blocks()

class Activity:
    """  Base class mandatory for any SP activty.
    The activity is started by instancing this class by the core.
    This class must at least provide the following methods.
    start (self) called by the core before calling 'next_level'.
    post_next_level (self) called once by the core after 'next_level' *and* after the 321 count.
    next_level (self,level) called by the core when the user changes levels.
    loop (self,events) called 40 times a second by the core and should be your main eventloop.
    get_helptitle (self) must return the title of the game can be localized.
    get_help (self) must return a list of strings describing the activty.
    get_helptip (self) must return a list of strings or an empty list
    get_name (self) must provide the activty name in english, not localized in lowercase.
    stop_timer (self) m/ust stop any timers if any.
    """

    def __init__(self,SPGoodies):
        """SPGoodies is a class object that SP sets up and will contain references"""
        self.logger =  logging.getLogger("schoolsplay.numbers.Activity")
        self.logger.info("Activity started")
        self.SPG = SPGoodies
        self.scoredisplay = self.SPG.get_scoredisplay()
        self.theme = self.SPG.get_theme()
        self.screen = self.SPG.get_screen()
        self.screenclip = self.SPG.get_screenclip()
        self.blit_pos = self.screenclip.left, self.screenclip.top
        self.orgscreen = pygame.Surface(self.screenclip.size) # we use this to restore the screen
        self.orgscreen.blit(self.screen, (0, 0), self.screenclip)
        self.backgr = self.SPG.get_background()
        # The location of the activities Data dir
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','NumbersData')
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.CPdatadir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        # Location of the alphabet sounds dir
        self.absdir = self.SPG.get_absdir_path()# alphabet sounds dir
        self.rchash = utils.read_rcfile(os.path.join(self.my_datadir, 'c'))
        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special CPGroup
        self.actives = SPSpriteUtils.SPInit(self.screen,self.backgr)
        self.GoodSound=utils.load_sound(os.path.join(self.CPdatadir, 'good.ogg'))
        self.WrongSound=utils.load_sound(os.path.join(self.CPdatadir, 'wrong.ogg'))
        self.Done=utils.load_sound(os.path.join(self.CPdatadir, 'wahoo.wav'))
        # FIXME:Use os.path.join
        self.playfield_background = utils.load_image(self.my_datadir + "/playfield.png").convert()
        self.lang = self.SPG.get_localesetting()[0][:2]
        self.background_x = 40
        self.background_y = 120
        self.background_width = 720
        self.background_height = 370
        Global.blocks = []
        Global.game_score = 0
        Global.blocks_hit = 0
        self.button = Button(self.my_datadir,self.lang)
        SPSpriteUtils.SPSprite.display_sprite(self.button, (325, 525))

    def clear_screen(self):
        self.screen.blit(self.orgscreen,self.blit_pos)
        self.backgr.blit(self.orgscreen,self.blit_pos)
        pygame.display.update()

    def refresh_sprites(self):
        """Mandatory method, called by the core when the screen is used for blitting
        and the possibility exists that your sprites are affected by it."""
        self.actives.refresh()

    def get_helptitle(self):
        """Mandatory method"""
        return _("Numbers")

    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "numbers"

    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),
        _("Click the buttons in the right order"),
        " "]
        return text

    def get_helptip(self):
        """Mandatory method, when no tips available returns an empty list"""
        return []

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

    def start(self):
        """Mandatory method."""
        self.AreWeDT = False

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

    def pre_level(self,level):
        """Mandatory method.
        Return True to call the eventloop after this method is called."""
        pass

    def get_positions(self):
        list_pos = []
        for i in range(((self.background_width - 10) / 70)):
            for j in range(((self.background_height - 10) / 70)):
                list_pos.append((((i * 70) + self.background_x + 10), (j* 70) + self.background_y + 10))
        return list_pos

    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        self.logger.debug("nextlevel called with: %s" % level)
        if level > 6: return False
        self.level = level
        # Your top blit position, this depends on the menubar position
        if self.blit_pos[1] == 0:
            y = 10
        else:
            y = 110
        Global.blocks_hit = 0
        # Different settings for the levels
        if level < 3:
            self.timer_block = 75
        elif level < 5:
            self.timer_block = 55
        else:
            self.timer_block = 35
            
        # FIXME: remove all this global stuff.
        Global.hint = True

        # Removes the levels from the previous level
        # FIXME: Whats wrong with self.actives.empty ??
        if(len(Global.blocks) > 0):
            # FIXME: this is VB style programming
            for i in range(len(Global.blocks)):
                Global.blocks[i].remove_sprite()

        # Adds the amount of blocks
        Global.amount_blocks = (3 + level)

        # Default level settings
        Global.counter = 1
        Global.reset_blocks = False
        self.show_block = True
        Global.blocks = []

        self.position_list = self.get_positions()

        self.screen.blit(self.playfield_background, (self.background_x, self.background_y))
        pygame.display.update()
        self.backgr.blit(self.playfield_background, (self.background_x, self.background_y))

        for i in range(Global.amount_blocks):
            Global.blocks.append(Block((i + 1), self.my_datadir, self.GoodSound, self.WrongSound))

        self.button.set_default_button()
        self.actives.add(self.button)

        for i in range(len(Global.blocks)):
            random = randint(0, len(self.position_list))
            # FIXME: WTF is this !! I'm curious how one comes up with this solution :-)
            SPSpriteUtils.SPSprite.display_sprite(Global.blocks[i], self.position_list.pop((random - 1)))
            self.actives.add(Global.blocks[i])

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
        m,s = timespend.split(':')
        seconds = int(m)*60 + int(s)
        S = float(int(m)*60 + int(s))
        if Global.game_score < 10:
            Global.game_score = 10
        T = float(Global.amount_blocks)
        K = float(Global.blocks_hit)
        F = 8.0
        F1 = 2.0
        C = 0.3
        C1 = 0.9
        points = F / max( K / T, 1.0 ) ** C1
        time = F1 / max(S / (T / 2), 1.0) ** C
        self.logger.info("@scoredata@ %s level %s T %s K %s S %s points %s time %s" %\
                          (self.get_name(), self.level, T, K, S, points, time))
        score = points + time
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
        # FIXME: remove the global shit and turn it into a proper OO eventloop.
        myevent = None

        for event in events:
            if event.type is MOUSEBUTTONDOWN:
                myevent = event
                self.actives.refresh(myevent)
                self.scoredisplay.set_score(Global.game_score)

        # Resetting the blocks
        if(Global.reset_blocks == True):
            for i in range(len(Global.blocks)):
                Global.blocks[i].clicked = False
                Global.blocks[i].update_blocks()

                Global.reset_blocks = False

        for i in range(len(Global.blocks)):
            Global.blocks[i].update_blocks()

        self.actives.refresh()

        # Game is done when the counter reach the amount of blocks plus 1
        # And will restart the level
        if((Global.amount_blocks + 1) == Global.counter):
            self.Done.play()
            pygame.time.wait(1000)
            if self.AreWeDT:
                self.SPG.tellcore_level_end()
            else:
                self.SPG.tellcore_level_end(store_db=True)

        return

