#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2010-2011 Stas Zykiewicz <stas.zytkiewicz@schoolsplay.org>
#
#           dialogs.py
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
import pygame
from pygame.constants import *
from base import Widget
from buttons import *
from SPConstants import *
from text import TextView
from SPSpriteUtils import SPSprite, SPGroup
from funcs import make_dialog_bg_dynamic
import subprocess

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
                 dialogwidth=0, dialogheight=0, name='', fbold=True):
        """screen - current pygame screen surface
        txt - can be a string or a list of strings or a SPSprite object.
        pos - is a tuple with x,y grid numbers. If not set the dialog is centered.
        fsize -  the fontsize (integer)
        buttons - a list with strings for the buttons (max two)
        dialog width and hight - 0 means dynamic.
        name - to identify this object (optional) 
        """
        Widget.__init__(self)
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
        self.dialogheight = dialogheight
        self.name = name
        self.fbold = fbold
        self.result = None
        self.runloop = True
        self.buttons_list = []
        self.butspace = 0
        self.padding = 8
        self.actives = SPGroup(self.screen, self.backgr)
        self.actives.set_onematch(True)
        for buttxt in self.buttons:
            b = ButtonDynamic(buttxt, (380,250), butfsize, padding=8, name=buttxt,\
                               fgcol=BLACK, colorname='green')
            b.set_use_current_background(True)
            b.connect_callback(self.cbf, MOUSEBUTTONUP, buttxt)
            self.actives.add(b)
            self.buttons_list.append(b)# keep the users order for showing (see below)
            self.butspace += b.rect.w + 8
        if not self.dialogwidth:
            self.dialogwidth = self.butspace
        self.ImShowed = False
        self._setup()
    
    def _setup(self):
        # get all the surfaces
        title = utils.char2surf(self.title, 24, ttf=TTF, fcol=self.THEME['dialog_title_fg_color'], bold=True)
        
        if type(self.txt) == types.ListType or type(self.txt) in types.StringTypes:
            tv = TextView(self.txt, (0, 0), pygame.Rect(0, 0, self.dialogwidth, 400),\
                           bgcol='trans',fsize=self.fsize ,\
                          fgcol=self.THEME['dialog_fg_color'], autofit=True, bold=self.fbold)
        else: # we assume a SPWidget.Widget object
            tv = self.txt
        b = self.buttons_list[0]
        # start building dialog
        if self.dialogwidth and self.dialogheight:
            r = pygame.Rect(0, 0, self.dialogwidth, self.dialogheight)
        else:
            r = pygame.Rect(0, 0, max(self.butspace,(tv.rect.w + (self.padding * 2)),100), \
                        title.get_rect().h + 8 + b.rect.h + tv.rect.h + (self.padding*3))
        if r.w > 750:
            r.w = 750
        if r.h > 530:
            r.h = 530
        dlgsurf, dlgsizes = make_dialog_bg_dynamic(r.w+50, r.h+70, self.THEME)
        
        r = dlgsurf.get_rect()
        if not self.pos:
            y = max(10, (600 - r.h) / 2)
            x = (800 - r.w) / 2
            self.pos = (x, y)

        y = 10
        x = 20
        dlgsurf.blit(title, (x,y))
        dlgsurf.blit(tv.image, (x, dlgsizes['title_area'].h))
        
        Widget.__init__(self, dlgsurf)
        
        self.image = dlgsurf

        self.rect.move_ip(self.pos)
        for k, v in dlgsizes.items():
            dlgsizes[k].move_ip(self.pos)
        x = self.rect.left + ((self.rect.w - (self.butspace + 16 * len(self.buttons_list))) / 2)
        y = self.rect.bottom - self.buttons_list[0].rect.h *2
        if len(self.buttons_list) == 2:
            x = self.rect.left + 16
            self.buttons_list[0].moveto((x, y), True)
            x = self.rect.right - (self.buttons_list[1].rect.w + 16)
            self.buttons_list[1].moveto((x, y), True)
        else:
            for b in self.buttons_list:
                b.moveto((x, y), True)
                x += b.rect.w + 16
        self.dlgsizes = dlgsizes
            
    def cbf(self, widget, event, data):
        self.result = data 
        self.runloop = False
        
    def get_result(self):
        return self.result
    
    def get_action_area(self):
        return self.dlgsizes
    
    def show(self, guests=None):
        if guests:
            self.actives.add(guests)
        self.display_sprite()
        for b in self.actives:
            b.display_sprite()
        self.ImShowed = True
    
    def run(self, guests=None):
        if not self.ImShowed:
            if guests:
                self.actives.add(guests)
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
        pygame.event.clear()
        self.erase_sprite()
        self.screen.blit(self.orgscreen, (0, 0))
        self.backgr.blit(self.orgbackgr, (0, 0))
        self.dim.undim()
        self.screen.set_clip(self.scrclip)
        if hasattr(self, 'reset_children'):
            # I'm a DialogWindow
            self.reset_children()

class DialogWindow(Dialog):
    """Modal dialog which displays sprites and has one or two buttons of it's own.
    The dialog has it's own eventloop.
    This differs from a standard dialog which can only display a surface. 
    
    This dialog can display and handle sprite objects which will be placed relativly
    to the dialogs' position.
    So if the dialog is displayed at 100,100 all sprites will be moved by 100,100.
    You must layout the sprites properly and make sure the dialog is big enough.
    The dialog will move all sprites by the dialogs display offset.
    
    The dialog calls the update method on all sprites in the eventloop.
    You can connect your sprites to callback functions to collect data or whatever.
    When the dialog quits all the sprite objects still exists so you can query them
    for data or states.
     
    Usage: TODO
    """
    def __init__(self, sprites, pos=None, butfsize=20,dialogheight=200, dialogwidth=200,\
              buttons=['OK'], title='', name=''):
        """screen - current pygame screen surface
        sprites - a list with all the sprites to display on the 'back' surface.
                The sprites must have the name attribute and position relative to the dialog set.
                You should connect the sprites to callbacks to get results.
        pos - is a tuple with x,y grid numbers. If not set the dialog is centered.
        buttons - a list with strings for the buttons (max two)
        name - to identify this object (optional) 
        """
        Dialog.__init__(self, ' ', pos=pos, fsize=12, butfsize=butfsize, buttons=buttons,\
                         title=title, dialogwidth=dialogwidth, dialogheight=dialogheight,\
                         name=name, fbold=True)
        self.show()
        self._org_pos = []
        x, y = self.get_action_area()['action_area'].topleft
        for s in sprites:
            s.set_use_current_background(True)
            sx, sy = s.get_sprite_pos()
            self._org_pos.append((s,(sx,sy)))
            s.moveto((sx + x,sy + y))
            s.display_sprite()
        self.sprites = sprites 
        self.actives.add(sprites)
     
    def reset_children(self):
        """This wil reset the positions from the sprites back to their original postions."""
        for s, pos in self._org_pos:
            s.moveto(pos) 

        
class MenuBar(Widget):
    def __init__(self, rect, actives, cbf, dice_cbf,lock, usestar=False, \
                 usegraph=False, usedice=False, volume_level=50):
        Widget.__init__(self)
        self.buttons_ypos = self.rect.top+8
        bname = 'core_info_button.png'
        hbname = 'core_info_button_ro.png'
        p = os.path.join(THEMESPATH, self.THEME['theme'],bname )
        hp = os.path.join(THEMESPATH, self.THEME['theme'],hbname )
        pos = (CORE_BUTTONS_XCOORDS[0], self.buttons_ypos)
        if not os.path.exists(p):
            p = os.path.join(DEFAULTTHEMESPATH, bname)
        if not os.path.exists(hp):
            hp = None
        if hp:
            self.infobutton = TransImgButton(p, hp,pos, name='Info')
        else:
            self.infobutton = ImgButton(p, pos, name='Info')
        self.infobutton.mouse_hover_leave_action = True
        self.infobutton.connect_callback(cbf, MOUSEBUTTONUP, 'Info')
        
        bname = 'core_quit_button.png'
        hbname = 'core_quit_button_ro.png'
        p = os.path.join(THEMESPATH, self.THEME['theme'],bname )
        hp = os.path.join(THEMESPATH, self.THEME['theme'],hbname )
        pos = (CORE_BUTTONS_XCOORDS[8], self.buttons_ypos)
        if not os.path.exists(p):
            p = os.path.join(DEFAULTTHEMESPATH, bname)
        if not os.path.exists(hp):
            hp = None
        if hp:
            self.quitbutton = TransImgButton(p, hp,pos, name='Quit')
        else:
            self.quitbutton = ImgButton(p, pos, name='Quit')
        self.quitbutton.mouse_hover_leave_action = True
        self.quitbutton.connect_callback(cbf, MOUSEBUTTONUP, 'Quit')
        
        if volume_level == 0:
            bname = 'core_volmute_button.png'
            hbname = 'core_volmute_button_ro.png'
        else:
            bname = 'core_volume_button.png'
            hbname = 'core_volume_button_ro.png'
        p = os.path.join(THEMESPATH, self.THEME['theme'],bname )
        hp = os.path.join(THEMESPATH, self.THEME['theme'],hbname )
        pos = (CORE_BUTTONS_XCOORDS[7], self.buttons_ypos)
        if not os.path.exists(p):
            p = os.path.join(DEFAULTTHEMESPATH, bname)
        if not os.path.exists(hp):
            hp = None
        if hp:
            self.volumebutton = TransImgButton(p, hp,pos, name='Volume')
        else:
            self.volumebutton = ImgButton(p, pos, name='Volume')
        self.volumebutton.mouse_hover_leave_action = True
        self.volumebutton.connect_callback(cbf, MOUSEBUTTONUP, 'Volume')
        
        if usegraph:
            self.chartbutton = ChartButton((CORE_BUTTONS_XCOORDS[5], self.buttons_ypos), cbf)
            self.chartbutton.mouse_hover_leave_action = True
        else:
            self.chartbutton = None
        if usestar:
            self.dicebuttons = StarButton((CORE_BUTTONS_XCOORDS[1], self.buttons_ypos), \
                                                        actives, dice_cbf, lock, usedice)
        else:
            self.dicebuttons = DiceButtons((CORE_BUTTONS_XCOORDS[3], self.buttons_ypos),\
                                                        actives, dice_cbf, usedice)
        self.scoredisplay = ScoreDisplay((CORE_BUTTONS_XCOORDS[6], self.buttons_ypos+4), cbf=cbf)
    
    def get_buttons_posy(self):
        return self.buttons_ypos        
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
    def get_volumebutton(self):
        return self.volumebutton


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
        self.logger = logging.getLogger("childsplay.SPWidgets_lgpl.Graph")
        # main surf is 500x300 the graph is a surf of 470x270.
        # 20 for the text bottom and left and 10 for a top and right offset
        gs = pygame.Surface((470, 270))# surf for the graph
        gs.fill((230, 230, 230))
        self.s = pygame.Surface((500, 400))# main surf
        self.s.fill((200, 200, 200))
        if not data:
            self.logger.warning("No data received to show in graph")
            ts = utils.char2surf(_("No data available for this level"), TTFSIZE + 8, ttf=TTF, split=35)
            y = 100
            for s in ts:
                self.s.blit(s, (20, y))
                y += s.get_height()
            Widget.__init__(self, self.s)
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
            ts = utils.char2surf(str(i), TTFSIZE-2, ttf=TTF, bold=True)
            i -= 1
            self.s.blit(ts, (4, y + 35))
        ts0 = utils.char2surf(headertext, TTFSIZE-2, ttf=TTF, bold=True)
        ts1 = utils.char2surf(_("Percentile scores for level %s") % level, TTFSIZE, ttf=TTF)
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
                ts = utils.char2surf(date, TTFSIZE-5, ttf=TTF)
                # rotate 90 degrees
                v_ts = pygame.transform.rotate(ts, 270)
                self.s.blit(v_ts, (x + 20, 320))
        # connect the dots if there are more then one
        if len(dotslist) > 1:
            pygame.draw.lines(gs, BLUE, 0, dotslist, 2)
        pygame.draw.rect(gs, (0, 0, 0), gs.get_rect().inflate(-1, -1), 2)
        # finally blit the two surfaces
        self.s.blit(gs, (20, 40))
        Widget.__init__(self, self.s)
    
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
        self.logger = logging.getLogger("childsplay.SPocwWidgets.ExeCounter")
        Widget.__init__(self)
        self.total = total
        self.done = 0
        if not text:
            text = _("Exercises")
        if len(text) > 14:#prevent to large label when localized
            text = text[:14]
        fgcol=self.THEME['execounter_fg_color']
        bgcol = self.THEME['execounter_bg_color']
        s0 = utils.char2surf(text, fsize=fsize, fcol=fgcol)
        txt = "%s/%s" % (self.done, self.total)
        
        self.lbl = Label(txt, (pos[0]+2, pos[1]+s0.get_height()), fsize=12, padding=4, border=0, fgcol=fgcol, bgcol=bgcol)
        
        r = pygame.Rect(0, 0,s0.get_rect().w+4, s0.get_rect().h +\
                                               self.lbl.rect.h+4)
        box, spam = get_boxes(bgcol, BLACK, r)
        
        box.blit(s0, (2, 2))
        self.image = box       
        Widget.__init__(self, box)
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
        Label.__init__(self, self.scorestr, pos, fsize=20, padding=9, border=1)
        if cbf:
            self.connect_callback(cbf, MOUSEBUTTONUP, 'scoredisplay')
            # We disguise our selfs into a graphbutton
            self.name = 'Chart'
        else:
            self.name = 'ScoreDisplay'
        self.UseMe = True
    
    def _showme(self):
        if self.UseMe:
            self.display_sprite()
    
    def set_score(self, score=0):
        if score < 0:
            return
        if score > 9999:
            score = 9999
        self.scorestr = '%04d' % score
        self.settext(self.scorestr)
        self._showme()
    
    def increase_score(self, score):
        if int(self.scorestr) + score > 9999:
            score = 0
        if int(self.scorestr) + score < 0:
            score = 0
        self.scorestr = '%04d' % (int(self.scorestr) + int(score))
        self.settext(self.scorestr)
        self._showme()
        
    def clear_score(self):
        self.scorestr = '0000'
        self.settext('0000')
        self._showme()
        
    def return_score(self):
        return int(self.scorestr)

class VolumeAdjust(Widget):
    """Widget that provides a volume change widget with on both ends a small button
    to increase or decrease and mute the volume level and in the middle a percentage display.
    """
    def __init__(self, pos, volume=None, voice_unmute=True, defval=50):
        """defval - value between 0, silent, and 100, maximum, volume level."""
        Widget.__init__(self)
        self.logger = logging.getLogger("childsplay.SPWidgets.VolumeAdjust")
        self.logger.debug("VolumeAdjust called with volume level %s" % volume)
        self.soundcheck = utils.load_sound(os.path.join(ACTIVITYDATADIR, 'CPData','volumecheck.wav'))
        self.theme = self.THEME['theme']
        if volume or int(volume) == 0:
            #print "we have volume"
            self.volume = int(volume)
        elif self.WEHAVEAUMIX:
            #print "we have aumix"
            self.volume = int(self.WEHAVEAUMIX)
        else:
            #print "else defval"
            self.volume = int(defval)
        self.logger.debug("setting volume string to %s" % self.volume)
        self.volstr = '%02d' % self.volume + "%"
        # TODO: set fgcol and bgcol kwargs ?
        self.logger.debug("setting voice unmute to %s" % voice_unmute)
        imgup = os.path.join(THEMESPATH, self.theme,'core_volup_button.png')
        imgup_ro = os.path.join(THEMESPATH, self.theme,'core_volup_button_ro.png')
        imgdown = os.path.join(THEMESPATH, self.theme,'core_voldown_button.png')
        imgdown_ro = os.path.join(THEMESPATH, self.theme,'core_voldown_button_ro.png')
        px, py = pos
        
        prev = os.path.join(THEMESPATH, self.theme, 'core_volume_button.png')
        prev_ro = os.path.join(THEMESPATH, self.theme, 'core_volume_button_ro.png')
        next = os.path.join(THEMESPATH, self.theme, 'core_volmute_button.png')
        next_ro = os.path.join(THEMESPATH, self.theme, 'core_volmute_button_ro.png')
        
        self.lbl0 = Label(_("Quiz voice"), pos, fsize=18, padding=4, minh=48)
        px += self.lbl0.rect.w + 10
        self.voicetoggle = TransPrevNextButton((px, py), self._cbf_toggle_voice, \
                                  prev, prev_ro,\
                                  next, next_ro, states=[True,False])
        py += self.voicetoggle.rect.h + 20
        px = pos[0]
        self.lbl1 = Label(self.volstr, pos, fsize=18, padding=4, border=1, minh=48)
        self.volumetoggle = TransPrevNextButton((px, py), self._cbf_toggle_volume, \
                                  prev, prev_ro,\
                                  next, next_ro)
        px += self.volumetoggle.rect.w + 20
        self.voldownbut = TransImgButton(imgdown, imgdown_ro, (px, py))
        self.voldownbut.mouse_hover_leave_action = True
        self.voldownbut.connect_callback(self._cbf, MOUSEBUTTONUP, -5)
        
        px += self.voldownbut.rect.w
        self.lbl1.moveto((px , py+4))
        px += self.lbl1.rect.w
        
        self.volupbut = TransImgButton(imgup, imgup_ro, (px, py))
        self.volupbut.mouse_hover_leave_action = True
        self.volupbut.connect_callback(self._cbf, MOUSEBUTTONUP, 5)
        if self.volume == 0:
            self.volumetoggle.toggle()
            self.volumetoggle.display_sprite()
        if not voice_unmute:
            self.voicetoggle.toggle()
            self.voicetoggle.display_sprite()
            
    def set_use_current_background(self, bool):
        self.voldownbut.set_use_current_background(bool)
        self.volupbut.set_use_current_background(bool)
        self.volumetoggle.but.set_use_current_background(bool)
        self.voicetoggle.but.set_use_current_background(bool)
        
    def _cbf_toggle_volume(self, widget, event, data):
        self.logger.debug("set volume %s" % data)
        if self.volume > 0:
            self.volume = 0
        else:
            self.volume = 75
        self.volumetoggle.toggle()
        self.volumetoggle.display_sprite()
        self.volstr = '%02d' % self.volume + "%"
        self.lbl1.erase_sprite()
        self.lbl1.settext(self.volstr)
        self.lbl1.display_sprite()
        subprocess.Popen("amixer set Master %s" % self.volume + "%",shell=True)

    def _cbf_toggle_voice(self, *args):
        self.voicetoggle.toggle()
        self.voicetoggle.display_sprite()
        
    def _cbf(self, widget, event, data):
        if self.volume >= 100 and data[0] > 0:
            return
        if self.volume <= 0 and data[0] < 0:
            return
        self.volume += data[0]
        if self.volume > 99:
            self.volume = 99
        if self.volume < 0:
            self.volume = 0
        if self.volume > 0 and self.volumetoggle.get_state() == 'next':
            self.volumetoggle.toggle()
            self.volumetoggle.display_sprite()
        self.volstr = '%02d' % self.volume + "%"
        self.lbl1.erase_sprite()
        self.lbl1.settext(self.volstr)
        self.lbl1.display_sprite()
        self.logger.debug("Volume set to %s" % self.volstr)
        #Here we set the actual volume (We do this with aumix)
        if self.WEHAVEAUMIX:
            subprocess.Popen("amixer set Master %s" % self.volume + "%",shell=True)
            self.soundcheck.play()
        else:
            self.logger.warning("Not possible to set volume level")
        
    def display(self):
        self.voldownbut.display_sprite()
        self.volupbut.display_sprite()
        self.lbl1.display_sprite()
        self.lbl0.display_sprite()
        self.volumetoggle.display_sprite()
        self.voicetoggle.display_sprite()
    
    def hide(self):
        self.voldownbut.erase_sprite()
        self.volupbut.erase_sprite()
        self.lbl1.erase_sprite()
        self.lbl0.display_sprite()
        self.volumetoggle.erase_sprite()
        self.voicetoggle.erase_sprite()
    
    def get_actives(self):
        return [self.voldownbut, self.volupbut, self.lbl0,  self.lbl1,\
                self.volumetoggle.get_actives(),self.voicetoggle.get_actives()]
    
    def get_volume(self):
        return int(self.volume)

    def get_voice_state(self):
        return self.voicetoggle.get_state()
            
class ScrollWindow(Widget):
    """Widget that holds other widgets and scrolls them up or down."""
    def __init__(self, pos, size, objects, padding=4, childpadding=20, \
                 scrollstep=0, border=0, cols=0, scrollbutton_size='64', \
                 bordercol=BLACK, autoscroll=False):
        """pos - position
        size - size of the scrollwindow
        objects - list with SPWidget object to display
        padding - space between the scrollwindow and the children
        childpadding - space between the children
        scrollstep - amount of pixels to scroll
        border - a border around the window thickness in pixels. 0 means no border
        cols - the amount of columns. 0 means that the amount of columns depends
        on the amount of children on a row. (Currently only 0 or 1 are supported)
        button_up and button_down - Defaults to None and than a text button is used.
        When it's not None a file path is assumed.
        scrollbutton_size - defaults to 64. Supported 
        A special attribute is added to the child called _scroll_focus."""
        # TODO: add append and insert methods
        Widget.__init__(self)
        self.image = pygame.Surface((1,1))# image is needed for a sprite object
        self.theme = self.THEME['theme']
        self.rect = pygame.Rect(pos+size)
        self.border = border
        self.bordercol = bordercol
        self.button_up = os.path.join(self.THEME['themepath'], '%s_scroll_up.png' % scrollbutton_size)
        self.button_up_ro = os.path.join(self.THEME['themepath'], '%s_scroll_up_ro.png' % scrollbutton_size)
        self.button_down = os.path.join(self.THEME['themepath'], '%s_scroll_down.png' % scrollbutton_size)
        self.button_down_ro = os.path.join(self.THEME['themepath'], '%s_scroll_down_ro.png' % scrollbutton_size)
        if self.border:
            self._draw_border()
        self.autoscroll = autoscroll
        self.rect.topleft = pos
        self.visiblerect = self.rect.inflate((-border*2, -border*2))
        start_x = pos[0] + padding
        start_y = pos[1] + padding
        max_x = pos[0] + size[0]
        max_y = pos[1] + size[1]
        x = start_x
        y = start_y
        biggest_width = 1
        firstobject = cols == 1
        _objects = []
        for obj in objects:
            if obj.get_sprite_width() > biggest_width:
                biggest_width = obj.get_sprite_width()
        
        obj_per_row = (size[0] / (biggest_width + childpadding))
        count = 0
        for obj in objects:
            if firstobject:
                y = y - obj.get_sprite_height() - childpadding
                firstobject = False
            if count == obj_per_row or cols == 1:
                x = start_x + padding + childpadding
                y = y + obj.get_sprite_height() + childpadding
                count = 1
            else:
                x += padding + childpadding
                count += 1
            obj.moveto((x, y))
            if self.rect.contains(obj.rect):
                obj._scroll_focus = True
            else:
                obj._scroll_focus = False
            
            x += biggest_width
            _objects.append(obj)
        if _objects:
            self.set_objects(_objects)
            if scrollstep == 0:
                self.scrollstep = objects[0].get_sprite_height() + childpadding
            else:
                self.scrollstep = scrollstep
    
    def _draw_border(self):
        pygame.display.update(pygame.draw.rect(self.screen, self.bordercol, self.rect, self.border))
            
    def set_objects(self, objects):
        self._firstchild = objects[0]
        self._firstchild_start = self._firstchild.get_sprite_pos()
        self._lastchild = objects[-1]
        self._objects = objects
        # setup the scrollbuttons
        if self.button_up:
            # we assume the rest is also set
            self.upbut = TransImgButton(self.button_up, self.button_up_ro, \
                                    (self.rect.right+4, self.rect.top))
            self.downbut = TransImgButton(self.button_down, self.button_down_ro, \
                                    (self.rect.right+4, self.rect.bottom))
        else:
            self.upbut = Button("up", (self.rect.right+4, self.rect.centery))
            self.downbut = Button("down", (self.rect.right+4, self.rect.centery))
        self.downbut.moveto((self.rect.right+4, self.rect.bottom - self.downbut.get_sprite_height()))
        self.upbut.connect_callback(self._cbf, MOUSEBUTTONUP, 'up')
        self.upbut.display_sprite()
        self.downbut.connect_callback(self._cbf, MOUSEBUTTONUP, 'down')
        self.downbut.display_sprite()  
        #self.display_sprite(pos)
        self.display_children()
    
    def _cbf(self, widget, event, data):
        if data[0] == 'down':
            if not self.rect.contains(self._lastchild.rect):
                self.scrollstep = -abs(self.scrollstep)
                self._scroll_children()
        else:
            if not self.rect.contains(self._firstchild.rect):
                self.scrollstep = abs(self.scrollstep)
                self._scroll_children()
        widget.mouse_hover_leave()
        
    def get_actives(self):
        if not self.rect.contains(self._lastchild.rect) or self.autoscroll:
            self.upbut.display_sprite()
            self.downbut.display_sprite()  
            return [self.upbut, self.downbut,self]
        else:
            return [self]


    def display_children(self):
        for obj in self._objects:
            if obj._scroll_focus:
                obj.display_sprite()
            else:
                break
    
    def erase_children(self):
        for obj in self._objects:
            obj.erase_sprite()
                
    def _scroll_children(self):
        oldclip = self.screen.get_clip()
        self.screen.set_clip(self.visiblerect)
        self.erase_children()
        for obj in self._objects:
            if obj._scroll_focus:# displayed object
                obj.moveto((obj.rect.x, obj.rect.y + self.scrollstep))
                if self.rect.contains(obj.rect):
                    obj.display_sprite()
                else:
                    obj._scroll_focus = False
            else:# not displayed
                obj.moveto((obj.rect.x, obj.rect.y + self.scrollstep))
                if self.rect.contains(obj.rect):
                    obj._scroll_focus = True
                    obj.display_sprite()
        self.screen.set_clip(oldclip)
        pygame.display.update()
    
    # Override the methods from SPWidget.SPSprite
    # We use it to redraw the border if we have one
    def display_sprite(self,*args):
        if self.border:
            self._draw_border()
    def erase_sprite(self,*args):
        pass

class ProgressBar(Widget):
    """Class which provides a surface with a progressbar.(400x100)
    """
    ## TODO: the progress bar is full after 95 steps, not 100.
    ## The reason is that it's not possible to split pixels. :-)
    def __init__(self,pos, size, steps=10,\
                 transparent=False, backcol=GREY, barfcol=DEEPSKYBLUE4, barbcol=BLACK):
        """pos is the postion to place this widget
        size is a tuple with the width and height of the widget
        steps is the amount of steps that should be taken to fill the bar, defaults to 10
        The update call returns the number of steps taken, when the bar is full it will return False
        """
        Widget.__init__(self)
        self.end = size[0]
        self.step = self.end / steps
        self.steps = steps
        self.backcol = backcol
        self.barfcol = barfcol
        self.barbcol = barbcol
        
        self.image = pygame.Surface((size[0],size[1]))
        self.image.fill(backcol)
        self.rect = self.image.get_rect()
        pygame.draw.rect(self.image, barbcol, self.rect.inflate(-8,-8),0)
                
        self.barsurf = pygame.Surface((size[0]-8,size[1]-8))
        self.barsurf.fill(barfcol)
        self.barrect =  self.barsurf.get_rect()
        self.barend = self.step        
        self._initbar()
        self.moveto(pos)
                
    def _initbar(self):
        self.x, self.progress = 0, 0 # used in update
        
    def update(self):
        """Update the progressbar with step.
        Returns the number of steps passed.
        """
        if self.progress >= self.steps:
            return False
        self.image.blit(self.barsurf, (4,4), (0, 0, self.x + self.barend, self.barrect.h))
        self.display_sprite()
        #self.refresh_sprite()
        self.progress += 1
        self.barend = (self.progress+1) * self.step
        return self.progress
    
    def reset_bar(self, header=''):
        """This will set the bar to 0."""
        self.erase_sprite()
        self._initbar()
        
    def clearbar(self, screen, backgr):
        """Remove the bar from the screen.
        @ backgr is blitted over @screen.
        This calls pygame.display.update"""
        self.erase_sprite()
    
