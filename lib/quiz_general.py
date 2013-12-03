# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zytkiewicz stas.zytkiewicz@schoolsplay.org
#
#           quiz.py
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
# self.logger =  logging.getLogger("childsplay.quiz_general.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("childsplay.quiz_knowledge")

# standard modules you probably need
import os,sys

import pygame
from pygame.constants import *

import utils
from SPConstants import *
import SPSpriteUtils
from SPWidgets import TransPrevNextButton

try:
    from xml.etree.ElementTree import ElementTree
except ImportError:
    # try the python2.4 way 
    from elementtree.ElementTree import ElementTree

def parse_xml(xml):
    """Parses the whole xml tree into a hash with lists. Each list contains hashes
    with the elelements from a 'activity' element.
    """  
    logger = logging.getLogger("childsplay.quiz_general.parse_xml")
    logger.debug("Starting to parse: %s" % xml)

    tree = ElementTree()
    tree.parse(xml)
    xml = {}
    # here we start the parsing
    acts = tree.findall('activity')
    logger.debug("found %s activities in total" % len(acts))
    acthash = utils.OrderedDict()
    for act in acts:
        e = act.find('cycles')
        acthash[act.get('name')] = {'cycles':int(e.text)}
    logger.debug("xml hash:%s" % acthash)
    return acthash

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
        self.logger =  logging.getLogger("childsplay.quiz_general.Activity")
        self.logger.info("Activity started")
        self.SPG = SPGoodies
        self.lang = self.SPG.get_localesetting()[0][:2]
        self.screen = self.SPG.get_screen()
        self.screenclip = self.SPG.get_screenclip()
        self.blit_pos = self.screenclip.left, self.screenclip.top
        self.logo_pos = (600, 200 + self.blit_pos[1])
        self.theme = self.SPG.get_theme()
        self.orgscreen = pygame.Surface(self.screenclip.size) # we use this to restore the screen
        self.orgscreen.blit(self.screen, (0, 0), self.screenclip)
        self.backgr = self.SPG.get_background()
        # The location of the activities Data dir
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','Quiz_generalData')
        self.quiz_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','Quizengine_Data')
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.CPdatadir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        self.rchash = utils.read_rcfile(os.path.join(self.my_datadir, 'quiz_general.rc'))
        self.rchash['theme'] = self.theme
        self.rchash['lang'] = self.lang
        self.logger.debug("found rc: %s" % self.rchash)
        p = os.path.join(self.CPdatadir,'good_%s.png' % self.lang)
        if not os.path.exists(p):
            p = os.path.join(self.CPdatadir,'thumbs.png')
        self.ThumbsUp = SPSpriteUtils.MySprite(utils.load_image(p))
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.CPdatadir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        # Location of the alphabet sounds dir
        self.absdir = self.SPG.get_absdir_path()# alphabet sounds dir
        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special CPGroup
        self.actives = SPSpriteUtils.SPInit(self.screen,self.backgr)
          
        self.num_questions = int(self.rchash[self.theme]['questions'])
        self.AreWeDT = False
        self.sessionresults = utils.OrderedDict()
        self.sessionresults_raw = utils.OrderedDict()
        self.old_level = None
        self.sessionid = time.time()
        self.act_score = 0
        self.act_cycles = 1
        self.act_mean = 0
        self.levelup = 0
        
    def _set_up(self, *args):
        """called by the core after this module is constructed."""
        xmlpath = os.path.join(self.my_datadir, 'general_knowledge.xml')
        if not os.path.exists(xmlpath):
            raise utils.MyError, _("xml file %s is missing, this shouldn't happen, contact the %s developers" % (xmlpath, self.theme))    
        self.actdatahash = parse_xml(xmlpath)# returns a ordereddict object
        self.actdata = self.actdatahash.items()
                
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
        return "dltr"
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "quiz_general"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),
                _("Answer the quiz questions."), 
        " ",
        _("At the top of the screen, you will see a question about general knowledge."),
        _("Below it are a choice of possible answers.\nTouch the correct answer."), 
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
        return _("This activity has %s levels") % 6
    
    def _cbf(self, *args):
        return args
    
    def pre_level(self,level):
        """Mandatory method.
        Return True to call the eventloop after this method is called."""
        
    def start(self):
        """Mandatory method."""
        self.levelup = 0
        try:
            self.currentactname, self.currentactdata = self.actdata.pop(0)
        except IndexError:
            self.logger.debug("No more activities to run")
            self._set_up()
            if self.act_mean >= 7.0:
                self.levelup = 1
            else:
                self.levelup = 0
            self.currentactname, self.currentactdata = self.actdata.pop(0)
        self.logger.debug("activity %s is next." % self.currentactname)
                    
    def act_stopped(self, activity):
        """called by the core when an act has finished the levels."""
        self.logger.debug("act_stopped called")
    
    def act_next_level_stopped(self, result):
        """called by the core when the act finished a level.
        This is also called after the last level of act, just before the core calls
        act_stopped."""
        self.logger.debug("act_next_level_stopped called with: %s" % result)
        if not result:
            # it's called with None because we are also a stopping act, weird stuff :-)
            return
        self.act_score = float(self.act_score + result)
        self.act_mean = self.act_score / self.act_cycles
        self.act_cycles += 1
        self.logger.debug("activity mean score now %s" % self.act_mean)
    
    def act_hit_levelindicator(self, level):
        """Called by the core when the levelindicator is hit by the user to change
        the level. (If we enabled the levelindicator of course)
        We use this to determine if we switch acts when act_stopped is called or that
        we must restart with all acts from the new level."""
        self.logger.debug("act_hit_levelindicator called with: %s" % level)
        self._set_up()
        self.oldlevel = level
        self.level = level
        self.act_score = 0
        self.act_mean = 0
        self.cycles = 1
        
    def dt_restarting(self):
        """Called just before the core restarts the DT"""
        self.old_level = self.level

    def get_actdata(self):
        """Called by the core"""
        return self.currentactdata
    
    def next_activity(self):
        self.logger.debug("next_activity called")
        cycles = self.currentactdata['cycles']
        if self.old_level:
            level = self.old_level
            self.old_level = None
        else:
            level = self.level
        self.SPG._menu_activity_userchoice(self.currentactname, level, cycles)
        
    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        self.logger.debug("nextlevel called with: %s" % level)
        if self.levelup:
            self.logger.debug("levelup is True, continue")
            return True
        self.level = level
        if level > self.old_level:
            self.old_level = level
        self.dbmapper = dbmapper
        self.next_activity()
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
        pass
    
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
        if self.levelup:
            self.levelup = False
            self.SPG.tellcore_level_end(store_db=False, \
                                    level=min(6, self.level + 1), \
                                    levelup=True)
        for event in events:
            if event.type in (MOUSEBUTTONDOWN, MOUSEMOTION):
                self.actives.update(event)
                
        return 
        
