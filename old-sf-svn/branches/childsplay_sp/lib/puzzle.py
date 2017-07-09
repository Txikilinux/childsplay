# -*- coding: utf-8 -*-

# Copyright (c) 2006 Miguel Pérez Francisco <mperez@icc.uji.es>
# Copyright (c) 2008 Stas Zytkiewicz stas.zytkiewicz@gmail.com
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
# self.logger =  logging.getLogger("schoolsplay.puzzle.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("schoolsplay.puzzle")

# standard modules you probably need
import os,sys,random,glob

import pygame
from pygame.constants import *

import childsplay_sp.utils as utils
from childsplay_sp.SPConstants import *
import childsplay_sp.SPSpriteUtils as SPSpriteUtils

########################################
# Constats definition
########################################

# Position of the splitted image
INIX=20
INIY=20

# Position of the target image
INIXF=450
INIYF=20

# Offset between the position of the mouse and the piece being translated
OFFSETIMGX=30
OFFSETIMGY=30

# Size of the lines between pieces
TAMLINEA=2

#Position of the thumbnail of the image
INIXTH,INIYTH=350,400

# containers that can be used globally to store stuff
class Img:
    pass
class Snd:
    pass
class Misc:
    score = 0
    
class Piece(pygame.sprite.Sprite):
    """ A piece of a puzzle """
    def __init__(self,image):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image = image
        self.rect = image.get_rect()
        
    def update(self):
        "move the image based on the mouse position"
        pos = pygame.mouse.get_pos()
        self.rect.midtop = pos

    def set_position(self,pos):
        self.rect.move_ip(pos)
        
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
        self.logger =  logging.getLogger("schoolsplay.puzzle.Activity")
        self.logger.info("Activity started")
        self.SPG = SPGoodies
        self.screen = self.SPG.get_screen()
        self.backgr = self.SPG.get_background()
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','PuzzleData')
        self.sounddir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        # You MUST call SPInit BEFORE using any of the SpriteUtils stuff
        # it returns a reference to the special CPGroup
        self.actives = SPSpriteUtils.SPInit(self.screen,self.backgr)
        
        try:
            self.myimages = glob.glob(os.path.join(HOMEIMAGES,'my_images','*'))
        except Exception,info:
            self.logger.debug("No 'my_images' found:%s" % info)
            self.myimages = []
        else:
            self.logger.debug("my_images found: %s" % self.myimages)
            if len(self.myimages) < 10:
                self.logger.debug("Not enough images found, must be at least 10")
                self.logger.debug("Loading default images")
                try:
                    self.pzimages = glob.glob(os.path.join(self.my_datadir,'*.png'))
                except Exception:
                    self.logger.exception("No puzzle images found?!")
                    raise utils.MyError
                else:
                    self.logger.debug("puzzle images found: %s" % self.pzimages)
            else:
                self.pzimages = self.myimages
        
        self.pressed = 0
        self.pieceselected = None
        self.bonus = 0
        self.gamelevels = [(2,2,10),
                           (3,2,10),
                           (3,3,10),
                           (4,3,10),
                           (4,4,10)]
    
        # Image Size, by now these values has to be "divisibles" by 2,3,4,5,6
        self.xsize = 324
        self.ysize = 324
        

    ################# Code from old childsplay puzzle ##################
    def load_puzzle(self):
        """  Load an image to split, it choose one between the images in
         myimages folder and the childsplay images.
        """
        # Select the image to split, choose one between the images in
        # myimages folder and the childsplay images
        imn=random.randint(0,len(self.pzimages)-1)
        self.image=utils.load_image(self.pzimages[imn])
        # We upscale if image is less then 324x324
        # Upscaling sucks so all the CP images are 324x324.
        # It's possible that the user provided images are smaller
        if self.image.get_width < self.xsize or self.image.get_height < self.ysize:
            self.logger.debug("Scaling image from %sx%s to %sx%s" % (self.image.get_width, \
                                                                     self.image.get_height, \
                                                                     self.xsize, \
                                                                     self.ysize))
            self.image=pygame.transform.scale(self.image,(self.xsize,self.ysize))

        self.pieces=[]
        self.posiciones=[] # The position of each pieze

        # Split the surface in pieces
        ix=0
        px=self.incx*ix
        while px<self.xsize:
            iy=0
            py=self.incy*iy
            while py<self.ysize:
                self.posiciones.append((INIX+px,INIY+py))
                pieze=self.image.subsurface(pygame.Rect((px,py),(self.incx,self.incy)))
                pieze=Piece(pieze)
                self.pieces.append(pieze)
                iy=iy+1
                py=self.incy*iy
            ix=ix+1
            px=self.incx*ix
                
        random.shuffle(self.posiciones)
        self.posicionesoriginales=self.posiciones[:]

        # TODO: Use sprites and groups with the draw method to draw
        # only the moved parts
        # self.allsprites = pygame.sprite.RenderPlain(self.pieces)

        return

    def create_puzzle(self):
        """ Loads an image and split it"""

        self.load_puzzle()
        self.ok=[0]*len(self.pieces)

        # Create a thumbnail of the image
        # TODO: scale the thumbnail in relation to the image size  
        self.puzzlethumb=pygame.transform.scale(self.image,(75,100))

        self.refresh_screen(100)
    
    def refresh_screen(self,retardo=None):
        """ Draw the all the parts of the game"""

        #TODO: Update only the parts that have been moved, with
        #sprites and groups

        # Draw the background
        self.screen.blit(self.backgr,(0,0))

        # Draw the thumbnail 
        self.screen.blit(self.puzzlethumb,(INIXTH,INIYTH))

        # Draw the contour of the target pieces 
        pygame.draw.rect(self.screen,(0,0,0),pygame.Rect(INIXF,INIYF,self.xsize,self.ysize),TAMLINEA)
        for rows in range(1,self.rows):
            pygame.draw.rect(self.screen,(0,0,0),pygame.Rect(INIXF,INIYF+(self.incy)*rows,self.xsize, TAMLINEA),TAMLINEA)
        for cols in range(1,self.cols):
            pygame.draw.rect(self.screen,(0,0,0),pygame.Rect(INIXF+(self.incx)*cols,INIYF,TAMLINEA,self.ysize),TAMLINEA)

        # Draw the pieces  
        i=0
        ix=0
        iy=0        
        for pieze in self.pieces:
            self.screen.blit(pieze.image, self.posiciones[i])
            iy+=1
            if iy==self.rows:
                iy=0
                ix+=1
            i=i+1
            #TODO: 
            #if retardo is not None:
            #    pygame.time.wait(retardo)
            #    pygame.display.update((self.posiciones[i][0],self.posiciones[i][1],self.incx,self.incy))
                

        # Draw the contour of the source pieces 
        pygame.draw.rect(self.screen,(0,0,0),pygame.Rect(INIX,INIY,self.xsize,self.ysize),TAMLINEA)
        for rows in range(1,self.rows):
            pygame.draw.rect(self.screen,(0,0,0),pygame.Rect(INIX,INIY+(self.incy)*rows,self.xsize, TAMLINEA),TAMLINEA)
        for cols in range(1,self.cols):
            pygame.draw.rect(self.screen,(0,0,0),pygame.Rect(INIX+(self.incx)*cols,INIY,TAMLINEA,self.ysize),TAMLINEA)
            
        # Draw the selected pieze so it appears always on top
        if self.pieceselected is not None:
            self.screen.blit(self.pieces[self.pieceselected].image,
                             self.posiciones[self.pieceselected])
        
        pygame.display.update()

    def put_piece_in_original_place(self,np):
        """ put a piece in its original place """
        self.posiciones[np]=self.posicionesoriginales[np]
        
    def put_piece_in_target_place(self,np):
        """put a piece in its target place """
        ix=np/self.rows
        iy=np%self.rows
        self.posiciones[np]=(INIXF+ix*(self.incx),
                             INIYF+iy*(self.incy))
        
    def is_in_target_place(self,targetpos,np):
        """ return true if the targetpos position is inside the target place."""
        ix=np/self.rows
        iy=np%self.rows

        targetrect=pygame.Rect((INIXF+ix*(self.incx),
                               INIYF+iy*(self.incy)),
                               (self.incx,self.incy))
        self.ok[np]=1
       
        return targetrect.collidepoint((targetpos[0]+self.offsetimgx,targetpos[1]+self.offsetimgy))


    ################### End old code ################################
    
    def get_helptitle(self):
        """Mandatory method"""
        return _("Puzzle")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "puzzle"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity"),
        _("Put all the pieces in the correct order.")]
        return text 
    
    def get_helptip(self):
        """Mandatory method, when no tips available returns an empty string"""
        text = [_("You can add your own images by placing them in the following directory: "),
        "%s" % HOMEIMAGES,
        " "]
        return text
        
    def get_helptype(self):
        """Mandatory method, you must set an type"""
        # Possible types are: Memory, Math, Puzzle, Keyboardtraining, Mousetraining
        #                     Language, Alphabet, Fun, Miscellaneous
        return _("Puzzle")
    
    def get_helplevels(self):
        """Mandatory method, must return a string with the number of levels
        in the follwing format:
        _("This level has %s levels" % number-of-levels)"""
        return _("This activity has %s levels") % 5
    
    def start(self):
        """Puzzle game"""
        self.bummer = utils.load_sound(os.path.join(self.sounddir,'bummer.wav'))
        self.wahoo = utils.load_sound(os.path.join(self.sounddir,'wahoo.wav'))
        
    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        self.logger.debug("next_level called with %s" % level)
        if level > 5: return False # We only have 6 levels
        # number of exercises in one level
        self.exercises = 5 # CHANGE BACK TO 5 after testing   
        # db_mapper is a Python class object that provides easy access to the 
        # dbase.
        self.db_mapper = dbmapper
                
        self.score = 0
        self.rows, self.cols ,self.bonus = self.gamelevels[level-1]
        self.npieces=self.cols*self.rows
        
        # store number of cards into the db table 'cards' col
        self.db_mapper.insert('pieces',self.npieces)
        
        # bonusp is the score for each piece put in its place
        self.bonusp=self.bonus/self.npieces
        # size of a piece
        self.incx=self.xsize/self.cols
        self.incy=self.ysize/self.rows
        #TODO: Control that the previous two divisions are exact
        self.next_exercise()
        #TODO: A button to advance in level. This should affect to the bonus???
        return True
    
    def next_exercise(self):
        self.logger.debug("next_exercise called, exercises = %s" % (self.exercises))
        if not self.exercises:
            # we call the SPGoodies observer to notify the core the level
            # is ended and we want to store the collected data
            self.SPG.tellcore_level_end(store_db=True)
        else:
            self.exercises -= 1
            self.create_puzzle()
    
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
        m,s = timespend.split(':')
        seconds = int(m)*60 + int(s)
        score = max(1,self.score - seconds/100.0)
        
        self.logger.debug("score is: %s" % score)
        return score
        
    def loop(self,events):
        """Mandatory method.
        This is the main eventloop called by the core 30 times a minute."""
        self.score = 0

        oka=0
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
              # if a piece was selected
              if self.pressed:
                self.pressed=0
                targetpos=self.posiciones[self.pieceselected]
                if not(self.is_in_target_place(targetpos,self.pieceselected)):
                    self.bummer.play()
                    self.bonus=self.bonus-self.bonusp
                    self.put_piece_in_original_place(self.pieceselected)
                else:
                    self.score=self.bonusp
                    self.put_piece_in_target_place(self.pieceselected)
                    
                    oka=1
                    for i in range(self.npieces):
                        oka=oka*self.ok[i]
                        
              # if a piece was not selected, select it if it is on the
              # source board
              else:
                pos_mouse=pygame.mouse.get_pos() 

                findpiece=0
                acpiece=0
                aux=0
                while (not findpiece and acpiece<len(self.pieces)):
                    if pygame.Rect(self.posiciones[acpiece],
                                   (self.incx,self.incy)).collidepoint(pos_mouse):
                        #mouse position
                        pos_mouse=pygame.mouse.get_pos()
                        self.pieceselected=acpiece

                        self.offsetimgx=pos_mouse[0]-self.posiciones[self.pieceselected][0]
                        self.offsetimgy=pos_mouse[1]-self.posiciones[self.pieceselected][1]

                        mousex=pos_mouse[0]-self.offsetimgx
                        mousey=pos_mouse[1]-self.offsetimgy
                        aux=acpiece
                        findpiece=1
                    else:
                        acpiece=acpiece+1
                        
                # Test if the piece is on the original position
                if findpiece and pygame.Rect((INIX,INIY),(self.xsize,self.ysize)).collidepoint(pos_mouse):
                    self.pressed=1
                    self.posiciones[self.pieceselected]=((mousex,mousey))

        if self.pressed==1:
            pos_mouse=pygame.mouse.get_pos() 
            mousex=pos_mouse[0]-self.offsetimgx
            mousey=pos_mouse[1]-self.offsetimgy
            self.posiciones[self.pieceselected]=((mousex,mousey))
            #print self.posiciones[self.pieceselected]
            #print self.pressed
        
        self.refresh_screen()

        if oka:
            # all the pieces are correctly placed
            self.score = self.bonus
            self.logger.debug("bonus: %s" % self.score)
            self.wahoo.play()
            pygame.time.wait(1500)
            self.next_exercise()
        
        Misc.score =+ self.score
        return 
        
