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

import sys

# needed to let activities import stuff from there own directory.
# SPMainCore uses the import_module to import activities so if activities
# want to import stuff from their cwd it would fail.
sys.path.append('lib')

# first parse commandline options
from SPOptionParser import OParser
# if this doesn't bail out the options are correct and we continue with schoolsplay
op = OParser()
# this will return a class object with the options as attributes 
# OLPC: set default options in the OParser class as we don't have cmd line options
CMD_Options = op.get_options()

try:
    from sugar.activity import activity as sgactivity
except ImportError:
    # only to prevent error messages
    import fake_sugar_activity as sgactivity

import utils
# this will return the tuple (lang,rtl=bool)
LANG = utils.set_locale(lang=CMD_Options.lang)   

import os,atexit,types,time,threading
import gtk
##import pygame
### Do we need to init all? We only use sound and music play.
##pygame.init()
##from pygame.constants import *
#### set a bigger buffer, seems that on win XP in conjuction with certain hardware
#### the playback of sound is scrambled with the "normal" 1024 buffer.
#####  XXXX this still sucks, signed or unsigned that's the question :-(
##pygame.mixer.pre_init(22050, -16, 2 , 2048)

#create logger, logger was configured by Sugar, or by SPLogging (see above)
import logging
module_logger = logging.getLogger("schoolsplay.SPMainCore")

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

class MainCoreGui:
    def __init__(self,parent,options=None,language=('en',False),observer=None):
        """The main SP core.
        This will also setup the GTK GUI.
        The idea is that we have a menubar at the botttom and a activity area
        just like in CP. 
        """
        self.parent = parent
        self.main_observer = observer
        self.logger = logging.getLogger("schoolsplay.SPMainCore.MainCoreGui")
        self.logger.debug("Start")
        self.cmd_options = options
        if self.cmd_options.no_sound:
            self.logger.info("Disabling sound support as requested by user")
            pygame.mixer.quit()
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
                                    self.activity_restart_level,\
                                    self.activity_game_end,\
                                    self.main_observer.stop_gui,\
                                    self.cmd_options)
        # If developing new activities we can use another menu
        if self.cmd_options.develop_menu:
            self.spgoodies._menupath = self.cmd_options.develop_menu
        else:
            self.spgoodies._menupath = 'SP_menu.xml'
        self.spgoodies._theme = self.cmd_options.theme
        self.spgoodies._menu_activity_userchoice = self._menu_activity_userchoice
        self.spgoodies._cmd_options = self.cmd_options
        
        # Get a datamanager which will also handle the login screen
        try:
            self.dm = SPDataManager.DataManager(self.spgoodies)
        except sqla_exceptions.SQLError:
            self.logger.exception("Error while handeling the dbase, try removing the existing dbase")
        #
        # if we get here the user has provided a valid name+pass, or anonymous,
        # and we move on.
        #
        #--------------- setup main GUI screen
        # self.GUI will hold the GUI object build from glade
        # The GUI will call methods from this class to handle button events. 
        self.GUI = sp_cr.MainWindow(self)
        self.GUI.mainwindow.set_size_request(800,600)
        # get references to the various widgets.
        self.currentuser_label = self.GUI.label27
        self.currentactivity_label = self.GUI.label28
        self.topalignment = self.GUI.alignment5
        self.mainalignment = self.GUI.alignment13
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
        self.activity = SPMenu.Activity(self.spgoodies)
        self.currentactivity_label.set_text(self.activity.get_helptitle())
        # keep a reference to the menu activity
        self.menu_saved = self.activity
        
        # get the rest of our widgets
        tbc = sp_cr.TopbarContainer(self)
        tbc.topbarcontainer.remove(tbc.mainframe)
        self.topbar = tbc.mainframe
        self.topbar.show()
        # Now we can also set the topbar reference
        self.spgoodies.topbar = tbc
##        self.logger.debug("BREAKPOINT0")
##        sys.exit(0)
        # and references to some of the buttons we want to control
        self.dicebut = self.GUI.dicebutton
        self.graphbut = self.GUI.graphbutton
        # show all the stuff
        self.GUI.mainwindow.show_all()
        
    ## called by schoolsplay.py to start the gtk mainloop
    def start(self):
        self.logger.debug("starting gtk eventloop")
        self.GUI.run()
    def stop(self):
        self.logger.debug("stopping gtk eventloop")
        self.GUI.quit()
        self.GUI.mainwindow.destroy()
    ############################################################################
    ## Methods for internal use 
    def add_topbarcontainer(self):
        # first make sure the menu doesn't use the parent.
        self.menu_saved._detach()
        self.topalignment.add(self.topbar)
        self.topalignment.show_all()
        
    def clear_screen(self):
        """Remove activity stuff"""
        self.logger.debug("clear_screen called")
        # TODO: remove activity and start menu 
        self.dicebut.set_sensitive(False)
        self.graphbut.set_sensitive(False)
        # remove all children that the activity has added from the activityframe.
        for child in self.activityframe.get_children():
            self.activityframe.remove(child)
        # remove and reset the top buttonbar
        self.spgoodies.topbar._reset_observers()
        for child in self.topalignment.get_children():
            self.topalignment.remove(child)
    
    def load_activity(self,name):
        # This will replace self.activity with the choosen activity
        self.logger.debug("load_activity called with %s" % name)
        try:
            self.activity_module = utils.import_module(os.path.join('lib',name))
            # remove menu from frames
            self.menu_saved._detach()
            self.activity = self.activity_module.Activity(self.spgoodies)
        except utils.MyError,info:
            self.logger.exception("Error constructing activity: %s" % info)
            self.activity = self.menu_saved
            # TODO: add some dialog to mention the activity screws up, also after StandardError
            self.clear_screen()
            self.start_main_loop()
        except StandardError,info:
            self.logger.exception("Error constructing activity: %s" % info)
            self.activity = self.menu_saved
            self.clear_screen()
            self.start_main_loop()
        else:
            self.logger.debug("Loaded activity succesfull")
            self.currentactivity_label.set_text(self.activity.get_helptitle())
            # add the topbar to the top frame.
            self.add_topbarcontainer()
            self.start_main_loop()           

    def display_levelstart(self,level):
        """Displays a 'ready 3-2-1' screen prior to starting the level.
        It also displays a blocking 'Start' button.
        TODO"""
        self.logger.debug("Starting display_levelstart")

        # and enable the dice again
        self.dicebut.set_sensitive(True)
        # and the graphbutton if we not running in anonymous mode
        self.graphbut.set_sensitive(not self.dm.are_we_anonymous())
        
    ###########################################################################
    # Main menubar button callbacks. Passed to SPCoreButtons.MainCoreButtons
    # These are called when the user hits the buttons in the lower menu bar of 
    # screen.
    def core_info_button_pressed(self):
        self.logger.debug("core_info_button_pressed called with")
        text = self.activity.get_help()
        if not text:
            text = "No help available"
        SPWidgets.InfoDialog('\n'.join(text))
        
    def core_quit_button_pressed(self):
        self.logger.debug("core_quit_button_pressed")
        if self.activity.get_name() == 'menu':
            dlg = sp_cr.QuitDialog()
            if dlg.run() == -5:
                # This differs from childsplay as GTK catch all exceptions.
                if self.cmd_options.bundle_id:
                    # we are on XO
                    self.main_observer.stop_gui()
                else:
                    self.main_observer.restart_gui()# will restart the login on non-xo
                
            return
        else:
            self.activity_game_end()
    
    def core_dice_button_pressed(self,count):
        self.logger.debug("core_dice_button_pressed with: %s" % count)
        if count == 5:
            txt = _("Activities have four levels.")
            SPWidgets.InfoDialog(txt)
            #self.activity_game_end()
            return 4
        else:
            self.activity_level_end()
        return count
    
    def core_graph_button_pressed(self):
        self.logger.debug("core_graph_button_pressed")
        # get data, user AND level
        query = self.mapper._get_level_data(levelnum=self.levelcount)
        # get the score and date data from the objects
        scorelist = filter(None,[(getattr(item,'start_time'),getattr(item,'score')) for item in query])
        self.logger.debug("scorelist from SQL query: %s" % scorelist)
        # get the mu and sigma for this activity.
        norm = self.dm.get_mu_sigma(self.activity.get_name())
        # turn the data into a graph blitted on a SDL surface
        htext = 'Generated by Schoolsplay %s for the %s activity' % (Version.version,self.activity.get_name())
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
        """Used by SPGoodies to notify the core that the level is ended.
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
            score = self.activity.get_score(stime)
            self.logger.debug("Score stored: %s" % score)
            self.mapper.insert('score',score)
            # You MUST call commit to write the contents of the mapper to disk.
            self.mapper.commit()
        # we try to stop any timers just in case
        try:
            self.activity.stop_timer()
        except:
            pass
        self.start_activity_loop()
    
    def activity_restart_level(self,store_db=None):
        """Used by SPGoodies to notify the core that the current level needs
        to be restarted."""
        self.logger.debug("activity_restart_level called")
        self.restart_level(store_db)

    def activity_game_end(self,store_db=None):
        """Used by SPGoodies to notify the core that the game is ended.
        The core will start the menu and delete the activity.
        @store is used by the activity to signal a normal level end."""
        self.logger.debug("activity_game_end called")
        try:
            # In case the activity uses SPTimer objects it must provide a method
            # to stop them called 'stop_timer'. 
            self.activity.stop_timer()
        except:
            pass
        # remove activity from the frame and disable buttons 
        self.clear_screen()
        # datacollecting
        if not self.activity.get_name() == 'menu' and store_db:
            self.mapper.commit()# write to any sql stuff to disk
        # check if we are the menu, if so we in deep shit and theres a big problem
        # in the menu
        if self.activity and self.activity.get_name() == 'menu':
            self.logger.critical("I'm the menu, I shouldn't be here, bail out")
            self.logger.exception("Check the logs, there's a critical problem in the menu")
            sys.exit(1)
        # Start menu again
        self.logger.debug("Start menu again")
        try:
            self.activity = self.menu_saved
        except Exception,info:
            self.logger.error("Failed to restore menu: %s. \nTrying to restart menu." % info)
            self.activity = SPMenu.Activity(self.spgoodies)
            self.activity.start()
        self.activity._detach()# make sure the menu was detached from the frames
        self.currentactivity_label.set_text('Menu')
        self.start_main_loop()
            
    # Added to the spgoodies for the menu activity
    def _menu_activity_userchoice(self,activity):
        self.logger.debug("menu_activity_userchoice called with %s" % activity)
        self.menu_saved = self.activity
        self.load_activity(activity)
    
    ############################################################################
    # Here we start the show. This will first call activity.start.
    # The activities eventloop is the GTK mainloop, as the activity uses GTK events.
    # This is fundamentally different from childsplay.
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
    # the activity calls one of the SPGoodies callbacks which will jump out the loop
    # and determine what's next. 
    def start_main_loop(self):
        self.levelcount = 0
        try:
            self.logger.debug("Call activity start")
            self.activity.start()
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

    def restart_level(self,store_db=None):
        """Used by activities to restart the level in case the numbersrange
        is changed by the user.
        This method is called through a SPGoodies callback."""
        if self.levelcount > 0:
            self.levelcount -= 1
            self.logger.debug("restarting level %s" % self.levelcount)
            self.start_next_level(store_db)
        else:
            self.logger.error("Can't restart level 0")
            return
        
    def start_next_level(self,store_db=None):
        """store_db is used to signal normal ending and that we should store the data"""
        if self.levelcount == 4:
            self.logger.debug("No more levels left")
            self.activity_game_end()
        self.levelcount += 1
        self.logger.debug("Calling activity next_level")
        if self.activity.get_name() == 'menu':
##            if self.levelcount == 2:
##                print "menu level is 2, start a traceback"
##                foobar
            try:
                self.activity.next_level(self.levelcount,None)                    
            except StandardError,info:
                self.logger.exception("Error in %s next_level" % self.activity.get_name())
                raise utils.MyError,info
        else: 
            # Here we fetch our data colletor object, we collect data per level,
            # so it's the best place to start datacollecting
            # get_mapper returns always an object, in case of anonymous mode the 
            # object is a fake.
            self.mapper = self.dm.get_mapper(self.activity.get_name())
            self.mapper.insert('level',self.levelcount)
            self.mapper.insert('start_time',utils.current_time())
            try:
                # we pass the db mapper so that the activity can store it's data
                if not self.activity.next_level(self.levelcount,self.mapper):
                    self.logger.debug("start_activity_loop: Levels ended")
                    self.activity_game_end()
                else:
                    # We (TODO?) display a blocking ready-start screen
                    self.display_levelstart(self.levelcount)
                    # and call the post_next_level
                    self.activity.post_next_level()
                    # and set the dice and enable it
                    self.GUI.next_dice(self.levelcount)
            except StandardError,info:
                self.logger.exception("Error in %s next_level" % self.activity.get_name())
                raise utils.MyError,info
        

class MainCoreGuiXO(MainCoreGui):
    def __init__(self,parent,options=None,language=('en',False),observer=None):
        """The main SP core.
        This will also setup the GTK GUI.
        The idea is that we have a menubar at the botttom and a activity area
        just like in CP. 
        """
        MainCoreGui.__init__(self,parent,options=options,language=language,observer=observer)
        self.logger = logging.getLogger("schoolsplay.SPMainCore.MainCoreGuiXO")
        self.logger.debug("Start")
        self._parent = parent
        # Get and set the sugar toolbar
        self.toolbox = sgactivity.ActivityToolbox(self._parent)
        self._parent.set_toolbox(self.toolbox)
        self.toolbox.show()
        # self.GUI will hold the GUI object build from glade
        # The GUI will call methods from this class to handle button events. 
        #self.GUI = sp_cr.MainWindow(self)
        # add main frame to new parent
        self.frame = self.GUI.main_frame
        self.GUI.mainwindow.remove(self.frame)
        self._parent.set_canvas(self.frame)
        
        self.frame.show_all()
        
    def start(self):
        """Override the start method as Sugar controls the eventloop"""
        self.logger.debug("Sugar will start gtk eventloop")
    def stop(self):
        """Override the stop method because on Sugar we call the callback
        fuction from the toolbars stop button to make sure we stop properly"""
        self.logger.debug("Calling same methods as the toolbar stop button callback")
        toolbar = self.toolbox.get_activity_toolbar()
        toolbar._activity.take_screenshot() 
        toolbar._activity.close() 
        
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
            
