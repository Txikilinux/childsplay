# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           SPWidgets.py
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

import os
import types

import glob
import ConfigParser
import pygame
from pygame.constants import *
from SPSpriteUtils import SPSprite, SPGroup
import utils
from SPConstants import *
import logging 
import ConfigParser
import pangofont
module_logger = logging.getLogger("schoolsplay.SPWidgets")

LOCALE_RTL = utils.get_locale()[1]
if LOCALE_RTL:
    ALIGN_RIGHT = True
    ALIGN_LEFT = False
else:
    ALIGN_LEFT = True
    ALIGN_RIGHT = False

WEHAVEAUMIX = False

class TextRectException(Exception):
    pass

def Init(theme):
    """Must be called before using anything in this class"""
    global THEME, BUT_CENTER, BUT_LEFT, BUT_RIGHT, BUTH_CENTER, BUTH_LEFT, BUTH_RIGHT, WEHAVEAUMIX
    module_logger.debug('Init called with:%s' % theme)
    # theme is used by the widgets
    config = ConfigParser.RawConfigParser()
    rc = os.path.join( GUITHEMESPATH, theme, 'SPWidgets.rc')
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
    if d.has_key('button_background_image_left') and \
                                os.path.exists(os.path.join(d['themepath'], \
                                                d['button_background_image_left'])):
        # We create the three pieces we need to create a rounded corner button background
        # By doing it here and using copies in make_button_bg we make it faster.
        # when we need to create many buttons the disk IO could take to much time.
        # the button is build from three pieces
        BUT_LEFT = utils.load_image(os.path.join(d['themepath'], \
                                                 d['button_background_image_left']))
        BUT_RIGHT = utils.load_image(os.path.join(d['themepath'], \
                                                  d['button_background_image_right']))
        BUT_CENTER = utils.load_image(os.path.join(d['themepath'], \
                                                 d['button_background_image_center']))
    if d.has_key('button_hover_background_image_left') and \
                                os.path.exists(os.path.join(d['themepath'], \
                                                d['button_hover_background_image_left'])):
        BUTH_LEFT = utils.load_image(os.path.join(d['themepath'], \
                                                 d['button_hover_background_image_left']))
        BUTH_RIGHT = utils.load_image(os.path.join(d['themepath'], \
                                                  d['button_hover_background_image_right']))
        BUTH_CENTER = utils.load_image(os.path.join(d['themepath'], \
                                                 d['button_hover_background_image_center']))
        
    THEME = d
    
    try:
        output=os.popen('aumix -q').readlines()
        end=output[0].find(",")
        volume_level=int(output[0][4:end])
    except:
        module_logger.warning("program 'aumix' not found, unable to set volume levels")
        WEHAVEAUMIX = False
    else:
        WEHAVEAUMIX = volume_level
    
    return THEME

class Widget(SPSprite):
    def __init__(self):
        SPSprite.__init__(self)
        self._mygroups = None
        self._amienabled = True
        self.trans = False
        self._oldimage = None
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

class Button(Widget):
    def __init__(self, txt, pos=(0, 0), fsize=18, padding=4, name='', **kwargs):
        """Button which shows a text
        txt - string to display
        pos - position to display the box
        fsize - Font size
        padding - space in pixels around the text
        name - string to indicate this object
        kwargs - bgcol, fgcol
        """
        if kwargs.has_key('fgcol'):
            fgcol = kwargs['fgcol']
        else:
            fgcol = THEME['button_fg_color']
        self.kwargs = kwargs
        Widget.__init__(self)
        self.ImSelected = False
        if padding < 2:
            padding = 2
        if type(txt) in (types.StringType, types.UnicodeType):
            s = utils.char2surf(txt, fcol=fgcol, fsize=fsize, ttf=P_TTF)
            r = s.get_rect()
            r.w += padding*2
            r.h += padding*2
        else:
            s = txt
            r = s.get_rect()
            r.w += padding*2
            r.h += padding*2
        self.pos = pos
        self.padding = padding
        self.name = name
        self.r = r
        self._setup(s)
        
    def _setup(self, s):
        if self.kwargs.has_key('bgcol'):
            bgcol = self.kwargs['bgcol']
        else:
            bgcol = THEME['button_bg_color']
        self._but, self._but_hover, self._but_selected = get_boxes(\
                                                bgcol,\
                                                THEME['button_color_hover'],\
                                                self.r, \
                                                THEME['button_selected_color'])

        self._but.blit(s, (self.padding, self.padding))
        self._but_hover.blit(s, (self.padding, self.padding))
        self._but_selected.blit(s, (self.padding, self.padding))
        self.image = self._but
        self.rect  = self.image.get_rect()
        SPSprite.__init__(self, self.image, name=self.name)
        self.rect.move_ip(self.pos)
    
    def mouse_hover_enter(self):
        if self.ImSelected:
            return
        self.hover_active = True
        self.image = self._but_hover
        self.erase_sprite()
        self.display_sprite()
        
    def mouse_hover_leave(self):
        if self.ImSelected:
            return
        self.hover_active = False
        self.image = self._but
        self.erase_sprite()
        self.display_sprite()
    
    def select(self):
        self.ImSelected = True
        self.erase_sprite()
        self.image = self._but_selected
        self.display_sprite()
        
    def unselect(self):
        self.ImSelected = False
        self.erase_sprite()
        self.image = self._but
        self.display_sprite()
    def get_button_rect(self):
        return self.rect
    
class ImgButton(Button):
    def __init__(self, path, pos=(0, 0),padding=4, name=''):
        """Button which shows an image.
        path - must be the path to the image file or a pygame surface
        pos - position to display the box
        rect - Rect indicating the size of the box
        padding - space in pixels around the text
        name - string to indicate this object
        """
        
        if type(path) in types.StringTypes:
            image = utils.load_image(path)
        else:
            image = path
        Button.__init__(self, image, pos, None, padding=padding, name=name)

class TransImgButton(ImgButton):
    def __init__(self, path, hpath, pos=(0, 0), padding=4,text='',fsize=24, fcol=BLACK, name=''):
        """Button which shows an image but has a fully transparent background.
        When a hover event occurs the image is changed.
        path - must be the path to the image file or a pygame surface
        hpath - must be the path to the image file or a pygame surface that will
                be shown when a hover event occurs.
        pos - position to display the box
        rect - Rect indicating the size of the box
        padding - space in pixels around the text
        name - string to indicate this object
        text - when a sting is given it will be blitted over the image.
        fsize - fontsize.
        """
        self.text = text
        self.fsize = fsize
        if type(path) in types.StringTypes:
            image = utils.load_image(path)
        else:
            image = path
        if hpath:
            if type(hpath) in types.StringTypes:
                self.hs = utils.load_image(hpath)
            else:
                self.hs = hpath
        else:
            self.hs = utils.grayscale_image(image.convert_alpha())
        if self.text:
            s = utils.char2surf(text, fsize, fcol)
            r = image.get_rect()
            sr = s.get_rect()
            sr.center = r.center
            image.blit(s, sr)
            self.hs.blit(s, sr)
        ImgButton.__init__(self, image, pos, padding=padding, name=name)
        
    def _setup(self, s):
        self.trans = True
        self._but = pygame.Surface(self.r.size,SRCALPHA)
        #self._but.fill((0, 0, 0, 0))
        self._but_hover = pygame.Surface(self.r.size, SRCALPHA)
        
        self._but.blit(s, (self.padding, self.padding))
        self._but_hover.blit(self.hs, (self.padding, self.padding))
    
        self._but_selected = self._but_hover
        self.image = self._but
        self.rect  = self.image.get_rect()
        SPSprite.__init__(self, self.image, name=self.name)
        self.rect.move_ip(self.pos)


class ButtonRound(Button):
    def __init__(self, txt, pos=(0, 0), fsize=18, padding=4, name='', **kwargs):
        """Button which shows a text on a background with round corners.
        txt - string to display
        pos - position to display the box
        fsize - Font size
        padding - space in pixels around the text
        name - string to indicate this object
        """
        self.kwargs = kwargs
        Button.__init__(self, txt,pos=pos, fsize=fsize, padding=padding, name=name, **kwargs)
        
    def _setup(self, s):
        self._but, self._but_hover = make_button_bg(self.r.size)
        r = self._but.get_rect()
        size = r.size
        sr = s.get_rect()
        sr.center = r.center
        if self.kwargs.has_key('bgcol'):
            bgcol = self.kwargs['bgcol']
        else:
            bgcol = THEME['button_selected_color']
        self._but_selected = pygame.Surface(size)
        self._but_selected.fill(bgcol)
        
        self._but.blit(s, sr)
        self._but_hover.blit(s, sr)
        self._but_selected.blit(s, sr)
        self.image = self._but
        self.rect  = self.image.get_rect()
        SPSprite.__init__(self, self.image, name=self.name)
        self.rect.move_ip(self.pos)

class ImgButtonRound(ButtonRound):
    def __init__(self, path, pos=(0, 0),padding=4, name='', hoverimg=None):
        """Button which shows an image on a background with round corners.
        path - must be the path to the image file or a pygame surface
        pos - position to display the box
        rect - Rect indicating the size of the box
        padding - space in pixels around the text
        name - string to indicate this object
        hoverimg - Image to use as the 'hover' image iso the button hover background.
        """
        if type(path) in types.StringTypes:
            image = utils.load_image(path)
        else:
            image = path
        ButtonRound.__init__(self, image, pos, None, padding=padding, name=name)

class SimpleButton(Button):
    """Button which shows a text and returns the value given by 'data'
        when a MOUSEBUTTONDOWN event occurs.
        This differs from a normal Button which should be connect a 
        function."""
    def __init__(self, txt, pos=(0, 0), fsize=18, padding=4, data=True, **kwargs):
        """
        txt - string to display
        pos - position to display the box
        fsize - Font size
        padding - space in pixels around the text
        data - Optional data to pass to the caller, defaults to True.        
        """
        Button.__init__(self, txt, pos, fsize, padding)
        self.connect_callback(self._cbf, MOUSEBUTTONDOWN)
        self.data = data
        
    def _cbf(self, *args):
        return (self.data, )
        
class SimpleButtonRound(ButtonRound):
    """Button which extends ButtonRound and returns the value given by 'data'
        when a MOUSEBUTTONDOWN event occurs.
        This differs from a normal ButtonRound which should be connect a 
        function."""
    def __init__(self, txt, pos=(0, 0), fsize=18, padding=4, data=True):
        fgcol = THEME['simplebuttonround_fg_color']
        ButtonRound.__init__(self, txt, pos, fsize, padding, fgcol=fgcol)
        self.connect_callback(self._cbf, MOUSEBUTTONDOWN)
        self.data = data
    def _cbf(self, *args):
        return (self.data, )

class SimpleTransImgButton(TransImgButton):
    """Button which extends TransImgButton and returns the value given by 'data'
        when a MOUSEBUTTONDOWN event occurs.
        This differs from a normal TransImgButton which should be connect a 
        function."""
    def __init__(self, path, hpath, pos=(0, 0), padding=4,text='',fsize=24, fcol=BLACK, data=True):
        TransImgButton.__init__(self, path, hpath, pos, padding,text,fsize, fcol)
        self.connect_callback(self._cbf, MOUSEBUTTONDOWN)
        self.data = data
    def _cbf(self, *args):
        return (self.data, )    
    

class Label(Widget):
    def __init__(self, txt, pos, fsize=18, padding=4, border=None, name='', bold=False, ** kwargs):
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
        self.transparent = False
        self.bold=bold
        fgcol = THEME['label_fg_color']
        bgcol = THEME['label_bg_color']
        if kwargs.has_key('fgcol'):
            fgcol = kwargs['fgcol']
        if kwargs.has_key('bgcol'):
            bgcol = kwargs['bgcol']
        if kwargs.has_key('minh'):
            self.minh = kwargs['minh']
        else:
            self.minh = None
        if kwargs.has_key('transparent'):
            self.transparent = kwargs['transparent']
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
        s = utils.char2surf(txt, fsize=self.fsize,ttf=P_TTF, fcol=self.fgcol, bold=self.bold)
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
        
class TextView(Widget):
    def __init__(self, txt, pos, rect, fsize=12, padding=4, \
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
            fgcol = THEME['textview_fg_color']
        if not bgcol:
            bgcol = THEME['textview_bg_color']

        if type(txt) in types.StringTypes and rect:
            self.image = render_textrect(txt, fsize, P_TTF, rect, fgcol, \
                              bgcol, justification=0, bold=bold, \
                              autofit=autofit, border=border)
        elif type(txt) == types.ListType:
            ll = []
            sll = []
            w = 0
            for line in txt:
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
        SPSprite.__init__(self, self.image)
        self.rect.move_ip(pos)

class TextEntry(Widget):
    # Original author: Joe Wreschnig, Copyright (c)2003 Joe Wreschnig
    # Original license: GNU GPL version 2 or higher
    # Copyright 2010 Stas Zytkiewicz
    #     Added support for SPSprite, maximum characters and automatic surface size.
    #     Fixed a bug in the backspace event handling.
    def __init__(self, pos, maxlen=12, length=100, message='', fsize = 28, border=True, \
                 ttf='arial', fgcol=None, bgcol=None, bold=False, password_mode=False):
        """Box which displays a text input. The height of the box is determined
        by the fontsize used.
        message - input prompt
        pos - position to display the box
        maxlen - is the maximum number of input characters.
        length - length of the display in pixels.
        fsize - font size
        border - One pixel border around the box
        ttf - family of fonts
        """
        font = pangofont.PangoFont(family=ttf, size=fsize, bold=bold)
        w, h = font.size(message)
        question = font.render(message, True, THEME['textentry_fg_prompt_color'])
        self.ql = question.get_rect().w
        surf = pygame.Surface((length + self.ql + 8, h))
        surf.fill(THEME['textentry_bg_color'])
        if border:
            pygame.draw.rect(surf,THEME['textentry_fg_color'] , surf.get_rect(), 1)
        surf.blit(question, [1, 1])

        self.password_mode = password_mode
        self.maxlen = maxlen
        self._font = font
        self.image = surf
        self.org_image = surf.convert()
        SPSprite.__init__(self, self.image)
        self.moveto(pos)

    def ask(self, string = ''):
        idx = len(string)
        cut = ""
        r_q = self.image.get_rect()
        while True:
            x_off = 6
            self.image.blit(self.org_image, r_q)
            for i in range(len(string)):
                c = string[i]
                if i == idx: self._font.set_underline(True)                    
                img_a = self._font.render(c, True,THEME['textentry_fg_color'] )
                self._font.set_underline(False)
                r_a = img_a.get_rect()

                r_a.topleft = [r_q.x + x_off + self.ql,
                               r_q.y -2]
                x_off += img_a.get_width()            
                self.image.blit(img_a, r_a)

            if idx == len(string):
                img_a = self._font.render("_", True, THEME['textentry_fg_color'])
                r_a = img_a.get_rect()

                r_a.topleft = [r_q.x + x_off + self.ql,
                               r_q.y -2]
                self.image.blit(img_a, r_a)
                
            self.display_sprite()

            ev = pygame.event.wait()
            while ev.type != KEYDOWN:
                ev = pygame.event.wait()

            if ev.key == K_ESCAPE: return None
            #elif ev.key == K_F11: pygame.display.toggle_fullscreen()
            elif ev.key == K_BACKSPACE and len(string) > 0:
                string = string[:idx - 1] + string[idx:]
                idx -= 1
            elif ev.key == K_DELETE:
                string = string[:idx] + string[idx + 1:]
            elif ev.key == K_RETURN: break
            elif ev.key == K_END: idx = len(string)
            elif ev.key == K_HOME: idx = 0
            elif ev.key == K_LEFT: idx = max(0, idx - 1)
            elif ev.key == K_RIGHT: idx = min(len(string), idx + 1)

            elif ev.key < 128:
                if ev.mod & KMOD_CTRL:
                    if len(string) == 0: pass
                    elif ev.key == K_u:
                        string = ""
                        idx = 0
                    elif ev.key == K_h: string = string[0:-1]
                    elif ev.key == K_e: idx = len(string)
                    elif ev.key == K_a: idx = 0
                    elif ev.key == K_f: idx = min(len(string), idx + 1)
                    elif ev.key == K_b: idx = max(0, idx - 1)
                    elif ev.key == K_t:
                        if idx == 0: idx = 1
                        if len(string) == 1: pass
                        elif idx == len(string):
                            string = string[:-2] + string[-1] + string[-2]
                        else:
                            string = (string[:idx - 1] + string[idx] +
                                      string[idx - 1] + string[idx + 1:])
                            idx = min(len(string), idx + 1)
                    elif ev.key == K_k:
                        cut = string[idx:]
                        string = string[:idx]
                    elif ev.key == K_y:
                        string = string[:idx] + cut + string[idx:]
                        idx += len(cut)
                    elif ev.key == K_w:
                        if string[-1] == "/": string = string[:-1]
                        string = string[:string.rfind("/") + 1]
                elif len(string) <= self.maxlen and not (ord (ev.unicode) < 32):
                    string = string[:idx] + ev.unicode + string[idx:]
                    idx += 1

        return string

class Dialog(Widget):
    """Modal dialog which displays text and has one or two buttons.
    The dialog has it's own eventloop.
    Usage:
    dlg = Dialog(txt, (10, 200),buttons=["Cancel", "OK"], title='Information')
    dlg.run() # this blocks any other events loops
    answer = dlg.get_result()
    dlg.erase_sprite()
    """
    def __init__(self, txt, pos=None, fsize=12, butfsize=20, buttons=['OK'], title='', \
                 dialogwidth=300, name='', fbold=True):
        """screen - current pygame screen surface
        txt - can be a string or a list of strings or a SPSprite object.
        pos - is a tuple with x,y grid numbers. If not set the dialog is centered.
        fsize -  the fontsize (integer)
        buttons - a list with strings for the buttons (max two)
        name - to identify this object (optional) 
        """
        self.scrclip = self.screen.get_clip()
        self.screen.set_clip((0, 0, 800, 600))   
        self.dim = utils.Dimmer()
        self.dim.dim(darken_factor=140, color_filter=CORNFLOWERBLUE)
        self.orgscreen = self.screen.convert()
        self.orgbackgr = self.backgr.convert()
        self.txt = txt 
        self.pos = pos
        self.fsize = fsize
        self.buttons = buttons
        self.title = title
        self.dialogwidth = dialogwidth
        self.name = name
        self.fbold = fbold
        self.result = None
        self.runloop = True
        self.buttons_list = []
        self.butspace = 0
        self.padding = 8
        self.actives = SPGroup(self.screen, self.backgr)
        for buttxt in self.buttons:
            b = Button(buttxt, (380, 250), butfsize, padding=12, name=buttxt, \
                       fgcol=THEME['dialog_but_fg_color'], \
                       bgcol=THEME['dialog_but_bg_color'])
            b.connect_callback(self.cbf, MOUSEBUTTONDOWN, buttxt)
            self.actives.add(b)
            self.buttons_list.append(b)# keep the users order for showing (see below)
            self.butspace += b.rect.w
        self._setup()
        
    def _setup(self):    
        # get all the surfaces
        title = utils.char2surf(self.title, 16, ttf=P_TTF, fcol=THEME['dialog_title_fg_color'])
        r = pygame.Rect(0, 0, self.dialogwidth, 500)
        
        if type(self.txt) == types.ListType or type(self.txt) in types.StringTypes:
            if type(self.txt) == types.ListType:
                self.txt = '\n'.join(self.txt)
            tv = TextView(self.txt, (0, 0), r, bgcol=THEME['dialog_bg_color'],fsize=self.fsize ,\
                          fgcol=THEME['dialog_fg_color'], autofit=True, bold=self.fbold)
        else: # we assume a SPWidget.Widget object
            tv = self.txt
        
        b = self.buttons_list[0]
        # start building dialog
        r = pygame.Rect(0, 0, tv.rect.w + (self.padding * 2), \
                        title.get_rect().h + 8 + b.rect.h + tv.rect.h + (self.padding*3))
        dlgsurf, spam = get_boxes(THEME['dialog_bg_color'], \
                            THEME['dialog_bg_color'], r)
        
        r = dlgsurf.get_rect()
        if not self.pos:
            y = max(10, (600 - r.h) / 2)
            x = (800 - r.w) / 2
            self.pos = (x, y)
        # the offset of 2 is needed to keep border
        titlesurf = pygame.Surface((r.w-3, title.get_rect().h+self.padding))
        titlesurf.fill(THEME['dialog_title_bg_color'])
        pygame.draw.rect(titlesurf, BLACK, titlesurf.get_rect(), 1)
        titlesurf.blit(title, (3, 3))
        dlgsurf.blit(titlesurf, (1, 1))
        
        y = titlesurf.get_rect().h
        x = r.w - 8
        dlgsurf.blit(tv.image, (self.padding, self.padding+titlesurf.get_rect().h))
        
        y = y + tv.rect.h + self.padding
        x = r.w - 8
        pygame.draw.line(dlgsurf, (0, 0, 0), (8,y), (x, y))
        
        barsurf = pygame.Surface((r.w-3, b.rect.h+self.padding-2))
        barsurf.fill(THEME['dialog_bar_color'])
        br = barsurf.get_rect()
        dlgsurf.blit(barsurf, (1, r.bottom-2 - br.h))
        
        SPSprite.__init__(self, dlgsurf)
        
        s = pygame.Surface(dlgsurf.get_rect().inflate(4, 4).size)
        w, h = s.get_rect().size
        s.blit(self.backgr, (0, 0), (self.pos[0], self.pos[1], w, h))
        shadow = pygame.Surface(dlgsurf.get_rect().size)
        shadow.fill(GRAY20)
        s.blit(shadow, (4, 4))
        s.blit(dlgsurf, (0, 0))
        self.image = s.convert()
        self.rect.inflate_ip(4, 4)
        self.rect.move_ip(self.pos)
        
        x = self.rect.left + ((self.rect.w - self.butspace) / 2)
        y = self.rect.bottom - b.rect.h - self.padding
        self.action_area_pos = ((self.pos[0], y-self.padding*2), dlgsurf.get_rect().w)
        if len(self.buttons_list) == 2:
            x = self.rect.left + 4
            self.buttons_list[0].moveto((x, y), True)
            x = self.rect.right - (self.buttons_list[1].rect.w + 8)
            self.buttons_list[1].moveto((x, y), True)
        else:
            for b in self.buttons_list:
                b.moveto((x, y), True)
                x += b.rect.w + 16
            
    def cbf(self, widget, event, data):
        self.result = data 
        self.runloop = False
        
    def get_result(self):
        return self.result
    
    def run(self, guests=None):
        if guests:
            self.actives.add(guests)
        result = None
        self.display_sprite()
        for b in self.actives:
            b.display_sprite()
        clock = pygame.time.Clock()
        while self.runloop:
            clock.tick(30)
            pygame.event.pump()
            events = pygame.event.get()
            for event in events:
                if event.type is KEYDOWN and event.key is K_ESCAPE:
                    self.runloop = False
                else:
                    self.actives.update(event)
        self.erase_sprite()
        self.screen.blit(self.orgscreen, (0, 0))
        self.backgr.blit(self.orgbackgr, (0, 0))
        self.dim.undim()
        self.screen.set_clip(self.scrclip)

class StarButtonsDialog(Widget):
    """Special dialog with a level indicator used by the braintrainer version.
    This is intended to be controlled by the SPSpriteGui.StarButtons object"""
    def __init__(self, maxlevels, start_level):
        SPSprite.__init__(self)
        self.theme = THEME['theme']
        self.runloop = True
        self.maxlevels = maxlevels
        self.start_level = start_level
        self.starlist =[]
        self.imgstar0 = utils.load_image(os.path.join(THEMESPATH, self.theme,'star0_b.png'))
        self.imgstar1 = utils.load_image(os.path.join(THEMESPATH, self.theme,'star1_b.png'))
        self.actives = SPGroup(self.screen, self.backgr)
        self.actives.set_onematch(True)
        self.scrclip = self.screen.get_clip()
        self.screen.set_clip((0, 0, 800, 600))    
        self.dim = utils.Dimmer()
        self.dim.dim(darken_factor=THEME['starbuttonsdialog_darkenfactor'], color_filter=THEME['starbuttonsdialog_dim_color'])
        x = 40
        y = 200
        for i in range(self.maxlevels):
            b = SPSprite(self.imgstar0)
            b.moveto((x, y), hide=True)
            b.connect_callback(self.cbf, MOUSEBUTTONDOWN, i+1)
            self.starlist.append(b)
            x += self.imgstar0.get_width()
        # set first star to active
        self.starlist[0].image = self.imgstar1
        self.actives.add(self.starlist)
        
        self.buttons_list = []
        x = 100
        y = 400
        
        for buttxt in [_("Cancel"), _("OK")]:
            b = Button(buttxt, (x, y), fsize=THEME['starbuttonsdialog_fsize'], name=buttxt)
            b.connect_callback(self.but_cbf, MOUSEBUTTONDOWN, buttxt)
            self.actives.add(b)
            self.buttons_list.append(b)# keep the users order for showing (see below)
            x += 300
        
    def cbf(self, widget, event, data):
        self.result = data 
        self.set_level(data[0])
            
    def but_cbf(self, widget, event, data):
        if data[0] == _("Cancel"):
            self.result = [None]
        self.runloop = False

    def get_result(self):
        if not self.result:
            return [None]
        return self.result
        
    def run(self):
        self.result = None
        for b in self.actives:
            b.display_sprite()
        for b in self.buttons_list:
            b.display_sprite()
        clock = pygame.time.Clock()
        while self.runloop:
            clock.tick(30)
            pygame.event.pump()
            events = pygame.event.get()
            for event in events:
                if event.type is KEYDOWN and event.key is K_ESCAPE:
                    self.runloop = False
                else:
                    self.actives.update(event)
        self.dim.undim()
        self.screen.set_clip(self.scrclip)
        
                
    def set_level(self, level):
        if level < self.start_level:
            return
        for i in range(0, level):
            self.starlist[i].image = self.imgstar1
            self.starlist[i].display_sprite()
        for i in range(level, self.maxlevels):
            self.starlist[i].image = self.imgstar0
            self.starlist[i].display_sprite()

        
class PrevNextButton:
    """Button that can switch between two images in a toggle like fashion.
    The data returnt to the callback function is also changed when the button
    image is changed"""
    def __init__(self, pos, cbf, prevname, nextname):
        self.pos = pos
        self._cbf = cbf
        self.prevname = prevname
        self.nextname = nextname
        self._setup()
        
    def _setup(self):
        pp = os.path.join(THEMESPATH, THEME['theme'], self.prevname)
        if not os.path.exists(pp):
            pp = os.path.join(DEFAULTTHEMESPATH, self.prevname)
        np = os.path.join(THEMESPATH, THEME['theme'], self.nextname)
        if not os.path.exists(np):
            np = os.path.join(DEFAULTTHEMESPATH, self.nextname)
        self.state = 'prev'

        previmg = utils.load_image(pp)
        self.nextimg = utils.load_image(np)
        self.but = ImgButton(previmg, self.pos, name='prevnext')
        self.previmg = self.but._but.convert_alpha()# image is now blitted on a button surface
        self.previmg_hover = self.but._but_hover.convert_alpha()
        self.current = self.previmg
        
        temp = ImgButton(self.nextimg, self.pos, name='prevnext')
        self.nextimg = temp._but.convert_alpha()
        self.nextimg_hover = temp._but_hover.convert_alpha()
        
        self.but.connect_callback(self._cbf, MOUSEBUTTONDOWN, 'prev')
    
    def get_actives(self):
        return self.but
    
    def toggle(self):
        """When called the button switch images."""
        if self.current == self.previmg:
            self.current = self.nextimg
            self.but._but = self.nextimg
            self.but._but_hover = self.nextimg_hover
            self.state = 'next'
            self.but.connect_callback(self._cbf, MOUSEBUTTONDOWN, 'next')
        else:
            self.current = self.previmg
            self.but._but = self.previmg
            self.but._but_hover = self.previmg_hover
            self.state = 'prev'
            self.but.connect_callback(self._cbf, MOUSEBUTTONDOWN, 'prev')
        self.but.mouse_hover_leave()

    # abstract methods so that this widget acts like a regular widget
    def enable(self, enable):
        self.but.enable(enable)
    def display_sprite(self, pos=None):
        self.but.display_sprite(pos)
    def erase_sprite(self):
        self.but.erase_sprite()

class TransPrevNextButton(PrevNextButton):
    """Transparent button that can switch between two images in a toggle like fashion.
    The data returnt to the callback function is also changed when the button
    image is changed"""
    def __init__(self, pos, cbf, prevname, hprevname, nextname, hnextname):
        self._cbf = cbf
        self.pos = pos
        self.prevname = prevname
        self.hprevname = hprevname
        self.nextname = nextname
        self.hnextname = hnextname
        PrevNextButton.__init__(self, pos, cbf, prevname, nextname)
                
    def _setup(self):
        self.state = 'prev'
        pp = os.path.join(THEMESPATH, THEME['theme'], self.prevname)
        hpp = os.path.join(THEMESPATH, THEME['theme'], self.hprevname)
        np = os.path.join(THEMESPATH, THEME['theme'], self.nextname)
        hnp = os.path.join(THEMESPATH, THEME['theme'], self.hnextname)

        self.but = TransImgButton(pp, hpp, self.pos, name='prevnext')
        # this is needed for Widet.enable, normal enable/disable doesn't work
        # for per pixel alphas
        s = pygame.Surface(self.but._but.get_size(), SRCALPHA)
        s.fill((0, 0, 0, 80))
        self.but.trans = s
        self.previmg = self.but._but.convert_alpha()# image is now blitted on a button surface
        self.previmg_hover = self.but._but_hover.convert_alpha()
        self.current = self.previmg

        temp = TransImgButton(np, hnp, self.pos, name='prevnext')
        self.nextimg = temp._but.convert_alpha()
        self.nextimg_hover = temp._but_hover.convert_alpha()
        
        self.but.connect_callback(self._cbf, MOUSEBUTTONDOWN, 'prev')
        

class ChartButton(ImgButton):
    def __init__(self, pos, cbf):
        bname = 'core_chart_button.png'
        p = os.path.join(THEMESPATH, THEME['theme'], bname)
        if not os.path.exists(p):
            p = os.path.join(DEFAULTTHEMESPATH, bname)
        ImgButton.__init__(self, p, pos, name='Chart')
        self.connect_callback(cbf, MOUSEBUTTONDOWN, 'Chart')
    
class DiceButtons:
    def __init__(self, pos, actives, cbf, usebutton=True):
        self.logger = logging.getLogger("schoolsplay.SPSpriteGui.DiceButtons")
        self.actives = actives
        theme = THEME['theme']
        self.minimallevel = 1
        self.maxlevels = 6
        self._setup(theme, pos, actives, cbf, usebutton=True)
        self.showme = True
        
    def _setup(self, theme, pos, actives, cbf, usebutton=True):
        bname = 'dice-1.png'
        p = os.path.join(THEMESPATH, theme, bname)
        if not os.path.exists(p):
            p = DEFAULTTHEMESPATH
        else:
            p = os.path.join(THEMESPATH, theme)
        dicelist = glob.glob(os.path.join(p, 'dice*.png'))
        self._butdict = {}
        self._current_but = None
        self.UseDice = usebutton
        count = 1
        try:
            dicelist.sort()
            for diceimg in dicelist:
                but = ImgButton(diceimg, pos, name='Dice')
                but.connect_callback(cbf, MOUSEBUTTONDOWN, count)
                self._butdict[count] = but
                count += 1
        except StandardError, info:
            self.logger.exception("Can't load dice images for buttons: %s" % info)
            self.logger.error('Disable the dice')
            self._current_but = self._butdict[1]
            self.UseDice = False
    
    def set_minimal_level(self, level):
        self.logger.debug("Minimallevel set to %s" % level)
        self.minimallevel = level
        self.next_level(1)
        self.enable(False)

    def get_minimal_level(self):
        return self.minimallevel

    def next_level(self, level):
        self.logger.debug("level %s called" % level)
        if level == 0:
            self.logger.debug("level called with 0, set it to 1")
            level = 1
        if not self.UseDice:
            self.logger.debug("theme doesn't use dice")
            return 
        if self._current_but:
            self._current_but.erase_sprite()
            self.actives.remove(self._current_but)
        level = min(self.maxlevels, level + self.minimallevel - 1)
        self._current_but = self._butdict[level]
        self.actives.add(self._current_but)
        if self.showme:
            self._current_but.enable(True)
            self.show()
            
    def enable(self, enable):
        self.logger.debug("enable called with: %s" % enable)
        if not self.UseDice:
            self.logger.debug("theme doesn't use dice")
            return
        self._current_but.enable(enable)
    
    def erase(self):
        self.logger.debug("erase called")
        self._current_but.erase_sprite()
        self.showme = False
    def show(self):
        self.logger.debug("display called")
        self._current_but.display_sprite()
        self.showme = True

class StarButton(DiceButtons):
    """Special level indicator for the level indicator used by the braintrainer version.
    This uses a special dialog, SPWidgets.StarButtonsDialog.
    It derived the DiceButtons class so that the changes to the core are minimal."""
    def __init__(self, pos, actives, cbf, lock, usebutton=True, theme='seniorplay'):
        
        self.maxlevels = 6
        self.cbf = cbf
        self._current_but = None
        self.UseDice = usebutton
        
        self.minimallevel = 1
        self.lock = lock
        DiceButtons.__init__(self, pos, actives, cbf, usebutton=True)
        self.logger = logging.getLogger("schoolsplay.SPSpriteGui.StarButton")
    
    def _setup(self, theme, pos, actives, cbf, usebutton=True):
        self.imgstar0 = utils.load_image(os.path.join(THEMESPATH, theme,'star0.png'))
        self.imgstar1 = utils.load_image(os.path.join(THEMESPATH, theme,'star1.png'))
        self.rectstar = self.imgstar0.get_rect()
        #self.image = pygame.Surface((self.rectstar.w * self.maxlevels, self.rectstar.h))
        #self.image.fill(THEME['starbutton_bg_color'])
        self.image = pygame.Surface((self.rectstar.w * self.maxlevels, self.rectstar.h), SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        self.pos = pos
        self._set_level(1)
        
    def next_level(self, level):
        self.logger.debug("level %s called" % level)
        if level == 0:
            self.logger.debug("level called with 0, set it to 1")
            level = 1
        if not self.UseDice:
            self.logger.debug("theme doesn't use dice")
            return 
        self._set_level(level)
    
    def _start_dlg(self,sprite, event, data):
        self.lock.acquire()
        sbd = StarButtonsDialog(self.maxlevels, self.minimallevel)
        sbd.set_level(data[0])
        sbd.run()
        result = sbd.get_result()[0]
        if result:
            self._set_level(result- (self.minimallevel - 1))
            self.cbf(sprite, event, result - (self.minimallevel - 1))
        else:
            self.cbf(sprite, event, result)
        self.lock.release()

    def _set_level(self, level):
        self.logger.debug("_set_level called with: %s" % level)
        if self._current_but:
            self.actives.remove(self._current_but)
        x = 0
        level = min(self.maxlevels, level + self.minimallevel-1)
        for i in range(0, level):
            self.image.blit(self.imgstar1, (x, 0))
            x += self.rectstar.w
        for i in range(level, self.maxlevels):
            self.image.blit(self.imgstar0, (x, 0))
            x += self.rectstar.w
        self._current_but = TransImgButton(self.image, None, self.pos, name='Star')
        self._current_but.connect_callback(self._start_dlg, MOUSEBUTTONDOWN, level)
        self.actives.add(self._current_but)
        self.show()
        
class MenuBar:
    def __init__(self, rect, actives, cbf, dice_cbf,lock, usestar=False, usegraph=False):
        bname = 'core_info_button.png'
        hbname = 'core_info_button_ro.png'
        p = os.path.join(THEMESPATH, THEME['theme'],bname )
        hp = os.path.join(THEMESPATH, THEME['theme'],hbname )
        pos = (CORE_BUTTONS_XCOORDS[0], rect.top+8)
        if not os.path.exists(p):
            p = os.path.join(DEFAULTTHEMESPATH, bname)
        if not os.path.exists(hp):
            hp = None
        if hp:
            self.infobutton = TransImgButton(p, hp,pos, name='Info')
        else:
            self.infobutton = ImgButton(p, pos, name='Info')
        self.infobutton.connect_callback(cbf, MOUSEBUTTONDOWN, 'Info')
        
        bname = 'core_quit_button.png'
        hbname = 'core_quit_button_ro.png'
        p = os.path.join(THEMESPATH, THEME['theme'],bname )
        hp = os.path.join(THEMESPATH, THEME['theme'],hbname )
        pos = (CORE_BUTTONS_XCOORDS[8], rect.top+8)
        if not os.path.exists(p):
            p = os.path.join(DEFAULTTHEMESPATH, bname)
        if not os.path.exists(hp):
            hp = None
        if hp:
            self.quitbutton = TransImgButton(p, hp,pos, name='Quit')
        else:
            self.quitbutton = ImgButton(p, pos, name='Quit')
        self.quitbutton.connect_callback(cbf, MOUSEBUTTONDOWN, 'Quit')
        
        
        if usegraph:
            self.chartbutton = ChartButton((CORE_BUTTONS_XCOORDS[7], rect.top+8), cbf)
        else:
            self.chartbutton = None
        if usestar:
            self.dicebuttons = StarButton((CORE_BUTTONS_XCOORDS[1], rect.top+8), \
                                                        actives, dice_cbf, lock)
        else:
            self.dicebuttons = DiceButtons((CORE_BUTTONS_XCOORDS[3], rect.top+8),\
                                                        actives, dice_cbf)
        self.scoredisplay = ScoreDisplay((CORE_BUTTONS_XCOORDS[6], rect.top+8), cbf=cbf)
            
    def get_scoredisplay(self):
        return self.scoredisplay
    def get_infobutton(self):
        return self.infobutton
    def get_quitbutton(self):
        return self.quitbutton
    def get_chartbutton(self):
        return self.chartbutton
    def get_dicebuttons(self):
        return self.dicebuttons

class Graph(Widget):
    """provides a SDL surface with a graph plotted onto.
    The surface will be, x*y, 502x302 and will hold up to 20 values.
    This can only be used to display scores from schoolsplay.
    """
    def __init__(self, data, level, headertext='', norm=None):
        """@data must be a list with tuples (score,date).
        @norm is a tuple containing the mu and sigma value.
        """   
        # dates are stored like this: 07-09-09_10:44:27
        # the data list is a list with tuples like (mu,sigma,date)
        self.logger = logging.getLogger("schoolsplay.SPocwWidgets.Graph")
        # main surf is 500x300 the graph is a surf of 470x270.
        # 20 for the text bottom and left and 10 for a top and right offset
        gs = pygame.Surface((470, 270))# surf for the graph
        gs.fill((230, 230, 230))
        self.s = pygame.Surface((500, 400))# main surf
        self.s.fill((200, 200, 200))
        if not data:
            self.logger.warning("No data received to show in graph")
            ts = utils.char2surf(_("No data available for this level"), P_TTFSIZE + 8, ttf=P_TTF, split=35)
            y = 100
            for s in ts:
                self.s.blit(s, (20, y))
                y += s.get_height()
            SPSprite.__init__(self, self.s)
            return
        # border around the surf
        pygame.draw.rect(self.s, (100, 100, 100), self.s.get_rect().inflate(-1, -1), 2)
        
        # draw mu line and sigma deviation as a transparent box.
        if norm:
            mu, sigma = norm
            # line
            pygame.draw.line(gs, DARK_BLUE, (0, 270-mu * 27), (470, 270-mu * 27), 3)
            # deviation box, transparent blue
            top_y = mu + (mu / 100.0 * 30)
            bottom_y = mu - (mu / 100.0 * 30)
            darken = pygame.Surface((470, int((top_y-bottom_y) * 27)))
            darken.fill(BLUE)
            darken_factor = 64
            darken.set_alpha(darken_factor)
            gs.blit(darken, (0, 270-top_y * 27))
            
        # draw y-axes graph lines, initial y offset is 30 pixels to leave room for text.
        i = 10
        for y in range(0, 270, 27):
            pygame.draw.line(gs, (0, 0, 0), (0, y), (470, y), 1)
            ts = utils.char2surf(str(i), P_TTFSIZE-2, ttf=P_TTF, bold=True)
            i -= 1
            self.s.blit(ts, (4, y + 35))
        ts0 = utils.char2surf(headertext, P_TTFSIZE-2, ttf=P_TTF, bold=True)
        ts1 = utils.char2surf(_("Percentile scores for level %s") % level, P_TTFSIZE, ttf=P_TTF)
        self.s.blit(ts0, (10, 2))
        self.s.blit(ts1, (20, 20))
        
        # Draw x-axes data
        # determine the size of the x graph steps. This depends on the number of data items.
        # as we fill the x axe. Y step is always the same as the y axe values are always 0-10.
        # The maximum is 470 items, one pixel per data item.
        x_step = 470 / len(data)
        dotslist = []
        # draw dots and x-axes lines
        for x in range(0, 471-x_step, x_step):
            pygame.draw.line(gs, (0, 0, 0), (x, 270), (x, 0), 1)
            try:
                item = data.pop(0)
                #print item
                y = int(float(item[1]) * 27)
                #print "y position",y
                date = item[0]
                #print "date",date
            except (IndexError, TypeError):
                self.logger.exception("Troubles in the datalist, this shouldn't happen\n I try to continue but expect weird results :-)\n Traceback follows:")
                continue
            else:
                pygame.draw.circle(gs, DARK_BLUE, (x + 4, 270-y + 4), 4, 0)
                dotslist.append((x, 270-y))
                # blit date, rotated 90 degrees clockwise
                ts = utils.char2surf(date, P_TTFSIZE-5, ttf=P_TTF)
                # rotate 90 degrees
                v_ts = pygame.transform.rotate(ts, 270)
                self.s.blit(v_ts, (x + 20, 320))
        # connect the dots if there are more then one
        if len(dotslist) > 1:
            pygame.draw.lines(gs, BLUE, 0, dotslist, 2)
        pygame.draw.rect(gs, (0, 0, 0), gs.get_rect().inflate(-1, -1), 2)
        # finally blit the two surfaces
        self.s.blit(gs, (20, 40))
        SPSprite.__init__(self, self.s)
    
    def _calculate_position(self, pos):
        new_pos = pos# finish this
        return new_pos
    
    def get_surface(self):
        return self.image


class ExeCounter(Widget):
    # TODO: Finish this into a SPWidgets widget
    """Object that provides a, transparent, Pygame Surface that displays a simple 
    exercise counter in the form, done/todo.
    It uses two label objects for the display and provides some methods to 
    interact with these labels.
    The object places the labels in the menubar.
    """
    def __init__(self, pos, total, fsize=10, text=''):
        """The width of the widget is determined by the width of the headertext
        with a minimal width of four spaces and a maximum of fourteen characters.
        total - the total number of exercises.
        fsize - Fontsize for the text
        text - Headertext defaults to 'Exercises' (localized)
        """
        self.logger = logging.getLogger("schoolsplay.SPocwWidgets.ExeCounter")
        
        self.total = total
        self.done = 0
        if not text:
            text = _("Exercises")
        if len(text) > 14:#prevent to large label when localized
            text = text[:14]
        fgcol=THEME['execounter_fg_color']
        bgcol = THEME['execounter_bg_color']
        s0 = utils.char2surf(text, fsize=fsize, fcol=fgcol)
        txt = "%s/%s" % (self.done, self.total)
        
        self.lbl = Label(txt, (pos[0]+2, pos[1]+s0.get_height()), fsize=12, padding=4, border=0, fgcol=fgcol, bgcol=bgcol)
        
        r = pygame.Rect(0, 0,s0.get_rect().w+4, s0.get_rect().h +\
                                               self.lbl.rect.h+4)
        box, spam = get_boxes(bgcol, BLACK, r)
        
        box.blit(s0, (2, 2))
                
        SPSprite.__init__(self, box)
        self.rect.move_ip(pos)
        self.display_sprite()
        self.lbl.display_sprite()
    
    def increase_counter(self):
        """Increase the 'done' part of the counter.
        When the 'done' part is equal to the 'total' part no increase
        is performed."""
        if self.done == self.total:
            return
        self.done += 1
        text = "%s/%s" % (self.done, self.total)
        self.lbl.settext(text)
        self.lbl.display_sprite()
    
    def reset_counter(self, total):
        """Reset the total counter to @total.
        The 'done' part is reset to zero.
        """
        self.total = total
        self.done = -1
        self.increase_counter()
        
    
class ScoreDisplay(Label):
    """Displays a sore value of max 4 digits.
    It provides methods to set, increase, clear and return the scores."""
    def __init__(self, pos, score=0, cbf=None):
        self.scorestr = '%04d' % score
        # TODO: set fgcol and bgcol kwargs ?
        Label.__init__(self, self.scorestr, pos, fsize=20, padding=8, border=2)
        if cbf:
            self.connect_callback(cbf, MOUSEBUTTONDOWN, 'scoredisplay')
            # We disguise our selfs into a graphbutton
            self.name = 'Chart'
        else:
            self.name = 'ScoreDisplay'
    
    def set_score(self, score=0):
        if score < 0:
            return
        if score > 9999:
            score = 9999
        self.scorestr = '%04d' % score
        self.settext(self.scorestr)
        self.display_sprite()
    
    def increase_score(self, score):
        if score < 0:
            return
        if int(self.scorestr) + score > 9999:
            score = 0
        self.scorestr = '%04d' % (int(self.scorestr) + int(score))
        self.settext(self.scorestr)
        self.display_sprite()
        
    def clear_score(self):
        self.scorestr = '0000'
        self.settext('0000')
        self.display_sprite()
        
    def return_score(self):
        return int(self.scorestr)

class VolumeAdjust:
    """Widget that provides a volume change widget with on both ends a small button
    to increase or decrease the volume level and in the middle a percentage display.
    """
    def __init__(self, pos, volume=None, defval=50):
        """defval - value between 0, silent, and 100, maximum, volume level."""
        self.logger = logging.getLogger("schoolsplay.SPWidgets.VolumeAdjust")
        self.soundcheck = utils.load_sound(os.path.join(ACTIVITYDATADIR, 'CPData','volumecheck.wav'))
        self.theme = THEME['theme']
        if volume:
            self.volume = volume
        elif WEHAVEAUMIX:
            self.volume = WEHAVEAUMIX
        else:
            self.volume = defval
        self.volstr = '%02d' % self.volume + "%"
        # TODO: set fgcol and bgcol kwargs ?
        self.lbl = Label(self.volstr, pos, fsize=20, padding=4, border=1, minh=56)
        imgup = utils.load_image(os.path.join(THEMESPATH, self.theme,'volup.png'))
        imgdown = utils.load_image(os.path.join(THEMESPATH, self.theme,'voldown.png'))
        px, py = pos
        
        self.voldownbut = ImgButtonRound(imgdown)
        self.voldownbut.moveto((px, py))
        self.voldownbut.connect_callback(self._cbf, MOUSEBUTTONDOWN, -5)
        
        px += self.voldownbut.rect.w
        self.lbl.moveto((px , py))
        px += self.lbl.rect.w
        
        self.volupbut = ImgButtonRound(imgup)
        self.volupbut.moveto((px, py))
        self.volupbut.connect_callback(self._cbf, MOUSEBUTTONDOWN, 5)
    
    def set_use_current_background(self, bool):
        self.voldownbut.set_use_current_background(bool)
        self.volupbut.set_use_current_background(bool)

    def _cbf(self, widget, event, data):
        if self.volume >= 95 and data[0] > 0:
            return
        if self.volume <=5 and data[0] < 0:
            return
        self.volume += data[0]
        self.volstr = '%02d' % self.volume + "%"
        self.lbl.settext(self.volstr)
        self.lbl.display_sprite()
        self.logger.debug("Volume set to %s" % self.volstr)
        #Here we set the actual volume (We do this with aumix)
        if WEHAVEAUMIX:
            output=os.popen('aumix -q').readlines()
            if len(output)==1: 
                os.system('aumix -w' + str(self.volume) +' -S')
            else: 
                os.system('aumix -v' + str(self.volume) +' -S')
            self.soundcheck.play()
        else:
            self.logger.warning("Not possible to set volume level")
        

    def display(self):
        self.voldownbut.display_sprite()
        self.volupbut.display_sprite()
        self.lbl.display_sprite()
    
    def hide(self):
        self.voldownbut.erase_sprite()
        self.volupbut.erase_sprite()
        self.lbl.erase_sprite()
    
    def get_actives(self):
        return [self.voldownbut, self.volupbut, self.lbl]
        
    def get_volume(self):
        return self.volume

def make_button_bg(size):
    left = BUT_LEFT.convert_alpha()
    right = BUT_RIGHT.convert_alpha()
    center = BUT_CENTER.convert_alpha()
    hleft = BUTH_LEFT.convert_alpha()
    hright = BUTH_RIGHT.convert_alpha()
    hcenter = BUTH_CENTER.convert_alpha()
    if size[1] > center.get_rect().h:
        module_logger.warning("Button background image is smaller %s than requested button height %s" % (center.get_rect().h, size[1]))

    
    offset = left.get_rect().w 
    hight = left.get_rect().h
    x = size[0]
    but = pygame.Surface((4+size[0] + offset * 2, 4+hight), SRCALPHA)
    buthov = pygame.Surface((4+size[0] + offset * 2, 4+hight), SRCALPHA)
    newcenter = pygame.transform.scale(center, (x, center.get_rect().h))
    hnewcenter = pygame.transform.scale(hcenter, (x, center.get_rect().h))
    but.blit(newcenter, (offset, 2))
    buthov.blit(hnewcenter, (offset, 2))
    offset += newcenter.get_rect().w
    
    but.blit(left, (2, 2))
    buthov.blit(hleft, (2, 2))

    but.blit(right, (offset, 2))
    buthov.blit(hright, (offset, 2))
    return (but, buthov)
        
def grey_it(img):
    red       = False
    green     = True
    blue      = False
    
    for x in range(img.get_width()):
        for y in range(img.get_height()):
            c = list(img.get_at((x,y))[:3])
            deg = (c[0]*red + c[1]*green + c[2]*blue) / (red + green + blue)
            img.fill( [deg]*3, ((x,y),(1,1)) )
    return img


def get_boxes(color, hover_color, rect, selected_color=None):
    """Draws rectangles for the buttons and dialogs."""
    s = pygame.Surface((rect.w, rect.h))
    s_hover = s.convert()
    pygame.draw.rect(s, color, rect, 0)
    hcolor = []
    rect.move_ip(-1, -1)
    for c in color:
        if c > 80:
            c -= 70
        elif c < 180:
            c +=70
        hcolor.append(c)
    h_color = tuple(hcolor)
    pygame.draw.rect(s, h_color, rect, 2)
    
    s_hover.fill(hover_color)
    hcolor = []
    for c in color:
        if c > 80:
            c -= 70
        elif c < 180:
            c += 70
        hcolor.append(c)
    h_color = tuple(hcolor)
    pygame.draw.rect(s_hover, hcolor, rect, 2)
    if selected_color:
        hcolor = []
        s_select = s_hover.convert()
        s_select.fill(selected_color)
        for c in color:
            if c > 80:
                c -= 70
            elif c < 180:
                c += 70
            hcolor.append(c)
        h_color = tuple(hcolor)
        pygame.draw.rect(s_select, hcolor, rect, 2)
        return (s, s_hover, s_select)
    return (s, s_hover)

def render_textrect(string, fsize, family, rect, text_color, background_color,\
                    justification=0, autofit=False, border=False, padding=8, bold=False):
    """Returns a surface containing the passed text string, reformatted
    to fit within the given rect, word-wrapping as necessary. The text
    will be anti-aliased.

    Takes the following arguments:

    string - the text you wish to render. \n begins a new line.
    font - a Font object
    rect - a rectstyle giving the size of the surface requested.
            If a pygame.Surface is given iso a rect the surface is used to blit the text to.
    text_color - a three-byte tuple of the rgb value of the
                 text color. ex (0, 0, 0) = BLACK
    background_color - a three-byte tuple of the rgb value of the surface.
    justification - 0 (default) left-justifiedSPWidgets.py
                    1 horizontally centered
                    2 right-justified
    autofit - When True any space left at the bottom of the surface will be discarded.
    border - A border is drawn around the surface.blit
    padding - Space around the text.
    Returns the following values:
    Success - a surface object with the text rendered onto it.
    Failure - raises a TextRectException if the text won't fit onto the surface.
    """
    final_lines = []
    requested_lines = string.splitlines()
    if NoGtk:
        font = pygame.font.Font(TTF, fsize)
    else:
        font = utils.pangofont.PangoFont(family=family, size=fsize, bold=bold)
    if type(rect) is not pygame.Rect:
        # we assume a surface
        if rect.get_alpha():
            surface = rect.convert_alpha()
        else:
            surface = rect.convert()
        rect = rect.get_rect()
    else:
        surface = pygame.Surface(rect.size)
        surface.fill(background_color)
    # Create a series of lines that will fit on the provided
    # rectangle.
    # we keep an padding on both sides
    for requested_line in requested_lines:
        if font.size(requested_line)[0] > (rect.width - padding*2):
            words = requested_line.split(' ')
            # if any of our words are too long to fit, return.
#            for word in words:
#                if font.size(word)[0] >= rect.width-16:
#                    raise TextRectException, "The word " + word + " is too long to fit in the rect passed."
            # Start a new line
            accumulated_line = ""
            for word in words:
                test_line = accumulated_line + word + " "
                # Build the line while the words fit.    
                if font.size(test_line)[0] < rect.width-padding*2:
                    accumulated_line = test_line
                else:
                    final_lines.append(accumulated_line)
                    accumulated_line = word + " "
            final_lines.append(accumulated_line)
        else:
            final_lines.append(requested_line)

    
        
    accumulated_height = 0
    for line in final_lines:
#        if accumulated_height + font.size(line)[1] >= rect.height:
#            raise TextRectException, "Once word-wrapped, the text string was too tall to fit in the rect."
        if line != "":
            tempsurface = font.render(line, 1, text_color)
            if justification == 0:
                surface.blit(tempsurface, (8, accumulated_height+8))
            elif justification == 1:
                surface.blit(tempsurface, ((rect.width-16 - tempsurface.get_width()) / 2, accumulated_height+8))
            elif justification == 2:
                surface.blit(tempsurface, (rect.width-16 - tempsurface.get_width(), accumulated_height+8))
#            else:
#                raise TextRectException, "Invalid justification argument: " + str(justification)
        accumulated_height += font.size(line)[1]
    if autofit:
        s = pygame.Surface((rect.w, accumulated_height+16))
        s.fill(background_color)
        s.blit(surface, (0, 0))
        surface = s
    if border:
        pygame.draw.rect(surface, (0, 0, 0), surface.get_rect().inflate(-1, -1), 1)
    return surface

if __name__ == '__main__':
    
    import __builtin__
    __builtin__.__dict__['_'] = lambda x:x
    
    import SPLogging
    SPLogging.set_level('debug')
    SPLogging.start()
        
    import pygame
    from pygame.constants import *
    pygame.init()
    
    from SPSpriteUtils import SPInit
    
    def cbf(sprite, event, data):
        print 'cb called with sprite %s, event %s and data %s' % (sprite, event, data)
        print 'sprite name: %s' % sprite.get_name()
        print 'data is %s' % data
    
    scr = pygame.display.set_mode((800, 600))
    scr.fill((250, 250, 250))
    pygame.display.flip()
    back = scr.convert()
    actives = SPInit(scr, back)
    
    Init('seniorplay')
    
    but = Button('Button', (10, 80), padding=6)
    but.connect_callback(cbf, MOUSEBUTTONDOWN, 'Button')
    lbl = Label('Hit escape key to continue', (10, 130))
    r = pygame.Rect(0, 0, 500, 240)
    txt = "This program is free software; you can redistribute it and/or modify it under the terms of version 3 of the GNU General Public License as published by the Free Software Foundation.  A copy of this license should be included in the file GPL-3."
    
    tv = TextView(txt, (290, 180), r, autofit=True, border=True)
    tv.display_sprite()
    
    va = VolumeAdjust((200, 20))
    va.display()
    
    pnb = PrevNextButton((150, 180), cbf)
        
    actives.add([but, lbl, va.get_actives(), pnb.get_actives()])
    for s in actives:
        s.display_sprite()
    
    
#    ec = ExeCounter((600, 10), 20)
#    ec.display_sprite()
    
    runloop = 1 
    while runloop:
        pygame.time.wait(100)
        pygame.event.pump()
        events = pygame.event.get()
        for event in events:
            if event.type is KEYDOWN:
                if event.key == K_ESCAPE:
                    runloop = 0
                elif event.key == K_F1:
                    but.enable(False)
                    print "button disabled"
                elif event.key == K_F2:
                    but.enable(True)
                    print "button enabled"
                elif event.key == K_F3:
                    pnb.toggle()
                    print "prevnext toggled"
            else:
                actives.update(event)
                
    txt = 'Dialog with two buttons and some more text, whatever that might be'
    dlg = Dialog(txt, (10, 400), \
                 buttons=["Cancel", "OK"], title='Information')
    dlg.run()                
    print "result", dlg.get_result()
    dlg.erase_sprite()
        
    box = TextEntry((500, 500), 12, "Input:")
    print "You entered", box.ask()
    
    
