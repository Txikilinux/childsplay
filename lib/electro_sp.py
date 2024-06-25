# -*- coding: utf-8 -*-

# Copyright (c) 2010 stas zytkiewicz stas.zytkiewicz@schoolsplay.org
# Parts are taken from the Braintrainer project http://www.braintrainerplus.com
# 
#           electro_sp.py
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
# self.logger =  logging.getLogger("childsplay.electro_sp.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("childsplay.electro_sp")

# standard modules you probably need
import os,sys, textwrap
import glob
import random
import pygame
from pygame.constants import *

import utils
from SPConstants import *
import SPSpriteUtils
import SPWidgets
# containers that can be used globally to store stuff
class Img:
    pass
class Snd:
    pass

class Global:
    pass   
class Card(SPSpriteUtils.SPSprite):
    # This is a global reference to hold a selected object.
    # Used like this Selected is the same in all card classes
    # So when we set Selected in class0 it's also set in class1, class2 etc
    # see the callback method on how we use Selected
    Selected = None 
    def __init__(self,opencard,name, scoreobs, sound):
        """This class has it's own callback function and it will connect itself"""
        # The image passed to SPSprite will become self.image
        SPSpriteUtils.SPSprite.__init__(self,opencard)# embed it in this class
        self.name = name
        self.openimage = opencard.convert() # image of a open card
        pygame.draw.rect(self.openimage, SPRING_GREEN,self.image.get_rect(), 12)
        self.wrongimage = opencard.convert()
        pygame.draw.rect(self.wrongimage, RED1,self.image.get_rect(), 12)
        self.org_openimage = opencard.convert()
        # connect to the MOUSEBUTTONDOWN event, no need for passing data
        self.connect_callback(self.callback,MOUSEBUTTONDOWN)
        self.scoreobs = scoreobs
        self.Sound = sound
            
    def callback(self,sprite,event,*args):
        """ we draw a green border around the card when the user hits us""" 
        # we check the 'global' attribute first 
        if not Card.Selected: # nothing selected yet
            # nothing selected, setting selected to this sprite
            self.Sound.button_hover.play()
            Card.Selected = self
            # keep track on how many times this card is opened
            # this is also stored in the dbase
            Global.selected_cards[self] += 1 
            self.image = self.openimage
            self.display_sprite()
            return
        # remember Card.Selected holds a sprite of the other card
        elif Card.Selected is self:
            # user hits same card
            self.Sound.wrong.play()
            # reset this card
            Card.Selected = None
            self.image = self.org_openimage
            self.display_sprite()
            return
        # we are the second card
        self.image = self.openimage
        self.display_sprite()
        Global.selected_cards[self] += 1
        if Card.Selected.name == sprite.name: # cards are the same  
            # "hooray" we found the second one
            self.Sound.good.play()
            pygame.time.wait(1000)
            self.remove_sprite()
            Card.Selected.remove_sprite()
            Card.Selected = None
            self.scoreobs(10)
        else:
            # bummer, wrong card
            self.image = self.wrongimage
            self.display_sprite()
            Card.Selected.image = Card.Selected.wrongimage
            Card.Selected.display_sprite()
            self.Sound.wrong.play()
            pygame.time.wait(1000)
            # reset this card
            self.image = self.org_openimage
            self.display_sprite()
            # reset previous selected card
            Card.Selected.image = Card.Selected.org_openimage
            Card.Selected.display_sprite()
            Card.Selected = None
            self.scoreobs(-10)
            
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
        self.logger =  logging.getLogger("childsplay.electro_sp.Activity")
        self.logger.info("Activity started")
        self.SPG = SPGoodies
        self.theme = self.SPG.get_theme()
        self.screen = self.SPG.get_screen()
        self.screenclip = self.SPG.get_screenclip()
        self.blit_pos = self.screenclip.left, self.screenclip.top
        self.orgscreen = pygame.Surface(self.screenclip.size) # we use this to restore the screen
        self.orgscreen.blit(self.screen, (0, 0), self.screenclip)
        self.backgr = self.SPG.get_background()
        # The location of the activities Data dir
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','Electro_spData')
        self.rchash = utils.read_rcfile(os.path.join(self.my_datadir, 'electro_sp.rc'))
        self.rchash['theme'] = self.theme
        self.logger.debug("rchash: %s" % self.rchash)
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.CPdatadir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        # Location of the alphabet sounds dir
        self.absdir = self.SPG.get_absdir_path()# alphabet sounds dir
        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special CPGroup
        self.actives = SPSpriteUtils.SPInit(self.screen,self.backgr)
        self.scoredisplay = self.SPG.get_scoredisplay()
        files = ('dealcard1.wav','good.ogg','wrong.ogg','button_hover.wav')
        self.Sound = Snd()
        for file in files:
            setattr(self.Sound, file[:-4], utils.load_sound(os.path.join(self.CPdatadir, file)))
            
    def clear_screen(self):
        self.screen.blit(self.orgscreen,self.blit_pos)
        self.backgr.blit(self.orgscreen,self.blit_pos)
        pygame.display.update()

    def get_moviepath(self):
        movie = os.path.join(self.my_datadir,'help.avi')
        return movie
            
    def refresh_sprites(self):
        """Mandatory method, called by the core when the screen is used for blitting
        and the possibility exists that your sprites are affected by it."""
        self.actives.redraw()

    def get_helptitle(self):
        """Mandatory method"""
        return ("Electro_sp")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "electro_sp"
    
    def get_help(self):
        """Mandatory method"""
        text = [("The aim of this activity:"), 
                ("The game is to match pairs of pictures"), 
                " ", 
                ("You select the pictures by touching them.\nAs you progress through the star levels more pairs appear to match."), 
            " ", 
            ]
        return text 
    
    def get_helptip(self):
        """Mandatory method, when no tips available returns an empty string"""
        return ("Correctness is more important than speed")
        
    def get_helptype(self):
        """Mandatory method, you must set an type"""
        # Possible types are: Memory, Math, Puzzle, Keyboardtraining, Mousetraining
        #                     Language, Alphabet, Fun, Miscellaneous
        return ("Memory")
    
    def get_helplevels(self):
        """Mandatory method, must return a string with the number of levels
        in the follwing format:
        _("This level has %s levels") % number-of-levels"""
        return ("This activity has %s levels") % 6

    def start(self):
        """Mandatory method."""
        # TODO: level 5&6 are the same
        #self.gamelevels = [(2,3,170,150),(2,4,95,100),(3,4,95,50),(4,4,160,40),(4,5,105,20),(4,5,105,20)]
        self.tile = 'tileset_1'# default value as self.tile could be uninitialized when running from DT
        self.pre_level_flag = False
        self.displaydscore = 0
        self.levelrestartcounter = 0
        self.level = 1
        self.AreWeDT = False
    
    def pre_level(self, level):
        """Mandatory method"""
        self.logger.debug("pre_level called with %s" % level)
        self.pre_level_flag = True
        if self.blit_pos[1] == 0:
            y = 10
        else:
            y = 110
        x = 100
        
        files = glob.glob(os.path.join(self.my_datadir,'tileset_*.png'))
        files.sort()
        lbl = SPWidgets.Label(("Please, choose a set of cards."),\
                                (30, y),fsize=24, transparent=True)
        lbl.display_sprite()
        y += lbl.get_sprite_height()
        for line in textwrap.wrap(("The difficulty of the set increases from left to right."), 40):
            lbl = SPWidgets.Label(line,(30, y), fsize=24, transparent=True)
            lbl.display_sprite()
            y += lbl.get_sprite_height()
        y += 50
        tmp_img = utils.load_image(files[0])
        count = 1
        total_width = ((len(files) / 2) * (tmp_img.get_width())) + (((len(files) / 2) - 1)  * 20)
        first_x = (self.screen.get_width() / 2) - (total_width / 2)
        for tilepath in files:
            x = first_x + (count-1)*tmp_img.get_width() + (count-1)*20
            img = utils.load_image(tilepath)
            data = os.path.splitext(os.path.split(tilepath)[1])[0]
            if not data[-2:] == 'ro':
                img_ro = utils.load_image(os.path.join(self.my_datadir, '%s_ro.png' % data))
                b = SPWidgets.SimpleTransImgButton(img, img_ro, (x, y), data=data)
                b.display_sprite()
                self.actives.add(b)
                count += 1
        return True
    
    def dailytraining_pre_level(self, level):
        """Mandatory method"""
        pass
        
    def dailytraining_next_level(self, level, dbmapper):
        """Mandatory method.
        This should handle the DT logic"""
        self.AreWeDT = True
        self.SPG.tellcore_disable_level_indicator()
        self.next_level(level, dbmapper)
        return True

    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        self.Sound.dealcard1.play()
        self.logger.debug("next_level called with %s" % level)
        if level > 6: return False # We only have 6 levels
        if level == self.level:
            self.levelrestartcounter += 1
        self.level = level
        # used to record how many times the same card is shown.
        # we store it into a class namespace to make it globally available.
        Global.selected_cards = {}
        Card.Selected = None
        # db_mapper is a Python class object that provides easy access to the 
        # dbase.
        self.db_mapper = dbmapper
        # make sure we don't have any sprites left in our group
        self.actives.empty()
        # reset the screen to clear any crap from former levels
        self.clear_screen()
        # here we setup the card layout for each level (6 levels), list[0] is level 1 ect
        # (4,2) means 4 collomns of 2 rows 
        level_layout = [(3,2),(4,2),(4,3),(4,4),(5,4),(6,4)]
        # store number of cards into the db table 'cards' col
        a,b = level_layout[level-1]
        self.db_mapper.insert('cards',a*b)
        self.num_of_cards = a*b//2# how many cards do we need in total?
        self.levelupcount = 1
        # we don't keep references to them as we query the sprites themself.
        imagelist = []
        # load all the images we need
        try:
            imgdir = os.path.join(self.my_datadir, self.tile, self.theme)
            if self.rchash.has_key(self.theme):
                cardfront = self.rchash[self.theme]['cardfront']
            else:
                cardfront = self.rchash['childsplay']['cardfront']
            emptycard = utils.load_image(os.path.join(imgdir,cardfront))
            
            images = glob.glob(os.path.join(imgdir,'*A.*'))
            images = random.sample(images, self.num_of_cards)
            #self.logger.debug("Contents of my_images %s" % myimages)
            for imgfile in images:
                # load and put the images in a list together with their file name - A | B
                # which we use as a id for the sprite later on
                file = os.path.basename(imgfile)
                # The A file
                img = utils.load_image(imgfile)
                imagelist.append((img,file[:-5]))
                # The B file
                img = utils.load_image(imgfile.replace('A','B', 1))
                imagelist.append((img,file[:-5]))
        except( Exception, utils.MyError ) as info:
            self.logger.exception("Can't load images for sprites: %s" % info)
            raise utils.MyError(str(info))# MyError will make the core end this game
        else:
            self.logger.debug("Loaded %s images" % len(imagelist))
        
        # Unpack our image list and blit them on scaled cards
        if emptycard.get_alpha():
            cimg = emptycard.convert_alpha()
        else:
            cimg = emptycard.convert()
        # must we scale? we only test y if y fits x will always fit as the diff 
        # between x and y is never greater then 2
        # max y screen is 490, standard card size is 150x150
        cards = []
        cx,cy = level_layout[level-1]# levels start with 1
        scalesize = 490//cy - 10
        if scalesize < 120 or cx > 6:# first scale cards
            if cx > 6: scalesize = 96
            for img,file in imagelist:
                if emptycard.get_alpha():
                    cimg = emptycard.convert_alpha()
                else:
                    cimg = emptycard.convert()
                cimg = utils.aspect_scale(cimg, (scalesize, scalesize))
                cardcenter = cimg.get_rect().center
                s = utils.aspect_scale(img, (scalesize-10, scalesize-10))
                # center the image on the card
                sc = s.get_rect()
                sc.center = cardcenter
                cimg.blit(s, sc)
                cardsprite = Card(cimg,file, self.scoreobs, self.Sound)
                cards.append(cardsprite)
        else:
            for img,file in imagelist:
                if emptycard.get_alpha():
                    cimg = emptycard.convert_alpha()
                else:
                    cimg = emptycard.convert()
                cardcenter = cimg.get_rect().center
                s = utils.aspect_scale(img, (120, 120))
                # center the image on the card
                sc = s.get_rect()
                sc.center = cardcenter
                cimg.blit(s, sc)
                cardsprite = Card(cimg,file, self.scoreobs, self.Sound)
                cards.append(cardsprite)
        random.shuffle(cards)
        if scalesize > 136:
            step = 155
        else:
            step = scalesize + 8
        # Your top blit position, this depends on the menubar position        
        if self.blit_pos[1] == 0:
            y = 10
        else:
            y = 110
        start_x = (800-(cx*step)) // 2
        start_y = (500-(cy*step)) // 2 + y 
        
        for yy in range(cy):
            for x in range(cx):
                sprite = cards.pop()
                Global.selected_cards[sprite] = 0
                sprite.display_sprite((start_x+(x*step),start_y+(yy*step)))
                self.actives.add(sprite)
        pygame.display.update()
        return True
        
    def post_next_level(self):
        """Mandatory method.
        This is called once by the core after 'next_level' *and* after the 321 count.
        You should place stuff in here that run in a seperate thread like sound play."""
                
    def get_score(self,timespend):
        """Mandatory method.
        @timespend is the time spend inside the level as it's calculated
        by the core.
        returns the score value for the past level.
        return None if no score value is used"""
        # T = Total cards
        # K = How many times the cards are selected. (a perfect game K == T)
        # F = Fraction of total result related to points. (maximum result is 10)
        # F1 = Fraction of result related to time
        # C = multiplier
        # S = time spend in seconds
        try:
            T = float(self.num_of_cards * 2)
            K = float(self.knowncards)
        except AttributeError:
            return None
        m,s = timespend.split(':')
        S = float(int(m)*60 + int(s))
        F = 7.0
        F1 = 3.0
        C = 0.6
        C1 = 1.8
        points = F / max( K / T, 1.0 ) ** C1
        time = F1 / max(S / T , 1.0) ** C
        self.logger.info("@scoredata@ %s level %s T %s K %s S %s points %s time %s" % \
                         (self.get_name(), self.level, T, K, S, points, time))
        score = points + time
        return score
    
    def scoreobs(self, i):
        """Called by the card object with a value to display as the score."""
        self.displaydscore += i
        if self.displaydscore <= 0:
            self.displaydscore = 0
        self.scoredisplay.set_score(self.displaydscore * 5)
        if i > 0:
            # correct answer
            self.levelupcount += 1
        else:
            self.levelupcount -= 1
    
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
        for event in events:
            if event.type in (MOUSEBUTTONUP, MOUSEBUTTONDOWN, MOUSEMOTION):
                result = self.actives.update(event)
                if self.pre_level_flag:
                    if result:
                        self.logger.debug("loop, got a result and stop this loop")
                        self.SPG.tellcore_pre_level_end()
                        self.pre_level_flag = False
                        self.tile = result[0][1][0]
                        break
                if not self.actives.sprites():
                    # no more sprites left so the level is done.
                    # count the times the cards are turned.
                    # a lower value would be better, ideally a number equal to
                    # the number of cards would be a perfect score.
                    num = 0
                    for n in Global.selected_cards.values():
                        num += n
                    # store into dbase
                    self.db_mapper.insert('knowncards',num)
                    # set an attribute so that 'get_score' can calculate the score
                    self.knowncards = num
                    # we call the SPGoodies observer to notify the core the level
                    # is ended and we want to store the collected data
                    if self.levelrestartcounter >= int(self.rchash[self.theme]['autolevel_value']):
                        levelup = 1
                        self.levelrestartcounter = 0
                    else:
                        levelup = 0
                    if self.AreWeDT:
                        self.SPG.tellcore_level_end(level=self.level)
                    else:
                        self.SPG.tellcore_level_end(store_db=True, \
                                            level=min(6, self.level), \
                                            levelup=levelup)
        return 
