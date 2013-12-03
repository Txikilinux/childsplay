# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zytkiewicz stas.zytkiewicz@schoolsplay.org
#
#           fishtank.py
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
# self.logger =  logging.getLogger("childsplay.fishtank.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("childsplay.fishtank")

# standard modules you probably need
import os,sys
import glob,random
import pygame
from pygame.constants import *

import utils
import Timer
from SPConstants import *
import SPSpriteUtils

# containers that can be used globally to store stuff
class Misc:
    # fish_clear_total is used as a counter.
    # Fish objects add the number of update loops they do before the user clicks
    # them. In the end we have a number which represents the number of update loops
    # it took to clear all the fish.
    # The lower this number is the quicker the user was in removing the fish.
    # By putting it into a class namespace all the objects can use it.
    fish_clear_total = 0
    # used by the scoredisplay
    score = 0

class Bubble(SPSpriteUtils.SPSprite):
    def __init__(self,image,snd, top):
        """Bubble that starts at the bottom and floats to the surface.
        It also plays a 'blub' sound"""
        self.image = image
        #SPSpriteUtils.SPSprite will set self.rect
        SPSpriteUtils.SPSprite.__init__(self,self.image)
        # we don't care about the iterator returnt as we let SPSprite call the 
        # SPSprite.on_update method. We do set the 'dokill' argument as we don't
        # want to reuse the sprite.
        # (see API docs for more info about the SPSprite.on_update method)
        start = (random.randint(50,750),500-self.image.get_height())
        end = (start[0],top)
        self.set_movement(start,end,step=6,retval=0,loop=1,dokill=1)
        snd.play()

class Fish(SPSpriteUtils.SPSprite):
    def __init__(self,imagepair, obs,  parent):
        """@x and @y are the start coords. 
        The fish always starts of screen either right or left.
        @step is the amount of pixels we move
        @delay is used as a counter to delay the movement,
        when it's zero the sprite moveit method is called.
        """
        self.logger = logging.getLogger("childsplay.fishtank.Fish")
        # we will use the two images to create a simple animation in on_update
        self.image_0,self.image_1 = imagepair
        self.image = self.image_0
        self.org_images = (self.image_0.convert_alpha(),self.image_1.convert_alpha())
        SPSpriteUtils.SPSprite.__init__(self,self.image)
        # rects are the same for both images so we don't need to swap rects
        self.rect = self.image.get_rect()
        self.obs = obs
        self.parent = parent
        
    def start(self,x,y,step,delay,react):
        """Set the sprite and start movement"""
        self.update_counter = 0
        self.delay = delay
        self.start = (x,y)# we use this as an end pos in level 6, see callback
        self.step = step
        self.delay = delay
        self.wait = delay
        self.react = react
        # determine the end position (we move horizontale so we don't care about y)
        if x < 1:
            # we start from the left
            endx = 800
        else:
            endx = 0 - self.image.get_width()
        end = (endx,y)# move of the screen
        self.end = end
        loop = 1
        self.moveit = self.set_movement(self.start,end,step,0,loop)# setup the movement of this object
        self.connect_callback(self.callback, event_type=MOUSEBUTTONDOWN)
    
    def mirror_image(self):
        self.image = pygame.transform.flip(self.image,1,0)
        self.image_0 = pygame.transform.flip(self.image_0,1,0)
        self.image_1 = pygame.transform.flip(self.image_1,1,0)

    def on_update(self,*args):
        """This is called by group.refresh method"""
        self.update_counter += 1
        if self.wait:# extra delay, otherwise they move to fast 
            self.wait -= 1
            return
        else:
            self.wait = self.delay
            if self.image == self.image_1:
                self.image = self.image_0
            else:
                self.image = self.image_1
            status = self.moveit.next()
            if status != -1:# reached the end of the movement
                if self.parent.are_we_in_aquarium_mode():
                    # special behaviour, fish turns each time it reaches the end
                    self.mirror_image()
                    self.stop_movement(now=1)
                    start = (self.end[0], self.end[1])
                    end = (self.start[0],self.start[1])
                    self.start = (start[0], start[1])
                    self.end = (end[0],end[1])
                    self.wait = self.delay
                    step = self.step
                    self.moveit = self.set_movement(start,end,step,0)
                else:
                    self.remove_sprite()
                # placeholder: no score

    def callback(self,*args):
        """ This is called when the sprite class update or refresh method is called
        and the mouse event occurs in this sprite.
        Remember that you must 'connect' a callback first with a call to
        self.connect_callback, see the SPSprite reference for info on possibilities
        of connecting callbacks.
        """
        # enable logger to see the args
        #self.logger.debug("callback called with %s, %s" % (args[0],args[1]))
        # when the user hits us this method is called.
        if self.react == 1:
            # special behaviour, fish turns and tries to get away
            self.mirror_image()
            self.stop_movement(now=1)
            start = self.rect.topleft
            end = self.start
            step = self.step*2
            self.moveit = self.set_movement(start,end,step,0,dokill=1)
            self.react += 1
        else:
            self.remove_sprite()# it will not destroyed
            # You must stop the movement because moveit is a generator
            self.stop_movement(now=1)
            # add the number to the global counter
            Misc.fish_clear_total += self.update_counter
            return self.obs((1000 - self.rect.topleft[0]) / 100)

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
        self.logger =  logging.getLogger("childsplay.fishtank.Activity")
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
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','FishtankData')
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.CPdatadir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        # Location of the alphabet sounds dir
        self.absdir = self.SPG.get_absdir_path()# alphabet sounds dir
        self.rchash = utils.read_rcfile(os.path.join(self.my_datadir, 'fishtank.rc'))
        self.rchash['theme'] = self.theme
        
        self.sounddir = os.path.join(self.my_datadir,'sounds')
        self.bubimg = utils.load_image(os.path.join(self.my_datadir,'backgrounds',self.theme,'blub0.png'))
        self.bubsnd = utils.load_sound(os.path.join(self.sounddir,'blub0.wav'))
        self.splashsnd = utils.load_sound(os.path.join(self.sounddir,'poolsplash.wav'))
        self.WeAreAquarium = False
        self.aquarium_counter = 0
        
        self.aquarium_music_list = glob.glob(os.path.join(self.sounddir,'*.ogg'))
        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special CPGroup
        self.actives = SPSpriteUtils.SPInit(self.screen,self.backgr)
        self.actives.set_onematch(True)
            
    def clear_screen(self):
        self.screen.set_clip()
        self.screen.blit(self.orgscreen,self.blit_pos)
        self.backgr.blit(self.orgscreen,self.blit_pos)
        pygame.display.update()

    def are_we_in_aquarium_mode(self):
        return self.WeAreAquarium

    def get_moviepath(self):
        movie = os.path.join(self.my_datadir,'help.avi')
        return movie

    def refresh_sprites(self):
        """Mandatory method, called by the core when the screen is used for blitting
        and the possibility exists that your sprites are affected by it."""
        self.actives.redraw()

    def get_helptitle(self):
        """Mandatory method"""
        return _("Fishtank")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "fishtank"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),
        _("Try to remove the fish by clicking on them with the mouse."),
        " "]
        return text 
    
    def get_helptip(self):
        """Mandatory method, when no tips available returns an empty list"""
        return []
        
    def get_helptype(self):
        """Mandatory method, you must set an type"""
        # Possible types are: Memory, Math, Puzzle, Keyboardtraining, Mousetraining
        #                     Language, Alphabet, Fun, Miscellaneous
        return _("Fun/Mousetraining")
    
    
    def get_helplevels(self):
        """Mandatory method, must return a string with the number of levels
        in the follwing format:
        _("This level has %s levels") % number-of-levels"""
        return _("This activity has %s levels") % 6

    def stop_timer(self):
        """You *must* provide a method to stop timers if you use them.
        The SPC will call this just in case and cache the exception in case 
        there's no 'stop_timer' method""" 
        try:
            self.timer_f.stop()
        except:
            pass
        try:
            self.timer_b.stop()
        except:
            pass
        try:
            self.aquariumsound.stop()
        except:
            pass
        self.clear_screen()

    def score_observer(self, score):
        self.aquarium_counter = 0
        self.WeAreAquarium = False
        self.aquarium_text.erase_sprite()
        self.actives.remove(self.aquarium_text)
#        if self.aquariumsound:
#            self.aquariumsound.stop()

        snd = utils.load_sound(os.path.join(self.my_datadir,'sounds', 'poolsplash.wav')) 
        snd.play()
        if score < 0:
            score = 1
        self.scoredisplay.increase_score(score + self.level*6)
    
    def start(self):
        """Mandatory method."""
        # here we setup our list with images we use to construct sprites through out the levels.
        rawimagelist = []
        filelist = glob.glob(os.path.join(self.my_datadir,'*.png'))
        filelist.sort()
        for i in range(0,len(filelist),2):
            rawimagelist.append((filelist[i],filelist[i+1]))
        self.imagelist = []
        try:
            for imgfile in rawimagelist:
                self.imagelist.append((utils.load_image(imgfile[0]),\
                                   utils.load_image(imgfile[1])))
        except Exception,info:
            self.logger.exception("Error loading images")
            raise utils.MyError()
        self.logger.debug("constructed %s groups of images" % len(self.imagelist))
        # get some 'blub' sounds
        self.sounds = []
        filelist = glob.glob(os.path.join(self.my_datadir,'*.wav'))
        for path in filelist:
            self.sounds.append(utils.load_sound(path))
        # level_data: one tuple per level six in total.
        # tuple values are: number of fish,x coord,delay,step,timersleep
        # x coord of 0 means both left and right
        # Third level adjust the speed of some of the fish
        # from the third level the speeds are randomized.
        self.level_data = [(20,-90,8,4,4),(20,0,8,4,4),(20,0,8,4,4),(20,890,4,6,4),\
                            (20,0,4,8,4),(20,0,4,6,4)]

        surf = utils.char2surf("Aquarium mode", 14, fcol=GREEN)
        self.aquarium_text = SPSpriteUtils.MySprite(surf, pos=(30, 580))
        self.aquarium_text.set_use_current_background()
        
    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        # Your top blit position, this depends on the menubar position 
        if self.blit_pos[1] == 0:
            self.ty = 10
        else:
            self.ty = 110
        if level > 6: return False
        self.level = level
        # make sure we don't have a timer running
        self.stop_timer()
        # db_mapper is a Python class object that provides easy access to the 
        # dbase.
        self.db_mapper = dbmapper
        # make sure we don't have fish left in the actives group.
        self.actives.empty()
        self.WeAreAquarium = False
        self.aquarium_counter = 0
        #self.aquariumsound = False
        self.aquariumsound = utils.load_music(random.choice(self.aquarium_music_list))
        #detrmine which background pic we will use:
        backimage = os.path.join(self.my_datadir, 'backgrounds', \
                                 self.theme,'%s.jpg' % level)
        if not os.path.exists(backimage):
            backimage = os.path.join(self.my_datadir, 'backgrounds', \
                                 'childsplay','%s.jpg' % level)
        # remember that SPC sets a clip in relation to the theme used
        self.coral_surf = utils.load_image(backimage)
        self.screen.blit(self.coral_surf,(0,self.ty-10))
        pygame.display.update()
        self.backgr.blit(self.coral_surf,(0,self.ty-10))
        random.shuffle(self.imagelist)
        # get values for the fish objects
        data = self.level_data[level-1]
        startx = data[1]
        delay = data[2]# lower = faster
        step = data[3] # higher = faster
        self.timersleep = data[4] # seconds between fish start
        react = 0
        self.logger.debug("setup fish with: x=%s,delay=%s,step=%s,timer=%s" % \
                                                (startx,delay,step,self.timersleep))
        # setup the fish objects, in two steps
        fishobjects = []
        for item in self.imagelist[:data[0]]:
            # we use copies, this way we can reuse the image list.
            s1, s2 = item[0].convert_alpha(),item[1].convert_alpha()
            # position and position are set when the level is started
            fishobjects.append(Fish((s1,s2), self.score_observer, self))
        
        # setup the objects and put them in a seperate list
        # we don't destroy them so we can use them in any level.
        self.livefish = []
        for obj in fishobjects:
            y = random.randint(self.ty,410+self.ty)
            if startx == 0:
                x = random.choice((-90,890))
            else:
                x = startx
            if x > 0:
                # we move from right to left and we must mirror the original image
                obj.mirror_image()
            if level >= 3:# third level, we adjust some of the speeds
                d = data[2]
                delay = random.choice((d,d,d//2))
                s = data[3]
                step = random.choice((s,s,s*2))
            if level == 6:
                d = data[2]
                delay = d//3
                s = data[3]
                step = s*2
            obj.start(x,y,step,delay,react)
            self.livefish.append(obj)
        
        # we need total fish for score calculation.
        self.totalfish = len(self.livefish)
        # we store the number of fish this level will have.
        self.db_mapper.insert('fish',self.totalfish)
        
        self.aquariumsound.play(-1)
        return True
    
    def pre_level(self, level):
        pass
    
    def post_next_level(self):
        """Mandatory method.
        This is called once by the core after 'next_level' *and* after the 321 count.
        You should place stuff in here that run in a seperate thread like sound play."""
        # placed here because it's another thread
        self.timer_f = Timer.Timer(self.timersleep,self.release_fish,\
                                   lock=self.SPG.get_thread_lock(), startnow=True)
        self.timer_f.start()
        self.timer_b = Timer.Timer(self.timersleep+1,self.release_bubble,\
                                   lock=self.SPG.get_thread_lock())
        self.timer_b.start() 
        self.screen.set_clip((0, 0, 800, self.ty+490))
    
    def release_fish(self):
        """Called by the timer, and responsible for the swimming of the fish.
        This will get a fish from the livefish list and place it in
        the Sprite actives group, and thereby it will be blitted on the screen."""
        try:
            obj = self.livefish.pop()
        except IndexError:
            return 0# stops the timer
        self.actives.add(obj)
        return 1# let the timer run    

    def release_bubble(self):
        # we don't keep a reference so it will be destroyed by the Python
        # garbage collector when 'kill' is called after the movement is ended
        self.actives.add(Bubble(self.bubimg,self.bubsnd, self.ty))
        return 1# let the timer run   
    
    def get_score(self,timespend):
        """Mandatory method.
        @timespend is the time spend inside the level as it's calculated
        by the core.
        returns the score value for the past level.
        return None if no score value is used"""
        #m,s = timespend.split(':')
        #seconds = int(m)*60 + int(s)  
#        c = 0.7
#        score = 10.0 / (max (float(Misc.fish_clear_total/100)/float(self.totalfish), 1.0)) ** c
        score = 8 # fishtank is not really suitable for reall scores, so now we make sure we the core does a levelup
        return score

    def loop(self,events):
        """Mandatory method.
        This is the main eventloop called by the core 30 times a minute."""
        myevent = None
        if self.aquarium_counter > 300 and not self.WeAreAquarium and\
                                     len(self.actives.sprites()):
            self.WeAreAquarium = True
            self.actives.add(self.aquarium_text)
            self.aquarium_text.display_sprite()
#            self.aquariumsound = utils.load_music(random.choice(self.aquarium_music_list))
#            self.aquariumsound.play(-1)
        self.aquarium_counter += 1
        if not self.livefish and not self.actives.sprites():
            # no more sprites left so the level is done.
            self.db_mapper.insert('clearfish',Misc.fish_clear_total)
            # we call the SPGoodies observer to notify the core the level
            # is ended and we want to store the collected data
            levelup = True
            self.SPG.tellcore_level_end(store_db=True, \
                                        level=min(6, self.level + levelup), \
                                            levelup=levelup, no_question=True)
        for event in events:
            if event.type is MOUSEBUTTONDOWN:
                self.aquarium_counter = 0
                self.WeAreAquarium = False
                self.aquarium_text.erase_sprite()
                self.actives.remove(self.aquarium_text)
#                if self.aquariumsound:
#                    self.aquariumsound.stop()
                # no need to query all sprites with all the events
                # we only pass it an event if it's an event were intrested in.
                myevent = event
        # move all fish
        self.actives.refresh(myevent)
        return 
        
