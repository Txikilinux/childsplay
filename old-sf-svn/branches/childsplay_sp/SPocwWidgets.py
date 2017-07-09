# -*- coding: utf-8 -*-

# Copyright (c) 2006-2008 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           SPocwWidgets.py
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

# Misc ocemgui and SPSpriteUtils widgets

import childsplay_sp.ocempgui.widgets as ocw
import childsplay_sp.ocempgui.widgets.Constants as ocwc
import logging
import os
import pygame
import types
from SPConstants import *
from SPSpriteUtils import SPSprite
from childsplay_sp import pangofont as PFont
from pygame.constants import *
from utils import char2surf, get_locale, txtfmt
module_logger = logging.getLogger("schoolsplay.SPocwWidgets")

LOCALE_RTL = get_locale()[1]
if LOCALE_RTL:
    ALIGN = ocwc.ALIGN_RIGHT
else:
    ALIGN = ocwc.ALIGN_LEFT
    
from SPConstants import CORE_BUTTONS_XCOORDS as CBXC

class SPEntry(SPSprite):
    """Entry widget which is RTL aware and uses Pango.
    This widget reacts only to two key events, backspace and enter.
    For a entry widget that has all the fancy editable properties use the ocempgui
    Entry widget.
    This widget is developed for the login window.(SPgdm.py)
    """
    def __init__(self, pos, charsize, fontsize=P_TTFSIZE, maxchar=20):
        """@charsize is the entry length in chars.
        @fontsize is the size of the font used (Pango)
        @maxchar is the maximum number of chars the widget will accept.
        """
        self.logger = logging.getLogger("schoolsplay.SPocwWidgets.SPEntry")
        self.text = ''
        self._maxchar = maxchar
        self._charsize = charsize
        self._fnt = PFont.PangoFont(family=P_TTF, size=P_TTFSIZE, bold=True)
        self._textsurf = self._fnt.render(self.text, True, BLACK, None)
        self.x, self.y = self._fnt.size('w' * self._charsize)# just a gamble as we don't use monospace
        self.image = pygame.Surface((self.x + 4, self.y + 4))
        #self.image = pygame.Surface((100, 100))
        self.image.fill(LIGHT_GREY)
        self.rect = self.image.get_rect()
        pygame.draw.rect(self.image, BLACK, self.rect, 1)
        self._orgimage = self.image.convert()
        SPSprite.__init__(self, self.image)
        self.connect_callback(self.callback, event_type=KEYDOWN)
        self.moveto(pos)
        self._draw_caret(0)
    
    def get_text(self):
        return self.text
    
    def _draw_caret(self, pos):
        if LOCALE_RTL:
            if pos != 12:
                pos = self.image.get_width() - self._textsurf.get_width() - 2
        else:
            pos = self._textsurf.get_width() + 2 + pos
        pygame.draw.rect(self.image, BLACK, (pos, 2, 2, self.y), 0)
    
    def _drawtext(self, text):
        self._textsurf = self._fnt.render(text, True, BLACK, None)
        if LOCALE_RTL:
            pos = self.image.get_width() - self._textsurf.get_width()-1 
        else:
            pos = 1
        self.image = self._orgimage.convert()
        if self._textsurf.get_width() >= self.image.get_width():
            pos = self.image.get_width() - self._textsurf.get_width() - 12
            if LOCALE_RTL:
                pos = 12
        self.image.blit(self._textsurf, (pos, 0))
        self._draw_caret(pos)
            
    def callback(self, widget, event, * args):
        """ This is called when the sprite class update method is called.
        Remember that you must 'connect' a callback first with a call to
        self.connect_callback, see the CPSprite reference for info on possibilities
        of connecting callbacks .
        """
        #self.logger.debug("event.key %s event.unicode %s" % (event.key, event.unicode))
        if event.key in (K_RETURN, K_KP_ENTER):
            return True
        elif event.key == K_BACKSPACE:
            self.text = self.text[:-1]
            self._drawtext(self.text)
        # Non-printable characters or maximum exceeded.
        elif (len (event.unicode) == 0) or (ord (event.unicode) < 32):
            # Any unicode character smaller than 0x0020 (32, SPC) is
            # ignored as those are control sequences.
            return False
        else:
            if len(self.text) >= self._maxchar:
                return
            self.text = self.text + event.unicode
            self._drawtext(self.text)
        return
                    

class SPLabel(SPSprite):
    """Transparent label"""
    def __init__(self, text, font=P_TTF, fontsize=P_TTFSIZE, fontcol=BLACK, bold=True):
        fnt = PFont.PangoFont(family=font, size=fontsize, bold=bold)
        self.image = fnt.render(text, True, fontcol, None)
        SPSprite.__init__(self, self.image)

class SPDialog:
    """Don't use this as a standalone, you must extend this class"""
    def __init__(self, re):
        self.re = re
    def run(self):
        while self.runloop:
            pygame.time.wait(100)
            pygame.event.pump()
            events = pygame.event.get()
            self.re.distribute_events(* events)
        return self.result
    def _close(self, result, dialog=None, label=None):
        # we remove widgets we added
        self.re.remove_widget(dialog)
        self.re.refresh()
        #dialog.destroy()
        # yes = 0, no = 1
        self.runloop = 0
        self.result = result

class ExitDialog(SPDialog):
    def __init__(self, re):
        SPDialog.__init__(self, re)
        yb = ocw.Button(_("Yes"))
        yb.child.create_style()
        yb.child.style["font"]["size"] = P_TTFSIZE
        #yb.child.style["font"]["name"] = TTF
        yb.set_focus()
        nb = ocw.Button(_("No"))
        nb.child.create_style()
        nb.child.style["font"]["size"] = P_TTFSIZE
        #nb.child.style["font"]["name"] = TTF
        
        buttons = [yb, nb]
        results = [ocwc.DLGRESULT_OK, ocwc.DLGRESULT_CANCEL]
        if LOCALE_RTL:
            buttons = [nb, yb]
            results = [ocwc.DLGRESULT_CANCEL, ocwc.DLGRESULT_OK]
            
        dlg = ocw.GenericDialog(_("Question"), buttons, results)
        ltxt = _("Do you really want to quit ?")
        # we add spaces to force the dialog width otherwise the caption isn't displayed properly. 
        lbl = ocw.Label(ltxt + "           ")
        lbl.set_align(ALIGN)
        lbl.create_style()
        lbl.style["font"]["size"] = P_TTFSIZE
        dlg.content.add_child(lbl)
        dlg.topleft = ((740-lbl.width) / 2, (460-lbl.height) / 2)
        dlg.connect_signal(ocwc.SIG_DIALOGRESPONSE, self._close, dlg, lbl)
        dlg.opacity = 220
        dlg.depth = 1
        self.re.add_widget(dlg)
        self.result = None
        self.runloop = 1
        
class InfoDialog(SPDialog):
    def __init__(self, re, text, fnsize=18, fnname="Helvetica", opacity=220):
        """Displays a info box. 
        @text may be a list with text strings or a ocemgui object.
        If the text string contains '\n' it's assumed the string is formatted in
        the correct length.
        If no '\n' are found the string is formatted.
        You must call this dialog from within your eventloop.""" 
        module_logger.debug("InfoDialog called with %s" % text)
        SPDialog.__init__(self, re)
        yb = ocw.Button(_("Ok"))
        yb.child.create_style()
        yb.child.style["font"]["size"] = P_TTFSIZE
        yb.set_focus()
        buttons = [yb]
        results = [ocwc.DLGRESULT_OK]
        dlg = ocw.GenericDialog(_("Information"), buttons, results)
        if type(text) in (types.UnicodeType, types.StringType) or \
            type(text) is types.ListType:
            if type(text) is types.ListType:
                text = "\n".join(txtfmt(text, 60))
            else:
                if text.find('\n') == -1:
                    text = "\n".join(txtfmt([text], 60))
            lbl = ocw.Label(text)
            lbl.multiline = True
            lbl.set_align(ALIGN)
            lbl.padding = 8
            lbl.create_style()
            lbl.style["font"]["size"] = P_TTFSIZE
        else:
            # we assume that it's a ocemgui widget
            lbl = text
        dlg.content.add_child(lbl)
        dlg.topleft = ((740-lbl.width) / 2, (460-lbl.height) / 2)
        dlg.connect_signal(ocwc.SIG_DIALOGRESPONSE, self._close, dlg, lbl)
        dlg.opacity = opacity
        dlg.depth = 1
        self.re.add_widget(dlg)
        self.result = None
        self.runloop = 1

class GraphDialog(SPDialog):
    def __init__(self, re, surf, fnsize=18, fnname="Helvetica", savebutton=None):
        """Displays a graph surface. 
        @surf must be a ocemgui object.
        @savebutton indicates displaying a save button.""" 
        SPDialog.__init__(self, re)
        yb = ocw.Button(_("Ok"))
        yb.child.create_style()
        yb.child.style["font"]["size"] = P_TTFSIZE
        yb.set_focus()
        buttons = [yb]
        if savebutton:
            sb = ocw.Button(_("Save"))
            sb.child.create_style()
            sb.child.style["font"]["size"] = P_TTFSIZE
            buttons.append(sb)
        results = [ocwc.DLGRESULT_OK, savebutton]
        dlg = ocw.GenericDialog(_("Results diagram"), buttons, results)
        dlg.content.add_child(surf)
        dlg.topleft = ((740-surf.width) / 2, (440-surf.height) / 2)
        dlg.connect_signal(ocwc.SIG_DIALOGRESPONSE, self._close, dlg, surf)
        dlg.depth = 1
        self.re.add_widget(dlg)
        self.result = None
        self.runloop = 1

class Label:
    """Object that extends the Ocempgui Label"""
    def __init__(self, re, text, pos, theme='default'):
        """This will create a label with the @text and add it to the renderer.
        @re, reference to the renderer.
        @text, the text to display.
        @pos, the position tuple x,y."""
        self.logger = logging.getLogger("schoolsplay.SPocwWidgets.Label")
        self._re = re
        self._frm = ocw.HFrame()
        if theme == 'mpt':
            self._frm.border = ocwc.BORDER_NONE
        self._frm.create_style()['bgcolor'][ocwc.STATE_NORMAL] = DARK_GREY
        self.pos = pos
        lbl = ocw.Label(text)
        if theme == 'mpt':
            lbl.create_style()['bgcolor'][ocwc.STATE_NORMAL] = DARK_GREY
        lbl.set_align(ALIGN)
        lbl.create_style()
        lbl.style["font"]["size"] = P_TTFSIZE
        self._frm.add_child(lbl)
        self._frm.topleft = self.pos
        self._re.add_widget(self._frm)
        self._re.update() 
        self.theme = theme
    
    def moveto(self, pos):
        """move the label, this will also call erase"""
        self.logger.debug("moveto called with: %s" % pos)
        self.erase()
        self._frm.topleft = pos
        self._re.add_widget(self._frm)
        
    def rename(self, text, pos=None):
        """rename the text inside the label, @pos is the position."""
        self.logger.debug("rename called with: %s,%s" % (text, pos))
        self.erase()
        self._frm = ocw.HFrame()
        if self.theme == 'mpt':
            self._frm.border = ocwc.BORDER_NONE
        self._frm.create_style()['bgcolor'][ocwc.STATE_NORMAL] = DARK_GREY
        lbl = ocw.Label(text)
        lbl.create_style()
        lbl.style["font"]["size"] = P_TTFSIZE
        if self.theme == 'mpt':
            lbl.create_style()['bgcolor'][ocwc.STATE_NORMAL] = DARK_GREY
        self._frm.add_child(lbl)
        self._frm.topleft = self.pos
        self._re.add_widget(self._frm)
        self._re.update() 
        
    def erase(self):
        """erase the label"""
        self._re.remove_widget(self._frm)
        self._re.update()

class ToolTip:
    """The TooltipWindow is a non-interactive widget that can display a short to
    medium amount of text and can be used to display additional information and
    descriptions. It uses a certain background color to be easily distinguished
    from other widgets. 
    Usage:
    tt = ToolTip()
    button1 = Button ("Move the mouse over me")
    button1.tooltip = "An enhanced description"
    button1.connect_signal (SIG_ENTER, tt._make_tooltip, button1.tooltip,renderer)
    button1.connect_signal (SIG_LEAVE, tt._destroy_tooltip)
        
    button2 = Button ("And over me, too")
    button2.tooltip = "Another description"
    button2.connect_signal (SIG_ENTER, tt._make_tooltip, button2.tooltip,renderer)
    button2.connect_signal (SIG_LEAVE, tt._destroy_tooltip)
    """
    _tooltip = None
    def __init__(self):
        pass
        
    def _make_tooltip(self, tip, renderer):
        """Called at runtime when the tooltip must be created"""
        # Destroy the tooltip, if it exists.
        if self._tooltip:
            self._tooltip.destroy ()
    
        # Create a new tooltip.
        self._tooltip = ocw.TooltipWindow(tip)
        self._tooltip.create_style()
        self._tooltip.style["font"]["size"] = P_TTFSIZE
        x, y = pygame.mouse.get_pos ()
        # Make tooltip display always inside window
        size = self._tooltip.size
        # We don't care about hight as we always inside the y-window
        if x + size[0] > 800:
            x = 790 - size[0]
        self._tooltip.topleft = x + 8, y - 5
        self._tooltip.depth = 99 # Make it the topmost widget.
    
        renderer.add_widget (self._tooltip)
    
    def _destroy_tooltip (self):
        # Destroy the tooltip, if it exists.
        if self._tooltip:
            #renderer.remove_widget(self._tooltip)
            self._tooltip.destroy ()
            self._tooltip = None
            #renderer.update()

class Graph:
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
            ts = char2surf(_("No data available for this level"), P_TTFSIZE + 8, ttf=P_TTF, split=35)
            y = 100
            for s in ts:
                self.s.blit(s, (20, y))
                y += s.get_height()
            return
        # border around the surf
        pygame.draw.rect(self.s, (100, 100, 100), self.s.get_rect().inflate(-1, -1), 2)
        
        # draw mu line and sigma deviation as a transparent box.
        if norm:
            mu, sigma = norm
            # line
            pygame.draw.line(gs, DARK_BLUE, (0, mu * 27), (470, mu * 27), 3)
            # deviation box, transparent blue
            # the sigma value is the percentage of the mu value
            top_y = mu + (mu / 100.0 * sigma)
            bottom_y = mu - (mu / 100.0 * sigma)
            darken = pygame.Surface((470, int((top_y-bottom_y) * 27)))
            darken.fill(BLUE)
            darken_factor = 64
            darken.set_alpha(darken_factor)
            gs.blit(darken, (0, 270-top_y * 27))
            
        # draw y-axes graph lines, initial y offset is 30 pixels to leave room for text.
        i = 10
        for y in range(0, 270, 27):
            pygame.draw.line(gs, (0, 0, 0), (0, y), (470, y), 1)
            ts = char2surf(str(i), P_TTFSIZE-2, ttf=P_TTF, bold=True)
            i -= 1
            self.s.blit(ts, (4, y + 35))
        ts0 = char2surf(headertext, P_TTFSIZE-2, ttf=P_TTF, bold=True)
        ts1 = char2surf(_("Scores reached in level %s") % level, P_TTFSIZE, ttf=P_TTF)
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
                y = int(item[1] * 27)
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
                ts = char2surf(date, P_TTFSIZE-5, ttf=P_TTF)
                # rotate 90 degrees
                v_ts = pygame.transform.rotate(ts, 270)
                self.s.blit(v_ts, (x + 20, 320))
        # connect the dots if there are more then one
        if len(dotslist) > 1:
            pygame.draw.lines(gs, BLUE, 0, dotslist, 2)
        pygame.draw.rect(gs, (0, 0, 0), gs.get_rect().inflate(-1, -1), 2)
        # finally blit the two surfaces
        self.s.blit(gs, (20, 40))
        
    
    def _calculate_position(self, pos):
        new_pos = pos# finish this
        return new_pos
    
    def get_surface(self):
        return self.s

class ExeCounter:
    """Object that provides a, transparent, Pygame Surface that displays a simple 
    exercise counter in the form, done/todo.
    It uses two label objects for the display and provides some methods to 
    interact with these labels.
    The object places the labels in the menubar.
    """
    def __init__(self, re, total, fgcol, parent=None, text=''):
        """@re is the ocemgui renderer
        @total is the total number of exercises.
        @fgcol is the foreground color (RGB).
        """
        self.logger = logging.getLogger("schoolsplay.SPocwWidgets.ExeCounter")
        self._re = re
        self.total = total
        self.done = 0
        self.fgcol = fgcol
        self.size = 60
        self.__parent = parent
        if not text:
            text = _("Exercises")
        self._frm = ocw.VFrame()
        self._frm.topleft = (CBXC[-5], 10)
        
        if len(text) > 14:#prevent to large label when localized
            text = text[:14]
        lbl = ocw.Label(text)
        lbl.create_style()
        lbl.style["font"]["size"] = P_TTFSIZE
        self._frm.add_child(lbl)
        
        self._lbl = ocw.Label("%s/%s" % (self.total, self.done))
        self._lbl.create_style()
        self._lbl.style["font"]["size"] = P_TTFSIZE
        self._frm.add_child(self._lbl)
        
        self._re.add_widget(self._frm)
        self._re.update() 
    
    def increase_counter(self):
        """Increase the 'done' part of the counter.
        When the 'done' part is equal to the 'total' part no increase
        is performed."""
        if self.done == self.total:
            return
        self.done += 1
        text = "%s/%s" % (self.done, self.total)
        self._lbl.set_text(text)
        if self.__parent:# needed when run by the SP core
            self.__parent.update_renderer()
    
    def reset_counter(self, total):
        """Reset the total counter to @total.
        The 'done' part is reset to zero.
        """
        self.total = total
        self.done = -1
        self.increase_counter()
        
    def erase(self):
        """This will remove the widgets from the renderer.
        """
        self.logger.debug("erase called")
        self._re.remove_widget(self._frm)
        self._re.update()
        
if __name__ == "__main__":
    import SPLogging
    SPLogging.set_level('debug')
    SPLogging.start()
    from SPSpriteUtils import SPInit
    
    import utils
    utils.set_locale()
    LOCALE_RTL = get_locale()[1]
    if LOCALE_RTL:
        ALIGN = ocwc.ALIGN_RIGHT
    else:
        ALIGN = ocwc.ALIGN_LEFT
        
    def exit():
        d = ExitDialog(re)
        result = d.run()
        print "result", result
        # this quit with an exception but I don't care as it's only test code.
        pygame.quit()
        
    # needed to simulate gettext
    import __builtin__
    __builtin__.__dict__['_'] = lambda x:x
        
    pygame.init()
    size = (800, 600)
    scr = pygame.display.set_mode(size)
    scr.fill((200, 100, 100))
    pygame.display.update()
    
    re = ocw.Renderer()
    re.set_screen(scr)
    
    ec = ExeCounter(re, 20, (0, 0, 255))
    i = 10
    while i:
        ec.increase_counter()
        pygame.time.wait(300)
        i -= 1
    ec.reset_counter(20)
    
    txt = ["This is a info text\nline 2\nline3"]
    d = InfoDialog(re, txt)
    result = d.run()
    print "result", result
    
    print "add graph to a dialog"
    # dates are like this 07-09-09_10:44:27
    # we ditch the second part
    data = [('07-09-09_10:44', 3.899), \
        ('07-09-09_11:44', 4.867), \
        ('07-09-09_12:44', 5.34), \
        ('07-09-09_13:44', 6.36), \
        ('07-09-09_14:44', 6.5), \
        ('07-09-09_15:44', 6.5), \
        ('07-09-10_10:44', 5.90), \
        ('07-09-10_10:34', 4.896), \
        ('07-09-10_10:20', 3.20)]
    
    s = Graph(data, 1, norm=(5, 50), headertext='Generated by Childsplay_sp 0.7 for the foobar activity').get_surface()
    ilbl = ocw.ImageLabel(s)
    d = GraphDialog(re, ilbl, savebutton=True)
    result = d.run()
    print "result", result
    if result:
        # True means save button is hit.
        path = os.path.join('/tmp', '%s.BMP' % 'test')
        pygame.image.save(s, path)
    
    lb = Label(re, "this is a label", (100, 100))
    
    actives = SPInit(scr, scr.convert())
    ent = SPEntry((100, 300), 8)
    actives.add(ent)
    ent.display_sprite()
    result = None
    while 1:
        pygame.event.pump()
        events = pygame.event.get()
        for event in events:
            if event.type is KEYDOWN:
                result = actives.refresh(event)
                break
        if result:
            print ent.get_text()
            break
        pygame.time.wait(100)
    
    tt = ToolTip()
    but = ocw.Button ("Move the mouse over me, click to quit, 0123456789")
    but.topleft = (100, 400)
    but.tooltip = "An enhanced description"
    but.connect_signal(ocwc.SIG_ENTER, tt._make_tooltip, but.tooltip, re)
    but.connect_signal(ocwc.SIG_LEAVE, tt._destroy_tooltip)
    but.connect_signal(ocwc.SIG_CLICKED, exit)
    re.add_widget(but)
    re.start()
    
