# $Id: FileList.py,v 1.7.2.4 2007/01/26 22:51:33 marcusva Exp $
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

"""Filesystem browsing and selection list."""

import os, stat
from pygame import K_RETURN
from childsplay_sp.ocempgui.widgets.components import ListItemCollection, FileListItem
from ScrolledList import ScrolledList
from Constants import *
import base

class FileList (ScrolledList):
    """FileList (width, height, directory=None) -> FileList

    A scrolled list, which can list and browse a filesystem.

    The FileList widget class is a ScrolledList, which can list and
    browse filesystem contents using FileListItem objects. It supports
    automatic directory changes and change notifications. By default the
    list will be sorted with the directories first.

    To set or get the directory of which's content should displayed, the
    'directory' attribute and set_directory() method can be used.

    filelist.directory = '/usr/bin'
    if filelist.directory == 'C:\':
        filelist.directory = 'C:\Windows'

    Default action (invoked by activate()):
    See the ScrolledList class.
    
    Mnemonic action (invoked by activate_mnemonic()):
    See the ScrolledList class.

    Signals:
    SIG_DOUBLECLICKED - Invoked, when the list is double-clicked.

    Arguments:
    directory - The directory to list the contents of.
    """
    def __init__ (self, width, height, directory=None):
        ScrolledList.__init__ (self, width, height)

        self._signals[SIG_DOUBLECLICKED] = []
        self._directory = None

        self.selectionmode = SELECTION_SINGLE
        self.set_directory (directory)

    def set_directory (self, directory):
        """F.set_directory (...) -> None

        Sets the directory to list the contents of.

        Sets the directory the FileList should list the contents of. If
        the directory could not be found or accessed, the bell keycode
        '\\a' will be printed and the directory will remain unchanged.

        Raises a ValueError, if the passed directory argument does not
        exist or is not a directory path.
        """
        if directory == None:
            directory = os.path.curdir
        if not os.path.exists (directory):
            raise ValueError ("directory path does not exist")
        if not os.path.isdir (directory):
            raise ValueError ("argument is not a directory path")
        olddir = self._directory
        self._directory = os.path.normpath (directory)
        try:
            self._list_contents ()
        except OSError:
            print "\a"
            self._directory = olddir

    def _list_contents (self):
        """F.list_contents (...) -> None

        Populates the directory contents to the scrolled list.
        """
        items = ListItemCollection ()
        items.append (FileListItem (os.pardir, stat.S_IFDIR))
        stats = None
        files = []
        dirs = []
        dappend = dirs.append
        fappend = files.append
        entries = os.listdir (self._directory)
        isdir = os.path.isdir
        pjoin = os.path.join
        
        for filename in entries:
            if isdir (pjoin (self._directory, filename)):
                dappend (filename)
            else:
                fappend (filename)
        dirs.sort ()
        files.sort ()
        
        map (items.append, [FileListItem (d, stat.S_IFDIR) for d in dirs])
        for filename in files:
            stats = os.stat (pjoin (self._directory, filename))
            items.append (FileListItem (filename, stats.st_mode))
        self.set_items (items)

    def notify (self, event):
        """F.notify (...) -> None
        
        Notifies the FileList about an event.
        """
        if not self.sensitive:
            return

        if event.signal == SIG_DOUBLECLICKED:
            eventarea = self.rect_to_client ()
            if eventarea.collidepoint (event.data.pos):
                self.run_signal_handlers (SIG_DOUBLECLICKED)
                if event.data.button == 1:
                    # Get the item and switch to the directory on demand.
                    item = self.child.get_item_at_pos (event.data.pos)

                    if item and item.selected and stat.S_ISDIR (item.filetype):
                        self.set_directory (os.path.join (self.directory,
                                                          item.text))
                event.handled = True

        elif event.signal == SIG_KEYDOWN:
            if event.data.key == K_RETURN:
                if self.cursor and stat.S_ISDIR (self.cursor.filetype):
                    self.set_directory (os.path.join (self.directory,
                                                      self.cursor.text))
                event.handled = True
        ScrolledList.notify (self, event)
    
    directory = property (lambda self: self._directory,
                          lambda self, var: self.set_directory (var),
                          doc = "The directory to list the contents of.")
