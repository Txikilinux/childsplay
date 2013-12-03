# -*- coding: utf-8 -*-

# Copyright (c) 2010 Stas Zykiewicz <stas.zytkiewicz@schoolsplay.org>
#
#           SPWidgets.py
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

from base import *
from buttons import *
from dialogs import *
from funcs import *
from text import *

from SPConstants import NoGtk
if not NoGtk:
    from gtk_widgets import *

LOCALE_RTL = utils.get_locale_local()[1]
if LOCALE_RTL:
    ALIGN_RIGHT = True
    ALIGN_LEFT = False
else:
    ALIGN_LEFT = True
    ALIGN_RIGHT = False

class TextRectException(Exception):
    pass


