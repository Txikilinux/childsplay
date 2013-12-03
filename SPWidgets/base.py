#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2010-2011 Stas Zykiewicz <stas.zytkiewicz@schoolsplay.org>
#
#           base.py
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

from SPSpriteUtils import SPSprite
import os
import types
import subprocess
import glob
import ConfigParser
from SPConstants import *
import logging 
module_logger = logging.getLogger("childsplay.SPWidgets")

WEHAVEAUMIX = False
THEME = None

def Init(theme):
    """Must be called before using anything in this class"""
    global THEME,  WEHAVEAUMIX
    module_logger.debug('Init called with:%s' % theme)
    # theme is used by the widgets
    config = ConfigParser.RawConfigParser()
    rc = os.path.join( GUITHEMESPATH, theme, 'SPWidgets.rc')
    if not os.path.exists(rc):
        module_logger.info('theme file %s does not exists' % rc)
        rc = os.path.join('..', GUITHEMESPATH, theme, 'SPWidgets.rc')
        module_logger.info('trying one step higher, %s' % rc)
        if not os.path.exists(rc):
            module_logger.info('theme file %s does not exists, using default file' % rc)
            rc = os.path.join(DEFAULTGUITHEMESPATH,'SPWidgets.rc')
    module_logger.debug("Using rc file %s" % rc)
    d = {}
    config.read(rc)
    for k, v in dict(config.items('default')).items():
        try:
            d[k] = eval(v, {'__builtins__': None}, {})
        except NameError:
            # v is a string
            d[k] = v
    d['theme'] = theme
    d['themepath'] = os.path.dirname(rc)
    d['defaultpath'] = os.path.join( GUITHEMESPATH,'default')
    module_logger.debug("rc file contents: %s" % [d])     
    THEME = d
    volume_level = 50
    try:
        cmd=subprocess.Popen("amixer get Master",shell=True,\
                              stdout=subprocess.PIPE,\
                              stderr=subprocess.PIPE)
        output = cmd.communicate()[0]
    except Exception, info:
        module_logger.warning("program 'amixer' not found, unable to set volume levels: %s" % info)
        WEHAVEAUMIX = False
    else:
        for line in output.split('\n'):
            if "%]" in line:
                volume_level = line.split("%]")[0].split("[")[1]
        WEHAVEAUMIX = volume_level
    return THEME

class Widget(SPSprite):
    def __init__(self, image=None, name=None):
        global THEME, WEHAVEAUMIX
        if image:
            SPSprite.__init__(self, image, name=name)
        else:
            SPSprite.__init__(self, name=name)
        self._mygroups = None
        self._amienabled = True
        self.trans = False
        self._oldimage = None
        self._IamWidget = True #special property, used in the SPSprite class update method
        self._CanHaveInputFocus = False
        self.MinimalDragTreshold = 20
        self._DragEnabled = False
        self._DropEnabled = False
        self.mouse_hover_leave_action = False
        # related to drag and drop
        self._prev_mouse_pos = None
        self.THEME = THEME
        self.WEHAVEAUMIX = WEHAVEAUMIX
        
    def enable(self, enable):
        """Set wetter the sprite can react to events. 
        enable - True or False 
        When enable is set to False the sprite is disconnected from the callback
        function as well as 'greyed-out'.
        When enable is True the sprite is connected again and redisplayed.
        """
        if not enable and self._amienabled:
            if hasattr(self, 'mouse_hover_leave'):
                self.mouse_hover_leave()
            # TODO: find a good solution for alpha trans for trans buttons.
            # problem lies in the per pixel alpha the buttons are using.
#            if self.trans:
#                print "im a trans widget", self.name
#                self._oldimage = self.image.convert_alpha()
#                self.image.blit(self.trans, (0, 0))
#            else:
#                self.image.set_alpha(80)
            self.image.set_alpha(80)
            self._mygroups = self.groups()
            self.remove(self._mygroups)
            self.erase_sprite()
            self.display_sprite()
            self._amienabled = False
        elif enable and not self._amienabled:
            if hasattr(self, 'mouse_hover_leave'):
                self.mouse_hover_leave()
#            if self.trans and self._oldimage:
#                self.image = self._oldimage.convert_alpha()
#            else:
#                self.image.set_alpha(255)
            self.image.set_alpha(255)
            if self._mygroups:
                self.add(self._mygroups)
            self.erase_sprite()
            self.display_sprite()
            self._amienabled = True
            
    def set_drag_enabled(self, enabled):
        self._DragEnabled = enabled
        self._org_center = self.rect.center
    def set_drop_enabled(self, enabled):
        self._DropEnabled = enabled
    def get_actives(self):
        return self
    
    def _DnDreset(self):
        self.moveto(self._org_pos,False)
        
    # These methods should be overridden in your derived class
    def start_drag_event(self, widget, mouseposition):
        self.logger.debug("start_drag_event: widget %s, position %s" % (widget,mouseposition))
    def end_drag_event(self, widget, mouseposition):    
        self.logger.debug("end_drag_event: widget %s, position %s" % (widget,mouseposition))
    def drop_event(self, widget, mouseposition):
        self.logger.debug("end_drag_event: widget %s" % widget,mouseposition)
    