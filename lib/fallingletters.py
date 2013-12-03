# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zytkiewicz stas.zytkiewicz@schoolsplay.org
#
#           fallingletters.py
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
# self.logger =  logging.getLogger("childsplay.fallingletters.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("childsplay.fallingletters")

# standard modules you probably need
import os,sys,random,string

import pygame
from pygame.constants import *

import utils
from SPConstants import *
import SPSpriteUtils
import Timer

if utils.get_locale()[0][:2] in SUPPORTEDKEYMAPS:
    LANG = utils.get_locale()[0][:2]
else:
    LANG = None
module_logger.debug("LANG set to %s" % LANG)

# containers that can be used globally to store stuff
class Misc:
    pass
    
class Letter(SPSpriteUtils.SPSprite):# we derive from this high-level class
    def __init__(self,c,x,y,step,delay):
        # create a image of the character c
        size = 48
        effect_amt = 6
        rectsizex,rectsizey = 80,80
        r,g,b = 255,0,0
        #self.image= utils.shadefade(c,size,effect_amt,(rectsizex,rectsizey),(r,g,b))
        self.image = utils.char2surf(c,size, fcol=RED, bold=True)
        SPSpriteUtils.SPSprite.__init__(self,self.image)# embed it in this class
        self.letter = c
        start = (x,y)
        self.delay = delay
        self.wait = delay
        self.rect = self.image.get_rect()
        end = (x,600)# move of the screen
        loop = 0# 0 means one time, 1 means twice
        # setup the movement of this object and get a reference to the iterator
        # which we need in the on_update method.
        self.moveit = self.set_movement(start,end,step,0,loop)
        self.connect_callback(self.callback, event_type=KEYDOWN)
        # counter that holds the number of on_update calls.
        # It is used to calculate the score value.
        # The bigger the counter the longer the object was visible
        self.visibletime = 0 
        
    def __str__(self):
        return self.letter
    
    def _get_visiblecounter(self):
        """This returns the visibletime counter devided by 30 as the counter
        is updated 30  times a second (currently SP is running at a frame rate of 30)"""
        return self.visibletime / 30.0 
    
    def on_update(self,*args):
        """This is called by group.refresh method"""
        self.visibletime += 1
        if self.wait:# extra delay, otherwise they drop still to fast 
            self.wait -= 1
            return
        else:
            self.wait = self.delay
            # we must call the iterator ourselfs because we override this method
            # from the SPSprite class
            # We override it because want to know if the movement is completed,
            # meaning user failed to type the correct character.
            # Otherwise the 'next' call is done by the SPSprite class
            status = self.moveit.next()
            if status != -1:# reached the end of the movement
                self.remove_sprite()
                # Update the missed_letters counter
                Misc.missed_letters += 1
                # update the time spend counter
                Misc.timespend += self._get_visiblecounter()
                # update the counter in the menubar
                Misc.execounter.increase_counter()

    def callback(self,*args):
        """ This is called when the sprite class update method is called.
        Remember that you must 'connect' a callback first with a call to
        self.connect_callback, see the CPSprite reference for info on possibilities
        of connecting callbacks .
        """
        try:
            c = args[1].unicode.upper()
        except ValueError:
            return
        module_logger.debug("received event: %s" % [args])
        if c == str(self).upper():
            self.remove_sprite()
            # update the time spend counter
            Misc.timespend += self._get_visiblecounter()
            # speak letter, if available
            if Misc.language:
                utils.speak_letter(c,Misc.language)
            # update the counter in the menubar
            Misc.execounter.increase_counter()
            return

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
        self.logger =  logging.getLogger("childsplay.fallingletters.Activity")
        self.logger.info("Activity started")
        self.SPG = SPGoodies
        self.scoredisplay = self.SPG.get_scoredisplay()
        self.theme = self.SPG.get_theme()
        # alphabetsounds playing
        Misc.language = self.SPG.get_localesetting()[0]
        self.screen = self.SPG.get_screen()
        self.screenclip = self.SPG.get_screenclip()
        self.blit_pos = self.screenclip.left, self.screenclip.top
        self.orgscreen = pygame.Surface(self.screenclip.size) # we use this to restore the screen
        self.orgscreen.blit(self.screen, (0, 0), self.screenclip)
        self.backgr = self.SPG.get_background()
        # The location of the activities Data dir
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','FallinglettersData')
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.CPdatadir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        # Location of the alphabet sounds dir
        self.absdir = self.SPG.get_absdir_path()# alphabet sounds dir
        self.rchash = utils.read_rcfile(os.path.join(self.my_datadir, 'c'))
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
        return _("Fallingletters")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "fallingletters"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),
        _("Type the falling letters on the keyboard before they hit the ground."),
        _("In the last two levels the uppercase and lowercase are mixed but you don't have to match the case only the letter"),
        " "]
        return text 
    
    def get_helptip(self):
        """Mandatory method, when no tips available returns an empty list"""
        return [_("Correctness is more important than speed")]
        
    def get_helptype(self):
        """Mandatory method, you must set an type"""
        # Possible types are: Memory, Math, Puzzle, Keyboardtraining, Mousetraining
        #                     Language, Alphabet, Fun, Miscellaneous
        return _("Alphabet/Keyboardtraining")
        
    
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
        if level > 6: return False # no more then 6 levels
        # make sure we don't have a timer running
        self.stop_timer()
        # db_mapper is a Python class object that provides easy access to the dbase.
        self.db_mapper = dbmapper
        # make sure we don't have objects left in the actives group.
        self.actives.empty()
        # reset the screen to clear any crap from former levels
        self.clear_screen()
        
        # (re)set counters
        Misc.missed_letters = 0
        Misc.wrong_letters = 0
        Misc.timespend = 0
        
        # setup the letters objects
        self.letter_objects = []
        if level == 1:
            # only numbers
            chars = self.numbers_list[:]# a copy just to be sure 
            delay = 2
            step = 1
            timersleep = 3
        elif level in (2,3):
            chars = self.letters_list[:]
            delay = 4 - level
            step = 1
            timersleep = 5 - level
        elif level in (4,5):
            chars = []
            # make lower caps
            for c in self.letters_list:
                chars.append(c.lower())
            delay = 6 - level
            step = 1
            timersleep = 7 - level
        else:
            # mix upper case and lower case and numbers
            chars = self.get_mixed_list(self.letters_list[:])
            chars += self.numbers_list[:]
            delay = 1
            step = 1
            timersleep = 2
        # num_chars is used in the score calculation
        self.num_chars = len(chars)
            
        random.shuffle(chars)
        for c in chars:
            x = random.randint(10,740)
            # create a list with Letter instances
            self.letter_objects.append(Letter(c,x,y-10,step,delay))
        # Tell the core to display a exercises/done counter
        Misc.execounter = self.SPG.tellcore_display_execounter(int(self.num_chars))
        # special threaded timer object
        self.timer = Timer.Timer(delay=timersleep,func=self.drop_letter,lock=self.lock, startnow=True)

        # return True to tell the core were not done yet
        return True
        
    def start(self):
        """Mandatory method."""
        # first we setup two lists, one with numbers 0-9 and one with letters A-Z
        # we convert them to images in next_level
        self.letters_list = list(string.lowercase)
        if LANG:
            newlist = []
            for char in self.letters_list:
                newlist.append(utils.map_keys(LANG, char.upper()))
            self.letters_list = newlist
        self.numbers_list = list(string.digits)
        # we will also use timers to 'launch' the letters
        self.timer = None # will hold the timer object
        # because we will use timers we must pass them the SPC lock object.
        # The lock is used to lock every thread when a dialog is shown and
        # everything should 'freeze'
        self.lock = self.SPG.get_thread_lock()
    
    def post_next_level(self):
        """Mandatory method.
        This is called once by the core after 'next_level' *and* after the 321 count.
        You should place stuff in here that run in a seperate thread like sound play."""
        self.timer.start()
        
    def get_score(self,timespend):
        """Mandatory method.
        @timespend is the time spend inside the level as it's calculated
        by the core.
        returns the score value for the past level.
        return None if no score value is used"""
        # timespend is not used, we keeping time ourselfs
        # As this method is called by the core when a level is finished
        # we also use it to store the counters
        self.db_mapper.insert('missedletters',Misc.missed_letters)
        self.db_mapper.insert('wrongletters',Misc.wrong_letters)
        self.db_mapper.insert('totaltime',Misc.timespend)
        # add wrongletters to dbase, TODO: add column to table
        # calculate score value
        # For every missed letter we add 40 seconds to timespend.
        # For every wrong letter we add 10 seconds to timespend.
        # An educated guess (tested with some children) would be the following
        # scores. The average seconds are calculated by dividing the timespend
        # by 26, the number of characters shown. 
        # 1 second average == 10
        # 13 second average == 7
        # 23 second average == 5.5
        # >43 == 1
        seconds = Misc.timespend
        seconds += (40.0 * Misc.missed_letters)
        seconds += (10.0 * Misc.wrong_letters)
        score = max(0.2, 10 - ((((seconds/26.0)*0.7) ** 0.6)-0.8))
        if score > 10:
            score == 10
        self.logger.debug('missed_letters %s' % Misc.missed_letters)
        self.logger.debug('wrong_letters %s' % Misc.wrong_letters)
        self.logger.debug('total time %s' % seconds)
        self.logger.debug('score %s' % score)
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
        myevent = None
        if not self.letter_objects and not self.actives.sprites():
            # no more sprites left so the level is done.
            # we call the SPGoodies observer to notify the core the level
            # is ended and we want to store the collected data
            self.SPG.tellcore_level_end(store_db=True)
        for event in events:
            if event.type is KEYDOWN:
                # no need to query all sprites with all the events
                # we only pass it an event if it's an event were intrested in.
                myevent = event
                # first we check if the event key is part of the active sprites
                # if not we increase the Misc.wrong_letters counter.
                if event.unicode.upper() not in [x.letter.upper() for x in self.actives.sprites()]:
                    Misc.wrong_letters += 1
                    break
        # move all images
        self.actives.refresh(myevent)
        return 

    def drop_letter(self):
        """Called by the timer, and responsible for the letter dropping.
        This will get a letter from the letter_objects list and place it in
        the Sprite actives group, and thereby it will be blitted on the screen."""
        try:
            obj = self.letter_objects.pop()
        except IndexError:
            return 0
        self.actives.add(obj)
        return 1        
    
    def get_mixed_list(self,charlist):
        # now we shuffle and split the list in two, one halve will
        # become lower and the other upper.
        random.shuffle(charlist)
        lowerlist = charlist[13:]
        upperlist = [x.lower() for x in charlist[:13]]
        charlist = lowerlist+upperlist
        random.shuffle(charlist)
        return charlist
          
