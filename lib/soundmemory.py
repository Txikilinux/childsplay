
# -*- coding: utf-8 -*-

# Copyright (c) 2008-2010 Stas Zytkiewicz stas.zytkiewicz@schoolsplay.org
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
# self.logger =  logging.getLogger("childsplay.soundmemory.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("childsplay.soundmemory")

# standard modules you probably need
import os,sys,random,glob

import pygame
from pygame.constants import *

import utils
from SPConstants import *
import SPSpriteUtils
import SPHelpText

# containers that can be used globally to store stuff
class Img:
    pass
class Snd:
    pass
class Global:
    """ Container to store all kind of stuff"""
    pass
    

class SndBut(SPSpriteUtils.SPSprite):
    Selected = None # This is a global reference to hold a selected object
    def __init__(self,snd,pos,img,img_high, name, scoreobs):
        self.snd = snd
        self.img = img
        self.img_high = img_high
        self.image = self.img
        SPSpriteUtils.SPSprite.__init__(self,self.image, name=name)
        self.rect = self.image.get_rect().move(pos)
        # self.image and self.rect are mandatory for the pygame sprite class
        self.high = 0 # used to signal highlight or not
        self.connect_callback(self.on_select_button, MOUSEBUTTONDOWN) # MOUSEBUTTONDOWN = pygame constant 
        self.scoreobs = scoreobs
    
    def set_number(self, s):
        self.img.blit(s, (0,0))
        self.img_high.blit(s, (0,0))
        self.image = self.img
        
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
        if SndBut.Selected.name == self.name: # sounds are the same
            SndBut.Selected.kill()# remove sprite object
            SndBut.Selected.erase_sprite()
            self.kill()# remove 
            self.erase_sprite()
            SndBut.Selected = None   
            self.scoreobs(10)
        else:
            SndBut.Selected.highlight() #toggle highlight to normal
            self.highlight()
            SndBut.Selected = None
            self.scoreobs(-10)
            
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
        self.logger =  logging.getLogger("childsplay.soundmemory.Activity")
        self.logger.info("Activity started")
        self.SPG = SPGoodies
        self.theme = self.SPG.get_theme()
        self.scoredisplay = self.SPG.get_scoredisplay()
        self.screen = self.SPG.get_screen()
        self.backgr = self.SPG.get_background()
        self.screenclip = self.SPG.get_screenclip()
        self.blit_pos = self.screenclip.left, self.screenclip.top
        self.orgscreen = pygame.Surface(self.screenclip.size) # we use this to restore the screen
        self.orgscreen.blit(self.screen, (0, 0), self.screenclip)
        # store two surfaces for later use
        Img.screen = self.screen
        Img.backgr = self.backgr
        self.screenclip = self.SPG.get_screenclip()
        self.blit_pos = self.screenclip.left, self.screenclip.top
        self.libdir = self.SPG.get_libdir_path()
        self.my_datadir = os.path.join(self.libdir,'CPData','SoundmemoryData')
        self.rchash = utils.read_rcfile(os.path.join(self.my_datadir, 'soundmemory.rc'))
        self.rchash['theme'] = self.theme
        self.logger.debug("found rc: %s" % self.rchash)
        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special CPGroup
        self.actives = SPSpriteUtils.SPInit(self.screen,self.backgr)
        self.beamer_set = 'off'
        
    def get_moviepath(self):
        movie = os.path.join(self.my_datadir,'help.avi')
        return movie
    
    def refresh_sprites(self):
        """Mandatory method, called by the core when the screen is used for blitting
        and the possibility exists that your sprites are affected by it."""
        self.actives.redraw()

    def clear_screen(self):
        self.screen.blit(self.orgscreen,self.blit_pos)
        self.backgr.blit(self.orgscreen,self.blit_pos)
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
        " ", 
        _("When you touch the picture you will hear a sound.\nMatch the image with others that make the same sound,to get points."), 
        " "]
        return text 
    
    def get_helptip(self):
        """Mandatory method, when no tips available returns an empty list"""
        return _("Correctness is more important than speed")
        
    def get_helptype(self):
        """Mandatory method, you must set an type"""
        # Possible types are: Memory, Math, Puzzle, Keyboardtraining, Mousetraining
        #                     Language, Alphabet, Fun, Miscellaneous
        return _("Memory")
        
    def get_helplevels(self):
        """Mandatory method, must return a string with the number of levels
        in the follwing format:
        _("This level has %s levels" % number-of-levels)"""
        return _("This activity has %s levels") % 6
    
    def start(self):
        """Mandatory method."""
        if not pygame.mixer.get_init():
            self.logger.error("No sound card found or not available")
            self.SPG.tellcore_info_dialog(_(SPHelpText.Nosound.ActivityStart))
            raise utils.MyError(SPHelpText.Nosound.ActivityStart)
        self.all_sounds_files = glob.glob(os.path.join(self.my_datadir,'Sounds','*.ogg'))
        self.logger.debug("Loaded %s files from %s" % (len(self.all_sounds_files), \
                                                    os.path.join(self.my_datadir,'Sounds','*.ogg')))
        # We use the same images for all the buttons.
        # We check the sound objects for equality not the images.
        self.snd_img = utils.load_image(os.path.join(self.my_datadir,'but_bleu_up.png'))
        self.snd_img_high = utils.load_image(os.path.join(self.my_datadir,'but_red_down.png'))
        if self.beamer_set == 'on':
            self.snd_img_b = utils.load_image(os.path.join(self.my_datadir,'but_bleu_up_beamer.png'))
            self.snd_img_high_b = utils.load_image(os.path.join(self.my_datadir,'but_red_down_beamer.png'))
        # number of items y, number of items x, x offset, y offset
        self.gamelevels = [(2,3,200,100),(2,4,180,100),(3,4,180,60),(4,5,100,20),(4,6,50,20), (4, 7, 2,10 )]
        #self.SPG.tellcore_set_dice_minimal_level(1)
        self.displaydscore = 0
        self.levelrestartcounter = 0
        self.level = 1
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
    
    def pre_level(self, level):
        """Mandatory method
        Return True if you want the core to enter the eventloop after this call."""
        pass
        
    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        if level > 6:
            return False
        if level == self.level:
            self.levelrestartcounter += 1
        self.level = level
        if self.blit_pos[1] == 0:
            ty = 10
        else:
            ty = 110
        
        # Lower framerate as we only check for mouse events and don't have animated
        # sprites
        self.SPG.tellcore_set_framerate(10)
        SndBut.Selected = None
        # make sure we don't have old sprites in the group
        self.actives.empty()
        # restore screen
        self.clear_screen()
        #pygame.display.update()
        
        r, c ,xoffset, yoffset = self.gamelevels[level-1]
        x_offset =  self.snd_img.get_width()+ 16
        y_offset = self.snd_img.get_height() + 16
        # shuffle sounds
        random.shuffle(self.all_sounds_files)
        num = (r * c)/2
        files = self.all_sounds_files[:num] * 2
        self.num_of_buttons = len(files)
        self.levelupcount = 1
        # db_mapper is a Python class object that provides easy access to the 
        # dbase.
        self.db_mapper = dbmapper
        # store number of cards into the db table 'cards' col
        self.db_mapper.insert('sounds',self.num_of_buttons)
        random.shuffle(files)
        # used to record how many times the same card is shown.
        # It's setup in the next_level method and used by the Card objects.
        # we store it into a class namespace to make it globally available.
        Global.selected_cards = {}
        i = 1
        for y in range(r):
            for x in range(c): 
                sfile = files.pop()
                
                snd = utils.load_sound(sfile)
                
                if self.beamer_set == 'on':
                    obj = SndBut(snd,\
                            (xoffset + x*x_offset,yoffset + y*y_offset+ty),\
                            self.snd_img_b.copy(),self.snd_img_high_b.copy(), sfile, self.scoreobs)
                    f = os.path.join(self.my_datadir, "%s.png" % i)
                    s = utils.load_image(f)
                    obj.set_number(s)
                    i += 1
                else:
                    obj = SndBut(snd,\
                            (xoffset + x*x_offset,yoffset + y*y_offset+ty),\
                            self.snd_img.copy(),self.snd_img_high.copy(), sfile, self.scoreobs)
                self.actives.add(obj) 
                obj.display_sprite()
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
    def scoreobs(self, i):
        """Called by the card object with a value to display as the score."""
        self.displaydscore += i
        if self.displaydscore <= 0:
            self.displaydscore = 0
        self.scoredisplay.set_score(self.displaydscore*5)
        
    def get_score(self,timespend):
        """Mandatory method.
        @timespend is the time spend inside the level as it's calculated
        by the core.
        returns the score value for the past level.
        return None if no score value is used"""
        # Same as the memory activities
        # T = Total cards
        # K = How many times the cards are selected. (a perfect game K == T)
        # F = Fraction of total result related to points. (maximum result is 10)
        # F1 = Fraction of result related to time
        # C = multiplier
        # S = time spend in seconds
        try:
            T = float(self.num_of_buttons * 2)
            K = float(self.knownbuttons)
        except AttributeError:
            return None
        m,s = timespend.split(':')
        S = float(int(m)*60 + int(s))
        F = 9.0
        F1 = 1.0
        C = 0.6
        C1 = 0.2
        points = F / max(K / T, 1.0 ) ** C1
        time = F1 / max(S / T , 1.0) ** C
        self.logger.info("@scoredata@ %s level %s T %s K %s S %s points %s time %s" %\
                          (self.get_name(), self.level, T, K, S, points, time))
        score = points + time
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
            self.actives.update(item)# Check all objects in group for callback function
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
            if self.levelrestartcounter >= int(self.rchash[self.theme]['autolevel_value']):
                levelup = 1
                self.levelrestartcounter = 0
            else:
                levelup = 0
            if self.AreWeDT:
                        self.SPG.tellcore_level_end(level=self.level)
            else:
                self.SPG.tellcore_level_end(store_db=True, \
                                    level=min(6, self.level), \
                                    levelup=levelup)
        return 
        
