# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zytkiewicz stas.zytkiewicz@schoolsplay.org
#
#           synonyms.py
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
# self.logger =  logging.getLogger("childsplay.synonyms.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("childsplay.synonyms")

# standard modules you probably need
import os,sys, random, textwrap, types
from string import ascii_letters
import pygame
from pygame.constants import *

import utils
from SPConstants import *
import SPSpriteUtils
from SPWidgets import TransImgButton, SimpleTransImgButton, TextView, Label, THEME
from SPVirtkeyboard import KeyBoard, WordCompleter

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
        self.logger =  logging.getLogger("childsplay.synonyms.Activity")
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
        self.language = self.SPG.get_localesetting()[0][:2]
        
        self.CPdatadir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        # Location of the alphabet sounds dir
        self.absdir = self.SPG.get_absdir_path()# alphabet sounds dir

        self.setup()

        self.logger.debug("rchash: %s" % self.rchash)
        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special CPGroup
        self.actives = SPSpriteUtils.SPInit(self.screen,self.backgr)
        
        self.background = utils.load_image(os.path.join(self.my_datadir, self.theme, 'background.png'))
        self.good_sound = utils.load_music(os.path.join(self.CPdatadir,'good.ogg'))
        self.wrong_sound = utils.load_music(os.path.join(self.CPdatadir,'wrong.ogg'))
        
        i = utils.load_image(os.path.join(self.my_datadir, self.theme, 'begin.png'))
        i_ro = utils.load_image(os.path.join(self.my_datadir, self.theme, 'begin_ro.png'))
        self.beginbut = SimpleTransImgButton(i, i_ro, (634, 530))
        
        i = utils.load_image(os.path.join(self.my_datadir, self.theme, 'newquestion.png'))
        i_ro = utils.load_image(os.path.join(self.my_datadir, self.theme, 'newquestion_ro.png'))
        self.newquestionbut = TransImgButton(i, i_ro, (560, 500))
        self.newquestionbut.connect_callback(self._on_newquestionbut_clicked, MOUSEBUTTONDOWN)
        
    def setup(self):
        """Override this in your derived class."""
        
        # The location of the activities Data dir
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','SynonymsData')
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.rchash = utils.read_rcfile(os.path.join(self.my_datadir, 'synonyms.rc'))
        
        self.alfabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','r','s','t','u','v','w','z']
        self.sequence = self.alfabet[:]
        random.shuffle(self.sequence)
        self.currentletter = self.sequence.pop()
        
        f = open(os.path.join(self.my_datadir,'dictionary_%s.txt' % self.language), 'r')
        self.wordlist = f.readlines()
        f.close()
        self.wc = WordCompleter(self.wordlist)
        
        self.questiontext = _("Make a word with the letter: ")
        self.foundtext =  _("Already found:")
        self.suggestiontext = _("Suggestions:")

    def dailytraining_pre_level(self, level):
        """Mandatory method"""
        pass
    def dailytraining_next_level(self, level, dbmapper):
        """Mandatory method.
        This should handle the DT logic"""
        self.next_level(level, dbmapper)
    
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
        return _("Synonyms")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "synonyms"
    
    def get_help(self):
        """Mandatory methods"""
        # Found a not translated FILE hooked to get it working in NL
        # _("On the next screen you'll find a keyboard, try to make as much words as possible that begin with the letter '%s'." % self.currentletter.upper()), \
        text = [_("The aim of this activity:"),\
                " ", \
                _("On the next screen you'll find a keyboard, try to make as much words as possible that begin with the letter '%s'.") % self.currentletter.upper(), \
                _("Only words from the dictionary are allowed."), \
               _("Hit the 'Begin' button to start." ), \
               " ", \
                _("Number of levels : 6")]
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
        return _("This activity has %s levels") % 6
    
    def pre_level(self,level):
        """Mandatory method.
        Return True to call the eventloop after this method is called."""
        self.logger.debug("pre_level called with: %s" % level)
        self.SPG.tellcore_hide_level_indicator()
        self.AreWeDT = False   
        background = utils.load_image(os.path.join(self.my_datadir, self.theme, 'storybackground.png'))
        if self.blit_pos[1] == 0:
            y = 10
        else:
            y = 110
        x = 10
        
        pygame.display.update(self.screen.blit(background, (x, y)))
        lines = []
        for l in self.get_help():
            if l == " ":
                lines.append(l)
                continue
            for line in textwrap.wrap(l, 48):
                lines.append(line)
        TextView(lines, (22, 108), None, fsize=23, bgcol="trans", \
                fgcol=self.fgcol, shade=0, bold=True).display_sprite()
        self.beginbut.set_use_current_background(True)
        self.beginbut.display_sprite()
        self.actives.add(self.beginbut)
        self.pre_level_flag = True
        return True
        
    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        self.logger.debug("nextlevel called with: %s" % level)
        #self.SPG.tellcore_hide_level_indicator()
        if self.kb:
            self.kb.destroy()
        self.exercises = 0
        self.AreWeDT = False    
        self.kb = KeyBoard(self._kb_cbf, self.actives, keyboard_mode='abc_square',\
                            position=(20,350), \
                      wordcompletion=self.wc, threshold=self.level_lookup[level], \
                      display_position=(20, 305), display_length=0, \
                      password_mode=False, maxlen=28)
        # Your top blit position, this depends on the menubar position 
        if self.blit_pos[1] == 0:
            self.y = 0
        else:
            self.y = 100
        self.x = 10
        self.clear_screen()
        # Various blit positions
        self.texttop_pos = (30, self.y + 15)
        self.textright_pos = (550, self.y + 15)
        self.found_x, self.found_y = self.textright_pos[0], self.textright_pos[1] + 50
        self.suggest_pos = (self.texttop_pos[0], self.texttop_pos[1]+40)
        self.suggest_ans_pos = (self.suggest_pos[0], self.suggest_pos[1]+40)
        self.suggest_pos_max = (540, 290)
        self.wc_pos = (self.suggest_pos[0], self.suggest_pos[1] + 40)
        self.found = []
        self.next_exercise(self.currentletter)       
        return True
    
    def start(self):
        """Mandatory method."""
        self.pre_level_flag = False
        self.fgcol = eval(self.rchash[self.theme]['begin_fgcol'], {}, {})
        self.bgcol = eval(self.rchash[self.theme]['begin_bgcol'], {}, {})
        self.suggest_lbl = {}
        self.level_lookup = {1:2, 2:3, 3:4, 4:5, 6:0} # 0 means no wordcompletion
        self.kb = None
            
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
        if self.kb:
            self.kb.destroy()
        self.SPG.tellcore_show_level_indicator()

    def _kb_cbf(self, parent, data):
        #self.logger.debug("_kb_cbf called")
        #self.logger.debug("suggestions: %s" % data)            
        if self.suggest_lbl:
            self.actives.remove(self.suggest_lbl.values())
            for lbl in self.suggest_lbl.values():
                lbl.erase_sprite()
        self.suggest_lbl = {}
        
        if type(data) in types.StringTypes:
            data = data.lower()
            #enter hit with display string
            if data in self.found:
                self.logger.debug("%s already in found" % data)
                self.wrong_sound.play()
                self.kb.clear_display()
                return
            else:
                lbl = Label(data, (0, 0), fsize=16, \
                    fgcol=eval(self.rchash[self.theme]['suggest_fgcol'], {}, {}),\
                    bold=True, transparent=True)
                # Fake user event to place the lbl at the correct position
                self._on_lbl_clicked(lbl, None, (data,))
        else:
            x, y = self.suggest_ans_pos
            for txt in data:
                if txt in self.found or self.suggest_lbl.has_key(txt):
                    continue             
                lbl = Label(txt, (0, 0), fsize=16, \
                            fgcol=eval(self.rchash[self.theme]['suggest_fgcol'], {}, {}),\
                            bold=True, transparent=True)
                h = lbl.get_sprite_height() + 8
                w = lbl.get_sprite_width()
                if x > (self.suggest_pos_max[0] - w - 12):
                    x = self.suggest_ans_pos[0]
                    y += h
                    if y > self.suggest_pos_max[1]:
                        del lbl
                        break
                lbl.moveto((x, y))
                x = x + w + 12
                lbl.connect_callback(self._on_lbl_clicked, MOUSEBUTTONDOWN, txt)
                self.suggest_lbl[lbl._txt] = lbl
                lbl.display_sprite()
                self.actives.add(self.suggest_lbl.values())
    
    def _on_lbl_clicked(self, lbl, event, txt):
        found_width = 250
        #self.logger.debug("_on_lbl_clicked called")
        if not self.wc.lookup(txt[0]):
            self.logger.debug("%s not in dictionary" % txt[0])
            self.wrong_sound.play()
            return
        self.found.append(txt[0])
        if len(self.found) > 17:
            # fake a button event
            self._on_newquestionbut_clicked()
            return
        self.actives.remove(lbl)
        if self.suggest_lbl.has_key(lbl._txt):
            del self.suggest_lbl[lbl._txt]
            lbl.erase_sprite()
        # check to see if we will fit in the 'already found' section
        if lbl.get_sprite_width() > found_width:
            fgcol = THEME['label_fg_color']
            txt = lbl.get_text()
            txt = txt[:-6] + '...'
            s = utils.char2surf(txt,fsize=lbl.fsize,ttf=TTF, fcol=lbl.fgcol, bold=lbl.bold)
            if s.get_size()[0] > found_width:
                for i in range(6):
                    txt = txt[:-4] + '...'
                    s = utils.char2surf(txt,fsize=lbl.fsize,ttf=TTF, fcol=lbl.fgcol, bold=lbl.bold)
                    if s.get_size()[0] < found_width:
                        break
            lbl.settext(txt)    
            
        lbl.display_sprite((self.found_x, self.found_y))
        self.found_y = self.found_y + lbl.get_sprite_height() - 8
        self.good_sound.play()
        self.kb.clear_display()
        if self.suggest_lbl:
            self.actives.remove(self.suggest_lbl.values())
            for lbl in self.suggest_lbl.values():
                lbl.erase_sprite()
        self.suggest_lbl = {}
    
    def _on_newquestionbut_clicked(self, *args):
        self.logger.debug("_on_newquestionbut_clicked called")
        self.found_x, self.found_y = self.textright_pos[0], self.textright_pos[1] + 30
        self.kb.clear_display()
        txt = _("Starting a new exercise")
        self.next_exercise()

    def next_exercise(self, currentletter=None):
        self.logger.debug("next_exercise called")
        self.found = []
        if not currentletter:
            if len(self.sequence) > 1:
                self.currentletter = self.sequence.pop()
            else: 
                self.sequence = self.alfabet[:]
                random.shuffle(self.sequence)
                self.currentletter = self.sequence.pop()
        self.screen.blit(self.background, (self.x, self.y))
        self.backgr.blit(self.background, (self.x, self.y))
        
        self.wc.set_firstletter(self.currentletter)
        self.kb._set_firstletter(self.currentletter, self.wrong_sound)
        self.kb.show()
                
        qs = utils.char2surf(self.questiontext, fsize=24, fcol=self.fgcol)
        r = self.screen.blit(qs,(self.texttop_pos[0], self.texttop_pos[1]))
        ls_pos = (r.topright[0], r.topright[1]-4)
        
        s = utils.char2surf(self.foundtext, fsize=20, fcol=self.fgcol)
        self.screen.blit(s, self.textright_pos)
        pygame.display.update()
        #### Start animation, increase or decrease attribute value from pygame.time.wait
        for i in range(4, 32):
            s = utils.char2surf(self.currentletter.upper(), fsize=i, fcol=RED, bold=True)
            r = self.screen.blit(s, ls_pos)
            pygame.display.update(r)
            pygame.time.wait(10)
            pygame.display.update(self.screen.blit(self.backgr, r, r))
        s = utils.char2surf(self.currentletter.upper(), fsize=i, fcol=self.fgcol, bold=True)
        r = self.screen.blit(s, ls_pos)
        pygame.display.update(r)
        #########################################################
        self.actives.add(self.newquestionbut)
        self.newquestionbut.display_sprite()
        
        self.wc_x,  self.wc_y = self.wc_pos
        
        #pygame.display.update()
        
    def loop(self,events):
        """Mandatory method.
        This is the main eventloop called by the core 30 times a minute."""
        for event in events:
            if event.type in (MOUSEBUTTONDOWN, MOUSEMOTION):
                if self.pre_level_flag and self.actives.update(event):
                    self.pre_level_flag = False
                    self.actives.remove(self.beginbut)
                    self.SPG.tellcore_pre_level_end()
                else:
                    self.actives.update(event)
                if self.AreWeDT and self.exercises >= self.rchash[self.theme]['exercises']:
                    self.SPG.tellcore_level_end(level=self.level)
        return 
        
