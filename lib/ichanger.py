# -*- coding: utf-8 -*-

# Copyright (c) 2010-2011 Stas Zytkiewicz stas.zytkiewicz@schoolsplay.org
#
#           ichanger.py
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
# self.logger =  logging.getLogger("childsplay.ichanger.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("childsplay.ichanger")

# standard modules you probably need
import os,sys, random, glob

import pygame
from pygame.constants import *

import utils
from SPConstants import *
import SPSpriteUtils
import SPWidgets
from SPHelpText import Act_ichanger
# containers that can be used globally to store stuff
class Img:
    pass
class Snd:
    pass

class Card(SPSpriteUtils.SPSprite):
    def __init__(self,closedcard,opencard,pos, observer, name):
        """This class has it's own callback function and it will connect itself"""
        SPSpriteUtils.SPSprite.__init__(self,opencard)
        self.rect.move_ip(pos)
        self.name = name
        self.closedimage = closedcard
        self.openimage = opencard.convert_alpha()
        self.observer = observer
        self.IMchanged = False
        self.wrongs = 0
        self.changed_image = None
        self.org_image = opencard.convert_alpha()
        self.newpos = pos
        self.orgpos = pos
        # connect to the MOUSEBUTTONDOWN event, no need for passing data
        self.connect_callback(self.callback,MOUSEBUTTONDOWN)
    
    def reset(self):
        self.openimage = self.org_image
        self.moveto(self.orgpos)
    
    def restart(self):
        self.moveto(self.newpos)
        if not self.IMchanged:
            self.openimage = self.org_image
        else:
            self.openimage = self.changed_image
        
            
    def close(self):
        self.image = self.closedimage
        self.display_sprite()
               
    def open(self):
        self.image = self.openimage
        self.display_sprite()
        
    def change_image(self):
        if not self.changed_image:
            return
        self.openimage = self.changed_image
        self.IMchanged = True
        
    def set_changed_image(self, image):
        self.changed_image = image
        
    def set_new_position(self, pos):
        self.moveto(pos)
        self.newpos = pos
                
    def callback(self,sprite,event,*args):
        if self.IMchanged:
            #print "correct"
            pygame.draw.rect(self.image,ROSYBROWN,self.image.get_rect(), 12)
            self.display_sprite()
            self.observer(True)
        else:
            self.wrongs += 1
            #print "wrong"
            self.close()
            self.disconnect_callback()
            self.observer(False)

class TextBox(SPSpriteUtils.SPSprite):
    def __init__(self, surf, pos):
        """This class has it's own callback function and it will connect itself"""
        SPSpriteUtils.SPSprite.__init__(self,surf)
        ai = Act_ichanger()
        self.textsurfs = []
        for txt in (ai.box1, ai.box2, ai.box3):
            s = SPWidgets.render_textrect(_(txt), 18, TTF, surf, WHITE, \
                              None, justification=0, \
                              autofit=False, border=0, padding=24)
            self.textsurfs.append(s)
        self.moveto(pos)
        
    def set_text(self, i):
        self.image = self.textsurfs[i]
        self.display_sprite()
                
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
        self.logger =  logging.getLogger("childsplay.ichanger.Activity")
        self.logger.info("Activity started")
        self.SPG = SPGoodies
        self.lang = self.SPG.get_localesetting()[0][:2]
        self.scoredisplay = self.SPG.get_scoredisplay()
        self.displayedscore = 0
        self.theme = self.SPG.get_theme()
        self.screen = self.SPG.get_screen()
        self.screenclip = self.SPG.get_screenclip()
        self.blit_pos = self.screenclip.left, self.screenclip.top
        self.orgscreen = pygame.Surface(self.screenclip.size) # we use this to restore the screen
        self.orgscreen.blit(self.screen, (0, 0), self.screenclip)
        self.backgr = self.SPG.get_background()
        # The location of the activities Data dir
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','IchangerData')
        self.rchash = utils.read_rcfile(os.path.join(self.my_datadir, 'ichanger.rc'))
        self.rchash['theme'] = self.theme
        self.my_rchash = self.rchash[self.theme]
        self.logger.debug("found rc: %s" % self.rchash)
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.CPdatadir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        # Location of the alphabet sounds dir
        self.absdir = self.SPG.get_absdir_path()# alphabet sounds dir
        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special CPGroup
        self.actives = SPSpriteUtils.SPInit(self.screen,self.backgr)
        
        imgdir = os.path.join(self.my_datadir,'images', self.theme)
        if not os.path.exists(imgdir):
            imgdir = os.path.join(self.my_datadir, 'images','childsplay')
        
        self.imagepaths_org = [f for f in glob.glob(os.path.join(imgdir, '*'))\
                            if os.path.basename(f) not in ('cardfront.png', 'cardback.png')]
        self.imagepaths = self.imagepaths_org[:]
        random.shuffle(self.imagepaths)
        self.opencard = utils.load_image(os.path.join(imgdir,'cardfront.png'))
        self.closedcard = utils.load_image(os.path.join(imgdir,'cardback.png'))
        
        boxsurf = utils.load_image(os.path.join(self.my_datadir,'box.png'))
        self.pausesnd = utils.load_music(os.path.join(self.CPdatadir,'pause_0_35.ogg'))
        self.good_sound=utils.load_music(os.path.join(self.CPdatadir,'good.ogg'))
        self.wrong_sound=utils.load_music(os.path.join(self.CPdatadir,'wrong.ogg'))
        p = os.path.join(self.CPdatadir,'good_%s.png' % self.lang)
        if not os.path.exists(p):
            p = os.path.join(self.CPdatadir,'thumbs.png')
        self.good_image = SPSpriteUtils.MySprite(utils.load_image(p))
        self.good_image.moveto((229,296))
        # Your top blit position, this depends on the menubar position
        if self.blit_pos[1] == 0:
            y = 10
        else:
            y = 110
        self.cardpositions = [(10, y), (260, y), (10, y+250), (260, y+250)]
        #self.start_pos = (600, 380 + y)
        self.but_pos = [(560, 420 + y), (700, 400+y)]
        boxpos = (510, y)
        self.box = TextBox(boxsurf, boxpos)
            
    def observer(self, result):
        self.logger.debug("observer called with %s" % result)
        if result:# correct card picked
            self.dbscore += (2 - self.WEcheat)
            self.actives.empty()
            self.EndExerciseFlag = True
            self.exercises -= 1
            self.displayedscore += 10 * 15
            self.levelupcount += 1
            self.scoredisplay.set_score(self.displayedscore)
            self.good_sound.play()
            self.good_image.display_sprite()
            pygame.time.wait(1500)
        else:
            self.dbscore -= 2
            if self.dbscore < 0:
                self.dbscore = 0
            self.displayedscore -= 10 * 50
            if self.displayedscore <= 0:
                self.displayedscore = 0
            self.levelupcount -= 1
            self.scoredisplay.set_score(self.displayedscore)
            self.wrong_sound.play()
            pygame.time.wait(1500)
            
    def _startbutton_cbf(self, sprite, *args):
        self.actives.remove(sprite)
        self.startbut.erase_sprite()
        if not self.WEcheat:
            for c in self.cardlist:
                c.close()
                c.change_image()
            if self.changepositions:
                positions = self.cardpositions[:len(self.cardlist)]
                random.shuffle(positions)
                for c in self.cardlist:
                    c.set_new_position(positions.pop())
        else:
            for c in self.cardlist:
                c.close()
                c.restart()
        self.pausesnd.play()
        pygame.time.wait(3500)
        
        for c in self.cardlist:
            c.open()
        self.actives.add(self.cardlist)
        self.actives.add(self.cheatbut)
        self.box.set_text(1)
        self.cheatbut.display_sprite()
    
    def _cheatbutton_cbf(self, sprite, *args):
        self.WEcheat = True
        self.actives.remove(sprite)
        self.cheatbut.erase_sprite()
        self.actives.empty()
        for c in self.cardlist:
            c.close()
            c.reset()
            pygame.time.wait(500)
        for c in self.cardlist:
            c.open()
        self.actives.add(self.startbut)
        self.box.set_text(2)
        self.startbut.display_sprite()        
    
    def clear_screen(self):
        self.screen.blit(self.orgscreen,self.blit_pos)
        self.backgr.blit(self.orgscreen,self.blit_pos)
        pygame.display.update()

    def get_moviepath(self):
        movie = os.path.join(self.my_datadir,'help.avi')
        return movie

    def refresh_sprites(self):
        """Mandatory method, called by the core when the screen is used for blitting
        and the possibility exists that your sprites are affected by it."""
        self.actives.redraw()

    def get_helptitle(self):
        """Mandatory method"""
        return _("Ichanger")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "ichanger"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),
                _("Several images from the past will appear on the screen.\nLook carefully at them and remember what you see."), 
        " ",
        _("Touch the 'START' button on the right.\nThe images will dissappear and when they return, one will have changed.\nTouch the picture which has changed."), 
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
        _("This level has %s levels") % number-of-levels"""
        return _("This activity has %s levels") % 4

    def start(self):
        """Mandatory method."""
        self.SPG.tellcore_set_dice_minimal_level(3)
        self.startbut = SPWidgets.SimpleButtonDynamic(_('Start'), self.but_pos[0], fsize=24, colorname='green')
        self.startbut.set_use_current_background(True)
        self.cheatbut = SPWidgets.SimpleButtonDynamic(_('Cheat'), self.but_pos[0], fsize=24, colorname='green')
        self.cheatbut.set_use_current_background(True)
        self.startbut.connect_callback(self._startbutton_cbf, MOUSEBUTTONDOWN)
        self.cheatbut.connect_callback(self._cheatbutton_cbf, MOUSEBUTTONDOWN)
        self.AreWeDT = False
        p = os.path.join(self.CPdatadir,'good_%s.png' % self.lang)
        if not os.path.exists(p):
            p = os.path.join(self.CPdatadir,'thumbs.png')
        self.ThumbsUp = SPSpriteUtils.MySprite(utils.load_image(p))
    
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
        if level > 4:
            return False
        self.level = level
        self.levelupcount = 1
        self.dbscore = 0
        # number of exercises in one level
        self.exercises = int(self.rchash[self.theme]['exercises'])
        self.actives.empty()
        self.changepositions = False
        # let the cards open until user hits start, then close them for some time, replace
        # image on one of the cards and show them again.
        self.next_exercise()
        return True
    
    def next_exercise(self):
        self.logger.debug("next_exercise called, exercises = %s" % (self.exercises))
        self.clear_screen()
        self.box.set_text(0)
        
        self.WEcheat = False
        self.EndExerciseFlag = False
        if not self.exercises:
            return True
        if self.level in (1, 2):
            if self.level == 2:
                self.changepositions = True
            num = 3
        else:
            if self.level == 4:
                self.changepositions = True
            num = 4
        if len(self.imagepaths) < num+1:
            self.imagepaths = self.imagepaths_org[:]
            random.shuffle(self.imagepaths)
        self.cardlist = []
        i = 0
        for i in range(num):
            f = self.imagepaths.pop()
            img = utils.load_image(f)
            c = self.opencard.convert_alpha()
            ix, iy = img.get_size()
            cx, cy = c.get_size()
            x = (cx - ix) / 2
            y = (cy - iy) / 2
            c.blit(img, (x, y))
            card = Card(self.closedcard, c, self.cardpositions[i], self.observer, f)
            card.display_sprite()
            self.cardlist.append(card)
            i += 1
        img = utils.load_image(self.imagepaths.pop())
        c = self.opencard
        ix, iy = img.get_size()
        cx, cy = c.get_size()
        x = (cx - ix) / 2
        y = (cy - iy) / 2
        c.blit(img, (x, y))
        card = random.choice(self.cardlist)
        card.set_changed_image(c)
        self.actives.add(self.startbut)
        self.startbut.display_sprite()
        
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
        # M = Maximum score (number of exercises * 2)
        # P = Users result in points
        # F = Fraction of total result related to points. (maximum result is 10)
        # F1 = Fraction of result related to time
        # C = multiplier
        # S = time spend in seconds
        M = float(int(self.my_rchash['exercises']) * 2)
        P = float(self.dbscore)
        F = 7.0
        F1 = 3.0
        C = 0.2
        S = float(seconds)
        points = max((F/100) * (P/(M / 100)), 1.0)
        time = min(F1 / ((S / (M * 2)) ** C), F1)
        self.logger.info("@scoredata@ %s level %s M %s P %s S %s points %s time %s" %\
                          (self.get_name(),self.level, M, P, S, points, time))
        score = points + time
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
            if event.type in (MOUSEBUTTONDOWN, MOUSEMOTION):
                self.actives.update(event)
            if not self.actives and self.EndExerciseFlag:
                self.clear_screen()
                pygame.time.wait(2000)
                if self.next_exercise():
                    self.clear_screen()
                    self.ThumbsUp.display_sprite((180, 100))
                    pygame.time.wait(2000)
                    self.ThumbsUp.erase_sprite()
                    if self.levelupcount >= int(self.rchash[self.theme]['autolevel_value']):
                        levelup = 1
                    else:
                        levelup = 0
                    if self.AreWeDT:
                        self.SPG.tellcore_level_end(level=self.level)
                    else:
                        self.SPG.tellcore_level_end(store_db=True, \
                                            level=min(4, self.level), \
                                            levelup=levelup)
        return 
        
