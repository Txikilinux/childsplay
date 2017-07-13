# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zytkiewicz stas.zytkiewicz@gmail.com
#
#           findit_sp.py
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
# self.logger =  logging.getLogger("schoolsplay.findit_sp.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("schoolsplay.findit_sp")

# standard modules you probably need
import os, sys, random

import pygame
from pygame.constants import *

import utils
from SPConstants import *
import SPSpriteUtils
from SPWidgets import ImgButton, TransPrevNextButton, PrevNextButton

class Img_Display(SPSpriteUtils.SPSprite):
    """Object that displays an image at a determined position and reacts to mouseclicks.
    It accepts rects for the differences and provides methods to do stuff with the rects."""
    points = 0
    wrongs = 0
    def __init__(self, image, rectlist, snd, wrongsprite, rchash):
        self.logger = logging.getLogger('schoolsplay.findit_sp.Img_Display')
        SPSpriteUtils.SPSprite.__init__(self, image)
        self.connect_callback(self.callback, MOUSEBUTTONDOWN)
        self.goodsnd, self.wrongsnd = snd        
        self.wrongsprite = wrongsprite
        theme = rchash['theme']
        self.maxwrong = int(rchash[theme]['wrongs'])

        i = 0
        self.offset = int(rchash[theme]['wrong_rect_offset_%s' % rchash['level']]) * 2
        
        self.RectHash = {}
        # This will become a hash with rect style tuples as keys because pygame rects aren't hashable
        self.RectHashCollide = {}
        for r in rectlist:
            tempr = r.inflate(self.offset, self.offset)
            self.RectHash[i] = tempr
            i += 1
            self.RectHashCollide[(tempr[0], tempr[1], tempr[2], tempr[3])] = i
        pygame.draw.rect(self.image, BLACK, self.rect, 4)
        self.wrongpos_x = 375
        self.wrongpos_y = 320
                
    def show_hint(self, widget, event, data):
        k, r = random.choice(self.RectHash.items())
        Img_Display.points -= 1
        if Img_Display.points < 0:
            Img_Display.points = 0
        self.draw_diff(k, r)
        # needed as we draw on the sprite which is updated already by the parentclass 
        # and when we the last hint our parent is never updated.
        self.display_sprite()
        if not self.RectHash:
            data[0].end_exercise()
            
    def set_position(self, x, y):
        self.rect.move_ip(x, y)
        self.ImgOffset = (x, y)

    def register_observer(self, obs):
        self.obs = obs
    
    def notify_observer(self, k, r):
        self.obs(k, r,self.wrongpos_y)
    
    def observer(self, k, r, wrongpos_y):
        self.logger.debug("%s.observer called" % self.name)
        self.wrongpos_y = wrongpos_y
        pygame.display.update(pygame.draw.rect(self.image, GREEN, r.inflate(-self.offset, -self.offset), 5))
        self.display_sprite()
        del self.RectHash[k]
        
    def callback(self,sprite,event,*args):
        self.logger.debug("%s.callback called" % self.name)
        goodflag = False
        mouserect = pygame.Rect(event.pos[0] - self.ImgOffset[0], \
                              event.pos[1] - self.ImgOffset[1], \
                              4, 4)
        mousepos = mouserect.topleft
        colliderects = mouserect.collidedictall(self.RectHashCollide)
        templist = []
        for item in colliderects:
            r = item[0]
            i = item[1]
            d = utils.calcdist(mousepos, pygame.Rect(*r).center)
            templist.append((d, (r, i)))
        templist.sort()
        if templist:
            target = templist[0][1]
            Img_Display.points += 1
            self.draw_diff(target[1]-1, pygame.Rect(target[0]))
            goodflag = True

        if not goodflag:
            if Img_Display.wrongs*2 < self.maxwrong*2:
                Img_Display.wrongs += 1
                self.wrongsprite.display_sprite((self.wrongpos_x, self.wrongpos_y))
                self.wrongpos_y += 50
                self.wrongsnd.play()
        if not self.RectHash:
            return True
    
    def draw_diff(self, k, r):
        self.goodsnd.play()
        self.points += 1
        pygame.display.update(pygame.draw.rect(self.image, GREEN, r.inflate(-self.offset, -self.offset), 5))
        self.display_sprite()
        del self.RectHash[k]
        del self.RectHashCollide[(r[0], r[1], r[2], r[3])]
        self.notify_observer(k, r)
    
    def get_result(self):
        return (Img_Display.points, Img_Display.wrongs)
    
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
        self.logger =  logging.getLogger("schoolsplay.findit_sp.Activity")
        self.logger.info("Activity started")
        self.SPG = SPGoodies
        self.scoredisplay = self.SPG.get_scoredisplay()
        self.theme = self.SPG.get_theme()
        self.screen = self.SPG.get_screen()
        self.screenclip = self.SPG.get_screenclip()
        self.blit_pos = self.screenclip.left, self.screenclip.top
        self.orgscreen = pygame.Surface(self.screenclip.size) # we use this to restore the screen
        self.orgscreen.blit(self.screen, (0, 0), self.screenclip)
        self.backgr = self.SPG.get_background()
        # The location of the activities Data dir
        self.MyDatadir = os.path.join(self.SPG.get_libdir_path(),'CPData','Findit_spData')
        self.rchash = utils.read_rcfile(os.path.join(self.MyDatadir, 'findit.rc'))
        self.rchash['theme'] = self.theme
        self.logger.debug("found rc: %s" % self.rchash)
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.CPdatadir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        # Location of the alphabet sounds dir
        self.absdir = self.SPG.get_absdir_path()# alphabet sounds dir
        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special CPGroup
        self.actives = SPSpriteUtils.SPInit(self.screen,self.backgr)
        self.actives.set_onematch(True)
    
    def clear_screen(self):
        self.screen.blit(self.orgscreen,self.blit_pos)
        self.backgr.blit(self.orgscreen,self.blit_pos)
        pygame.display.update()
        for s in self.actives:
            s.display_sprite()

    def refresh_sprites(self):
        """Mandatory method, called by the core when the screen is used for blitting
        and the possibility exists that your sprites are affected by it."""
        self.actives.redraw()

    def get_helptitle(self):
        """Mandatory method"""
        return _("Findit")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "findit_sp"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),
                _("On the screen you will see two almost identical pictures.\nHowever, there are differences between the images."), 
                " ", 
                _("When you spot a difference, touch it with your finger.\nYou can click the question mark in the middle of the screen if you need a hint."), 
        " ",
        _("The arrows to the left take you to the previous image.")
        ]
        return text 
    
    def get_helptip(self):
        """Mandatory method, when no tips available returns an empty string"""
        return ''
        
    def get_helptype(self):
        """Mandatory method, you must set an type"""
        # Possible types are: Memory, Math, Puzzle, Keyboardtraining, Mousetraining
        #                     Language, Alphabet, Fun, Miscellaneous
        return _("Miscellaneous")
    
    
    def get_helplevels(self):
        """Mandatory method, must return a string with the number of levels
        in the follwing format:
        _("This level has %s levels") % number-of-levels"""
        return _("This activity has %s levels") % 6

    def start(self):
        """Mandatory method."""
        self.GoodSound=utils.load_sound(os.path.join(self.CPdatadir, 'good.ogg'))
        self.WrongSound=utils.load_sound(os.path.join(self.CPdatadir, 'wrong.ogg'))
        self.ThumbsUp = SPSpriteUtils.MySprite(utils.load_image(os.path.join(self.CPdatadir, 'thumbs.png')))
        self.HintBut = ImgButton(os.path.join(self.MyDatadir, 'hint.png'), (370, 200),name='hint')
        self.wrongImg = SPSpriteUtils.MySprite(utils.load_image(os.path.join(self.MyDatadir, 'incorrect.png')))
        self.prevnextBut = TransPrevNextButton((370, 260), \
                                              self._cbf_prevnext_button, \
                                              'findit_prev.png', \
                                              'findit_prev_ro.png',\
                                              'findit_next.png', \
                                              'findit_next_ro.png')
        
#        self.prevnextBut = PrevNextButton((370, 260), \
#                                              self._cbf_prevnext_button, \
#                                              'findit_prev.png', \
#                                              'findit_next.png', \
#                                              )                                   
        self.imgdir = os.path.join(self.MyDatadir, 'images', self.theme)
        if not os.path.exists(self.imgdir):
            self.imgdir = os.path.join(self.MyDatadir, 'images','default')                                      
        self.previous_list = []
        self.score = 0
        
    def pre_level(self, level):
        """Mandatory method"""
        pass

    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        self.logger.debug("next_level called with %s" % level)
        if level > 6: return False # We only have 5 levels
        self.rchash['level'] = level
        self.levelupcount = 0
        # db_mapper is a Python class object that provides easy access to the 
        # dbase.
        self.dbmapper = dbmapper
        # TODO: are the number of differences the same for each level ? We now have 3 hardcoded
        self.dbmapper.insert('total_diffs', int(self.rchash[self.theme]['exercises'])*3)
        self.totalwrongs = 0
        self.level = level
        self.actives.empty()
        self.clear_screen()
        
        if self.blit_pos[1] == 0:
            y = 10
        else:
            y = 110
        
        self.logger.debug("searching images in %s"  % self.imgdir)
        p = os.path.join(self.imgdir, 'img_diffs_%s.csv')
        self.ImgDiffHash = {}
        self.ImgDiffList = []
        try:
            lines = open(p % level, 'r').readlines()
        except IOError, info:
            raise utils.MyError, info
        for line in lines:
            k, v = line[:-1].split(';',1)
            try:
                self.ImgDiffHash[os.path.join(self.imgdir, k)] = \
                                [pygame.Rect(eval(x,{'__builtins__': None},\
                                {'True':True,'False':False})) for x in v.split(':')]
            except SyntaxError, info:
                self.logger.error('Badly formed rect line in %s; %s' % (p % level, line))
        self.LevelScoreHash = {1:3, 2:3, 3:3, 4:3, 5:3, 6:3}
        
        self.ImgDisplayList = []
        # TODO: pick a number of images based on the rc file value 
        for k, v in self.ImgDiffHash.items():
            self.ImgA = Img_Display(utils.load_image(k+'A.jpg'), v,\
                                     (self.GoodSound, self.WrongSound), self.wrongImg, self.rchash)
            self.ImgA.set_position(15, y)
            self.ImgA.name = 'ImgA'# needed for debugging only
            self.ImgB = Img_Display(utils.load_image(k+'B.jpg'), v,\
                                     (self.GoodSound, self.WrongSound), self.wrongImg, self.rchash)
            self.ImgB.set_position(435, y)
            self.ImgB.name = 'ImgB'
            self.ImgA.register_observer(self.ImgB.observer)
            self.ImgB.register_observer(self.ImgA.observer)
            self.ImgDisplayList.append((self.ImgA, self.ImgB))
        random.shuffle(self.ImgDisplayList)
        self.start_exercise()
        return True
        
    def post_next_level(self):
        """Mandatory method.
        This is called once by the core after 'next_level' *and* after the 321 count.
        You should place stuff in here that run in a seperate thread like sound play."""
        
    def get_score(self,timespend):
        """Mandatory method.
        @timespend is the time spend inside the level as it's calculated
        by the core.
        returns the score value for the past level.
        return None if no score value is used"""
        m,s = timespend.split(':')
        seconds = int(m)*60 + int(s)
        # TODO: score not yet ready
        self.score = 0
        return self.score
    
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
            if event.type in (MOUSEBUTTONDOWN, MOUSEMOTION):
                if self.actives.update(event):
                    self.end_exercise()
        return 
        
    def _cbf_prevnext_button(self, sprite, event, data):
        self.logger.debug('_cbf_prevnext_button called with: %s' % data[0])
        if data[0] == 'prev': self._cbf_prev_button(data)
        else: self._cbf_next_button(data)
    
    def _cbf_next_button(self, data):
        self.logger.debug("_cbf_next_button: %s" % data)
        if not self.previous_list:
            return
        self.clear_screen()
        self.actives.add(self.currentlist)
        for s in self.currentlist:
            s.display_sprite()
        self.prevnextBut.toggle()
        
          
    def _cbf_prev_button(self, data):
        self.logger.debug("_cbf_prev_button: %s" % data)
        self.actives.remove(self.currentlist)
        self.clear_screen()
        self.prevnextBut.toggle()
        for s in self.previous_list:
            s.display_sprite()
        

    def end_exercise(self, thumbs=True): 
        result = self.ImgA.get_result()
        
        self.logger.debug("got score from ImgA, points: %s, wrongs: %s" % (result[0], result[1]))
        self.totalwrongs += result[1]
        self.score += (result[0] - result[1]) * 10
        self.scoredisplay.set_score(self.score)
        # TODO: we have hardcoded a check for the amount of wrongs iso rc file values.
        if self.totalwrongs < 4:
            levelup = 1
        else:
            levelup = 0
        self.actives.empty()
        self.previous_list = self.currentlist[:]
        pygame.time.wait(2000)
        if not result[0] == self.LevelScoreHash[self.level]:
            thumbs = False
            self.clear_screen()
            #pygame.time.wait(2000)
        if thumbs:
            self.clear_screen()
            self.ThumbsUp.display_sprite((180, 100))
            pygame.time.wait(2000)
            self.ThumbsUp.erase_sprite()
        if not self.ImgDisplayList:
            self.dbmapper.insert('wrongs', self.totalwrongs)
            self.SPG.tellcore_level_end(store_db=True, \
                                        next_level=min(6, self.level + levelup), \
                                            levelup=levelup)
        else:
            self.start_exercise()
      
    def start_exercise(self):
        obj = self.ImgDisplayList.pop()
        self.currentlist = [obj[0], obj[1]]
        self.HintBut.connect_callback(obj[0].show_hint, MOUSEBUTTONDOWN, self)
        self.HintBut.display_sprite()
        #self.prevnextBut.enable(False)
        self.actives.add(self.HintBut)
        self.actives.add(obj)
        if self.previous_list:
           self.actives.add(self.prevnextBut.get_actives())
           self.prevnextBut.enable(True)
        self.actives.redraw()
        
    
    
