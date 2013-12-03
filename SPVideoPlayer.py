# -*- coding: utf-8 -*-
 
# Copyright (c) 2010 Stas Zykiewicz <stas.zytkiewicz@schoolsplay.org>
#
#           SPVideoPlayer.py
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
import os
import subprocess

class _Cmd(object):
    # class that provides shell command strings
    start = "/usr/bin/vlc --one-instance-when-started-from-file --intf 'skins2' --skins2-last=%s %s"

class Player:
    """class that wraps the system call to the vlc player and provides
    some abstraction. It also restores the volume when vlc quits."""
    def __init__(self,skinpath):
        self.skinpath = os.path.abspath(skinpath)
        self._cmd = _Cmd()
        # Default is used in case of an error when calling amixer
        self.volume_level = 75

    def start(self, moviepath):
        """Start player.
        Returns (True,'') when successful and (False,text) on any error.
        This call blocks the main thread until the player is stopped."""
        self._get_volume()
        result = self._execute(self._cmd.start % (self.skinpath, os.path.abspath(moviepath))) 
        self._restore_volume()
        return result
        
    def stop(self):
        pass
    
    # internally used
    def _get_volume(self):
        try:
            cmd=subprocess.Popen("amixer get Master",shell=True, \
                                 stdout=subprocess.PIPE, \
                                 stderr=subprocess.PIPE)
            output = cmd.communicate()[0]
        except Exception, info:
            module_logger.warning("program 'amixer' not found, unable to get volume levels")
        else:
            for line in output.split('\n'):
                if "%]" in line:
                    self.volume_level = int(line.split("%]")[0].split("[")[1])
                    
    def _restore_volume(self):
        subprocess.Popen("amixer set Master %s" % self.volume_level + "%",shell=True)
        
    def _execute(self,cmd):
        try:
            #result = subprocess.call(cmd)
            result = os.system(cmd)
        except OSError,info:
            return (False,  cmd+" "+str(info))
        if result:
            return (False, str(result))
        return (True,'')


if __name__ == '__main__':
    pl = Player('lib/SPData/themes/braintrainer/btp_800x600.vlt')
    print pl.start('lib/CPData/Test_actData/ayb.avi')
    
    
    
    
    
