# -*- coding: utf-8 -*-

# Copyright (c) 2007 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           sp_cr.py
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

# Module which holds the GTK based main window and dialogs.

import logging
import glob
import os

import pango,gtk

from SimpleGladeApp import SimpleGladeApp
from SPWidgets import InfoDialog, Timer
import SPHelpText
from SPConstants import ACTIVITYDATADIR,LIGHT_GRAY,BASEDIR
from utils import MyError

glade_dir = os.path.join(BASEDIR,'pixmaps')

class MainWindow(SimpleGladeApp):
    """Main window used internally by SP
    """
    def __init__(self, parent=None, dice_cbf=None,\
                glade_path="sp_cr.ui", root="mainwindow", domain=None):
        self.logger = logging.getLogger("schoolsplay.sp_cr.MainWindow")
        self.parent = parent
        glade_path = os.path.join(glade_dir, glade_path)
        SimpleGladeApp.__init__(self, glade_path, root, domain)
        # set the fontsize for the various labels
        fnt = 'sans bold 12'
        self.label25.modify_font(pango.FontDescription(fnt))# Bottombar 'user:'
        self.label26.modify_font(pango.FontDescription(fnt))# Bottombar 'name'
        self.label27.modify_font(pango.FontDescription(fnt))# Bottombar 'activity name:'
        self.label28.modify_font(pango.FontDescription(fnt))# Bottombar 'name'
        self.label21.modify_font(pango.FontDescription(fnt))# Bottombar 'activity icon:'
        # setup the dice button
        self.dicebutton = self.button_dice
        theme = 'white'# not sure if we will use themes.
        # Get the dice images and place a start image on the dice button
        # The dice button uses different images so we set it up here and not in from glade.
        ICONPATH = os.path.join(ACTIVITYDATADIR,'SPData','base','dice',theme)
        DEFAULTICONPATH = os.path.join(ACTIVITYDATADIR,'SPData','base','dice','white')
        self.dicelist = glob.glob(os.path.join(ICONPATH,'dice*.png'))
        if len(self.dicelist) < 6:
            self.dicelist = glob.glob(os.path.join(DEFAULTICONPATH,'dice*.png'))
        self.dicelist.sort()
        # Change the image used for the dice button
        image = gtk.Image()
        image.set_from_file(self.dicelist[0])
        self.dicebutton.set_image(image)
        # set the global counter to keep track of the dice number
        self.dicecounter = 1
        # but start disabled
        self.dicebutton.set_sensitive(False)
        # and the graph button
        self.graphbutton = self.button_graph
        self.graphbutton.set_sensitive(False)
        
        
    def new(self):
        self.logger.debug("A new MainWindow has been created")
        self.logger.debug("Window size is : %sx%s" % self.mainwindow.get_size())
    
    def next_dice(self,count):
        self.logger.debug("next_dice called with:%s" % count)
        self.dicecounter = count
        image = gtk.Image()
        image.set_from_file(self.dicelist[count-1])
        self.dicebutton.set_image(image)
        self.dicebutton.set_sensitive(True)
        
    def on_mainwindow_delete_event(self, widget, *args):
        self.logger.debug("on_mainwindow_delete_event called with self.%s" % widget.get_name())
        return True

    def on_button_help_clicked(self, widget, *args):
        self.logger.debug("on_button_help_clicked called with self.%s" % widget.get_name())
        self.parent.core_info_button_pressed()
        return True

    def on_button_dice_clicked(self, widget, *args):
        self.logger.debug("on_button_dice_clicked called with self.%s" % widget.get_name())
        self.dicecounter += 1
        # The core checks that we never have a counter larger then available images 
        self.dicecounter = self.parent.core_dice_button_pressed(self.dicecounter)
        self.next_dice(self.dicecounter) 
        return True

    def on_button_graph_clicked(self, widget, *args):
        self.logger.debug("on_button_graph_clicked called with self.%s" % widget.get_name())
        self.parent.core_graph_button_pressed()
        return True

    def on_button_stop_clicked(self, widget, *args):
        self.logger.debug("on_button_stop_clicked called with self.%s" % widget.get_name())
        self.parent.core_quit_button_pressed()
        return True
        
class QuitDialog(SimpleGladeApp):
    """
    Dialog used internally by SP
    """

    def __init__(self, parent=None, glade_path="sp_cr.ui", root="quit_dialog", domain=None):
        self.logger = logging.getLogger("schoolsplay.sp_cr.QuitDialog")
        glade_path = os.path.join(glade_dir, glade_path)
        SimpleGladeApp.__init__(self, glade_path, root, domain)

    def new(self):
        self.logger.debug("A new QuitDialog has been created")
        self.quit_dialog.set_position(gtk.WIN_POS_CENTER)
        
    def run(self):
        return self.quit_dialog.run()
        
    def on_cancelbutton1_clicked(self, widget, *args):
        self.logger.debug("on_cancelbutton1_clicked called with self.%s" % widget.get_name())
        self.quit_dialog.destroy()
        return True

    def on_okbutton1_clicked(self, widget, *args):
        self.logger.debug("on_okbutton1_clicked called with self.%s" % widget.get_name())
        self.quit_dialog.destroy()
        return True

class LoginDialog(SimpleGladeApp):
    """
    Dialog used internally by SP
    """
    
    #This is a dialog because we can't have different top level windows
    #in Sugar. It makes it a bit harder but we try to imitate a toplevel window
    def __init__(self, parent=None, glade_path="sp_cr.ui", root="login_dialog", domain=None):
        self.logger = logging.getLogger("schoolsplay.sp_cr.LoginDialog")
        self.parent = parent
        # some attributes the caller checks
        self.username = None
        self.password = None
        self.quit = None
        
        glade_path = os.path.join(glade_dir, glade_path)
        SimpleGladeApp.__init__(self, glade_path, root, domain)
        
    def new(self):
        self.logger.debug("A new LoginDialog has been created")
        self.login_dialog.set_position(gtk.WIN_POS_CENTER)

    def run(self):
        # set the version labels
        import SPVersion
        self.label58.set_markup("<b>%s</b>" % SPVersion.spversion)
        self.label58.show()
        self.label59.set_markup("<b>%s</b>" % SPVersion.gtkversion)
        self.label59.show()
        self.label60.set_markup("<b>%s</b>" % SPVersion.pygtkversion)
        self.label60.show()
        self.label61.set_markup("<b>%s</b>" % SPVersion.sqlversion)
        self.label61.show()
        return self.login_dialog.run()

    def on_delete_event(self,widget,*args):
        self.logger.debug("on_delete_event called")

    def on_button_cancel_clicked(self, widget, *args):
        self.logger.debug("on_button_cancel_clicked called with self.%s" % widget.get_name())
        dlg = QuitDialog()
        if dlg.run() == -5:
            # we are also a dialog so we must set a attribute so that the 
            # caller knows that we want to stop
            self.quit = True
        self.login_dialog.destroy()
        return True

    def on_button_help_clicked(self, widget, *args):
        self.logger.debug("on_button_help_clicked called with self.%s" % widget.get_name())
        InfoDialog(SPHelpText.SPgdm._help_button_callback)
        return True

    def on_button_login_clicked(self, widget, *args):
        self.logger.debug("on_button_login_clicked called with self.%s" % widget.get_name())
        self.username = self.entry6.get_text()
        self.password = self.entry7.get_text()
        self.login_dialog.destroy()
        return True


class TopbarContainer(SimpleGladeApp):
    """
    This is the bar at the top of the screen with the numberrange togglebuttons
    and various other widgets.
    """
    def __init__(self, parent=None, toggle_labels=['10','20','100','1000'],\
                glade_path="sp_cr.ui", root="topbarcontainer", domain=None):
        self.logger = logging.getLogger("schoolsplay.sp_cr.MainWindow.TopbarContainer")
        self.parent = parent
        glade_path = os.path.join(glade_dir, glade_path)
        SimpleGladeApp.__init__(self, glade_path, root, domain)

        # create a tooltips object
        self.tooltips = gtk.Tooltips()
        # set fontsize
        fnt = 'sans bold 18'
        #self.label63.modify_font(pango.FontDescription(fnt))# Topbar excerises '1/1'
        #self.label67.modify_font(pango.FontDescription(fnt))# Topbar time '0'
        # get our top frame and set it as an attribute. The core expect it.
        self.mainframe = self.eventbox1
        # get eventbox and set backgroud color
        color = LIGHT_GRAY
        e = self.eventbox1
        e.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(color))

        # we have to add a buttonbox with toggle buttons ourselfs as glade can't
        # create a togglebuttonbox.
        self.bb = gtk.HButtonBox()
        self.bb.set_border_width(8)
        self.bb.set_layout(gtk.BUTTONBOX_SPREAD)
        self.bb.set_spacing(8)
        # get the buttons and set them to the given values
        self.but0 = gtk.RadioButton(None,toggle_labels[0])
        self.but0.get_child().modify_font(pango.FontDescription(fnt))
        self.tooltips.set_tip(self.but0, _("Use this to set the numbersrange the exercise will use."))
        self.but0.connect('toggled',self._on_toggle_button_toggled,\
                            (1,int(toggle_labels[0])))
        self.bb.add(self.but0)

        self.but1 = gtk.RadioButton(self.but0,toggle_labels[1])
        self.but1.get_child().modify_font(pango.FontDescription(fnt))
        self.tooltips.set_tip(self.but1, _("Use this to set the numbersrange the exercise will use."))
        self.but1.connect('toggled',self._on_toggle_button_toggled,\
                            (int(toggle_labels[0]),int(toggle_labels[1])))
        self.bb.add(self.but1)

        self.but2 = gtk.RadioButton(self.but0,toggle_labels[2])
        self.but2.get_child().modify_font(pango.FontDescription(fnt))
        self.tooltips.set_tip(self.but2, _("Use this to set the numbersrange the exercise will use."))
        self.but2.connect('toggled',self._on_toggle_button_toggled,\
                            (int(toggle_labels[1]),int(toggle_labels[2])))
        self.bb.add(self.but2)

        self.but3 = gtk.RadioButton(self.but0,toggle_labels[3])
        self.but3.get_child().modify_font(pango.FontDescription(fnt))
        self.tooltips.set_tip(self.but3, _("Use this to set the numbersrange the exercise will use."))
        self.but3.connect('toggled',self._on_toggle_button_toggled,\
                            (int(toggle_labels[2]),int(toggle_labels[3])))
        self.bb.add(self.but3)

        # Now we get the frame from the parent to wich we add the buttonbox
        align = self.alignment2
        align.add(self.bb)
        # Get a reference to the clock alignment
        self.timer_align = self.alignment3
        # and place the clock widget
        self.timer = Timer()
        self.timer_align.add(self.timer)
        # define some members
        self.numbersrange = (1, int(toggle_labels[0]))
        self.solution_observer = None
        self.numbers_observer = None
        # show ourselfs, just in case the core doesn't do it.
        self.mainframe.show_all()

    def new(self):
        self.logger.debug("A new TopbarContainer has been created")

    def _reset_observers(self):
        """Reset the bar, called by the core when an activity is stopped."""
        self.solution_observer = None
        self.numbers_observer = None
        self.set_sensitive_toggles((1,1,1,1))

    def _on_toggle_button_toggled(self,widget,data):
        """Radio buttons callback"""
        self.logger.debug("%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()]))
        self.numbersrange = data
        try:
            if self.numbers_observer:
                apply(self.numbers_observer,(data,widget.get_active()))
        except StandardError,info:
            self.logger.exception("the numbers observer raised an exception")
            raise MyError,info
        return True

    def _on_button33_clicked(self,widget,*args):
        """Solution button callback"""
        self.logger.debug("on_button33_clicked called with self.%s" % widget.get_name())
        try:
            if self.solution_observer:
                apply(self.solution_observer)
        except StandardError,info:
            self.logger.exception("the solution observer raised an exception")
            raise MyError,info

    def set_sensitive_toggles(self,seq):
        """Disable certain numbersrange toggle buttons.
        @seq must be a tuple with 4 numbers, 0 or 1.
        The numbers maps to the four toggle buttons.
        For example (0,1,1,1) will disable the '10' toggle and enable the rest
        """
        focus = False
        for i in (0,1,2,3):
            but = getattr(self,'but%s' % i)
            but.set_sensitive(seq[i])
            if seq[i] and not focus:# the first one that's True will be set active
                but.set_active(True)
                focus = True
                # emits a toggle signal
                #but.toggled()

    def register_solutionbut_observer(self,obs):
        """Register an observer function which will be notified when the user hits
        the 'check solution' button.
        The function must not takes arguments.
        """
        self.solution_observer = obs
    def register_numbersrangebut_observer(self,obs):
        """Register an observer function which will be notified when the user changes
        the 'numbersrange' toggle buttons.
        The function must takes one argument.
        """
        self.numbers_observer = obs

    def set_exercisecounter(self,done=1,total=1):
        """Set the exercisecount.
        @total must be an integer indicating the total exercises in this level.
        @done, an integer indicating the number of exercises done."""
        self.label63.set_text('%s/%s' % (done,total))

    def get_numbersrange(self):
        """Returns the current selected numbersrange.
        Users can change the numbersrange by selecting the toggle buttons.
        You should register an observer to be notified when an toggle event occurs.
        The value returnt by get_numbersrange is also updated when a toggle event
        occurs."""
        return self.numbersrange
    def get_timer(self):
        """
        Returns a reference to the timer object.
        See the SPWidgets.Timer documentation for more info.
        """
        return self.timer


def main():
    window2 = Window2()
    
    window2.run()

if __name__ == "__main__":
    main()
