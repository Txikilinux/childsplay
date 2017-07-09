# -*- coding: utf-8 -*-

# Copyright (c) 2006-2008 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
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

import atexit
import os
import pygame
import threading
import types
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

import childsplay_sp.ocempgui.widgets as ocw

from SPSpriteUtils import SPInit, MySprite, set_big_mouse_cursor
from SPGoodies import SPGoodies

# This is a kludge to execute the toplevel code in SPConstants as it is already
# imported in SPlogging before the loggers are set.
import SPConstants
reload(SPConstants)
from SPConstants import *

import SPMenu as SPMenu
import SPCoreButtons as SPCoreButtons
import SPDataManager as SPDataManager
import Version
from SPocwWidgets import ExitDialog, InfoDialog, GraphDialog, Graph, Label, \
    ExeCounter
from SPVirtualkeyboard import VirtualKeyboard
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
        global ACTIVITYDATADIR
        self.cmd_options = options
        if self.cmd_options.theme == 'cognitionplay':
            ACTIVITYDATADIR = ACTIVITYDATADIR.replace('childsplay_sp', 'cognitionplay')
        self.logger = logging.getLogger("schoolsplay.SPMainCore.MainCoreGui")
        self.logger.debug("Start")
        if self.cmd_options.no_sound:
            self.logger.info("Disabling sound support as requested by user")
            pygame.mixer.quit()
        # set mouse cursor ?
        # TODO: use different cursors with an cmdline option
        if self.cmd_options.bigcursor:
            cursorfile = os.path.join(ACTIVITYDATADIR, 'SPData', 'base', 'icons', 'cursor_1.xbm')
            maskfile = os.path.join(ACTIVITYDATADIR, 'SPData', 'base', 'icons', 'cursor_1-mask.xbm')
            set_big_mouse_cursor(cursorfile, maskfile)
        self.resolution = resolution
        self.vtkb = None # will become the virtual keyboard object
        ## Set icon for the window manager ## 
        ICONPATH = os.path.join(ACTIVITYDATADIR, 'SPData', 'menu', self.cmd_options.theme)
        DEFAULTICONPATH = os.path.join(ACTIVITYDATADIR, 'SPData', 'menu', 'default')
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
        # setup main screen
        # The screen is devided in two parts. one for the ocempgui renderer and one for
        # the activities. Pygame can only handle one mainscreen, so we use the pygame
        # screen for the activities and a pygame surface for the renderer.
        # The activities only use (0,0,800,500) so we don't need to update the
        # renderer screen all the time. We can't update the renderer screen as we 
        # do the pygame mainscreen so we blit the renderer surface when needed
        # to the mainscreen. We don't need ocempgui on the mainscreen to use it.
        # this is the pygame mainscreen
        if self.cmd_options.fullscreen:
            self.screen = pygame.display.set_mode(self.resolution, FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.resolution)
        self.backgr = self.screen.convert()# a real copy
        captxt = _("Childsplay_sp - educational activities")
        if self.cmd_options.theme == 'cognitionplay':
            captxt = captxt.replace('Childsplay_sp', 'Cognitionplay')
        pygame.display.set_caption(captxt.encode('utf-8'))
        # self.activity_screen is only a surface we use to clear the screen.
        self.activity_screen = pygame.Surface((800, 500)).convert()
        self.activity_screen.fill((0, 0, 0))
        # backgr must be the same as it is used in the SpriteUtils to erase sprites
        self.backgr.blit(self.activity_screen, (0, 0))
        
        # init SpriteUtils, mandatory when using SpriteUtils
        self.actives_group = SPInit(self.screen, self.backgr)
        # shortcut
        self.col = pygame.color.Color
        # Thread lock, must be used by activities to be able to block evrything.
        self.lock = threading.Lock() 
        # setup SPGoodies which we pass to the activities
        # screen clip is set to None as it don't work properly with oyher widgets
        # activities should take care not to overwrite the menubar
        self.screenclip = pygame.Rect(0, 0, 800, 500)
        self.spgoodies = SPGoodies(self.screen, self.backgr, self.screenclip, \
            self.get_virtkb, \
            language, \
            self.lock, \
            self.activity_level_end, \
            self.activity_game_end, \
            self.activity_info_dialog, \
            self.display_execounter, \
            self.set_framerate, \
            self.enable_dice)
        self.spgoodies._menupath = 'SP_menu.xml'
        self.spgoodies._theme = self.cmd_options.theme
        self.spgoodies._menu_activity_userchoice = self._menu_activity_userchoice
        self.spgoodies._cmd_options = self.cmd_options
        # first we start with the SPgdm login
        # get a datamanager which will also handle the login screen
        try:
            self.dm = SPDataManager.DataManager(self.spgoodies)
        except sqla_exceptions.SQLError:
            self.logger.exception("Error while handeling the dbase, try removing the existing dbase")
        # setup misc stuff
        
        # restore window title after the datamanager replaced it
        pygame.display.set_caption(captxt.encode('utf-8'))
        self.clock = pygame.time.Clock()
        self.run_activity_loop = True
        self.run_event_loop = True
        self.run_main_loop = True
        
        # We get the menu activity here. We need the ocwcol so we create the menu before
        # the renderer. The rest of the menu is setup later.
        try:
            self.activity = SPMenu.Activity(self.spgoodies)
        except Exception, info:
            self.logger.exception("Failed to setup the menu")
            raise utils.MyError, info
        # get a reference to the menu, we also use it to get help the text
        self.menu_saved = self.activity
        ocwcol = self.activity._get_ocwcol()
        # Here setup the ocempgui renderer for the menubar
        self.renderer = ocw.Renderer()
        if type(ocwcol) != types.TupleType:
            self.logger.error("failed to set menubar color/image: %s" % repr(ocwcol))
            ocwcol = self.col('LightSteelBlue')
            self.logger.debug("set menubar color to:%s" % repr(ocwcol))
            self.renderer.set_screen(pygame.Surface((800, 100)).convert())
            self.renderer.color = (ocwcol)
        else:
            try:
                # first we check if ocwcol is a image path
                if type(ocwcol[0]) is types.UnicodeType:
                    if os.path.exists(ocwcol[0]):# it's always wrapped in a tuple
                        self.renderer.set_screen(utils.load_image(ocwcol[0], alpha=1, transparent=1))
                else:
                    self.renderer.set_screen(pygame.Surface((800, 100)).convert())
                    self.renderer.color = (ocwcol)
            except:
                self.logger.exception("Failed to setup the menubar")
                self.logger.error("Failed to setup the menubar, check your %s" % self.spgoodies._menupath)
                ocwcol = self.col('LightSteelBlue')
                self.logger.debug("set menubar color to:%s" % repr(ocwcol))
                # get a new renderer, just in case the old one is fucked up by previous errors
                self.renderer = ocw.Renderer()
                self.renderer.set_screen(pygame.Surface((800, 100)).convert())
                self.renderer.color = (ocwcol)
        # finish the ocempgui renderer
        self.renderer_blit_pos = (0, 500)# were are we gonna blit the renderer screen
        self.cb = SPCoreButtons.MainCoreButtons(self.cmd_options.theme, \
            self.core_quit_button_pressed, \
            self.core_info_button_pressed)
        ocwbuts = self.cb.get_buttons()# returns a dict
        self.renderer.add_widget(* ocwbuts.values())
        # we must set the render coords to the coords to which it will be blitted.
        self.renderer.topleft = self.renderer_blit_pos
        
        # setup the dice button
        # This is a class which implements 6 dice buttons and by calling dice.next_level(int)
        # the correct dice is placed in the renderer and it's refreshed.
        self.dice = SPCoreButtons.DiceButtons(self.renderer, \
            self.core_dice_button_pressed)
                                                
        # add the current user, if it exists
        text = _("User: %s") % self.dm.get_username()
        if self.cmd_options.adminmode:
            text = text + " (Adminmode)"
        self.usernamelabel = Label(self.renderer, text, (CORE_BUTTONS_XCOORDS[1], 10))
        text = _("Activity : %s") % self.activity.get_helptitle()
        self.activitylabel = Label(self.renderer, text, (CORE_BUTTONS_XCOORDS[1], 50))
        
        #set framerate
        self.framerate = 30
        
        # Show the mainscreen and blit renderer
        self.clear_screen()
        
        # start menu
        self.activity.start()
        self.start_main_loop()
        
    ############################################################################
    ## Methods for internal use 
    def update_renderer(self):
        # force renderer to update its surface
        self.renderer.update()
        # As we don't use ocempgui on the mainscreen
        # we must 'manually' blit the renderer screen to the mainscreen
        self.screen.set_clip()
        r = self.screen.blit(self.renderer.screen, self.renderer.topleft)
        pygame.display.update(r)
        self.screen.set_clip(self.screenclip)
 
    def clear_screen(self):
        self.logger.debug("clear_screen called")
        # rebuild screen with the standard background 
        self.menu_saved._remove_buttons()# if any
        self.screen.set_clip(self.screenclip)# reset any clipping
        pygame.display.update(self.screen.blit(self.menu_saved.saved_screen, (0, 0)))
        self.update_renderer()
        self.screen.set_clip()
        self.backgr.blit(self.screen.convert(), (0, 0))
        # reset the screens in SPGoodies so that any activities gets a proper screen.
        #self.screen.set_clip(self.screenclip)
        self.spgoodies.screen = self.screen
        self.spgoodies.background = self.backgr
        
    def load_activity(self, name):
        # This will replace self.activity with the choosen activity
        self.logger.debug("load_activity called with %s" % name)
        self.set_framerate()
        try:
            # Check if we are running locally for developing activities
            if hasattr(self.spgoodies._cmd_options, 'run_local'):
                self.logger.debug("We running from source, trying to import activity from cwd/lib")
                # When we run locally, meaning from sources, the activities still import utils
                # from the installed childsplay_sp package and when they raise an exception defined
                # in utils we can catch it because we import utils from sources.
                # That's why we check if we run from sources by checking for a special attribute
                # set in childsplay_sp_local
                import utils
                self.activity_module = utils.import_module(os.path.join('lib', name))
            else:
                self.logger.debug("Trying to import activity from childsplay_sp.lib")
                self.activity_module = getattr(__import__('childsplay_sp.lib', \
                    globals(), locals(), [str(name)]), name)
            self.activity = self.activity_module.Activity(self.spgoodies)
        except (utils.MyError, ImportError, AttributeError), info:
            self.logger.exception("Error importing activity %s" % name)
            # we must use a new renderer so that we leave the screen intact that
            # is used by the pygame sprite classes.
            re = ocw.Renderer()
            re.set_screen(self.screen)
            dlg = InfoDialog(re, ["Error importing activity: %s" % info])
            dlg.run()
            self.activity = self.menu_saved
            self.start_main_loop()
        except (utils.MyError, StandardError), info:
            self.logger.exception("Error constructing activity: %s" % info)
            re = ocw.Renderer()
            re.set_screen(self.screen)
            dlg = InfoDialog(re, ["Error constructing activity: %s" % info])
            dlg.run()
            self.activity = self.menu_saved
            self.start_main_loop()
        else:
            self.logger.debug("Loaded %s activity succesfull" % self.activity)
            text = _("Activity : %s") % self.activity.get_helptitle()
            self.activitylabel.rename(text, (CORE_BUTTONS_XCOORDS[1], 50))
            self.update_renderer()
            self.start_main_loop()
            
    def start_start(self):
        self.logger.debug("Calling activity start")
        self.levelcount = 0
        
        try:
            self.activity.start()
        except Exception, info:
            self.logger.exception("Error in %s start" % self.activity.get_name())
            raise utils.MyError, info
        if not self.dm.anonymous:
            # as were datacollectors we also add a chart button to the menubar
            # we make the button a attribute as we must remove it when the game
            # is finished
            self.chart_but = SPCoreButtons.ChartButton(self.renderer, \
                self.cmd_options.theme, \
                self.core_chart_button_pressed)
                                            
    def display_levelstart(self, level):
        """Displays a 'ready 3-2-1' screen prior to starting the level.
        It also displays a blocking 'Start' button."""
          
        self.logger.debug("Starting display_levelstart")
        if self.cmd_options.no_text:
            return
        org_screen = pygame.display.get_surface().convert()
        org_backgr = self.backgr.convert()

        self.screen.set_clip()
        
        # disable the dice to prevent users clicking it
        self.dice.enable(False)
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
        pygame.event.clear()    
        # restore the screens
        # undim the screen
        sdim.dim(darken_factor=255, color_filter=(0, 0, 0))
        self.screen.blit(org_screen, (0, 0))
        self.backgr.blit(org_backgr, (0, 0))
        # reset the screens in SPGoodies so that any activities gets a proper screen.
        SPInit(self.screen, self.backgr)
        pygame.display.update()
        # and enable the dice again
        self.dice.enable(True)
        self.screen.set_clip(self.screenclip)
        
    def start_next_level(self, store_db=None):
        """store_db is used to signal normal ending and that we should store the data"""
        self.levelcount += 1
        self.logger.debug("Calling activity next_level")
        # are we in the data collecting bussiness ?
        if not self.activity.get_name() == 'menu':
            if store_db:
                # Here we fetch our data colletor object, we collect data per level,
                # so it's the best place to start datacollecting
                # get_mapper returns always an object, in case of anonymous mode the 
                # object is a fake.
                self.mapper = self.dm.get_mapper(self.activity.get_name())
                self.mapper.insert('level', self.levelcount)
                self.mapper.insert('start_time', utils.current_time())
        # disable any clipping
        self.screen.set_clip()
        try:
            if self.activity.get_name() == 'menu':
                self.activity.next_level(self.levelcount)
            # we pass the db mapper so that the activity can store it's data
            elif not self.activity.next_level(self.levelcount, self.mapper):
                self.logger.debug("start_activity_loop: Levels ended")
                self.activity_info_dialog(self.activity.get_helplevels())
                self.activity_game_end()
            else:
                self.dice.next_level(self.levelcount)
                self.update_renderer()
                # We display a blocking ready-start screen
                self.display_levelstart(self.levelcount)
                # and call the post_next_level
                self.activity.post_next_level()
        except utils.MyError, info:
            self.logger.exception("Error in %s next_level" % self.activity.get_name())
            raise utils.MyError, info
        # reset clipping
        self.screen.set_clip(self.screenclip)
        
    def ask_exit(self):
        # we must use a new renderer so that we leave the screen intact that
        # is used by the pygame sprite classes.
        if not self.cmd_options.noexitquestion:
            re = ocw.Renderer()
            re.set_screen(self.screen)
            dlg = ExitDialog(re)
            c = dlg.run()
        else:
            c = 0
        if c == 0:
            self.logger.info("User wants exit")
            print self.activity.get_name()
            if self.activity.get_name() != 'menu':
                try:
                    self.activity_game_end()
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
            y = 60
            for line in txt:
                s = utils.char2surf(line, P_TTFSIZE + 12, fcol=GREEN, ttf=P_TTF, bold=True)
                self.screen.blit(s, (10, y))
                y += s.get_height()
            pygame.display.update()
            pygame.time.wait(1000)# just to show the text in case there are no timers 
            raise MainEscapeKeyException # let schoolsplay.py decide what next
            
    ###########################################################################
    # Main menubar button callbacks. Passed to SPCoreButtons.MainCoreButtons
    # These are called when the user hits the buttons in the lower menu bar of 
    # screen.
    def core_info_button_pressed(self, button):
        self.logger.debug("core_info_button_pressed %s" % button)
        self.lock.acquire()
        # we must use a new renderer so that we leave the screen intact that
        # is used by the pygame sprite classes.
        re = ocw.Renderer()
        re.set_screen(self.screen)
        # Construct the help text from the activity's various get_help* methods
        help = self.activity.get_help()
        if self.activity.get_name() != 'menu':
            tip = self.activity.get_helptip()
            if tip:
                help.append(_("Tip:"))
                help += tip + [" "]
            help.append(self.activity.get_helplevels())
            help.append(_("This activity belongs to the category: %s") % self.activity.get_helptype())
        d = InfoDialog(re, help, fnsize=14)
        d.run()
        # restore any crap that is put onto the menubar by the dialog
        self.update_renderer()
        self.lock.release()
        
    def core_quit_button_pressed(self, button):
        self.logger.debug("core_quit_button_pressed %s" % button)
        self.lock.acquire()
        if self.activity.get_name() == 'menu':
            self.ask_exit()# if this returns the user said no.
            self.lock.release()
            return
        else:
            self.lock.release()
            self.activity_game_end()
    # Callback for the dice in the menu bar. Passed to SPCoreButtons.DiceButtons
    def core_dice_button_pressed(self, button):
        self.logger.debug("core_dice_button_pressed %s" % button)
        self.activity_level_end()
    # Callback for the chart button in the menubar. Passed to SPCoreButtons.ChartButton
    def core_chart_button_pressed(self, button):
        self.logger.debug("core_chart_button_pressed %s" % button)
        self.lock.acquire()
        # get data, user AND level
        query = self.mapper._get_level_data(levelnum=self.levelcount)
        # get the score and date data from the objects
        scorelist = filter(None, [(getattr(item, 'start_time'), getattr(item, 'score')) for item in query])
        self.logger.debug("scorelist from SQL query: %s" % scorelist)
        # get the mu and sigma for this activity.
        norm = self.dm.get_mu_sigma(self.activity.get_name())
        # TODO: apply the Z-TRANSFORMATION as described in the post:
        # [Schoolsplay-devel] score mathematic
        # See also the "z - Score (zS)" at http://cse.yeditepe.edu.tr/~eozcan/webTools/grading/stat.html
        utils.Zscore(scorelist, norm[0], norm[1])# just as testcode
        # turn the data into a graph blitted on a SDL surface
        htext = _("Generated by Childsplay_sp version %s for the %s activity") % (Version.version, self.activity.get_name())
        s = Graph(scorelist, self.levelcount, norm=norm, headertext=htext).get_surface()
        ilbl = ocw.ImageLabel(s)
        # we must use a new renderer so that we leave the screen intact that
        # is used by the pygame sprite classes.
        re = ocw.Renderer()
        re.set_screen(self.screen)
        # set dialog to opacity 255, non transparent, because the graph uses
        # transparenty also.
        d = GraphDialog(re, ilbl, fnsize=14, savebutton=self.cmd_options.adminmode)
        result = d.run()
        if result:
            # True means save button is hit.(only in adminmode)
            name = self.activity.get_name()
            user = self.dm.get_username()
            level = self.levelcount
            path = os.path.join(HOMEDIR, '%s-%s-level_%s.BMP' % (user, name, level))
            pygame.image.save(s, path)
            d = InfoDialog(re, [_("Your image is saved at:\n%s" % path)])
            d.run()
        # restore any crap that is put onto the menubar by the dialog
        self.update_renderer()
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
    def activity_level_end(self, store_db=None):
        """Use this to notify the core that the level is ended.
        The core will call next_level on the activity.
        @store is used by the activity to signal a normal level end."""
        self.logger.debug("activity_level_end called")
        if store_db:
            self.mapper.insert('end_time', utils.current_time())
            # calculate the time spend inside the level and store it
            stime = utils.calculate_time(self.mapper._get_start_time(), \
                self.mapper._get_end_time())
            self.mapper.insert('timespend', stime)
            # get the score value, if any and insert it into the dbase
            sc = self.activity.get_score(stime)
            self.logger.debug('got activity score: %s' % sc)
            self.mapper.insert('score', sc)
            # You MUST call commit to write the contents of the mapper to disk.
            self.mapper.commit()
        # we try to stop any timers or execounter, just in case
        try:
            self.activity.stop_timer()
        except:
            pass
        try:
            self.execounter.erase()
        except Exception:
            pass
        self.start_next_level(store_db=store_db)
        
    def activity_game_end(self, store_db=None):
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
            self.dice.erase()
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
        self.clear_screen()
        # reset framerate
        self.set_framerate()
        # datacollecting
        if not self.activity.get_name() == 'menu' and store_db:
            self.mapper.commit()# write to any sql stuff to disk
        # check if we are the menu, if so we in deep shit and theres a big problem
        # in the menu
        if self.activity and self.activity.get_name() == 'menu':
            self.logger.critical("I'm the menu, I shouldn't be here, bail out")
            self.logger.exception("Check the logs, there's a problem in the menu")
            sys.exit(1)
        # Start menu again
        try:
            self.activity = self.menu_saved
        except Exception, info:
            self.logger.error("Failes to restore menu: %s" % info)
            self.activity = SPMenu.Activity(self.spgoodies)
            self.activity.start()
        text = _("Current activity : %s") % self.activity.get_helptitle()
        self.activitylabel.rename(text, (CORE_BUTTONS_XCOORDS[1], 50))
        self.update_renderer()
        self.start_main_loop()
        
    def activity_info_dialog(self, text):
        self.logger.debug("activity_info_dialog called")
        re = ocw.Renderer()
        re.set_screen(self.screen)
        d = InfoDialog(re, text, fnsize=18)
        d.run()
        
    def display_execounter(self, total):
        self.logger.debug("display_execounter called")
        self.execounter = ExeCounter(self.renderer, total, (0, 0, 255), self)
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
            raise StandardError
        self.framerate = rate

    def enable_dice(self, enable=True):
        self.logger.debug("enable_dice called with: %s" % enable)
        self.dice.enable(enable)

    # Added to the spgoodies for the menu activity
    def _menu_activity_userchoice(self, activity):
        self.logger.debug("menu_activity_userchoice called with %s" % activity)
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
        # we only break this loop on SP quit or escape key
        # The menu activity starts this also from _menu_activity_userchoice
        while self.run_main_loop:
            if self.activity.get_name() != 'menu':
                self.logger.debug("Start activity start")
                try:
                    self.start_start()
                except utils.MyError, info:
                    self.logger.error("%s" % info)
                    self.run_event_loop = False
                    self.run_activity_loop = False
                    # this way we don't crash but return to the menu
                    self.activity_game_end()
            self.run_activity_loop = True
            try:
                self.logger.debug("Start activity loop")
                self.start_activity_loop()
            except EscapeKeyException:
                # user hits escape
                self.logger.info("User hits escape")
                self.ask_exit()# if this returns the user said no.
            except utils.MyError, info:
                # trouble in paradise
                self.logger.error("start_main_loop: MyError, %s" % info)
                self.run_event_loop = False
                self.run_activity_loop = False
                #self.run_main_loop = False
                # this way we don't crash but return to the menu
                self.activity_game_end()
            except StandardError, info:
                # even more trouble in paradise
                self.logger.exception("start_main_loop: StandardError, %s" % info)
                self.run_event_loop = False
                #self.run_activity_loop = False
                self.activity_game_end()
        self.logger.debug("Break out of start_main_loop")
                
        
    def start_activity_loop(self):
        # start stepping throught the activity levels
        while self.run_activity_loop:
            try:
                self.logger.debug("Start next level")
                self.start_next_level(store_db=True)
            except utils.MyError, info:
                self.logger.error("Exception raised in the activity %s: %s" % (self.activity.get_name(), info))
                self.run_event_loop = False
                self.run_activity_loop = False
                self.activity_game_end()
            # block events from entering the queue.
            # Pro: cpu usage drops dramaticly.
            # Con: ocempgui can't show fancy color changes in the widgets as the 
            #       mouse passes over them.
            pygame.event.clear()
            if self.activity.get_name() == 'menu':
                # we need mousemotion for the tooltips
                pygame.event.set_allowed([KEYDOWN, MOUSEBUTTONDOWN, MOUSEMOTION])
            else:
                # and here we block mousemotion to conserve cpu usage
                pygame.event.set_blocked(MOUSEMOTION)
            self.run_event_loop = True
            # enter activity level eventloop
            self.logger.debug("Enter eventloop")
            while self.run_event_loop:
                self.clock.tick(self.framerate)
                pygame.event.pump()
                events = pygame.event.get()
                # let ocempgui handles the gui events, if needed
                # renderer loops the events
                self.renderer.distribute_events(* events)
                #pygame.display.update (self.renderer.screen.get_rect ())
                for event in events:
                    if event.type == KEYDOWN:
                        if event.key is K_ESCAPE or event.type is QUIT:
                            self.run_event_loop = False
                            raise EscapeKeyException
                        elif event.key == K_F1 and 'screenshots' in sys.argv:
                            # THIS IS ONLY FOR TAKING SCREENSHOTS
                            try:
                                scr = pygame.display.get_surface()
                                path = os.path.join(HOMEDIR, self.activity.get_name() + '.BMP')
                                pygame.image.save(scr, path)
                                self.logger.info("Screenshot %s taken" % path)
                            except RuntimeError, info:
                                self.logger.error("Failed to make screenshot %s" % info)
                            # END OF SCREENSHOT STUFF
                            
                # Call the activity loop.
                try:
                    self.activity.loop(events)
                except StandardError, info:
                    self.activity.stop_timer()
                    self.logger.exception("%s raised an unhandled exception: %s traceback follows:" % \
                        (self.activity.get_name(), info))
                    self.activity_info_dialog(_("There was an error in %s. Please check the logs and inform the developers") % self.activity.get_name())
                    # stop loops
                    self.run_event_loop = False
                    self.run_activity_loop = False
                    self.activity_game_end()
            self.logger.debug("run_event_loop done")

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
            
