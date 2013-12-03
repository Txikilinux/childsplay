#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2010-2011 Stas Zykiewicz <stas.zytkiewicz@schoolsplay.org>
#
#           buttons.py
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

import utils
import types
import glob
import pygame
from pygame.constants import *
from base import Widget
from SPConstants import *
from text import Label
from funcs import get_boxes, make_button_bg_dynamic
from SPSpriteUtils import SPSprite, SPGroup

class RadioButton(Widget):
    """Radiobuttons are buttons that has two states, selected or not selected.
    The differences with other 'state' buttons is that these buttons are usually 
    grouped so that only one can be selected at a time."""
    def __init__(self, group, text, pos, fsize=18, padding=8, name='', **kwargs):
        """Radiobutton with a optional text label.
        group - the widget to which this button belongs. (must be None or another radiobutton)
        text - string to display
        pos - position to display the box
        fsize - Font size
        padding - space in pixels around the text
        name - string to indicate this object
        kwargs - bgcol, fgcol
        """
        self.box_pos = pos
        self.image_pos = (pos[0]+1, pos[1]+1)
        self.name = name
        
        if not group:
            self._rb_group = [self]
        else:
            self._rb_group = group._rb_group + [self]
            for rb in self._rb_group:
                rb._rb_group = self._rb_group
        self._rb_selected = False
        box = pygame.Surface((18, 18))
        box.fill(WHITE)
        rect = box.get_rect()
        lbl = Label(text, (pos[0] + 10 + rect.width, pos[1]), fsize=18, transparent=True, \
                            fgcol=WHITE, bold=True)
        lbl.display_sprite()
        pygame.draw.line(box, GREY30, (0, 0), (18, 0), 1)
        pygame.draw.line(box, GREY30, (0, 0), (0, 18), 1)
        pygame.draw.line(box, GREY30, (17, 0), (17, 17), 1)
        pygame.draw.line(box, GREY30, (1, 17), (17, 17), 1)
        self.box = box.convert()
        Widget.__init__(self, box, name=name)
        self.selected_image = utils.load_image(os.path.join(self.THEME['defaultpath'], 'radiobut_selected.png'))
        self.moveto(self.box_pos)
        self.connect_callback(self._cbf_on_select, MOUSEBUTTONUP)
    
    def _rb_select(self):
        print 'selecting:', self.name
        self.image = self.selected_image
        self.moveto(self.image_pos)
        self._rb_selected = True
        self.display_sprite()
    
    def _rb_unselect(self):
        print 'unselecting:', self.name
        self.image = self.box
        self.moveto(self.box_pos)
        self._rb_selected = False
        self.display_sprite()
    
    def _cbf_on_select(self, *args):
        print "_cbf %s: selection = %s" % (self.name, self._rb_selected)
        if self._rb_selected:
            self._rb_unselect()
        else:
            for rb in self._rb_group:
                if not rb is self:
                    rb._rb_unselect()
            self._rb_select()
            
    def get_selected_name(self):
        for rb in self._rb_group:
            if rb._rb_selected:
                return rb.name
        return ''
        
    def get_group(self):
        return self._rb_group

class Button(Widget):
    def __init__(self, txt, pos=(0, 0), fsize=18, padding=4, name='', fbold=True, **kwargs):
        """Button which shows a text
        txt - string to display
        pos - position to display the box
        fsize - Font size
        padding - space in pixels around the text
        name - string to indicate this object
        kwargs - bgcol, fgcol
        """
        Widget.__init__(self)
        if kwargs.has_key('fgcol'):
            fgcol = kwargs['fgcol']
        else:
            fgcol = self.THEME['button_fg_color']
        self.kwargs = kwargs
        self.ImSelected = False
        if type(txt) in (types.StringType, types.UnicodeType):
            s = utils.char2surf(txt, fcol=fgcol, fsize=fsize, ttf=TTF, bold=fbold)
            r = s.get_rect()
            r.w += padding*2
            r.h += padding*2
        else:
            s = txt
            r = s.get_rect()
            r.w += padding*2
            r.h += padding*2
        if kwargs.has_key('maxlength') and r.w > kwargs['maxlength']:
            r.w = kwargs['maxlength']
        self.pos = pos
        self.padding = padding
        self.name = name
        self.r = r
        self._setup(s)
        
    def _setup(self, s):
        if self.kwargs.has_key('bgcol'):
            bgcol = self.kwargs['bgcol']
        else:
            bgcol = self.THEME['button_bg_color']
        self._but, self._but_hover, self._but_selected = get_boxes(\
                                                bgcol,\
                                                self.THEME['button_color_hover'],\
                                                self.r, \
                                                self.THEME['button_selected_color'])

        self._but.blit(s, (self.padding, self.padding))
        self._but_hover.blit(s, (self.padding, self.padding))
        self._but_selected.blit(s, (self.padding, self.padding))
        self.image = self._but
        self.rect  = self.image.get_rect()
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
    def __init__(self, path, pos=(0, 0),padding=4, name='', **kwargs):
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

class ImgTextButton(ImgButton):
    def __init__(self, path, text, pos=(0, 0), textpos=2, padding=4, fsize=24,\
                  fgcol=BLACK, name='', **kwargs):
        """Button which shows an image with text.
        path - must be the path to the image file or a pygame surface
        pos - position to display the box
        rect - Rect indicating the size of the box
        padding - space in pixels around the text
        name - string to indicate this object
        text - text to display. String will be split on \n.
        textpos - position of the text, 1 means left from the image, 2 means right from the image
        """
        if type(path) in types.StringTypes:
            image = utils.load_image(path)
        else:
            image = path
        surflist = []
        for line in text.split('\n'):
            if line == '':
                line = ' '
            surflist.append(utils.char2surf(line, fcol=fgcol, fsize=fsize, ttf=TTF))
        w = max([s.get_width() for s in surflist])
        h = surflist[0].get_height() 
        totalh = h * len(surflist)
        textsurf = pygame.Surface((w, totalh), SRCALPHA)
        y = 0
        for s in surflist:
            textsurf.blit(s, (0, y))
            y += h
        w = image.get_width() + w + padding * 2
        h = max(image.get_height(),  totalh)
        surf = pygame.Surface((w, h), SRCALPHA)
        image_y = (surf.get_height() - image.get_height()) / 2
        text_y = (surf.get_height() - textsurf.get_height()) / 2 
        if textpos == 1:
            surf.blit(textsurf, (0, text_y))
            surf.blit(image, (textsurf.get_width() + padding, image_y))
        else:
            surf.blit(image, (0, image_y))
            surf.blit(textsurf, (image.get_width() + padding, text_y))
        ImgButton.__init__(self, surf, pos, padding=padding, name=name)


class TransImgButton(ImgButton):
    def __init__(self, path, hpath, pos=(0, 0), padding=4,text='',fsize=24, fcol=BLACK, name='', **kwargs):
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

class TransImgTextButton(TransImgButton):
    def __init__(self, path, hpath, text, pos=(0, 0), textpos=2, padding=4, fsize=24,\
                  fgcol=BLACK, name='', **kwargs):
        """Button which shows an image and text.
        path - must be the path to the image file.
        hpath - 'rollover' image path.
        pos - position to display the box
        rect - Rect indicating the size of the box
        padding - space in pixels around the text
        name - string to indicate this object
        text - text to display. String will be split on \n.
        textpos - position of the text, 1 means left from the image, 2 means right from the image
        """
        image = utils.load_image(path)
        imageh = utils.load_image(hpath)
        surflist = []
        surfhlist = []
        for line in text.split('\n'):
            if line == '':
                line = ' '
            surflist.append(utils.char2surf(line, fcol=fgcol, fsize=fsize, ttf=TTF))
            surfhlist.append(utils.char2surf(line, fcol=GREY, fsize=fsize, ttf=TTF))
        w = max([s.get_width() for s in surflist])
        h = surflist[0].get_height() 
        totalh = h * len(surflist)
        textsurf = pygame.Surface((w, totalh), SRCALPHA)
        y = 0
        for s in surflist:
            textsurf.blit(s, (0, y))
            y += h
        textsurf_h = pygame.Surface((w, totalh), SRCALPHA)
        y = 0
        for s in surfhlist:
            textsurf_h.blit(s, (0, y))
            y += h
        w = image.get_width() + w + padding * 2
        h = max(image.get_height(),  totalh)
        surf = pygame.Surface((w, h), SRCALPHA)
        hsurf = surf.copy()
        image_y = (surf.get_height() - image.get_height()) / 2
        text_y = (surf.get_height() - textsurf.get_height()) / 2
        if textpos == 1:
            surf.blit(textsurf, (0, text_y))
            surf.blit(image, (textsurf.get_width() + padding, image_y))
            hsurf.blit(textsurf_h, (0, text_y))
            hsurf.blit(imageh, (textsurf_h.get_width() + padding, image_y))
        else:
            surf.blit(image, (0, image_y))
            surf.blit(textsurf, (image.get_width() + padding, text_y))
            hsurf.blit(imageh, (0, image_y))
            hsurf.blit(textsurf_h, (imageh.get_width() + padding, text_y))
        
        TransImgButton.__init__(self, surf, hsurf, pos=pos, padding=padding, \
                                    fsize=fsize, fcol=fgcol, name=name)

class ButtonDynamic(Button):
    def __init__(self, txt, pos=(0, 0), fsize=18, bold=False, padding=8, name='', \
                 length=None, colorname='blue', sizename='54px', fgcol=WHITE, **kwargs):
        """Button which shows a text on a background with round corners.
        txt - string to display
        pos - position to display the box
        fsize - Font size
        padding - space in pixels around the text
        sizename - name for the kind of image set to use.
            supported size names are: '36px','54px','81px'.
        name - string to indicate this object
        kwargs - bgcol, fgcol
        """
        self.colorname = colorname
        self.sizename = sizename
        self.padding = padding
        self.kwargs = kwargs
        Button.__init__(self, txt,pos=pos, fsize=fsize, padding=padding, name=name, fbold=bold, fgcol=fgcol,**kwargs)
        
    def _setup(self, s):
        self._but, self._but_hover = make_button_bg_dynamic(self.r.width + self.padding*2, \
                                                            self.sizename, \
                                                            self.colorname,\
                                                            colorname_ro='black',\
                                                            THEME=self.THEME)
        r = self._but.get_rect()
        size = r.size
        sr = s.get_rect()
        sr.center = r.center
                
        self._but.blit(s, sr)
        self._but_hover.blit(s, sr)
        self.image = self._but
        self.rect  = self.image.get_rect()
        SPSprite.__init__(self, self.image, name=self.name)
        self.rect.move_ip(self.pos)

class ImgButtonDynamic(ButtonDynamic):
    def __init__(self, path, pos=(0, 0),padding=4, name='', \
                 length=None, colorname='blue', sizename='54px', **kwargs):
        """Button which shows an image on a background with round corners.
        path - must be the path to the image file or a pygame surface
        pos - position to display the box
        rect - Rect indicating the size of the box
        padding - space in pixels around the text
        sizename - name for the kind of image set to use.
            supported size names are: '36px','54px','81px'.
        name - string to indicate this object
        """
        if type(path) in types.StringTypes:
            image = utils.load_image(path)
        else:
            image = path
        ButtonDynamic.__init__(self, image, pos, None, padding=padding, name=name, \
                             length=length, colorname=colorname, sizename=sizename)

class SimpleButton(Button):
    """Button which shows a text and returns the value given by 'data'
        when a MOUSEBUTTONUP event occurs.
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
        self.connect_callback(self._cbf, MOUSEBUTTONUP)
        self.data = data
        
    def _cbf(self, *args):
        return (self.data, )
        
class SimpleButtonDynamic(ButtonDynamic):
    """Button which extends ButtonDynamic and returns the value given by 'data'
        when a MOUSEBUTTONUP event occurs.
        This differs from a normal ButtonDynamic which should be connect a 
        function."""
    def __init__(self, txt, pos=(0, 0), fsize=18, padding=4, data=True, \
                 length=None, colorname='blue', sizename='54px', fgcol=WHITE,**kwargs):
        ButtonDynamic.__init__(self, txt, pos, fsize, padding, fgcol=fgcol, \
                             length=length, colorname=colorname, sizename=sizename)
        self.connect_callback(self._cbf, MOUSEBUTTONUP)
        self.data = data
    def _cbf(self, *args):
        return (self.data, )

class SimpleTransImgButton(TransImgButton):
    """Button which extends TransImgButton and returns the value given by 'data'
        when a MOUSEBUTTONUP event occurs.
        This differs from a normal TransImgButton which should be connect a 
        function."""
    def __init__(self, path, hpath, pos=(0, 0), padding=4,text='',fsize=24, fcol=BLACK,\
                  data=True, **kwargs):
        TransImgButton.__init__(self, path, hpath, pos, padding,text,fsize, fcol)
        self.connect_callback(self._cbf, MOUSEBUTTONUP)
        self.data = data
    def _cbf(self, *args):
        return (self.data, )    

class PrevNextButton:
    """Button that can switch between two images in a toggle like fashion.
    The data returnt to the callback function is also changed when the button
    image is changed"""
    def __init__(self, pos, cbf, prevname, nextname, states=['prev','next']):
        self.pos = pos
        self._cbf = cbf
        self.prevname = prevname
        self.nextname = nextname
        self._setup()
        
    def _setup(self):
        pp = self.prevname
        np = self.nextname
        self.state = self.states[0]

        previmg = utils.load_image(pp)
        self.nextimg = utils.load_image(np)
        self.but = ImgButton(previmg, self.pos, name='prevnext')
        self.previmg = self.but._but.convert_alpha()# image is now blitted on a button surface
        self.previmg_hover = self.but._but_hover.convert_alpha()
        self.current = self.previmg
        
        temp = ImgButton(self.nextimg, self.pos, name='prevnext')
        self.nextimg = temp._but.convert_alpha()
        self.nextimg_hover = temp._but_hover.convert_alpha()
        self.rect = self.nextimg.get_rect()
        self.but.connect_callback(self._cbf, MOUSEBUTTONUP, self.states[1])
    
    def get_actives(self):
        return self.but
    
    def toggle(self):
        """When called the button switch images."""
        if self.current is self.previmg:
            self.current = self.nextimg
            self.but._but = self.nextimg
            self.but._but_hover = self.nextimg_hover
            self.state = self.states[1]
            self.but.connect_callback(self._cbf, MOUSEBUTTONUP, self.states[1])
        else:
            self.current = self.previmg
            self.but._but = self.previmg
            self.but._but_hover = self.previmg_hover
            self.state = self.states[0]
            self.but.connect_callback(self._cbf, MOUSEBUTTONUP, self.states[0])
        self.but.mouse_hover_leave()

    def get_state(self):
        return self.state

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
    def __init__(self, pos, cbf, prevname, hprevname, nextname, hnextname, states=['prev','next']):
        self._cbf = cbf
        self.pos = pos
        self.prevname = prevname
        self.hprevname = hprevname
        self.nextname = nextname
        self.hnextname = hnextname
        self.states = states
        PrevNextButton.__init__(self, pos, cbf, prevname, nextname)
                
    def _setup(self):
        self.state = self.states[0]
        pp =  self.prevname
        hpp =  self.hprevname
        np = self.nextname
        hnp = self.hnextname
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
        self.rect = self.nextimg.get_rect()
        self.but.connect_callback(self._cbf, MOUSEBUTTONUP, self.states[1])
        

class ChartButton(ImgButton):
    def __init__(self, pos, cbf):
        bname = 'core_chart_button.png'
        p = os.path.join(self.THEMESPATH, self.THEME['self.THEME'], bname)
        if not os.path.exists(p):
            p = os.path.join(DEFAULTTHEMESPATH, bname)
        ImgButton.__init__(self, p, pos, name='Chart')
        self.connect_callback(cbf, MOUSEBUTTONUP, 'Chart')
    
class DiceButtons(Widget):
    def __init__(self, pos, actives, cbf, usebutton=True):
        Widget.__init__(self)
        self.logger = logging.getLogger("childsplay.SPSpriteGui.DiceButtons")
        self.actives = actives
        self.theme = self.THEME['theme']
        self.minimallevel = 1
        self.maxlevels = 6
        self._isenabled = True
        self._setup(self.theme, pos, actives, cbf, usebutton=True)
        self.showme = True
        
    def _setup(self, THEME, pos, actives, cbf, usebutton=True):
        bname = 'dice-1.png'
        p = os.path.join(self.THEMESPATH, self.theme, bname)
        if not os.path.exists(p):
            p = DEFAULTTHEMESPATH
        else:
            p = os.path.join(self.THEMESPATH, self.theme)
        dicelist = glob.glob(os.path.join(p, 'dice*.png'))
        self._butdict = {}
        self._current_but = None
        self.UseDice = usebutton
        count = 1
        try:
            dicelist.sort()
            for diceimg in dicelist:
                but = ImgButton(diceimg, pos, name='Dice')
                but.connect_callback(cbf, MOUSEBUTTONUP, count)
                self._butdict[count] = but
                count += 1
        except StandardError, info:
            self.logger.exception("Can't load dice images for buttons: %s" % info)
            self.logger.error('Disable the dice')
            self._current_but = self._butdict[1]
            self.UseDice = False
    
    def isenabled(self):
        return self._isenabled
    
    def set_minimal_level(self, level):
        self.logger.debug("Minimallevel set to %s" % level)
        self.minimallevel = level
        self.next_level(1)

    def get_minimal_level(self):
        return self.minimallevel

    def next_level(self, level):
        self.logger.debug("level %s called" % level)
        if level == 0:
            self.logger.debug("level called with 0, set it to 1")
            level = 1
#        if not self.UseDice:
#            self.logger.debug("self.theme doesn't use dice")
#            return 
        if self._current_but:
            self._current_but.erase_sprite()
            self.actives.remove(self._current_but)
        level = min(self.maxlevels, level + self.minimallevel - 1)
        self._current_but = self._butdict[level]
        self.actives.add(self._current_but)
        if self._isenabled:
            self.actives.add(self._current_but)
            self._current_but.enable(True)
        self.show()
            
    def enable(self, enable):
        self.logger.debug("enable called with: %s" % enable)
        if not self.UseDice:
            self.logger.debug("self.theme doesn't use dice")
            return
        self._current_but.enable(enable)
        self._isenabled = enable
    
    def erase(self):
        self.logger.debug("erase called")
        if not self.UseDice:
            self.logger.debug("self.theme doesn't use dice")
            return
        self._current_but.erase_sprite()
        self.showme = False
        
    def show(self):
#        if not self._isenabled:
#            return
        self.logger.debug("display called")
        if not self.UseDice:
            self.logger.debug("self.theme doesn't use dice")
            return
        self._current_but.display_sprite()
        self.showme = True

class StarButton(DiceButtons):
    """Special level indicator for the level indicator used by the braintrainer version.
    This uses a special dialog, SPWidgets.StarButtonsDialog.
    It derived from the DiceButtons class so that the changes to the core are minimal."""
    def __init__(self, pos, actives, cbf, lock, usebutton=True, THEME='seniorplay'):
        self.maxlevels = 6
        self.cbf = cbf
        self._current_but = None
        self.UseDice = usebutton
        
        self.minimallevel = 1
        self.lock = lock
        DiceButtons.__init__(self, pos, actives, cbf, usebutton=True)
        self.logger = logging.getLogger("childsplay.SPSpriteGui.StarButton")
    
    def _setup(self, THEME, pos, actives, cbf, usebutton=True):
        self.imgstar0 = utils.load_image(os.path.join(THEMESPATH, self.theme,'star0.png'))
        self.imgstar1 = utils.load_image(os.path.join(THEMESPATH, self.theme,'star1.png'))
        self.rectstar = self.imgstar0.get_rect()
        #self.image = pygame.Surface((self.rectstar.w * self.maxlevels, self.rectstar.h))
        #self.image.fill(self.THEME['starbutton_bg_color'])
        self.image = pygame.Surface((self.rectstar.w * self.maxlevels, self.rectstar.h), SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        self.pos = pos
        self._set_level(1)
        
    def next_level(self, level):
        self.logger.debug("level %s called" % level)
        if level == 0:
            self.logger.debug("level called with 0, set it to 1")
            level = 1
        if not self.UseDice :
            self.logger.debug("THEME doesn't use dice")
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
        if level < self.minimallevel:
            level = self.minimallevel
        for i in range(0, level):
            self.image.blit(self.imgstar1, (x, 0))
            x += self.rectstar.w
        for i in range(level, self.maxlevels):
            self.image.blit(self.imgstar0, (x, 0))
            x += self.rectstar.w
        self._current_but = TransImgButton(self.image, None, self.pos, name='Star')
        if self._isenabled:
            self._current_but.connect_callback(self._start_dlg, MOUSEBUTTONUP, level)
            self.actives.add(self._current_but)
        self.show()
        
class StarButtonsDialog(Widget):
    """Special dialog with a level indicator used by the braintrainer version.
    This is intended to be controlled by the SPSpriteGui.StarButtons object"""
    def __init__(self, maxlevels, start_level):
        Widget.__init__(self)
        self.theme = self.THEME['theme']
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
        self.dim.dim(darken_factor=self.THEME['starbuttonsdialog_darkenfactor'], color_filter=self.THEME['starbuttonsdialog_dim_color'])
        x = 40
        y = 200
        for i in range(self.maxlevels):
            b = SPSprite(self.imgstar0)
            b.moveto((x, y), hide=True)
            b.connect_callback(self.cbf, MOUSEBUTTONUP, i+1)
            self.starlist.append(b)
            x += self.imgstar0.get_width()
        # set first star to active
        self.starlist[0].image = self.imgstar1
        self.actives.add(self.starlist)
        
        self.buttons_list = []
        x = 100
        y = 400
        
        for buttxt in [_("Cancel"), _("OK")]:
            b = Button(buttxt, (x, y), fsize=self.THEME['starbuttonsdialog_fsize'], name=buttxt)
            b.connect_callback(self.but_cbf, MOUSEBUTTONUP, buttxt)
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
