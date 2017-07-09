
# -*- coding: utf-8 -*-

# Copyright (c) 2008 Stas Zytkiewicz stas.zytkiewicz@gmail.com
#
#           soundmemory.py
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
# self.logger =  logging.getLogger("schoolsplay.soundmemory.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("schoolsplay.soundmemory")

# standard modules you probably need
import os,sys,random,glob

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
class Global:
    """ Container to store all kind of stuff"""
    pass
    
##NOSOUNDTXT = """It seems that we cannot use the sound card right now and because this game
##  is all about sound, we just quit.
##  This problem can also be caused by another application which uses the
##  soundcard right now."""

class SndBut(SPSpriteUtils.SPSprite):
    Selected = None # This is a global reference to hold a selected object
    def __init__(self,snd,pos,img,img_high):
        self.snd = snd
        self.img = img
        self.img_high = img_high
        self.image = self.img.convert()
        SPSpriteUtils.SPSprite.__init__(self,self.image)
        self.rect = self.image.get_rect().move(pos)
        # self.image and self.rect are mandatory for the pygame sprite class
        self.high = 0 # used to signal highlight or not
        self.connect_callback(self.on_select_button, MOUSEBUTTONDOWN) # MOUSEBUTTONDOWN = pygame constant 
        
    def play(self):
        self.snd.play()
    def stop(self):
        self.snd.stop()
        
    def highlight(self):
        if self.high:# we use a flag, because the images used are references.
            self.image = self.img
            self.high = 0
        else:
            self.image = self.img_high
            self.high = 1
        r = Img.screen.blit(self.image,self.rect)
        pygame.display.update(r)
        
    def on_update(self,*args):
        """ This is called when there's no callback function registered with
         the connect_callback method."""
        pass # we use callbacks, this is just as an example
    
    def on_select_button(self,obj,event,*args):
        """ This is a callback function used by a CPSprite object, like the callback
        fuctions in gtk++.
        A callback function must be connected to the object with a call to the 
        connect_callback method.
        When this fuction is called by the class it is called with a tuple of arguments.
        This tuple consist of:
            0 - a reference to the connected object.
            1 - the event that triggers this call.
            2 .. - data which where passed to the connect call.
        """
        
        #print " obj,event,*args",obj,event,args
        
        if not SndBut.Selected: # nothing selected yet
            self.play() # play the sound
            self.highlight() # toggle the high light button
            # keep track on how many times this card is opened
            # this is also stored in the dbase
            Global.selected_cards[self] += 1
            SndBut.Selected = self # store reference to compare when there's a second selection
            return
        if self.rect is SndBut.Selected.rect:# selected the same object twice, do nothing
            return
        # we are the second card
        self.play()
        self.highlight()
        Global.selected_cards[self] += 1
        pygame.time.wait(1500)
        if SndBut.Selected.snd is self.snd: # sounds are the same
            SndBut.Selected.remove_sprite()# remove sprite object
            self.remove_sprite()# remove 
            SndBut.Selected = None
            
        else:
            SndBut.Selected.highlight() #toggle highlight to normal
            self.highlight()
            SndBut.Selected = None

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
        self.logger =  logging.getLogger("schoolsplay.soundmemory.Activity")
        self.logger.info("Activity started")
        self.SPG = SPGoodies
        self.screen = self.SPG.get_screen()
        self.backgr = self.SPG.get_background()
        self.orgscreen = self.screen.convert()# we use this to restore the screen
        # store two surfaces for later use
        Img.screen = self.screen
        Img.backgr = self.backgr
        
        self.libdir = self.SPG.get_libdir_path()
        self.my_datadir = os.path.join(self.libdir,'CPData','SoundmemoryData')
        self.sounddir = os.path.join(self.libdir,'CPData','FindsoundData')
        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special CPGroup
        self.actives = SPSpriteUtils.SPInit(self.screen,self.backgr)
        
    def clear_screen(self):
        self.screen.blit(self.orgscreen,(0,0))
        self.backgr.blit(self.orgscreen,(0,0))
        pygame.display.update()    
        
    def get_helptitle(self):
        """Mandatory method"""
        return _("Soundmemory")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "soundmemory"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),
        _("Classic memory game where you have to find pairs of sounds."),
        " "]
        return text 
    
    def get_helptip(self):
        """Mandatory method, when no tips available returns an empty list"""
        return [_("Correctness is more important than speed")]
        
    def get_helptype(self):
        """Mandatory method, you must set an type"""
        # Possible types are: Memory, Math, Puzzle, Keyboardtraining, Mousetraining
        #                     Language, Alphabet, Fun, Miscellaneous
        return _("Memory")
        
    def get_helplevels(self):
        """Mandatory method, must return a string with the number of levels
        in the follwing format:
        _("This level has %s levels" % number-of-levels)"""
        return _("This activity has %s levels") % 5
    
    def start(self):
        """Mandatory method."""
        if not pygame.mixer.get_init():
            self.logger.error("No sound card found or not available")
            self.SPG.tellcore_info_dialog(_(SPHelpText.CP_find_char_sound.ActivityStart))
            raise utils.MyError(SPHelpText.CP_find_char_sound.ActivityStart)
        self.all_sounds = []
        for file in glob.glob(os.path.join(self.sounddir,'Sounds','*'+os.sep+'*.ogg')):
            self.all_sounds.append(utils.load_sound(file))
        
        # We use the same images for all the buttons.
        # We check the sound objects for equality not the images.
        self.snd_img = utils.load_image(os.path.join(self.my_datadir,'but_bleu_up.png'),1)
        self.snd_img_high = utils.load_image(os.path.join(self.my_datadir,'but_red_down.png'),1)
        # number of items y, number of items x, x offset, y offset
        self.gamelevels = [(2,3,200,100),(2,4,180,100),(3,4,180,60),(4,5,100,20),(4,6,50,20)]
        
    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        if level == 6:
            return False
        
        # Lower framerate as we only check for mouse events and don't have animated
        # sprites
        self.SPG.tellcore_set_framerate(10)
        # make sure we don't have old sprites in the group
        self.actives.empty()
        # restore screen
        self.clear_screen()
        pygame.display.update()
        
        r, c ,xoffset, yoffset = self.gamelevels[level-1]
        x_offset =  self.snd_img.get_width()+ 16
        y_offset = self.snd_img.get_height() + 16
        # shuffle sounds
        random.shuffle(self.all_sounds)
        num = (r * c)/2
        objects = self.all_sounds[:num] * 2
        self.num_of_buttons = len(objects)
        # db_mapper is a Python class object that provides easy access to the 
        # dbase.
        self.db_mapper = dbmapper
        # store number of cards into the db table 'cards' col
        self.db_mapper.insert('sounds',self.num_of_buttons)
        random.shuffle(objects)
        # used to record how many times the same card is shown.
        # It's setup in the next_level method and used by the Card objects.
        # we store it into a class namespace to make it globally available.
        Global.selected_cards = {}
        for y in range(r):
            for x in range(c): 
                obj = SndBut(objects.pop(),\
                            (xoffset + x*x_offset,yoffset + y*y_offset),\
                            self.snd_img,self.snd_img_high)
                self.actives.add(obj)        
                Global.selected_cards[obj] = 0
        return True
    
    def stop_timer(self):
        for obj in Global.selected_cards:
            obj.stop()
    
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
        # Same as the memory activities
        totalcards = self.num_of_buttons
        cardsturnt = self.knownbuttons
        m,s = timespend.split(':')
        seconds = int(m)*60 + int(s)
        c = 0.7
        f = 0.5
        score =  8.0 / ( max( float(cardsturnt)/float(totalcards)/1.5, 1.0 ) )**c \
                        + 2.0 / ( max( seconds/(totalcards*2), 1.0)) **f
        return score
        
    def loop(self,events):
        """Mandatory method.
        This is the main eventloop called by the core 30 times a minute."""
        item = None
        for event in events:
            if event.type is MOUSEBUTTONDOWN:
                item = event
                break
        try:
            self.actives.refresh(item)# Check all objects in group for callback function
        except:
            self.logger.exception("Unhandled exception")
            raise StandardError
        # check if there objects left in the sprite group
        if not self.actives.sprites():
            # we call the SPGoodies observer to notify the core the level
            # is ended and we want to store the collected data
            num = 0
            for n in Global.selected_cards.values():
                num += n
            # store into dbase
            self.db_mapper.insert('knownsounds',num)
            # set an attribute so that 'get_score' can calculate the score
            self.knownbuttons = num
            self.SPG.tellcore_level_end(store_db=True)
        return 
        
