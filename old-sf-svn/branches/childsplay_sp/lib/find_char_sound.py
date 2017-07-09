# -*- coding: utf-8 -*-

# Copyright (c) 2007 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           CP_find_char_sound.py
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

module_logger = logging.getLogger("schoolsplay.CP_find_char_sound")

# standard modules you probably need
import os,sys,random,glob,string

import pygame
from pygame.constants import *

import childsplay_sp.utils as utils
from childsplay_sp.SPConstants import *
import childsplay_sp.SPSpriteUtils as SPSpriteUtils
import childsplay_sp.Timer as Timer
from childsplay_sp import SPHelpText
 
# containers that can be used globally to store stuff
class Misc:
    # for every 'blinked' char we increase the missed_chars counter
    # at the start of each level it's set to zero.
    missed_chars = 0

class ImageObject(SPSpriteUtils.SPSprite):
    def __init__(self,img,blink,snd,lock):
        self.logger =  logging.getLogger("schoolsplay.CP_find_char_sound.ImageObject")
        self.image = img
        self.blinkimg = blink
        self.rect = self.image.get_rect()
        SPSpriteUtils.SPSprite.__init__(self,self.image)
        self.sound = snd
        self.connect_callback(self.callback, event_type=MOUSEBUTTONDOWN)
        self.lock = lock
    
    def blink(self):
        """Called by the timer, returns False to stop the timer.
        We blink once by changing the image and redisplay it.
        This is all done by this object"""
        Misc.missed_chars += 1
        self.erase_sprite()
        pygame.draw.rect(self.blinkimg,BLACK,self.image.get_rect(),3)
        self.image = self.blinkimg
        self.display_sprite()
        return False# will stop timer
    
    def start_timer(self,secs):
        # start a timer which will let the object 'blink' once after 60 seconds. 
        # we keep a reference as we *must* make sure we stop any timers.
        self._timer = Timer.Timer(delay=secs,func=self.blink,loop=1,lock=self.lock)
        self._timer.start()
        
    def stop_timer(self):
        self._timer.stop()

    def play(self):
        sndobj = utils.load_music(self.sound)
        if sndobj == 'NoneSound':
            self.logger.error("No sound card found or not available")
            raise utils.MyError(SPHelpText.CP_find_char_sound.ActivityStart)
        sndobj.play(1)
        
    def callback(self,*args):
        """If this is called the user hits the right image."""
        self.erase_sprite()
        self.stop_timer()  
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
        self.logger =  logging.getLogger("schoolsplay.CP_find_char_sound.Activity")
        self.logger.info("Activity started")
        self.SPG = SPGoodies
        self.screen = self.SPG.get_screen()
        self.backgr = self.SPG.get_background()
        self.orgscreen = self.screen.convert()# we use this to restore the screen
        self.absdir = self.SPG.get_absdir_path()
        self.imgchardir = os.path.join(self.SPG.get_libdir_path(),'SPData','base','CharacterImages')
        self.language = self.SPG.get_localesetting()[0]
        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special CPGroup
        self.actives = SPSpriteUtils.SPInit(self.screen,self.backgr)
        self.selected_object = None
    
    def stop_timer(self):
        """You *must* provide a method to stop timers if you use them.
        The SPC will call this just in case and cache the exception in case 
        there's no 'stop_timer' method""" 
        try:
            self.selected_object.stop_timer()
        except:
            pass
            
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
            self.selected_object.start_timer(10)
    
    def get_mixed_list(self):
        charlist = []
        for car in range(97,122):
            charlist.append(chr(car))
        # now we shuffle and split the list in two, one halve will
        # become lower and the other upper.
        random.shuffle(charlist)
        lowerlist = charlist[13:]
        upperlist = [x.upper() for x in charlist[:13]]
        charlist = lowerlist+upperlist
        random.shuffle(charlist)
        return charlist
    
    def _make_fonts(self,names,toUpper=False):
        imgsnd = {}
        size = 60
        effect_amt = 6
        rectsizex,rectsizey = 50,50
        for path in names:
            name = os.path.basename(path)[1:-4] # XXX This doesn't work for 10.ogg .. 20.ogg
            if toUpper:
                text = string.upper(unichr(int(name, 16)))
            else:
                text = unichr(int(name, 16))
            #print '_make_fonts',text
#            asdf = utils.shadefade(text,size,effect_amt,(rectsizex,rectsizey),(255,0,0))
#            asdf_b = utils.shadefade(text,size,effect_amt,(rectsizex,rectsizey),(255,255,0))
            asdf = utils.char2surf(text, size, fcol=RED, bold=True)
            asdf_b = utils.char2surf(text, size, fcol=YELLOW, bold=True)
            imgsnd[path] = (asdf,asdf_b)
        return imgsnd
    
    def get_helptitle(self):
        """Mandatory method"""
        return _("Find the characters")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "CP_find_char_sound"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),
        _("Listen to the sound and click on the character to which it belongs."),
        _("When you can't find the correct character after a certain period of time a box will be drawn around it."), 
        _("The faster you find all the characters the better your score will be."),
        " "]

        return text 
    
    def get_helptip(self):
        """Mandatory method, when no tips available returns an empty string"""
        return [_("The faster you find all the characters the better your score will be.")]
        
    def get_helptype(self):
        """Mandatory method, you must set an type"""
        # Possible types are: Memory, Math, Puzzle, Keyboardtraining, Mousetraining
        #                     Language, Alphabet, Fun, Miscellaneous
        return _("Alphabet")
    
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
        # we check if we have localized soundfiles
        # if not we fall back on the 'builtin' English sounds.
        self.soundlanguagedir = self.SPG.get_absdir_loc_path()
        
        img = utils.load_image(os.path.join(self.SPG.get_libdir_path(),\
                                        'CPData','soundbut.png'),1)
        pos = (360,400)
        self.soundbutton = SPSpriteUtils.SPButton(img,pos,1)
        # Get all the imagesfile paths.
        # Get the soundfile paths, this is set to the proper locale in start()
        # filenames looks like this U0031.ogg
        self.all_sounds = glob.glob(os.path.join(self.soundlanguagedir,'U*.ogg'))
        # we can display 45 chars
        if len(self.all_sounds) > 45:
            self.all_sounds = self.all_sounds[:45]
        self.all_sounds.sort()
        # Generate the positions matrix.
        # images will be 90x90 and in each level we pick positions from this matrix
        # so that we can easily place them randomly.
        # The matrix is a list of lists holding tuples with x,y pairs.
        # Every list represent a row with columns
        # to get a position at row 3 column 6; self.postions[2][5]
        self.positions = []
        self.all_positions = []
        for y in range(0,410,90):
            collist = []
            for x in range(8,800,90):
                collist.append((x,y))
            self.positions.append(collist)
            self.all_positions += collist
        # remove the position of the soundbutton so that we don't blit over it.
        self.all_positions.remove((368,360))
        
    def get_score(self,timespend):
        """ The score is calculated as follows:
         (time is calculated in seconds)
         The average adult, me :-), does level 1 in 20 seconds and the 2-6 in 
         60 seconds. So 1 char in 60/26 = 2 seconds.
         If a level is done in (characters * 2) the score is 10
         we don't use the blinked chars count because it takes a long time to blink so
         the time penalty is big enough.
         Let's say that (characters * 10) is rather bad (5 times slower then me) which
         would give a score of 6.
         
         f is used to increase the difference between times.
         self.lencharslist is the number of characters.
         seconds is the time spend to clear the level.
         
         f = 1.4
         score = 10 - (float(seconds) / float(self.lencharslist))*f / 2.0 + 1
         if score > 10:
            score = 10
         """
        # as this method is called by the core when a level is finished
        # we also use it to store the 'missed_chars' counter
        self.db_mapper.insert('missedchars',Misc.missed_chars)
        m,s = timespend.split(':')
        seconds = int(m)*60 + int(s)
        # The score is calculated as follows:
        # (time is calculated in seconds)
        # The average person, me :-), does level 1 in 20 seconds and the 2-5 in 
        # 60 seconds. So 1 char in 60/26 = 2 seconds.
        # If a level is done in len(chars) * 2 the score is 10
        # we don't use the blinked chars count because it takes a long time to blink so
        # the time penalty is big enough.
        # Let's say that len(chars) * 10 is rather bad (5 times slower then me) which
        # would give a score of 6.
        # 
        # f is used to increase the difference between times       
        f = 1.4
        score = max(0.2,(10 - (float(seconds) / float(self.lencharslist))*f / 2.0 + 1))
        self.logger.debug("Score : %s" % score)
        if score > 10:
            score = 10
        return score
        
    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        # Until now only 5 levels work
        if level == 6:
            return False
        # make sure we don't have a timer running
        self.stop_timer()
        # db_mapper is a Python class object that provides easy access to the 
        # dbase.
        self.db_mapper = dbmapper
        # make sure we don't have objects left in the actives group.
        self.actives.empty()
        # reset the screen to clear any crap from former levels
        self.clear_screen()
        # reset missed chars counter
        Misc.missed_chars = 0
        # setup the level
        # level 1 is numbers from 1 to 10 in one line
        # 2 is numbers mixed
        # 3 is uppercase
        # 4 is lowercase
        # 5 is upper and lowercase mixed
        # 6 is upper, lowercase and numbers mixed
        #
        # 0030 = 0 and 0039 =9, 10 - 20 are not in hex as they are made up of
        # two images.
        # 
        # Filenames in AlphabetSounds:
        # U0030 - U0039 -> numbers 0-9
        # U0061 - U007a -> latin a-z
        # Reminder:
        # 0041 - 005a -> latin upper case
        # 0061 - 007a -> latin lower case 
        
        if level == 1:
            # A valid sound package contains the same names as the image list
            # so we assume the sound list will be correct
            level_sounds = self.all_sounds[:10]
            # get a dict with images generated from the sound file names
            sndimg_dict = self._make_fonts(level_sounds)
            whichlevel = 'Numbers in line'    
            level_positionslist = []
            for r in [1,2]:
                for c in [1,2,3,4,5]:
                    level_positionslist.append(self.positions[r][c])
        elif level == 2:
            level_sounds = self.all_sounds[:10]
            sndimg_dict = self._make_fonts(level_sounds)
            whichlevel = 'Numbers shuffle'    
            level_positionslist = []
            copy_positions = self.all_positions[:]
            random.shuffle(copy_positions)
            level_positionslist = copy_positions[:10]
        elif level == 3:
            level_sounds = self.all_sounds[10:]
            sndimg_dict = self._make_fonts(level_sounds,toUpper=True)
            whichlevel = 'Letters uppercase'    
            level_positionslist = []
            copy_positions = self.all_positions[:len(sndimg_dict.keys())]
            #random.shuffle(copy_positions)
            level_positionslist = copy_positions[:]
        elif level == 4:
            level_sounds = self.all_sounds[10:]
            sndimg_dict = self._make_fonts(level_sounds)
            whichlevel = 'Letters lowercase'    
            level_positionslist = []
            copy_positions = self.all_positions[:]
            random.shuffle(copy_positions)
            level_positionslist = copy_positions[:len(sndimg_dict.keys())]
        elif level in (5,6):
            level_sounds = self.all_sounds[10:]
            if len(level_sounds) > 35:
                level_sounds = level_sounds[:35]
            sndimg_dict = self._make_fonts(level_sounds)
            level_sounds = self.all_sounds[1:10]# remove zero as it resembles O
            sndimg_dict.update(self._make_fonts(level_sounds))
            whichlevel = 'Lowercase+numbers'
            level_positionslist = []
            copy_positions = self.all_positions[:]
            level_positionslist = copy_positions[:len(sndimg_dict.keys())]
                
        self.db_mapper.insert('chars',len(sndimg_dict.keys()))
        self.db_mapper.insert('kind',whichlevel)
        
        # keep a reference to calculate the score
        self.lencharslist = len(sndimg_dict.keys())
        # Now we gonna build and display our objects
        self.objects = []
        itemslist = sndimg_dict.items()
        if level == 1 or level == 3:
            itemslist.sort(reverse=True)
        else:
            level_positionslist.sort()
        for snd, img in itemslist:
            obj = ImageObject(img[0],img[1],snd,self.SPG.get_thread_lock())
            obj.display_sprite(level_positionslist.pop())
            self.objects.append(obj)
        self.soundbutton.display_sprite()
        random.shuffle(self.objects)# See picked_object on why we randomize
        # return True to tell the core were not done yet
        return True
        
    def post_next_level(self):
        """Mandatory method.
        This is called by the core after 'next_level' *and* after the 321 count.
        You should place stuff in here that run in a seperate thread like sound play."""
        # this is the object that must be found, when the user clicks on it
        # we pick another
        # This is placed here because it also plays a sound
        self.selectedobject = self.picked_object()    
    
    def loop(self,events):
        """Mandatory method
        """
        for event in events:
            if event.type is MOUSEBUTTONDOWN and self.selected_object:
                if self.selected_object.update(event):
                    # if the object returns True it's hit by the user and we
                    # pick another object
                    if self.picked_object():
                        # we call the SPGoodies observer to notify the core the level
                        # is ended and we want to store the collected data
                        self.SPG.tellcore_level_end(store_db=True)
                if self.soundbutton.update(event):
                    # is the soundbutton hit?
                    self.selected_object.play()
        return 
        
