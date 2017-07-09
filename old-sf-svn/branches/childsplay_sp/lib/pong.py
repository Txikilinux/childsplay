
# -*- coding: utf-8 -*-

# Copyright (c) 2008 Stas Zytkiewicz stas.zytkiewicz@gmail.com
#
#           pong.py
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
# self.logger =  logging.getLogger("schoolsplay.pong.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("schoolsplay.pong")

# standard modules you probably need
import os,sys,random

import pygame
from pygame.constants import *

import childsplay_sp.utils as utils
from childsplay_sp.SPConstants import *
import childsplay_sp.SPSpriteUtils as SPSpriteUtils

# containers that can be used globally to store stuff
class Img:
    pass
class Snd:
    pass
class Misc:
    """ Container to store all kind of stuff"""
    pass
    
# Options used by the game.
# THESE OPTIONS ARE USED, NO CONFIG FILE EXISTS IN CHILDSPLAY_SP
# These will be merged with the ones from the rcdic.
# When there's a problem with the rcdic we use these as defaults. 
defaults_dict = {'__name__':'default',\
                'sound':'yes',\
                'computerAI':'impossible',\
                'gameplay':'single',\
                'batsize':'72',\
                'batspeed':'12',\
                'ballspeed':'5',\
                'goalsize':'300',\
                'winpoints':'11',\
                'useprofile':'none',\
                'left_keyup':'q',\
                'left_keydown':'a',\
                'right_keyup':'p',\
                'right_keydown':'l'}
                
## set ONEPLAYER to 1 for single player pong
## set to 0 for two players, one human and one computer
## this works by moving the left goal and bat behind the wall.
## So everything works the same as in multiplayer but it looks like single player
ONEPLAYER = 1# how may persons, 1 = 1, 0 = 2 or 1 + computer
PCPLAYER = 0# used only in combination with ONEPLAYER = 0

class Winner:
    def __init__(self,side):
        img = self.load_stuff()
        if side == 'left': pos = (200,150)
        else: pos = (500,150)
        Snd.winner.play()
        pygame.display.update(Img.screen.blit(img,pos))
            
    def load_stuff(self):
        return Img.winner
        
class Loser(Winner):
    def __init__(self,side):
        Winner.__init__(self,side)
    def load_stuff(self):
        return Img.loser

class PcPlayer:
    """The computer player.
    This will control the bat by adding pygame events to the pygame event queue.
    """
    def __init__(self):
        """bat must be a Bat class object."""
        self.up,self.down = ord(Misc.bat_l.up),ord(Misc.bat_l.down)
        self.u_up,self.u_down = unicode(Misc.bat_l.up), unicode(Misc.bat_l.down)
        self.batstarty = Misc.bat_l.rect[1]
        self.balldirection = Misc.ball.xoffset
        self.event_dict = {'key':self.up,'unicode':self.u_up}
        self.keystate = KEYUP
        #self.counter = 2# about 0.15 second (clockrate chidsplay 30/sec)
        self.AIlist = (0,)*(int(Misc.rc_dic['ballspeed'])-1) + (1,)
        Misc.bat_l.init_speed = 6
        if Misc.rc_dic['computerAI'] == 'hard':
            self.AIlist = (0,0, 1)
        elif Misc.rc_dic['computerAI'] == 'impossible':
            self.AIlist = (0,0)
        
    def play(self,events):
#        if self.counter > 0: 
#            self.counter -= 1
#            return events
#        else:
#            self.counter = 2
        if self.keystate is KEYDOWN:
            self.keystate = KEYUP
            events.append(pygame.event.Event(self.keystate,self.event_dict))
            return events
        #the ball is moving away from us and we're not back in the middle
        elif Misc.ball.xoffset > 0 and \
                Misc.bat_l.rect[1] == self.batstarty:
            return events  
        elif self.keystate is KEYUP:
            self.keystate = KEYDOWN
        if self.keystate is KEYUP and random.choice(self.AIlist):
            return events        
        bally = Misc.ball.rect[1]
        baty = Misc.bat_l.rect.inflate(0,-4)[1]
        #print bally,baty
        if bally > baty:
            self.event_dict['key'] = self.down
            self.event_dict['unicode'] = self.u_down
        else:
            self.event_dict['key'] = self.up
            self.event_dict['unicode'] = self.u_up
        event = pygame.event.Event(self.keystate,self.event_dict)
        events.append(event)
        return events

class ScoreBoard:
    def __init__(self,end=11,size=48):
        try:
            s = int(Misc.rc_dic['winpoints'])
        except (TypeError,KeyError):
            pass
        else: end = s
        self.pos_l,self.pos_r = (340,20),(410,20)
        self.size = size
        self.end = end#at which score the game ends
        self.score = (0,0)
        self.black = pygame.Surface((48,48))
                
    def set_score(self,score,side):
        if side == 'right':
            self.score = (self.score[0],self.score[1]+score)
        else:
            self.score = (self.score[0]+score,self.score[1])
        self.update()            
        
    def update(self):
        rects = []
        sr = self.black.convert()
        sr.blit(utils.char2surf(str(self.score[1]),self.size,GREEN),(0,0))
        sl = self.black.convert()
        sl.blit(utils.char2surf(str(self.score[0]),self.size,GREEN),(0,0))
        rects.append(Img.screen.blit(sl,(self.pos_l)))
        rects.append(Img.screen.blit(sr,(self.pos_r)))
        rects.append(Img.backgr.blit(sl,(self.pos_l)))
        rects.append(Img.backgr.blit(sr,(self.pos_r)))
        pygame.display.update(rects)
        if self.end in self.score:
            # hack to erase the sprite. Because the position of the sprite is changed
            # after it's drawn on the screen. So we must erase it's 'old' position.
            Misc.ball.rect = Misc.ball.oldrect
            Misc.ball.erase_sprite()
            pygame.time.wait(3000)
            if self.score[0] == self.end:
                Winner('left')
                Loser('right')
            else:
                Winner('right')
                Loser('left')
            pygame.time.wait(9500)
            # End of this game
            self.score = (0,0)
            self.update()

class Goal:
    def __init__(self,size=(20,300)):
        try:
            s = int(Misc.rc_dic['goalsize'])
        except (TypeError,KeyError):
            pass
        else: size = (20,s)
        self.image = pygame.Surface(size).convert()
        self.score = 0
        #self.image.fill((255,255,255))# use to display goals (debugging)
        self.rect = self.image.get_rect()
    def set_scoreboard(self,side):
        self.side = side#this should be the other side
    def move(self,pos):
        self.rect.move_ip(pos)
    def scored(self):
        Snd.goal.play()
        self.score += 1
        Misc.scoreboard.set_score(1,self.side)
    def get_score(self):
        return self.score    

class Ball(SPSpriteUtils.SPSprite):
    def __init__(self,speed=4):
        try:
            s = int(Misc.rc_dic['ballspeed'])
        except (TypeError,KeyError):
            pass
        else: speed = s
        self.image = pygame.Surface((24,24)).convert()
        pygame.draw.circle(self.image,\
                           GREEN,\
                           (12,12),\
                           12,\
                           0)
        self.image.set_colorkey(self.image.get_at((0, 0)), RLEACCEL)
        SPSpriteUtils.SPSprite.__init__(self,self.image)
        self.rect = self.image.get_rect()
        self.xpos,self.ypos = 390,250
        self.rect.move_ip(self.xpos,self.ypos)
        self.xoffset = random.choice((-speed,speed))
        self.yoffset = random.choice((-speed,speed))
        self.move()
        
    def move(self):
        self.oldrect = self.rect
        if self.rect.centerx > 764:
            Snd.bump.play()
            self.xoffset = -self.xoffset
        if self.rect.centerx < 37:
            Snd.bump.play()
            self.xoffset = abs(self.xoffset)
        if self.rect.centery > 464:
            Snd.bump.play()
            self.yoffset = -self.yoffset
        if self.rect.centery < 36:
            Snd.bump.play()
            self.yoffset = abs(self.yoffset)
        self.rect.centerx += self.xoffset
        self.rect.centery += self.yoffset

    def update(self,*args):
        self.move()
        for obj in (Misc.goal_l,Misc.goal_r):
            if self.rect.colliderect(obj.rect):
                obj.scored()
                return -1
        collide = self.rect.colliderect(Misc.bat_r.rect) or \
                    self.rect.colliderect(Misc.bat_l.rect)
        if collide:
            self.xoffset = -self.xoffset
            Snd.pong.play()

class Bat(SPSpriteUtils.SPSprite):
    def __init__(self,action_keys,size=64,speed=12):
        self.current_key = None#used to fix the "no unicode key in keyup event" pygame bug
        try:
            s = int(Misc.rc_dic['batspeed'])
            bs = int(Misc.rc_dic['batsize'])
        except (TypeError,KeyError):
            pass
        else: 
            size = bs
            speed = s
        self.init_speed = speed
        self.speed = 0
        self.size = size
        self.top,self.bottom = 18,482
        self.up,self.down = action_keys[0].upper(),action_keys[1].upper()
        self.image = pygame.Surface((8,size))
        self.image.fill(GREEN)
        SPSpriteUtils.SPSprite.__init__(self,self.image)
        self.rect = self.image.get_rect()
            
    def set_position(self,pos):
        self.rect.move_ip(pos[0],pos[1])
        
    def update(self,*args):
        """This keeps moving until a keyup event is raised"""
        #c = None
        for event in Misc.events:
            if event.type == KEYDOWN:
                try:
                    c = event.unicode.upper()
                except ValueError,info:
                    print info
                    return
                else:
                    if c == self.up:
                        self.speed = self.init_speed
                        self.speed = -self.speed
                        self.current_key = c
                    elif c == self.down:
                        self.speed = self.init_speed
                        self.speed = abs(self.speed)
                        self.current_key = c
            elif event.type == KEYUP and self.current_key:
                self.speed = 0
                self.current_key = None
        newrect = self.rect.move(0,self.speed)
        if newrect.top > self.top and newrect.bottom < self.bottom:
            self.rect = newrect

class Activity:
    """  Base class mandatory for any SP activty.
    The activity is started by instancing this class by the core.
    This class must at least provide the following methods.
    start (self) called by the core before calling loop.
    next_level (self,level) called by the core when the user changes levels.
    loop (self,events) called 40 times a second by the core and should be your 
                      main eventloop.
    helptitle (self) must return the title of the game can be localized.
    help (self) must return a list of strings describing the activty.
    name (self) must provide the activty name in english, not localized in lowercase.
  """

    def __init__(self,SPGoodies):
        """SPGoodies is a class object that SP sets up and will contain references
        to objects, callback methods and observers
        TODO: add more explaination"""
        self.logger =  logging.getLogger("schoolsplay.pong.Activity")
        self.logger.info("Activity started")
        self.SPG = SPGoodies
        self.screen = self.SPG.get_screen()
        self.backgr = self.SPG.get_background()
        Img.org_screen = self.screen.convert()
        Img.org_backgr = self.backgr.convert()
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','PongData')
        Img.screen = self.screen
        Img.backgr = self.backgr
        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special CPGroup
        Misc.actives = SPSpriteUtils.SPInit(self.screen,self.backgr)
        Misc.rc_dic = defaults_dict
        
    def get_helptitle(self):
        """Mandatory method"""
        return _("Pong")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "pong"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of the game:"),
        _("The classic pong game where you must hit a ball with your bat."),
        _("There are three modes to choose from:"),\
        _("Single play - Hit the ball against the wall."),\
        _("Multi player against the computer - Try to defeat the computer."),\
        _("Multi player - Play against another player."),\
        _("In the multiplayer modes, the one who has 11 points wins."),\
        " ",\
        _("The game has a configuration file called 'pongrc', located in the .childsplay directory of your homedirectory."),\
        _("In this file you can set a number of options to change the game play."),\
        " "]
        return text 
        
    def get_helptip(self):
        """Mandatory method, when no tips available returns an empty list"""
        text = []
        return text 
        
    def get_helptype(self):
        """Mandatory method, you must set an type"""
        # Possible types are: Memory, Math, Puzzle, Keyboardtraining, Mousetraining
        #                     Language, Alphabet, Fun, Miscellaneous
        return _("Fun")

    def get_helplevels(self):
        """Mandatory method, must return a string with the number of levels
        in the follwing format:
        _("This level has %s levels" % number-of-levels)"""
        return _("This activity has %s levels") % 1
    
    def start(self):
        """Mandatory method."""
        
        Img.screen.fill((0,0,0))
        pygame.display.update()
        fs = 36
        Misc.scoreboard = ScoreBoard(size=fs)
        Img.winner = utils.load_image(os.path.join(self.my_datadir,'winner.jpg'),1)
        Img.loser = utils.load_image(os.path.join(self.my_datadir,'loser.jpg'),1)
        self.skipstart = None# used when the user sets a predefined game play in the config file
        self.skipssplash = None
        if Misc.rc_dic['sound'].lower() == 'no':
            Snd.pong = utils.load_sound(os.path.join(self.my_datadir,''))
            Snd.winner = utils.load_sound(os.path.join(self.my_datadir,''))
            Snd.goal = utils.load_sound(os.path.join(self.my_datadir,''))
            Snd.bump = utils.load_sound(os.path.join(self.my_datadir,''))
        else:
            Snd.pong = utils.load_sound(os.path.join(self.my_datadir,'pick.wav'))
            Snd.winner = utils.load_music(os.path.join(self.my_datadir,'winner.ogg'))
            Snd.goal = utils.load_sound(os.path.join(self.my_datadir,'goal.wav'))
            Snd.bump = utils.load_sound(os.path.join(self.my_datadir,'bump.wav'))
        #set kind of game play
        # we only check for multi and multipc, anything else is considerd single play
        # which is the default
        if Misc.rc_dic['gameplay'] == 'multi':
            self.restart([[None,'2']])
            self.skipstart = 1
        elif Misc.rc_dic['gameplay'] == 'multipc':
            self.restart([[None,'3']])
            self.skipstart = 1
        
    def next_level(self,level,dbmapper):
        """Return True if there levels left.
        False when no more levels left."""
        if level == 2:
            return False
        return True
        
    def post_next_level(self):
        """Mandatory method.
        This is called by the core after 'next_level' *and* after the 321 count.
        You should place stuff in here that run in a seperate thread like sound play."""
        self.SPG.tellcore_enable_dice(False)
        if not self.skipstart:
            self._get_choice()
        if not self.skipssplash:
            self._splash_controls()
        self.next_exercise()  
    
    def next_exercise(self):
        self.logger.debug("ONEPLAYER: %s PCPLAYER: %s" % (ONEPLAYER,PCPLAYER))

        self.PCplayer = None
        self._draw_field()
        Misc.scoreboard.update()
        Misc.goal_r = Goal()
        Misc.goal_r.set_scoreboard('left')
        Misc.goal_r.move((774,100))
        Misc.goal_l = Goal()
        Misc.goal_l.set_scoreboard('right')
        if ONEPLAYER:
            Misc.goal_l.move((-20,100))# move behind the wall
        else:
            Misc.goal_l.move((6,100))
        Img.screen.blit(Misc.goal_r.image,Misc.goal_r.rect)
        Img.screen.blit(Misc.goal_l.image,Misc.goal_l.rect)
                
        pygame.display.update()
        
        lspeed,rspeed = 8,8
        try:
            u = unicode(Misc.rc_dic['right_keyup'])
            d = unicode(Misc.rc_dic['right_keydown'])
        except (TypeError,KeyError):
            u,d = u'p',u'l'
        Misc.bat_r = Bat(action_keys=(u,d),speed=rspeed)# to keep a reference to the bat, see class Ball
        Misc.bat_r.set_position((768,220))
        try:
            u = unicode(Misc.rc_dic['left_keyup'])
            d = unicode(Misc.rc_dic['left_keydown'])
        except (TypeError,KeyError):
            u,d = u'q',u'a'
        Misc.bat_l = Bat(action_keys=(u,d),speed=lspeed)
        
        if ONEPLAYER:
            Misc.bat_l.set_position((-20,220))
        else:
            Misc.bat_l.set_position((24,220))
        Misc.ball = Ball()# now the computer player can check the ball
        Misc.actives.add(Misc.ball)
        if PCPLAYER and not ONEPLAYER:#we play against the pc
            self.PCplayer = PcPlayer()
        
        Misc.actives.add([Misc.bat_r,Misc.bat_l])
        r = Misc.actives.draw(Img.screen)
        pygame.display.update(r)
            
    def _draw_field(self):
        Img.screen.fill((0,0,0))
        Img.backgr.fill((0,0,0))
        
        box = pygame.Rect(0,0,800,500).inflate(-32,-32)
        #box.inflate(-32,-32)
        pygame.draw.rect(Img.screen,\
                         GREEN,\
                         box,\
                         4)
        pygame.draw.line(Img.screen,\
                          GREEN,\
                          (398,16),\
                          (398,484),\
                          4)
        pygame.draw.line(Img.backgr,\
                          GREEN,\
                          (398,16),\
                          (398,484),\
                          4)
                          
    def _splash_controls(self):
        Img.screen.fill((0,0,0))
        txt = _("Use these keys on your keyboard to control the bat.")
        txtlist = utils.txtfmt([txt],36)
        s1,spam = utils.font2surf(txtlist[0],18,GREEN, bold=True)
        s2,spam = utils.font2surf(txtlist[1],18,GREEN, bold=True)
        Img.screen.blit(s1,(100,200))
        Img.screen.blit(s2,(100,240))
        pygame.display.update()
        rects = []
        fsize = 24
        
        surf = pygame.Surface((60,300))
        surf.blit(utils.load_image(os.path.join(self.my_datadir,'arrow_up.png')),(4,0))
        #surf.blit(utils.load_image(os.path.join(self.my_datadir,'bat.png')),(26,120))
        surf.blit(utils.load_image(os.path.join(self.my_datadir,'arrow_down.png')),(4,240))
        surf_r = surf.convert()# copy for the right side
        print ONEPLAYER, PCPLAYER
        if ONEPLAYER == 0 and PCPLAYER == 0:
            surf.blit(utils.char2surf(Misc.rc_dic['left_keyup'].upper(),fsize,GREEN, bold=True),(16,70))
            surf.blit(utils.char2surf(Misc.rc_dic['left_keydown'].upper(),fsize,GREEN, bold=True),(16,190))
        surf_r.blit(utils.char2surf(Misc.rc_dic['right_keyup'].upper(),fsize,GREEN, bold=True),(16,70))
        surf_r.blit(utils.char2surf(Misc.rc_dic['right_keydown'].upper(),fsize,GREEN, bold=True),(16,190))
        rects.append(Img.screen.blit(surf,(40,100)))
        rects.append(Img.screen.blit(surf_r,(700,100)))
        pygame.display.update(rects)
        pygame.time.wait(4000)
        self.skipssplash = 1

    def _get_choice(self):
        """Display the three choices of game play.
        This will put the menu items in the actives group which then will be updated
        in the game loop. When the users picks one the result will be handled by
        the restart method."""
        self.choice = None # will be set in loop
        positions = [(130,70),(130,220),(130,370)]
        images = ('single.jpg','multi_person.jpg','multi_pc.jpg')
        head = _("Choose the game to play:")
        s = utils.char2surf(head,32,GREEN, bold=True)
        pygame.display.update(Img.screen.blit(s,(80,4)))
        for pos,img,data in map(None,positions,images,('1','2','3')):
            img = os.path.join(self.my_datadir,img)
            obj = SPSpriteUtils.SPButton(utils.load_image(img),pos,data)
            Misc.actives.add(obj) 
        clock = pygame.time.Clock()
        self.stop_choiceloop = 0
        while not self.stop_choiceloop:
            pygame.event.pump()
            self.loop(pygame.event.get())
            clock.tick(30)
        # The loop is stopped by setting stop_choiceloop to True in loop
        for obj in Misc.actives.get_sprites():
            obj.erase_sprite()
        Misc.actives.empty()
        
    def restart(self,v):
        """Used to restart the game when there's a goal.
        This is also used to set the global vars when ending the first level(menu choices)"""
        global ONEPLAYER,PCPLAYER
        self.logger.debug("restart called with %s" % v)
        
        obj,val = v[0][0],v[0][1]
        if val == -1:#scored
            Misc.actives.empty()
            self.next_exercise() 
        # Handle the vals from the first level
        else:
            if val == '2':# 1 is the default so we don't test it
                ONEPLAYER = 0
            elif val == '3':
                ONEPLAYER = 0
                PCPLAYER = 1
            Misc.actives.empty()    
            #self.SPG.tellcore_level_end()
        
    def get_score(self,timespend):
        """Mandatory method.
        @timespend is the time spend inside the level as it's calculated
        by the core.
        returns the score value for the past level.
        return None if no score value is used"""
        m,s = timespend.split(':')
        seconds = int(m)*60 + int(s)
        
    def loop(self,events):
        """Mandatory method.
        This is the main eventloop called by the core 30 times a minute."""
        item,self.stop,Misc.score = None, 0,0
        if PCPLAYER:
            events = self.PCplayer.play(events)# let the computer make his move. 
            #This will add an event to pygame events. Just like a real player :-)
        Misc.events = []#This is a hack to be able to use keydown AND keyup with
                        #CPSprite stuff
        for event in events:
            if event.type == KEYDOWN or \
                    event.type == KEYUP or\
                    event.type == MOUSEBUTTONDOWN:
                item = event
                Misc.events.append(event)
        
        v = Misc.actives.refresh(item)# This will return -1 when there's a score
        # The menu objects from the first level will return strings ('1','2' or '3')
        if v:
            if not self.stop_choiceloop:
                self.stop_choiceloop = 1
                self.restart(v)
            else:
                self.restart(v)
        return 
        
