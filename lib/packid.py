
# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zytkiewicz stas.zytkiewicz@schoolsplay.org
#
#           packid.py
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

#create logger, logger was setup in SPLogging
import logging
# In your Activity class -> 
# self.logger =  logging.getLogger("childsplay.packid.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("childsplay.packid")

# standard modules you probably need
import os,sys, random

import pygame
from pygame.constants import *

import utils
from SPConstants import *
import SPSpriteUtils

# containers that can be used globally to store stuff
class Img:
    pass
class Snd:
    pass

class PacKid:
    def __init__(self,matrix,startx,starty,speed=24):
        self.speed = speed
        self.pac_r = Img.pac_r
        self.pac_r_c = Img.pac_r_c
        self.pac_l = Img.pac_l
        self.pac_l_c = Img.pac_l_c
        self.pac_u = Img.pac_u
        self.pac_u_c = Img.pac_u_c
        self.pac_d = Img.pac_d
        self.pac_d_c = Img.pac_d_c
        self.pac_smile = Img.pac_smile
        self.img = self.pac_smile
        
        self.rect = self.img.get_rect()
        self.rect.move_ip(startx,starty)
        
        self.startrect = self.img.get_rect()
        self.startrect.move_ip(startx,starty)
        self.matrix = matrix
        self.row = 1
        self.col = 1
        self.dir_dic = {'UP':self._up,'DOWN':self._down,'LEFT':self._left,'RIGHT':self._right}
                
    def update(self,direc):
        Snd.waka.play()
        apply(self.dir_dic[direc])
        return (self.row,self.col)
        #print self.row,self.col,self.rect
       
    def _up(self):
        if self.img == self.pac_u_c:
            self.img = self.pac_u
        else:
            self.img = self.pac_u_c
        if self.matrix[self.row-1][self.col]: # can we go here?
            self.row -= 1
            self.rect.move_ip(0,-self.speed)
        
    def _down(self):
        if self.img == self.pac_d_c:
            self.img = self.pac_d
        else:
            self.img = self.pac_d_c
        if self.matrix[self.row+1][self.col]: # can we go here?
            self.row += 1
            self.rect.move_ip(0,self.speed)
        
    def _left(self):
        if self.img == self.pac_l_c:
            self.img = self.pac_l
        else:
            self.img = self.pac_l_c
        if self.matrix[self.row][self.col-1]: # can we go here?
            self.col -= 1
            self.rect.move_ip(-self.speed,0)
    
    def _right(self):
        if self.img == self.pac_r_c:
            self.img = self.pac_r
        else:
            self.img = self.pac_r_c
        if self.matrix[self.row][self.col+1]: # can we go here?
            self.col += 1
            self.rect.move_ip(self.speed,0)
    
class Memory:
    def __init__(self,points=('1','2','3','4','5')):
        self.memory = {}
        self.stack = [None]* len(points)
        
    def remember(self,(key,item)):
        #print key,item
        self.memory[key] = item
        self.stack.insert(0,key)
        try:
            del self.memory[self.stack.pop()]
        except KeyError:
            pass
            
    def recall(self,key):
        if self.memory.has_key(key):
            return self.memory[key] 

class Letters(Memory):
    instance = 0
    def __init__(self,char,fcol,dest,ttf, y):
        Letters.instance += 2
        self.wait = Letters.instance
        Memory.__init__(self)
#        print "char",char
        self.char = char
        self.image = utils.char2surf(char,16,fcol,ttf, bold=True)
        self.rect = self.image.get_rect()
        self.lifetime = 50 # if we get in a loop
        # calculate the pix pos row*24+60, col*24+150
        self.row = 8
        self.col = 12
        self.rect.move_ip(self.col*24+150,self.row*24+60+y)
        self.dest = dest
        
        self.old_move = None
        #self.org = (self.row,self.col)
        #self.vector = self.dest[0]-self.org[0],self.dest[1]-self.org[1]
        self.matrix = Img.matrix
        self.speed = 24

    def update(self):
        if self.wait:
            self.wait -= 1
            return 0
        self.lifetime -= 1
        if self.lifetime < 0:
            #print 'died'
            return 1 # he died :-(
        self.org = (self.row,self.col)
        stop = self._iq((self.dest[0]-self.org[0],self.dest[1]-self.org[1]))
        return stop
            
    def _iq(self,vector):
        direcs = self._where_to_go()
        if (self.row,self.col) == (8,12):# still in the box
            direcs = ['u']
        if len(direcs) == 1:
            self._move(direcs[0])
            stop = self.dest == (self.row,self.col)
            return stop
        else:
            try:
                direcs.remove(self.old_move)
            except ValueError:
                pass
        if len(direcs) == 1:
            self._move(direcs[0])
            stop = self.dest == (self.row,self.col)
            return stop
        else:
            prior = [None]*4
            #print vector
            if abs(vector[0]) > abs(vector[1]): # y is pref.
                if vector[0] < 0:
                    prior[0] = 'u'
                    prior[3] = 'd'
                else:
                    prior[0] = 'd'
                    prior[3] = 'u'
                
                if vector[1] < 0:
                    prior[1] = 'l'
                    prior[2] = 'r'
                else:
                    prior[1] = 'r'
                    prior[2] = 'l'
                
            else:
                if vector[1] < 0:
                    prior[0] = 'l'
                    prior[3] = 'r'
                else:
                    prior[0] = 'r'
                    prior[3] = 'l'
                if vector[0] < 0:
                    prior[1] = 'u'
                    prior[2] = 'd'
                else:
                    prior[1] = 'd'
                    prior[2] = 'u'
        
        #print 'direcs',direcs,'prior',prior,'row/col',self.row,self.col
        for d in prior:
            if d in direcs:
                if self.recall((self.row,self.col)) == d:
                    #print self.recall((self.row,self.col))
                    d = random.choice(direcs)
                    self._move(d)
                    break
                else:
                    #print d
                    self.remember(((self.row,self.col),d))
                    self._move(d)
                    break
        stop = self.dest == (self.row,self.col)
        #print 'stop-iq',stop
        return stop
        
    def _where_to_go(self):
        direcs = []
        if self.matrix[self.row-1][self.col]: # up
            direcs.append(('u'))
        if self.matrix[self.row+1][self.col]: # down
            direcs.append(('d'))
        if self.matrix[self.row][self.col-1]: # left
            direcs.append(('l'))
        if self.matrix[self.row][self.col+1]: # right
            direcs.append(('r'))
        return direcs
        
    def _move(self,choice):
        
        if choice == 'u':
            self.row -= 1
            self.rect.move_ip(0,-self.speed)
            self.old_move = 'd'
        elif choice == 'd':
            self.row += 1
            self.rect.move_ip(0,self.speed)
            self.old_move = 'u'
        elif choice == 'l':
            self.col -= 1
            self.rect.move_ip(-self.speed,0)
            self.old_move = 'r'
        elif choice == 'r':
            self.col += 1
            self.rect.move_ip(self.speed,0)
            self.old_move = 'l'
        return        

class Word:
    """  Highlight the letter in the word"""
    def __init__(self,word,ttf,cpg):
        self.chars = word
        self.ttf = ttf
        self.index = -1
        self.fontsize = 12
        self.cpg = cpg

        self.fcol = (255,255,51)
        self.hfcol = (255,0,0)

    def update(self):
        if self.index < len(self.chars):
             self.index += 1
        else:
            return self.surf
        return self._render(),self.chars[self.index]

    def _render(self):
        #print self.index
        high_letter,lettersize = utils.text2surf(self.chars[self.index],self.fontsize,self.hfcol,self.ttf,1, bold=True)

        if self.index == 0: # Highlight first letter
            split = self.chars[1:]
            word,wordsize = utils.text2surf(split,self.fontsize,self.fcol,self.ttf,1, bold=True)
            surfsize = (lettersize[0]+wordsize[0],lettersize[1])
            surf = pygame.Surface(surfsize).convert()
            if self.cpg.get_localesetting()[1]: # RTL
                surf.blit(word,(0,0))
                surf.blit(high_letter,(wordsize[0],0))
            else:
                surf.blit(high_letter,(0,0))
                surf.blit(word,(lettersize[0],0))

        elif self.index == len(self.chars)-1: # Highlight last letter
            split = self.chars[:-1]
            word,wordsize = utils.text2surf(split,self.fontsize,self.fcol,self.ttf,1, bold=True)
            surfsize = (lettersize[0]+wordsize[0],lettersize[1])
            surf = pygame.Surface(surfsize).convert()
            if self.cpg.get_localesetting()[1]: # RTL
                surf.blit(high_letter,(0,0))
                surf.blit(word,(lettersize[0],0))
            else:
                surf.blit(word,(0,0))
                surf.blit(high_letter,(wordsize[0],0))

        else: # Letter inside the word, the word must be split in two parts
            word,wordsize = utils.text2surf(self.chars[:self.index],self.fontsize,\
                            self.fcol,self.ttf,1, bold=True)
            word1,word1size = utils.text2surf(self.chars[self.index+1:],self.fontsize,\
                              self.fcol,self.ttf,1, bold=True)
            surfsize = (lettersize[0]+wordsize[0]+word1size[0],lettersize[1])
            surf = pygame.Surface(surfsize).convert()
            if self.cpg.get_localesetting()[1]: # RTL
                surf.blit(word1,(0,0))
                surf.blit(high_letter,(word1size[0],0))
                surf.blit(word,(word1size[0]+lettersize[0],0))
            else:
                surf.blit(word,(0,0))
                surf.blit(high_letter,(wordsize[0],0))
                surf.blit(word1,(lettersize[0]+wordsize[0],0))
        self.surf = surf # see self.update
        return self.surf

class SidePanel:
    def __init__(self,levels,ttf,blitpos):
        self.ttf = ttf
        self.surf = pygame.Surface((130,400)).convert()
        pygame.draw.rect(self.surf,(42,191,44),self.surf.get_rect(),6)
        self.when = 9# number of gooditems to play last level
        self.level_pos_list = [(10,10),(10,110),(10,210),(10,310)]
        self.inlevel_word_pos_list = [(26,10),(26,110),(26,210),(26,310)]
        
        self.x = 30
        self.y = 6
        self.fsize = 12
        
        self.fcol = (255,255,51)
        i = 1
        for l in levels[:-1]: # The last level is different
            self._set_level("Level "+str(l+1)+":",i)
            i += 1
        self.lastlevel_y = self.level_pos_list[i-1]
        self.fcol = (186,184,154)
        self._set_last_level(self.level_pos_list[3])
        self.fcol = (255,255,51)
        #set x and y to the first position
        self.y = self.level_pos_list[0][1]
        self.x = self.level_pos_list[0][0]+16
        
        self.goodimg = pygame.transform.scale(Img.pac_smile,(12,12))
        self.wrongimg = pygame.transform.scale(Img.pac_sad,(12,12))
        self.gooditems = 0
        self.count,self.level = 0,0

        self.switch_task()
               
    def _set_last_level(self,pos):
        self._set_level("Level "+str(4)+":", 4)
    
    def _set_level(self,levelstr,level):
        pos = self.level_pos_list[level-1]
        levelimg = utils.char2surf(levelstr,self.fsize+2,self.fcol,self.ttf, \
                             antialias=True, bold=True)
        self.surf.blit(levelimg,pos)
                             
    def set_word(self,word):
        wordimg, size = utils.text2surf(word,self.fsize-2,self.fcol,self.ttf,sizel=True,\
                                   antialias=True, bold=True)
        self.y += size[1]
        self.surf.blit(wordimg,(self.x,self.y))
            
    def switch_task(self):
        SwitchLevel = False
        if self.count == 3:
            self.level += 1
            self.y = self.inlevel_word_pos_list[self.level][1]
            self.count = 0
            SwitchLevel = True
        self.count += 1
        return SwitchLevel
    
    def set_good_wrong(self,gw):
        if gw > 2:
            self.surf.blit(self.wrongimg,(self.x-16,self.y+4))
        else:
            self.surf.blit(self.goodimg,(self.x-16,self.y+4))
            self.gooditems += 1
    
    def get_surf(self):
        return self.surf.convert()
        
    def get_level_score(self):
        #print 'gooditems',self.gooditems
        if self.gooditems >= self.when:
            self.when = 0
            return 1
        else:
            return 0

class LastLevelImg:
    def __init__(self,music,img,pos):
        self.char = 'FRUIT' # to be compatible with the letters class in the loop
        self.file = os.path.join(Img.datadir,music)
        self.img = utils.load_image(os.path.join(Img.datadir,img),1)
        self.pos = pos
        self.rect = self.img.get_rect()
        # calculate the pix pos row*24+60, col*24+150
        self.row,self.col = pos
        self.rect.move_ip(self.col*24+150,self.row*24+60)
        
    def eat(self):
        utils.load_music(self.file).play()
        return 25 #score


class Activity:
    """  Base class mandatory for any SP activty.
    The activity is started by instancing this class by the core.
    This class must at least provide the following methods.
    start (self) called by the core before calling 'next_level'.
    post_next_level (self) called once by the core after 'next_level' *and* after the 321 count. 
    next_level (self,level) called by the core when the user changes levels.
    loop (self,events) called 40 times a second by the core and should be your 
                      main eventloop.
    get_helptitle (self) must return the title of the game can be localized.
    get_help (self) must return a list of strings describing the activty.
    get_helptip (self) must return a list of strings or an empty list
    get_name (self) must provide the activty name in english, not localized in lowercase.
    stop_timer (self) must stop any timers if any.
  """

    def __init__(self,SPGoodies):
        """SPGoodies is a class object that SP sets up and will contain references
        to objects, callback methods and observers
        TODO: add more explaination"""
        self.logger =  logging.getLogger("childsplay.packid.Activity")
        self.logger.info("Activity started")
        self.SPG = SPGoodies
        self.scoredisplay = self.SPG.get_scoredisplay()
        self.theme = self.SPG.get_theme()
        self.screen = self.SPG.get_screen()
        self.screenclip = self.SPG.get_screenclip()
        self.blit_pos = self.screenclip.left, self.screenclip.top
        self.orgscreen = pygame.Surface(self.screenclip.size) # we use this to restore the screen
        self.orgscreen.blit(self.screen, (0, 0), self.screenclip)
        self.backgr = self.SPG.get_background()
        # The location of the activities Data dir
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','PackidData')
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.CPdatadir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        # Location of the alphabet sounds dir
        self.absdir = self.SPG.get_absdir_path()# alphabet sounds dir
        self.rchash = utils.read_rcfile(os.path.join(self.my_datadir, 'c'))
        self.rchash['theme'] = self.theme
        self.logger.debug("found rc: %s" % self.rchash)
        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special CPGroup
        self.actives = SPSpriteUtils.SPInit(self.screen,self.backgr)
        
        self.language = self.SPG.get_localesetting()[0]
        self.ttf = None
        self.stopflag = None# used to stop the loop when not level 4
        self.score = 0
        self.letters_spots = []
        self.gamelevels = range(4)
        self.oldvolume = 0
    
    def __del__(self):
        #print 'Reached del'
        try:
            Snd.walk.stop()
        except:
            pass  
    
    def clear_screen(self):
        self.screen.blit(self.orgscreen,self.blit_pos)
        self.backgr.blit(self.orgscreen,self.blit_pos)
        pygame.display.update()

    def refresh_sprites(self):
        """Mandatory method, called by the core when the screen is used for blitting
        and the possibility exists that your sprites are affected by it."""
        self.actives.refresh()

    def get_helptitle(self):
        """Mandatory method"""
        return _("Packid")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "packid"
    
    def get_help(self):
        """Mandatory methods"""
        text=[_("The aim of the game:"),
        _("Try to 'eat' all the letters in the appropriated order."),
        _("There are thee levels with three words each."),
        _("When you have finished all the levels, without making to much mistakes"),
        _("(max two per word), you can play the last level which is a maze."),
        _("Try to find the way out while eating the fruits for extra points and"),
        _("funny sounds :-)")]
        return text 
    
    def get_helptip(self):
        """Mandatory method, when no tips available returns an empty list"""
        return []
        
    def get_helptype(self):
        """Mandatory method, you must set an type"""
        # Possible types are: Memory, Math, Puzzle, Keyboardtraining, Mousetraining
        #                     Language, Alphabet, Fun, Miscellaneous
        return _("Fun/Alphabet")
        
    
    def get_helplevels(self):
        """Mandatory method, must return a string with the number of levels
        in the follwing format:
        _("This level has %s levels") % number-of-levels"""
        return _("This activity has %s levels") % 4
    
    def pre_level(self,level):
        """Mandatory method.
        Return True to call the eventloop after this method is called."""
        self.logger.debug("pre_level called with: %s" % level)
        pass
        
    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        self.logger.debug("nextlevel called with: %s" % level)
        if level == 5:
            return False
        self.level = level
        self.dbmapper = dbmapper
        # Your top blit position, this depends on the menubar position 
        if self.blit_pos[1] == 0:
            y = 10
            self.gamearea = pygame.Rect(0, y, 800, 490) 
        else:
            y = 110
            self.gamearea = pygame.Rect(0, y, 800, 600) 
        return True
    
    def start(self):
        """Mandatory method."""
        Snd.waka = utils.load_music(os.path.join(self.my_datadir,'waka.wav'))
        Snd.walk = utils.load_sound(os.path.join(self.my_datadir,'walk.wav'))
        Snd.finlevel = utils.load_sound(os.path.join(self.my_datadir,'finlevel.wav'))
        Snd.bummer = utils.load_sound(os.path.join(self.CPdatadir,'bummer.wav'))
        Snd.eat = utils.load_sound(os.path.join(self.my_datadir,'eat.wav'))
        
        Img.datadir = self.my_datadir

        Img.pac_u = utils.load_image(os.path.join(self.my_datadir,'pac_u.png'),1)
        Img.pac_u_c = utils.load_image(os.path.join(self.my_datadir,'pac_u_c.png'),1)
        Img.pac_d = utils.load_image(os.path.join(self.my_datadir,'pac_d.png'),1)
        Img.pac_d_c = utils.load_image(os.path.join(self.my_datadir,'pac_d_c.png'),1)
        Img.pac_l = utils.load_image(os.path.join(self.my_datadir,'pac_l.png'),1)
        Img.pac_l_c = utils.load_image(os.path.join(self.my_datadir,'pac_l_c.png'),1)
        Img.pac_r = utils.load_image(os.path.join(self.my_datadir,'pac_r.png'),1)
        Img.pac_r_c = utils.load_image(os.path.join(self.my_datadir,'pac_r_c.png'),1)
        Img.pac_smile = utils.load_image(os.path.join(self.my_datadir,'pac_smile.png'),0)
        Img.pac_sad = utils.load_image(os.path.join(self.my_datadir,'pac_sad.png'),0)
        
        self.sidepan = SidePanel(self.gamelevels,self.ttf,self.blit_pos)
        
        # test if we have a words list for the locale
        try:
            wordsloc = self.SPG.get_localesetting()[0].split('_')[0]
            wordlist = 'words-'+wordsloc
            if not os.path.exists(os.path.join(self.my_datadir,wordlist)):
                raise IndexError
        except IndexError,info:
            self.logger.info("Can't find words for locale %s Using english for the words and sounds." % wordsloc)
            wordlist = 'words-en'
            wordsloc = 'en'
        try:
            items = utils.read_unicode_file(os.path.join(self.my_datadir,wordlist))
        except IOError,info:
            self.logger.exception("can't open or read words file %s" % \
                                  os.path.join(self.my_datadir,wordlist))
            raise MyError
        if self.SPG.get_localesetting()[1]:
            self.words = [s[:-1] for s in items]
        else:
            self.words = [s[:-1].upper() for s in items]
        #print self.words
        # Look for alphabet sounds for this locale.
        # If all fails we fall back to the "old" wahoo sound.
        self.alphabetdir = self.SPG.get_absdir_loc_path()
        if self.alphabetdir == 'en' and self.alphabetdir not in self.language:
            # if true the sound dir wasn't found and 'en' is returnt as fallback
            self.alphabetdir = None
        self.SPG.tellcore_set_dice_minimal_level(3)
        
        
    def _setup_last_level(self):
        self.fruits,spots = [],[]
        self.letters_spots = []# use this again for the fruits
        music = ['pac1.ogg','pac2.ogg','pac3.ogg','pac4.ogg','pac5.ogg','pac6.ogg']
        random.shuffle(music)
        for file in ('kers.png','banaan.png','aardbei.png','citroen.png','appel.png','peer.png'):
            spot = self._rand_spot()
            if spot in spots or spot in ((1,1),(15,23),(15,24),(16,23),(16,24)):
                spot = self._rand_spot()
            spots.append((spot))
            self.letters_spots.append((spot))
            self.fruits.append((LastLevelImg(music.pop(),file,spot)))
        self.letters_spots.append(((15,23)))    
    
    def post_next_level(self):
        """Mandatory method.
        This is called once by the core after 'next_level' *and* after the 321 count.
        You should place stuff in here that run in a seperate thread like sound play."""
        self.next_exercise()
        
    def get_score(self,timespend):
        """Mandatory method.
        @timespend is the time spend inside the level as it's calculated
        by the core.
        returns the score value for the past level.
        return None if no score value is used"""
        # As this is called when a level is finished we also use it to store
        # dbase stuff.
        m,s = timespend.split(':')
        seconds = int(m)*60 + int(s)
        
        self.dbmapper.insert('word',self.word)
        self.dbmapper.insert('wrong',self.gw)
        
        score = max(1,(10-self.gw) - (seconds/150.0))
        self.logger.debug("score is: %s" % score)
        return score
    
    def stop_timer(self):
        """You *must* provide a method to stop timers if you use them.
        The SPC will call this just in case and catch the exception in case 
        there's no 'stop_timer' method""" 
        try:
            self.timer.stop()
        except:
            pass

    def loop(self,events):
        """Mandatory method.
        This is the main eventloop called by the core 30 times a minute."""
        if self.stopflag:
            self.SPG.tellcore_game_end(True)
        self.stop = 0
        self.score = 0
        for event in events:
            pos = pygame.Rect(pygame.mouse.get_pos() + (4,4))
            if event.type is KEYDOWN and not self.objs_to_move:
                key = self._on_keypress(event.key)
                if key:
                    r = self.screen.blit(Img.backgr,self.packid.rect.inflate(2,2),self.packid.rect.inflate(2,2))
                    self.pack_pos = self.packid.update(key)
                    rr = self.screen.blit(self.packid.img,self.packid.rect)
                    pygame.display.update((r,rr))
        if self.objs_to_move: # Are there letters to move?
            self._move_objs()
        
        elif self.pack_pos in self.letters_spots: # Have we hit a letter?
            if self.level == 4 and self.pack_pos == (15,23):# pac hit exit in last level
                self.SPG.tellcore_game_end(True)
            else:
                for item in self.letter_objs:
                    if self.pack_pos == (item.row,item.col):
                        if item.char == 'FRUIT':
                            self.score = item.eat()
                            self.letter_objs.remove(item)
                            pygame.display.update(self.screen.blit(Img.backgr_start,item.rect,item.rect))# erase fruit
                            self.packid.img = Img.pac_smile
                            pygame.display.update(self.screen.blit(Img.pac_smile,self.packid.rect))
                        else:
                            self._check_letter(item)
                        break
        return 
    def next_exercise(self): 
        pygame.display.update(self.screen.fill((0,0,0), self.gamearea))
        self.letters_spots = []
        if self.level == 1:
            self.brick = utils.load_image(os.path.join(self.my_datadir,'brick.png'),0)
            matrix = self._read_grid('grid0.txt')
            self._build_field(matrix)
        elif self.level == 2:
            self.brick = utils.load_image(os.path.join(self.my_datadir,'leafs.png'),0)
            matrix = self._read_grid('grid1.txt')
            self._build_field(matrix,1)
        elif self.level == 3:
            self.brick = utils.load_image(os.path.join(self.my_datadir,'sea.png'),0)
            matrix = self._read_grid('grid2.txt')
            self._build_field(matrix,1)
        elif self.level == 4:
            if self.sidepan.get_level_score():
                load_music(os.path.join(self.my_datadir,'feelgood.ogg')).play()
                
                self.brick = utils.load_image(os.path.join(self.my_datadir,'camo.png'),0)
                m = MazeGen(17,25)
                matrix = m.get_maze()
                
                #matrix = self._read_grid('grid3.txt')
                self._build_field(matrix)
                self._setup_last_level()
            else:
                text = _("The last level is only available when you finish the first three levels without errors.")
                self.SPG.tellcore_info_dialog(text)
                self.SPG.tellcore_game_end(store_db=True)
                return
        else:
            self.stopflag = 1
            return
                       
        Img.backgr = self.screen.convert()
        Img.backgr_start = self.screen.convert()# keep a begin situation surface
        
        line1 = _("Find all the letters in the right order.")
        line2 = _("The word to find is: ")
        ### TODO fix RTL issues here
        if self.level != 4:
            if self.SPG.get_localesetting()[1]:
                surf,spam = utils.text2surf(line1,12,(183,255,50),self.ttf,1, bold=True)
                pygame.display.update(self.screen.blit(surf,(780-spam[0],0+self.gamearea.top)))
                surf,self.surfword_offset = utils.text2surf(line2,12,(183,255,50),self.ttf,1, bold=True)
                pygame.display.update(self.screen.blit(surf,(780-self.surfword_offset[0],24+self.gamearea.top)))
                word = random.choice(self.words)
            else:
                surf,spam = utils.text2surf(line1,12,(183,255,50),self.ttf,1, bold=True)
                pygame.display.update(self.screen.blit(surf,(28,4+self.gamearea.top)))
                surf,self.surfword_offset = utils.text2surf(line2,12,(183,255,50),self.ttf,1, bold=True)
                pygame.display.update(self.screen.blit(surf,(8,30+self.gamearea.top)))
                word = random.choice(self.words)
        
        # start the show and set some initial values
        self.gw = 0 #good/wrong counter
        if self.level == 4:
            self.word = ''
            self.objs_to_move,self.letter_objs = [],[]
            for obj in self.fruits:
                pygame.display.update(self.screen.blit(obj.img,obj.rect))
                self.letter_objs.append((obj))
                r = self.screen.blit(self.packid.img,(174,84))# blit packid
                pygame.display.update(r)
        else:
            self.word = word
            self._start_letters(word)
            self.sidepan.set_word(word)
            self._update_sidepanel()
            self.surfword = Word(word,self.ttf,self.SPG)
            self._update_surfword()
        x = 174
        y = 84 + self.gamearea.top
        self.packid = PacKid(matrix,x,y,24)
        
        self.pack_pos = (self.packid.row,self.packid.col)# start postion
        if self.level < 4:
            self.oldvolume = Snd.walk.get_volume()
            #print "volume:",self.oldvolume
            Snd.walk.set_volume(0.4)
            Snd.walk.play(-1)# stop when the letters are stopped (in def _move_objs)
        return True
    
    def _update_surfword(self):
        surf, letter_to_speak = self.surfword.update()
#        if self.SPG.get_localesetting()[1]:
#            # The Hebrew chars are rendered with a lot of empty space
#            # So we cut of the top and bottom to get it to blit in a mal space
#            cutoff_rect = surf.get_rect().inflate(0,-10)
#            pygame.display.update(self.screen.blit(surf,\
#                    (780-self.surfword_offset[0]-65,30),cutoff_rect))
#        else:
        pygame.display.update(self.screen.blit(surf,\
                        (8+self.surfword_offset[0],30+self.gamearea.top)))
        pygame.time.wait(1000)
    
    def _speak_letter(self,letter):
        """Plays the alphabet soundfile for @letter
        Return True on succes and False on failure"""
        return utils.speak_letter(letter.lower(), self.language)
           
    def _update_sidepanel(self):
        pygame.display.update(self.screen.blit(self.sidepan.get_surf(),(0,60 + self.gamearea.top)))
    
    def _read_grid(self,name):
        grid = []
        filename = os.path.join(self.my_datadir,name)
        f = open(filename,'r')
        for line in f.readlines():
            grid.append((tuple(map(int,line[:-1]))))
        f.close()
        return tuple(grid)
    
    def _build_field(self,matrix, ran=0):
        Img.matrix = matrix #stash ref
        surf = pygame.Surface((620,428))
        y = 10
        for row in matrix:
            x = 10
            for item in row:
                if not item:
                    if ran:
                        brick = self.brick#.convert()
                        angle = random.choice((0,90,180,270))
                        surf.blit(pygame.transform.rotate(brick,angle),(x,y))
                    else:
                        surf.blit(self.brick,(x,y))
                elif item == 2:# special
                    i = utils.load_image(os.path.join(self.my_datadir,'exit.png'),0)
                    #image = 48x48
                    #x -= 24
                    #y -= 24
                    surf.blit(i,(x,y))
                    break
                x +=24
            y += 24
        pygame.display.update(self.screen.blit(surf,(140,50 + self.gamearea.top)))
        
    def _start_letters(self,word):
        self.word,spots = word,[]
        self.letter_to_find = 0
        self.objs_to_move,self.letter_objs = [],[]# lists to hold Letters objects
        Letters.instance = 0 #reset instance counter
        for item in word:
            spot = self._rand_spot()
            if spot in spots or spot in ((8,11),(8,12),(8,13),(1,1)):# same coords or inside the box,packid
                spot = self._rand_spot()
            spots.append((spot))
            self.objs_to_move.append((Letters(item,(255,255,255),spot,self.ttf, self.gamearea.top)))
            
            #print item,spot,Img.matrix[spot[0]][spot[1]]

    def _rand_spot(self):
        #return (1,3)
        while 1:
            spot = (random.randrange(1,17),random.randrange(1,24))
            if Img.matrix[spot[0]][spot[1]]:
                break
        return spot
        
    def _on_keypress(self,key):
        if key == K_UP:
            return 'UP'
        elif key == K_DOWN:
            return 'DOWN'
        elif key == K_LEFT:
            return 'LEFT'
        elif key == K_RIGHT:
            return 'RIGHT'
        
    def _move_objs(self):
        objs_to_remove,dirty_rects = [],[]
        for obj in self.objs_to_move:
            dirty_rects.append((self.screen.blit(Img.backgr,obj.rect.inflate(2,2),obj.rect.inflate(2,2))))
            flag = obj.update()
            if flag:
                rec = obj.rect
                rec.move_ip(4,0)
                Img.backgr.blit(obj.image,rec)
                objs_to_remove.append((obj))
                self.letter_objs.append((obj)) # store letters objs 
                # store the pos of the letter, used to check collide with packid
                # take these positions because a obj maybe died (look in class)
                self.letters_spots.append(((obj.row,obj.col))) 
            dirty_rects.append((self.screen.blit(obj.image,obj.rect)))
        pygame.time.wait(100)
        pygame.display.update(dirty_rects)
        
        if objs_to_remove:
            for item in objs_to_remove:
                self.objs_to_move.remove(item)
                if self.objs_to_move == []:
                    Snd.walk.stop()
                    Snd.walk.set_volume(self.oldvolume)
                    r= self.screen.blit(self.packid.img,self.packid.rect)# blit packid
                    pygame.display.update(r)
                    pygame.time.wait(500)
    
    def _check_letter(self,obj):
        if obj.char == self.word[self.letter_to_find]:
            # Good letter
            #print 'letter',obj.char
            self.letter_objs.remove(obj)
            Img.backgr.blit(Img.backgr_start,obj.rect.inflate(8, 8),obj.rect.inflate(8, 8))# erase letter
            self.packid.img = Img.pac_smile
            pygame.display.update(self.screen.blit(Img.pac_smile,self.packid.rect))
            if self.alphabetdir:
                if not self._speak_letter(obj.char):
                    Snd.eat.play()
            else:
                Snd.eat.play()
            pygame.time.wait(500)
            
            self.score = 10
            self.letters_spots.remove(self.pack_pos)
            #print self.letters_spots
            if self.letters_spots:
                self.letter_to_find += 1 
                self._update_surfword()
            else: # last letter 
                Snd.finlevel.play()
                self.score = 100
                Img.backgr.blit(Img.backgr_start,obj.rect,obj.rect)# erase letter
                self.sidepan.set_good_wrong(self.gw)
                self._update_sidepanel()   
                pygame.time.wait(2000)
                if self.sidepan.switch_task():
                    self.SPG.tellcore_level_end(store_db=True)
                else:
                    self.next_exercise() 
        else:
            #wrong letter
            if self.packid.img is Img.pac_sad:
                return # still on the wrong letter
            self.gw += 1
            Snd.bummer.play()
            self.packid.img = Img.pac_sad
            pygame.display.update(self.screen.blit(Img.pac_sad,self.packid.rect))
            pygame.time.wait(500)
        
