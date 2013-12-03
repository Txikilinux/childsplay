# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zytkiewicz stas.zytkiewicz@schoolsplay.org
#
#           wipe.py
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
# self.logger =  logging.getLogger("childsplay.wipe.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("childsplay.wipe")

# standard modules you probably need
import os,sys, glob, random

import pygame
from pygame.constants import *

import utils
from SPConstants import *
import SPSpriteUtils
import SPWidgets

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
        self.logger =  logging.getLogger("childsplay.wipe.Activity")
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
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','WipeData')
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.CPdatadir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        # Location of the alphabet sounds dir
        self.absdir = self.SPG.get_absdir_path()# alphabet sounds dir
        self.rchash = utils.read_rcfile(os.path.join(self.my_datadir, 'wipe.rc'))
        self.logger.debug("rchash: " + str(self.rchash))
        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special CPGroup
        self.actives = SPSpriteUtils.SPInit(self.screen,self.backgr)
        self.newbutton = SPWidgets.ButtonRound(_("New"), (300, 560), fgcol=WHITE, \
                                                     fsize=18, sizename='small')
        self.newbutton.connect_callback(self._cbf_new, MOUSEBUTTONDOWN)
                
    def _cbf_new(self, *args):
        self.next_exercise()

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
        return _("Wipe")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "wipe"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),
        " ",
        _("Wipe with your finger on the screen to uncover the picture."),
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
    
    def start(self):
        """Mandatory method."""
        pass
        
    
    def get_helplevels(self):
        """Mandatory method, must return a string with the number of levels
        in the follwing format:
        _("This level has %s levels") % number-of-levels"""
        return _("This activity has %s levels") % 1
    
    def pre_level(self,level):
        """Mandatory method.
        Return True to call the eventloop after this method is called."""
        self.logger.debug("pre_level called with: %s" % level)
        self.SPG.tellcore_disable_score_button()
        self.SPG.tellcore_disable_level_indicator()
        self.level = level
        self.pre_level_flag = True
        self.grepwiper = False
        if self.blit_pos[1] == 0:
            y = 10
        else:
            y = 110
        x = 100
        img = utils.load_image(glob.glob(os.path.join(self.my_datadir,'sponge.png'))[0])
        #img = pygame.Surface((60, 60))
        self.wiper = SPSpriteUtils.SPSprite(img)
        files = glob.glob(os.path.join(self.my_datadir,'tileset_*.png'))
        files.sort()
        lbl = SPWidgets.Label(_("Please, choose a set of images."),\
                                (80, y),fsize=24, transparent=True)
        lbl.display_sprite()
#        y += lbl.get_sprite_height()
#        for line in textwrap.wrap(_("The difficulty of the set increases from left to right."), 40):
#            lbl = SPWidgets.Label(line,(30, y), fsize=24, transparent=True)
#            lbl.display_sprite()
#            y += lbl.get_sprite_height()
        y += 50
        for tilepath in files:
            img = utils.load_image(tilepath)
            data = os.path.splitext(os.path.split(tilepath)[1])[0]
            b = SPWidgets.SimpleButton(img, (x, y), data=data)
            b.display_sprite()
            self.actives.add(b)
            x += 150
        return True
        
    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        self.logger.debug("nextlevel called with: %s" % level)
        # Your top blit position, this depends on the menubar position 
        if self.blit_pos[1] == 0:
            self.y = 0
        else:
            self.y = 100
        self.SPG.tellcore_disable_score_button()
        self.SPG.tellcore_disable_level_indicator()
        self.files = glob.glob(os.path.join(self.my_datadir,self.tile, '*.jpg'))
        random.shuffle(self.files)
        self.coverfiles = glob.glob(os.path.join(self.my_datadir,'overlay_*.png'))
        random.shuffle(self.coverfiles)
        
        self.next_exercise()
        return True
    
    def next_exercise(self):
        self.logger.debug("next_exercise called")
        self.clear_screen()
        self.actives.empty()
        # The maximum size for a image can be 800x450 so all images must be smaller.
         
        self.grepwiper = False
        if not self.files:
            self.files = glob.glob(os.path.join(self.my_datadir,self.tile,'*.jpg'))
            random.shuffle(self.files)
        img = utils.load_image(self.files.pop()).convert_alpha()
        r = img.get_rect()
        self.backgr.blit(img, ((800-r.w)/2 , self.y + (450-r.h)/2))
        if not self.coverfiles:
            self.coverfiles = glob.glob(os.path.join(self.my_datadir,'overlay_*.png'))
            random.shuffle(self.coverfiles)
        self.wipe_field = self.screen.blit(img, ((800-r.w)/2 , self.y + (450-r.h)/2))
        cover = utils.load_image(self.coverfiles.pop())
        self.screen.blit(cover, self.wipe_field.topleft, (0, 0) + self.wipe_field.size)
        pygame.display.update()
        self.actives.add(self.wiper)
        self.wiper.display_sprite((350, 350))
        self.actives.add(self.newbutton)
        self.newbutton.display_sprite()
    
    def dailytraining_pre_level(self, level):
        """Mandatory method"""
        pass
        
    def dailytraining_next_level(self, level, dbmapper):
        """Mandatory method.
        This should handle the DT logic"""
        pass
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
            if event.type is MOUSEBUTTONDOWN:
                # were in prelevel loop
                if self.pre_level_flag:
                    result = self.actives.update(event)
                    if result:
                        self.logger.debug("loop, got a result and stop this loop")
                        self.SPG.tellcore_pre_level_end()
                        self.pre_level_flag = False
                        self.tile = result[0][1][0]
                        break
                    break
                if self.grepwiper:
                    self.grepwiper = False
                    break
                else:
                    self.grepwiper = True
            elif event.type is MOUSEBUTTONUP:
                if self.grepwiper:
                    self.grepwiper = False
                    break
            elif event.type is MOUSEMOTION and self.grepwiper:
                self.screen.set_clip(self.wipe_field)
                self.wiper.moveto((event.pos[0], event.pos[1]), hide=False)
                self.screen.set_clip(None)
            self.actives.update(event)
        return 
        
