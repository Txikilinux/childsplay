# -*- coding: utf-8 -*-

# Copyright (c) 2007 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           out.py
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

import sys,os
try:
    logpath = os.path.join(os.environ["HOMEDRIVE"],os.environ["HOMEPATH"])
except:
    # for win 98/*nix (on *nix, set TEMP)
    logpath = os.environ["TEMP"]
    
class StdoutCatcher:
    def __init__(self):
        self.pyoutf = os.path.join(logpath,"sp_stdout.log")
        f = open(self.pyoutf,'w')
        f.close()    
    def write(self, msg):
        self.outfile = open(self.pyoutf, 'a')
        self.outfile.write(msg)
        self.outfile.close()
    def flush(self,*args):
        pass

class StderrCatcher:
    def __init__(self):
        self.pyerrf = os.path.join(logpath,"sp_stderr.log")
        f = open(self.pyerrf,'w')
        f.close()    
    def write(self, msg):
        self.outfile = open(self.pyerrf, 'a')
        self.outfile.write(msg)
        self.outfile.close()
    def flush(self,*args):
        pass

sys.stdout = StdoutCatcher()
sys.stderr = StderrCatcher()
