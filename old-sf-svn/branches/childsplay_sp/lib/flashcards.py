# -*- coding: utf-8 -*-

# Copyright (c) 2007-2008 Stas Zytkiewicz stas.zytkiewicz@gmail.com
# Copyright (c) 2006 bruno schwander <bruno@tinkerbox.org>
#               
#           flashcards.py
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
# self.logger =  logging.getLogger("schoolsplay.flashcards.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("schoolsplay.flashcards")

# standard modules you probably need
import os,sys,glob
import random,logging,types

import pygame
from pygame.constants import *

import childsplay_sp.utils as utils
from childsplay_sp.SPConstants import *
import childsplay_sp.SPSpriteUtils as SPSpriteUtils
from childsplay_sp import Timer
from childsplay_sp.SPSpriteUtils import SPButton as Button

EXTRABORDER = 10
# The locales we support, it's used to switch to English if we run
# in a non supported locale.
# Add any new locales to this list.
# For a supported language it's needed to have the pofile translated
# aswell as localized soundfiles.
SUPPORTED_LOCALES = ['en','nl','fr','it','ca', 'ru', 'es', 'de', 'pt_BR']

# containers that can be used globally to store stuff
class Img:
    pass
class Snd:
    pass

class Card:
    def __init__(self,img,descr, ttf):
        self.logger = logging.getLogger("schoolsplay.flashcards.Card")
        self.img = img
        self.descr = descr
        self.descrfontsize = 48
        self.initialfontsize = 200
        self.fcol = (226,178,31)
        self.ttf = ttf
        self.wordsurf,spam =  utils.font2surf(self.descr,self.descrfontsize,self.fcol,self.ttf, bold=True)
        self.initialsurf, spam = utils.font2surf(self.descr[:1],self.initialfontsize,self.fcol,self.ttf, bold=True)
        self.imgPos = self.img.get_rect()
        self.descrPos = self.wordsurf.get_rect()
        self.initialPos = self.initialsurf.get_rect()

    def addSound(self, sound):
        """ adds a sound object, the sound that that object does """
        self.sound = sound
        
    def addName(self, name):
        """ adds a sound object, the spoken name of the object """
        self.name = name

    def addInitialSound(self, initial):
        """ adds a sound object, the spoken initial of the object """
        self.initialSound = initial

    def getImg(self):
        return self.img

    def getSnd(self):
        return self.sound

    def setImagePos(self, x, y):
        self.imgPos.move_ip(x, y)

    def setDescrPos(self, x, y):
        self.descrPos.move_ip(x, y)

    def setInitialPos(self, x, y):
        self.initialPos.move_ip(x, y)
        
    def stopSound(self):
        """Needed to stop any sounds when the user quits"""
        try:
            self.sound.stop()
        except:
            pass

    def playSound(self):
        try:
            self.sound.play()
        except Exception,info:
            self.logger.error("Can't play card sound:%s" % info)
        
    def queueSound(self):
        try:
            self.sound.queue()
        except Exception,info:
            self.logger.error("Can't queue card sound:%s" % info)
                    
    def playInitialSound(self):
        try:
            utils.speak_letter(self.initialSound[0], self.initialSound[1])
        except Exception,info:
            self.logger.error("Can't play card sound:%s" % info)
            
    #to play that object as soon as the current one finishes. play() would stop current
    def queueInitialSound(self):
        self.initialSound.queue()

    def playName(self):
        try:
            self.name.play()
        except Exception,info:
            self.logger.error("Can't play card sound:%s" % info)
            
    def queueName(self):
        self.name.queue()

    def draw(self):
        rec = self.descrPos
        rec = Img.screen.blit(self.wordsurf,rec)
        rec2 = self.imgPos
        rec2 = Img.screen.blit(self.img,rec2)
        rec3 = self.initialPos
        rec3 = Img.screen.blit(self.initialsurf,rec3)

        pygame.display.update((rec,rec2, rec3))

    def erase(self):
        rec = self.descrPos
        rec = Img.screen.blit(Img.backgr,rec,rec)
        rec2 = self.imgPos
        rec2 = Img.screen.blit(Img.backgr,rec2,rec2)
        rec3 = self.initialPos
        rec3 = Img.screen.blit(Img.backgr,rec3,rec3)

        pygame.display.update((rec,rec2,rec3))

class Activity:
    """  Base class mandatory for any SP activty.
    The activity is started by instancing this class by the core.
    This class must at least provide the following methods.
    start (self) called by the core before calling loop.
    next_level (self,level) called by the core when the user changes levels.
    post_next_level (self) called once by the core after 'next_level' *and* after the 321 count. 
    loop (self,events) called 40 times a second by the core and should be your 
                      main eventloop.
    get_helptitle (self) must return the title of the game can be localized.
    get_help (self) must return a list of strings describing the activty.
    get_name (self) must provide the activty name in english, not localized in lowercase.
    stop_timer (self) must stop any timers if any.
  """

    def __init__(self,SPGoodies):
        """SPGoodies is a class object that SP sets up and will contain references
        to objects, callback methods and observers
        """
        self.logger =  logging.getLogger("schoolsplay.flashcards.Activity")
        self.logger.info("Activity started")
        self.SPG = SPGoodies
        self.screen = self.SPG.get_screen()
        self.backgr = self.SPG.get_background()
        
        Img.screen = self.screen# Add some 'global' references
        Img.backgr = self.backgr
        
        # The location of the activities Data dir
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','FlashcardsData')
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.CPbasedir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        # Location of the alphabet sounds dir
        self.absdir = self.SPG.get_absdir_path()# alphabet sounds dir
        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special CPGroup
        self.actives = SPSpriteUtils.SPInit(self.screen,self.backgr)
        
    def _findNextInitial(self,c):
        for i,v in enumerate(self.cardnameslist):
            if _(v)[:1] == c: 
                self.cardindex = i
                self.currentcardname = v
                return True

    def _displayCard(self):
        if self.oldcard:
            self.oldcard.erase()
        self.oldcard = self.carddict[self.currentcardname]
        c = self.carddict[self.currentcardname]
        c.draw()
        c.playName()
        c.queueSound()

    def _showNextCard(self):
        if self.cardindex < self.maxcardindex:
            self.cardindex += 1
            self._next_card()
        
    def _showPreviousCard(self):
        if self.cardindex < 1:
            return
        self.cardindex -= 1
        self.currentcardname = self.cardnameslist[self.cardindex]
        self._displayCard()

    def _check_key(self,key):
        key = unicode(key)
        if self._findNextInitial(key):
            self._next_card()
        return 0

    def _mouseDownProcess(self, event):
        pos = pygame.Rect(event.pos + (4,4))
        if not self.screen.get_clip().contains(pos):
            return
            
        card = self.carddict[self.currentcardname]

        if card.imgPos.contains(pos):
            card.playSound()

        if card.initialPos.contains(pos):
            card.playInitialSound()

        if card.descrPos.contains(pos):
            card.playName()

        v = self.pageFwdButton.update(event)
        if v:
            self._showNextCard()

        v = self.pageBwdButton.update(event)
        if v:
            self._showPreviousCard()
 
    def _next_card(self):
        self.currentcardname = self.cardnameslist[self.cardindex]    
        # check to see if we already have a card object
        if self.carddict.has_key(self.currentcardname) and \
                type(self.carddict[self.currentcardname]) not in types.StringTypes:
            self._displayCard()
            return
        # pre-check if we have a localized name file, if not we call the next card
        name = self.cardnameslist[self.cardindex] 
        try:    
            namepath = glob.glob(os.path.join(self.my_datadir,'names',self.loc,'%s.ogg' % name))[0]
        except IndexError, e:
            self.logger.error("Not found: %s.ogg, please inform the developers." % name)
            self._showNextCard()# this only returns if we don't have any cards left
            return
        
        cardpath = self.carddict[self.currentcardname]
        cardimage = utils.load_image(cardpath,1,1)
        if self.loc == 'en':
            # We make sure we get an english name when running in 'en'.
            # The en locale can also be set because we don't support the current locale.
            card = Card(cardimage,name.upper(), P_TTF)
        else:
            card = Card(cardimage,_(name).upper(), P_TTF)
        cardW = card.img.get_width()
        cardH = card.img.get_height()
        topMargin = card.descrfontsize + EXTRABORDER
        descrW = card.wordsurf.get_rect().width
        initialW = card.initialsurf.get_rect().width
        initialH = card.initialsurf.get_rect().height

        screenW = self.screen.get_clip().width
        screenH = self.screen.get_clip().height
        card.setImagePos(screenW/2 + screenW/4 - cardW/2,
                         topMargin 
                         + (screenH - topMargin)/2 
                         - cardH/2) 
        card.setDescrPos( screenW/2 - descrW/2 , 5 )
        card.setInitialPos(screenW/4 - initialW/2, 
                           topMargin 
                                + (screenH - topMargin)/2
                                - initialH/2) 
                                
        # Here we add sounds to the cards.
        # The idea is that we always display a card regardless if there's a sound.
        sndobject = utils.load_music(namepath)
        if sndobject == 'NoneSound':
            self.logger.error("Not found: names soundfile %s" % namepath)
            self.logger.error("using nonesound object")
        card.addName(sndobject)
        
        if self.loc == 'en':
            initial = name[:1].lower()
        else:
            initial = _(name)[:1].lower()
        card.addInitialSound((initial, self.SPG.get_localesetting()[0]))
                    
        sndobject = utils.load_music(os.path.join(self.crysounddir,name + '.ogg'))
        if sndobject == 'NoneSound':
            self.logger.info("Not found: names soundfile %s" % os.path.join(self.crysounddir,name + '.ogg'))
            self.logger.info("using nonesound object")
        card.addSound(sndobject)
        
        self.carddict[name] = card
        self._displayCard() 
        
##        bs = utils.load_image(os.path.join(self.libdir,'letterFlashcardData','back.jpg'))
##        pygame.display.update(Img.screen.blit(bs,(0,0)))
##        Img.backgr.blit(bs,(0,0))
 
    def get_helptitle(self):
        return _("Flashcards")
    
    def get_help(self):
        text = [_("The aim of the game:"),
        _("This is a game to teach the alphabet to very little childrens."),
        _("At the start of the game, a photograph of an animal is shown, above the picture the name of the animal is written."),
        _("On the left the initial of the animal name is shown."),
        _("Then the animal name is spoken ('the dog'), and the animal makes his cry ('woof' 'cui-cui' etc.)."),
        _("Each part of the screen can also be clicked on to make the animal scream, his name or initial spoken."),
        ""]
        return text
    
    def get_helptip(self):
        """Mandatory method, when no tips available returns an empty string"""
        return [_("When a letter is hit on the keyboard, a corresponding animal is shown.")]
        
    def get_helptype(self):
        """Mandatory method, you must set an type"""
        # Possible types are: Memory, Math, Puzzle, Keyboardtraining, Mousetraining
        #                     Language, Alphabet, Fun, Miscellaneous
        return _("Alphabet")
        
    def get_helplevels(self):
        """Mandatory method, must return a string with the number of levels
        in the follwing format:
        _("This level has %s levels" % number-of-levels)"""
        return _("This activity has %s levels") % 1
      
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "flashcards"
    
    def start(self):
        """Mandatory method."""
        # horrible hacks to get it to work with extended locales
        # This whole module must be redesigned for 2.0
        
        loc = self.SPG.get_localesetting()[0]
        self.logger.debug("Systems locale:%s" % loc)
        fnamesfull = os.path.join(self.my_datadir,'names',loc)
        fnames = os.path.join(self.my_datadir,'names',loc[:2])
        if os.path.exists(fnames):
            self.loc = loc[:2]
        elif os.path.exists(fnamesfull):
            self.loc = loc
        else:
            self.SPG.tellcore_info_dialog(_("Your language, %s, is not supported.\n I will now switch to English" % self.loc))
            self.loc = 'en'
        self.logger.debug("found {0}".format(self.loc))   

        self.initialsounddir = os.path.join(self.absdir,self.loc)
        self.crysounddir = os.path.join(self.my_datadir,'sounds')
        self.nameslist = os.path.join(self.my_datadir,'names',self.loc)
        self.logger.debug("self.initialsounddir:%s" % self.initialsounddir)
        self.logger.debug("self.crysounddir:%s" % self.crysounddir)
        self.logger.debug("self.nameslist:%s" % self.nameslist)
        cardpathslist = glob.glob(os.path.join(self.my_datadir,'cards','*.png'))
        random.shuffle(cardpathslist)
        
        # construct a list with cardnames and a lookup table
        self.cardnameslist = []
        self.carddict = {}# caches card objects as they are being constructed
        for cardpath in cardpathslist:
            name,ext = os.path.splitext(os.path.basename(cardpath))
            self.carddict[name] = cardpath
            self.cardnameslist.append(name)
            
        butnFwdImg = utils.load_image(os.path.join(self.CPbasedir,'arrow.png'),1,1)
        butnFwdImg = pygame.transform.rotate(butnFwdImg, 90)
        pos = (700,10)
        self.pageFwdButton = Button(butnFwdImg,pos,1)
        butnBwdImg = pygame.transform.rotate(butnFwdImg, 180)
        pos = (10,10)
        self.pageBwdButton = Button(butnBwdImg,pos,1)
        
        self.oldcard = None
        self.currentcardname = self.cardnameslist[0]
        self.cardindex = 0
        self.maxcardindex = len(self.cardnameslist) - 1
        
    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        if level == 2:
            return False
        
        return True
    
    def post_next_level(self):
        """Mandatory method.
        This is called by the core after 'next_level' *and* after the 321 count.
        You should place stuff in here that run in a seperate thread like sound play."""
        self.SPG.tellcore_enable_dice(False)
        self.pageFwdButton.display_sprite()
        self.pageBwdButton.display_sprite()
        self._next_card()
        
    def get_score(self,timespend):
        """Mandatory method.
        @timespend is the time spend inside the level as it's calculated
        by the core.
        returns the score value for the past level.
        return None if no score value is used"""
        m,s = timespend.split(':')
        seconds = int(m)*60 + int(s)
        
    def loop(self,events):
        """Mandatory method.
        This is the main eventloop called by the core 30 times a minute."""
        item = None
        for event in events:
            if event.type is KEYDOWN and event.key == K_LEFT:
                self._showNextCard()

            if event.type is KEYDOWN and event.key == K_RIGHT:
                self._showPreviousCard()

            if event.type is KEYDOWN and 96<event.key<123:
                userkey = event.unicode
                #print userkey
                self._check_key(userkey[0])
                break
            if event.type is MOUSEBUTTONDOWN:
                self._mouseDownProcess(event)
                break
        return 
        
    def stop_timer(self):
        """You *must* provide a method to stop timers if you use them.
        The SPC will call this just in case and catch the exception in case 
        there's no 'stop_timer' method""" 
        try:
            self.carddict[self.currentcardname].stopSound() 
        except:
            pass    
