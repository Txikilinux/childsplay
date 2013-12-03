# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zykiewicz <stas.zytkiewicz@schoolsplay.org>
#
#           SPMoviePlayer.py
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

import pygame
from pygame.constants import *
from SPWidgets import Button, Label
import logging
from SPColors import *
from SPSpriteUtils import SPSprite

class MoviePlayer:
    def __init__(self, file, actives, rect, observer, hidebuttons=False):
        """rect must be a pygame.Rect indicating the position and screen size the player
        can use for the movie and buttons.
        TODO: add more info"""
        self.logger = logging.getLogger('schoolsplay.SPMoviePlayer.MoviePlayer')
        self.maxW = rect.width
        butH = 50
        self.maxH = rect.height - butH # leave room for buttons
        self.observer = observer
        self.posX,  self.posY = rect.topleft
        self.actives = actives
        self.file = file 
        
        self._movie = pygame.movie.Movie(file)
        w, h = self._movie.get_size()
        w = min(int(w * 1.3 + 0.5), self.maxW)
        h = min(int(h * 1.3 + 0.5), self.maxH)
        self._surf = pygame.Surface((w, h))
        pygame.draw.rect(self._surf, GREY, self._surf.get_rect(), 4)
        self._movie.set_display(self._surf, pygame.Rect(4, 4, w-8, h-8))
        
        self.butlist = []       
        # TODO: these coords are hardcoded and depend on a certain surf size.
        # make it dynamic
        y = self.posY + self.maxH +10
        butXpos = (self.posX + 60, self.posX + 170, self.posX + 340, self.posX + 510)
        
        # TODO: We should use images iso text
        but = Button('Quit', (butXpos[0], y), padding=6)
        but.connect_callback(self._on_quit_but_cbf, MOUSEBUTTONDOWN)
        self.butlist.append(but)
        
        but = Button('Play movie', (butXpos[1], y), padding=6)
        but.connect_callback(self._on_play_movie_but_cbf, MOUSEBUTTONDOWN)
        self.butlist.append(but)
        
        but = Button('Pause movie', (butXpos[2], y), padding=6)
        but.connect_callback(self._on_pause_movie_but_cbf, MOUSEBUTTONDOWN)
        self.butlist.append(but)
        
        if not hidebuttons:
            self.show_buttons()

    def _on_quit_but_cbf(self, *args):
        self.logger.debug('on_quit_but_cbf called')
        self._stop()
        self._surf.fill(BLACK)
        self.observer('stop')
        
    def _on_play_movie_but_cbf(self, *args):
        self.logger.debug('_on_play_movie_but_cbf called')
        if not self._movie.get_busy():
            self._pause()
            
    def _on_pause_movie_but_cbf(self, *args):
        self.logger.debug('_on_pause_movie_but_cbf called')
        self._pause()
    
    def _stop(self):
        if self._movie.get_busy():
            self._movie.stop()
        pygame.mixer.init()
    
    def _pause(self):
        self._movie.pause()
    
    def start(self):
        pygame.mixer.quit()
        self._movie.set_volume(1.0)
        self._movie.play()
        
    def stop(self):
        self._on_quit_but_cbf()
    
    def hide_buttons(self):
        self.actives.remove(self.butlist)
        for s in self.butlist:
            s.erase_sprite()
            
    def show_buttons(self):
        self.actives.add(self.butlist)
        for s in self.butlist:
            s.display_sprite()
    
    def get_movie_surface(self):
        return self._surf

if __name__ == '__main__':
    
    import __builtin__
    __builtin__.__dict__['_'] = lambda x:x
    
    import SPLogging
    SPLogging.set_level('debug')
    SPLogging.start()
    
    from SPWidgets import Init
    
    import pygame
    from pygame.constants import *
    pygame.init() 
    
    from SPSpriteUtils import SPInit
 
    scr = pygame.display.set_mode((800, 600))
    back = scr.convert()
    actives = SPInit(scr, back)
    
    Init('seniorplay')
    
    def observer(state):
        global runloop
        print "observer called with state", state
        if state == 'stop':
            runloop = 0
    
    ####### movieplayer stuff, the rest is crap to mimic a CP environment ##########
    mprect = pygame.Rect(0, 80, 800, 500)
    mppos = mprect.topleft
    hidebuttons = False
    mp = MoviePlayer('test1.mpg', actives, mprect, observer, hidebuttons)
    mp.start()
    msurf = mp.get_movie_surface()
    ###########################
    
    runloop = 1
    clock = pygame.time.Clock()
    while runloop:
        clock.tick(30)
        pygame.event.pump()
        events = pygame.event.get()
        for event in events:
            if event.type is KEYDOWN:
                if event.key == K_ESCAPE:
                    print "escape hit, stopping loop"
                    runloop = 0
            actives.update(event)
        r = scr.blit(msurf, mppos)
        pygame.display.update(r)
        
    
    
