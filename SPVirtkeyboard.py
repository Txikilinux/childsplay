# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zykiewicz <stas.zytkiewicz@schoolsplay.org>
# 
#           SPVirtkeyboard.py
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
import logging
import random
import pygame
from pygame.constants import *

import SPWidgets
from SPConstants import *
import utils
import SPVirtkeyboardMap as VKM

KEYCOL = 45, 83, 152 

class SuperKey(SPWidgets.ImgButton):
    def __init__(self, s, pos, pad, value):
        SPWidgets.ImgButton.__init__(self, s, pos, pad, value)
    
class Key(SuperKey):
    def __init__(self, value, pos, obs, fsize=28, butsize=(48, 48)):
        ci = utils.char2surf(value,fsize, WHITE, ttf=TTFBOLD)
        s = pygame.Surface(butsize)
        s.fill(KEYCOL)
        pygame.draw.rect(s, WHITE, s.get_rect(), 1)
        cir = ci.get_rect()
        cir.center = s.get_rect().center
        s.blit(ci, cir)
        
        SuperKey.__init__(self, s, pos, 4, value)
        self.connect_callback(obs, MOUSEBUTTONUP, value)

class SpaceKey(SuperKey):
    def __init__(self, pos, obs, butsize=(100, 48)):
        s = pygame.Surface(butsize)
        s.fill(KEYCOL)
        pygame.draw.rect(s, WHITE, s.get_rect(), 1)
        
        SuperKey.__init__(self, s, pos, 4, 'space')
        self.connect_callback(obs, MOUSEBUTTONUP, 'space')

class BackspaceKey(SuperKey):
    def __init__(self, pos, obs, butsize=(100, 50)):
        s = pygame.Surface(butsize)
        s.fill(KEYCOL)
        
        pygame.draw.rect(s, WHITE, s.get_rect(), 1)
        pygame.draw.line(s, WHITE, (15,31), (92,31),2)
        pygame.draw.line(s, WHITE, (15,31), (20,26),2)
        pygame.draw.line(s, WHITE, (15,32), (20,37),2)
        
        SuperKey.__init__(self, s, pos, 4, 'backspace')
        self.connect_callback(obs, MOUSEBUTTONUP, 'backspace')

class EnterKey(SuperKey):
    def __init__(self, pos, obs, fsize=28, butsize=(100, 104)):
        text = utils.char2surf("Enter", fsize, WHITE, ttf=TTFBOLD)
        textpos = text.get_rect()
        s = pygame.Surface(butsize)
        s.fill(KEYCOL)
        sr = s.get_rect()
        blockoffx = (sr.width / 2)
        blockoffy = (sr.height / 2)
        offsetx = blockoffx - (textpos.width / 2)
        offsety = blockoffy - (textpos.height / 2) + 8 
        s.blit(text,(offsetx, (offsety-30)))
        
        pygame.draw.rect(s, WHITE, s.get_rect(), 1)
        pygame.draw.line(s, WHITE, (80,71), (80,81),2)
        pygame.draw.line(s, WHITE, (80,81), (25,81),2)
        pygame.draw.line(s, WHITE, (25,81), (30,76),2)
        pygame.draw.line(s, WHITE, (25,82), (30,87),2)
        
        SuperKey.__init__(self, s, pos, 4, 'enter')
        self.connect_callback(obs, MOUSEBUTTONUP, 'enter')


class ShiftKey(SuperKey):
    def __init__(self, pos, obs, fsize=28, butsize=(48, 48)):
        s = pygame.Surface(butsize)
        s.fill(KEYCOL)
        sr = s.get_rect()
        
        pygame.draw.rect(s, WHITE, s.get_rect(), 1)
        pygame.draw.line(s, WHITE, (22, 10), (22,36),2)
        pygame.draw.line(s, WHITE, (22, 10), (16,16),2)
        pygame.draw.line(s, WHITE, (22, 10), (28,16),2)
        
        SuperKey.__init__(self, s, pos, 4, 'shift')
        self.connect_callback(obs, MOUSEBUTTONUP, 'shift')

class KeyBoard(SPWidgets.Widget):
    """Class which provides a virtual on screen keyboard for use on touchscreens or
    in a kioskmode system.
    """
    def __init__(self, cbf, actives, keyboard_mode='qwerty', password_mode=False,\
                  wordcompletion=None, threshold=3, maxanswers=10, \
                  theme='default', position=(0, 100), \
                  display_position=(0, 0), maxlen=22, display_length=0, display=True):
        """This class provides a onscreen keyboard (670x225) with keys that are 
        placed in a SPGroup so that you can incorporate in your eventloop.
        The caller must call the update method on this group.
        The keyboard doesn't have an eventloop.
        The mandatory callback function must be able receive the following data from this object:
            self and a string with the text entered by the user when the user hits Enter.
            self and a list with strings from the wordcompleter if used.
        After Enter is clicked the widget is still fully functional.
        
        cbf - The callback function to call when the user hits enter.
        actives - A SPGroup instance.
        keyboard_mode - Define layout, possible values: 'qwerty', 'qwerty_square',
                    'numbers', 'abc','abc_square'
        password_mode - Boolean. Characters entered will be displayed as stars.
        wordcompletion - WordCompleter instance or None. (only used if threshold > 0)
        threshold - Threshold value for wordcompletion. (0 means no wordcompletion) 
        maxanswers - The maximum number of completion suggestions. (defaults to 10)
        theme - Theme used. Values taken from SPData/base/themes/core.rc
        display_position - position in x,y coords for the text display.
        display_length - length of the display in pixels. 0 means equal to the keyboard length.
        maxlen - number of characters to display.
        display - If normal display is to be used. When set to None the entry which has
         the input focus. You must make sure to set some entry widget to have the input focus
         otherwise nothing is shown.
        """
        SPWidgets.Widget.__init__(self)
        self.logger = logging.getLogger("childsplay.SPVirtkeyboard.Keyboard")
        self.cbf = cbf
        self.position = position
        self.password_mode = password_mode
        self.maxlen = maxlen
        self.display_length = display_length
        self.display_position = display_position
        self.actives = actives
        self.display = display
        self._ShiftActive = False
        self._KeepDisplay = False
        self.keyboard_mode = keyboard_mode
        self.set_keymap()
        # wordcompleter related stuff.
        if threshold == 0:
            self.WC = None
        else:
            self.WC = wordcompletion
        self.threshold = threshold
        self.text = ''# we also keep text in TI but local is faster (for wordcompletion)
        self.maxanswers = maxanswers
        self._IamShowed = False
                
    def set_keymap(self):
        kbmap = self.keyboard_mode
        if kbmap == 'qwerty':
            map = VKM.Qwerty()
        elif kbmap == 'abc':
            map = VKM.Abc()
        elif kbmap == 'numbers':
            map = VKM.Numbers()
        elif kbmap == 'qwerty_square':
            map = VKM.QwertySquare()
        elif kbmap == 'abc_square':
            map = VKM.AbcSquare()
        elif kbmap == 'abc_minus':
            map = VKM.AbcMinus()
        elif kbmap == 'qwerty_minus':
            map = VKM.QwertyMinus()
        but_x,  but_y = 56, 56
                # setup keys
        x = self.position[0]
        y = self.position[1]
        extrakeys_pos = []
        self.keys = []
        for line in map.getlines():
            for k in line:
                if self._ShiftActive:
                    k = k.upper()
                else:
                    k = k.lower()
                k = Key(k,(x, y), self.observer)
                self.keys.append(k)
                x += but_x
            extrakeys_pos.append((x, y))
            x = self.position[0]
            y += but_y
        # bacspace
        kb = BackspaceKey(extrakeys_pos[0], self.observer)
        self.keys.append(kb)
        
        # enter
        ke = EnterKey(extrakeys_pos[1], self.observer)
        self.keys.append(ke)
        
        # space
        if map != 'numbers':
            ks = SpaceKey(extrakeys_pos[3], self.observer)
            ksh = ShiftKey((extrakeys_pos[3][0] + ks.rect.w, extrakeys_pos[3][1]),\
                                            self.observer)
            self.keys += [ks, ksh]
            
        correction = 8
        if self.display_length == 0:
            self.display_length = extrakeys_pos[0][0] - x + kb.get_sprite_width() - correction    
        # setup the text display
        if self._KeepDisplay:
            return
        if self.display:
            self.TI = SPWidgets.TextEntry(pos=self.display_position, \
                            length=self.display_length, maxlen=self.maxlen, \
                            message='', fsize = 28, border=True, ttf=TTFBOLD, \
                            fgcol=BLACK, password_mode=self.password_mode)
            self.actives.set_input_focus(self.TI)
        else:
            self.TI = self.actives.who_has_input_focus()
            self._KeepDisplay = True

    def _set_firstletter(self, c, snd):
        # special attributes set in TextEntry, only used by various Argos acts.
        self.TI._fl = c.upper()
        self.TI._snd = snd
        
    def show(self):
        for b in self.keys:
            b.display_sprite()
        self.TI.display_sprite()
        if self._IamShowed:
            return
        else:
            self.actives.add(self.keys)
            if not self._KeepDisplay:
                self.actives.add(self.TI)
            self._IamShowed = True
        
    def hide(self):
        for b in self.keys:
            b.erase_sprite()
        if  not self._KeepDisplay:
            self.TI.erase_sprite()
        if not self._IamShowed:
            return
        else:
            self.actives.remove(self.keys)
            if not self._KeepDisplay:
                self.actives.remove(self.TI)
            self._IamShowed = False
    
    def visible(self):
        return self._IamShowed
        
    def destroy(self):
        self.clear_display()
        self.hide()
    
    def clear_display(self):
        self.TI.clear()
    
    def observer(self, widget, event, data):
        """Notified by the key class"""
        if self.TI is not self.actives.who_has_input_focus():
            self.TI = self.actives.who_has_input_focus()
        c = data[0]
        if c == 'space':
            c = ' '
            self.TI.add(c)
        elif c == 'backspace':
            self.TI.backspace()
            text = self.TI.get_text().lower()
            if self.WC and len(text) >= self.threshold:
                ans = self.WC.get_answers(text, self.maxanswers)
                self.cbf(self, ans)
        elif c == 'enter':
            # notify our parent observer
            result = self.cbf(self, self.get_text())
            if result:
                self.hide()
        elif c == 'shift':
            self._KeepDisplay = True
            if self._ShiftActive:
                self._ShiftActive = False
                self.hide()
                self.set_keymap()
                self.show()
            else:
                self._ShiftActive = True
                self.hide()
                self.set_keymap()
                self.show()
        else:
            if self._ShiftActive:
                self._ShiftActive = False
                self.hide()
                self.set_keymap()
                self.show()
            self.TI.add(c)
            text = self.TI.get_text().lower()
            if self.WC and len(text) >= self.threshold:
                ans = self.WC.get_answers(text, self.maxanswers)
                self.cbf(self, ans)
                
    def get_text(self):
        return self.TI.get_text()
        
    def toggle_numbers(self, value):
        pass
        
        
class WordCompleter:
    """Class which provides word completion.
    """
    def __init__(self, wordlist, firstletter=''):
        """All the words from the list are converted to lowercase and doubles
        are removed.
        wordlist - list with strings
        firstletter - one character string indicating for which letter we look for suggestions."""
        if firstletter:
            self._firstletter = firstletter.lower()
        else:
            self._firstletter = None
        self.set_wordlist(wordlist)
    
    def set_wordlist(self, wordlist):
        self.words = {}
        self.wordlist = wordlist
        for w in wordlist:
            w = w.lower()
            if not self.words.has_key(w[0]):
                self.words[w[0]] = [w]
            else:
                self.words[w[0]].append(w)
    
    def set_firstletter(self, c):
        if not c:
            self._firstletter = None
        else:
            self._firstletter = c.lower()
    
    def get_answers(self, part, max=0):
        """Get suggestions from the wordlist based on the string @part.
        part is the partial string.
        max - the number of possible answers we should return.
        More answers means more lookup time.
        Most of the time 10 answers is more than enough.
        0 means all answers"""
        answers = []
        #print self._firstletter
        if not self._firstletter:
            self._firstletter = part[0].lower()
        if part[0].lower() != self._firstletter:
            return []
        try:
            for k in self.words[part[0].lower()]:
                if k.startswith(part):
                    if k[-1] == '\n':
                        k = k[:-1]
                    answers.append(k)
        except KeyError:
            answers = []
        else:
            if max:
                try:
                    foundanswers = random.sample(answers, max)
                except ValueError:
                    pass
                else:
                    return foundanswers
            return answers
        return []

    def lookup(self, word):
        """Check to see if @word is part of the wordlist.
        The words in the wordlist must end with a \n, not \r\n
        Returns True of False."""
        if not word or not self._firstletter:
            return None
        if 47 < ord(word[0]) < 58:
            # The first letter is a number 
            return True
        return word+'\n' in self.words[self._firstletter]


if __name__ == '__main__':
    
    import __builtin__
    __builtin__.__dict__['_'] = lambda x:x
    
    import SPLogging
    SPLogging.set_level('debug')
    SPLogging.start()
    import psyco
    psyco.full()
#    f = open('dictionary_nl.txt', 'r')
#    wordlist = f.readlines()
#    f.close()
    wordlist = []
    wc = WordCompleter(wordlist)
    print wc.get_answers('aa')
    
    import pygame
    from pygame.constants import *
    pygame.init()
    
    from SPSpriteUtils import SPInit
    
    scr = pygame.display.set_mode((800, 600))
    scr.fill((135,206,250))
    
    back = scr.convert()
    s = utils.char2surf("Hit ESC to cycle trough the layouts, F1 to quit", 24)
    scr.blit(s, (20, 10))
    
    actives = SPInit(scr, back)
    
    pygame.display.flip() 
    
    SPWidgets.Init('braintrainer')
    
    def cbf(parent, data):
        print "cbf called with: ", parent, data
    
    kb = None
    for layout in ('qwerty', 'qwerty_square','numbers', 'abc', 'abc_square'):
        if kb:
            kb.hide()
        actives.empty()
        kb = KeyBoard(cbf, actives, keyboard_mode=layout, position=(80, 210), \
                      wordcompletion=wc, threshold=2, \
                      display_position=(80, 160), display_length=0, \
                      password_mode=False)
        kb.show()
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
                        sys.exit(0)
                else:
                    actives.update(event)
    
