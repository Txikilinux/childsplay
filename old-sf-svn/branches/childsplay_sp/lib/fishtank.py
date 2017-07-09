# -*- coding: utf-8 -*-

# Copyright (c) 2006 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
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
# replace activity_template in "schoolsplay.activity_template" with the name
# of the activity. Example: activity is called memory -> 
# logging.getLogger("schoolsplay.memory")
# In your Activity class -> 
# self.logger =  logging.getLogger("schoolsplay.memory.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("schoolsplay.fishtank")

# standard modules you probably need
import os,sys
import glob,random
import pygame
from pygame.constants import *

import childsplay_sp.utils as utils
import childsplay_sp.Timer as Timer
from childsplay_sp.SPConstants import *
import childsplay_sp.SPSpriteUtils as SPSpriteUtils

# containers that can be used globally to store stuff
class Misc:
    # fish_clear_total is used as a counter.
    # Fish objects add the number of update loops they do before the user clicks
    # them. In the end we have a number which represents the number of update loops
    # it took to clear all the fish.
    # The lower this number is the quicker the user was in removing the fish.
    # By putting it into a class namespace all the objects can use it.
    fish_clear_total = 0

class Bubble(SPSpriteUtils.SPSprite):
    def __init__(self,image,snd):
        """Bubble that starts at the bottom and floats to the surface.
        It also plays a 'blub' sound"""
        self.image = image
        #SPSpriteUtils.SPSprite will set self.rect
        SPSpriteUtils.SPSprite.__init__(self,self.image)
        # we don't care about the iterator returnt as we let SPSprite call the 
        # SPSprite.on_update method. We do set the 'dokill' argument as we don't
        # want to reuse the sprite.
        # (see API docs for more info about the SPSprite.on_update method)
        start = (random.randint(10,790),500-self.image.get_height())
        end = (start[0],-50) # move off the screen
        self.set_movement(start,end,step=6,retval=0,loop=1,dokill=1)
        snd.play()

class Fish(SPSpriteUtils.SPSprite):
    def __init__(self,imagepair):
        """@x and @y are the start coords. 
        The fish always starts of screen either right or left.
        @step is the amount of pixels we move
        @delay is used as a counter to delay the movement,
        when it's zero the sprite moveit method is called.
        """
        self.logger = logging.getLogger("schoolsplay.fishtank.Fish")
        # we will use the two images to create a simple animation in on_update
        self.image_0,self.image_1 = imagepair
        self.image = self.image_0
        self.org_images = (self.image_0.convert(),self.image_1.convert())
        SPSpriteUtils.SPSprite.__init__(self,self.image)
        # rects are the same for both images so we don't need to swap rects
        self.rect = self.image.get_rect()
                    
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
            #status = self.moveit()# we move accoording to the movement set in the constructor
            status = self.moveit.next()
            if status != -1:# reached the end of the movement
                self.remove_sprite()
                # placeholder: no score

    def callback(self,*args):
        """ This is called when the sprite class update or refresh method is called
        and the mouse event occurs in this sprite.
        Remember that you must 'connect' a callback first with a call to
        self.connect_callback, see the SPSprite reference for info on possibilities
        of connecting callbacks .
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

class Activity:
    """  Base class mandatory for any SP activty.
    The activity is started by instancing this class by the core.
    This class must at least provide the following methods.
    start (self) called by the core before calling loop.
    next_level (self,level) called by the core when the user changes levels.
    loop (self,events) called 30 times a second by the core and should be your 
                      main eventloop.
    helptitle (self) must return the title of the game can be localized.
    help (self) must return a list of strings describing the activty.
    name (self) must provide the activty name in english, not localized in lowercase.
  """

    def __init__(self,SPGoodies):
        """SPGoodies is a class object that SP sets up and will contain references
        to objects, callback methods and observers
        """
        self.logger =  logging.getLogger("schoolsplay.fishtank.Activity")
        self.logger.info("Activity started")
        self.SPG = SPGoodies
        self.screen = self.SPG.get_screen()
        self.backgr = self.SPG.get_background()
        backimage = random.choice(['back0.jpg','back1.jpg'])
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','FishtankData')
        self.coral_surf = utils.load_image(os.path.join(self.my_datadir,'backgrounds',backimage))
        self.bubimg = utils.load_image(os.path.join(self.my_datadir,'backgrounds','blub0.png'),1,1)
        self.bubsnd = utils.load_sound(os.path.join(self.my_datadir,'backgrounds','blub0.wav'))
        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special CPGroup
        self.actives = SPSpriteUtils.SPInit(self.screen,self.backgr)
        # we want only one sprite react to an event in case there are multiple 
        # sprites in one rect.
        self.actives.set_onematch(True)
        self.timer = None # will hold the timer object
        
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
        _("In the last level the fish needs to be clicked two times while they try to escape."),
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
        _("This level has %s levels" % number-of-levels)"""
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
            
    def start(self):
        """Load images and turn them into fish objects.
        """        
        # here we setup our list with images we use to construct sprites through out the levels.
        rawimagelist = []
        filelist = glob.glob(os.path.join(self.my_datadir,'*.png'))
        filelist.sort()
        for i in range(0,len(filelist),2):
            rawimagelist.append((filelist[i],filelist[i+1]))
        self.imagelist = []
        try:
            for imgfile in rawimagelist:
                self.imagelist.append((utils.load_image(imgfile[0],1),\
                                   utils.load_image(imgfile[1],1)))
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
        self.level_data = [(10,-70,8,4,4),(20,0,8,4,4),(20,0,8,4,4),(20,870,4,6,4),\
                            (20,0,4,8,4),(20,0,4,6,4)]
        
    def get_score(self,timespend):
        """Mandatory method.
        @timespend is the time spend inside the level as it's calculated
        by the core.
        returns the score value for the past level.
        return None if no score value is used"""
        #m,s = timespend.split(':')
        #seconds = int(m)*60 + int(s)  
        c = 0.7
        score = 10.0 / (max (float(Misc.fish_clear_total/100)/float(self.totalfish), 1.0)) ** c
        return score
        
    def next_level(self,level,db_mapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        if level > 6: return False
        
        # make sure we don't have a timer running
        self.stop_timer()
        # db_mapper is a Python class object that provides easy access to the 
        # dbase.
        self.db_mapper = db_mapper
        # make sure we don't have fish left in the actives group.
        self.actives.empty()
        # remember that SPC sets a clip in relation to the theme used
        self.screen.blit(self.coral_surf,(0,0))
        pygame.display.update()
        self.backgr.blit(self.coral_surf,(0,0))
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
            s1, s2 = item[0].convert(),item[1].convert()
            # position and position are set when the level is started
            fishobjects.append(Fish((s1,s2)))
        
        # setup the objects and put them in a seperate list
        # we don't destroy them so we can use them in any level.
        self.livefish = []
        for obj in fishobjects:
            y = random.randint(10,420)
            if startx == 0:
                x = random.choice((-70,870))
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
                react = 1
            obj.start(x,y,step,delay,react)
            self.livefish.append(obj)
        
        # we need total fish for score calculation.
        self.totalfish = len(self.livefish)
        # we store the number of fish this level will have.
        self.db_mapper.insert('fish',self.totalfish)
        # special threaded timer object for the fish
        self.timer_f = Timer.Timer(self.timersleep,self.release_fish,lock=self.SPG.get_thread_lock())
        self.timer_f.start()
        return True
    
    def post_next_level(self):
        """Mandatory method.
        This is called by the core after 'next_level' *and* after the 321 count.
        You should place stuff in here that run in a seperate thread like sound play."""
        # and one timer for the bubbles
        # placed here because it's another thread
        self.timer_b = Timer.Timer(self.timersleep+1,self.release_bubble,lock=self.SPG.get_thread_lock())
        self.timer_b.start()
    
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
        self.actives.add(Bubble(self.bubimg,self.bubsnd))
        return 1# let the timer run   
        
    def loop(self,events):
        """Mandatory method
        """
        myevent = None
        if not self.livefish and not self.actives.sprites():
            # no more sprites left so the level is done.
            self.db_mapper.insert('clearfish',Misc.fish_clear_total)
            # we call the SPGoodies observer to notify the core the level
            # is ended and we want to store the collected data
            self.SPG.tellcore_level_end(store_db=True)
        for event in events:
            if event.type is MOUSEBUTTONDOWN:
                # no need to query all sprites with all the events
                # we only pass it an event if it's an event were intrested in.
                myevent = event
        # move all fish
        self.actives.refresh(myevent)
        return 
        
