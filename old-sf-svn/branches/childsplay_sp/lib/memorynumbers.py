# -*- coding: utf-8 -*-

# Copyright (c) 2006-2008 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           nmemory.py
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

# letter memory numbers

#create logger, logger was setup in SPLogging
import logging
module_logger = logging.getLogger("schoolsplay.memorynumbers")

import os,sys,glob,random,copy

import pygame
from pygame.constants import *

import childsplay_sp.utils as utils
from childsplay_sp.SPConstants import *
from childsplay_sp.SPSpriteUtils import SPInit, SPSprite,MySprite

# containers that can be used globally to store stuff
class Img:
    pass
class Snd:
    pass
class Global:
    pass

class Card(SPSprite):
    # This is a global reference to hold a selected object.
    # Used like this Selected is the same in all card classes
    # So when we set Selected in class0 it's also set in class1, class2 etc
    # see the callback method on how we use Selected
    Selected = None 
    def __init__(self,closedcard,opencard,name):
        """This class has it's own callback function and it will connect itself"""
        # The image passed to SPSprite will become self.image
        SPSprite.__init__(self,closedcard)# embed it in this class
        self.name = name
        self.closedimage = closedcard
        self.openimage = opencard# image of a open card
        # connect to the MOUSEBUTTONDOWN event, no need for passing data
        self.connect_callback(self.callback,MOUSEBUTTONDOWN)
        
    def callback(self,sprite,event,*args):
        """ we will show the openimage when the user hits us""" 
        # we check the 'global' attribute first 
        if not Card.Selected: # nothing selected yet
            # nothing selected, setting selected to this sprite
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
            return
        # we are the second card
        self.image = self.openimage
        self.display_sprite()
        Global.selected_cards[self] += 1
        if Card.Selected.name is sprite.name: # cards are the same  
            # "hooray" we found the second one
            pygame.time.wait(1000)
            self.remove_sprite()
            Card.Selected.remove_sprite()
            Card.Selected = None
        else:
            # bummer, wrong card
            pygame.time.wait(1000)
            # reset this card
            self.image = self.closedimage
            self.display_sprite()
            # reset previous selected card
            Card.Selected.image = Card.Selected.closedimage
            Card.Selected.display_sprite()
            Card.Selected = None

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
        self.col = pygame.color.Color
        self.logger =  logging.getLogger("schoolsplay.memorynumbers.Activity")
        self.logger.info("Activity started")
        self.SPG = SPGoodies
        self.screen = self.SPG.get_screen()
        self.orgscreen = self.screen.convert()# we use this to restore the screen
        self.backgr = self.SPG.get_background()
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','LMemoryData')
        self.theme = self.SPG.get_theme()
        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special SPGroup
        self.actives = SPInit(self.screen,self.backgr)
        # list to hold the sprite objects.
        # we don't keep references to them as we query the sprites themself.
        self.imagelist = []
        # list with characters
        self.charlist = map(str,range(1,21))
        scaler = utils.ScaleImages(None,(136,136))
        # load all the images we need
        try:
            self.cardback = scaler.get_images(\
                utils.load_image(os.path.join(self.my_datadir,'cardback.png'),\
                                theme=self.theme)\
                                            )[0]
            # the rest of the images are turn into sprites in the start method
            self.emptycard = scaler.get_images(\
                utils.load_image(os.path.join(self.my_datadir,'cardfront.png'))\
                                            )[0]
        except (StandardError,utils.MyError),info:
            self.logger.error("Can't load images for sprites: %s" % info)
            raise utils.MyError(str(info))# MyError will make the core end this game
        
    def get_helptitle(self):
        """Mandatory method"""
        return _("NumbersMemory")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase and must be the 
        module name without the '.py' extension."""
        return "memorynumbers"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),
        _("Classic memory game where you have to find pairs of cards."),
        " "]
        return text 
    
    def get_helptip(self):
        """Mandatory method, when no tips available returns an empty string"""
        return [_("Correctness is more important than speed")]
        
    def get_helptype(self):
        """Mandatory method, you must set an type"""
        # Possible types are: Memory, Math, Puzzle, Keyboardtraining, Mousetraining
        #                     Language, Alphabet, Fun, Miscellaneous
        return _("Memory")
        
    def get_helplevels(self):
        """Mandatory method, must return a string with the number of levels
        in the follwing format:
        _("This level has %s levels" % number-of-levels)"""
        return _("This activity has %s levels") % 6
    
    def start(self):
        """Mandatory method.
        Called when the activity is first started by the core."""        
        # here we setup the card layout for each level (6 levels), list[0] is level 1 ect
        # (4,2) means 4 collomns of 2 rows 
        self.level_layout = [(4,2),(4,3),(5,4),(7,4),(6,5),(6,6)]
        
    def next_level(self,level,db_mapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        global selected_cards
        self.logger.debug("next_level called with %s" % level)
        if level > 6: return False # We only have 6 levels
        # db_mapper is a Python class object that provides easy access to the 
        # dbase.
        self.db_mapper = db_mapper
        # store number of cards into the db table 'cards' col
        a,b = self.level_layout[level-1]
        self.db_mapper.insert('cards',a*b)
        # make sure we don't have any sprites left in our group
        self.actives.empty()
        # reset the screen to clear any crap from former levels
        self.clear_screen()
        cx,cy = self.level_layout[level-1]# levels start with 1
        random.shuffle(self.charlist)
        self.num_of_cards = cx*cy//2# how many cards do we need in total?
        cards = self.charlist[:self.num_of_cards]*2# we must have doubles of course
        random.shuffle(cards)# needs to be shuffled
        # values for the shadefade method
        size = 120
        effect_amt = 6
        rectsizex,rectsizey = 136,136
        r,g,b = 255,0,0
        # must we scale? we only test y if y fits x will always fit as the diff 
        # between x and y is never greater then 2
        # max y screen is 500, standard card size is 136 + little border = 140
        scalesize = 470//cy - 10
        if scalesize < 120 or cx > 6:# first scale cards
            if cx > 6: scalesize = 96
            scaler = utils.ScaleImages(None,(scalesize,scalesize))
            # we also need a scaled cardback
            scaledcardback = scaler.get_images(image=self.cardback)[0]
            # and a emptycard
            emptycard = scaler.get_images(image=self.emptycard)[0]
            for char in cards:
                # load and put the images in a list together with their name
                # which we use as a id for the sprite later on
                # Create nicer characters then the standard fonts.
                img = utils.char2surf(char,scalesize - 30, bold=True)
                #img = utils.shadefade(char,scalesize,effect_amt,\
                #                        (scalesize,scalesize),(r,g,b))
                cimg = emptycard.convert()
                ix, iy = img.get_size()
                cix, ciy = cimg.get_size()
                x = (cix - ix) / 2
                y = 4
                cimg.blit(img,(x, y))
                #self.imagelist.append((img,char))
                # No need to create lookup tables we just use
                # the sprite callback framework to pass objects around.
                # See the Card class how you can use the SPSprite objects and how
                # these objects can act on events.
                # Card connects itself to a MOUSEBUTTONDOWN event.
                cardbacksprite = Card(scaledcardback,cimg,name=char)
                # we must add the sprite to the actives group, we call this group in the
                # eventloop
                self.actives.add(cardbacksprite)
        else:
            # We don't scale, logic is the same as above.
            for char in cards:
                img = utils.char2surf(char,70, bold=True)
    #            img = utils.shadefade(char,size,effect_amt,\
    #                                    (rectsizex,rectsizey),(r,g,b))
                # center the image on the card
                cimg = self.emptycard.convert()
                ix, iy = img.get_size()
                cix, ciy = cimg.get_size()
                x = (cix - ix) / 2
                y = 4
                cimg.blit(img,(x, y))
                cardbacksprite = Card(self.cardback,cimg,name=char)
                self.actives.add(cardbacksprite)
        if scalesize > 136:
            step = 140
        else:
            step = scalesize + 8
        start_x = (800-(cx*step)) // 2
        start_y = 6+(500-(cy*step)) // 2
        # get a list with our sprites from the actives group
        spritelist = self.actives.get_sprites()
        # used to record how many times the same card is shown.
        # It's setup in the next_level method and used by the Card objects.
        # we store it into a class namespace to make it globally available.
        Global.selected_cards = {}
        for y in range(cy):
            for x in range(cx):
                sprite = spritelist.pop()
                Global.selected_cards[sprite] = 0
                sprite.display_sprite((start_x+(x*step),start_y+(y*step)))
        pygame.display.update()
        return True
    
    def post_next_level(self):
        """Mandatory method.
        This is called by the core after 'next_level' *and* after the 321 count.
        You should place stuff in here that run in a seperate thread like sound play."""
        pass
    
    def get_score(self,timespend):
        """Mandatory method.
        @timespend is the time spend inside the level as it's calculated
        by the core.
        returns the score value for the past level.
        return None if no score value is used"""
        # when this is called the level is finished
        # the score is calculated like this:
        totalcards = self.num_of_cards*2
        cardsturnt = self.knowncards
        m,s = timespend.split(':')
        seconds = int(m)*60 + int(s)
        print totalcards,cardsturnt,seconds
        c = 0.7
        f = 0.5
        
        score =  8.0 / ( max( float(cardsturnt)/float(totalcards)/1.5, 1.0 ) )**c \
                        + 2.0 / ( max( seconds/(totalcards*2), 1.0)) **f
        return score
    
    def clear_screen(self):
        self.screen.blit(self.orgscreen,(0,0))
        self.backgr.blit(self.orgscreen,(0,0))
        pygame.display.update()
    
    def loop(self,events):
        """Mandatory method
        """
        for event in events:
            if event.type is MOUSEBUTTONDOWN:
                self.actives.refresh(event)
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
                    self.SPG.tellcore_level_end(store_db=True)
        return 

