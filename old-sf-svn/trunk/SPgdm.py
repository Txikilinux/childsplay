# -*- coding: utf-8 -*-

# Copyright (c) 2006 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           SPgdm.py
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

# Graphical login manager, like the gdm.
# The difference is that this is started by schoolsplay DataManager much like a splash screen.
# There will be an option for SP to disable this and run in a anonymous version.

# Start SP like this to disable the login stuff: schoolsplay --anonymous

import os,sys
#create logger, logger was configured in SPLogging
import logging
module_logger = logging.getLogger("schoolsplay.SPgdm")


# This holds the stuff from libglade generated gui
from sp_cr import LoginDialog
import gtk

from SPWidgets import InfoDialog
import SPHelpText

class GDMEscapeKeyException(Exception):
    """ This is raised from the activity_loop when the user hits escape.
    We basically using this exception as a signal"""
    pass
    
class SPGreeter:
    """Starts a login screen, this will be a window, not fullscreen.
    """
    def __init__(self,spg):
        self.logger = logging.getLogger("schoolsplay.SPgdm.SPGreeter")
        self.logger.debug("Starting")
        self.__name = ''
        
        #----------- setup screen
        # We always start with the login as we are a multi user app.
        # This is just one big dialog so we don't reparent it.
        # It's a dialog so that it could be modal and blocking
        loop = 1
        while loop:
            dlg = LoginDialog(parent=self)
            response = dlg.run()
            if response == gtk.RESPONSE_DELETE_EVENT:
                spg.tellcore_stop_gui()
            else:
                loop = 0
        # LoginDialog is a dialog so we must resort to hacking to get results
        if dlg.quit:
            # user has clicked ok in the quit dialog
            spg.tellcore_stop_gui()
            sys.exit(0)
        self.__name = dlg.username
        self.__passwrd = dlg.password
        

    def _login_button_callback(self,entry):
        self.logger.debug("_login_button_callback called")
        self.__name = entry.get_text()
        
##    def _help_button_callback(self):
##        self.logger.debug("_help_button_callback called")
##        ht = SPHelpText.SPgdm._help_button_callback
##        InfoDialog(ht)

    def get_loginname(self):
        return self.__name
    def get_password(self):
        return self.__passwrd
        
        
if __name__ == '__main__':
    # needed to simulate gettext
    import __builtin__
    __builtin__.__dict__['_'] = lambda x:x
        
    g = SPGreeter()
    print "got name: %s" % g.get_loginname()
        
        


