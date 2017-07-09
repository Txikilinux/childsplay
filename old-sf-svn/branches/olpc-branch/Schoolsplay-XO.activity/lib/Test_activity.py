# activty template
# Nothing final yet, just to test ideas

#create logger, logger was setup in SPLogging
import logging

# standard modules you probably need
import os,sys

import utils
from SPConstants import *

import gtk

# containers that can be used globally to store stuff
class Img:
    pass
class Snd:
    pass

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
    name (self) must provide the activty name in english, not localized.
  """

    def __init__(self,SPGoodies):
        """SPGoodies is a class object that SP sets up and will contain references
        to objects, callback methods and observers
        TODO: add more explaination"""
        self.logger = logging.getLogger("schoolsplay.Test_Activity.Activity")
        self.logger.debug("Activity started")
        self.SPG = SPGoodies

        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'Test_activityData')
        # The frame received from the core will be our "parent window" 
        # The core will remove us when were finished.
        self.frame = self.SPG.get_parent()
        # setup the widgets we will use as our test activity
        # a box to hold a button and a label
        self.hbox = gtk.VBox(False, 0)
        # add it to the frame
        self.frame.add(self.hbox)
        # a button
        self.but = gtk.Button("Hit me 6 times")
        # put the button in a buttonbox
        self.butbox = gtk.HButtonBox()
        self.butbox.add(self.but)
        self.but.connect('clicked', self.on_button_clicked_cb, None)
        # label
        self.labeltext = "Level:%s, button hit %s times"
        # we will use self.labeltext as a dynamic label text which is altered by
        # the button
        # We will basically connect the button to the label
        self.label = gtk.Label(self.labeltext % (1,0))
        # pack widgets into a box
        self.hbox.pack_start(self.label,False,False,4)
        self.hbox.pack_start(self.butbox,False,False,4)
        # the level counter, used internally.
        self.levelscount = 1
        # finally show everything
        self.frame.show_all()
        # maincore takes care of the gtk main loop
    
    def on_button_clicked_cb(self,widget,*args):
        """gets called when the button is clicked"""
        if self.counter == 6:
            self.counter = 0
            self.SPG.tellcore_level_end()
        self.counter += 1
        self.label.set_text(self.labeltext % (self.levelscount,self.counter))
        
        
    def get_helptitle(self):
        """Mandatory method"""
        return _("Test_Activity")
    
    def get_name(self):
        """Mandatory method"""
        return "Test_activity"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity"),
        _(""),
        " ",
        _("Difficulty :  years"),
        " ",
        _("")]

        return text 
    
    def start(self):
        """Mandatory method."""
        self.logger.debug("start called")
        self.counter = 0
        
    def next_level(self,level,db_mapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        self.logger.debug("next_level called: %s" % level)
        # Do all kinds of stuff
        self.levelscount = level
        if self.levelscount >= 7:
            self.SPG.tellcore_game_end()
            return False
        self.counter = 0
        self.label.set_text(self.labeltext % (self.levelscount,self.counter))
        return True
        
    def post_next_level(self):
        """Mandatory method.
        This is called by the core after 'next_level' *and* after the 321 count.
        You should place stuff in here that run in a seperate thread like sound play."""
        self.logger.debug("post_next_level called")
        pass    
    def loop(self,events):
        """Mandatory method
        TODO: Do we need a return value?"""
        if self.counter >= 40:
            print "activity loops yet another second"
            self.counter = 0
        else:
            self.counter += 1
        for event in events:
            if event.type is MOUSEBUTTONDOWN:
                # call your objects
                self.actives.refresh(event)
        return 
        
