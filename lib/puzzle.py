# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zytkiewicz stas.zytkiewicz@schoolsplay.org
# Copyright (c) 2006 Miguel Pérez Francisco <mperez@icc.uji.es>
#
#           puzzle.py
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
# self.logger =  logging.getLogger("childsplay.puzzle.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("childsplay.puzzle")

# standard modules you probably need
import os,sys,random,glob, textwrap

import pygame
from pygame.constants import *

import utils
from SPConstants import *
import SPSpriteUtils
import SPWidgets

########################################
# Constats definition
########################################

# Position of the splitted image
INIX=20
INIY=0

# Position of the target image
INIXF=450
INIYF=0

# Offset between the position of the mouse and the piece being translated
OFFSETIMGX=30
OFFSETIMGY=30

# Size of the lines between pieces
TAMLINEA=2

#Position of the thumbnail of the image
INIXTH,INIYTH=350,396

# containers that can be used globally to store stuff
class Img:
    pass
class Snd:
    pass
class Misc:
    score = 0

#TODO: make sure we don't get the same image twice in one level

class Piece(SPSpriteUtils.SPSprite):
    """ A piece of a puzzle """
    Selected = None
    Brothers = []
    def __init__(self,image, correct_position, obs, name):
        self.org_image = image.convert()
        shadow = pygame.Surface(image.get_rect().size)
        shadow.fill(DARKGREEN)
        self.shadow = SPSpriteUtils.SPSprite(shadow)
        pygame.draw.rect(image, BLACK, image.get_rect(), TAMLINEA)
        SPSpriteUtils.SPSprite.__init__(self,image)
        self.connect_callback(self._activated_cbf, MOUSEBUTTONDOWN)
        self.correct_position = correct_position
        self.name = name
        self.logger = logging.getLogger("childsplay.puzzle.Piece")
        self.ImSelected = False
        self.obs = obs
        Piece.Brothers.append(self) 
        self.temp = 140
        
    def _activated_cbf(self, sprite, event, data):
        #self.logger.debug("_activated_cbf called")
        if Piece.Selected and self.name == Piece.Selected.name:
            self._do_unselect()
        elif self.name == 'piece' and not Piece.Selected:
            self._do_select()
        elif self.name == 'target' and Piece.Selected:
            self._do_check()
                    
    def _do_select(self):
        if self.ImSelected:
            return
        #self.logger.debug("_do_select called")
        self.ImSelected = True
        Piece.Selected = self
        # we are placed at a position by the caller
        self.org_position = self.rect.topleft
        x, y = self.rect.topleft
        self.erase_sprite()
        self.shadow.moveto((x+24, y+20))
        self.moveto((x+12, y+12))
        for s in Piece.Brothers:
            s.do_fade()
        self.shadow.display_sprite()
        self.display_sprite()
        
    def _do_unselect(self):
        if not self.ImSelected:
            return
        #self.logger.debug("_do_unselect called")
        self.ImSelected = False
        Piece.Selected.moveto(self.org_position, hide=False)
        Piece.Selected.shadow.erase_sprite()
        Piece.Selected = None
        for s in self.group_owner:
            s.image.set_alpha(255)
            s.display_sprite()
        
        
    def _do_check(self):
        #self.logger.debug("_do_check called")
        if self.correct_position == Piece.Selected.correct_position:
            #self.logger.debug('correct piece selected')
            Piece.Selected.image = Piece.Selected.org_image
            Piece.Selected.moveto(self.rect.topleft, hide=False)
            Piece.Selected.kill()
            self.kill()
            Piece.Selected.shadow.erase_sprite()
            Piece.Selected = None
            for s in self.group_owner:
                s.image.set_alpha(255)
                s.display_sprite()
            self.obs(1)
        else:
            self.obs(-1)
   
    def do_fade(self):
        """make the image a bit more transparent to let the selected piece standout more"""
        if self.ImSelected or self.name == 'target':
            return
        self.erase_sprite()
        self.image.set_alpha(80)
        self.display_sprite()
            
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
    get_name (self) must provide the activity name in english, not localized in lowercase.
    stop_timer (self) must stop any timers if any.
  """

    def __init__(self,SPGoodies):
        """SPGoodies is a class object that SP sets up and will contain references
        to objects, callback methods and observers
        TODO: add more explaination"""
        self.logger =  logging.getLogger("childsplay.puzzle.Activity")
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
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','PuzzleData')
        self.rchash = utils.read_rcfile(os.path.join(self.my_datadir, 'puzzle.rc'))
        self.rchash['theme'] = self.theme
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.CPdatadir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        self.DbAssets = os.path.join(self.SPG.get_libdir_path(),'CPData', 'DbaseAssets')
        # Location of the alphabet sounds dir
        self.absdir = self.SPG.get_absdir_path()# alphabet sounds dir
        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special CPGroup
        self.actives = SPSpriteUtils.SPInit(self.screen,self.backgr)
        self.actives.set_onematch(True)
        imgdir = os.path.join(self.my_datadir, self.theme)
        if not os.path.exists(imgdir):
            old = imgdir
            imgdir = os.path.join(self.my_datadir,'childsplay')
            self.logger.debug("not found %s using %s" % (old, imgdir))
        target_path = os.path.join(imgdir,'target.png')
        self.target_image = utils.load_image(target_path)
       
        self.gamelevels = [(2,2,10),
                           (3,2,10),
                           (3,3,10),
                           (4,3,10),
                           (4,4,10)]
        # Images must be 324x324
        # Image Size, by now these values has to be "divisibles" by 2,3,4,5,6
        self.xsize = 324
        self.ysize = 324
        
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
        return _("Puzzle")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "puzzle"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),
                _("Place the puzzle piece on the right where you think it belongs..."), 
        " ",
        _("At the bottom you'll see a image of the complete puzzle."), 
        " "]
        return text 
    
    def get_helptip(self):
        """Mandatory method, when no tips available returns an empty list"""
        return _("Look closely at the complete puzzle picture at the bottom.")
        
    def get_helptype(self):
        """Mandatory method, you must set an type"""
        # Possible types are: Memory, Math, Puzzle, Keyboardtraining, Mousetraining
        #                     Language, Alphabet, Fun, Miscellaneous
        return _("Puzzle")
    
    
    def get_helplevels(self):
        """Mandatory method, must return a string with the number of levels
        in the follwing format:
        _("This level has %s levels") % number-of-levels"""
        return _("This activity has %s levels") % 5

    
    def start(self):
        """Mandatory method."""
        # Your top blit position, this depends on the menubar position 
        self.tile = 'tileset_1'
        if self.blit_pos[1] == 0:
            self.blit_pos_y = 10
        else:
            self.blit_pos_y = 110
        self.SPG.tellcore_set_dice_minimal_level(2)
        p = os.path.join(self.CPdatadir,'good_%s.png' % self.lang)
        if not os.path.exists(p):
            p = os.path.join(self.CPdatadir,'thumbs.png')
        self.ThumbsUp = SPSpriteUtils.MySprite(utils.load_image(p))
        self.good = utils.load_music(os.path.join(self.CPdatadir, 'good1.ogg'))
        self.wrong = utils.load_music(os.path.join(self.CPdatadir, 'wrong1.ogg'))
        self.score = 0
        self.AreWeDT = False
        self.pre_level_flag = False
     
    def pre_level(self, level):
        """Mandatory method"""
        self.logger.debug("pre_level called with: %s" % level)
        if level > len(self.gamelevels):
            return
        self.pre_level_flag = True
        y = self.blit_pos_y
        
        imgdir = os.path.join(self.my_datadir, self.theme)
        if not os.path.exists(imgdir):
            imgdir = os.path.join(self.my_datadir,'childsplay')
        
        files = glob.glob(os.path.join(imgdir,'tileset_*.png'))
        files.sort()
        lbl = SPWidgets.Label(_("Please, choose a set of puzzle images."),\
                                (30, y),fsize=24, transparent=True)
        lbl.display_sprite()
        y += lbl.get_sprite_height()
        for line in textwrap.wrap(_("The difficulty of the set increases from left to right."), 40):
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
                img_ro = utils.load_image(os.path.join(imgdir, '%s_ro.png' % data))
                b = SPWidgets.SimpleTransImgButton(img, img_ro, (x, y), data=data)
                b.display_sprite()
                self.actives.add(b)
                count += 1
        return True
  
    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        if level > len(self.gamelevels):
            return
        self.level = level
        self.levelupcount = 1
        self.dbscore = 0
        Piece.Brothers = []
        # number of exercises in one level
        if self.AreWeDT:
            self.exercises = 1
        else:
            self.exercises = int(self.rchash[self.theme]['exercises'])
        
        self.totalexercises = self.exercises
        self.xoffset = 420 # space between the two puzzle areas left borders
        self.db_mapper = dbmapper
        self.rows, self.cols ,self.bonus = self.gamelevels[level-1]
        self.npieces=self.cols*self.rows
        imgdir = os.path.join(self.my_datadir, self.theme, self.tile)
        if not os.path.exists(imgdir):
            old = imgdir
            imgdir = os.path.join(self.my_datadir,'childsplay', self.tile)
            self.logger.debug("not found %s using %s" % (old, imgdir))
        self.logger.debug("Using imagedir %s" % imgdir)
        self.pzimages = glob.glob(os.path.join(imgdir,'*.jpg'))
        random.shuffle(self.pzimages)
        self.logger.debug("Found %s images" % len(self.pzimages))
        # store number of cards into the db table 'cards' col
        self.db_mapper.insert('total_pieces',self.npieces)
        # bonusp is the score for each piece put in its place
        self.bonusp=self.bonus/self.npieces
        # size of a piece
        self.incx=self.xsize/self.cols
        self.incy=self.ysize/self.rows
        self.clear_screen()
        self.next_exercise()

        return True
    
    
    
    def dailytraining_pre_level(self, level):
        """Mandatory method"""
        # TODO: it's hardcoded, for 2.2 we must have it in the rcfile
        self.tile = 'tileset_1'

    def dailytraining_next_level(self, level, dbmapper):
        """Mandatory method.
        This should handle the DT logic"""
        self.AreWeDT = True
        self.SPG.tellcore_disable_level_indicator()
        self.next_level(level, dbmapper)
        return True
    
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
        # M = Maximum score (number of pieces * total images)
        # P = Users result in points
        # F = Fraction of total result related to points. (maximum result is 10)
        # F1 = Fraction of result related to time
        # C = multiplier
        # S = time spend in seconds
        M = float(self.npieces * self.totalexercises)
        P = float(self.dbscore)
        F = 7.0
        F1 = 3.0
        C = 0.2
        S = float(seconds)
        points = max((F/100) * (P/(M / 100)), 1.0)
        time = min(F1 / ((S / (M * 2)) ** C), F1)
        self.logger.info("@scoredata@ %s level %s M %s P %s S %s points %s time %s" % \
                         (self.get_name(),self.level, M, P, S, points, time))
        score = points + time
        result = points + time
        return result
        
    
    def stop_timer(self):
        """You *must* provide a method to stop timers if you use them.
        The SPC will call this just in case and catch the exception in case 
        there's no 'stop_timer' method""" 
        try:
            self.timer.stop()
        except:
            pass

    def score_observer(self, score):
        if score < 0:
            self.wrong.play()
        else:
            self.good.play()
        self.score += score * 10
        self.dbscore += score
        if self.score <= 0:
            self.score = 10
        if score > 0:
            # correct answer
            self.levelupcount += 1
        else:
            self.levelupcount -= 1

    def loop(self,events):
        """Mandatory method.
        This is the main eventloop called by the core 30 times a minute."""
        for event in events:
            if event.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION):
                result = self.actives.update(event)
                if self.pre_level_flag:
                    if result:
                        self.logger.debug("loop, got a result and stop this loop")
                        self.SPG.tellcore_pre_level_end()
                        self.pre_level_flag = False
                        self.tile = result[0][1][0]
                        break
                if not self.actives:
                    self.scoredisplay.set_score(self.score*3)
                    pygame.time.wait(int(self.rchash[self.theme]['wait_value']))
                    self.clear_screen()
                    self.ThumbsUp.display_sprite((229, 120))
                    pygame.time.wait(1000)
                    self.ThumbsUp.erase_sprite()
                    if self.next_exercise():
                        self.logger.debug("%s" % self.level)
                        if self.level<5 and self.levelupcount >= int(self.rchash[self.theme]['autolevel_value']):
                            levelup = 1
                        else:
                            levelup = 0
                        if self.AreWeDT:
                            self.SPG.tellcore_level_end(level=self.level)
                        else:
                            self.SPG.tellcore_level_end(store_db=True, \
                                                level=min(6, self.level), \
                                                levelup=levelup)
        return 
     
    def next_exercise(self):
        self.logger.debug("next_exercise called, exercises = %s" % (self.exercises))
        
        self.actives.purge()# remove sprites from previous exercise and erase them
        if not self.exercises:
            return True
        else:
            self.load_puzzle()
            self.ok=[0]*len(self.actives)
            for s in self.actives:
                s.display_sprite()
            pygame.display.update()
            self.puzzlethumb.display_sprite((INIXTH-20,INIYTH+self.blit_pos_y-50))
            self.exercises -= 1
  
    def load_puzzle(self):
        """  Load an image to split, it choose one between the images in
         myimages folder and the childsplay images.
        """
        imgpath = self.pzimages.pop()
        image=utils.load_image(imgpath)
        img = utils.aspect_scale(image.convert(),(140,140))
        self.puzzlethumb = SPSpriteUtils.MySprite(img)
        positions=[] 
        self.pieceslist = []
                
        # Split the surfaces in pieces
        sc = 324 / (self.npieces/2)
        target_image = utils.aspect_scale(self.target_image, (sc, sc))
        ix=0
        px=self.incx*ix
        while px<self.xsize:
            iy=0
            py=self.incy*iy
            while py<self.ysize:
                position = (INIX+px,self.blit_pos_y+INIY+py)
                positions.append(position)
                r = pygame.Rect((px,py),(self.incx,self.incy))
                try:
                    piece=image.subsurface(r)
                except ValueError:
                    self.logger.debug("Failed to get a subsurface, image has wrong size %s" % imgpath)
                piece=Piece(piece, position,self.score_observer, name='piece')
                self.pieceslist.append(piece)
                s = pygame.Surface((r.w, r.h))
                s.fill(WHITE)
                s.blit(target_image, ((r.w - target_image.get_rect().w) / 2, \
                                       (r.h - target_image.get_rect().h) / 2))
                target = Piece(s, position, self.score_observer, name='target')
                target.moveto((position[0]+self.xoffset, position[1]))
                self.actives.add(target)
                iy=iy+1
                py=self.incy*iy
            ix=ix+1
            px=self.incx*ix
        
        self.org_positions=positions[:]
        while positions == self.org_positions:
            random.shuffle(positions)
            
        for s in self.pieceslist:
            s.moveto(positions.pop(0))
        self.actives.add(self.pieceslist)
        
        return

    
    
