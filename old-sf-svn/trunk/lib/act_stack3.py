# -*- coding: utf-8 -*-

# Copyright (c) 2007 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           stack1.py
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

# standard modules you probably need
import os,sys,random

import utils
from SPConstants import *

import gtk
# SimpleGladeApp turns a glade file into a GTK app
from SimpleGladeApp import SimpleGladeApp

import pango

# containers that can be used globally to store stuff
class Img:
    pass
class Snd:
    pass

class StackWidget(SimpleGladeApp):
    """We create a GTK window from the glade file and then extract the frame with
    all the widgets. As a result we will have a complete frame widget with all
    the children connected to the callback functions.
    The parent can call 'get_frame' to get a frame widget. This way the parent can
    use as much stack widgets a sit likes and put them inside a box or whatever.
    The stack widget controls itself and provides abstract functions for the
    parent to retrieve state and results.
    """
    def __init__(self, parent=None,numbersrange=100,level=1,\
                glade_path="stack1.ui", root="window_stack15", domain=None):
        self.logger = logging.getLogger("schoolsplay.stack1.MainWindow")
        self.logger.debug("Building a 15 stack widget")
        SimpleGladeApp.__init__(self, glade_path, root, domain)
        self.low,self.high = numbersrange
        self.wrongsolutions = 0
        self.level = level
        # detach our frame with everything from our parent window
        self.window_stack15.remove(self.frame3)
        # Now we loop through our entries to set another, bigger, font.
        # The entries have a size of 96x32 which truns out to be the correct size
        # for the 'sans 24' font.
        start, end = 17, 32
        self.e_list = []# keep track of our entries, we use it to calculate the numbers
        for i in range(start,end):
            # Our entries are named: entry17,.. entry31
            e = getattr(self,'entry%s' % i)
            e.modify_font(pango.FontDescription("sans 18"))
            e.set_alignment(0.5)
            self.e_list.append(e)
        self._create_exercise()
        
    ############# Abstract methods for the parent ################    
    def get_frame(self):
        return self.frame3
    def destroy(self):
        self.frame3.destroy()
    def get_result(self):
        return self.wrongsolutions
    def _check_solution(self):
        """Checks solutions and return True on success and None if it's incorrect"""
        self.wrongsolutions = utils.validate_entry_cells_integers(self.e_list)
        if self.wrongsolutions:
            return None            
        # Now we check if the numbers are correct.
        # We also reset the entries as this can be the second or more time and
        # it's possible that entries are still colored red from before.
        # parse the matrix and check the solution.
        i = 0
        maxrows = 5
        for row in range(maxrows-1):# last row is just a solution
            fields = len(self.matrix[row])
            fi = 0
            for f in range(fields-1):
                f1 = self.matrix[row][f]
                f2 = self.matrix[row][f+1]
                f3 = self.matrix[row+1][fi]
                if not int(f3.get_text()) == int(f1.get_text())+int(f2.get_text()):
                    self.wrongsolutions += 1
                    # We first check if the solution is wrong or the solution.
                    # When the solution is one of the predefined numbers, the solution must be wrong
                    # If so we check if one of the sums numbers is a predefined.
                    # what's left we reset and color red.
                    elist = self.predefined.keys()
                    if f3 not in elist:
                        f3.set_text('')
                        f3.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse(RED))
                    else:
                        if f1 not in elist:
                            f1.set_text('')
                            f1.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse(RED))
                        if f2 not in elist:
                            f2.set_text('')
                            f2.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse(RED))
                    return False
                i += 1
                fi += 1
        return True
    ############ Internal used methods ######################
    def _create_exercise(self):
        # For an exercise we put some numbers in some entry widgets.
        # We start with a solution to make sure the numbers we show can lead 
        # to a correct solution.
        # If the user hits the solution button we just calculate all the numbers
        # from the enries to see if the users solution is correct.
        # For this exercise we have 10 fields in 4 rows (pyramid shape).
        # We consider row 4 the top row and row 1 the bottom.
        
        # first create a matrix.
        self.matrix = {}
        self.wrongsolutions = 0
        i = 5
        maxrows = 5
        for j in range(maxrows):
            self.matrix[j] = [0,]*i
            i -= 1
        # now we put random numbers from the numbersrange in the first row.
        for f in range(len(self.matrix[0])):
            self.matrix[0][f] = random.randint(self.low,self.high)
        # Start calculate the rest of the rows.
        i = 0
        for row in range(maxrows-1):# last row is just a solution
            fields = len(self.matrix[row])
            i = 0
            for f in range(fields-1):
                f1, f2 = self.matrix[row][f], self.matrix[row][f+1]
                self.matrix[row+1][i] = f1+f2
                i += 1
        print self.matrix
        # determine in which four fields we show the numbers.
        rlist = range(17,32)
        elist = []
        self.predefined = {}# class attribute, we use it in _check_solution
        for i in range(4):
            elist.append(rlist.pop(random.randint(1,len(rlist)-1)))
        # parse the matrix and check if we should display a number.
        # we also replace the values with the entry objects.
        i = 17# index start for the entries 
        for row,fields in self.matrix.items():
            fi = 0
            for f in fields:
                e = getattr(self,'entry%s' % i)
                self.matrix[row][fi] = e
                fi += 1
                if i in elist:
                    self.predefined[e] = (row,fi)
                    e.set_text(str(f))
                    e.set_editable(False)# prevent editing
                i += 1

class Activity:
    """  Base class mandatory for any SP activty.
    The activity is started by instancing this class by the core.
    This class must at least provide the following methods.
    start (self) called by the core before calling loop.
    next_level (self,level) called by the core when the user changes levels.
    helptitle (self) must return the title of the game can be localized.
    help (self) must return a list of strings describing the activty.
    name (self) must provide the activty name in english, not localized.
  """

    def __init__(self,SPGoodies):
        """SPGoodies is a class object that SP sets up and will contain references
        to objects, callback methods and observers
        TODO: add more explanation"""
        self.logger = logging.getLogger("schoolsplay.stack1.Activity")
        self.logger.debug("Activity started")
        self.SPG = SPGoodies
        
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CRData','StackData')
        # The frame received from the core will be our "parent window" 
        # The core will remove us when were finished.
        self.parentframe = self.SPG.get_parent()
        # we use an alignment to center our stackwidget in the parentframe
        self.mainalignment = gtk.Alignment(xalign=0.5, yalign=0.5)
        self.parentframe.add(self.mainalignment)
        # This will probably be boilerplate code for any activity.
        self.topbar = self.SPG.get_topbar()
        # Be aware that calling 'set_sensitive_toggles' will emits a GTK 'toggled'
        # signal by the topbar and if you have registered any observers they will
        # be called.
        # That's why we call 'set_sensitive_toggles' BEFORE 'register_*_observer'.
        # If we don't our observer numbersrangebut_observer will try to remove
        # the not existing stackwidget :-(
        self.topbar.set_sensitive_toggles((0,0,1,1))
        self.topbar.register_numbersrangebut_observer(self._numbersrange_observer)
        self.topbar.register_solutionbut_observer(self._solutionbut_observer)
        # the 'next_level' call by the core will create the stackwidget and put
        # it into mainalignment.
        # The core calls the following methods after the activity is loaded:
        # 0 start
        # 1 next_level
        # 2 post_next_level
        # From there the activity should have connected callbacks to events.
        #
        # The maincore takes also care of the gtk main loop
    
    def _set_stackwidget(self):
        # first check if we already have a widget.(user hits dice in a level)
        if self.stackwidget:
            self.stackwidget.destroy()
            # when we have a stackwidget we also have a hbox, remove it.
            self.mainalignment.remove(self.hbox)
        # a box to hold the stackwidget(s)
        self.hbox = gtk.HBox(False, 0)
        # add it to the alignment
        self.mainalignment.add(self.hbox)
        # Create our stack widget
        self.stackwidget = StackWidget(parent=self,\
                        numbersrange=self.topbar.get_numbersrange(),\
                        level=self.levelscount,\
                        glade_path=os.path.join(self.my_datadir,'stack1.ui'))
        # pack widget(s) into a box
        self.hbox.pack_start(self.stackwidget.get_frame(),False,False,4)
        # show the stuff
        self.parentframe.show_all()
    
    def _remove_stackwidget(self):
        # used when we want to restart the stackwidget.
        self.mainalignment.remove(self.hbox)
    
    def _numbersrange_observer(self,range):
        self.logger.debug("_numbersrange_observer called with: %s")
        # When the user changes the numberrange we will quit this activity and
        # restart the current level with a new numberrange
        self.SPG.tellcore_restart_level(store_db=True)
        
    def _solutionbut_observer(self):
        self.logger.debug("_solutionbut_observer called")
        # When the user hits the solution button we gonna check the exercise
        if self.stackwidget.check_solution():
            # all is correct
            if self.stackcount < self.total_exercises:
                self.wrong += self.activity.get_result()
                self.stackcount += 1
                self.topbar.set_exercisecounter(self.total_exercises,self.stackcount)
                self._set_stackwidget()
            else:
                self.SPG.tellcore_level_end()
        else:
            # TODO: parhaps a "bummer" kind of action
            pass
            
    def get_score(self,timespend):
        """Mandatory method, called by the core and must return
        a value between 0.0-10.0"""
        # solutions meaning number of entries to be filled
        # w = self.wrongsolutions
        # ts = total solutions
        # ks = known solutions (the number of entries shown on start)
        m,s = timespend.split(':')
        seconds = int(m)*60 + int(s)
        ks = 3
        ts = 15 - ks
        w = self.wrong
        c = 0.3
        f = 0.2
        score =   8.0 / ((float(ts) +float(w))/float(ts)) ** 0.4 + \
                    2.0 / ( max( seconds/(ts*2), 1.0)) **f
        self.logger.debug("score: %s" % score)
        self.dbmapper.insert('wrong',w)
        return score

    def get_helptitle(self):
        """Mandatory method"""
        return _("NumbersStack 10")
    
    def get_name(self):
        """Mandatory method"""
        return "act_stack2"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),
        _("Find and add all the numbers from the bottom up."),
        " ",
        _("Add the numbers in the first two fields and put the solution in the field above these two fields."),
        _("Click the 'thumbs' button to check your work."),
        " ",
        _("Difficulty : 7-10 years"),
        " ",
        _("Author: Stas Zytkiewicz")]

        return text 

    def get_helptip(self):
        """Mandatory method, when no tips available returns an empty list"""
        return []
        
    def get_helptype(self):
        """Mandatory method, you must set an type"""
        # Possible types are: Memory, Math, Puzzle, Keyboardtraining, Mousetraining
        #                     Language, Alphabet, Fun, Miscellaneous
        return _("Math")
    
    def get_helplevels(self):
        """Mandatory method, must return a string with the number of levels
        in the follwing format:
        _("This level has %s levels") % number-of-levels"""
        return _("This activity has %s levels") % self.get_levelscount()

    def get_levelscount(self):
        """Mandatory method, must return an iteger indicating the number of levels."""
        return 4

    def start(self):
        """Mandatory method."""
        self.logger.debug("start called")
        self.levelscount = 0
        self.total_exercises = 5
        self.stackwidget = None
        
    def next_level(self,level,db_mapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left.
        This activity has one exercise per level."""
        self.logger.debug("next_level called: %s" % level)
        if level > self.get_levelscount():
            return False
        self.dbmapper = db_mapper
        self.levelscount = level
        self.stackcount = 0
        self.topbar.set_exercisecounter(self.total_exercises,1)
        self._set_stackwidget()
        self.stackcount += 1
        return True
        
    def post_next_level(self):
        """Mandatory method.
        This is called by the core after 'next_level' *and* after the 321 count.
        You should place stuff in here that run in a seperate thread like sound play."""
        self.logger.debug("post_next_level called")
        pass    
    
        
