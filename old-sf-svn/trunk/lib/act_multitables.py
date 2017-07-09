# -*- coding: utf-8 -*-

# Copyright (c) 2008 Stas Zytkiewicz stas.zytkiewicz@gmail.com
#
#           multitables.py
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
import os,sys,random,time, types

import utils
from SPConstants import *

import gtk,pango

# SimpleGladeApp turns a glade file into a GTK app
from SimpleGladeApp import SimpleGladeApp
from SPWidgets import WarningDialog
# containers that can be used globally to store stuff
class Img:
    pass
class Snd:
    pass

class MultiTable(SimpleGladeApp):
    """We create a GTK window from the glade file and then extract the frame with
    all the widgets. As a result we will have a complete frame widget with all
    the children connected to the callback functions.
    The parent can call 'get_frame' to get a frame widget.
    """
    def __init__(self, timer,parent=None,numbersrange=10,level=1,dbmapper=None,\
                glade_path="multitables.ui", root="window1", domain=None):
        # Boilerplate code, used it in other activities also
        self.logger = logging.getLogger("schoolsplay.multitables.MultiTable")
        self.logger.debug("Building a MultiTable widget with numbersrange: %s,%s" % numbersrange)
        SimpleGladeApp.__init__(self, glade_path, root, domain)
        self.low,self.high = numbersrange
        self.level = level
        self.dbmapper = dbmapper
        self.timer = timer
        self.timer.show()
        self.entry_solutions = {}
        self.time_to_finish = ''
        self.tablenum = 1
        self.e_list = []# keep track of our entries, we use it to calculate the numbers
        self.old_frame = None
        # detach our frame with everything from our parent window
        self.window1.remove(self.frame1)
        # setup the button labels
        # We connect the callback to the button and pass a tuple with the number
        # of the exercise and the parent frame name to set it's color in on_table_button_clicked
        # we have 10 exercises per numberrange
        for i in range(1, 11):
            b = getattr(self, 'button%s' % i)
            b.set_label("X %s" % i)
            # we also connect the signal with some data to identify this button
            # by the callback function.
            b.connect("clicked", self.on_table_button_clicked, (i,'frame%s' % (i+2), 'label%s' % (i+1)))
            i += 1

    def on_table_button_clicked(self,widget,data):
        self.logger.debug("on_table_button_clicked with: %s,%s" % (widget,data))
        self.timer.reset_timer()
        self.timerstarted = False# reset so that we can restart timer
        # the button's parent frame widget
        frame = getattr(self,data[1])
        # the label below the button holding the time.
        # we set the text for this lable in check_solution.
        self.time_label = getattr(self, data[2])
        # we change the color of the frame to indicate that it's selected.
        # In case there's a frame choosen before we reset it
        if self.old_frame:
            self.old_frame.modify_bg(gtk.STATE_NORMAL, None)
        self.old_frame = frame
        frame.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(GREEN))
        
        self.tablenum = data[0]
        # Now we know the kind of exercise, we set up the labels and a solutions hashtable
        # The keys are a reference to the entry widgets and the value is the solution
        i = 1 # labels start at label12, entrys at entry1
        for j in range(self.high-9, self.high+1):
            lbl = getattr(self, 'label%s' % (i+11))
            lbl.set_sensitive(True)
            ent = getattr(self, 'entry%s' % i)
            ent.set_text('')
            self.e_list.append(ent)
            self.entry_solutions[ent] = j*int(data[0])
            lbl.set_markup("<b> %s x %s = </b>" % (j, self.tablenum))
            i += 1
        utils.reset_entry_cells(self.e_list)# just in case if there are red cells
        # Start timer, if not yet running
        if not self.timerstarted:
            self.logger.debug("Starting timer")
            self.timer.restart_timer()
            # we allow only one activation otherwise people can restart the timer.
            self.timerstarted = True
        else:
            self.logger.debug("Not starting timer")
        return 
        
    ############# Abstract methods for the parent ################    
    def get_frame(self):
        return self.frame1
    def destroy(self):
        self.frame1.destroy()
    def get_result(self):
         return (self.time_to_finish, self.wrongsolutions)
    def check_solution(self):
        """Checks solutions and return True on success and None if it's incorrect"""
        # we stop the timer when all the solutions are correct
        # first we check if all the entries have valid input.
        self.wrongsolutions = utils.validate_entry_cells_integers(self.e_list)
        # if so, we bail out as the user must first provide at least integers 
        # for all entries
        if self.wrongsolutions:
            self.logger.debug("wrongsolutions = %s,  not all entries validate" % self.wrongsolutions)
            return None
        # Then we check the solutions.
        for ent in self.e_list:
            print "ent", ent.get_text(), "entry_solutions",  self.entry_solutions[ent]
            if int(ent.get_text()) != self.entry_solutions[ent]:
                ent.set_text('')
                ent.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse(RED))
                self.wrongsolutions += 1
            else:
                utils.reset_entry_cells([ent])# in case the user corrected a red cell
                
        if self.wrongsolutions:
            self.logger.debug("wrongsolutions = %s, not storing the time into the db" % self.wrongsolutions)
            return None
        else:
            self.logger.debug("All entries are correct, inserting time")
            self.logger.debug("stopping timer")
            self.time_to_finish = self.timer.stop_timer()
            # time_label is always set to the correct label in on_table_button_clicked
            self.time_label.set_text('%s' % self.time_to_finish)
            self.time_label.show()
            # and reset timer.
            self.timer.reset_timer()
        # Store it into the dbase (only if not running in anonymous mode).
        self.dbmapper.insert("x%s" % self.tablenum, self.time_to_finish)
        # We must call commit to actually store it into the DB.
        # Normally th ecore calls it after getting the score.
        if not self.dbmapper.commit():
            self.logger.debug("commited table data")
        return True

class Exam:
    """ Object that will handle the exam in level two."""
    def __init__(self,parent, timer):
        self.logger = logging.getLogger("schoolsplay.multitables.Exam")
        self.logger.debug("Building an Exam object")
        self.totalexercises = 50
        self.exercisecounter = 0
        self.wrongsolutions = 0
        self.hbox = None
        self.timer = timer
        self.parent = parent
        self.frame = gtk.Frame()
        self.startbut = gtk.Button(_("When you are ready to start the exam, click on me."))
        self.startbut.connect('clicked', self.on_startbutton_clicked)
        self.startbut.child.modify_font(pango.FontDescription("sans 14"))
        self.frame.add(self.startbut)
        self.startbut.show()
    
    def on_startbutton_clicked(self, widget):
        self.logger.debug("on_startbutton_clicked")
        self.frame.remove(self.startbut)
        self.startbut.destroy()
        self.show_next_exercise()
        self.timer.restart_timer()
    
    def show_next_exercise(self):
        if self.hbox:
            # we destroy the box and anything within it to make sure we don't leave a bunch of  
            # stale widgets live.
            self.frame.remove(self.hbox)
            self.hbox.destroy()
            
        if self.exercisecounter == self.totalexercises:
            self.time_left = self.timer.stop_timer()
            self.parent._exam_finished(self.get_result())
            return True # we are called from a gtk widget event
        self.exercisecounter += 1
        first = random.randint(1, 10)
        second = random.randint(1, 10)
        solution = first * second
        lbl = gtk.Label("%s x %s = " % (first, second))
        lbl.modify_font(pango.FontDescription("sans 24"))
        self.ent = gtk.Entry(max=4)
        self.ent.set_width_chars(4)
        self.ent.modify_font(pango.FontDescription("sans 24"))
        self.ent.connect('activate', self.on_entry_activate, solution)
        self.hbox = gtk.HBox()
        self.hbox.pack_start(lbl)
        self.hbox.pack_start(self.ent)
        self.frame.add(self.hbox)
        self.ent.grab_focus()
        self.hbox.show_all()
        return True# we are called from a gtk widget event
        
    def on_entry_activate(self, widget, solution):
        try:
            esolution = int(widget.get_text())
        except ValauError:
            self.wrongsolutions += 1
        else:
            if esolution != solution:
                self.wrongsolutions += 1
        self.show_next_exercise()        

    ############# Abstract methods for the parent ################    
    def get_frame(self):
        return self.frame
    def destroy(self):
        self.frame.destroy()
    def get_result(self):
         return (self.time_left, self.wrongsolutions)

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
        self.logger =  logging.getLogger("schoolsplay.multitables.Activity")
        self.logger.debug("Activity started")
        self.SPG = SPGoodies
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CRData','MultitablesData')
        self.levelscount = 1
        # The frame received from the core will be our "parent window" 
        # The core will remove us when were finished.
        self.parentframe = self.SPG.get_parent()
        # we use an alignment to center our widget in the parentframe
        self.mainalignment = gtk.Alignment(xalign=0.5, yalign=0.5)
        self.parentframe.add(self.mainalignment)
        
        # get a reference to the topbar with the 'numberrange' and thumbs button.
        # We need it to get the numberrange which will be used for the exercise
        # and we also want to be notified when the user hits the thumbs button.
        # This will probably be boilerplate code for any activity.
        self.topbar = self.SPG.get_topbar()
        # The timer is started by the MultiTable class which is instanced in 
        # the nextlevel method and the 'alarm' signal is connected
        # to the 'timer_alarm' method
        self.timer = self.topbar.get_timer()
        self.timer.show_timer()
        # Be aware that calling 'set_sensitive_toggles' will emits a GTK 'toggled'
        # signal by the topbar and if you have registered any observers they will
        # be called.
        # That's why we call 'set_sensitive_toggles' BEFORE 'register_*_observer'.
        self.topbar.set_sensitive_toggles((1,1,0,0))
        self.topbar.register_numbersrangebut_observer(self._numbersrange_observer)
        self.topbar.register_solutionbut_observer(self._solutionbut_observer)
    
    def _numbersrange_observer(self,range,on_off):
        # When the user changes the numberrange we will quit this activity and
        # restart the current level with a new numberrange
        self.SPG.tellcore_restart_level(store_db=True)

    def _solutionbut_observer(self):
        # This behaviour differs from 'normal' activities as this activity stays
        # in the exercise widget instead of going through levels.
        self.logger.debug("_solutionbut_observer called")
        if self.exercisewidget.check_solution():
            # all is correct
            self.logger.debug("solutions: all correct")
        else:
            self.logger.debug("solutions: some errors")

    def _exam_finished(self, timeleft, wrongsolutions):
        """Called by the Exam object"""
        self.logger.debug("_exam_finished called with: %s %s" % (timeleft, wrongsolutions))
        WarningDialog(txt='(work in progress) Passed the exam.')
        # TODO: finish this
        
    def _exam_failed(self, *args):
        """called by the timer object 'alarm' signal"""
        self.logger.debug("_exam_failed called")
        WarningDialog(txt='(work in progress) Failed the exam.')
        # TODO: finish this
        
    def get_helptitle(self):
        """Mandatory method"""
        return _("Multitables")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "act_multitables"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),
        _("Level 1 is the level where the child must finish all the tables in a certain amount of time. When the times set in level one are low enough they will show up in green and level two will be available which is a 'exam' where the child must finish 50 exercises within a certain time."), 
            " ",
        _("Author: Stas Zytkiewicz")]
        return text 

    def get_helptip(self):
        """Mandatory method, when no tips available returns an empty list"""
        return [_("Repeat the same table a number of times and the time to finish it will get better.")]
        
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
        return 1 + self.unlock_level2
    def start(self):
        """Mandatory method."""
        # TODO: add support for dbase checking as the time and number of exercises
        #       can be set in the dbase.
        self.examtime = '4:30'
        # TODO: Check the dbase to see if we can unlock level 2
        self.unlock_level2 = True
        
    def stop(self):
        """Mandatory method, called by the core.
        Used to stop any timers started by this object."""
        self.logger.debug("Stopping the timer, if any")
        self.timer.stop_timer()
    
    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        self.logger.debug("next_level called: %s" % level)
        if level > self.get_levelscount():
            return False
        self.dbmapper = dbmapper
        
        # make sure in case we are recalled that the alignment is empty
        child = self.mainalignment.get_child()
        if child:
            self.mainalignment.remove(child)
            
        if level == 1:
            self.timer.reinit_timer('0:00', increase=True)
            # the MultiTable object handles everything in level 1
            self.exercisewidget = MultiTable(timer=self.timer,parent=self,\
                                numbersrange=self.topbar.get_numbersrange(),\
                                level=self.levelscount,dbmapper=dbmapper,\
                                glade_path=os.path.join(self.my_datadir,'multitables.ui'))
        else:
            # TODO: add check to see if all the preconditions are met like all the 
            # tables are done in a certain time.
            self.unlock_level2 = True
            precond = True
            if precond:
                self.timer.reinit_timer(self.examtime, increase=False)
                self.timer.connect('alarm', self._exam_failed)
                self.exercisewidget = Exam(self, self.timer)
            else:
                return false

        # add it to the alignment
        self.mainalignment.add(self.exercisewidget.get_frame())
        self.mainalignment.show_all()
        self.levelscount = level
        return True
    
    def post_next_level(self):
        """Mandatory method.
        This is called by the core after 'next_level' *and* after the 321 count.
        You should place stuff in here that run in a seperate thread like sound play."""
        # disable the dicebutton as we only have one level
        #self.SPG.tellcore_enable_dice(False)
        
    def get_score(self,timespend):
        """Mandatory method.
        @timespend is the time spend inside the level as it's calculated
        by the core.
        returns the score value for the past level.
        return None if no score value is used"""
        # Not used, exercisewidget uses it's own timer.
        return None
        
