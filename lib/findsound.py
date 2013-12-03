
# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zytkiewicz stas.zytkiewicz@schoolsplay.org
#
#           findsound.py
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
# self.logger =  logging.getLogger("childsplay.findsound.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("childsplay.findsound")

# standard modules you probably need
import os,sys,glob,random

import pygame
from pygame.constants import *

import utils
from SPConstants import *
import SPSpriteUtils
import SPHelpText

class ImageObject(SPSpriteUtils.SPSprite):
    def __init__(self,img,snd):
        self.image = img
        self.rect = self.image.get_rect()
        SPSpriteUtils.SPSprite.__init__(self,self.image)
        self.sound = snd
        self.connect_callback(self.callback, event_type=MOUSEBUTTONDOWN)
        
    def set_position(self,pos):
        self.rect.move_ip(pos)
    
    def play(self):
        utils.load_music(self.sound).play(1)
        
    def callback(self,*args):
        """If this is called the user hits the right image."""
        self.erase_sprite()
        #return true to signal that were removed
        return True
        

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
        self.logger =  logging.getLogger("childsplay.findsound.Activity")
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
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','FindsoundData')
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.CPdatadir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        # Location of the alphabet sounds dir
        self.absdir = self.SPG.get_absdir_path()# alphabet sounds dir
        self.rchash = utils.read_rcfile(os.path.join(self.my_datadir, 'findsound.rc'))
        self.logger.debug("rchash: " + str(self.rchash))
        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special CPGroup
        self.actives = SPSpriteUtils.SPInit(self.screen,self.backgr)
                
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
        return _("Findsound")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "findsound"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),
        _("Listen to the sound and click on the image to which it belongs."),
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
        if not pygame.mixer.get_init():
            self.logger.error("No sound card found or not available")
            self.SPG.tellcore_info_dialog(_(SPHelpText.CP_find_char_sound.ActivityStart))
            raise utils.MyError(SPHelpText.CP_find_char_sound.ActivityStart)
        self.soundlanguagedir = os.path.join(self.my_datadir,'Sounds')
        self.imagelanguagedir = os.path.join(self.my_datadir,'Images')
        img = utils.load_image(os.path.join(self.SPG.get_libdir_path(),\
                                        'CPData','soundbut.png'),1)
        pos = (360,500)
        self.soundbutton = SPSpriteUtils.SPButton(img,pos,1)
    
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
        # Your top blit position, this depends on the menubar position 
        if self.blit_pos[1] == 0:
            y = 10
        else:
            y = 110
        if level == 7:
            return False
        # db_mapper is a Python class object that provides easy access to the 
        # dbase.
        self.db_mapper = dbmapper
        # make sure we don't have objects left in the actives group.
        self.actives.empty()
        # reset the screen to clear any crap from former levels
        self.clear_screen()
        # load images for the apropriate level
        self.all_images = glob.glob(os.path.join(self.imagelanguagedir,'level'+str(level),'*.png'))
        self.level = level
        # needed to calculate the score
        self.wrongs = 0
        
        # setup the class objects
        self.objects = []
        x = 30
        i = 0
        for img in self.all_images:
            root, ext = os.path.splitext(os.path.basename(img))
            snd = os.path.join(self.soundlanguagedir,'level'+str(level),root+'.ogg')
            if not os.path.exists(snd):
                self.logger.error("image and sound files don't match, soundfile %s does not exist" % snd)
                raise utils.MyError,"image and sound files don't match"
            obj = ImageObject(utils.load_image(img),snd)
            obj.display_sprite((x,y))
            i += 1
            x += obj.get_sprite_width() + 50
            if i > 3:
                i = 0
                y += obj.get_sprite_height() + 50
                x = 30
            self.objects.append(obj)
        self.soundbutton.display_sprite()
        random.shuffle(self.objects)# See picked_object on why we randomize
        
        return True
        
    def picked_object(self):
        try:
            self.selected_object = self.objects.pop()
        except IndexError:
            return 1
        else:
            self.selected_object.play()

    
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
        # this is the object that must be found, when the user clicks on it
        # we pick another
        # This is placed here because it also plays a sound
        self.selectedobject = self.picked_object()      
        
    def get_score(self,timespend):
        """Mandatory method.
        @timespend is the time spend inside the level as it's calculated
        by the core.
        returns the score value for the past level.
        return None if no score value is used"""
        m,s = timespend.split(':')
        seconds = int(m)*60 + int(s)
        score = max(1,((10-self.wrongs)-seconds/100.0))
        self.logger.debug("score is: %s" % score)
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
            if event.type is MOUSEBUTTONDOWN:
                if self.selected_object.update(event):
                    # if the object returns True it's hit by the user and we
                    # pick another object
                    if self.picked_object():
                        # we call the SPGoodies observer to notify the core the level
                        # is ended and we want to store the collected data
                        self.SPG.tellcore_level_end(store_db=True, \
                                                next_level=min(6, self.level + 1), \
                                                levelup=True)
                else:
                    # wrong object hit
                    self.wrongs += 1
                if self.soundbutton.update(event):
                    # is the soundbutton hit?
                    self.selected_object.play()
        return 
        
