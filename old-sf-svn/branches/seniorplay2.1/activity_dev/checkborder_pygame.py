import os,sys
import pygame
from pygame.constants import *
pygame.init()

# tool to look for the first non-alpha pixel on the x-axe in a pygame surface.
# It stores the pixel coords in a list and displays this list.
# Used to get coords to draw a border next to the image.

if len(sys.argv) < 3:
    print "Usage: checkborder_pygame.py imgpath <coords output path>"
    sys.exit(1)
    
imgpath = sys.argv[1]
fpath = sys.argv[2]

img = pygame.image.load(imgpath)
coords = []
w = img.get_width()
h = img.get_height()
for x in range(w):
    y = h-1
    while y > 0:
        if img.get_at((x, y))[3] > 127:
           coords.append(str((x, y)))
           break
        y -= 1

scr = pygame.display.set_mode((w+20, h*2+40))

scr.blit(img, (0, h + 20))

for c in coords:
    scr.set_at(eval(c), (100, 100, 100))

s = ";".join(coords)

print "coords written to ", fpath
f = open(fpath, 'w')    
f.write(s)
f.close()

pygame.display.flip()
raw_input("any key")
