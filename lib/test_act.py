# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zytkiewicz stas.zytkiewicz@schoolsplay.org
#
#           test_act.py
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 of the GNU General Public License
# as published by the Free Software Foundation. A copy of this license should
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
# self.logger =  logging.getLogger("childsplay.test_act.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("childsplay.test_act")

# standard modules you probably need
import os
import sys
print sys.path
# Now python finds the pygame 1.9 package first.
# It's ignored when there's no such path
import pygame
module_logger.warning("Using pygame version %s" % pygame.version.ver)
import pygame.camera
from pygame.constants import *
from pygame.locals import *

import mpylayer
import time
from datetime import datetime
import utils
from SPConstants import *
import SPSpriteUtils
import SPWidgets


class Capture(object):
    def __init__(self, screen, SPGoodies, size=(512, 384)):
        self.screen = screen
        self.SPG = SPGoodies
        self.size = size
        self.cam = '/dev/video0'
        # We set a flag to check if we have a initialised camera.
        # If the caller accesses it pygame segfaults.
        self.WeHaveCamera = False
        self.blit_pos = (0, 0)

    def __del__(self):
        # This is called when the object is garbage collected by the
        # Python VM. This way we make sure the camera is stopped.
        # We have a lot of problems with video in pygame so I assume
        # that manually stopping the camera is a good thing.
        # But you should never depend on __del__ as its not known when
        # it's actual garbage collected. It's only to make sure it is called
        # sometime. The caller class should call 'stop' when it's finished 
        # with this class.
        self.WeHaveCamera = False
        try:
            self.stop()
        except:
            pass
    
    def start(self):
        pygame.camera.init()
        self.WeHaveCamera = True
        self.camera = pygame.camera.Camera(self.cam, self.size)
        self.snapshot = pygame.surface.Surface(self.size, 0, self.screen)
        self.camera.start() 

    def get_and_flip(self):
        if not self.WeHaveCamera:
            return
        self.snapshot = self.camera.get_image(self.snapshot)
        r = self.snapshot.get_rect()
        self.blit_pos = ((800-r.w)/2 , 100 + (500-r.h)/2)
        self.screen.blit(self.snapshot, self.blit_pos)
        pygame.display.flip()

    def save_image(self,  base_dir = '/tmp'):
        capture_path = os.path.join(base_dir,'braintrainer','capture')
        if not os.path.isdir(capture_path):
            os.mkdir(capture_path)
        filename = os.path.join(capture_path, str(self.SPG.get_current_user_id()) + ".png")
        print "Filename: ", filename
        pygame.image.save(self.snapshot, filename)
        #self.screen.blit(self.snapshot, self.blit_pos)
        #pygame.time.wait(1500)
    
    def stop(self):
        self.WeHaveCamera = False
        self.camera.stop()
        
    def running(self):
        return self.WeHaveCamera        

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
        self.logger =  logging.getLogger("childsplay.test_act.Activity")
        self.logger.info("Activity started")
        self.SPG = SPGoodies        
        self.lang = self.SPG.get_localesetting()[0][:2]
        self.scoredisplay = self.SPG.get_scoredisplay()
        self.theme = self.SPG.get_theme()
        self.screen = self.SPG.get_screen()
        self.screenclip = self.SPG.get_screenclip()
        self.blit_pos = self.screenclip.left, self.screenclip.top
        self.orgscreen = pygame.Surface(self.screenclip.size) # we use this to restore the screen
        self.orgscreen.blit(self.screen, (0, 0), self.screenclip)
        self.backgr = self.SPG.get_background()
        # The location of the activities Data dir
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','Test_actData')
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.CPdatadir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        # Location of the alphabet sounds dir
        self.absdir = self.SPG.get_absdir_path()# alphabet sounds dir
        self.rchash = utils.read_rcfile(os.path.join(self.my_datadir, 'test_act.rc'))
        self.movie = os.path.join(self.my_datadir,'test1.mpg')
        self.yTop = 100
        self.logger.debug("rchash: " + str(self.rchash))
        #movie stuff
        self.moviePlaying=0
        self.moviePaused=0

        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special CPGroup
        self.actives = SPSpriteUtils.SPInit(self.screen,self.backgr)
                
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
        return _("Test_act")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "test_act"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),
        " ",
        _("Number of levels : 5"),
        " "]
        return text 
    
    def get_helptip(self):
        """Mandatory method, when no tips available returns an empty list"""
        return []
        
    def get_helptype(self):
        """Mandatory method, you must set an type"""
        # Possible types are: Memory, Math, Puzzle, Keyboardtraining, Mousetraining
        #                     Language, Alphabet, Fun, Miscellaneous
        return _("Miscellaneous")
    
    def start(self):
        """Mandatory method."""
        self.cap = Capture(self.screen, self.SPG,  size=(320, 240))
        
        b = os.path.join(self.CPdatadir, '200px_80px_blue.png')
        b_ro = os.path.join(self.CPdatadir, '200px_80px_black.png')
        self.shootbut = SPWidgets.TransImgButton(b, b_ro, (300, 500), fcol=WHITE, \
                                             text=_("Shoot"))
        self.shootbut.connect_callback(self._cbf_shoot_but, MOUSEBUTTONUP, None)
        
        mp = mpylayer.MPlayerControl()
        test = os.path.join(ACTIVITYDATADIR, 'CPData', 'VideoData','video', 'test1')
        mp.loadfile(os.path.join(test,'aquaa.mpg'))

    def get_helplevels(self):
        """Mandatory method, must return a string with the number of levels
        in the follwing format:
        _("This level has %s levels") % number-of-levels"""
        return _("This activity has %s levels") % 6
    
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
        self.cap.start()
        self.shootbut.display_sprite()
        self.actives.add(self.shootbut)
        return True
    
    def _cbf_shoot_but(self, widget, event, data):
        # we don't use the args, but it serve as an example.
        self.cap.save_image(HOMEDIR)
    
    def start_help_movie(self):
        pygame.mixer.quit()
        self.movie = os.path.join(self.my_datadir,'test1.mpg')
        self.logger.debug("starting playback of %s" % self.movie)
        self.myMovie = pygame.movie.Movie(self.movie)
        self.myMovie.set_volume(1.0)
        sz = self.myMovie.get_size()
        # set size 300x150 but this is returnt by movie.get_size (624, 352) ???
        #print ">>>>>>>",  'set size', pygame.Rect(250,self.yTop+50,350,self.yTop+200)
        self.myMovie.set_display(self.screen,(250,self.yTop+50,350,self.yTop+200))
        #print ">>>>>>>>", 'actual movie size', self.myMovie.get_size()
        self.myMovie.play()
        
    def stop_help_movie(self):
        self.myMovie.stop()
        pygame.time.wait(1000)
        del self.myMovie
                    
    def dailytraining_pre_level(self, level):
        """Mandatory method"""
        pass
        
    def dailytraining_next_level(self, level, dbmapper):
        """Mandatory method.
        This should handle the DT logic"""
        pass
        
    def get_dailytraining_result(self):
        """Mandatory method"""
        # TODO: make real result dict
        return {'score':5}
    
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
    
    def stop_timer(self):
        """You *must* provide a method to stop timers if you use them.
        The SPC will call this just in case and catch the exception in case 
        there's no 'stop_timer' method""" 
        try:
            self.timer.stop()
        except:
            pass
        try:
            self.stop_help_movie()
        except:
            pass
        try:
            self.cap.stop()
        except:
            pass

#    def startMovie(self):
#        self.moviePlaying=1
#        self.moviePaused=0
#        self.logger.debug("starting playback of %s" % self.movie)
#        movie = pygame.movie.Movie(self.movie)
#        movie.set_volume(1.0)
#        sz=movie.get_size()
#        movie.set_display(self.screen,(0,0+self.yTop,800,500))
#        movie.play()
#        return movie
#
#    def pauseMovie(self):
#        self.logger.debug("user paused movie")
#        self.myMovie.set_display(self.screen,(0,0+self.yTop,800,500))
#        self.myMovie.pause()
#        self.moviePlaying=1
#        self.moviePaused=1
#
#    def unPauseMovie(self):
#        self.logger.debug("user continued movie")
#        self.myMovie.set_display(self.screen,(0,0+self.yTop,800,500))
#        self.myMovie.pause()
#        self.moviePlaying=1
#        self.moviePaused=0

    def loop(self,events):
        """Mandatory method.
        This is the main eventloop called by the core 30 times a minute."""
        for event in events:
            if event.type in (MOUSEBUTTONUP, MOUSEMOTION):
                self.actives.update(event)
        if self.cap.running():
            self.cap.get_and_flip()
        
#                if self.moviePlaying:
#                    if self.moviePaused==1: self.unPauseMovie() 
#                    else: self.pauseMovie() 
#        return 
        
