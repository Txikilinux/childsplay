# -*- coding: utf-8 -*-

# Copyright (c) 2006-2010 Stas Zykiewicz <stas.zytkiewicz@schoolsplay.org>
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
from SPHelpText import ActivityMenuText
from SPWidgets import Button, ImgButton, TransImgButton, ImgTextButton
from SPSpriteUtils import SPInit, SPSprite
import SPDataManager
import Version

module_logger = logging.getLogger("childsplay.SPMenu")



class ParseMenu:
    def __init__(self, xml, complete=False):
        self.logger = logging.getLogger("childsplay.SPMenu.ParseMenu")
        self.tree = ElementTree()
        self.tree.parse(xml)
        root = self.tree.getroot()
        rootdefault = root.get('defaultsubmenu')
        menuhash = {'menudefault':rootdefault}
        
        submenus = self.tree.findall('submenu')
        
        for sub in submenus:
            menlist = []
            subicon = sub.get('file')
            subhicon = sub.get('hoverfile')
            # when theres no position we assume the images together will be 800 width.
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
                    if complete:
                        enabled = False
                    else:
                        continue
                else:
                    self.logger.debug("activity %s added to the menu" % menact)
                    enabled = True
                menicon = item.get('file')
                menhicon = item.get('hoverfile')
                mentext = item.get('text')
                if mentext == 'True':
                    mentext = True
                else:
                    mentext = False
                try:
                    menpos = tuple([int(x) for x in item.find('position').text.split(',')])
                except AttributeError:
                    # we will calculate the position based on image size
                    menpos = (-1, -1)
                menlist.append((menicon, menhicon, menpos, menact, mentext, enabled))
            menuhash[((subicon, subhicon), subpos)] = menlist
        self.menuhash = {}
        for k, v in menuhash.items():
            if k == 'menudefault':
                self.menuroot = v
            else:
                self.menuhash[k] = v
                        
    def get_menu(self):
        return self.menuhash
    def get_menudefault(self):
        return self.menuroot
      
class Menu:
    def __init__(self, iconpath, menu, cbf, theme, lang, default, removeables=None):
        self.logger = logging.getLogger("childsplay.SPMenu.Menu")
        lang = lang[:2]
        buttons = utils.OrderedDict()
        acttext = ActivityMenuText()
        self.buttonslist = []
        self.defaultbuttonslist = []
        default_iconpath = iconpath
        self.removeables = removeables# list of button names that should be removed
        # menu = {(<submenu icon name>,<subicon pos>): [(<act icon>, <act pos>, <act name>)]}
        # the hash key 'rootmenu' is removed from menu
        # here we construct the menu buttons
        #
        # It's possible to have localized menu act buttons.
        # First we look if there's a subdir in /lib/SPData/<theme>/menuicons named
        # to the current locale, eg /lib/SPData/<theme>/menuicons/nl for dutch.
        # If so we use those icons, if not we use the default ones in 
        # /lib/SPData/<theme>/menuicons/
        # If there's a localized subdir we use it, missing icons are replaced with the default ones.
        if os.path.exists(os.path.join(iconpath, lang)):
            iconpath = os.path.join(iconpath, lang)
        max_x = 790
        x_padding =50
        for k, v in menu.items():
            #self.logger.debug("building menu item: %s,%s" % (k, v))
            x, y = 50, 110 # start coords when theres no position given for the menu buts  
            for t in v:
                if os.path.splitext(t[0])[0].rstrip('.icon') in self.removeables:
                    continue
                p = os.path.join(iconpath, t[0])
                if not os.path.exists(p):
                    p = os.path.join(default_iconpath, t[0])
                if t[1]:
                    hp = os.path.join(iconpath, t[1])
                    if not os.path.exists(hp):
                        hp = os.path.join(default_iconpath, t[1])
                else:
                    hp = None
                if t[2][0] == -1:
                    pos = (x, y)
                else:
                    pos = t[2]
                print t
                if t[4]:
                    try:
                        txt = getattr(acttext, t[3])
                    except AttributeError:
                        self.logger.warning("No text attribute found in SPHelpText for %s" % t[3])
                        b = ImgButton(p, pos, name=t[3])
                    else:
                        b = ImgTextButton(p, _(txt) ,pos, padding=6, fsize=14, name=t[3])
                else:    
                    if theme['menubuttons'] == 'transparent':
                        b = TransImgButton(p, hp, pos, name=t[3])
                    else:
                        b = ImgButton(p, pos, name=t[3])
                b.connect_callback(cbf, MOUSEBUTTONUP, t[3])
                # we set the name of the activity to be used to identify the button later
                b.name = os.path.splitext(t[0])[0].rstrip('.icon')
                x += b.get_sprite_width() + x_padding
                if x > max_x - b.get_sprite_width():
                    x = 50
                    y += 140
                if buttons.has_key(k):
                    buttons[k].append(b)
                else:
                    buttons[k] = [b]
        # here we construct the category buttons
        # first we must determine which button list belongs to the left 
        x , y = 0, 532 # start coords when theres no position given for the submenu buts  
        for k, v in buttons.items():
            p0 = os.path.join(iconpath, 'submenu', k[0][0])
            p1 = os.path.join(iconpath, 'submenu', k[0][1])
            if k[1][0] == -1:
                pos = (x, y)
            else:
                pos = k[1]
            b = TransImgButton(p0, p1, pos, padding=0, values=v, name=os.path.splitext(k[0][0])[0])
            if k[1][0] == -1:
                x += b.get_sprite_width()
            if k[0][0] == default:
                self.defaultbuttonslist = v
                self.defaultbutton = b
            b.set_use_current_background(True)
            b.connect_callback(cbf, MOUSEBUTTONUP, v)
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
    def __init__(self, copmode=False, showpersonalquiz=False, showlocalquiz=False):
        """SPGoodies is a class object that SP sets up and will contain references
        to objects, callback methods and observers
        This SPGoodies differs from the regular SPGoodies the activities get."""
        self.logger = logging.getLogger("childsplay.SPMenu.Activity")
        self.logger.info("Activity started")
        self.displayed_buttons = []
        self.displayed_bottom_buttons = []
        self.selected_button = None
        self.COPmode = copmode
        self.removeables = []
        if not showpersonalquiz:
            self.removeables.append('quiz_personal')
        if not showlocalquiz:
            self.removeables.append('quiz_regional')   
    
    def _setup(self, SPGoodies, dm, bottombar):
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
                
        img = utils.load_image(os.path.join(self.theme_dir, bottombar))
        self.bottom_bar = SPSprite(img)
        if self.COPmode:# used for the btp controlpanel
            self.bottom_bar.moveto((0, 900))
        else:
            self.bottom_bar.moveto((0, 534))
        
    def _parse_menu(self, theme_dir, xmlname):
        p = os.path.join(theme_dir, xmlname)
        try:
            Pm = ParseMenu(p)
        except Exception, info:
            self.logger.exception("Error while parsing menu xml file: %s" % p)
            raise utils.MyError, info
        self.menu = Pm.get_menu()
        self.menudefault = Pm.get_menudefault()
    
    def _build_menu(self, theme_dir, theme_rc, lang):
        p = os.path.join(theme_dir, 'menuicons')
        try:
            self.Mn = Menu(p, self.menu, self.menu_callback, theme_rc, lang, self.menudefault, \
                           removeables=self.removeables)
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
        return "BrainTrainerPlus"
    
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
                    _("All the games have there own help page, just start a game and hit the stars on top of the screen to select another difficulty."),
                    _("Use the menu below to choose between the different game categories"),
                    " ",
                "Credits:",
                "Based on the Open Source Game framework Seniorplay (www.schoolsplay.org)",
                "The source code for this program is free software; you can redistribute it and/or modify it under the terms of version 3 of the GNU General Public License as published by the Free Software Foundation.",
                "A copy of this license should be included in the file GPL-3.", 
                " ",
                "Artwork and game content is property of QiosQ.com and is excluded from the GPL-3 license."
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
    
    
