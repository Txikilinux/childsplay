
# -*- coding: utf-8 -*-

# Copyright (c) 2009 Stas Zytkiewicz stas.zytkiewicz@gmail.com
#
#           act_add_1.py
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

# standard modules you probably need
import os,sys,random,time

import utils
from SPConstants import *

import gtk,pango

# SimpleGladeApp turns a glade file into a GTK app
from SimpleGladeApp import SimpleGladeApp
import SPWidgets

# containers that can be used globally to store stuff
class Img:
    pass
class Snd:
    pass

class ExercisesTable:
    """gtk.Table object which holds a number of exercises in rows.
    Exercises can be any of +,-,*,/"""
    def __init__(self, kind, rows, cols, numberrange):
        """@kind must be a string withone of these characters: +,-,:
        @rows must be an iteger indicating the number of rows.
        @numberrange must be a tuple with the numbers range. 
        """
        self.wrongsolutions = 0
        self._set_table(kind, rows, cols, numberrange)
        
    def _set_table(self, kind, rows, cols, numberrange):
        """Constructs a GTK table widget with rows of exercises.
        It also sets up a dictionary called 'solutionentries' which sets the
        entry widget as key with the correct solution as value."""
        self.solutionentries = {}
        self.table = gtk.Table(2, rows, False)
        top_attach = 0
        bottom_attach = 1
        for row in range(rows):
            ent = gtk.Entry(max=4)
            ent.set_width_chars(4)
            exerc, solution = self._get_exercise(kind, cols, numberrange)
            lbl = gtk.Label()
            lbl.set_markup(exerc)
            self.solutionentries[ent] = solution
            self.table.attach(lbl, 0, 1, top_attach, bottom_attach,\
                xoptions=gtk.SHRINK, yoptions=gtk.SHRINK,\
                xpadding=0, ypadding=2)
            self.table.attach(ent, 1, 2, top_attach, bottom_attach,\
                xoptions=gtk.SHRINK, yoptions=gtk.SHRINK,\
                xpadding=0, ypadding=2)
            top_attach += 1
            bottom_attach += 1

    def _get_exercise(self, kind, cols, numberrange):
        first = random.randint(numberrange[0], numberrange[1])
        second = random.randint(numberrange[0], numberrange[1])
        if cols == 1:
            if kind == "+":
                solution = first+second
                exerc = "<b>%s + %s = </b>" % (first, second)
            elif kind == "-":
                first = first + second
                solution = first-second
                exerc = "<b>%s - %s = </b>" % (first, second)
            elif kind == ":":
                first = first*second
                solution = first / second
                exerc = "<b>%s : %s = </b>" % (first, second)
        else:
            third = random.randint(numberrange[0], numberrange[1])
            if kind == "+":
                solution = first+second+third
                exerc = "<b>%s + %s + %s = <b/>" % (first, second, third)
            elif kind == "-":
                first = first + second + third
                solution = first-second - third
                exerc = "<b>%s - %s - %s = </b>" % (first, second, third)
            elif kind == ":":
                first += 0.5
                dfirst = first * second
                solution = dfirst / second
                exerc = "<b>%s : %s = <b>" % (dfirst, second)
        return exerc, solution
    
    def get_table(self):
        return self.table
    def destroy(self):
        pass
    def get_result(self):
        return self.wrongsolutions
    def check_solution(self):
        """Checks solutions for proper entries.
        Returns True on success and None if it's incorrect"""
        self.wrongsolutions = utils.validate_entry_cells_integers(self.solutionentries.keys())
        for ent, sol in self.solutionentries.items():
            try:
                if int(ent.get_text()) != sol:
                    self.wrongsolutions += 1
                    utils.set_widget_to_red(ent)
            except ValueError:
                self.wrongsolutions += 1
                utils.set_widget_to_red(ent)
        return True
        
class Activity:
    """  Base class mandatory for any SP activty.
    The activity is started by instancing this class by the core.
    This class must at least provide the following methods.
    start (self) called by the core before calling loop.
    next_level (self,level) called by the core when the user changes levels.
    helptitle (self) must return the title of the game can be localized.
    help (self) must return a list of strings describing the activty.
    name (self) must provide the activty name in english, not localized in lowercase.
  """

    def __init__(self,SPGoodies):
        """SPGoodies is a class object that SP sets up and will contain references
        to objects, callback methods and observers
        TODO: add more explaination"""
        self.logger =  logging.getLogger("schoolsplay.act_add_1.Activity")
        self.logger.debug("Activity started")
        self.SPG = SPGoodies
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CRData','Act_add_1Data')
        self.exercisewidget = None
        self.kindstring = "+"
        # The frame received from the core will be our "parent window" 
        # The core will remove us when were finished.
        self.parentframe = self.SPG.get_parent()
        # we use an alignment to center our toplevel activity widget in the parentframe
        self.mainalignment = gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0.5, yscale=0.5)
        self.parentframe.add(self.mainalignment)
        
        # get a reference to the topbar with the 'numberrange' and thumbs button.
        # We need it to get the numberrange which will be used for the exercise
        # and we also want to be notified when the user hits the thumbs button.
        # This will probably be boilerplate code for any activity.
        self.topbar = self.SPG.get_topbar()
        # Be aware that calling 'set_sensitive_toggles' will emits a GTK 'toggled'
        # signal by the topbar and if you have registered any observers they will
        # be called.
        # That's why we call 'set_sensitive_toggles' BEFORE 'register_*_observer'.
        # If we don't the observers will be called while they are not properly setup yet
        self.topbar.set_sensitive_toggles((1,1,1,1))
        self.topbar.register_numbersrangebut_observer(self._numbersrange_observer)
        self.topbar.register_solutionbut_observer(self._solutionbut_observer)
                        
    def _numbersrange_observer(self,range,on_off):
        # When the user changes the numberrange we will quit this activity and
        # restart the current level with a new numberrange
        self.SPG.tellcore_restart_level(store_db=True)

    def _solutionbut_observer(self):
        self.logger.debug("_solutionbut_observer called")
        self.wrong = 0
        if self.exercisewidget.check_solution():
            # all is correct
            self.wrong += self.exercisewidget.get_result()
            # Display a modal dialog to allow the user to examinate the results
            dlg = SPWidgets.InfoDialog(_("This level is finished"))
            dlg.run()
            dlg.destroy()
            self.SPG.tellcore_level_end(store_db=True)

    def get_helptitle(self):
        """Mandatory method"""
        return _("Add numbers")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "act_add_1"
    
    def get_levelscount(self):
        """Mandatory method, must return an iteger indicating the number of levels."""
        return 2
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),
        _("Add the numbers."),
        _("Empty solutions are considered wrong solutions."), 
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

    def start(self):
        """Mandatory method."""
        pass
    
    def stop(self):
        """Mandatory method, called by the core when the activity is finished.
        Used to stop any threads started by this object."""
        pass

    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        self.logger.debug("next_level called %s" % level)
        self.level = level
        if level > self.get_levelscount():
            return False
        self.dbmapper = dbmapper
        # first check if we already have a widget.(user hits dice in a level)
        if self.exercisewidget:
            self.exercisewidget.destroy()
            # when we have a widget we also have a hbox, remove it.
            self.mainalignment.remove(self.hbox)
        
        self.total_exercises = 10
        cols = level
        self.hbox = gtk.HBox()
        self.exercisewidget = ExercisesTable(self.kindstring, self.total_exercises, cols, self.topbar.get_numbersrange())
        self.hbox.pack_start(self.exercisewidget.get_table(), expand=True, fill=True, padding=0)
        
        self.mainalignment.add(self.hbox)
        self.mainalignment.show_all()
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
        #m,s = timespend.split(':')
        #seconds = int(m)*60 + int(s)
        #time is not used
        if self.wrong == 0:
            score = 10
        else:
            score = self.total_exercises / float(self.wrong)
        self.logger.debug("score: %s" % score)
        self.dbmapper.insert('wrong',self.wrong)
        return score