# -*- coding: utf-8 -*-

# Copyright (c) 2006 Stas Zykiewicz <stas.zytkiewicz@schoolsplay.org>
#
#           SPOptionParser.py
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

# will becomes the thing to parse the options given at startup.
# returns a dict
import sys, os

from SPConstants import SUPPORTEDTHEMES, ACTIVITYDATADIR
from SPVersion import optversion
from optparse import OptionParser
import ConfigParser
import logging

class OParser(OptionParser):
    def __init__(self):
        usage = "usage: %prog [options]"
        OptionParser.__init__(self, usage=usage, version=optversion)
        # set some reasonable defaults
        self.set_defaults(loglevel="warning", \
            theme="childsplay", \
            no_login=False, \
            remotemysqlserver='localhost', \
            kioskmode=False, \
            adminmode=False, \
            no_sound=False, \
            no_text=False,\
            admingui=False, \
            default_language='en_US.utf8', \
            lang='', \
            fullscreen=False, \
            bigcursor=False, \
            nocursor=False, \
            no_exit_question=False, \
            nocountdown=True, \
            user='', \
            no_level_pause=False, \
            checklog = False, \
            crapplatform=False,
            moviepointer=False,\
            plainversion=False)
        # add possible options to the parser
        self.add_option("--no-login", action="store_true",
            help="Don't show login window. This will run schoolsplay in 'anonymous' mode which means that there will be no data collecting",
        dest="no_login")
        self.add_option("--kioskmode", action="store_true",
            help="Enable kioskmode. This will run schoolsplay in kioskmode which means that there will be no keyboard support.",
        dest="kioskmode")
        self.add_option("--remote-mysqlserver", action="store_true",
            help="(NOT USED YET)The ip nummer of the remote mySQL server.",
            dest="remotemysqlserver")
        self.add_option("-t", "--theme",
            help="Set the theme schoolsplay will use.",
            dest="theme")
        self.add_option("-l", "--loglevel",
            help="Set logging level. Possible values are: debug,info,warning,error,critical",
            dest="loglevel")
        self.add_option("--adminmode", action="store_true",
            help="Enable adminmode. This will run schoolsplay in adminmode which means that certain extra possibilities are enabled",
        dest="adminmode")
        self.add_option("--no-sound", action="store_true",
            help="Disable any sound. Be aware that certain activities that rely on sound won't start.",
        dest="no_sound")
        self.add_option("--no-text",action="store_true",
            help="Disable text before every level's activities.",
            dest="no_text")
        self.add_option("--language",
            help="Set the language schoolsplay should use. Be aware that not all languages are supported yet. If your language isn't supported and you want to provide language support,please contact the schoolsplay team.",
            dest="lang")
        self.add_option("--default_language",
            help="Set the default language. Only use this if you know why you want to use it.",
            dest="default_language")
        self.add_option("--fullscreen", action="store_true",
            help="Run schoolsplay in fullscreen mode.",
        dest="fullscreen")
        self.add_option("--bigcursor", action="store_true",
            help="Use a bigger (48x48) cursor.",
        dest="bigcursor")
        self.add_option("--nocursor", action="store_true",
            help="Hide the mouse cursor. This is intended for touchscreens",
        dest="nocursor")
        self.add_option("--no-exit-question", action="store_true",
            help="No 'are you sure?' questions will be asked",
            dest="noexitquestion")
        self.add_option("--no-countdown", action="store_true",
            help="No '4,3,2,1' countdown screen will displayed between levels",
            dest="nocountdown")
        self.add_option("--user",
            help="Set the username to be used for dbase actions",
            dest="user")
        self.add_option("--no-level-pause", action="store_true",
            help="Don't show graphics and don't play a sound between levels.",
            dest="no_level_pause") 
        self.add_option("--checklog", action="store_true",
            help="Check the SP log for anomalies in the logs.",
            dest="checklog") 
        self.add_option("--crapware", action="store_true",
            help="When running on wellknown crapware like the white MSI 1900 set this option and we try to work around the various OS/hardware bugs.",
            dest="crapware")
        self.add_option("--plainversion", action="store_true",
            help="Return the version number in a plain string",
            dest="plainversion")
        self.add_option("--kill-btp",
            help="If we should kill any running btp, a pid must be given. BTP is started again when childsplay quits. (ONLY available on BTP machines)",
            dest="kill_btp") 
        self.add_option("--restart-btp",
            help="If we killed any running btp, we use this to start BTP again when childsplay quits. (ONLY available on BTP machines)",
            dest="restart_btp")          
        (self.options, self.args) = self.parse_args()
        
        # in case the user starts us with a unknown theme
        if self.options.theme not in SUPPORTEDTHEMES:
            print("WARNING: theme %s unknown, using default theme 'childsplay'" % self.options.theme)
            self.options.theme = 'childsplay'
        try:
            self.parse_themerc()
        except ConfigParser.NoSectionError, info:
            print("ERROR: Error in rc file %s" % info)
            sys.exit(1)
    
    def exit(self,  * args):
        """This overrides the OptionParser exit method"""
        if args:
            print args[1]
            self.print_help()
        sys.exit(0)
        
    def get_options(self):
        return self.options

    def get_args(self):
        return self.args

    def parse_themerc(self):
        config = ConfigParser.ConfigParser()
        print config
        rc = os.path.join(ACTIVITYDATADIR, 'SPData', 'themes', self.options.theme, 'theme.rc')
        print("DEBUG: parsing rc file %s" % rc)
        config.read(rc)
        #print config.items('menubar')
        d = {}
        d['background_login'] = config.get('login','background_login')
        d['exclude_modules'] = config.get('menubar','exclude_modules')
        d['exclude_buttons'] = config.get('menubar','exclude_buttons')
        d['menubar_position'] = config.get('menubar','menubar_position')
        d['level_indicator'] = config.get('menubar','level_indicator')
        d['menubuttons']= config.get('menubar', 'menubuttons')
        d['menubartop'] = config.get('menubar', 'menubartop')
        d['menubarbottom'] = config.get('menubar', 'menubarbottom')
        d['background'] = config.get('main', 'background')
        
        d['theme'] = self.options.theme
        self.options.theme_rc = d
        
        
            

if __name__ == '__main__':
    op = OParser()
    print op.get_options()
    
    
    
    
