# $Id: FileDialog.py,v 1.9.2.1 2007/01/26 22:51:33 marcusva Exp $
#
# Copyright (c) 2004-2007, Marcus von Appen
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""File selection dialog class."""

import os
from GenericDialog import GenericDialog
from FileList import FileList
from Frame import HFrame
from Label import Label
from Entry import Entry
from Constants import *

class FileDialog (GenericDialog):
    """FileDialog (title, buttons, results, directory=None) -> FileDialog

    A modal file selection dialog.

    The FileDialog is a GenericDialog, that allows the user to select
    files and directories from a filesystem using a FileList widget. It
    also displays an entry widget to allow quick modifications of the
    current directory path.

    The selected files and directories can be retrieved at any moment
    using the get_filenames() method, which returns them as a list.

    selection = dialog.get_filenames ()

    Default action (invoked by activate()):
    See the GenericDialog class.
    
    Mnemonic action (invoked by activate_mnemonic()):
    See the GenericDialog class.

    Attributes:
    filelist - The FileList widget displayed on the FileDialog.
    """
    def __init__ (self, title, buttons, results, directory=None):
        GenericDialog.__init__ (self, title, buttons, results)
        
        if directory == None:
            directory = os.curdir
        directory = os.path.abspath (directory)
        
        # Path access.
        self._pathframe = HFrame ()
        self._pathframe.minsize = 200, self._pathframe.minsize[1]
        self._pathframe.padding = 0
        self._pathframe.border = BORDER_NONE
        self._lblpath = Label ("#Path:")
        self._txtpath = Entry (directory)
        self._txtpath.minsize = 165, self._txtpath.minsize[1]
        self._lblpath.widget = self._txtpath
        self._pathframe.add_child (self._lblpath, self._txtpath)
        
        # File list browser.
        self._filelist = FileList (200, 160, directory)
        self.content.add_child (self._pathframe, self._filelist)

        # Align anything on the right.
        self.main.align = ALIGN_RIGHT

        # Events.
        self._txtpath.connect_signal (SIG_INPUT, self._set_directory)
        self._filelist.connect_signal (SIG_LISTCHANGED, self._set_path)

    def _set_path (self):
        """F._set_path () -> None

        Sets the entry text to the current directory path.
        """
        self._txtpath.text = self.filelist.directory
    
    def _set_directory (self):
        """F._set_directory () -> None
        
        Sets the directory to list after a text input
        """
        print "switching directory..."
        path = os.path.normpath (self._txtpath.text)
        if os.path.isdir (path):
            if path != self.filelist.directory:
                self.filelist.directory = path

    def get_filenames (self):
        """F.get_filenames () -> list

        Gets a list with the selected filenames.
        """
        items = self._filelist.get_selected ()
        directory = self.filelist.directory
        return [os.path.join (directory, item.text) for item in items]

    filelist = property (lambda self: self._filelist,
                         doc ="The filelist shown on the FileDialog.")
