# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zytkiewicz stas.zytkiewicz@schoolsplay.org
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
# self.logger =  logging.getLogger("childsplay.findit_sp.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("childsplay.findit_sp")

# standard modules you probably need
import os, sys, random

import pygame
from pygame.constants import *

import utils
from SPConstants import *
import SPSpriteUtils
from SPWidgets import ImgButton, TransPrevNextButton, PrevNextButton, SimpleTransImgButton

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
        Img_Display.wrongs = 0
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
            
            return True
            
    def set_position(self, x, y):
        self.rect.move_ip(x, y)
        self.ImgOffset = (x, y)

    def register_observer(self, obs):
        self.obs = obs
    
    def notify_observer(self, k, r):
        self.obs(k, r,self.wrongpos_y)
    
    def observer(self, k, r, wrongpos_y):
        #self.logger.debug("%s.observer called" % self.name)
        self.wrongpos_y = wrongpos_y
        pygame.display.update(pygame.draw.rect(self.image, RED, r.inflate(-self.offset, -self.offset), 10))
        self.display_sprite()
        if self.RectHash.has_key(k):
            del self.RectHash[k]
        
    def callback(self,sprite,event,*args):
        #self.logger.debug("%s.callback called" % self.name)
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
            if Img_Display.wrongs*2 < self.maxwrong*2 or self.maxwrong == -1:
                Img_Display.wrongs += 1
                if self.wrongsprite:
                    self.wrongsprite.display_sprite((self.wrongpos_x, self.wrongpos_y))
                self.wrongpos_y += 50
                self.wrongsnd.play()
            else:
                return True
        if not self.RectHash:
            return True
    
    def draw_diff(self, k, r):
        self.goodsnd.play()
        self.points += 1
        pygame.display.update(pygame.draw.rect(self.image, RED, r.inflate(-self.offset, -self.offset), 10))
        self.display_sprite()
        try:
            del self.RectHash[k]
            del self.RectHashCollide[(r[0], r[1], r[2], r[3])]
        except KeyError:
            pass
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
        self.logger =  logging.getLogger("childsplay.findit_sp.Activity")
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
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','Findit_spData')
        self.rchash = utils.read_rcfile(os.path.join(self.my_datadir, 'findit.rc'))
        self.rchash['theme'] = self.theme
        self.logger.debug("found rc: %s" % self.rchash)
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.CPdatadir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        self.DbAssets = os.path.join(self.SPG.get_libdir_path(),'CPData', 'DbaseAssets')
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

    def get_moviepath(self):
        movie = os.path.join(self.my_datadir,'help.avi')
        return movie

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
        p = os.path.join(self.CPdatadir,'good_%s.png' % self.lang)
        if not os.path.exists(p):
            p = os.path.join(self.CPdatadir,'thumbs.png')
        self.ThumbsUp = SPSpriteUtils.MySprite(utils.load_image(p))

        i = utils.load_image(os.path.join(self.my_datadir, 'hint.png'))
        i_ro = utils.load_image(os.path.join(self.my_datadir, 'hint_ro.png'))
        self.HintBut = SimpleTransImgButton(i,i_ro, (370, 200))
        if int(self.rchash[self.theme]['show_errors']):
            self.wrongImg = SPSpriteUtils.MySprite(utils.load_image(os.path.join(self.my_datadir, 'incorrect.png')))
        else:
            self.wrongImg = None
        prev = os.path.join(self.my_datadir, 'findit_prev.png')
        prev_ro = os.path.join(self.my_datadir, 'findit_prev_ro.png')
        next = os.path.join(self.my_datadir, 'findit_next.png')
        next_ro = os.path.join(self.my_datadir, 'findit_next_ro.png')
        self.prevnextBut = TransPrevNextButton((370, 460), \
                                              self._cbf_prevnext_button, \
                                              prev, prev_ro, next, next_ro)
        self.imgdir = os.path.join(self.my_datadir, 'images', self.theme)
        if not os.path.exists(self.imgdir):
            self.imgdir = os.path.join(self.my_datadir, 'images','default')                                      
        self.score = 0
        self.AreWeDT = False
        # get language code
        loclang = utils.get_locale_local()[0]
        
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
        if level > 6: return False # We only have 5 levels
        self.rchash['level'] = level
        self.levelupcount = 1
        self.done = 0
        self.dbscore = 0
        # db_mapper is a Python class object that provides easy access to the 
        # dbase.
        self.dbmapper = dbmapper
        # TODO: are the number of differences the same for each level ? We now have 3 hardcoded
        self.dbmapper.insert('total_diffs', int(self.rchash[self.theme]['exercises'])*3)
        self.totalwrongs = 0
        self.level = level
        self.actives.empty()
        self.clear_screen()
        self.previous_screen = None
        if self.blit_pos[1] == 0:
            y = 10
        else:
            y = 110
        Img_Display.wrongs = 0
        Img_Display.points = 0
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
        # M = Maximum score (number of differences * total images)
        # P = Users result in points
        # F = Fraction of total result related to points. (maximum result is 10)
        # F1 = Fraction of result related to time
        # C = multiplier
        # S = time spend in seconds
        M = float(3 * int(self.rchash[self.theme]['exercises']) * self.level)
        P = float(self.dbscore)
        F = 7.0
        F1 = 3.0
        C = 0.2
        S = float(seconds)
        points = max((F/100) * (P/(M / 100)), 1.0)
        time = min(F1 / ((S / (M * 2)) ** C), F1)
        self.logger.info("@scoredata@ %s level %s M %s P %s S %s points %s time %s" %\
                          (self.get_name(),self.level, M, P, S, points, time))
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

    def loop(self,events):
        """Mandatory method.
        This is the main eventloop called by the core 30 times a minute."""
        for event in events:
            if event.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION):
                if self.actives.update(event):
                    self.end_exercise()
                    pygame.event.clear()
                    break
        return 
        
    def _cbf_prevnext_button(self, sprite, event, data):
        self.logger.debug('_cbf_prevnext_button called with: %s' % data[0])
        if data[0] == 'prev': 
            self._cbf_prev_button(data)
        else: 
            self._cbf_next_button(data)
    
    def _cbf_next_button(self, data):
        self.logger.debug("_cbf_next_button: %s" % data)
        if not self.previous_screen:
            return
        self.clear_screen()
        self.actives.add(self.currentlist)
        for s in self.currentlist:
            s.display_sprite()
        self.prevnextBut.toggle()
        self.HintBut.display_sprite()
        self.actives.add(self.HintBut)
          
    def _cbf_prev_button(self, data):
        self.logger.debug("_cbf_prev_button: %s" % data)
        self.actives.remove(self.currentlist)
        self.HintBut.erase_sprite()
        self.actives.remove(self.HintBut)
        pygame.display.update(self.screen.blit(self.previous_screen, (0, self.blit_pos[1])))
        self.prevnextBut.toggle()
        
    def end_exercise(self, thumbs=True): 
        
        result = self.ImgA.get_result()
        
        self.logger.debug("got score from ImgA, points: %s, wrongs: %s" % (result[0], result[1]))
        self.totalwrongs += result[1]
        self.dbscore = (result[0] - result[1]) * self.level
        self.score += self.dbscore * 10
        self.scoredisplay.set_score(self.score)
        # TODO: we have hardcoded a check for the amount of wrongs iso rc file values.
        if self.totalwrongs < 4:
            levelup = 1
        else:
            levelup = 0
        self.actives.empty()
        if self.currentlist and not self.AreWeDT:
            self.previous_screen = pygame.Surface((800, 500))
            surf = pygame.display.get_surface()
            self.previous_screen.blit(surf, (0, 0), (0, self.blit_pos[1], 800, 500))
        utils.sleep(2000)
        if not result[0] == self.LevelScoreHash[self.level]:
            thumbs = False
            self.clear_screen()
        if thumbs:
            self.clear_screen()
            self.ThumbsUp.display_sprite((229, 120))
            utils.sleep(2000)
            self.ThumbsUp.erase_sprite()
        if not self.ImgDiffHash or self.done == int(self.rchash[self.theme]['exercises']):
            self.dbmapper.insert('wrongs', self.totalwrongs)
            if self.AreWeDT:
                self.SPG.tellcore_level_end(level=self.level)
            else:
                self.SPG.tellcore_level_end(store_db=True, \
                                    level=min(6, self.level), \
                                    levelup=levelup)
        else:
            self.start_exercise()
      
    def start_exercise(self):
        if self.blit_pos[1] == 0:
            y = 10
        else:
            y = 110
        
        k = random.choice(self.ImgDiffHash.keys())
        
        v = self.ImgDiffHash[k]
        del self.ImgDiffHash[k]
        ImgA = Img_Display(utils.load_image(k+'A.jpg'), v,\
                                     (self.GoodSound, self.WrongSound), self.wrongImg, self.rchash)
        ImgA.set_position(15, y)
        ImgA.name = 'ImgA'# needed for debugging only
        ImgB = Img_Display(utils.load_image(k+'B.jpg'), v,\
                                 (self.GoodSound, self.WrongSound), self.wrongImg, self.rchash)
        ImgB.set_position(435, y)
        ImgB.name = 'ImgB'
        ImgA.register_observer(ImgB.observer)
        ImgB.register_observer(ImgA.observer)
        self.currentlist = [ImgA, ImgB]
        self.HintBut.connect_callback(ImgA.show_hint, MOUSEBUTTONUP, self)
        self.HintBut.display_sprite()
        #self.prevnextBut.enable(False)
        self.actives.add(self.HintBut)
        self.actives.add([ImgA, ImgB])
        if self.previous_screen and not self.AreWeDT:
            self.actives.add(self.prevnextBut.get_actives())
            self.prevnextBut.enable(True)
        self.actives.redraw()
        self.ImgA, self.ImgB = ImgA, ImgB
        self.done += 1
    
    
