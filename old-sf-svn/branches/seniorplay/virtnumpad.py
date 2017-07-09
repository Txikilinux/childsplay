"""

    (C) Copyright 2008 Rene Dohmen

   Version 1.0.5 - September 15th, 2008
   
   This program is build for QioSQ braintrainer
   
   Usage:
   
   import virtkeyboard
   mykeys = virtkeyboard.VirtualNumpad()
   userinput = mykeyboard.run(screen, default_text)

"""
import pygame, time
from pygame.locals import *

import utils
from SPConstants import *

class QuitException(Exception):
    pass

class NumberInput(object):
    ''' Handles the text input box and manages the cursor '''
    def __init__(self, background, screen, text, x, y):
        self.x = x
        self.y = y
        self.text = text
        self.T9Anwers=[]
        self.fontSize=25
        self.yStep=33
        self.width = 800
        self.height = 60        
        self.yTop = 100
        self.xPosCloud=self.initialXPosCloud=25
        self.yPosCloud=self.initialYPosCloud=22
        #self.font = pygame.font.Font(None, 50)
        self.cursorpos = len(text)
        self.rect = Rect(self.x,self.y+self.yTop,self.width,self.height)
        self.layer = pygame.Surface((self.width,self.height),SRCALPHA).convert_alpha()
        self.background = pygame.Surface((self.width,self.height),SRCALPHA).convert_alpha()
        self.background.blit(background,(0,0),self.rect) # Store our portion of the background
        self.cursorlayer = pygame.Surface((3,50))
        self.screen = screen
        self.cursorvis = False
        self.draw()
    
    def draw(self):
        ''' Draw the text input box '''
        self.layer.fill([0, 0, 0, 0])
        color = [0,0,0,200]
#        pygame.draw.rect(self.layer, (220, 220, 220), (0,0,self.width,self.height), 2)        
        
#        text = self.font.render(self.text, 1, (255,255,255))
        text = utils.char2surf(self.text, 48, (255, 255, 255), TTF)
        self.layer.blit(text,(4,4))               
        
        self.screen.blit(self.background,(self.x, self.y+self.yTop))
        self.screen.blit(self.layer,(self.x,self.y+self.yTop))        
#        self.drawcursor()

    def flashcursor(self):
        ''' Toggle visibility of the cursor '''
#        if self.cursorvis:
#            self.cursorvis = False
#        else:
#            self.cursorvis = True
        
#        self.screen.blit(self.background,(self.x, self.y))
#        self.screen.blit(self.layer,(self.x,self.y))  
        
#        if self.cursorvis:
#            self.drawcursor()
#        pygame.display.flip()
        
    def addcharatcursor(self, letter):
        ''' Add a character whereever the cursor is currently located '''
        if self.cursorpos < len(self.text):
            # Inserting in the middle
            self.text = self.text[:self.cursorpos] + letter + self.text[self.cursorpos:]
            self.cursorpos += 1
            self.draw()
            return
        self.text += letter
        self.cursorpos += 1
        self.draw()   
        
    def backspace(self):
        ''' Delete a character before the cursor position '''
        if self.cursorpos == 0: return
        self.text = self.text[:self.cursorpos-1] + self.text[self.cursorpos:]
        self.cursorpos -= 1
        self.draw()
        return

    def deccursor(self):
        ''' Move the cursor one space left '''
        if self.cursorpos == 0: return
        self.cursorpos -= 1
        self.draw()
        
    def inccursor(self):
        ''' Move the cursor one space right (but not beyond the end of the text) '''
        if self.cursorpos == len(self.text): return
        self.cursorpos += 1
        self.draw()
        
    def drawcursor(self):
        ''' Draw the cursor '''
        x = 4
        y = 5 + self.y
        # Calc width of text to this point
        if self.cursorpos > 0:
            mytext = self.text[:self.cursorpos]
            text = self.font.render(mytext, 1, (0, 0, 0))
            textpos = text.get_rect()
            x = x + textpos.width + 1
        self.screen.blit(self.cursorlayer,(x,y))    
        

class VirtualNumber(object):
    ''' A single key for the VirtualNumpad '''
    def __init__(self, caption, x, y, w=67, h=67):
        self.x = x
        self.y = y+100
        self.caption = caption
        self.width = w
        self.height = h
        self.enter = False
        self.bskey = False
        self.font = None
        self.selected = False
        self.enabled = False
        self.dirty = True
        self.keylayer = pygame.Surface((self.width,self.height)).convert()
        self.keylayer.fill((0, 0, 0))
        self.keylayer.set_alpha(160)
        # Pre draw the border and store in my layer
        pygame.draw.rect(self.keylayer, (255,255,255), (0,0,self.width,self.height), 1)
    
    def draw(self, screen, background, shifted=False, forcedraw=False):
        '''  Draw one key if it needs redrawing '''
        if not forcedraw:
            if not self.dirty: return
        
        myletter = self.caption
        if shifted:
            if myletter == 'SHIFT':
                self.selected = True # Draw me uppercase
            myletter = myletter.upper()
        
        
        position = Rect(self.x, self.y, self.width, self.height)
        
        # put the background back on the screen so we can shade properly
        screen.blit(background, (self.x,self.y), position)      
        
        # Put the shaded key background into my layer
        if self.selected: 
            color = (100,100,100)
        else:
            color = (0,0,0)
        
        # Copy my layer onto the screen using Alpha so you can see through it
        pygame.draw.rect(self.keylayer, color, (1,1,self.width-2,self.height-2))                
        screen.blit(self.keylayer,(self.x,self.y))    
                
        # Create a new temporary layer for the key contents
        # This might be sped up by pre-creating both selected and unselected layers when
        # the key is created, but the speed seems fine unless you're drawing every key at once
        templayer = pygame.Surface((self.width,self.height))
        templayer.set_colorkey((0,0,0))
                       
        color = (255,255,255)
        if self.bskey:
            pygame.draw.line(templayer, color, (52,31), (15,31),2)
            pygame.draw.line(templayer, color, (15,31), (20,26),2)
            pygame.draw.line(templayer, color, (15,32), (20,37),2)
        elif self.enter:
            text = self.font.render("Enter", 1, (255, 255, 255))
            textpos = text.get_rect()
            blockoffx = (self.width / 2)
            blockoffy = (self.height / 2)
            offsetx = blockoffx - (textpos.width / 2)
            offsety = blockoffy - (textpos.height / 2)
            templayer.blit(text,(offsetx, (offsety-30)))

            pygame.draw.line(templayer, color, (100,71), (100,81),2)
            pygame.draw.line(templayer, color, (100,81), (25,81),2)
            pygame.draw.line(templayer, color, (25,81), (30,76),2)
            pygame.draw.line(templayer, color, (25,82), (30,87),2)
            
        else:
            text = self.font.render(myletter, 1, (255, 255, 255))
            textpos = text.get_rect()
            blockoffx = (self.width / 2)
            blockoffy = (self.height / 2)
            offsetx = blockoffx - (textpos.width / 2)
            offsety = blockoffy - (textpos.height / 2)
            templayer.blit(text,(offsetx, offsety))
        
        screen.blit(templayer, (self.x,self.y))
        self.dirty = False

class VirtualNumpad(object):
    ''' Implement a basic full screen virtual keyboard for touchscreens '''

    def run(self, screen, text='', layout=0, quitrect=None):
        self.quitrect = quitrect
        # First, make a backup of the screen        
        self.screen = screen
        self.background = pygame.Surface((800,480))
        self.maxNumbers=2
        
        # Copy original screen to self.background
        self.background.blit(screen,(0,0))
        
        # Shade the background surrounding the keys
        self.keylayer = pygame.Surface((800,480))
        self.keylayer.fill((0, 0, 0))
        self.keylayer.set_alpha(0)
        self.screen.blit(self.keylayer,(0,0))
       
        self.currentLayout=layout #default layout 0: qwerty, layout 1: abcde
        self.keys = []
        self.textbox = pygame.Surface((800,30))
        self.text = text
        self.caps = False
        
        pygame.font.init() # Just in case 
        self.font = pygame.font.Font(None, 40)   
        
        text = utils.char2surf(_("Year of birth"), 48, WHITE, TTF)
        pygame.display.update(self.screen.blit(text,(200,150)))
        text_year = utils.char2surf("19", 48, WHITE, TTF)
        pygame.display.update(self.screen.blit(text_year,(240,148+100)))
        
        self.input = NumberInput(self.background,self.screen,self.text,300,145)
        
        self.addkeys()
          
        self.paintkeys()
        counter = 0
        # My main event loop (hog all processes since we're on top, but someone might want
        # to rewrite this to be more event based.  Personally it works fine for my purposes ;-)
        # OK :-)
        pygame.event.pump()
        pygame.event.clear()
        while 1:
            pygame.time.wait(100)
            pygame.event.pump()
            events = pygame.event.get() 
            if events <> None:
                for e in events:
                    if (e.type == KEYDOWN):
                        if e.key == K_ESCAPE:
                            self.clear()
                            return self.text # Return what we started with
                        if e.key == K_RETURN:
                            self.clear()
                            if self.input.text=='': return "0"
                            else: return self.input.text # Return what the user entered
                        if e.key == K_LEFT:
                            self.input.deccursor()
                            pygame.display.flip()
                        if e.key == K_RIGHT:
                            self.input.inccursor()
                            pygame.display.flip()
                    if (e.type == MOUSEBUTTONDOWN):
                        pos = pygame.Rect(pygame.mouse.get_pos() + (2,2))
                        y=pos[1]

                    if (e.type == MOUSEBUTTONDOWN):
                        if self.clickatmouse():
                            # user clicked enter if returns True
                            self.clear()
                            if self.input.text=='': return "0"
                            else: return self.input.text # Return what the user entered
#                    if (e.type == MOUSEMOTION):
#                        if e.buttons[0] == 1:
#                            # user click-dragged to a different key?
#                            self.selectatmouse()
#                        
            counter += 1
            if counter > 10:                
                self.input.flashcursor()
                counter = 0
            #gtk.main_iteration(block=False)
        
    def unselectall(self, force = False):
        ''' Force all the keys to be unselected
            Marks any that change as dirty to redraw '''
        for key in self.keys:
            if key.selected:
                key.selected = False
                key.dirty = True


    def clickatmouse(self):
        ''' Check to see if the user is pressing down on a key and draw it selected '''
        self.unselectall()
        for key in self.keys:
            myrect = Rect(key.x,key.y,key.width,key.height)
            if myrect.collidepoint(pygame.mouse.get_pos()):
                key.dirty = True
                if key.bskey:
                    # Backspace
                    self.input.backspace()
                    self.paintkeys() 
                    return False
                if key.caption == 'SPACE':                    
                    self.input.addcharatcursor(' ')
                    self.paintkeys() 
                    return False
                if key.caption == 'SHIFT':
                    self.togglecaps()
                    self.paintkeys() 
                    return False
                if key.enter:
                    return True
                    
                mykey = key.caption
                if self.caps:
                    mykey = mykey.upper()

                if len(self.input.text)<self.maxNumbers: self.input.addcharatcursor(mykey)
                self.paintkeys()
                return False
        
        #check quit button
        if self.quitrect.contains(pygame.Rect(pygame.mouse.get_pos()+(1, 1))):
            raise QuitException
#        if pos[0]>693 and pos[1]<80:
#            print "QUIT pressed:"
#            self.input.bladibla[1]="QUIT" #ITS SO UGLY (make an parse error to quit keyboard and game)
#            return True

        self.paintkeys() 
        return False
        
    def togglecaps(self):
        ''' Toggle uppercase / lowercase '''
        if self.caps: 
            self.caps = False
        else:
            self.caps = True
        for key in self.keys:
            key.dirty = True        
        
    def selectatmouse(self):
        ''' User has clicked a key, let's use it '''
        self.unselectall()
        for key in self.keys:
            myrect = Rect(key.x,key.y,key.width,key.height)
            if myrect.collidepoint(pygame.mouse.get_pos()):
                key.selected = True
                key.enabled = False
                key.dirty = True
                self.paintkeys()
                return
            
        self.paintkeys()        
            
    def addkeys(self):
        ''' Adds the setup for the keys.  This would be easy to modify for additional keys
        
         The default start position places the keyboard slightly left of center by design.'''
        
        x=250 
        y = 205
        
        if self.currentLayout==0: row = ['1','2','3']
        else: row = ['7','8','9']
        for item in row:
            onekey = VirtualNumber(item,x,y)
            onekey.font = self.font
            self.keys.append(onekey)
            x += 70
            
        onekey = VirtualNumber('<-',x,y)
        onekey.font = self.font
        onekey.bskey = True
        self.keys.append(onekey)
        
        y += 70
        x=250
       

        if self.currentLayout==0: row = ['4','5','6']
        else: row = ['4','5','6']
        for item in row:
            onekey = VirtualNumber(item,x,y)
            onekey.font = self.font
            self.keys.append(onekey)
            x += 70

        onekey = VirtualNumber('ENTER',x,y,138, 137)
        onekey.font = self.font
        onekey.enter = True
        self.keys.append(onekey)

        y += 70
        x=250

        if self.currentLayout==0: row = ['7','8','9']
        else: row = ['1','2','3']
        for item in row:
            onekey = VirtualNumber(item,x,y)
            onekey.font = self.font
            self.keys.append(onekey)
            x += 70

        x=250
        y += 70        
   
        x += 35
        onekey = VirtualNumber('0',x,y,138)
        onekey.font = self.font
        self.keys.append(onekey)

    def paintkeys(self):
        ''' Draw the keyboard (but only if they're dirty.) '''
        for key in self.keys:
            key.draw(self.screen, self.background, self.caps)
        
        pygame.display.flip()
    
    def clear(self):    
        ''' Put the screen back to before we started '''
        #self.screen.blit(self.background,(0,0))
        pygame.display.flip()
        
if __name__ == '__main__': 
    pygame.init()
    screen = pygame.display.set_mode((800, 600),0)

    mykeys = VirtualNumpad()
    userinput = mykeys.run(screen, "", layout=1)
    print userinput
