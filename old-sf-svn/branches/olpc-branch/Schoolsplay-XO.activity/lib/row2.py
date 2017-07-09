
# -*- coding: utf-8 -*-

# Copyright (c) 2008 Stas Zytkiewicz stas.zytkiewicz@gmail.com
#
#           row2.py
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

from row1 import Activity as ActivityRow1 # we gonna extend the Activity class with the row1 Activity class
from row1 import RowWidget as RowWidgetRow1 # idem

# containers that can be used globally to store stuff
class Img:
    pass
class Snd:
    pass
    
class RowWidget(SimpleGladeApp):
    """We create a GTK window from the glade file and then extract the frame with
    all the widgets. As a result we will have a complete frame widget with all
    the children connected to the callback functions.
    The parent can call 'get_frame' to get a frame widget. This way the parent can
    use as much stack widgets a sit likes and put them inside a box or whatever.
    The stack widget controls itself and provides abstract functions for the
    parent to retrieve state and results.
    """
    def __init__(self, parent=None,numbersrange=20,level=1,\
                glade_path="row1.glade", root="window_row6", domain=None):
        # Boilerplate code, used it in other activities also
        self.logger = logging.getLogger("schoolsplay.row2.RowWidget")
        self.logger.debug("Building a 6 row widget")
        SimpleGladeApp.__init__(self, glade_path, root, domain)
        self.low,self.high = numbersrange
        self.level = level
        # detach our frame with everything from our parent window
        self.window_row6.remove(self.frame2)
        # Now we loop through our entries to set another, bigger, font
        # and add some filters.
        # The entries have a size of 96x32 which turns out to be the correct size
        # for the 'sans 24' font.
        start, end = 6,11
        self.e_list = []# keep track of our entries, we use it to calculate the numbers
        for i in range(start,end):
            # Our entries are named: entry6, entry7, ..., entry11
            e = getattr(self,'entry%s' % i)
            e.modify_font(pango.FontDescription("sans 24"))
            e.set_alignment(0.5)
            self.e_list.append(e)
        self._create_exercise()
    
    ############# Abstract methods for the parent ################    
    def get_frame(self):
        return self.frame2
    def destroy(self):
        self.frame2.destroy()
    def get_result(self):
        return self.wrongsolutions
    def check_solution(self):
        # called by the activity when there's a solution button event
        pass
    def check_solution(self):
        """Checks solutions and return True on success and None if it's incorrect"""
        self.wrongsolutions = utils.validate_entry_cells(self.e_list)
        if self.wrongsolutions:
            return None
        # We not intrested if the user has entered the same numbers as our
        # solution. We only check if the numbers are correctly added.
        for i in range(len(self.e_list)-2):
            n0 = self.e_list[i]
            n1 = self.e_list[i+1]
            n2 = self.e_list[i+2]
            if not int(n2.get_text()) == (int(n0.get_text()) + int(n1.get_text())):
                self.wrongsolutions += 1
                # We first check if the solution is wrong .
                # When the solution is one of the predefined numbers, the solution must be wrong
                # If so we check if one of the sums numbers is a predefined.
                # what's left we reset and color red.
                if n2 not in self.predefined:
                    n2.set_text('')
                    n2.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse(RED))
                else:
                    if n0 not in self.predefined:
                        n0.set_text('')
                        n0.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse(RED))
                    if n1 not in elist:
                        n1.set_text('')
                        n1.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse(RED))
                return False
        return True
        
    ############ Internal used methods ######################
    def _create_exercise(self):
        # We have 6 entries on a row which must be added together in a Fibonacci
        # sequence.
        # First we get 2 random numbers in the numberrange to start the sequence.
        sol = 0
        n1 = random.randint(self.low,self.high)
        n2 = random.randint(self.low,self.high)
        self.numbers = [n1,n2]
            
        # calculate the rest of the numbers
        for i in range(5):
            n = self.numbers[i]+self.numbers[i+1]
            self.numbers.append(n)
        print self.numbers
        # decide which entries are shown
        if self.level == 1:
            self.e_list[0].set_text(str(self.numbers[0]))
            self.e_list[0].set_editable(False)# prevent editing
            self.e_list[1].set_text(str(self.numbers[1]))
            self.e_list[1].set_editable(False)# prevent editing
            self.predefined = [self.e_list[0],self.e_list[1]]
        if self.level == 2:
            self.e_list[0].set_text(str(self.numbers[0]))
            self.e_list[0].set_editable(False)# prevent editing
            self.predefined = [self.e_list[0]]
        if self.level == 3:
            n = random.randint(0,3)
            self.e_list[n].set_text(str(self.numbers[n]))
            self.e_list[n].set_editable(False)# prevent editing
            self.e_list[n+1].set_text(str(self.numbers[n+1]))
            self.e_list[n+1].set_editable(False)# prevent editing
            self.predefined = [self.e_list[n],self.e_list[n+1]]
        if self.level >= 4:
            elist = range(0,5)
            random.shuffle(elist)
            n = elist[0]
            nn = elist[1]
            self.e_list[n].set_text(str(self.numbers[n]))
            self.e_list[n].set_editable(False)# prevent editing
            self.e_list[nn].set_text(str(self.numbers[nn]))
            self.e_list[nn].set_editable(False)# prevent editing
            self.predefined = [self.e_list[n],self.e_list[nn]]
        
class Activity(ActivityRow1):
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
        ActivityRow1.__init__(self,SPGoodies)
        # The Activity class from row1 adds a GTK alignment of it's own so we first remove it 
        for child in self.parentframe.get_children():
            self.parentframe.remove(child)
        self.logger =  logging.getLogger("schoolsplay.row2.Activity")
        self.logger.debug("Activity started")
        self.SPG = SPGoodies
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CRData','Row1Data')
        
        # The frame received from the core will be our "parent window" 
        # The core will remove us when were finished.
        self.parentframe = self.SPG.get_parent()
        # we use an alignment to center our stackwidget in the parentframe
        self.mainalignment = gtk.Alignment(xalign=0.5, yalign=0.5)
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
        # If we don't our observer numbersrangebut_observer will try to remove
        # the not existing stackwidget :-(
        self.topbar.set_sensitive_toggles((0,1,1,1))
        self.topbar.register_numbersrangebut_observer(self._numbersrange_observer)
        self.topbar.register_solutionbut_observer(self._solutionbut_observer)
    
    def _next_exercise(self):
        # first check if we already have a widget.(user hits dice in a level)
        if self.exercisewidget:
            self.exercisewidget.destroy()
            # when we have a rowwidget we also have a hbox, remove it.
            self.mainalignment.remove(self.hbox)
        # a box to hold the stackwidget(s)
        self.hbox = gtk.HBox(False, 0)
        # add it to the alignment
        self.mainalignment.add(self.hbox)
        # Create our stack widget
        self.exercisewidget = RowWidget(parent=self,\
                            numbersrange=self.topbar.get_numbersrange(),\
                            level=self.levelscount,\
                            glade_path=os.path.join(self.my_datadir,'row1.glade'))
        # pack widget(s) into a box
        self.hbox.pack_start(self.exercisewidget.get_frame(),False,False,4)
        # show the stuff
        self.parentframe.show_all()
    
    def get_helptitle(self):
        """Mandatory method"""
        return _("Row2")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "row2"
    
