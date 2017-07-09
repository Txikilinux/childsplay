# -*- coding: utf-8 -*-

# Copyright (c) 2006 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           SPCoreButtons.py
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

# Provides buttons and callbacks for the core

#create logger, logger was configured in SPLogging
import logging
module_logger = logging.getLogger("schoolsplay.SPCoreButtons")

import os, glob

import childsplay_sp.ocempgui.widgets as ocw
import childsplay_sp.ocempgui.widgets.Constants as ocwc

from SPConstants import *

class MainCoreButtons:
    """Object that provides the buttons used by the core in the main menu bar.
    Th buttons has to be added to a renderer.
    """
    def __init__(self, theme, quit_cb, info_cb):
        """theme is the name of the theme used. See manual about themes.
        quit_cb is the callback for the quit button.
        info_cb idem for the info button.
        logout_cb idem for logout button.
        """
        global ACTIVITYDATADIR
        if theme != 'default':
            ACTIVITYDATADIR = ACTIVITYDATADIR.replace('childsplay_sp', theme)
        self.logger = logging.getLogger("schoolsplay.SPCoreButtons.MainCoreButtons")
        # text is not used
        self.quit_text = _("Quit")
        self.info_text = _("Info")
        self.sleep_text = _("Pause")
        
        self.__butdict = {}
        ICONPATH = os.path.join(ACTIVITYDATADIR, 'SPData', 'menu', theme)
        DEFAULTICONPATH = os.path.join(ACTIVITYDATADIR, 'SPData', 'menu', 'default')
        # info button
        if theme != 'mpt':
            p = os.path.join(ICONPATH, 'core_info_button.png')
            if not os.path.exists(p):
                p = os.path.join(DEFAULTICONPATH, 'core_info_button.png')
            but = ocw.ImageButton(p)
        else:
            but = ocw.Button()
            but.set_text(self.info_text)
            but.child.create_style()["font"]["size"] = 24
            but.child.style['bgcolor'][ocwc.STATE_NORMAL] = DARK_GREY
            but.create_style()['bgcolor'][ocwc.STATE_NORMAL] = DARK_GREY
        but.connect_signal(ocwc.SIG_CLICKED, info_cb, but)
        self.__butdict['info'] = but
        but.topleft = (CORE_BUTTONS_XCOORDS[0], 10)
        self.logger.debug("info button size: %sx%s" % but.size)
        
        # quit button
        if theme != 'mpt':
            offset = 0
            p = os.path.join(ICONPATH, 'core_quit_button.png')
            if not os.path.exists(p):
                p = os.path.join(DEFAULTICONPATH, 'core_quit_button.png')
            but = ocw.ImageButton(p)
        else:
            offset = 20
            but = ocw.Button()
            but.set_text(self.quit_text)
            but.child.create_style()["font"]["size"] = 24
            but.child.style['bgcolor'][ocwc.STATE_NORMAL] = DARK_GREY
            but.create_style()['bgcolor'][ocwc.STATE_NORMAL] = DARK_GREY
        but.connect_signal(ocwc.SIG_CLICKED, quit_cb, but)
        self.__butdict['quit'] = but
        but.topleft = (CORE_BUTTONS_XCOORDS[-1]-offset, 10)
        
##        # pause button
##        p = os.path.join(ICONPATH,'core_pause_button.png')
##        if not os.path.exists(p):
##            p = os.path.join(DEFAULTICONPATH,'core_pause_button.png')
##        but = ocw.ImageButton(p)
##        #but.set_text(self.quit_text)
##        but.connect_signal(ocwc.SIG_CLICKED,pause_cb,but)
##        self.__butdict['pause'] = but
##        but.topleft = (CORE_BUTTONS_XCOORDS[-5],10)
        
    def get_buttons(self):
        """Returns the ocempgui.table with the buttons.
        """
        return self.__butdict

class ChartButton:
    """Object that provides the chart button used by the core in the main menu bar
    when the activity has a score data member.
    It has to be added to a renderer.
    """
    def __init__(self, re, theme, cb):
        """theme is the name of the theme used. See manual about themes.
        cb is the callback for the button.
        """
        self.logger = logging.getLogger("schoolsplay.SPCoreButtons.ChartButton")
        self._re = re
        ICONPATH = os.path.join(ACTIVITYDATADIR, 'SPData', 'menu', theme)
        DEFAULTICONPATH = os.path.join(ACTIVITYDATADIR, 'SPData', 'menu', 'default')
        p = os.path.join(ICONPATH, 'core_chart_button.png')
        if not os.path.exists(p):
            p = os.path.join(DEFAULTICONPATH, 'core_chart_button.png')
        but = ocw.ImageButton(p)
        # self.chart_text = "Chart"
        #but.set_text(self.chart_text)
        #but.child.create_style()["font"]["size"] = 24
        but.connect_signal(ocwc.SIG_CLICKED, cb, but)
        but.topleft = (CORE_BUTTONS_XCOORDS[-2], 10)
        self._but = but
        self._re.add_widget(self._but)
        self._re.update()

    def erase(self):
        """erase the button"""
        self.logger.debug("erase called")
        self._re.remove_widget(self._but)
        self._re.update()
        
class DiceButtons:
    """Object that provides dice buttons"""
    def __init__(self, re, cb, theme='white'):
        self.logger = logging.getLogger("schoolsplay.SPCoreButtons.DiceButtons")
        self._re = re
        ICONPATH = os.path.join(ACTIVITYDATADIR, 'SPData', 'base', 'dice', theme)
        DEFAULTICONPATH = os.path.join(ACTIVITYDATADIR, 'SPData', 'base', 'dice', 'white')
        dicelist = glob.glob(os.path.join(ICONPATH, 'dice*.png'))
        if len(dicelist) < 6:
            dicelist = glob.glob(os.path.join(DEFAULTICONPATH, 'dice*.png'))
        self._butdict = {}
        count = 1
        try:
            dicelist.sort()
            for diceimg in dicelist:
                but = ocw.ImageButton(diceimg)
                but.topleft = (CORE_BUTTONS_XCOORDS[-3], 10)
                but.connect_signal(ocwc.SIG_CLICKED, cb, but)
                self._butdict[count] = but
                count += 1
        except StandardError, info:
            self.logger.error("Can't load dice images for buttons: %s" % info)
        self._current_but = self._butdict[1]
        
    def next_level(self, level):
        self.logger.debug("level %s called" % level)
        if self._current_but:
            self._re.remove_widget(self._current_but)
        self._current_but = self._butdict[level]
        self._re.add_widget(self._current_but)
        self._re.update()
                
    def erase(self):
        self.logger.debug("erase called")
        if self._current_but:
            self._re.remove_widget(self._current_but)
        self._current_but = None
        self._re.update()

    def enable(self, enable):
        self.logger.debug("enable called with: %s" % enable)
        self._current_but.sensitive = enable
