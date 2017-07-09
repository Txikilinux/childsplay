
# -*- coding: utf-8 -*-

# Copyright (c) 2009 Stas Zytkiewicz stas.zytkiewicz@gmail.com
#
#           letterflash1.py
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
import os,sys,random,time, glob

import utils
from SPConstants import *

import gtk,pango

# SimpleGladeApp turns a glade file into a GTK app
from SimpleGladeApp import SimpleGladeApp

from SPHelpText import Global

# containers that can be used globally to store stuff
class Img:
    pass
class Snd:
    pass

class Node:
    """Clas that represent the GTK image/label box which is displayed in rows
    on the screen.
    This class plays it own sound and checks and stores the users choice.
    """
    def __init__(self, imagepath, soundpath, name):
        self.char = name[0]
        self.sound = soundpath
        self.name = name
        self.snd = None
        but = gtk.Button()
        image = gtk.Image()
        image.set_from_file(imagepath)
        but.add(image)
        but.connect('clicked', self.on_image_clicked)
        self.lbl = gtk.Label("?")
        self.frame = gtk.Frame()
        self.frame.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        vbox = gtk.VBox(homogeneous=False, spacing=4)
        self.frame.add(vbox)
        vbox.pack_start(but, expand=False, fill=False, padding=0)
        vbox.pack_start(self.lbl, expand=False, fill=False, padding=0)
    
    def on_image_clicked(self, *args):
        print "on_image_clicked called with %s" % args
    
    def set_labelname(self):
        self.lbl.set_text(self.name)
        self.lbl.show()
    def get_frame(self):
        """Returns the frame containing the complete image/label widgets."""
        return self.frame
    def play_sound(self):
        self.snd = utils.load_music(self.sound)
        self.snd.play()
    def stop_sound(self):
        if self.snd:
            self.snd.stop()
    def show(self):
        self.frame.show_all()
    def hide(self):
        self.frame.hide()
        

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
        self.logger =  logging.getLogger("schoolsplay.letterflash1.Activity")
        self.logger.debug("Activity started")
        self.SPG = SPGoodies
        self.my_datadir = os.path.join(self.SPG.get_libdir_path(),'CRData','Letterflash1Data', self.SPG.get_localesetting()[0])
        self.stop = False
        if utils.NOSOUND:
            dlg = gtk.MessageDialog(parent=None, flags=0, type=gtk.MESSAGE_INFO,\
                               buttons=gtk.BUTTONS_OK, \
                               message_format= Global.no_sound_available)
            dlg.run()
            dlg.destroy()
            # used to stop when we are in next_level.
            # This way we stop gracefully
            self.stop = True
            return
            
        if not os.path.exists(self.my_datadir):
            self.logger.info("The locale %s isn't supported yet, exit" % loc)
            dlg = gtk.MessageDialog(parent=None, flags=0, type=gtk.MESSAGE_INFO,\
                               buttons=gtk.BUTTONS_OK, \
                               message_format= Global.no_alphabet_sounds % loc)
            dlg.run()
            dlg.destroy()
            # used to stop when we are in next_level.
            # This way we stop gracefully
            self.stop = True
            return
        self.logger.debug("Looking for content in %s" % os.path.join(self.my_datadir, 'names'))
        nameslist = glob.glob(os.path.join(self.my_datadir, 'names', '*.ogg'))
        contentlist = []
        for namepath in nameslist:
            name = os.path.splitext(os.path.basename(namepath))[0]
            imgpath = os.path.join(self.my_datadir, 'images', name+'.png')
            if not os.path.exists(imgpath):
                continue
            contentlist.append((imgpath, namepath, name))
        self.logger.debug("contentlist: %s" % contentlist)
        
        if len(contentlist) < 20:
            dlg = gtk.MessageDialog(parent=None, flags=0, type=gtk.MESSAGE_INFO,\
                               buttons=gtk.BUTTONS_OK, \
                               message_format= Global.not_enough_content % len(contentlist))
            dlg.run()
            dlg.destroy()
            # used to stop when we are in next_level.
            # This way we stop gracefully
            self.stop = True
            return

        random.shuffle(contentlist)
        l = len(contentlist)
        maxcol = 10
        maxrow = max(1, l / maxcol)
        if not l % maxcol:
            maxrow += 1
        box = gtk.VBox()
        table = gtk.Table(rows=1, columns=3, homogeneous=False)
        box.pack_start(table, expand=False, fill=False, padding=0)
        for row in range(0, maxrow):
            for col in range(0, maxcol):
                try:
                    item = contentlist.pop()
                except IndexError:
                    break
                child = Node(item[0], item[1], item[2]).get_frame()
                table.attach(child, left_attach=col, right_attach=col+1,\
                                   top_attach=row, bottom_attach=row+1,\
                                   xoptions=gtk.EXPAND|gtk.FILL, \
                                   yoptions=gtk.EXPAND|gtk.FILL, \
                                   xpadding=0, ypadding=0)
        # The frame received from the core will be our "parent window" 
        # The core will remove us when were finished.
        self.parentframe = self.SPG.get_parent()
        # we use an alignment to center our toplevel activity widget in the parentframe
        self.mainalignment = gtk.Alignment(xalign=0.5, yalign=0.5, xscale=1, yscale=1)
        self.parentframe.add(self.mainalignment)
        self.mainalignment.add(box)
        # show everything we have packed
        self.mainalignment.show_all()
#        # TESTCODE remove these two lines in a real activity
#        self.mainalignment.add(gtk.Label("TEST LABEL"))
#        self.mainalignment.show_all()
        
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
        # We disable all the toggles as we don't need numbersrange
        self.topbar.set_sensitive_toggles((0,0,0,0))
        self.topbar.register_numbersrangebut_observer(self._numbersrange_observer)
        self.topbar.register_solutionbut_observer(self._solutionbut_observer)
        
    def _numbersrange_observer(self,range,on_off):
        # When the user changes the numberrange we will quit this activity and
        # restart the current level with a new numberrange
        self.SPG.tellcore_restart_level(store_db=True)

    def _solutionbut_observer(self):
        self.logger.debug("_solutionbut_observer called")

    def get_helptitle(self):
        """Mandatory method"""
        return _("Letterflash 1")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "act_letterflash1"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("The aim of this activity:"),
        _(""),
        " ",
        _("Difficulty :  years"),
        " "]

        return text 

    def get_helptip(self):
        """Mandatory method, when no tips available returns an empty list"""
        return []
        
    def get_helptype(self):
        """Mandatory method, you must set an type"""
        # Possible types are: Memory, Math, Puzzle, Keyboardtraining, Mousetraining
        #                     Language, Alphabet, Fun, Miscellaneous
        return _("Alphabeth")
    
    def get_helplevels(self):
        """Mandatory method, must return a string with the number of levels
        in the follwing format:
        _("This level has %s levels") % number-of-levels"""
        return _("This activity has %s levels") % 1

    def start(self):
        """Mandatory method."""
        pass
        
    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        # stop is set in the class constructor when we don't have sound
        if self.stop:
            self.SPG.tellcore_game_end()
        return True
    
    def post_next_level(self):
        """Mandatory method.
        This is called by the core after 'next_level' *and* after the 321 count.
        You should place stuff in here that run in a seperate thread like sound play."""
        # disable the dicebutton as we only have one level
        self.SPG.tellcore_enable_dice(False)
        
    def get_score(self,timespend):
        """Mandatory method.
        @timespend is the time spend inside the level as it's calculated
        by the core.
        returns the score value for the past level.
        return None if no score value is used"""
        m,s = timespend.split(':')
        seconds = int(m)*60 + int(s)
        
