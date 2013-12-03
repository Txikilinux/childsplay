# -*- coding: utf-8 -*-

# Copyright (c) 2006 Stas Zykiewicz <stas.zytkiewicz@schoolsplay.org>
#
#           SPgdm.py
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

# Graphical login manager, like the gdm.
# The difference is that this is started by schoolsplay DataManager much like a splash screen.
# There will be an option for SP to disable this and run in a anonymous version.

# Start SP like this to disable the login stuff: schoolsplay --anonymous

import logging
import os
module_logger = logging.getLogger("childsplay.SPgdm")

from SPConstants import *
from SPSpriteUtils import SPInit

from utils import char2surf, load_image

CORE_BUTTONS_XCOORDS = range(6, 790, 88)

import pygame

from pygame.constants import *

#import childsplay_sp.ocempgui.widgets as ocw
#import childsplay_sp.ocempgui.widgets.Constants as ocwc

if __name__ == '__main__':
    # needed to simulate gettext
    import __builtin__
    __builtin__.__dict__['_'] = lambda x:x
        
#from SPocwWidgets import InfoDialog, ExitDialog, SPEntry, SPLabel
#from SPVirtualkeyboard import VTKEscapeKeyException
import SPHelpText
import Version

# Load the ocempgui theme.
# TODO" make ocw theme configurable
# TODO: this is not working
#ocw.base.GlobalStyle.load (os.path.join(ACTIVITYDATADIR,'ocw','themes','schoolsplay.rc'))

class GDMEscapeKeyException(Exception):
    """ This is raised from the activity_loop when the user hits escape.
    We basically using this exception as a signal"""
    pass
    
class SPGreeter:
    """Starts a login screen, this will be a window, not fullscreen.
    """
    def __init__(self, cmd_options, theme='default', vtkb=None, fullscr=None):
        global ACTIVITYDATADIR
        self.logger = logging.getLogger("childsplay.SPgdm.SPGreeter")
        self.logger.debug("Starting")
        self.cmd_options = cmd_options
        self.__name = ''
        captxt = _("Childsplay_sp login")
        if self.cmd_options.theme != 'default':
            captxt = captxt.replace('Childsplay_sp', self.cmd_options.theme)
        ICONPATH = os.path.join(ACTIVITYDATADIR, 'SPData', 'themes', self.cmd_options.theme)
        DEFAULTICONPATH = os.path.join(ACTIVITYDATADIR, 'SPData', 'themes', 'default')
        self.vtkb = vtkb# is used in the _run_loop
        # setup screen
        size = (800, 600)
        if fullscr:
            self.screen = pygame.display.set_mode(size, FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(size)
        p = os.path.join(ICONPATH, 'spgdm_back.png')
        if not os.path.exists(p):
            p = os.path.join(DEFAULTICONPATH, 'spgdm_back.png')
        back = load_image(p)
        self.screen.blit(back, (0, 0))
        # get the version image
        vs = "Childsplay_sp version: %s" % Version.version
        if self.cmd_options.theme != 'default':
            vs = vs.replace('Childsplay_sp', self.cmd_options.theme)
        if self.cmd_options.adminmode:
            vs = vs + " (Adminmode)"
        vsurf = char2surf(vs, TTFSIZE-4, (0, 0, 0), ttf=TTF, bold=True, antialias=False)
        self.screen.blit(vsurf, (300, 0))
        
        self.actives = SPInit(self.screen, self.screen.convert())
        
        pygame.display.set_caption(captxt.encode('utf-8'))

        # setup our SP widgets
        label = SPLabel(_("Username:"), fontsize=TTFSIZE + 2)
        label.moveto((340, 250))
        self.actives.add(label)
        
        self.entry = SPEntry((340, 280), 9)
        self.entry.display_sprite()
        self.actives.add(self.entry)
        
        # setup ocempgui widgets
        self.renderer = ocw.Renderer()
        self.renderer.set_screen(self.screen)
        p = os.path.join(ICONPATH, 'spgdm_login_button.png')
        if not os.path.exists(p):
            p = os.path.join(DEFAULTICONPATH, 'spgdm_login_button.png')
        but = ocw.ImageButton(p)
        # The button resize accoording to the string size, this sucks.
        # We now must check the tring length to prevent the button from overflowing :-)
        # Looks like the C days are here again :-D
        t = _("Login")
        but.set_text(t)# we set the fontsize below
        
        but.child.create_style()
        but.child.style["font"]["size"] = TTFSIZE
        but.child.style['bgcolor'][ocwc.STATE_NORMAL] = KOBALT_LIGHT_BLUE
        but.create_style()['bgcolor'][ocwc.STATE_NORMAL] = KOBALT_LIGHT_BLUE
        but.connect_signal(ocwc.SIG_CLICKED, self._login_button_callback, self.entry)
        #but.opacity = 255
        but.topleft = (340, 320)
        # We clear the event queue as we sometimes get an crash with the message
        # error: Event queue full
        # Nothing to be found on Google so I've put a clear before the error
        # was generated.
        pygame.event.clear()
        self.renderer.add_widget(but)
        
        # logout button
        p = os.path.join(ICONPATH, 'spgdm_quit_button.png')
        if not os.path.exists(p):
            p = os.path.join(DEFAULTICONPATH, 'spgdm_quit_button.png')
        but = ocw.ImageButton(p)
        but.create_style()['bgcolor'][ocwc.STATE_NORMAL] = KOBALT_LIGHT_BLUE
        but.connect_signal(ocwc.SIG_CLICKED, self._quit_button_callback, but)
        #but.opacity = 180
        but.topleft = (720, 520)
        self.renderer.add_widget(but)
        
        # info button
        p = os.path.join(ICONPATH, 'spgdm_info_button.png')
        if not os.path.exists(p):
            p = os.path.join(DEFAULTICONPATH, 'spgdm_info_button.png')
        but = ocw.ImageButton(p)
        #but.set_text(_("Quit"))
        #but.child.create_style()["font"]["size"] = 36
        but.create_style()['bgcolor'][ocwc.STATE_NORMAL] = KOBALT_LIGHT_BLUE
        but.connect_signal(ocwc.SIG_CLICKED, self._info_button_callback, but)
        #but.opacity = 180
        but.topleft = (20, 520)
        self.renderer.add_widget(but)
        
        self.clock = pygame.time.Clock()
        self.runloop = True
        
        pygame.display.update()
        # run the virtual keyboard if we have one.
        if self.vtkb:
            self._run_vtkb_loop(self.renderer)
        else:
            # else we run a 'normal' loop.
            self._run_loop()
        
    def _run_loop(self):
        #self.runloop=0 # Used when profiling this module
        while self.runloop:
            self.clock.tick(30)
            pygame.event.pump()
            events = pygame.event.get()
            for event in events:
                if event.type is KEYDOWN and event.key is K_ESCAPE or event.type is QUIT:
                    self.run_event_loop = False
                    self._quit_button_callback(None)
                elif event.type is KEYDOWN:
                    if self.actives.refresh(event):
                        self._login_button_callback(self.entry)
            self.renderer.distribute_events( * events)
            
            
    def _run_vtkb_loop(self, parent_re=None):
        self.vtkb.show()
        kb = self.vtkb.echo_run(parent_re=[parent_re, self.renderer])
        word = []
        while self.runloop:
            try:
                k = kb.next()# this will return a string or none
                if k and k not in ('quit', 'enter'):# user hits anything but None, enter or escape
                    word.append(k)
                    self.entry.set_text(''.join(word))
                elif k == 'quit':# user hits escape
                    self._quit_button_callback()
                    break
                elif k == 'enter':
                    break
            except (StopIteration, VTKEscapeKeyException):
                self._quit_button_callback()
                break
                
    def _login_button_callback(self, entry):
        self.logger.debug("_login_button_callback called with %s" % entry)
        self.__name = entry.text
        self.runloop = False

    def _quit_button_callback(self,  * args):
        self.logger.debug("_quit_button_callback called")
        if not self.cmd_options.noexitquestion:
            dlg = ExitDialog(self.renderer)
            c = dlg.run()
        else:
            c = 0
        if c == 0:
            self.logger.info("User wants exit")
            raise GDMEscapeKeyException # let schoolsplay.py decide what next

    def _info_button_callback(self, but):
        self.logger.debug("_info_button_callback called")
        d = InfoDialog(self.renderer, SPHelpText.SPgdm._info_button_callback)
        d.run()

    def get_loginname(self):
        return self.__name
        
if __name__ == '__main__':
    def main():
        class Fake:
            adminmode = False
            theme = 'default'
            noexitquestion = None
        try:
            g = SPGreeter(Fake())
        except GDMEscapeKeyException:
            pass
        else:
            print "got name: %s" % g.get_loginname()

    import cProfile
    prof = cProfile.run('main()','profiler_out_0')
 
    
        


