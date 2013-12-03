
# -*- coding: utf-8 -*-

# Copyright (c) 2013 Stas Zytkiewicz stas.zytkiewicz@gmail.com
# Copyright (c) 2013 Ana Lopes anajoaolopes@gmail.com
# Copyright (c) 2013 Helder Costa h24costa@gmail.com
# Copyright (c) 2013 Rui Bento rui.m.bento@gmail.com
#
#           TicTacToe.py
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
# self.logger =  logging.getLogger("schoolsplay.TicTacToe.Activity")
# self.logger.error("I don't understand logger")
# See SP manual for more info 

module_logger = logging.getLogger("schoolsplay.TicTacToe")

# standard modules you probably need
import os,sys, random

import pygame
from pygame.constants import *

import utils
from SPConstants import *
import SPSpriteUtils

def whoPlaysFirst():
    # Who plays first is choosen randomly.
    return random.randint(0, 1)

def drawGrid(screen):
    pygame.draw.line(screen, BLACK, [325, 120], [325,570], 5)
    pygame.draw.line(screen, BLACK, [475, 120], [475,570], 5)
    
    pygame.draw.line(screen, BLACK, [175, 270], [625,270], 5)
    pygame.draw.line(screen, BLACK, [175, 420], [625,420], 5)

    Score(screen)

#0
def GridGame0(screen):
    if player == 1:
        pygame.draw.line(screen, BLUE, [200, 145], [300,245], 10)
        pygame.draw.line(screen, BLUE, [300, 145], [200,245], 10)
    else:
        pygame.draw.circle(screen, RED, [250, 195], 50, 10)
    GridGame[0] = player
    return 1 + player * (-1)

#1
def GridGame1(screen):
    if player == 1:
        pygame.draw.line(screen, BLUE, [350, 145], [450,245], 10)
        pygame.draw.line(screen, BLUE, [450, 145], [350,245], 10)
    else:
        pygame.draw.circle(screen, RED, [400, 195], 50, 10)
    GridGame[1] = player
    return 1 + player * (-1)
   
#2
def GridGame2(screen):
    if player == 1:
        pygame.draw.line(screen, BLUE, [500, 145], [600,245], 10)
        pygame.draw.line(screen, BLUE, [600, 145], [500,245], 10)
    else:
        pygame.draw.circle(screen, RED, [550, 195], 50, 10)
    GridGame[2] = player
    return 1 + player * (-1)
   
#3
def GridGame3(screen):
    if player == 1:
        pygame.draw.line(screen, BLUE, [200, 295], [300,395], 10)
        pygame.draw.line(screen, BLUE, [300, 295], [200,395], 10)
    else:
        pygame.draw.circle(screen, RED, [250, 345], 50, 10)
    GridGame[3] = player
    return 1 + player * (-1)
   
#4
def GridGame4(screen):
    if player == 1:
        pygame.draw.line(screen, BLUE, [350, 295], [450,395], 10)
        pygame.draw.line(screen, BLUE, [450, 295], [350,395], 10)
    else:
        pygame.draw.circle(screen, RED, [400, 345], 50, 10)
    GridGame[4] = player
    return 1 + player * (-1)
   
#5
def GridGame5(screen):
    if player == 1:
        pygame.draw.line(screen, BLUE, [500, 295], [600,395], 10)
        pygame.draw.line(screen, BLUE, [600, 295], [500,395], 10)
    else:
        pygame.draw.circle(screen, RED, [550, 345], 50, 10)
    GridGame[5] = player
    return 1 + player * (-1)
   
#6
def GridGame6(screen):
    if player == 1:
        pygame.draw.line(screen, BLUE, [200, 445], [300,545], 10)
        pygame.draw.line(screen, BLUE, [300, 445], [200,545], 10)
    else:
        pygame.draw.circle(screen, RED, [250, 495], 50, 10)
    GridGame[6] = player
    return 1 + player * (-1)
   
#7
def GridGame7(screen):
    if player == 1:
        pygame.draw.line(screen, BLUE, [350, 445], [450,545], 10)
        pygame.draw.line(screen, BLUE, [450, 445], [350,545], 10)
    else:
        pygame.draw.circle(screen, RED, [400, 495], 50, 10)
    GridGame[7] = player
    return 1 + player * (-1)
   
#8
def GridGame8(screen):
    if player == 1:
        pygame.draw.line(screen, BLUE, [500, 445], [600,545], 10)
        pygame.draw.line(screen, BLUE, [600, 445], [500,545], 10)
    else:
        pygame.draw.circle(screen, RED, [550, 495], 50, 10)
    GridGame[8] = player
    return 1 + player * (-1)

def Winner(player, x_start, y_start, x_end, y_end, screen):
    if player == 1:
        pygame.draw.line(screen, BLUE, [x_start, y_start], [x_end,y_end], 20)
    else:
        pygame.draw.line(screen, RED, [x_start, y_start], [x_end,y_end], 20)

def WinnerTest(player, line, screen):
    if (GridGame[0] == player and GridGame[1] == player and GridGame[2] == player): # across the top
        if line == 1 :
            Winner(player,175,195,625,195, screen)
            GameResult(player, screen)
        return True
    if (GridGame[3] == player and GridGame[4] == player and GridGame[5] == player): # across the middle
        if line == 1 :
            Winner(player,175,345,625,345, screen)
            GameResult(player, screen)
        return True    
    if (GridGame[6] == player and GridGame[7] == player and GridGame[8] == player): # across the bottom
        if line == 1 :
            Winner(player,175,495,625,495, screen)
            GameResult(player, screen)
        return True
    if (GridGame[0] == player and GridGame[3] == player and GridGame[6] == player): # down the left side
        if line == 1 :
            Winner(player,250,120,250,570, screen)
            GameResult(player, screen)
        return True
    if (GridGame[1] == player and GridGame[4] == player and GridGame[7] == player): # down the middle
        if line == 1 :
            Winner(player,400,120,400,570, screen)
            GameResult(player, screen)
        return True
    if (GridGame[2] == player and GridGame[5] == player and GridGame[8] == player): # down the right side
        if line == 1 :
            Winner(player,550,120,550,570, screen)
            GameResult(player, screen)
        return True
    if (GridGame[0] == player and GridGame[4] == player and GridGame[8] == player): # diagonal
        if line == 1 :
            Winner(player,175,120,625,570, screen)
            GameResult(player, screen)
        return True
    if (GridGame[2] == player and GridGame[4] == player and GridGame[6] == player): # diagonal
        if line == 1 :
            Winner(player,625,120,175,570, screen)
            GameResult(player, screen)
        return True    
    return False

def ClearGridGame():
    #drawScreen()
    # Reset the Game Grid
    for i in range(9):
        GridGame[i] = ' '

def isGridGameFull():
    # Return True if every space on the board has been taken. Otherwise return False.
    for i in range(9):
        if GridGame[i] == ' ':
            return False
    return True

def GameResult(player, screen):
    global n_player
    global n_computer
    if player==0:
        text = "The Computer Won!!!"
        n_computer += 1
    if player==1:
        text = "The Player Won!!!"
        n_player += 1
    if player==2:
        text = "The Game is Tie!!!"
    surf = utils.char2surf(text,72,BLACK)
    screen.blit(surf,(100,300))
    pygame.display.flip()
    pygame.time.wait(2000)
    pygame.event.clear()

def Score(screen):
    surf = utils.char2surf("Player: " + str(n_player),18,BLUE)
    screen.blit(surf,(20,570))
    surf = utils.char2surf("Computer: " + str(n_computer),18,RED)
    screen.blit(surf,(680,570))
    

def chooseRandomMoveFromList(listmoves):
    # Choose a move on the list is is possible
    moves = []
    for i in listmoves:
        if GridGame[i] == ' ':
            moves.append(i)

    if len(moves) != 0:
        return random.choice(moves)
    else:
        return None

def ComputerMove(player, screen):

    # Check if the computer can win in the next move
    for i in range(9):
        if GridGame[i] == ' ':
            GridGame[i] = player
            if WinnerTest(player, 0, screen):
                GridGame[i] = ' '
                return i
            GridGame[i] = ' '

    # Check if the player could win on his next move, and block them.
    for i in range(9):
        if GridGame[i] == ' ':
            GridGame[i] = 1 + player * (-1)
            if WinnerTest(1 + player * (-1), 0, screen):
                GridGame[i] = ' '
                return i
            GridGame[i] = ' '

    # Try to move to the corners, if they are free.
    move = chooseRandomMoveFromList([0, 2, 6, 8])
    if move != None:
        return move

    # Try to take the center, if it is free.
    if GridGame[4] == ' ':
        return 4

    # Move on one of the sides.
    return chooseRandomMoveFromList([1, 3, 5, 7])

# Reset the Game
GridGame = [' '] * 9

# who Plays First
player = whoPlaysFirst()

n_player = 0
n_computer = 0



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
        self.logger =  logging.getLogger("schoolsplay.TicTacToe.Activity")
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
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CPData','TictactoeData')
        # Location of the CPData dir which holds some stuff used by multiple activities
        self.CPdatadir = os.path.join(self.SPG.get_libdir_path(),'CPData')
        # Location of the alphabet sounds dir
        self.absdir = self.SPG.get_absdir_path()# alphabet sounds dir
        self.rchash = utils.read_rcfile(os.path.join(self.my_datadir, 'TicTacToe.rc'))
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
        self.actives.refresh()

    def get_helptitle(self):
        """Mandatory method"""
        return _("Tictactoe")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "TicTacToe"
    
    def get_help(self):
        """Mandatory methods"""
        text = ["Objective:",
        " ",
        "Try to complete, first, a row of 3 matching symbols,",
        "horizontally, vertically or diagonally.",
        " ",
        "Tip:",
        " ",
        "If your opponent has two symbols on the same line,",
        "you must put your symbol on that line to block him.",
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
        pass
        
    
    def get_helplevels(self):
        """Mandatory method, must return a string with the number of levels
        in the follwing format:
        _("This level has %s levels") % number-of-levels"""
        #return _("This activity has %s levels") % 6
        return _("This activity has no levels")
    
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
        # Remove these four lines
        #text = "Template activity for " + self.get_helptitle()
        #surf = utils.char2surf(text,24,RED)
        #self.screen.blit(surf,(20,200))

        drawGrid(self.screen)

        return True
    

    
    def dailytraining_pre_level(self, level):
        """Mandatory method"""
        pass
        
    def dailytraining_next_level(self, level, dbmapper):
        """Mandatory method.
        This should handle the DT logic"""
        pass
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
    
    def stop_timer(self):
        """You *must* provide a method to stop timers if you use them.
        The SPC will call this just in case and catch the exception in case 
        there's no 'stop_timer' method""" 
        try:
            self.timer.stop()
        except:
            pass

    def loop(self,events):
        global player
        """Mandatory method.
        This is the main eventloop called by the core 30 times a minute."""

        if player == 0:
            move = ComputerMove(player, self.screen)
            if move == 0:
                player = GridGame0(self.screen)
            elif move == 1:
                player = GridGame1(self.screen)
            elif move == 2:
                player = GridGame2(self.screen)
            elif move == 3:
                player = GridGame3(self.screen)
            elif move == 4:
                player = GridGame4(self.screen)
            elif move == 5:
                player = GridGame5(self.screen)
            elif move == 6:
                player = GridGame6(self.screen)
            elif move == 7:
                player = GridGame7(self.screen)
            else:
                player = GridGame8(self.screen)

        for event in events:
            if event.type is MOUSEBUTTONDOWN:
                pos_x = event.pos[0]
                pos_y = event.pos[1]
                if pos_x > 175 and pos_x <325:
                    if pos_y > 120 and pos_y < 270:
                        #0
                        if GridGame[0] == ' ':
                            player = GridGame0(self.screen)
                    elif pos_y > 270 and pos_y < 420:
                        #3
                        if GridGame[3] == ' ':
                            player = GridGame3(self.screen)
                    elif pos_y > 420 and pos_y < 570:
                        #6
                        if GridGame[6] == ' ':
                            player = GridGame6(self.screen)
                elif pos_x > 325 and pos_x <475:
                    if pos_y > 120 and pos_y < 270:
                        #1
                        if GridGame[1] == ' ':
                            player = GridGame1(self.screen)
                    elif pos_y > 270 and pos_y < 420:
                        #4
                        if GridGame[4] == ' ':
                            player = GridGame4(self.screen)
                    elif pos_y > 420 and pos_y < 570:
                        #7
                        if GridGame[7] == ' ':
                            player = GridGame7(self.screen)
                elif pos_x > 475 and pos_x <625:
                    if pos_y > 120 and pos_y < 270:
                        #2
                        if GridGame[2] == ' ':
                            player = GridGame2(self.screen)
                    elif pos_y > 270 and pos_y < 420:
                        #5
                        if GridGame[5] == ' ':
                            player = GridGame5(self.screen)
                    elif pos_y > 420 and pos_y < 570:
                        #8
                        if GridGame[8] == ' ':
                            player = GridGame8(self.screen)

        if WinnerTest(1 + player * (-1), 1, self.screen):
            self.clear_screen()
            ClearGridGame()
            drawGrid(self.screen)

        if isGridGameFull():
            GameResult(2, self.screen)
            self.clear_screen()
            ClearGridGame()
            drawGrid(self.screen)

        pygame.display.flip()

        return

    
        
