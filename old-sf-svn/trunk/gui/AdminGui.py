# -*- coding: utf-8 -*-

# Copyright (c) 2007 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           AdminGui.py
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

"""Simple GUI to set mu and sigma values in the activity_options table."""

import sys,os

# Enable special streams redirection useful on win32 when run from an exe
# because on win32 the output and error streams are send into a black hole.
WIN32REDIRECT = False
if sys.platform == 'win32' and WIN32REDIRECT:
    try:
        import childsplay_sp.out as out
    except ImportError:
        print "Failed to import out.py, no redirection of streams"
    else:
        print >> sys.stderr,"Redirect sys.stderr to %s\sp_stderr.log" % out.logpath
        print "Redirect sys.stdout to %s\sp_stdout.log" % out.logpath
        
# make sure we don't run as root user, that's a bad habit and we refuse to do it.
if sys.platform == 'linux2' and os.environ['USER'] == 'root':
    print "\n=============== IMPORTANT READ THIS =============================="
    print "You running this program as the 'root' user, why?"
    print "You should only run programs as 'root' if you want to do system management."
    print "You risk the integrity of your system by running programs as root."
    print "Childsplay will not run as the 'root' user and will now quit.\n"
    sys.exit(1)

import SPLogging
SPLogging.set_level('debug')
SPLogging.start()
#create logger, configuration of logger was done above
import logging
module_logger = logging.getLogger("schoolsplay")
module_logger.debug("Created schoolsplay loggers")

import utils
utils.set_locale()
import SPHelpText

try:
    import pygtk
    #this is needed for py2exe
    if sys.platform == 'win32':
        pass
    else:
        #not win32, ensure version 2.0 of pygtk is imported
        pygtk.require('2.0')
    import gtk
except ImportError,info:
    module_logger.critical("This GUI depends on GTK and the Python bindings PyGTK. See the website for more information")
    sys.exit(1)
    
import SPGuiDBModel

class WarningDialog(gtk.MessageDialog):
    def __init__(self,parent=None,flags=gtk.DIALOG_MODAL,type=gtk.MESSAGE_WARNING,
                    buttons=gtk.BUTTONS_CLOSE,message_format='',txt=''):
        gtk.MessageDialog.__init__(self,parent=parent,
                            flags=flags,
                            type=type,
                            buttons=buttons,
                            message_format=message_format)
        self.connect("response", self.response)
        self.set_markup('%s%s%s' % ('<b>',txt,'</b>'))
        self.show()
    def response(self,*args):
        """destroys itself on a respons, we don't care about the response value"""
        self.destroy()
        
class ErrorDialog(WarningDialog):
    def __init__(self,txt):
        WarningDialog.__init__(self,parent=None,
                            flags=gtk.DIALOG_MODAL,
                            type=gtk.MESSAGE_ERROR,
                            buttons=gtk.BUTTONS_CLOSE,
                            message_format='',
                            txt=txt)
    def response(self,*args):
        gtk.main_quit()
            
class InfoDialog(WarningDialog):
    def __init__(self,txt):
        WarningDialog.__init__(self,parent=None,
                            flags=gtk.DIALOG_MODAL,
                            type=gtk.MESSAGE_INFO,
                            buttons=gtk.BUTTONS_CLOSE,
                            message_format='',
                            txt=txt)

class MainWindow:
    def __init__(self):
        self.logger = logging.getLogger("schoolsplay.AdminGui.MainWindow")
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Childsplay AdminGUI")
        self.window.set_border_width(10)
        self.window.set_size_request(300, 400)
        self.window.connect('delete_event', self.delete_event)
        
        # main box to hold two frames
        main_vbox = gtk.VBox(False, 0)
        self.window.add(main_vbox)
        
        # Two frames in a box, one for treeview and one to hold the button box
                
        self.tv_frame = gtk.Frame()
        # tv adds itself to the frame
        self.tv = TreeView(parent=self)
        
        self.but_frame = gtk.Frame()
        main_vbox.pack_start(self.tv_frame, True, True, 10)
                
        # setup the button box
        bbox = gtk.HButtonBox()
        bbox.set_border_width(5)
        # Set the appearance of the Button Box
        bbox.set_layout(gtk.BUTTONBOX_SPREAD)
        bbox.set_spacing(40)
        # set the buttons
        button = gtk.Button(stock=gtk.STOCK_HELP)
        button.connect('clicked',self.on_button_help)
        bbox.add(button)
        
        button = gtk.Button(stock=gtk.STOCK_SAVE)
        button.connect('clicked',self.on_save_button)
        bbox.add(button)
        
        button = gtk.Button(stock=gtk.STOCK_CLOSE)
        button.connect('clicked',self.on_close_button)
        bbox.add(button)
        main_vbox.pack_start(self.but_frame, False, False, 10)
        
        self.but_frame.add(bbox)

        self.window.show_all()
    
    def on_button_help(self,*args):
        self.logger.debug("help button clicked")
        InfoDialog(SPHelpText.AdminGui.on_button_help)
    
    def on_save_button(self,*args):
        self.logger.debug("save button clicked")
        self.tv.save_all_data()

    def on_close_button(self,*args):
        self.logger.debug("close button clicked")
        self.delete_event()
    
    # close the window and quit
    def delete_event(self,*args):
        gtk.main_quit()
        return False

class TreeView:
    def __init__(self,parent):
        self.parent = parent
        self.parent_frame = parent.tv_frame
        # Here we set up the dbase connection
        self.DM = SPGuiDBModel.get_datamanager()
        try:
            #hardcoded as we only handle this table
            self.tbm = self.DM.get_mapper('activity_options')
        except utils.NoSuchTable:
            ErrorDialog(_("The table 'activity_options' doesn't exist in the dbase"))
            return
        
        # We want all tables to have there activity_options set so if an activity
        # doesn't have a row it's set it with the default values.
        # If a activity name does exists we assume the values are set.
        for table in self.DM.get_table_names():
            # we don't care about the return values we just make sure we have all
            # the activity rows set
            self.DM.get_mu_sigma(table)
        # Get all the column entries in one list
        tb_data = self.tbm.get_table_data()
        
        # Setup the treeview in a scrollwindow
        self.scrollwindow = gtk.ScrolledWindow()
        self.scrollwindow.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.scrollwindow.set_size_request(300,300)
        # create a liststore with one string column to use as the model
        self.liststore = gtk.ListStore(str, str, str, 'gboolean')
        # create the TreeView using liststore
        self.treeview = gtk.TreeView(self.liststore)
        self.model = self.treeview.get_model()
        self.scrollwindow.add(self.treeview)
        # create the TreeViewColumns to display the data
        self.tvcolumn = gtk.TreeViewColumn('Activity name')
        self.tvcolumn1 = gtk.TreeViewColumn('MU-value')
        self.tvcolumn2 = gtk.TreeViewColumn('SIGMA-value')
        
        # add text from the table
        for row in tb_data:
            self.liststore.append([row[1],row[2],row[3], True])

        # add columns to treeview
        self.treeview.append_column(self.tvcolumn)
        self.treeview.append_column(self.tvcolumn1)
        self.treeview.append_column(self.tvcolumn2)

        # create a CellRenderers to render the data
        self.cell = gtk.CellRendererText()
        self.cell1 = gtk.CellRendererText()
        self.cell2 = gtk.CellRendererText()

        # set cell properties
        self.cell.set_property('cell-background', 'lightgrey')
        self.cell.set_property('editable', False)
        
        self.cell1.set_property('editable', True)
        self.cell1.connect('edited', self._edited_cb, 1)
        
        self.cell2.set_property('editable', True)
        self.cell2.connect('edited', self._edited_cb, 2)
        
        # add the cells to the columns 
        self.tvcolumn.pack_start(self.cell, True)
        self.tvcolumn1.pack_start(self.cell1, True)
        self.tvcolumn2.pack_start(self.cell2, True)

        # set the cell attributes to the appropriate liststore column
        self.tvcolumn.set_attributes(self.cell, text=0)
        self.tvcolumn1.set_attributes(self.cell1, text=1)
        self.tvcolumn2.set_attributes(self.cell2, text=2)

        # make treeview searchable
        self.treeview.set_search_column(0)
        # Allow sorting on the column
        self.tvcolumn.set_sort_column_id(0)
        # Allow drag and drop reordering of rows
        self.treeview.set_reorderable(True)
        # Add the scrollwindow to the gtk window
        self.parent_frame.add(self.scrollwindow)
    
    def save_all_data(self):
        self.rows = []# is populated by _get_all_treedata 
        # this is called until there no more rows
        self.liststore.foreach(self._get_all_treedata,None)
        result = self.tbm.replace_me_with(self.rows)
        if result:
            ErrorDialog(_("There was a problem while replacing the rows in the database.\nThe exception was:\n%s") % result)
        else:
            InfoDialog(_("All the data was stored succesfully."))
    
    def _edited_cb(self, cell, path, new_text, col):
        self.model[path][col] = new_text
        return True
    
    def _get_all_treedata(self,model, path, iter, user_data=None):
        row = []
        for col in [0,1,2]:
            row.append(model.get_value(iter,col))
        self.rows.append([None]+row)
    
def main():
    win = MainWindow()
    gtk.main()

if __name__ == '__main__':
    main()

