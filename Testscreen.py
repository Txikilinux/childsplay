

import pygame
from pygame.constants import *
pygame.init()

scr = pygame.display.set_mode((800, 600))
scr.fill((250, 250, 250))
pygame.display.flip()

print "start eventloop, hit Esc to stop"
runloop = 1 
while runloop:
    pygame.time.wait(100)
    pygame.event.pump()
    events = pygame.event.get()
    for event in events:
        if event.type is KEYDOWN:
            if event.key == K_ESCAPE:
                runloop = 0

print "eventloop stopped"
raw_input("hit any key to quit")
pygame.quit()
