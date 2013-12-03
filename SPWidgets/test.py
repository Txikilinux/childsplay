
import sys
sys.path.insert(0, '..')

from base import *
from buttons import *
from dialogs import *
from funcs import *
from text import *
from gtk_widgets import *

import pygame
from pygame.constants import *
import logging 

from SPSpriteUtils import SPSprite, SPGroup
import utils
from SPConstants import *
import SPLogging
 
if __name__ == '__main__':
    
    import __builtin__
    __builtin__.__dict__['_'] = lambda x:x
    
    SPLogging.set_level('debug')
    SPLogging.start()
        
    pygame.init()
    
    from SPSpriteUtils import SPInit
    
    def cbf(sprite, event, data=''):
        print 'cb called with sprite %s, event %s and data %s' % (sprite, event, data)
        print 'sprite name: %s' % sprite.get_name()
        print 'data is %s' % data
    
    def cbf_but(sprite, event, data=''):
        back = pygame.Surface((300,300))
        back.fill(GREEN)
        but = Button('Dialog Button', (10, 10), padding=6)
        but.connect_callback(cbf, MOUSEBUTTONUP, 'Dialog Button')
        objects =[but]
        
        dlg = DialogWindow(back,objects)
        dlg.run()
    
    scr = pygame.display.set_mode((800, 600))
    scr.fill(GREY90)
    pygame.display.flip()
    back = scr.convert()
    actives = SPInit(scr, back)
    
    Init('braintrainer')
    
#    but = Button('Button', (10, 80), padding=6)
#    but.connect_callback(cbf_but, MOUSEBUTTONUP, 'Button')
#    actives.add(but)
#    lbl = Label('Hit escape key to continue', (10, 130))
#    r = pygame.Rect(0, 0, 500, 240)
#    txt = "This program is free software; you can redistribute it and/or modify it under the terms of version 3 of the GNU General Public License as published by the Free Software Foundation.  A copy of this license should be included in the file GPL-3."
#    
#    tv = TextView(txt, (290, 180), r, autofit=True, border=True)
#    tv.display_sprite()
#    
#    va = VolumeAdjust((200, 20))
#    va.display()
#    
#    pnb = PrevNextButton((150, 180), cbf)
#        
#    actives.add([but, lbl, va.get_actives(), pnb.get_actives()])
#    for s in actives:
#        s.display_sprite()
    
    
#    ec = ExeCounter((600, 10), 20)
#    ec.display_sprite()
    
#    box = TextEntryBox((10, 100), height=10, length=500)
#    box.display_sprite()
#    actives.add(box.get_actives())
#
#    TI = TextEntry((10, 10), message="BT2.1")
#    TI.display_sprite()
#    actives.add(TI)

#    objects = []
#    for i in range(30):
#        t = "Label %s" % i
#        lbl = Label(t, (0, 0))
#        lbl.connect_callback(cbf, MOUSEBUTTONUP, t)
#        actives.add(lbl)
#        objects.append(lbl)
#    
#    sw = ScrollWindow((100, 100), (400, 400), objects, border=2)
#    actives.add(sw)
#    actives.add(sw.get_actives())

#    rb = RadioButton(None, "test radiobutton", (100, 100), name='rb')
#    rb.display_sprite()
#    actives.add(rb)
#    
#    rb0 = RadioButton(rb, "test radiobutton", (100, 130), name='rb0')
#    rb0.display_sprite()
#    actives.add(rb0)
    runloop = 1 
    
    pb = ProgressBar((100,200), (300,30), steps=10)
    pb.display_sprite()
    count = 0
    while runloop:
        if count > 5:
            count = 0
            steps = pb.update()
            print steps
            if steps == False:
                runloop = False
        else:
            count += 1
        pygame.time.wait(100)
        pygame.event.pump()
        events = pygame.event.get()
        for event in events:
            if event.type is KEYDOWN:
                if event.key == K_ESCAPE:
                    runloop = 0
#                elif event.key == K_F1:
#                    but.enable(False)
#                    print "button disabled"
#                elif event.key == K_F2:
#                    but.enable(True)
#                    print "button enabled"
#                elif event.key == K_F3:
#                    pnb.toggle()
#                    print "prevnext toggled"
            result = actives.update(event)
            if result and result[0][1] == -1:
                break
                
#    print TI.get_text()
#    print box.get_text()
    raw_input("hit any key to stop")
    