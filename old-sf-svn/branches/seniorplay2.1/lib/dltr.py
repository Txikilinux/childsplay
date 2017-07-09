# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zytkiewicz stas.zytkiewicz@gmail.com
#
#           dltr.py
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


####### IMPORTANT READ THIS ####################################################
# This is a special activity which provides a so called "daily training"       #
# This module looks like a regular activity but isn't.                         #
# Make sure you contact the maintainers(s) before making changes               #
################################################################################


#create logger, logger was setup in SPLogging
import logging
# In your Activity class -> 
# self.logger =  logging.getLogger("schoolsplay.video.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("schoolsplay.dltr")

# standard modules you probably need

import pygame
from pygame.constants import *

import utils
from SPConstants import *
import SPSpriteUtils
import SPWidgets

try:
    from xml.etree.ElementTree import ElementTree
except ImportError:
    # try the python2.4 way 
    from elementtree.ElementTree import ElementTree

def parse_xml(xml):
    """Parses the whole xml tree into a hash with lists. Each list contains hashes
    with the elelements from a 'activity' element.
    """  
    logger = logging.getLogger("schoolsplay.dltr.parse_xml")
    logger.debug("Starting to parse: %s" % xml)

    tree = ElementTree()
    tree.parse(xml)
    xml = {}
    # here we start the parsing
    acts = tree.findall('activity')
    logger.debug("found %s activities in total" % len(acts))
    acthash = utils.OrderedDict()
    #acthash = {}
    for act in acts:
        hash = {}
        try:
            hash['name'] = act.get('name')
            
            e = act.find('level')
            hash['level'] = int(e.text)
            
            e = act.find('cycles')
            hash['cycles'] = int(e.text)
        except AttributeError, info:
            logger.error("The %s is badly formed, missing element(s):%s,%s" % (xml, info, e))
            raise utils.MyError, _("XML data file is incorrect, please contact the maintainers.")
        else:
            acthash[hash['name']] = hash
    return acthash

class ProgressBar:
    """Displays a progressbar.
    TODO: add more info"""
    def __init__(self, scr, steps, red, green, coords):
        self.screen = scr
        self.red = red
        self.green = green
        self.coords = coords
        self.start, self.end = (0, 75),(800, 75)
        self.steps = steps
        self.compleetpart = (self.end[0] - self.start[0]) / steps
        self.partsdone = 0
        #self.SurfsPerPart = self.compleetpart / self.partwidth
        #self.green_startX = self.start[0]
            
    def refresh_sprites(self):
        self._draw()

    def update(self):
        if self.partsdone == self.steps:
            return
        self.partsdone += 1
        #print "update", self.partsdone
        self._draw()
    
    def _draw(self):
        done = self.partsdone * self.compleetpart
        #print "done ", done
        green = self.green.subsurface(0,0,done,24)
        #red = self.red.subsurface(0+(self.daily*113),0,1360-(self.daily*113),38)
        self.screen.blit(self.red, (self.start))
        self.screen.blit(green, (self.start))
        pygame.display.update()


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
        self.logger =  logging.getLogger("schoolsplay.dltr.Activity")
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
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','dltrData')
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.CPdatadir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        # Location of the alphabet sounds dir
        self.absdir = self.SPG.get_absdir_path()# alphabet sounds dir
        self.rchash = utils.read_rcfile(os.path.join(self.my_datadir, 'dltr.rc'))
        try:
            f = open(os.path.join(self.my_datadir,'%s.coords' % self.theme), 'r')
        except (OSError, IOError), info:
            self.logger.critical(str(info))
            raise utils.MyError, info
        else:
            s = f.read()
            f.close()
            self.coords = []
            for item in s.split(';'):
                self.coords.append(eval(item, {},{}))
            
        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special CPGroup
        self.actives = SPSpriteUtils.SPInit(self.screen,self.backgr)
    
        xmlpath = os.path.join(self.SPG.get_libdir_path(),'SPData', 'themes',self.theme, 'dailytraining.xml')
        if not os.path.exists(xmlpath):
            raise utils.MyError, _("xml file %s is missing, this shouldn't happen, contact the %s developers" % (xmlpath, self.theme))
        self.actdata = parse_xml(xmlpath).items()# returns a ordereddict object
        
        self.runme = True
        
        green = utils.load_image(os.path.join(self.my_datadir,'status_green_800_600.png'))
        red = utils.load_image(os.path.join(self.my_datadir,'status_red_800_600.png'))
        
        #red = utils.load_image(os.path.join(self.my_datadir, 'red.png'))
        #green = utils.load_image(os.path.join(self.my_datadir, 'green.png'))
        steps = len(self.actdata) 
        self.PB = ProgressBar(self.screen, steps, red, green, self.coords)
           
    def clear_screen(self):
        self.screen.blit(self.orgscreen,self.blit_pos)
        self.backgr.blit(self.orgscreen,self.blit_pos)
        pygame.display.update()

    def refresh_sprites(self):
        """Mandatory method, called by the core when the screen is used for blitting
        and the possibility exists that your sprites are affected by it."""
        self.actives.refresh()
        self.PB.refresh_sprites()

    def get_helptitle(self):
        """Mandatory method"""
        return "dltr"
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "dltr"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),
        _("This activity is known as the daily training which is a collection of activities."), 
        _("Number of levels : 1"),
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
        return _("This activity has %s levels") % 1
    
    def _cbf(self, *args):
        return args
    
    def pre_level(self,level):
        """Mandatory method.
        Return True to call the eventloop after this method is called."""
        self.logger.debug("pre_level called with: %s" % level)
        self.SPG.tellcore_hide_level_indicator()
        if not self.runme:
            return
        txt = [_("If you ready to start the next activity, hit the 'start' button.")]
        txt = utils.txtfmt(txt, 40)
        y = 200
        for t in txt:
            surf = utils.char2surf(t,32,BLACK)
            r = self.screen.blit(surf, (50, y))
            pygame.display.update(r)
            y += 50
        startbutpath = utils.load_image(os.path.join(self.my_datadir, 'start.png'))
        startbutpath_ro = utils.load_image(os.path.join(self.my_datadir, 'start_ro.png'))
        self.startbutton = SPWidgets.TransImgButton(startbutpath, startbutpath_ro, \
                                    (300, 350), fsize=32,text= _("Start"))
        self.startbutton.connect_callback(self._cbf, MOUSEBUTTONDOWN, 'start')
        self.startbutton.display_sprite()
        self.actives.add(self.startbutton)
        self.start_loop_flag = True
        self.PB.update()
        return True 
        
    def start(self):
        """Mandatory method."""
        try:
            self.currentactname, self.currentactdata = self.actdata.pop(0)
        except IndexError:
            self.logger.debug("No more activities to run")
            self.runme = False
        else:
            self.logger.debug("activity %s is next." % self.currentactname)
        self.act_score = 0
    
    def act_stopped(self):
        """called by the core when an act has finished the levels."""
        # TODO store result
        self.logger.debug("act_stopped called")
        stime = utils.calculate_time(self.act_start_time, \
                utils.current_time())
        self.dbmapper.insert('start_time', self.act_start_time)
        self.dbmapper.insert('end_time', utils.current_time())
        self.dbmapper.insert('timespend', stime)
        self.dbmapper.insert('score', self.act_score)
        self.dbmapper.insert('done', 1)
        self.dbmapper.commit()

    def act_next_level_stopped(self, result):
        """called by the core when the act finished a level.
        This is also called after the last level of act, just before the core calls
        act_stopped."""
        self.logger.debug("act_next_level_stopped called with: %s" % result)
        self.act_score += result
        
    def get_actdata(self):
        """Called by the core"""
        return self.currentactdata
    
    def next_activity(self):
        self.logger.debug("next_activity called")
        self.dbmapper.insert('cycles', self.currentactdata['cycles'])
        self.dbmapper.insert('level', self.currentactdata['level'])
        self.logger.debug("Calling _menu_activity_userchoice")
        self.act_start_time = utils.current_time()
        self.dbmapper.insert('activity', self.currentactname)
        #self.SPG.tellcore_show_level_indicator()
        self.SPG._menu_activity_userchoice(self.currentactname)

    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        if not self.runme:# in case of an error or when there are no act left this flag is set
            self.logger.debug("Stop me")
            return False
        self.logger.debug("nextlevel called with: %s" % level)
        self.SPG.tellcore_disable_level_indicator()
        self.SPG.tellcore_hide_level_indicator()
        
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
        for event in events:
            if event.type in (MOUSEBUTTONDOWN, MOUSEMOTION):
                if self.actives.update(event):
                    self.logger.debug("Starting %s" % self.currentactname)
                    self.startbutton.erase_sprite()
                    self.actives.empty()
                    self.SPG.tellcore_pre_level_end()
                    self.clear_screen()
        return 
        
