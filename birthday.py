
# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zykiewicz <stas.zytkiewicz@schoolsplay.org>
#
#           birthday.py
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

import utils
from SPConstants import *
import SPSpriteUtils
import SPWidgets
import glob

class Animation(SPSpriteUtils.SPSprite):
    def __init__(self, animationlist, pos=(300, 200)):
        self.part_index = 0
        self.index = 0
        self.max_index = len(animationlist) - 1
        self.animationlist = animationlist
        self.wait = 5
        self.counter = 0
        SPSpriteUtils.SPSprite.__init__(self, self.animationlist[0])
        self.moveto(pos)
    
    def on_update(self,*args):
        """This is called by group.refresh method"""
        if self.counter < self.wait: 
            self.counter += 1
            return
        else:
            self.counter = 0
            self.erase_sprite()
            if self.index < self.max_index:
                self.index += 1
            else:
                self.index = 0
            self.image = self.animationlist[self.index]
        self.display_sprite()

class birthday:
    def __init__(self, screen, back, name, age):
        self.screen = screen
        self.back = back
        self.actives = SPSpriteUtils.SPInit(self.screen, self.back)
        but = SPWidgets.SimpleButtonDynamic(_("Close"), (350, 500), fsize=24, data='close')
        but.set_use_current_background(True)
        but.display_sprite()
        self.actives.add(but)
        lbl = SPWidgets.Label(_("Congratulations %s, you are %s year old today.") % (name, age), \
                              (100, 120), fgcol=ORANGERED, transparent=True).display_sprite()
        self.datadir = os.path.join(ACTIVITYDATADIR, 'SPData', 'themes', 'braintrainer', 'birthday')
        # we only use cake for now
        self.animations_path = os.path.join(self.datadir, 'party', '*')
        self.animationlist = []
        for file in glob.glob(self.animations_path):
            self.animationlist.append(utils.load_image(file))
        self.animation = Animation(self.animationlist)
                    
    def run(self):
        runloop = 100
        
        while runloop:
            runloop -= 1
            pygame.time.wait(100)
            pygame.event.pump()
            events = pygame.event.get()
            for event in events:
                if event.type is KEYDOWN:
                    if event.key == K_ESCAPE:
                        runloop = 0
                if self.actives.update(event):
                    runloop = 0
            self.animation.on_update()
            
        

if __name__ == '__main__':
    
    import __builtin__
    __builtin__.__dict__['_'] = lambda x:x
    
    import SPLogging
    SPLogging.set_level('debug')
    SPLogging.start()
    
    pygame.init()
    
    from SPSpriteUtils import SPInit
    
    def cbf(sprite, event, data=''):
        print 'cb called with sprite %s, event %s and data %s' % (sprite, event, data)
        print 'sprite name: %s' % sprite.get_name()
        print 'data is %s' % data
    
    scr = pygame.display.set_mode((800, 600))
    scr.fill(GREY90)
    pygame.display.flip()
    back = scr.convert()
    actives = SPInit(scr, back)
    
    SPWidgets.Init('braintrainer')
    
    b = birthday(scr, back)
    b.run()
    

