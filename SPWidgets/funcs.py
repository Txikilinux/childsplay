#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2010-2011 Stas Zykiewicz <stas.zytkiewicz@schoolsplay.org>
#
#           funcs.py
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

if __name__ == '__main__':
    import sys
    sys.path.insert(0,'..')
import subprocess
import utils
import pygame
from pygame.constants import *
from SPConstants import TTF, NoGtk

def detect_keyboard():
    process = subprocess.Popen(['lsusb -v | grep "Keyboard"'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    txt = list(process.communicate())
    for line in txt[0].split('/n'):
        if "Keyboard" in line or "keyboard" in line:
            return True
    return False


def make_button_bg_dynamic(width, sizename, colorname, colorname_ro='black', THEME={}):
    """width - integer for the total length of the button images.
    sizename - name for the kind of image set to use.
    supported size names are: '36px','54px','81px'.
    colorname - name for the color to use.
    colorname_ro - name for the 'rollover' color to use.
    Supported colornames are: 'black', 'blue', 'green'.
    When a name isn't found a Exception is raised."""
    try:
        left = utils.load_image(os.path.join(THEME['themepath'], "%s_%s_%s.png" % (sizename, 'left', colorname)))
        right = utils.load_image(os.path.join(THEME['themepath'], "%s_%s_%s.png" % (sizename, 'right', colorname)))
        center = utils.load_image(os.path.join(THEME['themepath'], "%s_%s_%s.png" % (sizename, 'center', colorname)))
        hleft = utils.load_image(os.path.join(THEME['themepath'], "%s_%s_%s.png" % (sizename, 'left', colorname_ro)))
        hright = utils.load_image(os.path.join(THEME['themepath'], "%s_%s_%s.png" % (sizename, 'right', colorname_ro)))
        hcenter = utils.load_image(os.path.join(THEME['themepath'], "%s_%s_%s.png" % (sizename, 'center', colorname_ro)))
    except IOError, info:
        raise Exception, info
    partwidth = left.get_rect().w 
    hight = left.get_rect().h
    x = width - partwidth*2
    if x < 1:
        x = 1
        width = partwidth *2 +1
    
    but = pygame.Surface((4+width, 4+hight), SRCALPHA)
    buthov = pygame.Surface((4+width, 4+hight), SRCALPHA)
    newcenter = pygame.transform.scale(center, (x, center.get_rect().h))
    hnewcenter = pygame.transform.scale(hcenter, (x, center.get_rect().h))
    but.blit(newcenter, (partwidth, 2))
    buthov.blit(hnewcenter, (partwidth, 2))
    partwidth += newcenter.get_rect().w
    
    but.blit(left, (2, 2))
    buthov.blit(hleft, (2, 2))

    but.blit(right, (partwidth, 2))
    buthov.blit(hright, (partwidth, 2))
    return (but, buthov)

def make_dialog_bg_dynamic(width, height, THEME):
    sizes = {}
    try:
        topleft = utils.load_image(os.path.join(THEME['themepath'], "dialog_top_left.png" ))
        topright = utils.load_image(os.path.join(THEME['themepath'], "dialog_top_right.png" ))
        topcenter = utils.load_image(os.path.join(THEME['themepath'], "dialog_top_center.png" ))
        botleft = utils.load_image(os.path.join(THEME['themepath'], "dialog_bottom_left.png" ))
        botright = utils.load_image(os.path.join(THEME['themepath'], "dialog_bottom_right.png" ))
        botcenter = utils.load_image(os.path.join(THEME['themepath'], "dialog_bottom_center.png" ))
        rightcenter = utils.load_image(os.path.join(THEME['themepath'], "dialog_center_right.png" ))
        leftcenter = utils.load_image(os.path.join(THEME['themepath'], "dialog_center_left.png" ))
        centcenter = utils.load_image(os.path.join(THEME['themepath'], "dialog_center_center.png" ))
    except IOError, info:
        raise Exception, info
    dlg = pygame.Surface((4+width, 4+height), SRCALPHA)
    partwidth = topleft.get_rect().w 
    partheight = topleft.get_rect().h
    y = 0
    centerwidth = width - partwidth * 2
    centerheight = height - partheight * 2
    dlg.blit(topleft,(0,y))
    dlg.blit(pygame.transform.scale(topcenter,(centerwidth,partheight)), (partwidth,y))
    dlg.blit(topright,(partwidth + centerwidth, y))
    y += partheight
    sizes['title_area'] = pygame.Rect(0,0,centerwidth + partwidth * 2,y)
    temp_y = y       
    dlg.blit(pygame.transform.scale(leftcenter,(partwidth,centerheight)), (0,y))
    dlg.blit(pygame.transform.scale(centcenter,(centerwidth,centerheight)), (partwidth,y))
    dlg.blit(pygame.transform.scale(rightcenter,(partwidth,centerheight)), (partwidth + centerwidth,y))
    y += centerheight
    sizes['action_area'] = pygame.Rect(0,temp_y,centerwidth + partwidth * 2,y)
    
    partheight = botleft.get_rect().h
    dlg.blit(botleft,(0,y))
    dlg.blit(pygame.transform.scale(botcenter,(centerwidth,partheight)), (partwidth,y))
    dlg.blit(botright,(partwidth + centerwidth, y))
    sizes['button_area'] = pygame.Rect(0,y,centerwidth + partwidth * 2, y +partheight )
    return (dlg, sizes)

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

def get_boxes(color, hover_color, rect, selected_color=None, invert=False):
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
        if background_color == 'trans':
            surface = pygame.Surface(rect.size, SRCALPHA)
            surface.fill((0, 0, 0, 0))
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
        y = accumulated_height+16
        if y > 500:
            y = 500
        if background_color == 'trans':
            s = pygame.Surface((rect.w, y), SRCALPHA)
            s.fill((0, 0, 0, 0))
        else:
            s = pygame.Surface((rect.w, y))
            s.fill(background_color)
        s.blit(surface, (0, 0))
        surface = s
    if border:
        pygame.draw.rect(surface, (0, 0, 0), surface.get_rect().inflate(-1, -1), 1)
    return surface

if __name__ == '__main__':
    
    import SPLogging
    SPLogging.set_level('debug')
    SPLogging.start()
    
    from base import Init
        
    import pygame
    from pygame.constants import *
    pygame.init()
    
    from SPSpriteUtils import SPInit
    
    scr = pygame.display.set_mode((800, 600))
    scr.fill((240,240,250))
    pygame.display.flip()
    back = scr.convert()
    actives = SPInit(scr, back)
    
    THEME = Init('braintrainer')
    dlg = make_dialog_bg_dynamic(300,500,THEME)
    
    scr.blit(dlg,(100,100))
    pygame.display.update()
    runloop = 1 
    while runloop:
        pygame.time.wait(100)
        pygame.event.pump()
        events = pygame.event.get()
        for event in events:
            if event.type is KEYDOWN:
                if event.key == K_ESCAPE:
                    runloop = 0
    
    
    
    
