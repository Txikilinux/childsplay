
# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zytkiewicz stas.zytkiewicz@gmail.com
#
#           photoalbum.py
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
# self.logger =  logging.getLogger("schoolsplay.photoalbum.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("schoolsplay.photoalbum")

# standard modules you probably need
import os,sys, glob

import pygame
from pygame.constants import *

import utils
from SPConstants import *
import SPSpriteUtils
import SPWidgets
from Timer import Timer

# containers that can be used globally to store stuff
class Img:
    pass
class Snd:
    pass

class Photo(SPSpriteUtils.SPSprite):
    def __init__(self, p):
        self.image = utils.load_image(p)
        SPSpriteUtils.SPSprite.__init__(self, self.image)
        pos = ((800 - self.rect.w) / 2, (600 - self.rect.h) / 2)
        self.moveto(pos)


# This activity differs from standard CP acts in the way that it runs fullscreen,
# disables the menubuttons, uses old fashion screen blitting for it's buttons
# and uses a state checking eventloop pattern.

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
        self.logger =  logging.getLogger("schoolsplay.photoalbum.Activity")
        self.logger.info("Activity started")
        self.SPG = SPGoodies
        self.theme = self.SPG.get_theme()
        self.screen = self.SPG.get_screen()
        self.screenclip = self.SPG.get_screenclip()
        self.blit_pos = self.screenclip.left, self.screenclip.top
        self.orgscreen = pygame.Surface(self.screenclip.size) # we use this to restore the screen
        self.orgscreen.blit(self.screen, (0, 0), self.screenclip)
        self.backgr = self.SPG.get_background()
        self.blacksurf = pygame.Surface((800, 600)).convert(8)
        self.blacksurf.fill(BLACK)
        # The location of the activities Data dir
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','PhotoalbumData')
        self.thumbsdir = os.path.join(self.my_datadir, 'thumbs')
        if not os.path.exists(self.thumbsdir):
            os.mkdir(self.thumbsdir)
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.CPdatadir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        # Location of the alphabet sounds dir
        self.absdir = self.SPG.get_absdir_path()# alphabet sounds dir
        self.rchash = utils.read_rcfile(os.path.join(self.my_datadir, 'photoalbum.rc'))
        self.rchash['theme'] = self.theme
        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special CPGroup
        self.actives = SPSpriteUtils.SPInit(self.screen,self.backgr)
        
        self.timer = None
        self.timerpause = int(self.rchash[self.theme]['pause'])
        # We use old fashion surfs to blit on the screen iso buttons as transbuttons
        # with dynamic background would store a complete background surface each in memory!!
        main_exit_surf = utils.load_image(os.path.join(self.my_datadir, 'quit.icon.png'))
        main_exit_pos = (800 - main_exit_surf.get_size()[0], 0)
        self.main_exit_but = SPWidgets.TransImgButton(main_exit_surf, None, pos=main_exit_pos)
        self.main_exit_but.connect_callback(self.main_exit_but_cbf, MOUSEBUTTONDOWN)
        self.main_exit_but.set_use_current_background(True)
        #self.main_exit_rect = pygame.Rect(self.main_exit_pos + self.main_exit_surf.get_size())
        
        exit_surf = utils.load_image(os.path.join(self.my_datadir, 'category.icon.png'))
        exit_pos = (0, 0)
        self.exit_but = SPWidgets.TransImgButton(exit_surf, None, pos=exit_pos)
        self.exit_but.connect_callback(self.exit_but_cbf, MOUSEBUTTONDOWN)
        self.exit_but.set_use_current_background(True)
        #self.exit_rect = pygame.Rect(self.exit_pos + self.exit_surf.get_size())
        
#        self.pause_surf = utils.load_image(os.path.join(self.my_datadir, 'pause.icon.png'))
#        self.pause_pos = (385, 600 - self.pause_surf.get_size()[1])
#        self.pause_rect = pygame.Rect(self.pause_pos + self.pause_surf.get_size())
        
        play_surf = utils.load_image(os.path.join(self.my_datadir, 'play.icon.png'))
        play_pos = (385, 600 - play_surf.get_size()[1])
        self.play_but = SPWidgets.TransImgButton(play_surf,None,  pos=play_pos)
        self.play_but.connect_callback(self.play_but_cbf, MOUSEBUTTONDOWN)
        self.play_but.set_use_current_background(True)
        #self.play_rect = pygame.Rect(self.play_pos + self.play_surf.get_size())
        
#        self.mybuttons_rects = [self.main_exit_rect, self.exit_rect, \
#                                self.pause_rect, self.play_rect]
        self.buttons_list = [self.play_but, self.main_exit_but, self.exit_but]
        self.prev_mouse_pos = None
        self.SPG.tellcore_set_dice_minimal_level(6)
        self.SPG.tellcore_disable_menubuttons()
                
        self.clear_screen()
    
    def __del__(self):
        self.SPG.tellcore_enable_menubuttons()
    
    def clear_screen(self):
#        self.screen.blit(self.orgscreen,self.blit_pos)
#        self.backgr.blit(self.orgscreen,self.blit_pos)
        self.screen.blit(self.blacksurf, (0, 0))
        self.backgr.blit(self.blacksurf, (0, 0))
        pygame.display.update()

    def refresh_sprites(self):
        """Mandatory method, called by the core when the screen is used for blitting
        and the possibility exists that your sprites are affected by it."""
        self.actives.refresh()

    def get_helptitle(self):
        """Mandatory method"""
        return _("Photoalbum")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "photoalbum"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),
        " ",
        _("Number of levels : 1"),
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
        
    
    def get_helplevels(self):
        """Mandatory method, must return a string with the number of levels
        in the follwing format:
        _("This level has %s levels") % number-of-levels"""
        return _("This activity has %s levels") % 1

    
    def start(self):
        """Mandatory method."""
        self.stopme = False
        self.thumbx, self.thumby = eval(self.rchash[self.theme]['thumbsize'], {}, {})
        # check to see if the thumbs dir is up to date
        tlist = os.listdir(self.thumbsdir)
        albums = glob.glob(os.path.join(self.my_datadir, 'Album_*'))
        if not albums:
            self.SPG.tellcore_info_dialog(_("No photo albums found !\nYou should place your pictures inside directories called 'Album_1', 'Album_2' etc\n Place these directories inside %s" % self.my_datadir))
            self.stopme = True
        for d in albums:
            tname = os.path.split(d)[1]
            flist = os.listdir(d)
            flist.sort()
            if flist and flist[0] == '.svn': flist.pop(0)
            if tname + '.jpeg' not in tlist:
                self.logger.debug("no thumb found for album %s, creating one" % tname)
                img = utils.load_image(os.path.join(d, flist[0]))
                tsurf = utils.aspect_scale(img, (self.thumbx, self.thumby))
                p = os.path.join(self.thumbsdir, tname + '.jpeg')
                pygame.image.save(tsurf, p)
                self.logger.debug("%s thumb saved to %s" % (tname, p))
    
    def pre_level(self, level):
        """Mandatory method.
        Return True to call the eventloop after this method is called."""
        
    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        self.clear_screen()
        
        if level > 1:
            return
        return True
    
    def post_next_level(self):
        """Mandatory method.
        This is called once by the core after 'next_level' *and* after the 321 count.
        You should place stuff in here that run in a seperate thread like sound play."""
        self.photoindex = -1
        self.currentphoto = None
        self.button_state = 'show'
        self.hide_buttons_timer = None
        self.button_action = False
        self.show_thumbs()
    
    def display_mainexit(self):
        self.main_exit_but.display_sprite()
        self.exit_but.display_sprite()
        self.actives.add(self.main_exit_but, self.exit_but)
    
    def display_play_button(self):
        self.play_but.display_sprite()
        self.actives.add(self.play_but)
        
            
    def show_thumbs(self):
        self.stop_timer()
        self.clear_screen()
        self.actives.empty()
        self.main_exit_but.display_sprite()
        self.actives.add(self.main_exit_but)
        self.state = 'thumbs'
        self.thumbslist =[]
        
        x = 20
        flist = glob.glob(os.path.join(self.thumbsdir, '*.jpeg'))
        flist.sort()
        # Your top blit position, this depends on the menubar position 
        if self.blit_pos[1] == 0:
            y = 10
        else:
            y = 110
        for f in flist:
            data = os.path.splitext(os.path.split(f)[1])[0]
            img = utils.load_image(f)
            b = SPWidgets.SimpleButton(img, (x, y), data=data)
            b.display_sprite()
            self.thumbslist.append(b)
            x += img.get_size()[0] + 30
            if x > 790 - self.thumbx:
                y += self.thumby + 30
                x = 20
        self.actives.add(self.thumbslist)
    
    def slideshow(self):
        """Start slideshow"""
        self.logger.debug("Start slideshow")
        self.timer = Timer(self.timerpause,self.next_photo,\
                                lock=self.SPG.get_thread_lock(), startnow=False)
        self.timer.start()
        self.state = 'play'
    
    def stop_slide_show(self):
        self.logger.debug("Stop slideshow")
        self.stop_timer()
        self.state = 'manual'
        self.show_all_buttons()
    
    def show(self):
        """Start show photos one at the time"""
        self.clear_screen()
        self.button_state = 'hide'
        self.stop_timer()
        self.state = 'manual'
        self.next_photo()
    
    def next_photo(self):
        # Load photo sprites at run time to prevent large amounts of memory usage.
        if self.photoindex >= len(self.filelist) - 1:
            self.photoindex = 0
        else:
            self.photoindex += 1
        if self.currentphoto:
            self.currentphoto.erase_sprite()
        self.currentphoto = Photo(self.filelist[self.photoindex])
        self.currentphoto.display_sprite()
        if self.state == 'manual':
            self.show_all_buttons()
        return True
    
    def prev_photo(self):
        if self.photoindex == 0:
            self.photoindex = len(self.filelist) - 1
        else:
            self.photoindex -= 1
        if self.currentphoto:
            self.currentphoto.erase_sprite()
        self.currentphoto = Photo(self.filelist[self.photoindex])
        self.currentphoto.display_sprite()
        if self.state == 'manual':
            self.show_all_buttons()

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
            self.hide_buttons_timer.stop()
        except:
            pass

    def main_exit_but_cbf(self, *args):
        self.button_action = True
        self.stop_timer()
        self.SPG.tellcore_enable_menubuttons()
        self.SPG.tellcore_game_end()

    def exit_but_cbf(self, *args):
        self.button_action = True
        self.stop_timer()
        if self.state != 'thumbs':
            self.hide_all_buttons()
            self.show_thumbs()

    def play_but_cbf(self, *args):
        self.button_action = True
        if self.state == 'manual':
            self.state = 'play'
            self.prev_mouse_pos = 0
            self.hide_all_buttons()
            self.slideshow()
            
    def hide_all_buttons(self):
        if self.button_state == 'hide':
            return
        self.button_state = 'hide'
        for b in self.buttons_list:
            b.erase_sprite()
        self.actives.remove(self.buttons_list)
    
    def show_all_buttons(self):
        if self.button_state == 'show':
            return
        if self.hide_buttons_timer:
            self.hide_buttons_timer.stop()
        self.button_state = 'show'
        for b in self.buttons_list:
            b.display_sprite()
        self.actives.add(self.buttons_list)
        self.hide_buttons_timer = Timer(2.0, self.hide_all_buttons,\
                                lock=self.SPG.get_thread_lock(), startnow=False)
        self.hide_buttons_timer.start()
         
    def loop(self,events):
        """Mandatory method.
        This is the main eventloop called by the core 30 times a minute."""
        if self.stopme:
            self.SPG.tellcore_enable_menubuttons()
            self.SPG.tellcore_game_end()
        for event in events:
            if event.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP,  MOUSEMOTION):
                result = self.actives.update(event)
                if self.button_action:
                    self.button_action = False
                    return
                if event.type == MOUSEBUTTONDOWN:
                    if self.state == 'play':
                        self.stop_slide_show()
                        self.prev_mouse_pos = 0
                        return
                    elif self.state == 'thumbs':
                        if result:
                            self.logger.debug("loop, got a thumb")
                            self.state = 'show'
                            self.album = result[0][1][0]
                            self.actives.remove(self.thumbslist)
                            self.filelist = glob.glob(os.path.join(self.my_datadir, self.album, '*'))
                            self.filelist.sort()
                            self.show()
                            return
                    elif self.state != 'thumbs':
                        self.show_all_buttons()
                        self.prev_mouse_pos = pygame.mouse.get_pos()[0]
                # gestures
                if event.type == MOUSEBUTTONUP and self.prev_mouse_pos and not self.state == 'thumbs':
                    x = pygame.mouse.get_pos()[0]
                    if self.prev_mouse_pos - x > 20:
                        self.hide_all_buttons()
                        self.next_photo()
                    elif x - self.prev_mouse_pos > 20:
                        self.hide_all_buttons()
                        self.prev_photo()
        return 
        
