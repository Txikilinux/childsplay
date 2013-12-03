
# -*- coding: utf-8 -*-

# Copyright (c) 2013 Stas Zytkiewicz stas.zytkiewicz@gmail.com
# Copyright (c) 2013 Ana Lopes anajoaolopes@gmail.com
# Copyright (c) 2013 Helder Costa h24costa@gmail.com
# Copyright (c) 2013 Rui Bento rui.m.bento@gmail.com
#
#           BlockBreaker.py
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
# self.logger =  logging.getLogger("schoolsplay.BlockBreaker.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("schoolsplay.BlockBreaker")

# standard modules you probably need
import os,sys, random, math

import pygame
from pygame.constants import *

import utils
from SPConstants import *
import SPSpriteUtils

class Activity:
    level = 0
    angle_var = 30 #Variation angle when the ball hit the base
    pontos = 0
    nv_comp = 0
    pos_x = 0
    pos_y = 0

    # Define the colors we will use in RGB format
    BLUE1 =  (  13,   52, 169)
    BLUE2 =  (  44,   83, 203)
    BLUE3 =  (  133,   161, 242)
    GREEN1 = ( 12, 114, 15)
    GREEN2 = (  50, 191,   55)
    GREEN3 = (  134, 236,   138)
    ORANGE1 = (  198, 59,   4)
    ORANGE2 = (  239, 105,   9)
    ORANGE3 = (  245, 160,   99)
    GRAY1 = (  115, 115,   115)
    GRAY2 = (  175, 175,   175)

    # Player Base
    player = pygame.Rect(350, 570, 90, 10)

    #Blocks
    blocks = []

    # set up movement variables
    moveLeft = False
    moveRight = False

    # Base speed
    BaseSpeed = 5

    # Ball
    Ball_x = 400
    Ball_y = 560
    Ball_angle = random.randint(45, 135)
    Ball_speed = 5
    
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
        self.logger =  logging.getLogger("schoolsplay.BlockBreaker.Activity")
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
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','BlockbreakerData')
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.CPdatadir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        # Location of the alphabet sounds dir
        self.absdir = self.SPG.get_absdir_path()# alphabet sounds dir
        self.rchash = utils.read_rcfile(os.path.join(self.my_datadir, 'BlockBreaker.rc'))
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
        return _("Blockbreaker")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "BlockBreaker"
    
    def get_help(self):
        """Mandatory methods"""
        text = ["Objective:",
        " ",
        "Try to complete, first, a row of 3 matching symbols,",
        "horizontally, vertically or diagonally.",
        " ",
        "Tip:",
        " ",
        "If your opponent has two symbols on the same line,",
        "you must put your symbol on that line to block him.",
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
        #Define nivel
        pass
   
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
        self.level = level
        self.next_exercise()

        return True
    
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

    def next_exercise(self):

        self.Ball_x = 400
        self.Ball_y = 560
        self.Ball_angle = random.randint(45, 135)

        self.Ball_speed = 5 + self.level * 1
        self.BaseSpeed  = 5 + self.level * 1

        self.player.left = 400 - self.player.width / 2

        # remove all elements from array
        for block in self.blocks[:]:
            self.blocks.remove(block)

        if self.level == 1:
            for i in range(8):
                self.blocks.append({'block':pygame.Rect(22 + i * 96, 120, 86, 30), 'color':self.GREEN1})
            for i in range(7):
                self.blocks.append({'block':pygame.Rect(65 + i * 96, 160, 86, 30), 'color':self.GREEN2})
            for i in range(8):
                self.blocks.append({'block':pygame.Rect(22 + i * 96, 200, 86, 30), 'color':self.GREEN3})

        if self.level == 2:
            for i in range(11):
                self.blocks.append({'block':pygame.Rect(18 + i * 70, 136, 64, 25), 'color':self.ORANGE1})
            for i in range(10):
                self.blocks.append({'block':pygame.Rect(50 + i * 70, 168, 64, 25), 'color':self.ORANGE2})
            for i in range(11):
                self.blocks.append({'block':pygame.Rect(18 + i * 70, 200, 64, 25), 'color':self.ORANGE3})

        if self.level == 3:
            for i in range(15):
                self.blocks.append({'block':pygame.Rect(22 + i * 51, 125, 45, 20), 'color':self.BLUE1})
            for i in range(14):
                self.blocks.append({'block':pygame.Rect(44 + i * 51, 150, 45, 20), 'color':self.BLUE2})
            for i in range(15):
                self.blocks.append({'block':pygame.Rect(22 + i * 51, 175, 45, 20), 'color':self.BLUE3})
            for i in range(14):
                self.blocks.append({'block':pygame.Rect(44 + i * 51, 200, 45, 20), 'color':WHITE})

        if self.level == 4:
            for i in range(5):
                self.blocks.append({'block':pygame.Rect(277 + i * 51, 150, 45, 20), 'color':self.BLUE1})
            for i in range(9):
                self.blocks.append({'block':pygame.Rect(175 + i * 51, 175, 45, 20), 'color':self.ORANGE2})
            for i in range(13):
                self.blocks.append({'block':pygame.Rect(73 + i * 51, 200, 45, 20), 'color':self.GREEN3})
            for i in range(9):
                self.blocks.append({'block':pygame.Rect(175 + i * 51, 225, 45, 20), 'color':self.ORANGE2})
            for i in range(5):
                self.blocks.append({'block':pygame.Rect(277 + i * 51, 250, 45, 20), 'color':self.BLUE1})

        if self.level == 5:
            for i in range(15):
                self.blocks.append({'block':pygame.Rect(22 + i * 51, 125, 45, 20), 'color':self.GRAY1})
            for i in range(14):
                self.blocks.append({'block':pygame.Rect(44 + i * 51, 150, 45, 20), 'color':self.GREEN1})
            for i in range(15):
                self.blocks.append({'block':pygame.Rect(22 + i * 51, 175, 45, 20), 'color':self.GREEN2})
            for i in range(14):
                self.blocks.append({'block':pygame.Rect(44 + i * 51, 200, 45, 20), 'color':self.GRAY1})

        if self.level == 6:
            for i in range(3):
                self.blocks.append({'block':pygame.Rect(22 + i * 51, 150, 45, 20), 'color':self.GRAY1})
            for i in range(3):
                self.blocks.append({'block':pygame.Rect(628 + i * 51, 150, 45, 20), 'color':self.GRAY1})
            for i in range(5):
                self.blocks.append({'block':pygame.Rect(44 + i * 51, 175, 45, 20), 'color':self.ORANGE2})
            for i in range(5):
                self.blocks.append({'block':pygame.Rect(504 + i * 51, 175, 45, 20), 'color':self.ORANGE2})
            for i in range(7):
                self.blocks.append({'block':pygame.Rect(22 + i * 51, 200, 45, 20), 'color':self.GRAY1})
            for i in range(7):
                self.blocks.append({'block':pygame.Rect(424 + i * 51, 200, 45, 20), 'color':self.GRAY1})                
            for i in range(5):
                self.blocks.append({'block':pygame.Rect(44 + i * 51, 225, 45, 20), 'color':self.ORANGE2})
            for i in range(5):
                self.blocks.append({'block':pygame.Rect(504 + i * 51, 225, 45, 20), 'color':self.ORANGE2})                
            for i in range(3):
                self.blocks.append({'block':pygame.Rect(22 + i * 51, 250, 45, 20), 'color':self.GRAY1})
            for i in range(3):
                self.blocks.append({'block':pygame.Rect(628 + i * 51, 250, 45, 20), 'color':self.GRAY1})


    def GameArea(self):
        # move the Player Base
        if self.moveLeft:
            self.player.left -= self.BaseSpeed
            if self.player.left < 10:
                self.player.left = 10
        if self.moveRight:
            self.player.right += self.BaseSpeed
            if self.player.right > 790:
                self.player.right = 790

        # move the Ball on x axis
        self.Ball_x = self.Ball_x + self.Ball_speed * math.cos( self.Ball_angle * math.pi / 180)

        # check if the ball hit left side
        if self.Ball_x <= 25 + self.Ball_speed:
            if self.Ball_angle < 180:
                self.Ball_angle = 180 - self.Ball_angle
            else:
                self.Ball_angle = 270 + 270 - self.Ball_angle

        # check if the ball hit right side
        if self.Ball_x >= 775 - self.Ball_speed:
            if self.Ball_angle < 90:
                self.Ball_angle = 180 - self.Ball_angle
            else:
                self.Ball_angle = 270 + 270 - self.Ball_angle

        # move the Ball on y axis
        self.Ball_y = self.Ball_y - self.Ball_speed * math.sin( self.Ball_angle * math.pi / 180)

        # check if the ball hit the top the screen
        if self.Ball_y <= 110 + self.Ball_speed:
            self.Ball_angle = 360 - self.Ball_angle

        # check if the ball hit the bottom of the screen
        if self.Ball_y >= 585 - self.Ball_speed:
            self.player.left = 400 - self.player.width / 2
            self.Ball_x = 400
            self.Ball_y = 560
            self.Ball_angle = random.randint(45, 135)
            self.moveLeft = False
            self.moveRight = False

        # check if the ball hit the player base
        if self.Ball_angle > 180:
            if self.Ball_x + 10 > self.player.left and self.Ball_x - 10 < self.player.right and self.Ball_y + 10 > self.player.top and self.Ball_y -10 < self.player.bottom:
                for i in range(0,100,10):

                    aux_x = self.Ball_x + 10 * math.cos( (270 + i) * math.pi / 180)
                    aux_y = self.Ball_y - 10 * math.sin( (270 + i) * math.pi / 180)

                    if self.player.collidepoint(aux_x, aux_y): 
                        if aux_y >= self.player.top and aux_y <= self.player.top + self.Ball_speed:
                            self.Ball_y = 560
                            self.Ball_angle = 360 - self.Ball_angle - ((self.Ball_x - (self.player.left + self.player.width / 2)) * 100 / ( self.player.width / 2 ) * self.angle_var /100)
                            break    
                        else:
                            self.Ball_angle = 270 + 270 - self.Ball_angle
                            self.player.left += self.Ball_speed
                            break

                    aux_x = self.Ball_x + 10 * math.cos( (270 - i) * math.pi / 180)
                
                    if self.player.collidepoint(aux_x, aux_y):
                        if aux_y >= self.player.top and aux_y <= self.player.top + self.Ball_speed:
                            self.Ball_y = 560
                            self.Ball_angle = 360 - self.Ball_angle - ((self.Ball_x - (self.player.left + self.player.width / 2)) * 100 / ( self.player.width / 2 ) * self.angle_var /100)
                            break    
                        else:
                            self.Ball_angle = 270 + 270 - self.Ball_angle
                            self.player.right -= self.Ball_speed
                            break

        # check if the ball hit the blocks
        if self.Ball_y < 250:
            for block in self.blocks[:]:
                for i in range(0, 360, 15):
                    aux_x = self.Ball_x + 10 * math.cos(i * math.pi / 180)
                    aux_y = self.Ball_y - 10 * math.sin(i * math.pi / 180)
                    if block['block'].collidepoint(aux_x, aux_y):
                        self.pontos += 1
                        if aux_x >= block['block'].left and aux_x <= block['block'].left + self.Ball_speed:
                            if block['color'] == self.GRAY1:
                                block['color'] = self.GRAY2
                            else:
                                self.blocks.remove(block)
                            if self.Ball_angle < 90:
                                self.Ball_angle = 180 - self.Ball_angle
                            else:
                                self.Ball_angle = 270 + 270 - self.Ball_angle
                            break
                        if aux_x <= block['block'].right and aux_x >= block['block'].right - self.Ball_speed:
                            if block['color'] == self.GRAY1:
                                block['color'] = self.GRAY2
                            else:
                                self.blocks.remove(block)
                            if self.Ball_angle < 180:
                                self.Ball_angle = 180 - self.Ball_angle
                            else:
                                self.Ball_angle = 270 + 270 - self.Ball_angle
                            break
                        if aux_y >= block['block'].top and aux_y <= block['block'].top + self.Ball_speed:
                            if block['color'] == self.GRAY1:
                                block['color'] = self.GRAY2
                            else:
                                self.blocks.remove(block)
                            self.Ball_angle = 360 - self.Ball_angle
                            break
                        if aux_y <= block['block'].bottom and aux_y >= block['block'].bottom - self.Ball_speed:
                            if block['color'] == self.GRAY1:
                                block['color'] = self.GRAY2
                            else:
                                self.blocks.remove(block)
                            self.Ball_angle = 360 - self.Ball_angle
                            break
                

        # draw the black screen
        pygame.draw.rect(self.screen, BLACK, [10, 100, 780, 490])

        # draw the blocks
        for block in self.blocks[:]:
            pygame.draw.rect(self.screen, block['color'], block['block'])

        # draw the Player Base onto the surface
        pygame.draw.rect(self.screen, YELLOW, self.player)

        # draw the Ball onto the surface
        pygame.draw.circle(self.screen, RED, (int(self.Ball_x), int(self.Ball_y)), 10, 0)

        # check if numbers of blocks > 0
        if len(self.blocks) == 0:
            self.Ball_x = 400
            self.Ball_y = 560
            self.Ball_angle = random.randint(45, 135)
            self.moveLeft = False
            self.moveRight = False
            #self.niveis()
            self.level += 1
            if self.level == 7:
                self.level = 1
            self.next_exercise()

    def loop(self,events):
        """Mandatory method.
        This is the main eventloop called by the core 30 times a minute."""
        for event in events:
            if event.type is MOUSEBUTTONDOWN:
                pass
                # call your objects
            if event.type == KEYDOWN:
                # change the keyboard variables
                if event.key == K_LEFT:
                    self.moveRight = False
                    self.moveLeft = True
                if event.key == K_RIGHT:
                    self.moveLeft = False
                    self.moveRight = True
            if event.type == KEYUP:
                if event.key == K_LEFT:
                    self.moveLeft = False
                if event.key == K_RIGHT:
                    self.moveRight = False

        self.GameArea()

        pygame.display.flip()
        return 
        
