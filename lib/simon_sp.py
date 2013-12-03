
# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zytkiewicz stas.zytkiewicz@schoolsplay.org
# Parts are taken from the Braintrainer project http://www.braintrainerplus.com
#
#           simon_sp.py
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

# TODO: this has to be rewritten some day to make it more SP like.
# Major headache is the stuff that goes on in the eventloop.

#create logger, logger was setup in SPLogging
import logging
# In your Activity class -> 
# self.logger =  logging.getLogger("childsplay.simon_sp.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("childsplay.simon_sp")

# standard modules you probably need
import os,sys,random

import pygame
from pygame.constants import *

import utils
from SPConstants import *
import SPSpriteUtils

CYELLOW = 1
CRED = 2
CBLUE = 3
CGREEN = 4

class CenterButton(SPSpriteUtils.SPSprite):
    def __init__(self, img, pos):
        SPSpriteUtils.SPSprite.__init__(self, img)
        self.rect = self.image.get_rect()
        self.moveto(pos)
        
class SndButton(SPSpriteUtils.SPSprite):
    def __init__(self, img_off, img_on, snd,pos, obs, col):
        SPSpriteUtils.SPSprite.__init__(self, img_off)
        self.rect = self.image.get_rect()
        self.obs = obs
        self.image_on = img_on
        self.image_off = img_off
        self.col = col
        self.snd = snd
        self.connect_callback(self.cbf, event_type=MOUSEBUTTONDOWN)
        self.moveto(pos)
    
    def activate(self):
        self.snd.play()
        self.erase_sprite()
        self.image = self.image_on
        self.display_sprite()
        pygame.time.delay(600)
        self.erase_sprite()
    
    def cbf(self, *args):
        # check for alpha pixel and if not display light image and call obs 
        mx, my = pygame.mouse.get_pos()
        pos = (mx - self.rect.left, my - self.rect.top)
        c = self.image.get_at(pos)[3]
        if c:
            self.activate()
            self.obs(self.col)
        return -1
            
        
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
        self.logger =  logging.getLogger("childsplay.simon_sp.Activity")
        self.logger.info("Activity started")
        self.SPG = SPGoodies
        self.theme = self.SPG.get_theme()
        self.scoredisplay = self.SPG.get_scoredisplay()
        self.screen = self.SPG.get_screen()
        self.screenclip = self.SPG.get_screenclip()
        self.blit_pos = self.screenclip.left, self.screenclip.top
        self.orgscreen = pygame.Surface(self.screenclip.size) # we use this to restore the screen
        self.orgscreen.blit(self.screen, (0, 0), self.screenclip)
        self.backgr = self.SPG.get_background()
        # The location of the activities Data dir
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','Simon_spData')
        self.rchash = utils.read_rcfile(os.path.join(self.my_datadir, 'simon_sp.rc'))
        self.rchash['theme'] = self.theme
        
        self.logger.debug("found rc: %s" % self.rchash)
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.CPdatadir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        # Location of the alphabet sounds dir
        self.absdir = self.SPG.get_absdir_path()# alphabet sounds dir
        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special CPGroup
        self.actives = SPSpriteUtils.SPInit(self.screen,self.backgr)
        
        ### BT related stuff, was rc file dependant replaced by hardcoded values.
        if self.blit_pos[1] == 0:
            y =10
        else:
            y = 110
        self.yTop=y #int(self.config["yMargin"])
        self.xMargin=0  #int(self.config["xMargin"])
        ##################################
        self.lang = self.SPG.get_localesetting()[0][:2]
        self.sequence = []
        self.all_choices=[1,2,3,4]
        
        
    def get_moviepath(self):
        movie = os.path.join(self.my_datadir,'help.avi')
        return movie
    
    def refresh_sprites(self):
        """Mandatory method, called by the core when the screen is used for blitting
        and the possibility exists that your sprites are affected by it."""
        self.actives.redraw()

    def get_helptitle(self):
        """Mandatory method"""
        return _("Simon_sp")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "simon_sp"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),
        _("Try to repeat the sequence of sounds played."),
        " ", 
        _("On the screen are four blocks of different colours."), 
        _("Press the Start button with your finger."), 
        " ", 
        _("The  blocks will light up randomly along with sound clues."), 
        _("When the flashing stops you will be prompted to repeat the sequence by touching the coloured blocks."), 
        " ",
        ]
        return text 
    
    def get_helptip(self):
        """Mandatory method, when no tips available returns an empty list"""
        return _("Mind the sound sequence as well as the colors sequence.")
        
    def get_helptype(self):
        """Mandatory method, you must set an type"""
        # Possible types are: Memory, Math, Puzzle, Keyboardtraining, Mousetraining
        #                     Language, Alphabet, Fun, Miscellaneous
        return _("Memory")
    
    def get_helplevels(self):
        """Mandatory method, must return a string with the number of levels
        in the follwing format:
        _("This level has %s levels") % number-of-levels"""
        return _("This activity has %s levels") % 6
    
    def stop(self):
        pygame.event.clear()
        
    def start(self):
        """Mandatory method."""
        self.snd_butts = []
        backdir = os.path.join(self.my_datadir,'backgrounds', self.lang)
        yellow_sound = utils.load_sound(os.path.join(self.my_datadir,'1.ogg'))
        red_sound = utils.load_sound(os.path.join(self.my_datadir,'2.ogg'))
        blue_sound = utils.load_sound(os.path.join(self.my_datadir,'3.ogg'))
        green_sound = utils.load_sound(os.path.join(self.my_datadir,'4.ogg'))
        self.good_sound=utils.load_sound(os.path.join(self.my_datadir,'good.ogg'))
        self.wrong_sound=utils.load_sound(os.path.join(self.my_datadir,'wrong.ogg'))
        self.backgr_normal = utils.load_image(os.path.join(backdir,'background.png'))
        self.backgr_start = utils.load_image(os.path.join(backdir,'background_start.png')) 
        self.backgr_tussen = utils.load_image(os.path.join(backdir,'background_repeat.png'))
        self.backgr_good = utils.load_image(os.path.join(backdir,'background_correct.png'))
        self.backgr_wrong = utils.load_image(os.path.join(backdir,'background_wrong.png'))
        
        yellow_on = utils.load_image(os.path.join(self.my_datadir,'yellow.png'))
        yellow_off = utils.load_image(os.path.join(self.my_datadir,'yellow_off.png')) 
        self.yellow_but = SndButton(yellow_off, yellow_on, yellow_sound,(14,245+self.yTop),\
                                     self.snd_but_observer, CYELLOW)   
        #self.yellow_but.set_use_current_background(True)
        self.snd_butts.append(self.yellow_but)    

        red_on = utils.load_image(os.path.join(self.my_datadir,'red.png'))
        red_off = utils.load_image(os.path.join(self.my_datadir,'red_off.png'))
        self.red_but = SndButton(red_off, red_on, red_sound,(400,16+self.yTop), \
                                 self.snd_but_observer, CRED)
        #self.red_but.set_use_current_background(True)
        self.snd_butts.append(self.red_but)
        
        blue_on = utils.load_image(os.path.join(self.my_datadir,'blue.png'))
        blue_off = utils.load_image(os.path.join(self.my_datadir,'blue_off.png'))
        self.blue_but = SndButton(blue_off, blue_on, blue_sound,(14,16+self.yTop),\
                                   self.snd_but_observer, CBLUE)
        #self.blue_but.set_use_current_background(True)
        self.snd_butts.append(self.blue_but)
        
        green_on = utils.load_image(os.path.join(self.my_datadir,'green.png'))
        green_off = utils.load_image(os.path.join(self.my_datadir,'green_off.png')) 
        self.green_but = SndButton(green_off, green_on, green_sound, (400,245+self.yTop),\
                                    self.snd_but_observer, CGREEN)
        #self.green_but.set_use_current_background(True)
        self.snd_butts.append(self.green_but)

        img = utils.load_image(os.path.join(self.my_datadir,self.lang,'start.png')) 
        self.start_but = CenterButton(img, (232, 148+self.yTop))
        self.start_but.connect_callback(self._cbf_start_button, MOUSEBUTTONDOWN)
        
        img = utils.load_image(os.path.join(self.my_datadir,self.lang,'simon.png')) 
        self.simon_but = CenterButton(img, (232, 148+self.yTop))
        img = utils.load_image(os.path.join(self.my_datadir,self.lang,'good.png')) 
        self.good_but = CenterButton(img, (232, 148+self.yTop))
        img = utils.load_image(os.path.join(self.my_datadir,self.lang,'wrong.png')) 
        self.wrong_but = CenterButton(img, (232, 148+self.yTop))      
        # lookup hash for the sounds dbase field, see generate_sequence for the
        # number of sounds in each level
        self.level_sounds_hash = {1:2, 2:3, 3:3, 4:4, 5:5, 6:6}
        self.scoredisplay.clear_score()
        self.AreWeDT = False
        self.score = 0
       
    def snd_but_observer(self,col):
        self.clicked_colors.append(col)
        self.check_sequence()
                
    def _cbf_start_button(self, widget,event,data):
        self.logger.debug("start clicked")
        mx, my = pygame.mouse.get_pos()
        pos = (mx - widget.rect.left, my - widget.rect.top)
        c = widget.image.get_at(pos)[3]
        if c:
            widget.erase_sprite()
            self.actives.remove(widget)
            self.start_sequence()
            self.actives.add(self.snd_butts)
            pygame.event.clear()
                
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
        """Mandatory method"""
        pass

    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        self.logger.debug("next_level called with %s" % level)
        if level > 6: return False # We only have 6 levels
        self.dbscore = 0
        # db_mapper is a Python class object that provides easy access to the 
        # dbase.
        self.dbmapper = dbmapper
        # number of exercises in one level
        if self.AreWeDT:
            self.exercises = 1
        else:
            self.exercises = int(self.rchash[self.theme]['exercises'])
        self.level=level
        self.levelupcount = 1
        self.dbmapper.insert('sounds', self.level_sounds_hash[level])
        self.stop_level = False
        self.levelrestartcounter = 0
        self.actives.empty()
        self.start_exercise()
        return True
    
    def start_exercise(self):
        self.levelrestartcounter += 1
        self.clicked_colors=[]
        # reset the screen to clear any crap from former levels
        self.clear_screen()
        self.screen.blit(self.backgr_normal, (15,self.yTop+15))
        self.backgr.blit(self.backgr_normal, (15,self.yTop+15))
        pygame.display.update()
        pygame.time.wait(1000)
        self.start_but.display_sprite()
        self.actives.add(self.start_but)
    
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
        # score should be dependent on how many correct sequence parts are entered.
        # N = Number sequence parts * number of exercises 
        # P = Users result in points
        # F = Fraction of total result related to points. (maximum result is 10)
        # F1 = Fraction of result related to time
        # C = multiplier
        # S = time spend in seconds
        N = float(self.level_sounds_hash[self.level] * self.exercises)
        P = float(self.dbscore)
        F = 8.0
        F1 = 2.0
        C = 0.4
        C1 = 1.3
        S = float(seconds)
        points = max((F/100) * ((P/(N/100)) * C1), 1.0)
        time = min(F1 / ((S/(N*2)) ** C), F1)
        self.logger.info("@scoredata@ %s level %s N %s P %s S %s points %s time %s" %\
                          (self.get_name(),self.level, N, P, S, points, time))
        result = points + time
        return result

    
    def stop_timer(self):
        """You *must* provide a method to stop timers if you use them.
        The SPC will call this just in case and catch the exception in case 
        there's no 'stop_timer' method""" 
        try:
            self.timer.stop()
        except:
            pass
    
    def clear_screen(self):
        self.screen.blit(self.orgscreen,self.blit_pos)
        self.backgr.blit(self.orgscreen,self.blit_pos)
        pygame.display.update()
                                
    def check_sequence(self):
        l = len(self.clicked_colors)
        if self.sequence[:l] != self.clicked_colors[:l]:
            self.logger.debug("Bad sequence entered")
            self.actives.remove(self.snd_butts)
            self.score = max(0, (self.score - 50)) 
            if self.levelupcount > 0: 
                self.levelupcount -= 1
            self.clicked_colors=[]
            self.screen.blit(self.backgr_wrong,(0+15+self.xMargin,0+self.yTop+15))
            pygame.display.update()
            self.wrong_sound.play()
            pygame.time.delay(2000)
            pygame.event.clear()
            self.start_exercise()
        if len(self.clicked_colors) == len(self.sequence) and self.sequence == self.clicked_colors:
            self.logger.debug("sequence correct")
            self.actives.remove(self.snd_butts)
            self.score += 50
            self.levelupcount += 1
            self.scoredisplay.set_score(self.score*2)
            self.dbscore += len(self.sequence)
            self.screen.blit(self.backgr_good,(0+15+self.xMargin,0+self.yTop+15))
            pygame.display.update()
            self.good_sound.play()
            pygame.time.delay(2000)
            pygame.event.clear()
            self.start_exercise()
        

    def start_sequence(self):    
        self.wrong_sequence = False
        self.sequence=self.generate_sequence()
        self.logger.debug("generated sequence:%s" % self.sequence)
        self.play_sequence()
        
    def play_sequence(self):
        pygame.time.delay(1000)
        self.logger.debug("Playing sequence")
        for color in self.sequence:
            if color==CYELLOW: self.yellow_but.activate()
            if color==CRED: self.red_but.activate()
            if color==CBLUE: self.blue_but.activate()
            if color==CGREEN: self.green_but.activate()
            pygame.time.delay(500)
        self.sequence_index = 0
        pygame.event.clear()
        self.screen.blit(self.backgr_tussen, (15,self.yTop+15))
        self.backgr.blit(self.backgr_tussen, (15,self.yTop+15))
        pygame.display.update()
        
        
    def generate_sequence(self):
        unique_choices=[]
        if self.level==1:
            unique_choices = random.sample(self.all_choices,2)
            return unique_choices
        if self.level==2:
            #3 choices: 2 unique choices and 1 double
            unique_choices = random.sample(self.all_choices,2)
            append_nr=random.sample(unique_choices,1)
            unique_choices.append(append_nr[0])
            return unique_choices
        if self.level==3:
            #3 unique choices
            unique_choices = random.sample(self.all_choices,3)
            return unique_choices
        if self.level==4:
            #4choices: 3 unique choices and 1 double
            unique_choices = random.sample(self.all_choices,3)
            append_nr=random.sample(unique_choices,1)
            unique_choices.append(append_nr[0])
            return unique_choices
        else:
            # levelNr complete random choices 
            i=0
            while i < self.level:
                append_nr=random.sample(self.all_choices,1)
                unique_choices.append(append_nr[0])
                i+=1
            return unique_choices

    def loop(self,events):
        """Mandatory method.
        This is the main eventloop called by the core 30 times a minute."""
        for event in events:
            if event.type is MOUSEBUTTONDOWN:
                self.actives.update(event)
        if self.levelrestartcounter >= self.exercises:
            if self.levelrestartcounter >= int(self.rchash[self.theme]['autolevel_value']):
                levelup = 1
            else:
                levelup = 0
            if self.AreWeDT:
                self.SPG.tellcore_level_end(level=self.level)
            else:
                self.SPG.tellcore_level_end(store_db=True, \
                                    level=min(6, self.level), \
                                                levelup=levelup)
