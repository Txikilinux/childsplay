
# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zytkiewicz stas.zytkiewicz@gmail.com
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

#create logger, logger was setup in SPLogging
import logging
# In your Activity class -> 
# self.logger =  logging.getLogger("schoolsplay.simon_sp.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("schoolsplay.simon_sp")

# standard modules you probably need
import os,sys,random

import pygame
from pygame.constants import *

import utils
from SPConstants import *
import SPSpriteUtils

# containers that can be used globally to store stuff
class Img:
    pass
class Snd:
    pass

CYELLOW = 1
CRED = 2
CBLUE = 3
CGREEN = 4

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
        self.logger =  logging.getLogger("schoolsplay.simon_sp.Activity")
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
        self.language = self.SPG.get_localesetting()[0][:2]
        self.sequence = []
        self.all_choices=[1,2,3,4]
        self.clicked_colors=[]
        self.clickingEnabled=0
        self.sequenceReady=0
    
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
    
    def start(self):
        """Mandatory method."""
        backdir = os.path.join(self.my_datadir,'backgrounds', self.language)
        self.yellow_sound = utils.load_sound(os.path.join(self.my_datadir,'1.ogg'))
        self.red_sound = utils.load_sound(os.path.join(self.my_datadir,'2.ogg'))
        self.blue_sound = utils.load_sound(os.path.join(self.my_datadir,'3.ogg'))
        self.green_sound = utils.load_sound(os.path.join(self.my_datadir,'4.ogg'))
        self.good_sound=utils.load_sound(os.path.join(self.my_datadir,'good.ogg'))
        self.wrong_sound=utils.load_sound(os.path.join(self.my_datadir,'wrong.ogg'))
        self.backgr_normal = utils.load_image(os.path.join(backdir,'background.png'))
        self.backgr_start = utils.load_image(os.path.join(backdir,'background_start.png')) 
        self.backgr_tussen = utils.load_image(os.path.join(backdir,'background_repeat.png'))
        self.backgr_good = utils.load_image(os.path.join(backdir,'background_correct.png'))
        self.backgr_wrong = utils.load_image(os.path.join(backdir,'background_wrong.png'))
        self.yellow_image = utils.load_image(os.path.join(self.my_datadir,'yellow.png'))
        self.red_image = utils.load_image(os.path.join(self.my_datadir,'red.png'))
        self.blue_image = utils.load_image(os.path.join(self.my_datadir,'blue.png'))
        self.green_image = utils.load_image(os.path.join(self.my_datadir,'green.png'))
        # lookup hash for the sounds dbase field, see generate_sequence for the
        # number of sounds in each level
        self.level_sounds_hash = {1:2, 2:3, 3:3, 4:4, 5:5, 6:6}
        self.scoredisplay.clear_score()
    
    def pre_level(self, level):
        """Mandatory method"""
        pass

    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        self.logger.debug("next_level called with %s" % level)
        if level > 6: return False # We only have 6 levels
        
        # db_mapper is a Python class object that provides easy access to the 
        # dbase.
        self.dbmapper = dbmapper
        self.throws = 0
        self.level=level
        self.levelupcount = 0
        self.dbmapper.insert('sounds', self.level_sounds_hash[level])
        self.score = 0
        self.started = 0
        # reset the screen to clear any crap from former levels
        self.clear_screen()

        self.screen.blit(self.backgr_start, (0+15+self.xMargin,0+self.yTop+15))
        pygame.display.update()
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
        #m,s = timespend.split(':')
        #seconds = int(m)*60 + int(s)
        # TODO: when doing new score and dbase stuff, see the loop as we determine
        # dbase field by dividing self.score by a hardcode value. (just a quick fix) 
        return self.score
    
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
    
    def loop(self,events):
        """Mandatory method.
        This is the main eventloop called by the core 30 times a minute."""
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                pos = pygame.Rect(pygame.mouse.get_pos() + (4,4))
                x=pos[0]
                y=pos[1]
                if y > 500 : break;
                elif self.started==0:
                    self.started=1
                    self.screen.blit(self.backgr_normal, (0+15+self.xMargin,0+self.yTop+15)) # this is needed here, as CP calls the start (and 
                    pygame.display.update()
                    pygame.time.delay(300)
                    pygame.event.clear()
                    self.sequenceReady=1
                    self.start_sequence()
                elif self.sequenceReady==0 and self.started==1:
                    self.screen.blit(self.backgr_normal,(0+15+self.xMargin,0+self.yTop+15))
                    pygame.display.update()
                    self.sequenceReady=1
                elif self.clickingEnabled==0 and self.started==1:   #code for tussenscherm 
                    self.clickingEnabled=1
                    self.screen.blit(self.backgr_normal,(0+15+self.xMargin,0+self.yTop+15))
                    pygame.display.update()
                elif self.clickingEnabled==1:
                    #find out if the mouse is above one of the buttons
                    #lefttop
                    if x > -4+self.xMargin and y > 24+self.yTop and x < 400+self.xMargin and y < 244+self.yTop:
                        self.blue_clicked()
                    #righttop
                    if x > 404+self.xMargin and y > 24+self.yTop and x < 800+self.xMargin and y < 244+self.yTop:
                        self.red_clicked()
                    #leftbottem    
                    if x > -4+self.xMargin and y > 247+self.yTop and x < 400+self.xMargin and y < 600:
                        self.yellow_clicked()
                    #rightbottem    
                    if x > 404+self.xMargin and y > 247+self.yTop and x < 800+self.xMargin and y < 600:
                        self.green_clicked()

                    #evaluate clicked colors right now (should maybe be triggerd from the color_clicked() methods..)
                    if self.sequence==self.clicked_colors: 
                        self.logger.debug("Correct sequence entered")
                        self.score += 50
                        self.levelupcount += 1
                        self.scoredisplay.set_score(self.score)
                        self.clickingEnabled=0
                        self.clicked_colors=[]
                        self.screen.blit(self.backgr_good,(0+15+self.xMargin,0+self.yTop+15))
                        pygame.display.update()
                        self.good_sound.play()
                        pygame.time.delay(2000)
                        if self.throws==4:
                            self.dbmapper.insert('result', self.score/50) 
                            # TODO:fix score 
                            if self.levelupcount == self.throws or \
                                self.levelupcount >= int(self.rchash[self.theme]['autolevel_value']):
                                levelup = 1
                            else:
                                levelup = 0
                            self.SPG.tellcore_level_end(store_db=True,\
                                            next_level=min(6, self.level + levelup), \
                                            levelup=levelup) 
                        else:
                            self.started=0
                            self.throws+=1
                            self.screen.blit(self.backgr_start,(0+15+self.xMargin,0+self.yTop+15))
                            pygame.display.update()
                    elif self.clicked_colors!=self.sequence[:len(self.clicked_colors)]:
                        self.logger.debug("Bad sequence entered")
                        self.score = max(0, (self.score - 50)) 
                        #if self.levelupcount > 0: self.levelupcount -= 1
                        self.clickingEnabled=0
                        self.clicked_colors=[]
                        self.screen.blit(self.backgr_wrong,(0+15+self.xMargin,0+self.yTop+15))
                        pygame.display.update()
                        self.wrong_sound.play()
                        pygame.time.delay(2000)
                        pygame.event.clear()
                        if self.throws==4: 
                            # TODO:fix score 
                            self.dbmapper.insert('result', self.score/50)
                            self.SPG.tellcore_level_end(store_db=True) 
                        else:
                            self.started=0
                            self.throws+=1
                            self.screen.blit(self.backgr_start,(0+15+self.xMargin,0+self.yTop+15))
                            pygame.display.update()
                    else: 
                        pass
                else: 
                    break
        return 
        
    def start_sequence(self):        
        self.sequence=self.generate_sequence()
        self.logger.debug("generated sequence:%s" % self.sequence)
        self.play_sequence()

    def play_sequence(self):
        pygame.time.delay(1000)
        self.logger.debug("Playing sequence")
        for color in self.sequence:
            if color==CYELLOW: self.yellow_clicked()
            if color==CRED: self.red_clicked()
            if color==CBLUE: self.blue_clicked()
            if color==CGREEN: self.green_clicked()
            self.screen.blit(self.backgr_normal, (0+15+self.xMargin,0+self.yTop+15)) # this is needed here, as CP calls the start (and 
            pygame.display.update()
            pygame.time.delay(500)

        pygame.event.clear()
        self.screen.blit(self.backgr_tussen,(0+15+self.xMargin,0+self.yTop+15))
        pygame.display.update()
        self.clickingEnabled=1

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

    def yellow_clicked(self):
        if self.clickingEnabled==1: 
            self.clicked_colors.append(CYELLOW)
        self.screen.blit(self.yellow_image,(14+self.xMargin,245+self.yTop))
        pygame.display.update()
        self.yellow_sound.play()
        pygame.time.delay(600)
        pygame.event.clear()
        self.screen.blit(self.backgr_normal, (0+15+self.xMargin,0+self.yTop+15)) # this is needed here, as CP calls the start (and 
        pygame.display.update()

    def red_clicked(self):
        self.screen.blit(self.red_image,(404+self.xMargin,16+self.yTop))
        pygame.display.update()
        self.red_sound.play()
        if self.clickingEnabled==1: 
            self.clicked_colors.append(CRED)
        pygame.time.delay(600)
        pygame.event.clear()
        self.screen.blit(self.backgr_normal, (0+15+self.xMargin,0+self.yTop+15)) # this is needed here, as CP calls the start (and 
        pygame.display.update()

    def blue_clicked(self):
        self.screen.blit(self.blue_image,(14+self.xMargin,16+self.yTop))
        pygame.display.update()
        self.blue_sound.play()
        if self.clickingEnabled==1: 
            self.clicked_colors.append(CBLUE)
        pygame.time.delay(600)
        pygame.event.clear()
        self.screen.blit(self.backgr_normal, (0+15+self.xMargin,0+self.yTop+15)) # this is needed here, as CP calls the start (and 
        pygame.display.update()
        
    def green_clicked(self):
        self.screen.blit(self.green_image,(404+self.xMargin,245+self.yTop))
        pygame.display.update()
        self.green_sound.play()
        if self.clickingEnabled==1: 
            self.clicked_colors.append(CGREEN)
        pygame.time.delay(600)
        pygame.event.clear()
        self.screen.blit(self.backgr_normal, (0+15+self.xMargin,0+self.yTop+15)) # this is needed here, as CP calls the start (and 
        pygame.display.update()
