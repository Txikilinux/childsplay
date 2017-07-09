# -*- coding: utf-8 -*-

# Copyright (c) 2007 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           start_activity.py
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
import logging
logging.getLogger('').setLevel(logging.DEBUG)

from sugar.activity import activity
import sys, os
import gtk

#logging.shutdown()# SP setsup it's own loggers

import schoolsplay

class SchoolsplayActivity(activity.Activity):
    """Start schoolsplay_cr from Sugar""" 
    def __init__(self, handle):
        self.logger = logging.getLogger("schoolsplay.start_activity.SchoolsplayActivity")
        self.logger.debug("start")
        activity.Activity.__init__(self, handle)
        # Start SP
        obs = schoolsplay.Observer(parent=self)
        try:
            obs.start_gui()
        except:
            self.logger.exception("Toplevel exception")
            self.close()
