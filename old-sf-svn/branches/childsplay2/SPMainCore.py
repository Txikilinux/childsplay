# -*- coding: utf-8 -*-

# Copyright (c) 2006-2010 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           SPMainCore.py
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

# The MainCoreCallbacks class, that's the thing that controls the events except
# activity stuff, is using ocempgui.
# The menu items are ocempgui buttons.
# Sprites are only used in the activities.
# The activity menu and the bottom menu bar are controlled by MainCoreGui

import sys
import gc
import atexit
import os
import pygame
import threading
import types
import ConfigParser

from pygame.constants import *
## set a bigger buffer, seems that on win XP in conjuction with certain hardware
## the playback of sound is scrambled with the "normal" 1024 buffer.
###  XXXX this still sucks, signed or unsigned that's the question :-(
pygame.mixer.pre_init(22050, -16, 2, 2048)
pygame.init()

#create logger, logger was configured in SPLogging
import logging
module_logger = logging.getLogger("schoolsplay.SPMainCore")

import utils
###### for debugging memoryleaks ###########
#from guppy import hpy                     #
#h = hpy()                                 #
############################################
from SPSpriteUtils import SPInit, MySprite, set_big_mouse_cursor, set_no_mouse_cursor
from SPGoodies import SPGoodies

# This is a kludge to execute the toplevel code in SPConstants as it is already
# imported in SPlogging before the loggers are set.
import SPConstants
reload(SPConstants)
from SPConstants import *

try:
    import psyco
    #psyco.log(PSYCOPATH, 'w')
    psyco.profile()
except:
    pass
else:
    module_logger.debug("We got psyco, we should go faster, but report any weird crashes.")


import SPMenu
import SPDataManager as SPDataManager
import Version
import SPContentTables

from SPWidgets import Init, Dialog, Label, MenuBar, VolumeAdjust, ExeCounter, Graph
#from SPVirtualkeyboard import VirtualKeyboard
from sqlalchemy import exceptions as sqla_exceptions

# Used to cleanup stuff when the Python vm ends
def cleanup():
    module_logger.info("cleanup called.")
    module_logger.info("flushing dbase to disk")
    # flush dbase?
    # remove any locks that been set
    utils._remove_lock()
    module_logger.info("logger stops.")
    # add cleanup stuff in here or register it like the Activity class does
    
atexit.register(cleanup)



class MainEscapeKeyException(Exception):
    """Raised when the user decides to quit the maincore.
    This is catched by schoolsplay.py to check if we quit or go back to the login"""
    pass
class EscapeKeyException(Exception):
    """ This is raised from the activity_loop when the user hits escape.
    We basically using this exception as a signal"""
    pass
class LevelsEndException(Exception):
    """ This is raised from activity_loop when there are no more levels in the game."""
    pass
class GDMEscapeKeyException(Exception):
    """ This is raised from the activity_loop when the user hits escape.
    We basically using this exception as a signal"""
    pass
    
class MainCoreGui:
    def __init__(self, resolution=(800, 600), options=None, language=('en', False), fullscr=None):
        """The main SP core.
        The idea is that we have a menubar at the botttom and a activity area
        just like in CP. The menu bar is the place for ocempgui gui widgets.
        SP sprites are only used in the activity area.
        The activity doesn't draw in the menu bar and the ocempgui doesn't comes
        into the activity area.
        We call from the eventloop first some local checks like pressing escape etc.
        Then we call the ocempgui render eventloop to check and control ocempgui
        stuff. Then we call the actives_group in which our activity sprites are
        held.
        In the real SP we won't call the actives_group but we call the eventloop
        of the activity.
        """
        self.logger = logging.getLogger("schoolsplay.SPMainCore.MainCoreGui")
        self.logger.debug("Start")
        
        self.myspritesactivated = None
        self.menubuttons_backup = []
        self.volume_level = None
        self.levelcount = 1
        self.DTmode = False
        self.DTactivity = None
        self.DTlevelscounter = 0
        self.DTlevelcount = 3
        self.DTact_is_finished = None
        self.cmd_options = options
        self.theme_rc = self.cmd_options.theme_rc
        self.logger.debug("Found menu rc options %s" % self.theme_rc)
        self.theme = self.cmd_options.theme
        
        dbase = os.path.join(HOMEDIR, self.theme, 'quizcontent.db')
        SPContentTables.check_tables(dbase)
        
        # get our base options from a rc file.
        self.core_rc_path = os.path.join(ACTIVITYDATADIR, 'SPData', 'base', 'themes','core.rc')
        self.logger.debug("Parsing core rc file %s" % self.core_rc_path)
        d = {}
        config = ConfigParser.ConfigParser()
        config.read(self.core_rc_path)
        for k, v in dict(config.items(self.theme)).items():
            d[k] = v
        d['theme'] = self.theme
        self.core_rc = d
        self.logger.debug("found core rc options %s" % d)
        
        self.theme_dir = os.path.join(ACTIVITYDATADIR, 'SPData', 'themes', self.theme)
        
        if self.cmd_options.no_sound:
            self.logger.info("Disabling sound support as requested by user")
            pygame.mixer.quit()
        else: #get the current aumix system volume if possible
            self.volume_level = 50
            try:
                output=os.popen('aumix -q').readlines()
                end=output[0].find(",")
                self.volume_level=int(output[0][4:end])
            except:
                module_logger.warning("program 'aumix' not found, unable to set volume levels")
            self.logger.debug("Current volume set to: %d" % self.volume_level)

        # set mouse cursor ?
        # TODO: use different cursors with an cmdline option
        if self.cmd_options.bigcursor:
            cursorfile = os.path.join(ACTIVITYDATADIR, 'SPData', 'base', 'icons', 'cursor_1.xbm')
            maskfile = os.path.join(ACTIVITYDATADIR, 'SPData', 'base', 'icons', 'cursor_1-mask.xbm')
            set_big_mouse_cursor(cursorfile, maskfile)
        if self.cmd_options.nocursor:
            set_no_mouse_cursor()
        self.resolution = resolution
        self.vtkb = None # will become the virtual keyboard object
        
        ## Set icon for the window manager ## 
        ICONPATH = os.path.join(ACTIVITYDATADIR, 'SPData', 'themes', self.theme)
        DEFAULTICONPATH = os.path.join(ACTIVITYDATADIR, 'SPData', 'themes', 'childsplay')
        # TODO:change icon files to the ones we would use
        if sys.platform == 'darwin':
            file = 'logo_cp_180x180.png'
        elif sys.platform == 'win32':
            file = 'logo_cp_64x64.png'
        else:
            file = 'logo_cp_32x32.xpm'
        if not os.path.exists(os.path.join(ICONPATH, file)):
            icon_path = os.path.join(DEFAULTICONPATH, file)
        else:
            icon_path = os.path.join(ICONPATH, file)
        try:
            surface = pygame.image.load(icon_path)
        except pygame.error:
            self.logger.error('Could not load image "%s"\n %s' % (file, pygame.get_error()))
        else:
            surface.set_colorkey(surface.get_at((0, 0)), RLEACCEL)
            pygame.display.set_icon(surface)
        
        # Thread lock, must be used by activities to be able to block everything.
        self.lock = threading.Lock() 
        
        # We get the minimum menu activity here.
        try:
            self.activity = SPMenu.Activity()
        except Exception, info:
            self.logger.exception("Failed to setup the menu")
            raise utils.MyError, info
        # then we parse the menu xml
        self.activity._parse_menu(self.theme_dir)
        # first finish the screen stuff
        # setup main screen
        if self.cmd_options.fullscreen:
            self.screen = pygame.display.set_mode(self.resolution, FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.resolution)
        if self.theme_rc['menubar_position'] == 'bottom':
            y = 500
            blitpos_y = 0
            menu_rect = pygame.Rect(0, 500, 800, 100)
        else:# we only have two options: top or bottom
            y = 0
            blitpos_y = 100
            menu_rect = pygame.Rect(0, 0, 800, 100)                
        captxt = _("Childsplay_sp - educational activities, using theme:%s") % self.theme
        if self.cmd_options.theme != 'childsplay':
            captxt = captxt.replace('Childsplay_sp', self.cmd_options.theme)
        pygame.display.set_caption(captxt.encode('utf-8'))
        
        self.backgroundimage = utils.load_image(self.activity._get_menuback_path())
        self.screen.blit(self.backgroundimage, (0, 0))
        img = utils.load_image(self.activity._get_menubar_path())
        self.menubar_image = img# we pass this to the DT start method
        self.backgroundimage.blit(img, (0, y))
        self.screen.blit(self.backgroundimage, (0, 0))
        self.backgr = self.screen.convert()# a real copy
        # init SpriteUtils, mandatory when using SpriteUtils
        self.actives_group = SPInit(self.screen, self.backgr)
        self.actives_group.set_onematch(True)
        # MustSPMainCore.py be called before using SPWidgets
        Init(self.theme)
        
        # now we can build the menu buttons
        self.activity._build_menu(self.theme_dir, self.theme_rc, language[0])
        
        # setup SPGoodies which we pass to the activities
        # from here on we set various attributes for the spgoodies instance 
        self.screenclip = None
        self.spgoodies = SPGoodies(self.screen, \
            self.get_virtkb, \
            language, \
            self.lock, \
            self.activity_pre_level_end, \
            self.activity_level_end, \
            self.activity_game_end, \
            self.activity_info_dialog, \
            self.display_execounter, \
            self.set_framerate, \
            self.enable_dice, \
            self.set_dice_minimal_level, \
            self.theme_rc, \
            self.cmd_options.theme,\
            self.disable_menubuttons, self.enable_menubuttons,\
            self.disable_level_indicator,self.enable_level_indicator, \
            self.disable_exit_button, self.enable_exit_button, \
            self.disable_score_button, self.enable_score_button, \
            self.hide_level_indicator, self.show_level_indicator)
        # special goodies for the menu
        self.spgoodies._menu_activity_userchoice = self._menu_activity_userchoice
        self.spgoodies._cmd_options = self.cmd_options

        r = pygame.Rect(0, blitpos_y, 800, 500)
        # Add the rect to SPGoodies so that activities know where to blit.
        self.spgoodies.screenrect = r
        self.spgoodies.background = self.backgr
        
        
        # we get a datamanager which will start the SPgdm login screen
        try:
            self.dm = SPDataManager.DataManager(self.spgoodies)
        except sqla_exceptions.SQLError:
            self.logger.exception("Error while handling the dbase, try removing the existing dbase")
        except utils.MyError, info:
            self.logger.error("%s" % info)
            raise utils.SPError
        # restore window title after the datamanager replaced it
        pygame.display.set_caption(captxt.encode('utf-8'))
        
        # now we can finally finish the menu object
        self.activity._setup(self.spgoodies, self.dm)
        
        # Setup the menubar
        self.excludebuttons = self.theme_rc['exclude_buttons']
        if self.theme_rc['level_indicator'] == 'star':
            usestar = True
        else:
            usestar = False
        if 'graph' in self.theme_rc['exclude_buttons']:
            usegraph = False
        else:
            usegraph = True
        self.menubar = MenuBar(menu_rect, \
                               self.actives_group, self.menubar_cbf,\
                                self.menubar_dice_cbf, self.lock, usestar, usegraph)
        self.infobutton = self.menubar.get_infobutton()
        self.quitbutton = self.menubar.get_quitbutton()
        self.scoredisplay = self.menubar.get_scoredisplay()
        self.menubarbuttons = [self.infobutton, self.quitbutton]
        
        self.chartbutton = self.menubar.get_chartbutton()
        self.dicebuttons = self.menubar.get_dicebuttons()
                
        self.spgoodies.scoredisplay = self.scoredisplay
        self.spgoodies.infobutton = self.infobutton
        self.spgoodies.quitbutton = self.quitbutton
        
        if not 'dice' in self.excludebuttons:
            self.dicebuttons.UseDice = True
        else:
            self.dicebuttons.UseDice = False
        if not 'graph' in self.excludebuttons:
            self.menubarbuttons.append(self.chartbutton)
            # disable the chartbutton
            self.chartbutton.enable(False) 
        if not 'score' in self.excludebuttons:
            self.menubarbuttons.append(self.scoredisplay)
        
        self.actives_group.add(self.menubarbuttons)
        
        # add the current user, if it exists
        text = _("User: %s") % self.dm.get_username()
        # TODO: Do we do an andmin mode ?
        if self.cmd_options.adminmode:
            text = text + " (Adminmode)"
        if self.theme_rc['menubar_position'] == 'bottom':
            y = 500
        else:
            y = 0
        if not 'user' in self.excludebuttons:
            self.usernamelabel = Label(text, (CORE_BUTTONS_XCOORDS[1], y+10))
        else:
            self.usernamelabel = None
        if not 'activity' in self.excludebuttons:
            text = _("Activity :") 
            self.activitylabel = Label(text, (CORE_BUTTONS_XCOORDS[1], y+50))
        else:
            self.activitylabel = None
        
        # Show the mainscreen and menubar
        self.clear_screen()
        
        # setup misc stuff
        self.clock = pygame.time.Clock()
        self.run_activity_loop = True
        self.run_event_loop = True
        self.run_main_loop = True
        self.framerate = 30
        self.were_in_pre_level = False
        
    def start(self):
        p = os.path.join(HOMEDIR, self.theme, 'askdialog')
        if not os.path.exists(p):
            txt = "We are in need of free mulimedia content like images and sounds. As a result most of the quizzes are disabled. If you want to create images, sounds or make quiz questions contact us at schoolsplay@gmail.com"
            dlg = Dialog(txt,dialogwidth=600,  \
                        buttons=[_("OK")], title=_('Request for help'))
            dlg.run()
            open(p, 'w').close()
            
        # start menu
        self.activity.start()
        #For memoryleak debugging 
        #h.setrelheap()
        self.start_main_loop()
        
    ############################################################################
    ## Methods for internal use 
    def clear_screen(self):
        self.logger.debug("clear_screen called")
        # rebuild screen with the standard background 
        x, y = self.spgoodies.screenrect.left, self.spgoodies.screenrect.top
        pygame.display.update(self.screen.blit(self.backgroundimage, (0, 0)))
        self.backgr.blit(self.screen.convert(),(0, 0) )
        # reset the screens in SPGoodies so that any activities gets a proper screen.
        self.spgoodies.screen = self.screen
        self.spgoodies.background = self.backgr
#        self.menubar.display_sprite()
        for b in self.menubarbuttons:
            b.display_sprite()
        if self.dicebuttons.UseDice:
            #self.dicebuttons.next_level(self.levelcount)
            self.dicebuttons.enable(False)
        if self.usernamelabel:
            self.usernamelabel.display_sprite()
        if self.activitylabel:
            self.activitylabel.display_sprite()
        
    def load_activity(self, name):
        # This will replace self.activity with the chosen activity
        self.logger.debug("load_activity called with %s" % name)
        self.set_framerate()
        try:
            # Check if we are running locally for developing activities
            if hasattr(self.spgoodies._cmd_options, 'run_local'):
                self.logger.debug("We running from source, import activity from cwd/lib")
                # When we run locally, meaning from sources, the activities still import utils
                # from the installed childsplay_sp package and when they raise an exception defined
                # in utils we can catch it because we import utils from sources.
                # That's why we check if we run from sources by checking for a special attribute
                # set in childsplay_sp_local
                
                self.activity_module = utils.import_module(os.path.join('lib', name))
            else:
                self.logger.debug("Trying to import activity from childsplay_sp.lib")
                self.activity_module = getattr(__import__('childsplay_sp.lib', \
                    globals(), locals(), [str(name)]), name)
            self.activity = self.activity_module.Activity(self.spgoodies)
        except (utils.MyError, ImportError, AttributeError), info:
            self.logger.exception("Error importing activity %s" % name)
            dlg = Dialog(_("Error importing activity\n%s" % info),dialogwidth=500,  \
                    buttons=[_("OK")], title=_('Error !'))
            dlg.run()
            self.activity = self.menu_saved
            self.activity.refresh_sprites()
            self.start_main_loop()
        except (utils.MyError, StandardError), info:
            self.logger.exception("Error constructing activity: %s" % info)
            dlg = Dialog(_("Error constructing activity\n%s" % info), dialogwidth=500, \
                    buttons=[_("OK")], title=_('Error !'))
            dlg.run()
            self.activity = self.menu_saved
            self.activity.refresh_sprites()
            self.start_main_loop()
        else:
            self.logger.debug("Loaded %s activity succesfull" % self.activity)
            self.enable_dice(True)
            text = _("Activity : %s") % self.activity.get_helptitle()
            if self.activitylabel:
                self.activitylabel.settext(text)
            if self.activity.get_name() == 'dltr':
                self.logger.debug("Got dltr, putting myself in DT mode")
                self.DTmode = True
                self.DTactivity = self.activity
            self.start_main_loop()
            
    def start_start(self):
        self.logger.debug("Calling activity start")
        self.show_level_indicator()
        self.levelcount = 0
        try:
            self.activity.start()
        except Exception, info:
            self.logger.exception("Error in %s start" % self.activity.get_name())
            raise utils.MyError, info
        if not self.dm.anonymous and 'graph' not in self.excludebuttons:
            # as were datacollectors we also add a chart button to the menubar
            self.chartbutton.enable(True)
        if self.DTmode and self.activity.get_name() == 'dltr':
            # we must make the call here as dltr sets up the data in start
            self.DTactdata = self.activity.get_actdata()
            self.DTlevelcount = self.DTactdata['level']
            self.DTlevelscounter = self.DTactdata['cycles']
        
            
    def display_levelstart(self, level):
        """Displays a 'ready 3-2-1' screen prior to starting the level.
        It also displays a blocking 'Start' button."""
          
        self.logger.debug("Starting display_levelstart")
        
        if self.cmd_options.no_text or self.cmd_options.nocountdown or self.DTmode:
            return
                
        org_screen = pygame.display.get_surface().convert()
        org_backgr = self.backgr.convert()

        self.screen.set_clip()
        
        # disable the dice to prevent users clicking it
        # dim the screen
        sdim = utils.Dimmer(keepalive=0)
        sdim.dim(darken_factor=200, color_filter=(51, 10, 10))
        # display text
        txt = _("Starting level %s") % level
        txt_s0 = utils.char2surf(txt, P_TTFSIZE + 20, fcol=GREEN, ttf=P_TTF, bold=True)
        self.screen.blit(txt_s0, ((780-txt_s0.get_width()) / 2, 100))
         
        txt = self.activity.get_help()[1]
        txt_s1 = utils.char2surf(txt, P_TTFSIZE + 2, fcol=GREEN, ttf=P_TTF, bold=True)
        self.screen.blit(txt_s1, ((780-txt_s1.get_width()) / 2, 200))
        
        txt = utils.txtfmt([_("Hit the 'space' key or a mousebutton to skip the countdown")], 60)
        print txt
        txtlist = []
        for line in txt:
            txtlist.append(utils.char2surf(line, P_TTFSIZE + 2, fcol=GREEN, ttf=P_TTF, bold=True))
        y = 260
        for s in txtlist:
            self.screen.blit(s, (40, y))
            y += s.get_height()
        
        pygame.display.update()
        
        # we have a animated sprite so we need to adjust the backgr screen
        self.backgr.blit(self.screen, (0, 0))
        # we re-init the sprite stuff as we use a different background 
        SPInit(self.screen, self.backgr)
        # i is used as a counter. The loop runs at approx 30 times a second so
        # when i == 30 we decrease the counter.  
        i = 0
        counter = 4# used for 4-3-2-1
        spr = None# will hold the sprite
        # local eventloop
        clock = pygame.time.Clock()
        runloop = True
        while runloop:
            # runloop is set to False by the a event or when the counter == 0
            pygame.event.pump()
            events = pygame.event.get()
            for event in events:
                if event.type is KEYDOWN and event.key is K_SPACE or\
                    event.type is MOUSEBUTTONDOWN:
                    runloop = False
                    break
            if i >= 29:
                if spr:
                    spr.erase_sprite()
                if counter == 0:
                    runloop = False
                else:
                    num_s = utils.char2surf(str(counter), 72, fcol=RED, ttf=P_TTF, bold=True)
                    spr = MySprite(num_s)
                    spr.display_sprite((350, 300))
                    i = 0
                    counter -= 1
            i += 1
            
            clock.tick(30)
        # restore the screens
        # undim the screen
        sdim.dim(darken_factor=255, color_filter=(0, 0, 0))
        self.screen.blit(org_screen, (0, 0))
        self.backgr.blit(org_backgr, (0, 0))
        # reset the screens in SPGoodies so that any activities gets a proper screen.
        SPInit(self.screen, self.backgr)
        pygame.display.update()
                
    def start_next_level(self, store_db=None, nextlevel=None, levelup=False):
        """store_db is used to signal normal ending and that we should store the data"""
        # reset any clipping
        self.screen.set_clip()
        if nextlevel and not self.DTmode:
            if levelup and self.levelcount < 6:
                dlg = Dialog(_("You play very good, do you want to try the next level ?"), \
                        buttons=[_("No"), _("Yes")], title=_('Question ?'))
                dlg.run()
                c = dlg.get_result()[0]
                if c == _('Yes'):
                    self.levelcount = nextlevel
                
            else:
                self.levelcount = nextlevel
        if self.levelcount == 0:
            self.levelcount = 1
        
        # are we in the data collecting bussiness ?
        if self.activity.get_name() != 'menu':
            # Here we fetch our data colletor object, we collect data per level,
            # so it's the best place to start datacollecting
            # get_mapper returns always an object, in case of anonymous mode the 
            # object is a fake.
            self.mapper = self.dm.get_mapper(self.activity.get_name())
            self.mapper.insert('level', self.levelcount)
            self.mapper.insert('start_time', utils.current_time())
        else:
            self.mapper = self.dm.get_mapper(None)
        try:
            if self.activity.get_name() == 'menu':
                self.activity.next_level(self.levelcount)
            else:
                if not self.menubuttons_backup:
                    self.dicebuttons.next_level(self.levelcount)
                if self.activity.get_name() != 'dltr' and self.DTmode:
                    if self.DTlevelscounter:
                        self.DTactivity.refresh_sprites()
                        self.logger.debug("Calling %s dailytraining_next_level, level:%s,counter:%s" % \
                                          (self.activity.get_name(), self.DTlevelcount, self.DTlevelscounter))
                        result = self.activity.dailytraining_next_level(self.DTlevelcount, self.mapper)
                        self.DTlevelscounter -= 1
                    else:
                        self.DTact_is_finished = True
                        # we don't store the scores as it differs from normal act results
                        # the DT act stores the results
                        self.activity_game_end(store_db=False)
                        result = True
                else:
                    self.logger.debug("Calling %s next_level, level:%s" % (self.activity.get_name(), self.levelcount))
                    result = self.activity.next_level(self.levelcount, self.mapper)
                # we pass the db mapper so that the activity can store it's data
                if not result:
                    if self.DTmode:
                        self.logger.debug("End the DT")
                        self.DTmode = False
                        self.DTactivity = None
                    self.logger.debug("start_activity_loop: Levels ended")
                    #self.activity_info_dialog(self.activity.get_helplevels())
                    self.activity_game_end(store_db=False)
                else:
                    # We display a blocking ready-start screen
                    self.display_levelstart(self.levelcount)
                    # and call the post_next_level
                    self.activity.post_next_level()
        except utils.MyError, info:
            self.logger.error("MyError in %s next_level" % self.activity.get_name())
            self.activity.stop_timer()
            raise utils.MyError, info
        except StandardError, info:
            self.logger.exception("StandardError in %s next_level" % self.activity.get_name())
            self.activity.stop_timer()
            raise utils.MyError, info
        
    def ask_exit(self):
        self.logger.debug("ask_exit called")
        if not self.cmd_options.noexitquestion:
            dlg = Dialog(_("Do you really want to quit ?"), \
                    buttons=[_("Cancel"), _("OK")], title=_('Quit ?'))
            dlg.run()
            c = dlg.get_result()[0]
            self.activity.refresh_sprites()
        else:
            c = _("OK")
        if c == _("OK"):
            self.logger.info("User wants exit")
            if self.activity.get_name() != 'menu':
                try:
                    self.activity_game_end(store_db=False)
                except:
                    pass
            # any cleanup is done by atexit functions
            # except this one :-)
            self.dm._cleanup()
            # dim the screen
            sdim = utils.Dimmer(keepalive=0)
            sdim.dim(darken_factor=200, color_filter=(51, 10, 10))
            # display text
            txt = utils.txtfmt([_("Stopping timers, please wait...")], 50)
            y = 240
            for line in txt:
                s = utils.char2surf(line, P_TTFSIZE + 12, fcol=GREEN, ttf=P_TTF, bold=True)
                self.screen.blit(s, (10, y))
                y += s.get_height()
            pygame.display.update()
            #pygame.time.wait(1000)# just to show the text in case there are no timers
            raise MainEscapeKeyException # let schoolsplay.py decide what next
            
    ###########################################################################
    # Main menubar button callbacks.
    # These are called when the user hits the buttons in the lower menu bar of 
    # screen.
    def menubar_cbf(self, sprite, event, data):
        """Callback function for the menubar buttons: quit, info, chart.
        Here we decide which button has called us and we call the appropriate 
        method for further event handling."""
        self.logger.debug("menubar_button_pressed: %s" % sprite.name)
        try:
            if sprite.name == 'Info':
                self.core_info_button_pressed()
                sprite.mouse_hover_leave()
            elif sprite.name == 'Quit':
                sprite.mouse_hover_leave()
                if self.DTmode:
                    self.lock.acquire()
                    text = _("Are sure you want to quit the dailytraining ? All the results will be lost.")
                    dlg = Dialog(text, buttons=[_("No"), _("Yes")], title=_('Question ?'))
                    dlg.run()
                    c = dlg.get_result()[0]
                    if c == _('No'):
                        self.lock.release()
                        return
                raise utils.StopGameException
                #self.core_quit_button_pressed()
            elif sprite.name == 'Chart' and self.activity.get_name() != 'menu':
                self.core_chart_button_pressed()
                sprite.mouse_hover_leave()
        except StandardError, info:
            self.logger.exception("System error: %s" % info)
            self.lock.release()
            self.clear_screen()
            self.activity.refresh_sprites() 
        
    def menubar_dice_cbf(self, sprite, event, data):
        """Callback function for the menubar dicebutton."""
        self.logger.debug("core_dice_button_pressed: %s" % data)
        self.myspritesactivated = True
        if data:
            if 1 < data > 6:
                data = 1
            if self.were_in_pre_level:
                self.levelcount = data
            else:
                self.activity_level_end(nextlevel=data)
        else:
            self.activity.refresh_sprites()
       
    def core_info_button_pressed(self):
        self.myspritesactivated = True
        self.lock.acquire()
        # Construct the help text from the activity's various get_help* methods
        help = self.activity.get_help()
        if self.activity.get_name() != 'menu':
            tip = self.activity.get_helptip()
            if tip:
                help.append(_("Tip:%s") % tip)
            help.append(self.activity.get_helplevels())
            #help.append(_("This activity belongs to the category: %s") % self.activity.get_helptype())
        if hasattr(self.activity, 'get_extra_info'):
            help.append("%s" % self.activity.get_extra_info())
            help += "\n\n"
        else:
            help += "\n\n\n"
        dlg = Dialog(help, dialogwidth=600, buttons=[_("OK")], title= _("Information about %s") % self.activity.get_helptitle())
        
        x, y = dlg.action_area_pos[0]
        w = dlg.action_area_pos[1]
        y -= 56
        x = w /2 + 10
        va = VolumeAdjust((x, y), volume=self.volume_level)
        va.set_use_current_background(True)# it will use the current screen as background as we blit over a dialog
        va.display()
        
        dlg.run(va.get_actives())
        self.volume_level = va.get_volume()
        self.logger.debug("Volume set to %s" % self.volume_level)
        
        self.activity.refresh_sprites()
        self.lock.release()
        return True
        
    def core_quit_button_pressed(self):
        self.myspritesactivated = True
        self.lock.acquire()
        if self.activity.get_name() == 'menu':
            self.ask_exit()# if this returns the user said no.
            self.lock.release()
            return
        elif self.DTmode:
            text = _("Are sure you want to quit the dailytraining ? All the results will be lost.")
            dlg = Dialog(text, buttons=[_("No"), _("Yes")], title=_('Question ?'))
            dlg.run()
            c = dlg.get_result()[0]
            if c == _('No'):
                self.lock.release()
                return
        else:
            self.lock.release()
            self.activity_game_end(store_db=False)
        return True

    # Callback for the chart button in the menubar. Passed to SPCoreButtons.ChartButton
    def core_chart_button_pressed(self):
        if not hasattr(self, 'mapper'):
            self.logger.warning("core_chart_button_pressed, no mapper found.")
            return 
        self.myspritesactivated = True
        self.lock.acquire()
        # get data, user AND level
        query = self.mapper._get_level_data(levelnum=self.levelcount)
        # get the score and date data from the objects
        scorelist = filter(None, [(getattr(item, 'start_time'), getattr(item, 'score')) for item in query])
        self.logger.debug("scorelist from SQL query: %s" % scorelist)
        # get the mu and sigma for this activity.
        norm = self.dm.get_mu_sigma(self.activity.get_name())
        # apply the Z-TRANSFORMATION as described in the post:
        # [Schoolsplay-devel] score mathematic
        # See also the "z - Score (zS)" at http://cse.yeditepe.edu.tr/~eozcan/webTools/grading/stat.html
        prclist = utils.score2percentile(scorelist, norm[0], norm[1])
        self.logger.debug("percentile list: %s" % prclist)
        # turn the data into a graph blitted on a SDL surface
        htext = _("Generated by Childsplay_sp version %s for the %s activity") % (Version.version, self.activity.get_name())
        s = Graph(prclist, self.levelcount, norm=norm, headertext=htext)
        dlg = Dialog(s, buttons=[_("Save image"),_("OK")], title=_('Results'))
        dlg.run()
        
        result = dlg.get_result()
        if result[0] == _('Save image'):
            name = self.activity.get_name()
            user = self.dm.get_username()
            level = self.levelcount
            path = os.path.join(HOMEDIR, '%s-%s-level_%s.BMP' % (user, name, level))
            pygame.image.save(s.get_surface(), path)
            dlg = Dialog(_("Your image is saved at:\n%s" % path),dialogwidth=500, \
                       buttons=[_("OK")],  title=_('Information'))
            dlg.run()
        self.activity.refresh_sprites()
        # and release the lock again
        self.lock.release()
        
    #############################################################################
    # SPGoodies callbacks that are passed to the activity and are used as observers
    # by the maincore. The activity calls one of these callbacks from within the
    # activity_loop. This means that when we don't set the
    # run_*_loop to False we will return back to the activity_loop.
    # The whole communication between the core and the activity is based on the
    # observer pattern. The dbase mapper object is not part of SPGoodies but is passed
    # in the activity.start method.
    def disable_menubuttons(self):
        """Activity wants to disable the menu buttons.
        We enable the buttons when the activity ends."""
        self.menubuttons_backup = self.actives_group.sprites()
        self.enable_dice(False)
        self.actives_group.empty()
    def enable_menubuttons(self):
        """Activity wants to enable the menu buttons again."""
        if self.menubuttons_backup:
            self.actives_group.add(self.menubuttons_backup)
            self.menubuttons_backup = []
    def disable_level_indicator(self):
        self.dicebuttons.enable(False)
    def enable_level_indicator(self):
        self.dicebuttons.enable(True)
    def disable_exit_button(self):
        self.actives_group.remove(self.quitbutton)
    def enable_exit_button(self):
        self.actives_group.add(self.quitbutton)
    def disable_score_button(self):
        self.actives_group.remove(self.scoredisplay)
    def enable_score_button(self):
        self.actives_group.add(self.scoredisplay)
    def hide_level_indicator(self):
        self.dicebuttons.erase()
    def show_level_indicator(self):
        self.dicebuttons.show()
    
    
    def activity_pre_level_end(self):
        """The pre_level is ended.
        The core will call next_level on the activity.
        """
        self.logger.debug("activity_pre_level_end called, stopping eventloop")
        self.run_event_loop = False
    
    def activity_level_end(self, store_db=None, nextlevel=None, levelup=False):
        """The level is ended.
        The core will call next_level on the activity.
        @store is used by the activity to signal a normal level end."""
        self.logger.debug("activity_level_end called with: %s,%s,%s" % \
                          (store_db, nextlevel, levelup))
        # reset any clipping
        self.screen.set_clip()
        self.clear_screen()
        sc = False
        if hasattr(self,'mapper') and str(self.mapper) != "BogusMapper":
            self.mapper.insert('end_time', utils.current_time())
            # calculate the time spend inside the level and score
            stime = utils.calculate_time(self.mapper._get_start_time(), \
                self.mapper._get_end_time())
            self.mapper.insert('timespend', stime)
            sc = self.activity.get_score(stime)
            self.logger.debug('got activity score: %s' % sc)
            self.mapper.insert('score', sc)
        if store_db and sc and sc <= 10:# If we don't get a score we store nothing.
            # You MUST call commit to write the contents of the mapper to disk.
            self.mapper.commit()
            # We also passes the score when were in DTmode, the DT act handles the scores.
            if self.DTmode:
                self.DTactivity.act_next_level_stopped(sc)
        else:
            self.logger.debug("no score or score > 10, nothing committed to dbase")
        if self.DTmode:
            self.DTactivity.act_next_level_stopped(sc)
        # we try to stop any timers or execounter, just in case
        try:
            self.activity.stop_timer()
        except:
            pass
        try:
            self.execounter.erase()
        except Exception:
            pass
        # add a little pause between levels.
        if not self.cmd_options.no_level_pause:
            p = os.path.dirname(self.core_rc_path)
            if self.core_rc.has_key('level_change_sound'):
                snd = utils.load_music(os.path.join(p, self.core_rc['level_change_sound']))
            if self.core_rc.has_key('level_change_image'):
                img = utils.load_image(os.path.join(p, self.core_rc['level_change_image']))
                self.screen.blit(img, (275, 200))
                pygame.display.update()
            if not self.core_rc.has_key('level_change_pause'):
                pause = 2
            else:
                pause = int(self.core_rc['level_change_pause'])
            snd.play()
            pygame.time.wait(pause*1000)
        self.clear_screen()
        self.start_next_level(store_db=store_db, nextlevel=nextlevel, levelup=levelup)
                
    def activity_game_end(self, store_db=True):
        """Use this to notify the core that the game is ended.
        The core will start the menu and delete the activity.
        @store is used by the activity to signal a normal level end."""
        self.logger.debug("activity_game_end called")
        try:
            self.lock.release()# release any locks that were set prior to this
        except Exception, info:
            #print info
            pass
        try:
            self.chart_but.erase()
        except Exception, info:
            #print info
            pass
        try:
            self.activity.stop_timer()
        except Exception, info:
            #print info
            pass
        try:
            self.execounter.erase()
        except Exception, info:
            #print info
            pass
        self.levelcount = 1
        #self.set_dice_minimal_level(1)
        self.clear_screen()
        # reset framerate
        self.set_framerate()
        # datacollecting
        if not self.activity.get_name() == 'menu' and store_db and hasattr(self, 'mapper'):
            self.logger.debug("commiting data to dbase")
            self.mapper.commit()# write any sql stuff to disk
        else:
            self.logger.debug("Not commiting data to dbase")
        # check if we are the menu, if so we in deep shit and theres a big problem
        # in the menu
        if self.activity and self.activity.get_name() == 'menu':
            self.logger.critical("I'm the menu, I shouldn't be here, bail out")
            self.logger.exception("Check the logs, there's a problem in the menu")
            sys.exit(1)
        # It seems that Python doesn't free all the memory like expected.
        # we must delete the activity to prevent memoryleak.
        # explicitly set the ref count to 0 for the activity
        del self.activity
        # And tell the garbage collector to free the memory
        gc.collect()
        
        self.dicebuttons.enable(False)
        
        if self.DTmode and self.DTact_is_finished:
            self.DTactivity.act_stopped()
            self.logger.debug("Restarting DT")
            self.activity = self.DTactivity
            self.DTact_is_finished = None
        else:
            # Now we can start the menu
            self.logger.debug("Restarting menu")
            self.activity = self.menu_saved
            self.DTactivity = None
            self.DTmode = None
        text = _("Current activity : %s") % self.activity.get_helptitle()
        if self.activitylabel:
            self.activitylabel.settext(text)
            self.activitylabel.display_sprite()
        self.run_main_loop = True
        self.start_main_loop()
        
    def activity_info_dialog(self, text):
        self.logger.debug("activity_info_dialog called")
        dlg = Dialog(text, (300, 200), buttons=[_('OK')], title=_('Information'))
        dlg.run()
        self.activity.refresh_sprites()
        
    def display_execounter(self, total):
        self.logger.debug("display_execounter called")
        self.execounter = ExeCounter((CORE_BUTTONS_XCOORDS[5], 8), total)
        return self.execounter
        
    # Creates a virtual keyboard gui to be used when running in kioskmode
    def get_virtkb(self):
        """return a virtual keyboard object.
        As this takes some time to create you should not destroy it but
        calls it's hide method to hide it.
        """
        # do we already have a kb?
        if self.vtkb:
            return self.vtkb
        # are we in kioskmode?
        if not self.cmd_options.kioskmode:
            return None
        # setup a new vt kb
        pos = (250, 480)
        fsize = 22
        vkb = VirtualKeyboard(self.screen, fsize, pos)
        self.vtkb = vkb
        return self.vtkb
    
    def set_framerate(self, rate=30):
        """Used by activities to set a lower framerate. Only use this if you
        know why you want to alter the framerate.
        The core resets the framerate to 30 fr/min when loading a activity.
        """
        self.logger.debug("set_framerate called with rate %s" % rate)
        if rate > 30:
            rate = 30
            self.logger.critical("framerate set to %s, which is not allowed as it could run the CPU to 100%" % rate)
        self.framerate = rate

    def enable_dice(self, enable=True):
        if self.menubuttons_backup:
            self.logger.debug("menubuttons disabled, not enabling dice")
            return
        self.logger.debug("enable_dice called with: %s" % enable)
        self.dicebuttons.enable(enable)

    def set_dice_minimal_level(self, level):
        self.logger.debug("set_dice_minimal_level called with: %s" % level)
        self.dicebuttons.set_minimal_level(level)
        self.enable_dice(True)
        
    # Added to the spgoodies for the menu and dltr activity
    def _menu_activity_userchoice(self, activity):
        self.logger.debug("menu_activity_userchoice called with %s" % activity)
        if not self.DTmode:
            self.menu_saved = self.activity
        self.load_activity(activity)
    
    ############################################################################
    # Here we start the loop. This loop will call activity.start and the calls 
    # the activity eventloop.
    #
    # The way to get out of the start_main_loop is when the user hits the escape
    # key which will raise an exception that we catch in start_main_loop.
    # We will ask to really quit or not, if not we don't break but call the
    # activity_loop again. The hitting of the quit button works the same as
    # the escape key.
    #
    # The other way to get out of activity_loop is when the activity level is ended
    # then the activity calls the callback: activity_level_end (see above)
    # The activity is passed a class object called SPGoodies which holds a number
    # of 'observer' methods which calls methods in the core. So when we talk about
    # the activity that calls callbacks, we mean SPGoodies observers.
    # This callback will determine what's next, but in fact were now out of the
    # start_main_loop. If there are more levels the activity_level_end method
    # will call the activity_loop again. 
    #
    # Finally we can break out when the activity is ended because all levels are done.
    # Then the activity will call the callback: activity_game_end (see above)
    # This callback will call activity.cleanup() to force any cleanup by the activity
    # and delete the activity. Then it will restart the menu and call the start_main_loop
    # which will run the menu again.
    #
    # In short:
    # The menu is constructed and start_main_loop is called.
    # Menu is started and the activity_loop is called which will loop the menu loop
    # until the user hits a button.
    # Then the menu will call SPGoodies.menu_activity_userchoice which will end
    # the menu and start the choosen activity.
    # Then the start_main_loop is called by menu_activity_userchoice and the 
    # activity is started and the activity_loop is called. This will loop until
    # the activity calls one of the SPGoodies callbacks which will jump out the loop
    # and determine what's next. 
    def start_main_loop(self):
        self.levelcount = 0
        error = False
        store = True
        # we only break this loop on SP quit or escape key
        # The menu activity starts this also from _menu_activity_userchoice
        while self.run_main_loop:
            if self.activity.get_name() != 'menu':
                self.logger.debug("Start activity start")
                try:
                    self.start_start()
                except (utils.MyError, utils.StopGameException), info:
                    self.logger.error("%s" % info)
                    self.run_event_loop = False
                    self.run_activity_loop = False
                    self.run_main_loop = False
            self.run_activity_loop = True
            try:
                self.logger.debug("Start activity loop")
                self.start_pre_level_loop()
            except EscapeKeyException:
                # user hits escape
                self.logger.info("User hits escape")
                self.ask_exit()# if this returns the user said no.
                store = False
            except utils.StopGameException:
                self.logger.debug("User hits quit menubutton")
                self.run_event_loop = False
                self.run_activity_loop = False
                self.run_main_loop = False
                store = False
            except utils.MyError, info:
                # trouble in paradise
                self.logger.error("start_main_loop: MyError, %s" % info)
                self.run_event_loop = False
                self.run_activity_loop = False
                self.run_main_loop = False
                error = True
                store = False
            except StandardError, info:
                # even more trouble in paradise
                self.logger.exception("start_main_loop: StandardError, %s" % info)
                self.run_event_loop = False
                self.run_main_loop = False
                error = True
                store = False
            
                
        self.logger.debug("Break out of start_main_loop")
        if self.activity.get_name() != 'menu' or error:
            self.activity_game_end(store_db=store)
        else:
            self.ask_exit()# if this returns the user said no
            self.logger.debug("Restarting menu")
            self.activity.start()
            text = _("Current activity : %s") % self.activity.get_helptitle()
            if self.activitylabel:
                self.activitylabel.settext(text)
                self.activitylabel.display_sprite()
            self.run_main_loop = True
            self.start_main_loop()
            
    def start_pre_level_loop(self):
        # Start the pre_level method once and calls the eventloop.
        self.were_in_pre_level = False
        try:
            self.were_in_pre_level = True
            if self.activity.get_name() != 'dltr' and self.DTmode:
                if not self.menubuttons_backup:
                    self.dicebuttons.next_level(self.DTlevelcount)
                self.logger.debug("Calling dailytraining_pre_level with level: %s" % (self.levelcount + 1))
                self.run_event_loop = self.activity.dailytraining_pre_level(self.DTlevelcount + 1)
            else:
                if not self.menubuttons_backup:
                    self.dicebuttons.next_level(self.levelcount)
                self.logger.debug("Calling pre_level with level: %s" % (self.levelcount + 1))
                self.run_event_loop = self.activity.pre_level(self.levelcount + 1)
        except utils.MyError, info:
            self.logger.error("Exception raised in the activity %s: %s" % (self.activity.get_name(), info))
            self.run_event_loop = False
            self.run_activity_loop = False
            self.run_main_loop = False
            
        # enter activity level eventloop if run_event_loop == True
        if self.run_event_loop:
            self.logger.debug("Enter pre_level eventloop")
            self._main_loop()
            self.logger.debug("run_event_loop done")
        self.were_in_pre_level = False
        self.run_activity_loop = True
        self.run_event_loop = False 
        
        self.start_activity_loop()

    def start_activity_loop(self):
        # start stepping throught the activity levels
        while self.run_activity_loop:
            try:
                self.logger.debug("Start next_level")
                self.start_next_level(store_db=True)
            except utils.MyError, info:
                self.logger.error("Exception raised in the activity %s: %s" % (self.activity.get_name(), info))
                if self.activity.get_name() == 'menu':
                    self.logger.error('Exception occurred in the menu, quiting')
                    raise utils.SPError
                self.run_event_loop = False
                self.run_activity_loop = False
                self.run_main_loop = False
                #self.activity_game_end()
            # block events from entering the queue.
            # Pro: cpu usage drops dramaticly.
            # Con: gui can't show fancy color changes in the widgets as the 
            #       mouse passes over them.
#            if self.activity.get_name() == 'menu':
#                # we need mousemotion for the tooltips
#                pygame.event.set_allowed([KEYDOWN, MOUSEBUTTONDOWN, MOUSEMOTION])
#            else:
#                # and here we block mousemotion to conserve cpu usage
#                pygame.event.set_blocked(MOUSEMOTION)
            else:
                self.run_event_loop = True
                # enter activity level eventloop
                self.logger.debug("Enter eventloop")
                self._main_loop()
                self.logger.debug("run_event_loop done")

    def _main_loop(self):
        self.logger.debug("Starting main_loop with framerate %s" % self.framerate)
        pygame.event.clear()
        while self.run_event_loop:
            self.clock.tick(self.framerate)
            pygame.event.pump()
            events = pygame.event.get()
            self.myspritesactivated = None
            for event in events:
                if event.type == KEYDOWN:
                    if event.key is K_ESCAPE or event.type is QUIT:
                        self.run_event_loop = False
                        raise EscapeKeyException
                    elif event.key == K_F1 and 'screenshots' in sys.argv:
                        pass
                        # THIS IS ONLY FOR TAKING SCREENSHOTS
#                        try:
#                            scr = pygame.display.get_surface()
#                            path = os.path.join(HOMEDIR, self.activity.get_name() + '.jpeg')
#                            pygame.image.save(scr, path)
#                            self.logger.info("Screenshot %s taken" % path)
#                        except RuntimeError, info:
#                            self.logger.error("Failed to make screenshot %s" % info)
                        # END OF SCREENSHOT STUFF
                    # Only for debugging memoryleaks
                    #elif event.key == K_F2:
                    #    utils.memory_profile(h)
                self.actives_group.update(event) 
            if self.myspritesactivated:
                continue
            # Call the activity loop.
            try:
                self.activity.loop(events)
            except utils.StopGameException, info:
                self.logger.debug("_main_loop, StopGameException")
                # stop loops
                self.run_event_loop = False
                self.run_activity_loop = False
                self.activity_game_end(store_db=False)
            except StandardError, info:
                self.activity.stop_timer()
                self.logger.exception("%s raised an unhandled exception: %s traceback follows:" % \
                    (self.activity.get_name(), info))
                self.activity_info_dialog(_("There was an error in %s. Please check the logs and inform the developers") % self.activity.get_name())
                # make sure we have enabled menubuttons
                self.enable_menubuttons()
                # stop loops
                self.run_event_loop = False
                self.run_activity_loop = False
                self.activity_game_end(store_db=False)
            except KeyboardInterrupt:
                try:
                    utils.load_music(os.path.join(CORESOUNDSDIR, 'hal.ogg')).play()
                    pygame.time.wait(10000)
                except:
                    pass
                self.logger.exception("KeyboardInterrupt stopping all threads")
                try:
                    self.activity.stop_timer()
                except:
                    pass
                self.logger.warning("Raising SystemExit to quit")
                raise SystemExit

if __name__ == '__main__':
    utils.set_locale()# TODO: add lang argument
    try:
        mcgui = MainCoreGui((800, 600))
    except SystemExit, status:
        if str(status) == '0':
            module_logger.info("clean exit")
        else:
            module_logger.info("not a clean exit")
    except Exception, status:
        module_logger.exception("unhandled exception in toplevel, traceback follows:")
            
