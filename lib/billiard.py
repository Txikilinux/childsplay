
# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zytkiewicz stas.zytkiewicz@schoolsplay.org
# Copyright (c) 2004  Matias Grana matiasg@dm.uba.ar
#           billiard.py
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
# self.logger =  logging.getLogger("childsplay.billiard.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("childsplay.billiard")

# standard modules you probably need
import os,sys,operator,random
from math import sqrt,acos

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
class Misc:
    pass
class Hole:
    pass

class Ball(SPSpriteUtils.SPSprite):
    """
    A ball that can move on the table, collide with other ball and enter the hole.
    """
    def __init__(self, pic, start, kind):
        self.image = pic
        SPSpriteUtils.SPSprite.__init__(self,self.image,name=kind)# embed it in this class, eg make SPSpriteUtils.SPSprite part of Ball
        self.rect = self.posint = pic.get_rect().move(start)
        self.posreal = (self.posint[0], self.posint[1])
        self.size = (self.posint.right - self.posint.left, self.posint.bottom - self.posint.top)
        self.sqradius = (self.size[1]/2)**2
        self.smthns = .95  #between 0 and 1. The higher, the more the ball will roll
        self.direc = (0,0)
        self.thkns = .9  #transmission of speed in collision
    
    def on_update(self, *args):
        """ This is called on every refresh call."""
        v = self.madehole()
        return v# we use this to return 1 to the refresh call
    def moveit(self):
        """ Moves the ball """
        # It is important that the position be a real number. Otherwise the movement is not nice.
        # We cast it to int to blit it.
        self.posreal = (self.posreal[0]+self.direc[0], self.posreal[1]+self.direc[1])
        self.posint.left, self.posint.top = int(self.posreal[0]), int(self.posreal[1])
        # Don't fall out of the table!
        if self.posint.right > 792:
            self.posint.left = 792 - self.size[0]
            self.posreal = (self.posint.left, self.posreal[1])
            self.direc = (-self.direc[0],self.direc[1])
        if self.posint.bottom > 592:
            self.posint.top = 592 - self.size[1]
            self.posreal = (self.posreal[0], self.posint.top)
            self.direc = (self.direc[0],-self.direc[1])
        if self.posint.left < 8:
            self.posint.left = 8
            self.posreal = (8, self.posreal[1])
            self.direc = (-self.direc[0],self.direc[1])
        if self.posint.top < 108:
            self.posint.top = 108
            self.posreal = (self.posreal[0], 108)
            self.direc = (self.direc[0],-self.direc[1])
        # Slow down a bit!
        self.direc = (self.direc[0] * self.smthns, self.direc[1] * self.smthns)
        # If it's almost stopped, just stop it.
        if self.direc[0]**2 + self.direc[1]**2 < 1:
            self.direc = (0,0)
            return 0
        return 1
    def addtodir(self, x, y):
        """ changes the direction of the ball """
        self.direc = (self.direc[0]+x, self.direc[1]+y)
        return self.direc[0]**2+self.direc[1]**2
    def addtopos(self, x, y):
        """ changes position of the ball """
        self.posreal = (self.posreal[0]+x, self.posreal[1]+y)
        self.posint.left += x
        self.posint.top += y
    def callback(self, mousepos, mousebut):
        """ What to do under mouse button pressed.
         This is not a callback like the ones used in a typical SPSpriteUtils.SPSprite object."""
        diff = self.posint.move(self.size[0]/2-mousepos[0],self.size[1]/2-mousepos[1])
        dist = sqrt(diff[0]**2+diff[1]**2)
        # see if the kick was inside the ball and out from the center. If yes, change direction.
        if (0 < dist <= self.size[0]/2):
            valtoreturn = 1
            if (mousebut == 1):
                self.direc = (diff[0] / dist,  diff[1] / dist)
        #utils.load_music(Snd.throw).play()
        else:
            valtoreturn = 0
        return valtoreturn
    def checkcollision(self, otherobj):
        """ checks whether two objects collide """
        x,y = (self.posreal[0] - otherobj.posreal[0], self.posreal[1] - otherobj.posreal[1])
        squaredist = x**2 + y**2
        dist = sqrt(squaredist)
        # check if both objects collide. If yes, change their directions.
        overlap = dist - (self.size[0] + otherobj.size[0]) / 2
        if overlap < 0:
            diffvel = (self.direc[0] - otherobj.direc[0], self.direc[1] - otherobj.direc[1])
            coef = self.thkns * (x*diffvel[0] + y*diffvel[1]) / squaredist
            newvel = self.addtodir(-x * coef, -y * coef)
            self.addtopos(-x * overlap / dist, -y * overlap / dist)
            self.moveit()
            newvelotherobj = otherobj.addtodir(x * coef, y * coef)
            otherobj.moveit()
            return (1, newvel, newvelotherobj)
        return (0,)
    def madehole(self):
        """ checks if ball entered the hole """
        diff = (self.posreal[0] - Hole.pos[0], self.posreal[1] - Hole.pos[1])
        sqdist = diff[0]**2 + diff[1]**2
        # this checks whether d(b,h) < radius  (b = center of ball, h = center of hole)
        if sqdist < self.sqradius:
            return (self,1)# self is the object 
        return 0

class Stick(SPSpriteUtils.SPSprite):
    def __init__(self, pic, start):
        self.image = self.origpic = pic
        SPSpriteUtils.SPSprite.__init__(self,self.image)
        self.origsize = pic.get_rect()
        self.angle = 0
        self.start = start
        self.rect = self.posint = pic.get_rect().move(start)
        self.disp = [0,0]
        self.maxstrength = 80 # the maximum force to hit the ball
    def prepare(self, posmouse, posball):
        self.positmouse = posmouse
        dif = (posball[0] - posmouse[0], posball[1] - posmouse[1])
        dist = sqrt(dif[0]**2 + dif[1]**2)
        dif = (dif[0]/dist, dif[1]/dist)
        self.angle = acos(dif[0]) * 180 / 3.141593
        if dif[1] > 0:
            self.angle = 360 - self.angle
        self.image = self.pic = pygame.transform.rotate(self.origpic, self.angle)
        if dif[0]>0:
            self.disp[0] = -self.origsize.right*dif[0]
        else:
            self.disp[0] = 0
        if dif[1]>0:
            self.disp[1] = -self.origsize.right*dif[1]
        else:
            self.disp[1] = 0
        self.displacement = (posmouse[0]+self.disp[0],posmouse[1]+self.disp[1])
        self.rect = self.posint = self.pic.get_rect().move(self.displacement)
    def update(self, *args):
        pass
    def grow(self, scale):
        # make the stick grow to indicate strength
        sc = (float(scale)/self.maxstrength)**2 + 1
        self.image = pygame.transform.scale(self.pic, (int(self.posint.width * sc), int(self.posint.height * sc) ))
        self.rect = self.pic.get_rect().move(self.positmouse[0] + int(self.disp[0]*sc), self.positmouse[1] + int(self.disp[1]*sc) )
        Misc.group.refresh()
    def draw(self, screen):
        screen.blit(self.pic, self.posint)
    
class MovingSign(SPSpriteUtils.SPSprite):
    def __init__(self, txt, size, start, stop, step, fcol, scr, bck, era):
        self.image,self.size = utils.text2surf(txt, size, fcol, bold=True)
        SPSpriteUtils.SPSprite.__init__(self,self.image)
        self.rect = self.image.get_rect()
        self.set_movement(start, stop, step, 1, 0)
        self.add(Misc.movingsign)
        self.display_sprite()
        self.wait = max(abs(stop[0]-start[0]),abs(stop[1]-start[1]))
        while self.wait:
            self.wait -= step
            Misc.movingsign.refresh()
            pygame.time.wait(5)
        self.remove(Misc.movingsign)
        if era:
            Misc.movingsign.refresh()

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
        self.logger =  logging.getLogger("childsplay.billiard.Activity")
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
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','BilliardData')
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.CPdatadir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        # Location of the alphabet sounds dir
        self.absdir = self.SPG.get_absdir_path()# alphabet sounds dir
        self.rchash = utils.read_rcfile(os.path.join(self.my_datadir, 'c'))
        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special CPGroup
        
        Misc.actives = SPSpriteUtils.SPInit(self.screen,self.backgr)
        Misc.movingsign = SPSpriteUtils.SPGroup(self.screen, self.backgr)
        Misc.group = SPSpriteUtils.SPGroup(self.screen, self.backgr)
        # MovingSign controls itself
        MovingSign(_("Billiard Game"), 48, (100,100), (100,400), 1, (8,0,120), self.screen, self.backgr, 1)
            
    def clear_screen(self):
        self.screen.blit(self.orgscreen,self.blit_pos)
        self.backgr.blit(self.orgscreen,self.blit_pos)
        pygame.display.update()

    def refresh_sprites(self):
        """Mandatory method, called by the core when the screen is used for blitting
        and the possibility exists that your sprites are affected by it."""
        Misc.actives.refresh()

    def get_helptitle(self):
        """Mandatory method"""
        return _("Billiard")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "billiard"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),
        _("You have to make the blue ball enter the hole (in level 1)"),
        _("and the red ones in levels 2 and 3."),
        _("Use the right mousebutton to aim and the left button to hit the ball."),
        _("The longer you hold the left button the harder it will hit the ball."),
        _("The fewer hits you need to get the ball in the hole, the more points you get."),
        ]
        return text 
    
    def get_helptip(self):
        """Mandatory method, when no tips available returns an empty list"""
        return [_("The fewer hits you need to get the ball in the hole, the more points you get.")]
        
    def get_helptype(self):
        """Mandatory method, you must set an type"""
        # Possible types are: Memory, Math, Puzzle, Keyboardtraining, Mousetraining
        #                     Language, Alphabet, Fun, Miscellaneous
        return _("Fun/Miscellaneous")
        
    
    def get_helplevels(self):
        """Mandatory method, must return a string with the number of levels
        in the follwing format:
        _("This level has %s levels") % number-of-levels"""
        return _("This activity has %s levels") % 3
    
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
        # Your top blit position, this depends on the menubar position 
        if self.blit_pos[1] == 0:
            y = 10
        else:
            y = 110
        if level == 4:
            return False
        self.level = level# make it part of this class so we can use it to test
        # in which level we are. See def _made_hole
        self.db_mapper = dbmapper
        self.points = 0
        self.tries = 0
        self.n_balls = 5
        self.maxpoints = 0
        # Tell the core to display a exercises/done counter
        Misc.execounter = self.SPG.tellcore_display_execounter(self.n_balls,text=_("Balls"))
        
        self.next_exercise()
        return True
    
    def start(self):
        """Mandatory method."""
        Hole.img = utils.load_image(os.path.join(self.my_datadir,'hole.png'))
        Hole.size = (Hole.img.get_width(), Hole.img.get_height())
        
        self.backgr_wohole = utils.load_image(os.path.join(self.my_datadir,'backgr.png'))
        Snd.throw = os.path.join(self.my_datadir,'sndt.wav')
        Snd.hurra = os.path.join(self.my_datadir,'sndh.wav')
        Snd.great = os.path.join(self.my_datadir,'sndh.wav')
    
    def post_next_level(self):
        """Mandatory method.
        This is called once by the core after 'next_level' *and* after the 321 count.
        You should place stuff in here that run in a seperate thread like sound play."""
        pass 
        
    def get_score(self,timespend):
        """Mandatory method.
        @timespend is the time spend inside the level as it's calculated
        by the core.
        returns the score value for the past level.
        return None if no score value is used"""
        m,s = timespend.split(':')
        seconds = int(m)*60 + int(s)
        score = max(1,10 *(float(self.n_balls)/self.tries)-(seconds/100.0))
        
        self.logger.debug('total time %s' % seconds)
        self.logger.debug('score %s' % score)
        # As this method is called by the core when a level is finished
        # we also use it to store the counters
        self.db_mapper.insert('balls',self.n_balls)
        #self.logger.debug("balls %s" % self.n_balls)
        self.db_mapper.insert('tries',self.tries)
        #self.logger.debug("tries %s" % self.tries)
        self.db_mapper.insert('maxpoints',self.maxpoints)
        #self.logger.debug("maxpoints %s" % self.maxpoints)
        self.db_mapper.insert('points',self.points)
        #self.logger.debug("points %s " % self.points)
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
        if not self.buttonpressed:
            for event in events:
                if event.type is MOUSEBUTTONDOWN:
                    #if self.ball1 in Misc.actives.sprites():
                    if len(Misc.actives):
                        continue
                    if event.button >= 2:
                        self.logger.debug("button >=2 down")
                        if self.ball1.callback(event.pos, event.button):
                            # put stick in position to see the direction it will have
                            self.stick.prepare(event.pos, (self.ball1.posreal[0]+self.ball1.size[0]/2, self.ball1.posreal[1]+self.ball1.size[1]/2))
                            Misc.group.add(self.stick)
                            Misc.group.refresh()
                    else:
                        self.logger.debug("button 1 down")
                        if self.ball1.callback(event.pos, event.button):
                            # there will be a kick. Begin counting the time buttonmouse is pressed.
                            self.buttonpressed = 1
                            self.timepressed = 0
                            self.stick.prepare(event.pos, (self.ball1.posreal[0]+self.ball1.size[0]/2, self.ball1.posreal[1]+self.ball1.size[1]/2))
                            Misc.group.add(self.stick)
                            Misc.group.refresh()
                if event.type is KEYDOWN and (event.key == 113):
                    # My mind is going down...
                    #self.stop = 1
                    self.start(self.level,None)
                if event.type is MOUSEBUTTONUP:
                    Misc.group.remove(self.stick)
                    Misc.group.refresh()
        else:
            if len(events):
                for event in events:
                    if event.type is MOUSEBUTTONUP and event.button == 1:
                        # stick was released. It's time to roll.
                        self.stick.remove(Misc.group)
                        self.buttonpressed = 0
                        #Misc.group.refresh()
                        Misc.actives.add(self.ball1)
                        strength = self.timepressed / 2
                        self.ball1.direc = (self.ball1.direc[0] * strength, self.ball1.direc[1] * strength)
                        self.throws += 1
                        utils.load_music(Snd.throw).play()
            else:
                # strength is going up
                if self.timepressed < self.stick.maxstrength:
                    self.timepressed += 1
                    self.stick.grow(self.timepressed)
        if Misc.actives.sprites():
            #pygame.time.wait(10)
            self.movethings()
            # Call refresh with a event to let it call callback and update methods.
            # See the game fallingletters for a simple implementation of this in action.
            v = Misc.group.refresh(pygame.event.Event(USEREVENT))# The ball returns 1 when it goes into the hole 
            # the ball also removes it self from the grou. see the ball class

            # check the return val from the on_update method
            # for the format see the reference and the ball class
            if v:
                #print "return val from inside refresh:", v # just as info to see how the return val looks like :-)
                if v[0][1][1] == 1:
                    self._made_hole(v[0][1][0])
        return 
        
    def next_exercise(self):
        self.logger.debug("next_exercise called")
        self.throws = 0
        self.buttonpressed = 0
        Misc.actives.empty()
        Misc.group.empty()
        Misc.score = 0# see def loop and further
        objects = []
        self.screen.blit(self.backgr_wohole, (0,self.blit_pos[1])) # this is needed here, as CP calls the start (and not setup) proc. on a level change.
        x,y = (random.randrange(8,791-Hole.size[0],1),random.randrange(self.blit_pos[1],600 - self.blit_pos[1] - Hole.size[1],1))
        Hole.pos = (x,y)
        objects.append([Hole.pos,Hole.size])
        self.backgr.blit(self.backgr_wohole, (0,self.blit_pos[1]))
        self.screen.blit(self.backgr_wohole, (0,self.blit_pos[1]))
        self.screen.blit(Hole.img, Hole.pos)
        self.backgr.blit(Hole.img, Hole.pos)
        #self.screen.blit(self.backgr,(0,0))
        pygame.display.update()
        img = utils.load_image(os.path.join(self.my_datadir,'ball1.png'))
        imgsize = (img.get_width(), img.get_height())
        x,y = (random.randrange(8,791-imgsize[0],1),\
               random.randrange(self.blit_pos[1],491 - self.blit_pos[1] -imgsize[1],1))
        while self.tooclose((x,y,imgsize), objects):
            x,y = (random.randrange(8,791-imgsize[0],1),\
                   random.randrange(self.blit_pos[1],491- self.blit_pos[1] -imgsize[1],1))
        objects.append([(x,y),imgsize])
        self.ball1 = Ball(img, (x,y),'blue')# the extra argument can be 'blue' or 'red'. this way we know what kind of ball it is.
        # use this if you just want to display a sprite
        self.ball1.display_sprite()
        Misc.actives.add(self.ball1)
        Misc.group.add(self.ball1)
        # Now it has level 2 repeated in level 3. Before it was (if level == 1), (if level > 1), (if level > 2).
        if self.level == 1:
            # set points to earn: just d(b1,h)/8 in this case
            self.pointstoadd = ( sqrt((self.ball1.posint[0] - Hole.pos[0])**2\
                            + (self.ball1.posint[1] - Hole.pos[1])**2) ) / 8
        if self.level == 2:
            img = utils.load_image(os.path.join(self.my_datadir,'ball2.png'))
            imgsize = (img.get_width(), img.get_height())
            x,y = (random.randrange(8,791-imgsize[0],1),random.randrange(8,491-imgsize[1],1))
            while self.tooclose((x,y,imgsize), objects):
                x,y = (random.randrange(8,791-imgsize[0],1),random.randrange(8,491-imgsize[1],1))
            self.ball2 = Ball(img, (x,y),'red')
            self.ball2.display_sprite()
            Misc.actives.add(self.ball2)
            Misc.group.add(self.ball2)
            # set points to earn: 0.2 * d(b2,h) + (2.4 + cos angle) * d(b2,b1) / 8
            # where b1,b2 = ball1,ball2, h = hole, d = distance, angle = angle at b2.
            diff1 = (Hole.pos[0] - self.ball2.posint[0], Hole.pos[1] - self.ball2.posint[1])
            diff2 = (self.ball1.posint[0] - self.ball2.posint[0], self.ball1.posint[1] - self.ball2.posint[1])
            diff1norm = sqrt(diff1[0]**2+diff1[1]**2)
            diff2norm = sqrt(diff2[0]**2+diff2[1]**2)
            self.pointstoadd = 0.2 * diff1norm + (diff1[0]*diff2[0]+diff1[1]*diff2[1]) / (6 * diff1norm) + diff2norm * 0.3
        if self.level == 3:
            img = utils.load_image(os.path.join(self.my_datadir,'ball2.png'))
            imgsize = (img.get_width(), img.get_height())
            x,y = (random.randrange(8,791-imgsize[0],1),random.randrange(8,491-imgsize[1],1))
            while self.tooclose((x,y,imgsize), objects):
                x,y = (random.randrange(8,791-imgsize[0],1),random.randrange(8,491-imgsize[1],1))
            objects.append([(x,y),imgsize])
            self.ball2 = Ball(img, (x,y),'red')
            x,y = (random.randrange(8,791-imgsize[0],1),random.randrange(8,491-imgsize[1],1))
            while self.tooclose((x,y,imgsize), objects):
                x,y = (random.randrange(8,791-imgsize[0],1),random.randrange(8,491-imgsize[1],1))
            self.ball3 = Ball(img, (x,y),'red')
            self.ball2.display_sprite()
            self.ball3.display_sprite()
            Misc.actives.add((self.ball2,self.ball3))
            Misc.group.add((self.ball2,self.ball3))
            #points to earn: as in level 2  +  0.2 * d(b3,h) + (2.4 + cos angle) * d(b3,b1) / 8
            diff1 = (Hole.pos[0] - self.ball2.posint[0], Hole.pos[1] - self.ball2.posint[1])
            diff2 = (self.ball1.posint[0] - self.ball2.posint[0], self.ball1.posint[1] - self.ball2.posint[1])
            diff1norm = sqrt(diff1[0]**2+diff1[1]**2)
            diff2norm = sqrt(diff2[0]**2+diff2[1]**2)
            self.pointstoadd = 0.2 * diff1norm + (diff1[0]*diff2[0]+diff1[1]*diff2[1]) / (8 * diff1norm) + diff2norm * 0.3
            diff1 = (Hole.pos[0] - self.ball3.posint[0], Hole.pos[1] - self.ball3.posint[1])
            diff2 = (self.ball1.posint[0] - self.ball3.posint[0], self.ball1.posint[1] - self.ball3.posint[1])
            diff1norm = sqrt(diff1[0]**2+diff1[1]**2)
            diff2norm = sqrt(diff2[0]**2+diff2[1]**2)
            self.pointstoadd += 0.2 * diff1norm + (diff1[0]*diff2[0]+diff1[1]*diff2[1]) / (8 * diff1norm) + diff2norm * 0.3
        img = utils.load_image(os.path.join(self.my_datadir,'stick.png'))
        self.stick = Stick(img, (200,120))

    def tooclose(self, ob1, obs):
        for i in obs:
            if (((ob1[0]-i[0][0])**2+(ob1[1]-i[0][1])**2) < (ob1[2][0]+i[1][0])**2/4) :
                return 1
        return 0
        
    def movethings(self):
        """ moves everything. Deletes from actives if stop. """
        for o in Misc.actives.sprites():
            keepit = o.moveit()
            # remove it from actives if it has stopped.
            if not keepit:
                Misc.actives.remove(o)
        # check all possible collisions
        for n1 in range(len(Misc.group.sprites())):
            o1 = Misc.group.sprites()[n1]
            for o2 in Misc.group.sprites()[n1:]:
                if o1 != o2:
                    newdirs = o1.checkcollision(o2)
                    if newdirs[0]:
                        if newdirs[1] == 0 and o1 in Misc.actives.sprites():
                            Misc.actives.remove(o1)
                        elif newdirs[1] and o1 not in Misc.actives.sprites():
                            Misc.actives.add(o1)
                        if newdirs[2] and o2 not in Misc.actives.sprites():
                            Misc.actives.add(o2)
                        elif newdirs[2] == 0 and o2 in Misc.actives.sprites():
                            Misc.actives.remove(o2)
    
    def _made_hole(self,obj):
        # Keeps also track of the score
        # This replaces _level_1,_level_2 and _level_3
        if self.level > 1 and obj == 'blue':
            return# we pot a red blue ball in the levels > 1
        obj.remove(Misc.group)# remove the ball from the group
        obj.remove_sprite()
        utils.load_music(Snd.hurra).play()
        if (len(Misc.group) == (self.level > 1)): # true if there are no balls in level 1 or there's in levels 2 and 3
            s = int(self.pointstoadd / self.throws)
            ## Consider this a placeholder, it doesn't work as it should
            #self.cpg.scorething(s)# Update the score display
            self.maxpoints += self.pointstoadd
            self.points += s
            self.tries += 1
            txt,sz = utils.text2surf(str(self.points)+'  '+_("points"), 48, (8, 0, 120), bold=True)
            self.screen.blit(txt, (200,200))
            pygame.display.update()
            pygame.time.wait(2000)
            # update the counter in the menubar
            Misc.execounter.increase_counter()
            if self.tries == self.n_balls:
                self.SPG.tellcore_level_end(store_db=True)#signal to childsplay that this level is ended. See return val of def loop
                if self.level == 3:
                    self.stop = 1
                    Misc.score = self.points
                    self.screen.blit(self.backgr, (0,0))
                    MovingSign(_("You won!!"), 80, (100,100), (100,300), 1, (8,0,120), self.screen, self.backgr, 0)
                    txt,sz = utils.text2surf(str(self.points)+'  '+_("points"), 48, (8, 0, 120), bold=True)
                    self.screen.blit(txt, (200,200))
                    pygame.display.update()
                    for i in range(0,3):
                        utils.load_music(Snd.hurra).play()
                        pygame.time.wait(1000)
            else:
                self.next_exercise()
