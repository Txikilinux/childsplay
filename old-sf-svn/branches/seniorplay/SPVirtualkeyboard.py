# -*- coding: utf-8 -*-

# Copyright (c) 2006 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           virt_keyboard.py
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 of the GNU General Public License
# as published by the Free Software Foundation. A copy of this license should
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

# Provides a virtual keyboard to be used in a kiosk mode.
import pygame

from pygame.constants import *

import childsplay_sp.ocempgui.widgets as ocw
import childsplay_sp.ocempgui.widgets.Constants as ocwc

import utils
#from SPConstants import *

num_line0 = ('1','2','3','4','5','6','7','8','9','0')
chars_line1 = ('Q','W','E','R','T','Y','U','I','O','P')
chars_line2 = ('A','S','D','F','G','H','J','K','L',' . ')
chars_line3 = ('Z','X','C','V','B','N','M','_',' - ')

class VTKEscapeKeyException(Exception):
    """ This is raised from the activity_loop when the user hits escape.
    We basically using this exception as a signal"""
    pass
class EnterKeyException(Exception):
    """Raised when the user hits enter in the virt_keyboard"""
    pass

class Input:
    def __init__(self):
        self.clear()
    def clear(self):
        self.word = []
        self.last_entry = ''
    def get_input(self):
        return ''.join(self.word)
    def get_entry(self):
        return self.last_entry
    def add_input(self,c):
        self.last_entry = c
        if c == 'Enter':
            raise EnterKeyException
        elif c == 'Esc':
            raise VTKEscapeKeyException
        self.word.append(c)
        

class Key:
    def __init__(self,c,input,fsize=18):
        ci = utils.char2surf(c,fsize)
        self.button = ocw.ImageButton(ci)
        # but is connected to a input instance so this button and the input object
        # take card of the handling of the users input 
        self.button.connect_signal(ocwc.SIG_CLICKED,input.add_input,c)

class VirtualKeyboard:
    """Provides a 'virtual keyboard' which can be used in a kiosk mode system.
    This class uses ocempgui lib to construct a qwerty keyboard
    with 0-9 and 'enter'.
    It will call pygame.display.update to update the scr and starts a eventloop
    which will return the characters given by the user.
    The behaviour is a bit like a GTK dialog which means you have to construct
    it and then call the 'run' method which will take over the events queue.
    When the run method returns you must destroy or hide the object.
    Be aware that this object uses a lot of resources so make sure you don't
    keep references to it but destroy it when you done with it.
    
    Special notice about game modules.
    Don't call this class directly but use the make_vkb method from the 
    ChildsplayGoodies instance"""
    def __init__(self,screen,fsize=18,pos=(0,0)):
        self.re = ocw.Renderer()
        self.re.screen = screen
        self.input = Input()
        self.clock = pygame.time.Clock()
        self.fsize = fsize
        # setup keys
        del_key = Key('Del',self.input,self.fsize)
        space_key = Key('Space', self.input,self.fsize)
        enter_key = Key('Enter',self.input,self.fsize)
        esc_key = Key('Esc',self.input,self.fsize)
        self.table = ocw.Table(4,11)
        self.table.topleft = pos
        x = 0
        y = 0
        for k in num_line0:
            k = Key(k,self.input,self.fsize)
            self.table.add_child(y,x,k.button)
            x += 1
        
        x,y = 0,1
        for k in chars_line1:
            k = Key(k,self.input,self.fsize)
            self.table.add_child(y,x,k.button)
            x += 1
        
        x,y = 0,2
        for k in chars_line2:
            k = Key(k,self.input,self.fsize)
            self.table.add_child(y,x,k.button)
            x += 1
        
        x,y = 0,3
        for k in chars_line3:
            k = Key(k,self.input,self.fsize)
            self.table.add_child(y,x,k.button)
            x += 1
        # add esc key at the beginning of line 1
        self.table.set_align (0,10, ocwc.ALIGN_LEFT)
        self.table.add_child(0,10,esc_key.button)
        # add del key at the end of line 2
        self.table.set_align (1,10, ocwc.ALIGN_LEFT)
        self.table.add_child(1,10,del_key.button)
        # add the space key at the end of line 3
        self.table.set_align (2,10, ocwc.ALIGN_LEFT)
        self.table.add_child(2,10,enter_key.button)
        # add the enter key at the end of line 4
        self.table.add_child(3,10,space_key.button)
        
    def get_input(self):
        return self.input.get_input()

    def show(self):
        """Shows the kb"""
        self.re.add_widget(self.table)
        self.re.update()
        
    def hide(self):
        """Hides the kb instead of destroying it. Usefull on slower systems
        were the creation of the kb can be slow"""
        self.input.clear()
        self.re.remove_widget(self.table)
        self.re.update()
    def destroy(self):
        """Clears and destroys the keyboard. You must create a new one after this call"""
        self.hide()
        self.table = None
        self.re = None
    def run(self,chars=0):
        """ Starts the eventloop and only returns when yhe user hits 'enter'
        or 'esc' on the virtual keyboard or when the user hits 'escape' on the
        real keyboard. If you want to 'echo' the keys use the run_echo method.
        When the loop exits it will return the kb values in a string.
        @chars is the number of chars the user can click. (not yet ready)
            0 means until the user hits 'enter'
            1.. means until the number is reached.
            -1 means one char without hitting enter."""
        self.runloop = 1
        while self.runloop:
            self.clock.tick(30)
            pygame.event.pump()
            events = pygame.event.get()
            for event in events:
                if event.type is KEYDOWN and event.key is K_ESCAPE:
                    self.run_event_loop = False
                    raise VTKEscapeKeyException
            # let ocempgui handles the gui events, if needed
            # renderer loops the events
            try:
                self.re.distribute_events(*events)       
            except EnterKeyException:
                self.runloop = 0
    def echo_run(self,chars=0,parent_re=None):
        """ Starts the eventloop and returns when the user hits 'enter'
        or 'esc' on the virtual keyboard or when the user hits 'escape' on the
        real keyboard. The return code in case of a 'enter' or 'esc' will be the
        string 'quit'. The escape keyboard key raises a exception.
        This method will return a generator object so you have to iterate over it
        in a loop. It will return each key entered by the user.
        (See at the bottom of this module for an example)
        @parent_re is a list with the renderer of the caller or a list of renderers.
        In case you have other ocempgui widgets you want to update you can pass
        your renderers and it's distribute_events will be called.
        @chars is the number of chars the user can click. (not yet ready)
            0 means until the user hits 'enter'
            1.. means until the number is reached.
            -1 means one char without hitting enter."""
        self.runloop = 1
        self.current_entry = ''
        while self.runloop:
            self.clock.tick(30)
            pygame.event.pump()
            events = pygame.event.get()
            for event in events:
                if event.type is KEYDOWN and event.key is K_ESCAPE:
                    self.run_event_loop = False
                    raise VTKEscapeKeyException
            # let ocempgui handles the gui events, if needed
            # renderer loops the events
            try:
                self.re.distribute_events(*events) 
                if parent_re:
                    for r in parent_re:
                        r.distribute_events(*events)
            except EnterKeyException:
                self.runloop = 0
            except VTKEscapeKeyException:
                yield 'quit'
            key_entry = self.input.get_entry()
            if key_entry == 'Enter':
                yield 'enter'
            elif key_entry == 'Esc':
                yield 'quit'
            if self.current_entry != key_entry:
                self.current_entry = key_entry
                yield self.current_entry
            yield ''    

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((800,600),0)
    pos = (100,100)
    fsize = 22
    vkb = VirtualKeyboard(screen,fsize,pos)
    vkb.show()
    try:
        print "start with run"
        vkb.run()
        word = vkb.get_input()
        print "input:",word
        vkb.hide()
        print "vkb hidden and wait 1 sec then we switch to echo_run"
        pygame.time.wait(1000)
        vkb.show()
        runloop = 1
        kb = vkb.echo_run()
        while 1:
            k = kb.next()
            if k and k != 'quit':
                print "user hits",k
            elif k == 'quit':
                break
            
    except VTKEscapeKeyException:
        print "user hits escape"
    
