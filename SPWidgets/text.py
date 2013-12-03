#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2010-2011 Stas Zykiewicz <stas.zytkiewicz@schoolsplay.org>
#
#           text.py
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

from base import Widget
from SPConstants import *
from SPSpriteUtils import SPSprite
import utils
import pygame
from pygame.constants import *
import types
from funcs import render_textrect
if not NoGtk:
    import pangofont
    
class Label(Widget):
    def __init__(self, txt, pos, fsize=18, padding=4, border=None, maxlen=0, name='', bold=False, transparent=False, ** kwargs):
        """Label which displays a line of text
        txt - string to display
        pos - position to display the box
        rect - Rect indicating the size of the box
        fsize - Font size
        padding - space in pixels around the text
        border - Integer. Draw a border around the label.
        name - string to indicate this object
        bold - set font to bold.
        
        Theres also a number of keyword arguments understood by this widget;
        fgcol - foreground color (other than the theme color)
        bgcol - Background color.
        minh - Minimal height of the widget.
        transparent - No background.
        """ 
        Widget.__init__(self)
        self.fsize = fsize
        self.bold=bold
        self.transparent = transparent
        fgcol = self.THEME['label_fg_color']
        bgcol = self.THEME['label_bg_color']
        if kwargs.has_key('fgcol'):
            fgcol = kwargs['fgcol']
        if kwargs.has_key('bgcol'):
            bgcol = kwargs['bgcol']
        if kwargs.has_key('minh'):
            self.minh = kwargs['minh']
        else:
            self.minh = None
        if kwargs.has_key('ttf'):
            self.ttf = kwargs['ttf']
        else:
            self.ttf = TTF
        if padding < 2:
            padding = 2
        self.padding = padding
        self.fgcol = fgcol
        self.bgcol = bgcol
        self.border = border
        self.settext(txt)
        self.rect  = self.image.get_rect()
        SPSprite.__init__(self, self.image)
        self.rect.move_ip(pos)
        
    def settext(self, txt):
        self._txt = txt
        s = utils.char2surf(txt, fsize=self.fsize,ttf=self.ttf, fcol=self.fgcol, bold=self.bold)
        r = s.get_rect()
        if self.minh:
            y = self.minh
            x = r.w
            x += self.padding*2
            surf = pygame.Surface((x, y))
        else:
            x = r.w
            x += self.padding*2
            y = r.h
            y += self.padding*2
            surf = pygame.Surface((x, y))
        x = (surf.get_rect().w - r.w) / 2
        y = (surf.get_rect().h - r.h) / 2
        surf.fill(self.bgcol)
        surf.blit(s, (x, y))
        if self.transparent:
            self.image = s
        else:
            self.image = surf
        if self.border:
            pygame.draw.rect(self.image, BLACK, self.image.get_rect(), self.border)
    def get_text(self):
        return self._txt


class TextView(Widget):
    def __init__(self, txt, pos, rect=None, fsize=12, padding=4, \
                 autofit=False, border=False, name='', \
                 bgcol=None, fgcol=None, shade=0, bold=False, **kwargs):
        """Box which displays a text, wrapped if needed. 
        txt - string to display. When txt is a list of strings the lines are
            blitted on a surface big enough to hold the longest line.
            rect is not used in this case.
        pos - position to display the box
        rect - Rect indicating the size of the box. 
                Only used in conjunction with txt if it's a string.
        fsize - Font size
        padding - space in pixels around the text
        fgcol - text color (R,G,B), if None the theme color will be used.
        bgcol - background color (R,G,B), if None the theme color will be used.
                If bgcol is set to 'trans' the background will be transparent.
        autofit - Discard the empty space around the text.
        name - string to indicate this object
        shade - The amount of "3D shade" the text should have, 0 means no shade.
                Beware that shading takes time.
        """
        if not fgcol: 
            fgcol = self.self.THEME['textview_fg_color']
        if not bgcol:
            bgcol = self.self.THEME['textview_bg_color']
        if type(txt) in types.StringTypes and rect != None:
            self.image = render_textrect(txt, fsize, TTF, rect, fgcol, \
                              bgcol, justification=0, bold=bold, \
                              autofit=autofit, border=border)
        elif type(txt) is types.ListType:
            ll = []
            w = 0
            for line in txt:
                if not line.strip('\n'):
                    line = ' '
                if shade:
                    s = utils.shadefade(line, fsize, amount=shade, bold=bold, fcol=fgcol, shadecol=DARKGREY)
                    ll.append(s)
                else:
                    s = utils.char2surf(line, fsize, fgcol, bold=bold)
                    ll.append(s)
                if s.get_rect().w > w:
                    w = s.get_rect().w
                
            h = s.get_rect().h   
            if bgcol == 'trans':
                self.image = pygame.Surface((w, h * len(ll)), SRCALPHA)
                self.image.fill((0, 0, 0, 0))
            else:
                self.image = pygame.Surface((w, h * len(ll)))
                self.image.fill(bgcol)
            x, y = 0, 0
            for s in ll:
                self.image.blit(s, (x, y))
                y += h
            
        self.rect  = self.image.get_rect()
        Widget.__init__(self, self.image)
        self.rect.move_ip(pos)       

class SimpleView(Widget):
    """Simple object that displays a numbers of strings.
        Any strings that are longer than the widgets rect are disgarded.
        Use this as a view for command that produces text output repeatedly
        like a shell command.
        Use the TextView for proper text display."""
    def __init__(self, rect, fsize, bgcol=None, fgcol=None, padding=8, border=2, lines=1):
        """Starts empty, use set_text to fill it.
        rect - Rect indicating the size of the box and position. 
        fsize - Font size
        fgcol - text color (R,G,B), if None the theme color will be used.
        bgcol - background color (R,G,B), if None the theme color will be used.
                If bgcol is set to 'trans' the background will be transparent.
        padding - space in pixels around the text
        border - border in pixels, None means no border.
        lines - how many previous lines of text should be visible (cheap scroll effect)
                """
        if not fgcol: 
            fgcol = self.THEME['textview_fg_color']
        if not bgcol:
            bgcol = self.THEME['textview_bg_color']
        self.fgcol = fgcol
        self.bgcol = bgcol
        self.padding = padding
        self.fsize = fsize
        self.image = pygame.Surface(rect.size)
        self.image.fill(self.bgcol)
        self.rect = self.image.get_rect()
        if border:
            pygame.draw.rect(self.image, BLACK, self.rect, border)
        self.org_image = self.image.copy()
        Widget.__init__(self, self.image)
        self.rect.move_ip(rect.topleft)
        self.prevlines = []
        self.lines = lines
    
    def set_text(self, text):
        """Add one line of text."""
        self.prevlines.append(text)
        if len(self.prevlines) > self.lines:
            self.prevlines = self.prevlines[-self.lines:]
        self.image.blit(self.org_image, (0, 0))
        y = 0
        for line in self.prevlines:
            surf = utils.char2surf(line, self.fsize, self.fgcol)
            self.image.blit(surf, (self.padding, self.padding + y))
            y += surf.get_height()

class TextEntry(Widget):
    def __init__(self, pos, length=200, maxlen=0, message='', fsize = 28, border=None, \
                 bold=None, ttf='arial', fgcol=None, bgcol=None, password_mode=False, \
                 validationlist=[], validation_values_list=[]):
        """Box which displays a text input. The height of the box is determined
        by the fontsize used.
        message - input prompt
        pos - position to display the box
        maxlen - is the maximum number of input characters.
        length - length of the display in pixels.
        fsize - font size
        border - One pixel border around the box
        ttf - family of fonts
        fgcol - foreground color (defaults to theme)
        bgcol - background color (defaults to theme)
        password_mode - displays input in stars
        validitionlist - A list with characters that are allowed
        validation_values_list - A list with values that are allowed
        """
        Widget.__init__(self)
        self.logger = logging.getLogger("childsplay.SPWidgets_lgpl.TextEntry")
        self.length = length
        self.maxlen = maxlen
        self.fsize = fsize
        self.message = message
        self.border = border
        self.ttf = ttf
        self.fgcol = fgcol
        if not self.fgcol:
            self.fgcol = self.THEME['textentry_fg_color']
        self.bgcol = bgcol
        if not self.bgcol:
            self.bgcol = self.THEME['textentry_bg_color']
        self.bold = bold
        self.password_mode = password_mode
        self.validationlist = validationlist
        self.validation_values_list = validation_values_list
        if NoGtk:
            font = pygame.font.Font(filename=None, size=fsize)
        else:
            font = pangofont.PangoFont(family=ttf, size=fsize, bold=bold)
        w, h = font.size(message)
        self.image = pygame.Surface((self.length, h))
        self.rect = self.image.get_rect()
        self.image.fill(self.bgcol)
        if self.border:
            pygame.draw.rect(self.image, BLACK, self.image.get_rect(), self.border)
        self.orgimage = self.image.convert()
        self._CanHaveInputFocus = True
        self.connect_callback(self._cbf, [KEYDOWN, MOUSEBUTTONDOWN])
        self.moveto(pos)
        self.xpadding = 6
        self.ypadding = 0
        if self.message:
            self._remove_prompt()
        
    def _cbf(self, widget, event, data):
        if event.type == MOUSEBUTTONDOWN:
            self._add_prompt()
        elif event.type == KEYDOWN:
            if event.key == K_BACKSPACE:
                self.backspace()
            elif event.key == K_RETURN:
                return self.get_text()
            elif event.unicode and ord(event.unicode) > 31:
                if self.validationlist:
                    if event.unicode in self.validationlist:
                        self.add(event.unicode)
                else:
                    self.add(event.unicode)
    
    def _add_prompt(self):
        self.image.blit(self.orgimage, (0, 0))
        self.draw()
    
    def _remove_prompt(self):
        self.image.blit(self.orgimage, (0, 0))
        self.messagesurf = utils.char2surf(self.message, self.fsize, self.fgcol, bold=self.bold)
        self.image.blit(self.messagesurf, (self.xpadding, self.ypadding))
        self.display_sprite()

    def add(self, c):
        if self.maxlen and len(self.message) > self.maxlen-1:
            return
        self.message += c
        self.draw()
        
    def backspace(self):
        self.message = self.message[:-1]
        self.draw()
    
    def draw(self):
        if self.password_mode:
            self.messagesurf = utils.char2surf('*' * len(self.message) +'_', self.fsize, self.fgcol, bold=self.bold)
        else:
            self.messagesurf = utils.char2surf(self.message+'_', self.fsize, self.fgcol, bold=self.bold)
        if self.messagesurf.get_size()[0] <= self.length:
            self.image.blit(self.orgimage, (0, 0))
            self.image.blit(self.messagesurf, (self.xpadding, self.ypadding))
        else:
            self.message = self.message[:-1]
        self.display_sprite()
     
    def clear(self):
        self.image.blit(self.orgimage, (0, 0))
        self.message = ""
        self.display_sprite()
        
    def get_text(self):
        txt = self.message.strip()
        try:
            i = int(txt)
            txt = str(i)
        except ValueError:
            pass
        if self.validation_values_list:
            if txt in self.validation_values_list:
                return txt
            else:
                return ''
        return txt
    
    def set_text(self,txt):
        self.message = txt
        self._remove_prompt() 
        
    def get_surface(self):
        return self.image

class TEB_TextEntry(TextEntry):
    """This eidget is used internally by the TextEntryBox. 
    Don't use this in your code, use the TextEntry
    """
    __current = None
    def __init__(self, pos, length=200, maxlen=0, message='', fsize = 28, border=None, \
                 bold=None, ttf='arial', fgcol=None, bgcol=None, password_mode=False):
        TextEntry.__init__(self, pos, length=length, maxlen=maxlen, \
                           message=message, fsize=fsize, border=border, \
                        bold=bold, ttf=ttf, fgcol=fgcol, bgcol=bgcol,\
                        password_mode=password_mode)
        self.logger = logging.getLogger("childsplay.SPWidgets_lgpl.TEB_TextEntry")
        self._TEfocus = False
    
    def _cbf(self, widget, event, data):
        pass
   
        
class TextEntryBox(Widget):
    def __init__(self, pos, maxlen=0, length=300, height=2, message='', fsize = 14, border=True, \
                 ttf='arial', fgcol=None, bgcol=None, bold=False, password_mode=False):
        """Text input box with multiple lines. The height of the box is determined
        by the fontsize used times the height. You can get the actual height in pixels by calling
        the "get_height" method.
        message - input prompt
        pos - position to display the box
        maxlen - is the maximum number of input characters.
        length - length of the display in pixels.
        height - height in characters lines, 2 means two lines of text.
        fsize - font size
        border - One pixel border around the box
        ttf - family of fonts
        """
        self.height = height
        self.TEs = utils.OrderedDict()
        self.currentline = 0
        self.maxline = height - 1
        sizey = 0
        tepos = (pos[0]+1, pos[1]+1)
        for line in range(height):
            te = TEB_TextEntry(pos=tepos, maxlen=maxlen, \
                            length=length, message=message,\
                            fsize = fsize, border=False, ttf='arial',\
                            fgcol=fgcol, bgcol=fgcol, bold=bold, \
                            password_mode=False)
            te.disconnect_callback()
            te.connect_callback(self._cbf, [KEYDOWN, MOUSEBUTTONDOWN])
            sizey += te.get_sprite_height()
            tepos = (tepos[0], tepos[1] + te.get_sprite_height())
            te.line = line
            self.TEs[line] = te
        sizex = te.get_sprite_width()# length stays the same for all lines
        self.image = pygame.Surface((sizex + 2, sizey + 2))
        Widget.__init__(self, self.image)
        self.image.fill(self.THEME['textentry_bg_color'])
        
        y = 0
        for te in self.TEs.values():
            self.image.blit(te.get_surface(), (0, y))
            y += te.get_sprite_height()
        if border:
            pygame.draw.rect(self.image, BLACK, self.rect, 1)
        self.moveto(pos)
        
    def _cbf(self, widget, event, data):
        if event.type == MOUSEBUTTONDOWN:
            if TEB_TextEntry._TEB_TextEntry__current:
                TEB_TextEntry._TEB_TextEntry__current._remove_prompt()
            TEB_TextEntry._TEB_TextEntry__current = widget
            self.currentline = widget.line
            widget._add_prompt()
        elif event.type == KEYDOWN:
            if TEB_TextEntry._TEB_TextEntry__current is not widget:
                return
            if event.key == K_BACKSPACE:
                widget.backspace()
            elif event.key == K_RETURN:
                if self.currentline < self.maxline:
                    widget._remove_prompt()
                    self.currentline += 1
                    newwidget = self.TEs[self.currentline]
                    newwidget._add_prompt()
                    TEB_TextEntry._TEB_TextEntry__current = newwidget
            elif event.unicode and ord(event.unicode) > 31:
                widget.add(event.unicode)
    
    def get_text(self):
        return [te.get_text() for te in self.TEs.values()]
        
    def get_actives(self):
        return self.TEs.values()
