"""

    (C) Copyright 2008 Rene Dohmen

   Version 1.0.5 - September 15th, 2008
   
   This program is build for QioSQ braintrainer
   
   Usage:
   
   import virtkeyboard
   mykeys = virtkeyboard.VirtualKeyboard()
   userinput = mykeyboard.run(screen, default_text)

"""
import pygame, time
from pygame.locals import *

class TextInput(object):
    ''' Handles the text input box and manages the cursor '''
    def __init__(self, background, screen, text, answers, x, y):
        self.x = x
        self.y = y
        self.text = text
        self.answers = answers
        self.T9Anwers=[]
        self.fontSize=18
        self.yStep=26
        self.width = 490
        self.height = 40 # input height
        self.cloudHeight=136
        self.yTop=100
        self.xPosCloud=self.initialXPosCloud=25
        self.yPosCloud=self.initialYPosCloud=62+self.yTop
        self.font = pygame.font.Font(None, 40)
        self.cloudFontSize=24
        self.cloudFont = pygame.font.Font(None, self.cloudFontSize)
        self.cursorpos = len(text)
        self.rect = Rect(self.x,self.y+self.yTop,self.width,self.height)
        self.inputLayer = pygame.Surface((self.width,self.height),SRCALPHA).convert_alpha()
        self.cloudLayer = pygame.Surface((self.width,self.cloudHeight),SRCALPHA).convert_alpha()
        self.background = pygame.Surface((self.width,self.height),SRCALPHA).convert_alpha()
        self.cloudBackground = pygame.Surface((self.width,self.cloudHeight),SRCALPHA).convert_alpha()
        self.background.blit(background,(0,0),self.rect) # Store our portion of the background
        self.cloudBackground.blit(background,(0,0),Rect(self.x,self.y+self.yTop-136,self.width,self.cloudHeight))
        #self.cloud_background.blit(background,(0,140),self.rect) # Store our portion of the background
        self.cursorlayer = pygame.Surface((3,50))
        self.screen = screen
        self.cursorvis = False
        self.nrOfCharsBeforeT9=4
        
        self.draw()
    
    def draw(self):
        ''' Draw the text input box '''
        self.inputLayer.fill([0, 0, 0, 0])
        #self.cloudLayer.fill([0,0,0,100])
        #self.inputLayer.fill([0, 0, 0, 100]) #debug the input layer
        color = [0,0,0,200]
#        pygame.draw.rect(self.inputLayer, color, (0,0,self.width,self.height), 1)        
        
        text = self.font.render(self.text, 1, (21,37,63))
        self.inputLayer.blit(text,(4,4))               
        
        self.screen.blit(self.background,(self.x, self.y+self.yTop))
        self.screen.blit(self.inputLayer,(self.x,self.y+self.yTop))        
        self.updateCloudbox()
#        self.drawcursor()
   
    def updateCloudbox(self):
        self.xPosCloud=self.initialXPosCloud
        self.yPosCloud=self.initialYPosCloud+10
        self.screen.blit(self.cloudBackground,(self.x,self.y+self.yTop-136))
#        cloudArea.fill((219,255,230)) # fill with soft green
#        self.screen.blit(cloudArea, (23,20))
        if len(self.text)>self.nrOfCharsBeforeT9-1: 
            print "starting autocompletion"
            self.T9Anwers=[]
            for answer in self.answers: 
                if answer[:len(self.text)]==self.text: 
                    print "adding answer %s" % answer
                    if self.xPosCloud+(len(answer)*self.cloudFontSize/2)>510:
                        self.yPosCloud+=self.yStep
                        self.xPosCloud=self.initialXPosCloud
                    if self.yPosCloud<280:
                        self.T9Anwers.append(answer)
                        self._drawCloud(answer)
             
    def _drawCloud(self, answer):
        #private function to daw a cloud: used by updateCloudbox...
        cloudText = self.cloudFont.render(answer, 1, (84, 185, 72))
        #check xValue and reset if reached end of line
        self.screen.blit(cloudText,(self.xPosCloud,self.yPosCloud))               
        self.xPosCloud=(len(answer)*self.cloudFontSize/2)+self.xPosCloud
        print "x=%d and y=%d" %(self.xPosCloud, self.yPosCloud)

        
    def flashcursor(self):
        ''' Toggle visibility of the cursor '''
#        if self.cursorvis:
#            self.cursorvis = False
#        else:
#            self.cursorvis = True
        
#        self.screen.blit(self.background,(self.x, self.y))
#        self.screen.blit(self.inputLayer,(self.x,self.y))  
        
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
        

class VirtualKey(object):
    ''' A single key for the VirtualKeyboard '''
    def __init__(self, caption, x, y, w=50, h=50):
        self.x = x
        self.y = y
        self.caption = caption
        self.width = w
        self.height = h
        self.enter = False
        self.bskey = False
        self.font = None
        self.selected = False
        self.enabled = False
        self.dirty = True
        self.keyColor= (29,80,185)
        self.keylayer = pygame.Surface((self.width,self.height)).convert()
        self.keylayer.fill(self.keyColor)
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
            color = (self.keyColor)
        
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
            pygame.draw.line(templayer, color, (92,31), (15,31),2)
            pygame.draw.line(templayer, color, (15,31), (20,26),2)
            pygame.draw.line(templayer, color, (15,32), (20,37),2)
        elif self.enter:
            text = self.font.render("Enter", 1, (255, 255, 255))
            textpos = text.get_rect()
            blockoffx = (self.width / 2)
            blockoffy = (self.height / 2)
            offsetx = blockoffx - (textpos.width / 2)
            offsety = blockoffy - (textpos.height / 2) + 8 
            templayer.blit(text,(offsetx, (offsety-30)))

            pygame.draw.line(templayer, color, (80,71), (80,81),2)
            pygame.draw.line(templayer, color, (80,81), (25,81),2)
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

class VirtualKeyboard(object):
    ''' Implement a basic full screen virtual keyboard for touchscreens '''

    def run(self, screen, answers, text='', layout=0):
        # First, make a backup of the screen        
        self.yTop=100
        self.screen = screen
        self.background = pygame.Surface((800,600))
        self.answers=answers
        self.maxChars=32
        # Copy original screen to self.background
        self.background.blit(screen,(0,0))
        
        # Shade the background surrounding the keys
        self.keylayer = pygame.Surface((800,600))
        self.keylayer.fill((0, 0, 0))
        self.keylayer.set_alpha(0)
        self.screen.blit(self.keylayer,(0,0))
       
        self.currentLayout=layout #default layout 0: qwerty, layout 1: abcde
        self.keys = []
        self.textbox = pygame.Surface((800,30))
        self.tagCloudBackground=pygame.Surface((525,200))
        self.tagCloudBackground.blit(screen,(30,10))
        self.text = text
        self.caps = False
        
        pygame.font.init() # Just in case 
        self.font = pygame.font.Font(None, 40)   
        self.smallfont= pygame.font.Font(None, 20) 
        self.input = TextInput(self.background,self.screen,self.text,self.answers,24,200)
        
        self.addkeys()
          
        self.paintkeys()
        counter = 0
        # My main event loop (hog all processes since we're on top, but someone might want
        # to rewrite this to be more event based.  Personally it works fine for my purposes ;-)
        while 1:
            time.sleep(.05)
            events = pygame.event.get() 
            if events <> None:
                for e in events:
                    if (e.type == KEYDOWN):
                        if e.key == K_ESCAPE:
                            self.clear()
                            return self.text # Return what we started with
                        if e.key == K_RETURN:
                            self.clear()
                            return self.input.text # Return what the user entered
                        if e.key == K_LEFT:
                            self.input.deccursor()
                            pygame.display.flip()
                        if e.key == K_RIGHT:
                            self.input.inccursor()
                            pygame.display.flip()
                    if (e.type == MOUSEBUTTONDOWN):
                        pos = pygame.Rect(pygame.mouse.get_pos() + (2,2))
                        y=pos[1]
                        if y>305:
                            # check if user clicked in the keyboard of cloudbox aea
                            self.selectatmouse()   
                        else: 
                            print "Current T9 options";
                            print self.input.T9Anwers
                            answer=self.checkCloud(pos)
                            if answer!=0 : 
                                print answer
                                return answer
                    if (e.type == MOUSEBUTTONUP):
                        if self.clickatmouse():
                            # user clicked enter if returns True
                            self.clear()
                            return self.input.text # Return what the user entered
                    if (e.type == MOUSEMOTION):
                        if e.buttons[0] == 1:
                            # user click-dragged to a different key?
                            self.selectatmouse()
                        
            counter += 1
            if counter > 10:                
                self.input.flashcursor()
                counter = 0
            gtk.main_iteration(block=False)
        
    def unselectall(self, force = False):
        ''' Force all the keys to be unselected
            Marks any that change as dirty to redraw '''
        for key in self.keys:
            if key.selected:
                key.selected = False
                key.dirty = True

    def checkCloud(self,pos):
        if len(self.input.T9Anwers)>0:
            x=pos[0]
            y=pos[1]
            print x,y
            myLoopX=25
            myLoopY=62+self.yTop+5
            for answer in self.input.T9Anwers: 
                if myLoopX+(len(answer)*24/2)>510:
                    myLoopY=myLoopY+26
                    myLoopX=25
                if x>myLoopX and x<(len(answer)*24/2) + myLoopX and y>myLoopY and y<myLoopY+26: return answer
                myLoopX=(len(answer)*24/2)+myLoopX

            return 0 
        else: return 0

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
                if key.caption == 'SPATIE':                    
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
                
                if len(self.input.text)<self.maxChars: self.input.addcharatcursor(mykey)
                self.paintkeys()
                return False
        #check quit button
        pos=pygame.mouse.get_pos()
        if pos[0]>693 and pos[1]<80:
            print "QUIT pressed:"
            self.input.bladibla[1]="QUIT" #ITS SO UGLY (make an parse error to quit keyboard and game)
            return True
        if pos[0]>574 and pos[1]>503:
            print "Nieuw woord pressed:"
            self.input.text="READY FOR NOW" #ITS SO UGLY (make an parse error to quit keyboard and game)
            return True
           
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
        
        x = 20 
        y = 263+self.yTop
        
        if self.currentLayout==0: row = ['q','w','e','r','t','y','u']
        else: row = ['a','b','c','d','e','f','g']
        for item in row:
            onekey = VirtualKey(item,x,y)
            onekey.font = self.font
            self.keys.append(onekey)
            x += 55
            
        #backspace
        onekey = VirtualKey('<-',x,y,105)
        onekey.font = self.font
        onekey.bskey = True
        self.keys.append(onekey)
        
        y += 55
        x = 20
       

        if self.currentLayout==0: row = ['i','o','p','a','s','d']
        else: row = ['h','i','j','k','l','m','n']
        for item in row:
            onekey = VirtualKey(item,x,y)
            onekey.font = self.font
            self.keys.append(onekey)
            x += 55

        onekey = VirtualKey('ENTER',x,y,105, 105)
        onekey.font = self.font
        onekey.enter = True
        self.keys.append(onekey)

        y += 55
        x = 20

       
        if self.currentLayout==0: row = ['f','g','h','j','k','l']
        else: row = ['o','p','q','r','s','t','u']
        for item in row:
            onekey = VirtualKey(item,x,y)
            onekey.font = self.font
            self.keys.append(onekey)
            x += 55

        x = 20
        y += 55        


        if self.currentLayout==0: row = ['z','x','c','v','b','n','m']
        else: row = ['v','w','x','y','z']
        for item in row:
            onekey = VirtualKey(item,x,y)
            onekey.font = self.font
            self.keys.append(onekey)
            x += 55

        #onekey = VirtualKey('SHIFT',x,y,138)
        #onekey.font = self.font
        #self.keys.append(onekey)
        #x += 143
  
        onekey = VirtualKey('SPATIE',x,y,215)
        #onekey = VirtualKey('SPATIE',x,y,105) #2 key specs for use with SHIFT
        onekey.font = self.font
        self.keys.append(onekey)
        #x += 250
        

        
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

    mykeys = VirtualKeyboard()
    answers= ['aa','aab','aac','aaa','aaaaaaaaa','aaaabaaa','aapje','aanraakbaar','aanaal','aaarsen','aaaas','aambeeld','aanstaande','aalbes','aardbei','abrikoos','acerola','aki','ananas','appel','appelbanaan','aprium','atemoya','avocado','awarra','banaan','bergamot','bergpapaja','bergzuurzak','blimbing','bloedsinaasappel','bosbes','braam','broodvrucht','cainito','canistel','cashew-Appel','cassabanana','cherimoya','china-Peer','chinese kumquat','Citroen','citrusvrucht','clementine','coronilla','dadel','doerian','druif','feijoa','framboos','gandaria','gatenplantvrucht','genipapo','granaatappel','grapefruit','grosella','ikakopruim','jaboticaba','jackfruit','jakhalsbes','jujube','kaki','kapoelasan','kepel','kers','kiwano','kiwi','knippa','korlan','kruisbes','kumquat','kweepeer','kwini','langsat','lijsterbes','longan','loquat','lotusvrucht','lulo','mabolo','mamey sapota','mandarijn','mangistan','mango','marang','meloen','mini-kiwi','mispel','moendoe','morel','morichepalm','nance','nashi-peer','natal-pruim','nectarine','noni','olifantsappel','papaja','papeda','passievrucht','pawpaw','peer','pepino','pereskie','perzik','perzikpalm','pitaya','plumcot','pluot','pomelo','pompelmoes','prachtframboos','pruim','ramboetan','rijsbes','rozenbottel','salak','santol','sapodilla','satsuma','schroefpalm','sharonfruit','sinaasappel','slijmappel','soncoya','stranddruif','surinaamse kers','sweetie','tamarillo','tjampedak','ugli','vijg','vlierbes','wampi','watermeloen','zoete passievrucht','zoetzak','zuurzak']
    userinput = mykeys.run(screen, answers, "", layout=1)
