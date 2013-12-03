# -*- coding: utf-8 -*-

# Copyright (c) 2006-2008 Stas Zykiewicz <stas.zytkiewicz@schoolsplay.org>
#
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

# Schooldsplay goodies
# SPGoodies is a class that is passed on to the activity constructor
# It contains references to useful stuff, callback functions from the core
# and observers from the core.
import SPConstants
import logging
import os
from BorgSingleton import Borg
import utils

class SPGoodies(Borg):
    """This class is a singleton because we want that the core and
    activity always uses the same object"""
    def __init__(self, core, screen, virtkb, lang, lock,cb_pre_level_end, \
        cb_level_end, cb_game_end, cb_info_dialog, \
        cb_display_execounter, cb_set_framerate, \
        cb_enable_dice,cb_dice_minimal_level,\
        theme_rc, theme, cb_disable_menubuttons, cb_enable_menubuttons, \
        cb_disable_level_indicator,cb_enable_level_indicator, \
            cb_disable_exit_button, cb_enable_exit_button, \
            cb_disable_score_button, cb_enable_score_button, 
            cb_hide_level_indicator, cb_show_level_indicator, \
            cb_get_orm, cb_register_core_observers):
        Borg.__init__(self)
        # references to stuff, use the methods to get them
        self.logger = logging.getLogger("childsplay.SPGoodies")
        self.screen = screen
        self.virtkb = virtkb
        self.pre_level_end = cb_pre_level_end
        self.level_end = cb_level_end
        self.game_end = cb_game_end
        if lang:
            if '.' in lang[0] and len(lang[0]) > 4:
                lang = (lang[0][:5], lang[1])
        else:
            lang = ('en_US.utf8', False)
        self.localesetting = lang
        self.lock = lock
        self.info_dialog = cb_info_dialog
        self.display_execounter = cb_display_execounter
        self.set_framerate = cb_set_framerate
        self.enable_dice = cb_enable_dice
        self.set_dice_minimal_level = cb_dice_minimal_level
        self.theme_rc = theme_rc
        self.theme = theme
        self.disable_menubuttons = cb_disable_menubuttons
        self.enable_menubuttons = cb_enable_menubuttons
        self.disable_level_indicator = cb_disable_level_indicator
        self.enable_level_indicator = cb_enable_level_indicator
        self.disable_exit_button = cb_disable_exit_button
        self.enable_exit_button = cb_enable_exit_button
        self.disable_score_button = cb_disable_score_button
        self.enable_score_button = cb_enable_score_button
        self.hide_level_indicator = cb_hide_level_indicator
        self.show_level_indicator = cb_show_level_indicator
        self.register_core_observer = cb_register_core_observers
        self._get_orm = cb_get_orm
        self.core = core
                
    # these methods are the observers that an activity can use to signal the core
    def tellcore_pre_level_end(self):
        """Use this to notify the core that the pre_level is ended.
        The core will call next_level on the activity."""
        apply(self.pre_level_end)
    def tellcore_level_end(self, store_db=None, level=1, levelup=False, no_question=False):
        """Use this to notify the core that the level is ended.
        The core will call next_level on the activity."""
        apply(self.level_end, (store_db, level, levelup, no_question))
    def tellcore_game_end(self, store_db=None):
        """Use this to notify the core that the game is ended.
        The core will start the menu and delete the activity."""
        raise utils.StopGameException, store_db
    def tellcore_info_dialog(self, text):
        """Use this to ask the core to display a info dialog with the text @text"""
        apply(self.info_dialog, (text, ))
    def tellcore_display_execounter(self, total, text=''):
        """Use this to display a exeCounter object in the menu bar. @total must
        be an integer indicating the total numebr of exercises."""
        return apply(self.display_execounter, (total, ))
    def tellcore_set_framerate(self, rate):
        """Use this to lower the framerate at which the loop runs.
        The maximum is 30 per minute to prevent running the CPU at 100%.
        The core resets the rate to 30 when loading a activity so you should call
        this in 'start' or 'next_level'.
        WARNING: only use this is you know why you want to use it.
        """
        apply(self.set_framerate, (rate, ))
    def tellcore_enable_dice(self, enable=True):
        """Use this to enable or disable the dice button.
        @enable is a bool, False to disable the dice, True to enable it.
        Defaults to True.
        """
        if enable:
            self.enable_level_indicator()
        else:
            self.disable_level_indicator()
    def tellcore_set_dice_minimal_level(self, level):
        """Use this to set the level indicator to a minimal level.
        The value must be the maximum number of levels minus one.
        You must call this in your start method otherwise the core will reset
        it to 1"""
        apply(self.set_dice_minimal_level, (level,))
    def tellcore_disable_menubuttons(self):
        """Use this to ask the core to disable it's menu buttons.
        This is needed when the activity wants to cover the menubar.
        Be aware that the activity must provide a bullet proof way for the user
        to quit the activity."""
        apply(self.disable_menubuttons)
    def tellcore_enable_menubuttons(self):
        """Use this to ask the core to enable it's menu buttons.
        This makes only sense if you have disabled them before."""
        apply(self.enable_menubuttons)
    def tellcore_disable_level_indicator(self):
        apply(self.disable_level_indicator)
    def tellcore_enable_level_indicator(self):
        apply(self.enable_level_indicator)
    def tellcore_disable_exit_button(self):
        apply(self.disable_exit_button)
    def tellcore_enable_exit_button(self):
        apply(self.enable_exit_button)
    def tellcore_disable_score_button(self):
        apply(self.disable_score_button)
    def tellcore_enable_score_button(self):
        apply(self.enable_score_button)    
    def tellcore_hide_level_indicator(self):
        apply(self.hide_level_indicator)
    def tellcore_show_level_indicator(self):
        apply(self.show_level_indicator)
        
    def tellcore_register_core_observer(self, obs):
        """You must register any observer methods that should be called in case of an error
        to clean up your mess. Your observer must be a method or funtion that takes no arguments.
        For example; the camera used by facerecognition is crappy and must be stopped manually"""
        apply(self.register_core_observer, (obs,))
    # these methods provide stuff needed by the activity.
    def get_screen(self):
        """get a references to the main SDL screen"""
        return self.screen
    def get_background(self):
        """get a references to the background surface"""
        return self.background
    def get_virtual_keyboard(self):
        """get a virtual keyboard object which is setup by the maincore.
        when we not in kioskmode this will return None so be sure to check
        the object returnt before trying to use it."""
        return apply(self.virtkb)
    def get_localesetting(self):
        """Returns the current locale as set by schoolsplay.
        The value is a tuple with the language code and a bool signaling if
        were in a RTL environment (Hebrew and Arabic)"""
        return self.localesetting
    def get_screenclip(self):
        """get a rect representing the area to be 'clipped'.
        This should be used to set a clip to the screen when your activity sets
        a background of it's own. You should set a screen clip to prevent
        your background from overlapping the SP background.
        The rect returnt is based on the current them used."""
        return self.screenrect
    def get_thread_lock(self):
        """Returns a reference to the thread lock setup by the core.
        This lock MUST be used when dealing with the timer object from
        the SP Timer module.
        """
        return self.lock
    def get_theme(self):
        """Returns the theme name or None for the default theme.
        """
        return self.theme
    def get_theme_rc(self):
        """Returns the dictionary with the contents of the theme.rc file"""
        return self.theme_rc
    def autolevelup(self):
        """Returns a boolean indicating if activities should do autolevelup"""
        return self.autolevelup
    def get_scoredisplay(self):
        """Returns a reference to the score display widget in the menubar."""
        return self.scoredisplay
    def get_infobutton(self):
        """Returns a reference to the infobutton widget in the menubar.
        Use this to place the button in your own eventloop if you want the functionality"""
        return self.infobutton
    def get_quitbutton(self):
        """Returns a reference to the quitbutton widget in the menubar.
        Use this to place the button in your own eventloop if you want the functionality"""
        return self.quitbutton
    def get_quitbutton_rect(self):
        """Returns the rect for the quit button which is located in the menubar.
        Use this if you activity starts it's own eventloop and you want to check
        if the user hits the menu exit button."""
        return self.quitbutton.get_button_rect()
    # dbase stuff
    def get_orm(self, tablename, dbase):
        """Returns a sqlalchemy ORM  for the table and a Session object which
        is connected to the proper engine.
        tablename must be a string with the name of the dbase table.
        dbase must be one of the strings, 'user' or 'content', indicating from 
        which dbase we want the table."""
        return self.dm.get_orm(tablename, dbase)
    def get_mapper(self, activity, dbase):
        return self.dm.get_mapper(activity, dbase)
    def get_current_user_id(self):
        return self.dm.get_user_id()
    def get_current_user_name(self):
        return self.dm.get_username()
    def get_user_id_by_loginname(self, username):
        return self.dm.get_user_id_by_loginname(username)
    def get_user_dbrow_by_loginname(self, username):
        return self.dm.get_user_dbrow_by_loginname(username)
    def get_current_user_dbrow(self):
        return self.get_user_dbrow_by_loginname(self.dm.current_user)
    def get_served_content_orm(self):
        return self.dm.get_served_content_orm()
    def get_served_content_mapper(self):
        return self.dm.get_served_content_mapper()
    def check_served_content(self, rows, game_theme, minimum=10, all_ids=None):
        return self.dm._check_already_served(rows, minimum, game_theme, all_ids)
    def get_table_data_userdb(self, table):
        return self.dm.get_table_data_userdb(table)
    def get_rckey(self, actname, key):
        return self.dm._get_rcrow(actname, key)
    def set_rckey(self, actname, key, value, comment):
        self.dm._set_rcrow(actname, key, value, comment)
    def update_rckey(self, actname, key, val):
        self.dm._update_rcrow(actname, key, val)
    def get_stats_hash(self):
        return self.stats_hash
    # paths related to the place where SP is currently installed
    def get_libdir_path(self):
        """path to the 'lib' directory were activities store there stuff"""
        return SPConstants.ACTIVITYDATADIR
    def get_absdir_path(self):
        """path to the alphabetsounds directory"""
        return SPConstants.ALPHABETDIR
    def get_absdir_loc_path(self):
        """path to the alphabetsounds directory for the current language"""
        absdir = self.get_absdir_path()
        lang = self.localesetting[0]
        soundlanguagedir = os.path.join(absdir, lang)
        if not os.path.exists(soundlanguagedir):
            if os.path.exists(os.path.join(absdir, lang[:2])):
                soundlanguagedir = os.path.join(absdir, lang[:2])
                self.logger.debug("Using alphabethsounds package %s" % soundlanguagedir)
            else:
                soundlanguagedir = os.path.join(absdir, 'en')
                self.logger.debug("No alphabethsounds found for %s, using english." % lang)
        return soundlanguagedir
    def get_base_dir(self):
        return SPConstants.BASEPATH
    def get_home_theme_path(self):
        return os.path.join(SPConstants.HOMEDIR, self.theme)
    

