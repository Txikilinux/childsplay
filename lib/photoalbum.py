# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zytkiewicz stas.zytkiewicz@schoolsplay.org
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
# self.logger =  logging.getLogger("childsplay.photoalbum.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("childsplay.photoalbum")

# standard modules you probably need
import os, glob, random
import shelve, textwrap
import pygame
from pygame.constants import *

import utils
from SPConstants import *
import SPSpriteUtils
import SPWidgets
from Timer import Timer

try:
    from xml.etree.ElementTree import ElementTree
except ImportError:
    # try the python2.4 way 
    from elementtree.ElementTree import ElementTree

class Photo(SPSpriteUtils.SPSprite):
    def __init__(self, p):
        self.image = utils.load_image(p)
        SPSpriteUtils.SPSprite.__init__(self, self.image)
        pos = ((800 - self.rect.w) / 2, (600 - self.rect.h) / 2)
        self.moveto(pos)
        
class TextDisplay(SPSpriteUtils.SPSprite):
    def __init__(self, text, surf):
        self.image = surf
        tsurf = utils.char2surf(text, fsize=14, fcol=BLACK)
        self.image.blit(tsurf, (10, 3))
        SPSpriteUtils.SPSprite.__init__(self, self.image)
        self.moveto((0, 500))
        self.set_use_current_background(True)
        

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
        self.logger =  logging.getLogger("childsplay.photoalbum.Activity")
        self.logger.info("Activity started")
        self.SPG = SPGoodies
        self.lang = self.SPG.get_localesetting()[0][:2]
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
        self.shelvepath = os.path.join(self.thumbsdir, 'thumbs.db')
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.CPdatadir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        self.importDir = os.path.join(HOMEDIR, 'braintrainer', 'PicImport', self.lang)
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
        quit_surf = utils.load_image(os.path.join(self.my_datadir, 'quit.icon.png'))
        quitro_surf = utils.load_image(os.path.join(self.my_datadir, 'quit_ro.icon.png'))
        main_exit_pos = (800 - quit_surf.get_size()[0], 0)
        self.main_exit_but = SPWidgets.TransImgButton(quit_surf, quitro_surf, pos=main_exit_pos)
        self.main_exit_but.connect_callback(self.main_exit_but_cbf, MOUSEBUTTONDOWN)
        self.main_exit_but.set_use_current_background(True)
        #self.main_exit_rect = pygame.Rect(self.main_exit_pos + self.main_exit_surf.get_size())
        
        exit_surf = utils.load_image(os.path.join(self.my_datadir, 'category.icon.png'))
        exitro_surf = utils.load_image(os.path.join(self.my_datadir, 'category_ro.icon.png'))
        exit_pos = (0, 0)
        self.exit_but = SPWidgets.TransImgButton(exit_surf, exitro_surf, pos=exit_pos)
        self.exit_but.connect_callback(self.exit_but_cbf, MOUSEBUTTONDOWN)
        self.exit_but.set_use_current_background(True)
        
        play_surf = utils.load_image(os.path.join(self.my_datadir, 'play.icon.png'))
        playro_surf = utils.load_image(os.path.join(self.my_datadir, 'play_ro.icon.png'))
        
        play_pos = (0, 490 - play_surf.get_size()[1])
        self.play_but = SPWidgets.TransImgButton(play_surf, playro_surf, pos=play_pos)
        self.play_but.connect_callback(self.play_but_cbf, MOUSEBUTTONDOWN)
        #self.play_but.set_use_current_background(True)

        text_surf = utils.load_image(os.path.join(self.my_datadir, 'text.icon.png'))
        textro_surf = utils.load_image(os.path.join(self.my_datadir, 'text_ro.icon.png'))
        text_pos = (800 - text_surf.get_size()[0], 490 - text_surf.get_size()[1])
        self.text_but = SPWidgets.TransImgButton(text_surf, textro_surf, pos=text_pos)
        self.text_but.connect_callback(self.text_but_cbf, MOUSEBUTTONDOWN)
        self.text_but.set_use_current_background(True)

        self.buttons_list = [self.play_but, self.main_exit_but, self.exit_but]
        
        self.text_label = None
        self.text_back = utils.load_image(os.path.join(self.my_datadir, 'text_backgr.png'))
        self.textstring = ''
        
        self.prev_mouse_pos = None
        self.SPG.tellcore_set_dice_minimal_level(6)
        
        self.clear_screen()
    
    def __del__(self):
        self.SPG.tellcore_enable_menubuttons()
    
    def clear_screen(self):
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
        # first we look for language specific albums.
        # TODO: look for import foto's in schoolsplay.rc
        self.logger.debug("looking for %s_Album_* " % self.lang)
        albums = glob.glob(os.path.join(self.my_datadir, '%s_Album_*' % self.lang))
        if not albums:
            self.logger.debug("looking for *Album_* ")
            albums = glob.glob(os.path.join(self.my_datadir, '*Album_*'))
        if not albums:
            self.logger.debug("looking for *_Album_* ")
            glob.glob(os.path.join(self.my_datadir, '*_Album_*'))
        if not albums:
            self.logger.debug("looking for *Album*")
            glob.glob(os.path.join(self.my_datadir, '*Album*'))
        # Check if we have custom imported pictures
        self.logger.debug("looking for imported pictures in %s" % self.importDir)
        extra_albums = glob.glob(os.path.join(self.importDir, '%s_Album*' % self.lang))
        if extra_albums:
            albums += extra_albums
        if not albums:
            self.SPG.tellcore_info_dialog(_("No photo albums found !\nYou should place your pictures inside directories called 'Album_1', 'Album_2' etc\n Place these directories inside %s" % self.my_datadir))
            self.stopme = True
        # check that we don't use empty albums.
        self.logger.debug("found albums: %s" % albums)
        sh = shelve.open(self.shelvepath)
        sh_keys = sh.keys()
        for d in albums:
            tname = os.path.split(d)[1].encode('utf-8')
            flist = os.listdir(d)
            flist.sort()
            if not flist or os.path.splitext(flist[0])[1] not in IMAGE_EXT:
                continue
            if tname + '.jpeg' not in tlist or not sh.has_key(tname):
                self.logger.debug("no thumb found for album %s, creating one" % tname)
                img = utils.load_image(os.path.join(d, flist[0]))
                tsurf = utils.aspect_scale(img, (self.thumbx, self.thumby))
                p = os.path.join(self.thumbsdir, tname + '.jpeg')
                pygame.image.save(tsurf, p)
                self.logger.debug("%s thumb saved to %s" % (tname, p))
                sh[tname] = d
            elif sh.has_key(tname):
                sh_keys.remove(tname)
        if sh_keys:
            # we have thumbs but no albums, this is caused by the removal of albums.
            for key in sh_keys:
                if sh.has_key(key):
                    del sh[key]
                p = os.path.join(self.SPG.get_base_dir(), self.thumbsdir, key + '.jpeg')
                if os.path.exists(p):
                    self.logger.debug("removing thumb %s" % p)
                    os.remove(p)
        sh.close() 
    
    def pre_level(self, level):
        """Mandatory method.
        Return True to call the eventloop after this method is called."""
        
    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        self.SPG.tellcore_disable_menubuttons()
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
        
    def show_thumbs(self):
        self.stop_mytimer()
        self.clear_screen()
        self.actives.empty()
        self.main_exit_but.display_sprite()
        self.actives.add(self.main_exit_but)
        self.state = 'thumbs'
        self.thumbslist =[]
        
        x = 20
        flist = glob.glob(os.path.join(self.thumbsdir, '%s_*.jpeg' % self.lang))
        flist.sort()
        # Your top blit position, this depends on the menubar position 
        if self.blit_pos[1] == 0:
            y = 10
        else:
            y = 110
        sh = shelve.open(self.shelvepath)
        for f in flist:
            key = os.path.splitext(os.path.split(f)[1])[0].encode('utf-8')
            img = utils.load_image(f)
            if sh.has_key(key):
                b = SPWidgets.SimpleButton(img, (x, y), data=sh[key])
            else:
                self.logger.error("missing shelve key: %s" % key)
                continue
            b.display_sprite()
            self.thumbslist.append(b)
            x += img.get_size()[0] + 30
            if x > 790 - self.thumbx:
                y += self.thumby + 30
                x = 20
        self.actives.add(self.thumbslist)
        sh.close()
    
    def slideshow(self):
        """Start slideshow"""
        self.logger.debug("Start slideshow")
        self.text_but.erase_sprite()
        self.actives.remove(self.text_but)
        self.timer = Timer(self.timerpause,self.next_photo,\
                                lock=self.SPG.get_thread_lock(), startnow=False)
        self.timer.start()
        self.state = 'play'
    
    def stop_slide_show(self):
        self.logger.debug("Stop slideshow")
        self.stop_mytimer()
        self.state = 'manual'
        self.show_all_buttons()
        
    def show(self):
        """Start show photos one at the time"""
        self.clear_screen()
        self.button_state = 'hide'
        self.stop_mytimer()
        self.state = 'manual'
        self.next_photo()
    
    def next_photo(self):
        # Load photo sprites at run time to prevent large amounts of memory usage.
        if self.photoindex >= len(self.filelist) - 1:
            self.photoindex = 0
        else:
            self.photoindex += 1
#        effects = (self.wipeleft2right, self.wiperight2left)
#        apply(random.choice(effects), (self.filelist[self.photoindex], ))
          
#        print "effects finished"
        if self.currentphoto:
            self.currentphoto.erase_sprite()
        if self.text_label:
            self.text_label.erase_sprite()
            self.text_label = None
        
        p = self.filelist[self.photoindex]
        if self.textxml and self.textxml.has_key(os.path.basename(p)):
            hash = self.textxml[os.path.basename(p)]
            title = "%s: %s" % (self.textxml['album_name'], hash['title'])
            text = "\n".join(textwrap.wrap(hash['text'], 90))
            
            self.textstring = "%s\n%s" % (title, text)
        else:
            self.textstring = ''    
            
        self.currentphoto = Photo(p)
        self.currentphoto.display_sprite()
        if self.state == 'text':
            self.state = 'manual'
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
        if self.text_label:
            self.text_label.erase_sprite()
            self.text_label = None
        p = self.filelist[self.photoindex]
        if self.textxml and self.textxml.has_key(os.path.basename(p)):
            hash = self.textxml[os.path.basename(p)]
            title = "%s: %s" % (self.textxml['album_name'], hash['title'])
            text = "\n".join(textwrap.wrap(hash['text'], 90))
            
            self.textstring = "%s\n%s" % (title, text)
        else:
            self.textstring = ''    
        self.currentphoto = Photo(p)
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
    
    def stop_mytimer(self):
        try:
            self.timer.stop()
        except:
            pass
        try:
            self.hide_buttons_timer.stop()
        except:
            pass
    
    def stop_timer(self):
        """You *must* provide a method to stop timers if you use them.
        The SPC will call this just in case and catch the exception in case 
        there's no 'stop_timer' method""" 
        self.SPG.tellcore_enable_menubuttons()

    def main_exit_but_cbf(self, *args):
        self.button_action = True
        self.stop_mytimer()
        self.SPG.tellcore_enable_menubuttons()
        self.SPG.tellcore_game_end()

    def exit_but_cbf(self, *args):
        self.button_action = True
        self.stop_mytimer()
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
    
    def text_but_cbf(self, *args):
        if self.state == 'play':
            return
        if self.text_label:
            self.text_label.erase_sprite()
            self.text_label = None
            self.state = 'manual'
            self.show_all_buttons()
        else:
            #self.play_but.erase_sprite()
            self.text_label = TextDisplay(self.textstring, self.text_back.copy())
            self.text_label.display_sprite()
            self.state = 'text'

    def hide_all_buttons(self):
        if self.button_state == 'hide':
            return
        self.button_state = 'hide'
        for b in self.buttons_list:
#            if self.state == 'text' and b is self.play_but:
#                continue
            b.erase_sprite()
        self.text_but.erase_sprite()
        self.actives.remove(self.buttons_list)
        self.actives.remove(self.text_but)
    
    def show_all_buttons(self):
        if self.button_state == 'show':
            return
        if self.hide_buttons_timer:
            self.hide_buttons_timer.stop()
        self.button_state = 'show'
        for b in self.buttons_list:
            b.display_sprite()
        self.actives.add(self.buttons_list)
#        if self.state == 'text':
#            self.actives.remove(self.play_but)
#            self.play_but.erase_sprite()
        if self.state == 'play':
            self.actives.remove(self.text_but)
            self.text_but.erase_sprite()
        else:
            if self.textstring:
                self.text_but.display_sprite()
                self.actives.add(self.text_but)
        #self.hide_buttons_timer = Timer(2.0, self.hide_all_buttons,\
         #                       lock=self.SPG.get_thread_lock(), startnow=False)
        #self.hide_buttons_timer.start()
    
    def parse_xml(self, p):
        """Parses the whole xml tree into a hash with lists. Each list contains hashes
        with the elelements from a 'activity' element.
        """  
        self.logger.debug("Starting to parse: %s" % p)
        if not os.path.exists(p):
            return {}
        tree = ElementTree()
        try:
            tree.parse(p)
        except Exception, info:
            self.logger.error("%s" % info)
            raise utils.MyError, info
        # here we start the parsing
        albumNode = tree.getroot()
        album_name = albumNode.get('name')
        album_numpics = albumNode.get('nofPicture')
        
        photoNodes = tree.findall('photo')
        self.logger.debug("found %s photo nodes in total" % len(photoNodes))
        albumhash = {'album_name': album_name, 'album_numpics':album_numpics}
        for node in photoNodes:
            hash = {}
            try:
                hash['name'] = node.get('name')
                hash['title'] = node.find('title').text
                hash['text'] = node.find('text').text
            except AttributeError, info:
                self.logger.error("The %s is badly formed, missing element(s):%s,%s" % (xml, info, e))
                albumhash = {}
            else:
                albumhash[hash['name']] = hash
        #self.logger.debug("xml hash:%s" % albumhash)
        return albumhash

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
                            album = result[0][1][0]
                            xml = os.path.join(album, 'text.xml')
                            self.textxml = self.parse_xml(xml)# could return None
                            self.actives.remove(self.thumbslist)
                            self.filelist = [f for f in utils.find_files(album, IMAGE_EXT_PATTERN)]
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
        
#    def wipeleft2right(self, p):
#        image = utils.load_image(p)
#        rect = image.get_rect()
#        pos = ((800 - rect.w) / 2, (600 - rect.h) / 2)
#        self.backgr.fill(BLACK)
#        self.backgr.blit(image, pos)
#        for y in range(0, 600, 10):
#            for x in range(0, 800, 10):
#                pygame.time.wait(2)
#                dirty = self.screen.blit(self.backgr, (x, y), (x, y, x+10, y+10))
#                pygame.display.update(dirty)
#
#    def wiperight2left(self, p):
#        image = utils.load_image(p)
#        rect = image.get_rect()
#        pos = ((800 - rect.w) / 2, (600 - rect.h) / 2)
#        self.backgr.fill(BLACK)
#        self.backgr.blit(image, pos)
#        x_range = range(0, 800, 10)
#        x_range.sort(reverse=True)
#        for y in range(0, 600, 10):
#            for x in x_range:
#                pygame.time.wait(2)
#                dirty = self.screen.blit(self.backgr, (x, y), (x-10, y, x, y+10))
#                pygame.display.update(dirty)
#
#   
