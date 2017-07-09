# -*- coding: utf-8 -*-

# Copyright (c) 2007 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
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

### OBSOLETE 

import sys
sys.path.append('lib')

# first parse commandline options
from SPOptionParser import OParser
# if this doesn't bail out the options are correct and we continue with schoolsplay
op = OParser()
# this will return a class object with the options as attributes 
# OLPC: set default options in the OParser class as we don't have cmd line options
CMD_Options = op.get_options()

import SPLogging
SPLogging.set_level(CMD_Options.loglevel)
SPLogging.start()

try:
    from sugar.activity import activity as sgactivity
    from sugar.graphics.toolbutton import ToolButton
except ImportError:
    # not running on a XO
    SUGAR=False
else:
    SUGAR=True

import utils
# this will return the tuple (lang,rtl=bool)
LANG = utils.set_locale(lang=CMD_Options.lang)   

import os,atexit,types,time,threading
import gtk

#create logger, logger was configured by Sugar, or by SPLogging (see above)
import logging
module_logger = logging.getLogger("schoolsplay.SchoolsplayActivity")

import utils

# This is a kludge to execute the toplevel code in SPConstants as it is already
# imported in SPlogging before the loggers are set.
import SPConstants
reload(SPConstants)
from SPConstants import *

from SPGoodies import SPGoodies
from SPConstants import *
import Version
import SPMenu
import SPDataManager
import SPgdm

# check if we have sqlalchemy database support.
# Add sqlalchemy to the path as we pack it ourselfs
sys.path.append('sqlalchemy')
try:
    import sqlalchemy
except ImportError:
    module_logger.debug("No sqlalchemy package found, running in anonymousmode")
    CMD_Options.no_login = True   
from sqlalchemy import exceptions as sqla_exceptions

# This holds the from libglade generated gui
import sp_cr
# misc gtk widgets
import SPWidgets

# Used to cleanup stuff when the Python vm ends
def cleanup():
    module_logger.info("flushing dbase to disk")
    module_logger.info("cleanup called, logger stops")
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

class SPToolbar(gtk.Toolbar):
    """A custom toolbar to be used in the sugar toolbox as we don't use the bottom
    menu bar we use in the nonsugar version.
    We use the normal buttons and labels so it's just a redesign the logic is the same."""
    def __init__(self,parent):
        """We setup different buttons and labels but we connect them to the parents
        callbacks just like sp_cr does in the normal SP"""
        gtk.Toolbar.__init__(self)
        self.logger = logging.getLogger("schoolsplay.SchoolsplayActivity.SPToolbar")
        self._parent = parent
        self.dicelist = ['dice-1','dice-2','dice-3','dice-4','dice-5','dice-6']
        
        self.quitbut = ToolButton('sp_quit')
        self.quitbut.set_tooltip(_("Quit this activity and return to the menu"))
        self.quitbut.connect('clicked', self._parent.core_quit_button_pressed)
        self.insert(self.quitbut, -1)
        #self.quitbut.show()
        
        self.helpbut = ToolButton('sp_info')
        self.helpbut.set_tooltip(_("Get help about this activity"))
        self.helpbut.connect('clicked', self._parent.core_info_button_pressed)
        self.insert(self.helpbut, -1)
        self.helpbut.show()
        
        self.graphbut = ToolButton('chart')
        self.graphbut.set_tooltip(_("Get your results from this activity"))
        self.graphbut.connect('clicked', self._parent.core_graph_button_pressed)
        self.insert(self.graphbut, -1)
        #self.graphbut.show()
                
        self.next_dice(1)
        self.dicebut.set_sensitive(False)

        
    def next_dice(self,count):
        self.logger.debug("next_dice called with:%s" % count)
        self.dicecounter = count
        self.dicebut = ToolButton(self.dicelist[count-1])
        self.dicebut.set_tooltip(_("Switch to another level"))
        self.dicebut.connect('clicked', self.on_button_dice_clicked)
        self.insert(self.dicebut, -1)
        #self.dicebut.show()
        #self.dicebut.set_sensitive(True)

    def on_button_dice_clicked(self, widget, *args):
        self.logger.debug("on_button_dice_clicked called with self.%s" % widget.get_name())
        self.dicecounter += 1
        # The core checks that we never have a counter larger then available images 
        self.dicecounter = self._parent.core_dice_button_pressed(self.dicecounter)
        self.next_dice(self.dicecounter) 
        return True

    def hide_activity_buttons(self):
        """Hides buttons related to activities as set_sensitive doesn't work properly"""
        self.dicebut.hide()
        self.graphbut.hide()
        self.quitbut.hide()
    def show_activity_buttons(self):
        self.dicebut.show()
        self.graphbut.show()
        self.quitbut.show()

class SchoolsplayActivity(sgactivity.Activity):
    """The main SP core meant to be used in XO Sugar.
        This will also setup the GTK GUI.
        """
    def __init__(self,handle,resolution=(800,600),options=CMD_Options,\
                    language=('en',False)):
        
        sgactivity.Activity.__init__(self, handle)
        self.logger = logging.getLogger("schoolsplay.SchoolsplayActivity.MainCoreGui")
        self.logger.debug("Start")
        self.cmd_options = options
        if self.cmd_options.no_sound:
            self.logger.info("Disabling sound support as requested by user(Not yet supported)")
            
        self.resolution = resolution# not used yet
        # Thread lock, must be used by activities to be able to block evrything.
        self.lock = threading.Lock() 
        
        # Now 'self' has become our starting point to which we attach children.
        # We use windows as containers to hold our glade stuff so we must detach
        # all children from the parent window and then reparent them to the 
        # Sugar toplevel window.
        #
        #------------ start login screen
        # We always start with the login as we are a multi user app.
        # This blocks until the user logs in. When the user hits cancel we never
        # return here.
        # setup SPGoodies which we pass to the activities and the datamanager
        # topbar is set to None, because we don't have it yet and the menu doesn't use it.
        self.spgoodies = SPGoodies(self,\
                                    language,\
                                    self.lock,\
                                    None,\
                                    self.activity_level_end,\
                                    self.activity_game_end)
        # If developing new activities we can use another menu
        if self.cmd_options.develop_menu:
            self.spgoodies._menupath = self.cmd_options.develop_menu
        else:
            self.spgoodies._menupath = 'SP_menu.xml'
        self.spgoodies._theme = self.cmd_options.theme
        self.spgoodies._menu_activity_userchoice = self._menu_activity_userchoice
        self.spgoodies._cmd_options = self.cmd_options
        
        # Get a datamanager which will also handle the login screen
        # CURRENTLY DISABLED IN SPgdm.py, don't start login dlg and will always
        # return the string sugar.profile.get_nick_name() ,eg the users name 
        try:
            self.dm = SPDataManager.DataManager(self.spgoodies)
        except sqla_exceptions.SQLError:
            self.logger.exception("Error while handeling the dbase, try removing the existing dbase")
        #
        # if we get here the user has provided a valid name+pass, or anonymous,
        # and we move on.
        #
        #--------------- setup main GUI screen
        # remove any children of the window that the login stuff may have added
##        for child in self.parentGUI.get_children():
##            self.parentGUI.remove(child)

        # self.GUIMainWindow will hold the GUI object build from glade
        # The GUI will call methods from this class to handle button events. 
        self.GUIMainWindow = sp_cr.MainWindow(self)
        
        # Now we repack the two main alignments and buttons that we gonna use.
        # We do this because the Sugar env set things up differently and instead
        # of our own bottom menu bar we use on sugar the sugar toolbox to hold
        # the buttons.
        toolbox = sgactivity.ActivityToolbox(self)
        # TODO: add our own buttons
        self.activity_tb = SPToolbar(self)
        toolbox.add_toolbar("Schoolsplay",self.activity_tb)
        self.set_toolbox(toolbox)
        self.activity_tb.show()
        toolbox.show()
        # and references to some of the buttons we want to control
        self.dicebut = self.activity_tb.dicebut
        self.graphbut = self.activity_tb.graphbut
        
        # test code
        toolbox.connect('destroy',self.__test)
        
        # This is the top alignment used to display the main menu and activity bar
        self.topframe = self.GUIMainWindow.frame5
        self.GUIMainWindow.vbox3.remove(self.topframe)
        # This is the middle part where the activities are shown.
        self.mainframe = self.GUIMainWindow.frame9
        self.GUIMainWindow.vbox3.remove(self.mainframe)
        # setup our own frame to hold the alignments
        frame = gtk.Frame()
        spVbox = gtk.VBox(homogeneous=False, spacing=0)
        spVbox.pack_start(self.topframe, expand=False, fill=False, padding=0)
        spVbox.pack_start(self.mainframe, expand=True, fill=True, padding=0)
        frame.add(spVbox)
        frame.show_all()
        # set it as the 'canvas' which will fill the space below the toolbox 
        self.set_canvas(frame)
        
        # get references to the various widgets.
        self.currentuser_label = self.GUIMainWindow.label27
        self.currentactivity_label = self.GUIMainWindow.label28
        self.mainalignment = self.GUIMainWindow.alignment13
        self.topalignment = self.GUIMainWindow.alignment5
        
        # set users name, or None
        self.currentuser_label.set_text(self.dm.get_username()) 
        
        # setup the frame used by activities.
        self.activityframe = gtk.Frame()
        self.activityframe.set_shadow_type(gtk.SHADOW_NONE)
        self.mainalignment.add(self.activityframe)
        
        # We also replace the parent attribute from SPGoodies as the activities
        # use the frame as their "main screen"
        self.spgoodies.parent = self.activityframe
        # we also put a reference to the top frame alignment which is used by the menu to
        # display it's submenu buttons. We don't have an abstraction method in
        # spgoodies as we don't want regular activities use it.
        self.spgoodies._topframe_alignment = self.topalignment
        
        # Start the menu
        self.spactivity = SPMenu.Activity(self.spgoodies)
        self.currentactivity_label.set_text(self.spactivity.get_helptitle())
        # keep a reference to the menu activity
        self.menu_saved = self.spactivity
        
        # get the rest of our widgets, it will be packed by the add_topbarcontainer
        # method which is called when a activity is loaded succesfully.
        
        tbc = sp_cr.TopbarContainer(self)
        tbc.topbarcontainer.remove(tbc.mainframe)
        self.topbar = tbc.mainframe
        self.topbar.show()
        
        # Now we can also set the topbar reference
        self.spgoodies.topbar = tbc
        
        
    ############################################################################
    ## Methods for internal use 
    
    # testing 
    def __test(self,*args):
        self.logger.debug("__test called with: %s" % args)
    
    def add_topbarcontainer(self):
        # first make sure the menu doesn't use the parent.
        self.menu_saved._detach()
        self.topalignment.add(self.topbar)
        self.topalignment.show_all()
        
    def clear_screen(self):
        """Remove activity stuff"""
        # TODO: remove activity and start menu 
        self.dicebut.set_sensitive(False)
        # remove all children that the activity has added from the activityframe.
        for child in self.activityframe.get_children():
            self.activityframe.remove(child)
        # remove and reset the top buttonbar
        self.spgoodies.topbar._reset_observers()
        for child in self.topalignment.get_children():
            self.topalignment.remove(child)
    
    def load_activity(self,name):
        # This will replace self.spactivity with the choosen activity
        self.logger.debug("load_activity called with %s" % name)
        try:
            self.activity_module = utils.import_module(os.path.join('lib',name))
            # remove menu from frames
            self.menu_saved._detach()
            self.spactivity = self.activity_module.Activity(self.spgoodies)
        except utils.MyError,info:
            self.logger.exception("Error constructing activity: %s" % info)
            self.spactivity = self.menu_saved
            # TODO: add some dialog to mention the activity screws up, also after StandardError
            self.clear_screen()
            self.start_main_loop()
        except StandardError,info:
            self.logger.exception("Error constructing activity: %s" % info)
            self.spactivity = self.menu_saved
            self.clear_screen()
            self.start_main_loop()
        else:
            self.logger.debug("Loaded activity succesfull")
            self.currentactivity_label.set_text(self.spactivity.get_helptitle())
            # add the topbar to the top frame.
            self.add_topbarcontainer()
            self.start_main_loop()           

    def display_levelstart(self,level):
        """Displays a 'ready 3-2-1' screen prior to starting the level.
        It also displays a blocking 'Start' button."""
        self.logger.debug("Starting display_levelstart")
##        txt = _("Starting level %s" % level)
##        txt_s = utils.char2surf(txt,64, fcol=YELLOW, ttf=TTF)  
##        org_screen = pygame.display.get_surface().convert()
##        org_backgr = self.backgr.convert()
##        # disable the dice to prevent users clicking it
##        self.dicebut.enable(False)
##        for value in range(1,36):
##            dark = pygame.Surface(self.screen.get_size(), 32)
##            dark.set_alpha(5,0)
##            self.screen.blit(dark,(0, 0))
##            pygame.display.update()
##            pygame.time.wait(20)
##        # we have a animated sprite so we need to adjust the backgr screen
##        self.backgr.blit(self.screen,(0,0))
##        self.screen.blit(txt_s,((760-txt_s.get_width())/2,100))
##        pygame.display.update()
##        # we re-init the sprite stuff as we use a different background 
##        SPInit(self.screen,self.backgr)       
##        for i in (3,2,1):
##            num_s = utils.char2surf(str(i),64, fcol=RED, ttf=TTF)
##            spr = MySprite(num_s)
##            spr.display_sprite((350,200))
##            pygame.time.wait(1000)
##            spr.erase_sprite()
##        # restore the screens
##        self.screen.blit(org_screen,(0,0))
##        self.backgr.blit(org_backgr,(0,0))
##        # reset the screens in SPGoodies so that any activities gets a proper screen.
##        SPInit(self.screen,self.backgr) 
##        pygame.display.update()
        # and enable the activity_tb buttons
        self.activity_tb.show_activity_buttons()
        
    #### TODO: refactor this for GTK
    def ask_exit(self):
        # we must use a new renderer so that we leave the screen intact that
        # is used by the pygame sprite classes.
        re = ocw.Renderer()
        re.set_screen(self.screen)
        dlg = ExitDialog(re)
        c = dlg.run()
        if c == 0:
            self.logger.info("User wants exit")
            try:
                self.usernamelabel.set_text('None')
                self.currentactivity_label.set_text('None')
                self.activity_tb.hide_activity_buttons()
            except:
                pass
            if self.spactivity.get_name() != 'menu':
                try:
                    self.activity_game_end()
                except:
                    pass
            # any cleanup is done by atexit functions
            # except this one :-)
            self.dm._cleanup()
            # TODO: add a "shutting down...." screen because sometimes we must wait until timers are stopped
            raise MainEscapeKeyException # let schoolsplay.py decide what next
            
    ###########################################################################
    # Main menubar button callbacks. Passed to SPCoreButtons.MainCoreButtons
    # These are called when the user hits the buttons in the lower menu bar of 
    # screen.
    def core_info_button_pressed(self,*args):
        self.logger.debug("core_info_button_pressed called with")
        text = self.spactivity.get_help()
        if not text:
            text = "No help available"
        SPWidgets.InfoDialog('\n'.join(text))
        
    def core_quit_button_pressed(self,*args):
        self.logger.debug("core_quit_button_pressed")
        if self.spactivity.get_name() == 'menu':
            dlg = sp_cr.QuitDialog()
            if dlg.run() == -5:
                # This doesn't work as GTK catch all exceptions, this sucks!
                raise MainEscapeKeyException
            return
        else:
            self.activity_game_end()
    
    def core_dice_button_pressed(self,count,*args):
        self.logger.debug("core_dice_button_pressed with: %s" % count)
        if count == 7:
            self.activity_game_end()
            return 1
        else:
            self.activity_level_end()
        return count
    
    def core_graph_button_pressed(self,*args):
        self.logger.debug("core_graph_button_pressed")
        # get data, user AND level
        query = self.mapper._get_level_data(levelnum=self.levelcount)
        # get the score and date data from the objects
        scorelist = filter(None,[(getattr(item,'start_time'),getattr(item,'score')) for item in query])
        self.logger.debug("scorelist from SQL query: %s" % scorelist)
        # get the mu and sigma for this activity.
        norm = self.dm.get_mu_sigma(self.spactivity.get_name())
        # turn the data into a graph blitted on a SDL surface
        htext = 'Generated by Schoolsplay %s for the %s activity' % (Version.version,self.spactivity.get_name())
        # This is a blocking dialog
        s = SPWidgets.GraphDialog(data=scorelist,norm=norm,header=htext)
        
    #############################################################################
    # SPGoodies callbacks that are passed to the activity and are used as observers
    # by the maincore. The activity calls one of these callbacks from within the
    # activity_loop. This means that when we don't set the
    # run_*_loop to False we will return back to the activity_loop.
    # The whole communication between the core and the activity is based on the
    # observer pattern. The dbase mapper object is not part of SPGoodies but is passed
    # in the activity.start method.
    def activity_level_end(self,store_db=None):
        """Use this to notify the core that the level is ended.
        The core will call next_level on the activity.
        @store is used by the activity to signal a normal level end."""
        self.logger.debug("activity_level_end called")
        if store_db:
            self.mapper.insert('end_time',utils.current_time())
            # calculate the time spend inside the level and store it
            stime = utils.calculate_time(self.mapper._get_start_time(),\
                                        self.mapper._get_end_time())
            self.mapper.insert('timespend',stime)
            # get the score value, if any and insert it into the dbase
            self.mapper.insert('score',self.spactivity.get_score(stime))
            # You MUST call commit to write the contents of the mapper to disk.
            self.mapper.commit()
        # we try to stop any timers just in case
        try:
            self.spactivity.stop_timer()
        except:
            pass
        self.start_activity_loop()
        
    def activity_game_end(self,store_db=None):
        """Use this to notify the core that the game is ended.
        The core will start the menu and delete the activity.
        @store is used by the activity to signal a normal level end."""
        self.logger.debug("activity_game_end called")
        self.activity_tb.hide_activity_buttons()
        try:
            self.spactivity.stop_timer()
        except:
            pass
        # remove activity from the frame
        self.clear_screen()
        # datacollecting
        if not self.spactivity.get_name() == 'menu' and store_db:
            self.mapper.commit()# write to any sql stuff to disk
        # check if we are the menu, if so we in deep shit and theres a big problem
        # in the menu
        if self.spactivity and self.spactivity.get_name() == 'menu':
            self.logger.critical("I'm the menu, I shouldn't be here, bail out")
            self.logger.exception("Check the logs, there's a critical problem in the menu")
            sys.exit(1)
        # Start menu again
        self.logger.debug("Start menu again")
        try:
            self.spactivity = self.menu_saved
        except Exception,info:
            self.logger.error("Failed to restore menu: %s" % info)
            self.spactivity = SPMenu.Activity(self.spgoodies)
            self.spactivity.start()
        self.spactivity._detach()# make sure the menu was detached from the frames
        self.currentactivity_label.set_text('Menu')
        self.start_main_loop()
        
    # Added to the spgoodies for the menu activity
    def _menu_activity_userchoice(self,activity):
        self.logger.debug("menu_activity_userchoice called with %s" % activity)
        self.menu_saved = self.spactivity
        self.load_activity(activity)
    
    ############################################################################
    # Here we start the show. This will first call activity.start.
    # The activities eventloop is the GTK mainloop, as the activity uses GTK events.
    # This is fundamentally different from the pygame schoolsplay.
    #
    # The way to get out of the activity is when the user hits the escape
    # key which is cached.
    # We will then ask to really quit or not, the hitting of the quit button
    # works the same as the escape key.
    #
    # The other way to get out of the activity is when the activity level is ended
    # then the activity calls the callback: activity_level_end (see above)
    # The activity is passed a class object called SPGoodies which holds a number
    # of 'observer' methods which calls methods in the core. So when we talk about
    # the activity that calls callbacks, we mean SPGoodies observers.
    # This callback will determine what's next, but in fact were now out of the
    # activity mainloop. If there are more levels the activity_level_end method
    # will call the start_activity_loop again. 
    #
    # Finally we can break out when the activity is ended because all levels are done.
    # Then the activity will call the callback: activity_game_end (see above)
    # This callback will call activity.cleanup() to force any cleanup by the activity
    # and delete the activity. Then it will restart the menu and call the start_main_loop
    # which will run the menu again.
    #
    # In short:
    # The menu is constructed.
    # Menu is started when it is shown.
    # Then the menu will call SPGoodies.menu_activity_userchoice which will end
    # the menu and start the choosen activity.
    # Then the start_main_loop is called by menu_activity_userchoice and the 
    # activity is started and the activity_loop is called. This will loop until
    # the activity calls aone of the SPGoodies callbacks which will jump out the loop
    # and determine what's next. 
    def start_main_loop(self):
        self.levelcount = 0
        try:
            self.logger.debug("Call activity start")
            self.spactivity.start()
        except utils.MyError,info:
            # trouble in paradise
            self.logger.error("start_main_loop: MyError, %s" % info)
            # this way we don't crash but return to the menu
            self.activity_game_end()
        except StandardError,info:
            # even more trouble in paradise
            self.logger.exception("start_main_loop: StandardError, %s" % info)
            self.activity_game_end()
        else:
            self.start_activity_loop()
    
    def start_activity_loop(self):
        # start stepping throught the activity levels
        try:
            self.logger.debug("Call start_next_level")
            self.start_next_level(store_db=True)
        except utils.MyError,info:
            self.logger.error("Error in start_activity_loop:%s" % info)
            self.run_event_loop = False
            self.run_activity_loop = False
            self.activity_game_end()

    def start_next_level(self,store_db=None):
        """store_db is used to signal normal ending and that we should store the data"""
        if self.levelcount == 6:
            self.logger.debug("No more levels left")
            self.activity_game_end()
        self.levelcount += 1
        self.logger.debug("Calling activity next_level")
        if self.spactivity.get_name() == 'menu':
            if self.levelcount == 2:
                print "menu level is 2, start a traceback"
                foobar
            try:
                self.spactivity.next_level(self.levelcount,None)                    
            except StandardError,info:
                self.logger.exception("Error in %s next_level" % self.spactivity.get_name())
                raise utils.MyError,info
        else: 
            # Here we fetch our data colletor object, we collect data per level,
            # so it's the best place to start datacollecting
            # get_mapper returns always an object, in case of anonymous mode the 
            # object is a fake.
            self.mapper = self.dm.get_mapper(self.spactivity.get_name())
            self.mapper.insert('level',self.levelcount)
            self.mapper.insert('start_time',utils.current_time())
            try:
                # we pass the db mapper so that the activity can store it's data
                if not self.spactivity.next_level(self.levelcount,self.mapper):
                    self.logger.debug("start_activity_loop: Levels ended")
                    self.activity_game_end()
                else:
                    # We (TODO?) display a blocking ready-start screen
                    self.display_levelstart(self.levelcount)
                    # and call the post_next_level
                    self.spactivity.post_next_level()
                    # and set the dice and enable it
                    self.GUIMainWindow.next_dice(self.levelcount)
            except StandardError,info:
                self.logger.exception("Error in %s next_level" % self.spactivity.get_name())
                raise utils.MyError,info
        
        
if __name__ == '__main__':
    utils.set_locale()# TODO: add lang argument
    try:
        mcgui = MainCoreGui((800,600))
    except SystemExit,status:
        if str(status) == '0':
            module_logger.info("clean exit")
        else:
            module_logger.info("not a clean exit")
    except Exception,status:        
        module_logger.exception("unhandled exception in toplevel, traceback follows:")
            
