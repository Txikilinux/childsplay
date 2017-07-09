# -*- coding: utf-8 -*-

# Copyright (c) 2006-2010 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
#
#           SPMenu.py
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

# Menu for the activities
# Special activity to provide a menu for maincore to load other activties

# We construct a hash with lists of tuples with xml items
# menu = {(<submenu icon name>,<subicon pos>): (<act icon>, <act pos>, <act name>)}
# It has also a special key called 'rootmenu' which holds the attributes
# from the rootmenu : {...,'rootmenu':(<file attr>, <menubartop attr>, \
#                        <menubarbottom attr>, <defaultsubmenu>),..}

# In Activity we turn them into buttons.
# Activity buttons return a module name and submenu buttons return other buttons.

import logging
import types
try:
    from xml.etree.ElementTree import ElementTree
except ImportError:
    # try the python2.4 way
    from elementtree.ElementTree import ElementTree

import pygame
from pygame.constants import *

import utils
from SPConstants import *
#from SPHelpText import ToolTipText
from SPWidgets import Button, ImgButton, TransImgButton
from SPSpriteUtils import SPInit, SPSprite
import SPDataManager
import Version

module_logger = logging.getLogger("schoolsplay.SPMenu")

#TODO: describe the format that must be used in the SP_menu.xml
# menu now only supports multilevel menus, this differs from previous CP.

class ParseMenu:
    def __init__(self, xml):
        self.logger = logging.getLogger("schoolsplay.SPMenu.ParseMenu")
        self.tree = ElementTree()
        self.tree.parse(xml)
        root = self.tree.getroot()
        rootfile = root.get('file')
        rootmbtop = root.get('menubartop')
        rootmbbottom = root.get('menubarbottom')
        rootdefault = root.get('defaultsubmenu')
        menuhash = {'rootmenu':(rootfile, rootmbtop, rootmbbottom, rootdefault)}
        
        submenus = self.tree.findall('submenu')
        
        for sub in submenus:
            menlist = []
            subicon = sub.get('file')
            subhicon = sub.get('hoverfile')
            # Fixme:when theres no position we assume the images together will be 800 width.
            # and we add postions based on the width of the images.
            try:
                subpos = tuple([int(x) for x in sub.find('position').text.split(',')])
            except AttributeError:
                # we will calculate the position based on image size
                subpos = (-1, -1)
            for item in sub.findall('menuitem'):
                menact = item.find('activity').text
                if item.get('enable') != 'True':
                    self.logger.debug("activity %s removed from menu, enable != True" % menact)
                    continue
                else:
                    self.logger.debug("activity %s added to the menu" % menact)
                menicon = item.get('file')
                menhicon = item.get('hoverfile')
                menpos = tuple([int(x) for x in item.find('position').text.split(',')])
                
                menlist.append((menicon, menhicon, menpos, menact))
            menuhash[((subicon, subhicon), subpos)] = menlist
        self.menuhash = {}
        for k, v in menuhash.items():
            if k == 'rootmenu':
                self.menuroot = v
            else:
                self.menuhash[k] = v
                
    def get_menu(self):
        return self.menuhash
    def get_root(self):
        return self.menuroot
  
class Menu:
    def __init__(self, iconpath, default, menu, cbf, theme, lang):
        self.logger = logging.getLogger("schoolsplay.SPMenu.Menu")
        print "default", default
        lang = lang[:2]
        buttons = utils.OrderedDict()
        self.buttonslist = []
        self.defaultbuttonslist = []
        # menu = {(<submenu icon name>,<subicon pos>): [(<act icon>, <act pos>, <act name>)]}
        # the hash key 'rootmenu' is removed from menu
        # here we construct the menu buttons
        #
        # It's possible to have localized menu act buttons.
        # First we look if there's a subdir in /lib/SPData/<theme>/menuicons named
        # to the current locale, eg /lib/SPData/<theme>/menuicons/nl for dutch.
        # If so we use those icons, if not we use the default ones in 
        # /lib/SPData/<theme>/menuicons/
        # If there's a localized subdir we assume all the icons are present, we don't check.
        if os.path.exists(os.path.join(iconpath, lang)):
            iconpath = os.path.join(iconpath, lang)
            
        for k, v in menu.items():
            self.logger.debug("building menu item: %s,%s" % (k, v))
            for t in v:
                p = os.path.join(iconpath, t[0])
                if t[1]:
                    hp = os.path.join(iconpath, t[1])
                else:
                    hp = None
                if theme['menubuttons'] == 'transparent':
                    b = TransImgButton(p, hp, t[2], name=t[3])
                else:
                    b = ImgButton(p, t[2], name=t[3])
                b.connect_callback(cbf, MOUSEBUTTONDOWN, t[3])
                
                if buttons.has_key(k):
                    buttons[k].append(b)
                else:
                    buttons[k] = [b]
        # here we construct the category buttons
        # first we must determine which button list belongs to the left 
        x , y = 0, 540 # start coords when theres no position given for the submenu buts  
        for k, v in buttons.items():
            
            p0 = os.path.join(iconpath, 'submenu', k[0][0])
            p1 = os.path.join(iconpath, 'submenu', k[0][1])
            if k[1][0] == -1:
                pos = (x, y)
            else:
                pos = k[1]
            b = TransImgButton(p0, p1, pos, padding=6, name=v)
            if k[1][0] == -1:
                x += b.get_sprite_width()
            if k[0][0] == default[3]:
                self.defaultbuttonslist = v
                self.defaultbutton = b
            b.set_use_current_background(True)
            b.connect_callback(cbf, MOUSEBUTTONDOWN, v)
            self.buttonslist.append(b)
            
    def _set_default_buttons(self, blist):
        self.defaultbuttonslist = blist
    def get_default_buttons(self):
        return (self.defaultbutton, self.defaultbuttonslist)
    def get_buttons(self):
        return self.buttonslist

class Activity:
    """  This provides the activity menu internally used by MainCore.
    
    It's much like an 'regular' activity but it is called differently
    """
    def __init__(self):
        """SPGoodies is a class object that SP sets up and will contain references
        to objects, callback methods and observers
        This SPGoodies differs from the regular SPGoodies the activities get."""
        self.logger = logging.getLogger("schoolsplay.SPMenu.Activity")
        self.logger.info("Activity started")
        
        self.displayed_buttons = []
        self.displayed_bottom_buttons = []
        self.selected_button = None
    
    def _setup(self, SPGoodies, dm):
        self.SPG = SPGoodies
        self.dm = dm
        self.screen = self.SPG.get_screen()
        self.screenclip = self.SPG.get_screenclip()
        self.blit_pos = self.screenclip.left, self.screenclip.top
        self.orgscreen = pygame.Surface(self.screenclip.size) # we use this to restore the screen
        self.orgscreen.blit(self.screen, (0, 0), self.screenclip)
        self.backgr = self.SPG.get_background()
        
        self.theme_dir = os.path.join(self.SPG.get_libdir_path(), 'SPData', 'themes', self.SPG.get_theme())
        self.theme_rc = self.SPG.get_theme_rc()
        self.actives = SPInit(self.screen,self.backgr)        
        self.actives.set_onematch(True)

        img = utils.load_image(os.path.join(self.theme_dir, self.rootmenu[2]))
        self.bottom_bar = SPSprite(img)
        self.bottom_bar.moveto((0, 520))
        
    def _parse_menu(self, theme_dir):
        p = os.path.join(theme_dir, 'SP_menu.xml')
        try:
            Pm = ParseMenu(p)
        except Exception, info:
            self.logger.exception("Error while parsing menu xml file: %s" % p)
            raise utils.MyError, info
        self.menu = Pm.get_menu()
        self.rootmenu = Pm.get_root()
        self.menubarpath = os.path.join(theme_dir, self.rootmenu[1])
        self.menubackpath = os.path.join(theme_dir, self.rootmenu[0])
    
    def _build_menu(self, theme_dir, theme_rc, lang):
        p = os.path.join(theme_dir, 'menuicons')
        try:
            self.Mn = Menu(p, self.rootmenu, self.menu, self.menu_callback, theme_rc, lang)
        except Exception, info:
            self.logger.exception("Error while constructing the menu buttons")
            raise utils.MyError, info
    
    def _remove_buttons(self, buttons):
        #self.logger.debug("_remove_buttons called with:%s" % buttons)
        if not self.actives:
            return
        for b in buttons:
            b.erase_sprite()
        self.actives.remove(buttons)
    
    def _display_buttons(self, menubuttons):
        if len(menubuttons) == 0:
            self.logger.error("No buttons found to display")
            raise utils.MyError, "No buttons found to display, check your install"
            return
        if menubuttons == self.displayed_bottom_buttons:
            refresh = False
        else:
            refresh = True
        for b in menubuttons:
            if refresh:
                b.mouse_hover_leave()
            b.display_sprite()
        self.actives.add(menubuttons)
    
    def _get_menuback_path(self):
        return self.menubackpath
    def _get_menubar_path(self):
        return self.menubarpath  
    
    def menu_callback(self, sprite, event, data):
        #self.logger.debug('menu_callback called with sprite %s, event %s and data %s' % (sprite, event, data))
        pygame.time.wait(200)
        if type(data[0]) not in types.StringTypes:
            self.logger.debug("menu cbf data is object list")
            if self.selected_button:
                self.selected_button.unselect()
            self.selected_button = sprite
            sprite.select()
            # clear the toplevel buttons
            self._remove_buttons(self.displayed_buttons)
            menubuttons = data[0]
            self.displayed_buttons = menubuttons
            self._display_buttons(menubuttons)
        else:
            self.logger.debug("menu cbf argument is module name")
            self.Mn._set_default_buttons(self.displayed_buttons)
            self._remove_buttons(self.displayed_buttons)
            self._remove_buttons(self.displayed_bottom_buttons)
            self.bottom_bar.erase_sprite()
            self.SPG._menu_activity_userchoice(data[0])
            return
    
    def refresh_sprites(self):
        """Mandatory method, called by the core when the screen is used for blitting
        and the possibility exists that your sprites are affected by it."""
        self.actives.redraw()

    def get_helptitle(self):
        """Mandatory method"""
        return _("Seniorplay")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "menu"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("This is the menu used to select an activity."),
        _("Select an activity and click on the button, the activity will be started."),
        _("Use the 'sub menu' buttons for the different activity menus"),
        " ",
        "Developers: Stas Zytkiewicz, Rene Dohmen, Chris van Bael",
        "Artwork and support: Formatics.nl, Qiosq.com, Wysiwich.be",
        "Beta testers: Wladek & Marek",
        "Feedback: Yvonne",
        " ",
        "This program is free software; you can redistribute it and/or modify it under the terms of version 3 of the GNU General Public License as published by the Free Software Foundation.",
        "A copy of this license should be included in the file GPL-3.", 
        "Version: %s" % Version.version
        ]
        if self.theme_rc['theme'] == 'braintrainer':
            text = [_("A collection of braintrain games for seniors."),
                    " ",
                    _("All the games have there own help page, just start a game and hit the stars on top of the screen to select another difficulty."),
                    _("Use the menu below to choose between the different game categories"),
                    " ",
                "Credits:",
                "Based on the Open Source Game framework Seniorplay (www.schoolsplay.org)",
                "The source code for this program is free software; you can redistribute it and/or modify it under the terms of version 3 of the GNU General Public License as published by the Free Software Foundation.",
                "A copy of this license should be included in the file GPL-3.", 
                " ",
                "Artwork and game content is property of QiosQ.com and is excluded from the GPL-3 license."
                " ", 
                "Artwork, Content and Support by QiosQ", 
                "Version: %s" % Version.version
                    ]
        return text 
    
    def get_helptip(self):
        """Mandatory method, when no tips available returns an empty string"""
        return ""
    def get_helptype(self):
        """Mandatory method, you must set an type"""
        return ""
    def get_helplevels(self):
        """Mandatory method, must return a string with the number of levels
        in the follwing format:
        _("This level has %s levels" % number-of-levels)"""
        return ""    

    def stop_timer(self):
        pass
    
    def start(self):
        """Mandatory method.
        This will start first level"""
        self.logger.debug("starting")
        self.scoredisplay = self.SPG.get_scoredisplay()
                
    def pre_level(self, level):
        """Mandatory method"""
        pass    
    def next_level(self, level):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        self.logger.debug("next_level")
        self.bottom_bar.display_sprite()
        menubuttons = self.Mn.get_buttons()
        #self.SPG.tellcore_enable_dice(1)
        self.SPG.tellcore_enable_dice(False)
        self.SPG.tellcore_hide_level_indicator()
        self.scoredisplay.clear_score()
        
        if self.displayed_buttons:
            # we are not in the start menu so we keep the stuff we had
            self._display_buttons(self.displayed_buttons)
            self._display_buttons(self.displayed_bottom_buttons)
            self.selected_button.select()
        else:
            self.displayed_bottom_buttons = menubuttons
            self._display_buttons(menubuttons)
            # display the default buttons
            but, menubuttons = self.Mn.get_default_buttons()
            self.displayed_buttons = menubuttons
            self._display_buttons(menubuttons)
            but.select()
            self.selected_button = but
        # we always return true as we don't have real levels        
        return True
        
    def loop(self, events):
        """Mandatory method"""
        for event in events:
            self.actives.update(event)
        return 
    
    
