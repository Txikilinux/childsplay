# -*- coding: utf-8 -*-

# Copyright (c) 2011 Stas Zytkiewicz stas.zytkiewicz@schoolsplay.org
#
# Code is taken from 
#   http://inventwithpython.com/blog/2011/06/10/new-game-source-code-four-in-a-row
# 
# Graphical Four-In-A-Row (a Connect Four clone)
# http://inventwithpython.com/blog
# By Al Sweigart al@inventwithpython.com
#
#           fourrow.py
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
# self.logger =  logging.getLogger("childsplay.fourrow.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("childsplay.fourrow")

# standard modules you probably need
import os,sys
import random
import copy
import pygame
from pygame.constants import *

import utils
from SPConstants import *
import SPSpriteUtils

from SPWidgets import Label, ButtonDynamic

BOARDWIDTH = 7  # how many spaces wide the board is
BOARDHEIGHT = 6 # how many spaces tall the board is
PILSIZE = 70
class Pil(SPSpriteUtils.SPSprite):
    def __init__(self, image, pos,id):
        SPSpriteUtils.SPSprite.__init__(self,image,id)
        self.moveto(pos)
        
class Tile(SPSpriteUtils.SPSprite):
    def __init__(self, image, pos):
        SPSpriteUtils.SPSprite.__init__(self,image,id)
        self.moveto(pos)
        
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
        self.logger =  logging.getLogger("childsplay.fourrow.Activity")
        self.logger.info("Activity started")
        self.SPG = SPGoodies
        self.lang = self.SPG.get_localesetting()[0][:2]
        self.scoredisplay = self.SPG.get_scoredisplay()
        self.theme = self.SPG.get_theme()
        self.screen = self.SPG.get_screen()
        self.screenclip = self.SPG.get_screenclip()
        self.windowSurf = self.screen
        self.blit_pos = self.screenclip.left, self.screenclip.top
        self.orgscreen = pygame.Surface(self.screenclip.size) # we use this to restore the screen
        self.orgscreen.blit(self.screen, (0, 0), self.screenclip)
        self.backgr = self.SPG.get_background()
        # The location of the activities Data dir
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','FourrowData')
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.CPdatadir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        # Location of the alphabet sounds dir
        self.absdir = self.SPG.get_absdir_path()# alphabet sounds dir
        self.rchash = utils.read_rcfile(os.path.join(self.my_datadir, 'fourrow.rc'))
        self.logger.debug("rchash: " + str(self.rchash))
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
        #self.actives.refresh()

    def get_helptitle(self):
        """Mandatory method"""
        return _("Fourrow")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "fourrow"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),
        _("Try to get four in a row in any possible direction."),
        " ", 
        _("You can vertically drop a red pill in a desired column by pressing that exact column."),
        _("All pills, both red and yellow, stack on each other."), 
        _("To win the game you'll need four red pills lined up after each other horizontally, vertically or diagonal."), 
        _("Tip: Try creating multiple winning scenario's."), 
        " "]
        return text 
    
    def get_helptip(self):
        """Mandatory method, when no tips available returns an empty list"""
        return []
        
    def get_helptype(self):
        """Mandatory method, you must set an type"""
        # Possible types are: Memory, Math, Puzzle, Keyboardtraining, Mousetraining
        #                     Language, Alphabet, Fun, Miscellaneous
        return _("Puzzle")
    def stop(self):
        """Mandatory method, will be called by the core when this activities is destroyed."""
        try:
            self.winSnd.stop()
            self.lossSnd.stop()
        except:
            pass
            
    def start(self):
        """Mandatory method."""
    
        img = utils.load_image(os.path.join(self.my_datadir,'4row_red.png'))
        self.spacesize = PILSIZE
        self.RedImg = pygame.transform.smoothscale(img, (self.spacesize, self.spacesize))
        
        img = utils.load_image(os.path.join(self.my_datadir,'4row_black.png'))
        self.BlackImg = pygame.transform.smoothscale(img, (self.spacesize, self.spacesize))
        
        img = utils.load_image(os.path.join(self.my_datadir,'4row_board.png'))
        img = pygame.transform.smoothscale(img, (self.spacesize, self.spacesize))
        self.boardImg = img
        
        self.gameClock = pygame.time.Clock()# tobe removed
        self.draggingToken = False
        self.tokenx, self.tokeny = None, None
        
        row = self.SPG.get_current_user_dbrow()
        user_id = self.SPG.get_current_user_id()
        UserImg = None
        offset = 0
        if user_id > 1:# demo is 1
            p = os.path.join(HOMEDIR, 'braintrainer', 'faces', 'big', '%s.png' % user_id)
            if os.path.exists(p):
                UserImg = utils.aspect_scale(utils.load_image(p), (125,125))
                offset = 12
        if not UserImg:
            st = utils.char2surf(row.first_name, 20, fcol=BLACK)
            sn =  utils.char2surf(row.last_name, 20, fcol=BLACK)
            surf = pygame.Surface((150,80), SRCALPHA, 32)
            surf.blit(st,(8,4))
            surf.blit(sn, (8,30))  
            UserImg = surf
        self.UserImg = SPSpriteUtils.SPSprite(UserImg)
        surf = UserImg.copy()
        pygame.draw.rect(surf, GREEN, UserImg.get_rect(), 10)
        self.TurnImgUser = SPSpriteUtils.SPSprite(surf)
        
        AIimg = utils.load_image(os.path.join(self.my_datadir,'computer.png'))
        self.AIimg = SPSpriteUtils.SPSprite(AIimg)
        surf = AIimg.copy()
        pygame.draw.rect(surf, GREEN, AIimg.get_rect(), 10)
        self.TurnAIimg = SPSpriteUtils.SPSprite(surf)
        
        self.WinnerImg = utils.load_image(os.path.join(self.my_datadir,'winner.png'))
        
        self.numbershash = {}
        for i in range(1, BOARDWIDTH+1):
            self.numbershash[i] = utils.load_image(os.path.join(self.my_datadir,'%s.png' % i))
        
        # sounds
        
        self.winSnd = utils.load_music(os.path.join(self.my_datadir,'won.ogg'))
        self.lossSnd = utils.load_music(os.path.join(self.my_datadir,'loss.ogg'))             
               
        # various constants
        self.FPS = 30 # frames per second to update the screen
        WINDOWWIDTH = 800 # width of the program's window, in pixels
        WINDOWHEIGHT = 600 # height in pixels
        
        self.XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * self.spacesize) / 2) # approx. number of pixels on the left or right side of the board to the edge of the window
        self.YMARGIN = int((WINDOWHEIGHT - BOARDHEIGHT * self.spacesize) / 2 + 80) # approx. number of pixels above or below board
        
        self.REDpos = (self.XMARGIN - self.spacesize * 2, self.YMARGIN + (BOARDHEIGHT - 1) * self.spacesize)
        self.BLACKpos = (self.XMARGIN + BOARDWIDTH * self.spacesize + self.spacesize, self.YMARGIN + (BOARDHEIGHT - 1) * self.spacesize)
        self.UserImgpos = (2 + offset, 380)
        self.UserImg.moveto(self.UserImgpos)
        self.TurnImgUser.moveto(self.UserImgpos)
        self.AIimgpos = (660, 380)
        self.AIimg.moveto(self.AIimgpos)
        self.TurnAIimg.moveto(self.AIimgpos)
        self.winner = 'tie'
        self.difficulty = 1# never more then 2, system will freeze
        self.AreWeDT = False
    
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
        
        self.isFirstGame = True
        self.level = level
        
        self.next_exercise()
        return True
        
    def next_exercise(self, *args):
        # build board
        self.clear_screen()
        self.actives.empty()
        self.Tiles = {} 
        self.old_pil_rect = None
        # draw board and the tokens
        for x in range(BOARDWIDTH):
            posx = self.XMARGIN + (x * self.spacesize)
            #palceholder for special trans numbers
            self.screen.blit(self.numbershash[x+1], (posx, self.YMARGIN))
            for y in range(BOARDHEIGHT):
                posy = self.YMARGIN + (y * self.spacesize)
                tile = Tile(self.boardImg, (posx, posy))
                tile.connect_callback(self._cbf_Tile, MOUSEBUTTONDOWN, (posx, posy))
                if not self.Tiles.has_key(posx):
                    self.Tiles[posx] = []
                self.Tiles[posx].append(tile)
                tile.display_sprite()
                self.actives.add(tile)
        self.backgr.blit(self.screen,self.blit_pos, self.screenclip)
        self.UserImg.display_sprite()
        self.AIimg.display_sprite()
#        self.screen.blit(self.RedPil, self.REDpos)
#        self.screen.blit(self.BlackPil, self.BLACKpos)
        Pil(self.RedImg, self.REDpos,'red').display_sprite()
        Pil(self.BlackImg, self.BLACKpos, 'black').display_sprite()
        
        pygame.display.update()
        
        if self.isFirstGame:
            self.turn = 'computer'
            self.isFirstGame = False
        else:
            self.turn = random.choice(['computer', 'human'])
        if self.turn == 'computer':
            self.AIimg.erase_sprite()
            self.TurnAIimg.display_sprite()
        else:
            self.UserImg.erase_sprite()
            self.TurnImgUser.display_sprite()
        self.firstmove = True
        self.mainBoard = self.getNewBoard()
        
    def _cbf_Tile(self, event, widget, data):
        if self.turn != 'human':
            return
        self.logger.debug("human turn")
        x = data[0][0]
        column = int((x - self.XMARGIN) / self.spacesize)
        if self.isValidMove(self.mainBoard, column):
            self.animateDroppingToken(self.mainBoard, column, 'red')
            self.mainBoard[column][self.getLowestFreeSpace(self.mainBoard, column)] = 'red'
            self.old_pil_rect = None
            if self.isWinner(self.mainBoard, 'red'):
                self.winner = 'user'
            self.turn = 'computer'
            self.TurnImgUser.erase_sprite()
            self.UserImg.display_sprite()
            self.TurnAIimg.display_sprite()
        return -1
                            
    def makeMove(self, board, player, column):
        lowest = self.getLowestFreeSpace(board, column)
        if lowest != -1:
            board[column][lowest] = player
    
    def getNewBoard(self):
        board = []
        for x in range(BOARDWIDTH):
            board.append([None] * BOARDHEIGHT)
        return board
        
    def animateDroppingToken(self, board, column, color):
        x = self.XMARGIN + column * self.spacesize
        y = self.YMARGIN - self.spacesize
        speed = 10
        dirty = []
        lowestFreeSpace = self.getLowestFreeSpace(board, column)
        RedPil = Pil(self.RedImg, (x,y),'red')
        BlackPil = Pil(self.BlackImg, (x,y), 'black')
        while True:
            y += int(speed)
            if (y - self.YMARGIN - speed) / self.spacesize >= lowestFreeSpace:
                if self.Tiles[x]:
                    self.Tiles[x].pop()
                return
#            if self.old_pil_rect:
#                self.screen.blit(self.backgr, self.old_pil_rect.topleft, self.old_pil_rect)
            for t in self.Tiles[x]:
                self.screen.blit(self.backgr,t.rect, t.rect)
#            pygame.display.update(dirty)
            if color == 'black':
                BlackPil.undraw_sprite()
                BlackPil.draw_sprite((x,y))
#                r= self.screen.blit(self.BlackPil, (x,y))
            else:
                RedPil.undraw_sprite()
                RedPil.draw_sprite((x,y))
#                r = self.screen.blit(self.RedPil, (x,y))
#            self.old_pil_rect = r
#            pygame.display.update(r)
            if self.Tiles.has_key(x):
                dirty = []
                for t in self.Tiles[x]:
                    self.screen.blit(t.image,t.rect)
#                pygame.display.update(dirty)
            pygame.display.flip()
            self.gameClock.tick(self.FPS)
            
        
    def getComputerMove(self, board):
        if self.isBoardFull(board):
            self._show_winner()
        if self.firstmove and self.level > 2:
            # Added intelligent, we check if we can place in the middle, even when the user
            # placed one stone, at least we will block his attempt
            # we disable this for the first two levels
            self.firstmove = False
            cl =[]
            if self.isValidMove(board, 3):
                cl.append(3)
            if self.isValidMove(board, 4):
                cl.append(4)
            if cl:
                return random.choice(cl)
        # make lower levels easier
        if self.level == 1:
            return self.getRandomMove(0)
        elif self.level == 2:
            return self.getRandomMove(4)
        elif self.level in (3,4):
            self.difficulty = 1
            return self.getRandomMove(7)
        elif self.level == 5:
            self.difficulty = 1
            return self.getRandomMove(-1)
        else:
            self.difficulty = 2
            return self.getRandomMove(-1)
    
    def getRandomMove(self, level):
        """The higher the level, max 7, the less random it is.
        ex. 5 means a chance of 1 out of 5 to get a random move.
        -1 means no random move"""
        # first we determine which moves are legal
        legalmoves = [i for i in range(BOARDWIDTH) if self.isValidMove(self.mainBoard, i)]
        if level == 0 or level != -1 and random.randrange(level) == 0:# random move
            return random.choice(legalmoves)
        
        potentialMoves = self.getPotentialMoves(self.mainBoard, 'black', self.difficulty)
        bestMoveScore = max([potentialMoves[i] for i in range(BOARDWIDTH) if self.isValidMove(self.mainBoard, i)])
        bestMoves = []
        for i in range(len(potentialMoves)):
            if potentialMoves[i] == bestMoveScore and self.mainBoard[i][0] == None:
                bestMoves.append(i)
        return random.choice(bestMoves)
        
    def getPotentialMoves(self, board, playerTile, lookAhead):
        if lookAhead == 0 or self.level ==1:
            return [0] * BOARDWIDTH
    
        potentialMoves = []
    
        if playerTile == 'red':
            enemyTile = 'black'
        else:
            enemyTile = 'red'
    
        # Returns (best move, average condition of this state)
        if self.isBoardFull(board):
            return [0] * BOARDWIDTH
             
        # Figure out the best move to make.
        potentialMoves = [0] * BOARDWIDTH
        for playerMove in range(BOARDWIDTH):
            dupeBoard = copy.deepcopy(board)
            if not self.isValidMove(dupeBoard, playerMove):
                continue
            self.makeMove(dupeBoard, playerTile, playerMove)
            if self.isWinner(dupeBoard, playerTile):
                potentialMoves[playerMove] = 1
                break
            else:
                # do other player's moves and determine best one
                if self.isBoardFull(dupeBoard):
                    potentialMoves[playerMove] = 0
                else:
                    for enemyMove in range(BOARDWIDTH):
                        dupeBoard2 = copy.deepcopy(dupeBoard)
                        
                        if not self.isValidMove(dupeBoard2, enemyMove):
                            continue
                        self.makeMove(dupeBoard2, enemyTile, enemyMove)
                        if self.isWinner(dupeBoard2, enemyTile):
                            potentialMoves[playerMove] = -1
                            break
                        else:
                            results = self.getPotentialMoves(dupeBoard2, playerTile, lookAhead - 1)
                            potentialMoves[playerMove] += (sum(results) / BOARDWIDTH) / BOARDWIDTH                   
        return potentialMoves
    
    
    def getLowestFreeSpace(self, board, column):
        for y in range(BOARDHEIGHT-1, -1, -1):
            if board[column][y] == None:
                return y
        return -1
    
    def isValidMove(self, board, move):
        if move < 0 or move >= (BOARDWIDTH):
            return False
        if board[move][0] != None:
            return False
        return True
    
    
    def isBoardFull(self, board):
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                if board[x][y] == None:
                    return False
        return True
    
    
    def isWinner(self, board, tile):
        # check horizontal spaces
        for y in range(BOARDHEIGHT):
            for x in range(BOARDWIDTH - 3):
                if board[x][y] == tile and board[x+1][y] == tile and board[x+2][y] == tile and board[x+3][y] == tile:
                    return True
    
        # check vertical spaces
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT - 3):
                if board[x][y] == tile and board[x][y+1] == tile and board[x][y+2] == tile and board[x][y+3] == tile:
                    return True
    
        # check / diagonal spaces
        for x in range(BOARDWIDTH - 3):
            for y in range(3, BOARDHEIGHT):
                if board[x][y] == tile and board[x+1][y-1] == tile and board[x+2][y-2] == tile and board[x+3][y-3] == tile:
                    return True
    
        # check \ diagonal spaces
        for x in range(BOARDWIDTH - 3):
            for y in range(BOARDHEIGHT - 3):
                if board[x][y] == tile and board[x+1][y+1] == tile and board[x+2][y+2] == tile and board[x+3][y+3] == tile:
                    return True
        return False
    
    def _show_winner(self):
        self.turn = None
        if self.winner == 'tie':
            self.TurnAIimg.erase_sprite()
            self.AIimg.display_sprite()
            self.TurnImgUser.erase_sprite()
            self.UserImg.display_sprite()
            pos = (self.UserImgpos[0], self.UserImgpos[1] - 50)
            SPSpriteUtils.SPSprite(self.WinnerImg.copy()).display_sprite((pos[0], pos[1] - 150))
            pos = (self.AIimgpos[0], self.AIimgpos[1] - 50)
            SPSpriteUtils.SPSprite(self.WinnerImg.copy()).display_sprite((pos[0], pos[1] - 150))
        else:
            self.TurnAIimg.erase_sprite()
            self.AIimg.display_sprite()
            self.TurnImgUser.erase_sprite()
            self.UserImg.display_sprite()
            pos = {'user':(self.UserImgpos[0], self.UserImgpos[1] - 50), \
                   'computer':(self.AIimgpos[0], self.AIimgpos[1] - 50)}[self.winner]
            SPSpriteUtils.SPSprite(self.WinnerImg).display_sprite((pos[0], pos[1] - 150))
            if self.winner == 'user':
                self.scoredisplay.increase_score(100)
                self.winSnd.play()
            elif self.winner =='tie':
                self.scoredisplay.increase_score(50)
            else:
                self.lossSnd.play()
        self.turn = 'restart'# this will cause the eventloop to call _restart
        
    def _restart(self):
        self.actives.empty()
        if self.winner == 'user':
            txt = _("Congratulations, try again ?")
        else:
            txt = _("Pity, try again ?")
        but = ButtonDynamic(txt, (250,110), fgcol=WHITE)
        but.connect_callback(self.next_exercise, MOUSEBUTTONUP)
        but.display_sprite()
        self.actives.add(but)
        
    def dailytraining_pre_level(self, level):
        """Mandatory method"""
        pass
        
    def dailytraining_next_level(self, level, dbmapper):
        """Mandatory method.
        This should handle the DT logic"""
        self.isFirstGame = True
        self.level = level
        self.AreWeDT = True
        self.next_exercise()
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
        if self.winner == 'user':
            return 100
        else:
            return 10
    
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
        if not self.turn:
            for event in events:
                if event.type in (MOUSEBUTTONUP, MOUSEMOTION):
                    self.actives.update(event)
        elif self.isBoardFull(self.mainBoard):
            self.winner = 'tie'
            self._show_winner()
            
        if self.turn == 'restart':
            self.turn = None
            if self.AreWeDT:
                self.SPG.tellcore_level_end(level=self.level)
            else:
                self._restart()
            
        if self.turn == 'human':
            for event in events:
                if event.type is MOUSEBUTTONDOWN:
                    self.actives.update(event)
                                    
            if self.isWinner(self.mainBoard, 'red'):
                self.winner = 'user'
                self._show_winner()
            elif self.isBoardFull(self.mainBoard):
                self.winner = 'tie'
                self._show_winner()
                
        if self.turn == 'computer':
            self.logger.debug("computer turn")
            # computer move runs in a loop of it's own
            column = self.getComputerMove(self.mainBoard)            
            self.animateDroppingToken(self.mainBoard, column, 'black')
            self.makeMove(self.mainBoard, 'black', column)
            if self.isWinner(self.mainBoard, 'black'):
                self.winner = 'computer'
                self._show_winner()
            elif self.isBoardFull(self.mainBoard):
                self.winner = 'tie'
                self._show_winner()
            else:
                self.old_pil_rect = None
                self.turn = 'human'
                self.TurnAIimg.erase_sprite()
                self.AIimg.display_sprite()
                self.UserImg.erase_sprite()
                self.TurnImgUser.display_sprite()
        
        return 
        
