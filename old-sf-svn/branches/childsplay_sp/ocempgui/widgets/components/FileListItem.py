# $Id: FileListItem.py,v 1.4 2006/07/03 10:13:31 marcusva Exp $
#
# Copyright (c) 2004-2005, Marcus von Appen
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

"""A list item suitable for displaying file and directory information."""

import os, stat
from childsplay_sp.ocempgui.draw import Image
from ListItem import TextListItem
from childsplay_sp.ocempgui.widgets.images import Icons16x16
from childsplay_sp.ocempgui.widgets.Constants import *
from childsplay_sp.ocempgui.widgets import base

class FileListItem (TextListItem):
    """FileListItem (filename, filetype) -> FileListItem

    A list item, which can display information about files.
    
    The FileListItem class is a TextListItem, which contains additional
    information about a file such as its type and a suitable icon
    surface.

    The 'filetype' argument of the constructor must be an integer value,
    which matches a valid value of the stat.S_IF* data values. It will
    be stored in the 'filetype' attribute of the FileSystem object.
    Take a look at the stat module and os.stat() documentation for more
    details about the different values.

    item = FileSystem ('myfile', stat.S_IFDIR)

    The passed filename will be stored in the 'text' attribute of the
    FileListItem as described in the TextListItem documentation.

    Dependant on the 'filetype' value a specific icon surface will be
    set in the 'icon' attribute of the list item. 

    Attributes:
    icon     - The icon to display on the FileListItem.
    filetype - The type of the file.
    """
    def __init__ (self, filename, filetype):
        TextListItem.__init__ (self, filename)

        if type (filetype) != int:
            raise TypeError ("filetype must be an integer")
        
        self._filetype = filetype
        self._icon = None

        iconpath = base.GlobalStyle.engine.get_icon_path ("16x16")
        
        if stat.S_ISDIR (filetype):
            self._icon = Image.load_image (os.path.join (iconpath,
                                                         Icons16x16.FOLDER),
                                           True)
        elif stat.S_ISLNK (filetype):
            self._icon = Image.load_image (os.path.join (Icons16x16.ICONPATH,
                                                         Icons16x16.FILE_LINK),
                                           True)
        elif stat.S_ISSOCK (filetype) or stat.S_ISFIFO (filetype):
            self._icon = Image.load_image (os.path.join \
                                           (iconpath, Icons16x16.FILE_SOCKET),
                                           True)
        elif stat.S_ISCHR (filetype):
            self._icon = Image.load_image (os.path.join (iconpath,
                                                         Icons16x16.FILE_CHAR),
                                           True)
        else:
            self._icon = Image.load_image (os.path.join (iconpath,
                                                         Icons16x16.FILE),
                                           True)
    
    icon = property (lambda self: self._icon, doc = "The icon to display.")
    filetype = property (lambda self: self._filetype,
                         doc = "The type of the file.")
