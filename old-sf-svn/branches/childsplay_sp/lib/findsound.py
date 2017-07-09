
# -*- coding: utf-8 -*-

# Copyright (c) 2008 Stas Zytkiewicz stas.zytkiewicz@gmail.com
#
#           findsound.py
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
# self.logger =  logging.getLogger("schoolsplay.findsound.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("schoolsplay.findsound")

# standard modules you probably need
import os,sys,glob,random

import pygame
from pygame.constants import *

import childsplay_sp.utils as utils
from childsplay_sp.SPConstants import *
import childsplay_sp.SPSpriteUtils as SPSpriteUtils
from childsplay_sp import SPHelpText

# containers that can be used globally to store stuff
class Img:
    pass
class Snd:
    pass
    
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
        self.logger =  logging.getLogger("schoolsplay.findsound.Activity")
        self.logger.info("Activity started")
        self.SPG = SPGoodies
        self.screen = self.SPG.get_screen()
        self.backgr = self.SPG.get_background()
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','FindsoundData')
        self.orgscreen = self.screen.convert()# we use this to restore the screen
        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special SPGroup
        self.actives = SPSpriteUtils.SPInit(self.screen,self.backgr)
        
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
        
    def get_helplevels(self):
        """Mandatory method, must return a string with the number of levels
        in the follwing format:
        _("This level has %s levels" % number-of-levels)"""
        return _("This activity has %s levels") % 6
    
    
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
        pos = (360,400)
        self.soundbutton = SPSpriteUtils.SPButton(img,pos,1)
        
        
    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
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
        # needed to calculate the score
        self.wrongs = 0
        
        # setup the class objects
        self.objects = []
        i, j= 0, 0
        
        for img in self.all_images:
            root, ext = os.path.splitext(os.path.basename(img))
            snd = os.path.join(self.soundlanguagedir,'level'+str(level),root+'.ogg')
            if not os.path.exists(snd):
                self.logger.error("image and sound files don't match, soundfile %s does not exist" % snd)
                raise utils.MyError,"image and sound files don't match"
            obj = ImageObject(utils.load_image(img,1,1),snd)
            obj.display_sprite((i*140+50,j*200+50))
            i += 1
            if i > 3:
                i = 0
                j += 1
            self.objects.append(obj)
        self.soundbutton.display_sprite()
        random.shuffle(self.objects)# See picked_object on why we randomize
        # return True to tell the core were not done yet
        
        return True
        
    def clear_screen(self):
        self.screen.blit(self.orgscreen,(0,0))
        self.backgr.blit(self.orgscreen,(0,0))
        pygame.display.update()    
        
    def picked_object(self):
        try:
            self.selected_object = self.objects.pop()
        except IndexError:
            return 1
        else:
            self.selected_object.play()
            
    def post_next_level(self):
        """Mandatory method.
        This is called by the core after 'next_level' *and* after the 321 count.
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
                        self.SPG.tellcore_level_end(store_db=True)
                else:
                    # wrong object hit
                    self.wrongs += 1
                if self.soundbutton.update(event):
                    # is the soundbutton hit?
                    self.selected_object.play()
        return 
        
