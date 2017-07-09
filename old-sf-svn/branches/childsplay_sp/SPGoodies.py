# -*- coding: utf-8 -*-

# Copyright (c) 2006-2008 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
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
 

class SPGoodies(Borg):
    """This class is a singleton because we want that the core and
    activity always uses the same object"""
    def __init__(self, screen, back, clip, virtkb, lang, lock, \
        cb_level_end, cb_game_end, cb_info_dialog, \
        cb_display_execounter, cb_set_framerate, \
        cb_enable_dice):
        Borg.__init__(self)
        # references to stuff, use the methods to get them
        self.logger = logging.getLogger("schoolsplay.SPGoodies")
        self.screen = screen
        self.background = back
        self.screenclip = clip
        self.screen.set_clip(self.screenclip)
        self.background.set_clip(self.screenclip)
        self.virtkb = virtkb
        self.level_end = cb_level_end
        self.game_end = cb_game_end
        if '.' in lang[0] and len(lang[0]) > 4:
            lang = (lang[0][:5], lang[1])
        self.localesetting = lang
        self.lock = lock
        self.info_dialog = cb_info_dialog
        self.display_execounter = cb_display_execounter
        self.set_framerate = cb_set_framerate
        self.enable_dice = cb_enable_dice
        
    # these methods are the observers that an activity can use to signal the core
    def tellcore_level_end(self, store_db=None):
        """Use this to notify the core that the level is ended.
        The core will call next_level on the activity."""
        apply(self.level_end, (store_db, ))
    def tellcore_game_end(self, store_db=None):
        """Use this to notify the core that the game is ended.
        The core will start the menu and delete the activity."""
        apply(self.game_end, (store_db, ))
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
        apply(self.enable_dice, (enable,))
    # these methods provide stuff needed by the activity.
    def get_screen(self):
        """get a references to the main SDL screen"""
        self.screen.set_clip(self.screenclip)
        return self.screen
    def get_background(self):
        """get a references to the background surface"""
        self.background.set_clip(self.screenclip)
        return self.background
    def get_virtual_keyboard(self):
        """get a virtual keyboard object which is setup by the maincore.
        when we not in kioskmode this will return None so be sure to check
        the object returnt before trying to use it."""
        return apply(self.virtkb)
    def get_localesetting(self):
        """Returns the current locale as set by schoolsplay.
        The value is a tuple with the language code and a bool signalling if
        were in a RTL environment (Hebrew and Arabic)"""
        return self.localesetting
    def get_screenclip(self):
        """get a rect representing the area to be 'clipped'.
        This should be used to set a clip to the screen when your activity sets
        a background of it's own. You should set a screen clip to prevent
        your background from overlapping the SP background.
        The rect returnt is based on the current them used."""
        return self.screenclip
    def get_thread_lock(self):
        """Returns a reference to the thread lock setup by the core.
        This lock MUST be used when dealing with the timer object from
        the SP Timer module.
        """
        return self.lock
    def get_theme(self):
        """Returns the theme name or None for the default theme.
        """
        return self._theme
    # paths related to the place where SP is currently installed
    def get_libdir_path(self):
        """path to the 'lib' directory were activities store there stuff"""
        if self._theme == 'cognitionplay':
            return SPConstants.ACTIVITYDATADIR.replace('childsplay_sp', 'cognitionplay')
        else:
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
        
        
