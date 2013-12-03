# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zytkiewicz stas.zytkiewicz@schoolsplay.org
#
#           spinbottle.py
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
# self.logger =  logging.getLogger("childsplay.completion.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("childsplay.spinbottle")

# standard modules you probably need
import os,sys, random, textwrap, types, glob
import fnmatch
import pygame
from pygame.constants import *

import utils
from SPConstants import *
import SPSpriteUtils
from SPVirtkeyboard import KeyBoard, WordCompleter

#sys.path.insert(0, './lib')
import synonyms

    
class SpinningWheel(pygame.sprite.Sprite):
    def __init__(self, img, initial_position):
        pygame.sprite.Sprite.__init__(self)
        self.loaded_image = img
        self.image=self.loaded_image
        self.rotate=0 
        self.angle=15 
        self.rect = self.image.get_rect()
        self.rect.topleft = initial_position
        self.next_update_time = 0 # update() hasn't been called yet.
        self.selected=0

    def clicked(self, target):
        # FIXME: Dead code ??
        "returns true if the iwheel gets clicked"
#        if not self.selected:
#            self.selected= 1
        hitbox = self.rect.inflate(-5, -5)
        #print "Wheel got clicked"
        return hitbox.colliderect(target)

    def update(self, current_time, bottom):
        # FIXME: What's the purpose ? It doesn't stop at the letter
        # Update every 10 milliseconds = 1/100th of a second.
        if self.next_update_time < current_time:
            # rotate and recenter sprite
            oldCenter=self.rect.center
            self.rotate += self.angle
            self.image = pygame.transform.rotate(self.loaded_image, self.rotate)
            self.rect = self.image.get_rect()
            self.rect.center=oldCenter
            self.next_update_time = current_time + 20 

class Activity(synonyms.Activity):
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
        self.logger =  logging.getLogger("childsplay.spinbottle.Activity")
        self.logger.info("Activity started")
        synonyms.Activity.__init__(self, SPGoodies)
        
    def setup(self):
        # The location of the activities Data dir
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','SpinbottleData')
        self.rchash = utils.read_rcfile(os.path.join(self.my_datadir, 'spinbottle.rc'))
        self.currentletter = None
        self.wordlisthash = {}
        paths = glob.glob(os.path.join(self.my_datadir, self.theme,'data_%s' % self.language, '*.txt'))
        self.logger.debug("found: %s " % paths)
        for p in paths:
            f = open(p, 'r')
            lines = f.readlines()
            f.close()
            self.wordlisthash[lines[0][:-1]] = lines[1:]
        self.categories = self.wordlisthash.keys()
        self.logger.debug("Found categories %s" % self.categories)
        random.shuffle(self.categories)
        self.currentcategory = self.categories.pop()
        self.questiontext = _("beginning with the letter: ")
        self.foundtext =  _("Already found:")
        self.suggestiontext = _("Suggestions:")
        self.wc = WordCompleter([])
        self.newexercise_counter = 3
    
    def _on_newquestionbut_clicked(self, *args):
        self.logger.debug("_on_newquestionbut_clicked called")
        self.newexercise_counter -= 1
        self.found_x, self.found_y = self.textright_pos[0], self.textright_pos[1] + 30
        self.kb.clear_display()
        txt = _("Starting a new exercise")
        self.next_exercise() 
 
    def next_exercise(self, currentletter=None):
        self.logger.debug("next_exercise called with %s" % currentletter)
        self.found_x, self.found_y = self.textright_pos[0], self.textright_pos[1] + 75
        if len(self.categories) < 1:
                self.categories = self.wordlisthash.keys()
                random.shuffle(self.categories)
        # Change self.newexercise_counter < 4 into 3 to get three times the same category wit a different letter. 
        if not self.currentcategory or self.newexercise_counter < 4:
            self.currentcategory = self.categories.pop()
            self.newexercise_counter = 3
        
        sequence = []
        for line in self.wordlisthash[self.currentcategory][2:]:
            c = line[1].lower()
            if c not in sequence:
                sequence.append(c)
            
        random.shuffle(sequence)
        if not currentletter:
            self.currentletter = sequence.pop()
        self.logger.debug("picked first letter %s" % self.currentletter)
        
        self.screen.blit(self.background, (self.x, self.y))
        self.backgr.blit(self.background, (self.x, self.y))
        
        self.wc.set_firstletter(self.currentletter)
        self.kb._set_firstletter(self.currentletter, self.wrong_sound)
        wordlist = self.wordlisthash[self.currentcategory][1:]
        self.wc.set_wordlist(wordlist)
        self.kb.show()
        
        h = 0
        txt = self.wordlisthash[self.currentcategory][:1][0][:-1]
        s = utils.char2surf(txt, fsize=20, fcol=self.fgcol)
        r = self.screen.blit(s,(self.texttop_pos[0], self.texttop_pos[1]+h))
        h += s.get_rect().h
        s = utils.char2surf(self.questiontext, fsize=20, fcol=self.fgcol)
        r = self.screen.blit(s,(self.texttop_pos[0], self.texttop_pos[1]+h))
        
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
        ########################################################################
        self.actives.add(self.newquestionbut)
        self.newquestionbut.display_sprite()
        
        self.wc_x,  self.wc_y = self.wc_pos
        
        pygame.display.update()

    def get_helptitle(self):
        """Mandatory method"""
        return _("Spin the bottle")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "spinbottle"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),\
                " ", \
                _("On the next screen you'll find a keyboard, try to name as much %s as possible with the same letter.") % (self.currentcategory), \
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
    
    def get_score(self,timespend):
        """Mandatory method.
        @timespend is the time spend inside the level as it's calculated
        by the core.
        returns the score value for the past level.
        return None if no score value is used"""
        m,s = timespend.split(':')
        seconds = int(m)*60 + int(s)
    
    
        
