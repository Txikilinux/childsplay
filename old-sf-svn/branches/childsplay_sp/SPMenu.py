# -*- coding: utf-8 -*-

# Copyright (c) 2006-2008 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
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

# We could allow multiple users menus and start SP with a menu option
# schoolsplay --menu my_menu.xml

# We construct a dict of dicts with menu items
# menu = {'memory':(icon.png path,position x y),
#         'soundmemory':(icon.png path,position x y),...}
# Or with submenus
# menu = {(menu-icon.png path,position):({menu dict},position x y),...}
# So if the keys are strings then we have a 'normal' menu and when it's a 
# tuple object we have a menu with submenus.
# Then in Activity we turn them into ocempgui buttons.
# Activity buttons return a module name and submenu buttons reeturn other buttons.

# Every menu dict will have a key 'background' which holds the path to the 
# background image

import xml.parsers.expat

import childsplay_sp.ocempgui.widgets as ocw
import childsplay_sp.ocempgui.widgets.Constants as ocwc
import logging
import pygame
import utils
from xml.dom import minidom
module_logger = logging.getLogger("schoolsplay.SPMenu")

from SPConstants import *
from SPocwWidgets import ToolTip
from SPHelpText import ToolTipText

class Activity:
    """  This provides the activity menu internally used by MainCore.
    
    It's much like an 'regular' activity but it uses ocempgui stuff and it's
    placed inside the SP base directory.
    """
    def __init__(self, SPGoodies):
        """SPGoodies is a class object that SP sets up and will contain references
        to objects, callback methods and observers
        This SPGoodies differs from the regular SPGoodies the activities get."""
        self.logger = logging.getLogger("schoolsplay.SPMenu.Activity")
        self.logger.info("Activity started")
        self.SPGoodies = SPGoodies
        self.renderer = ocw.Renderer()
        MENUPATH = os.path.join(self.SPGoodies.get_libdir_path(), 'SPData', 'menu', self.SPGoodies._theme)
        if not os.path.exists(MENUPATH):
            self.logger.error("Themed path %s doesn't exists, using default" % MENUPATH)
            MENUPATH = os.path.join(self.SPGoodies.get_libdir_path(), 'SPData', 'menu', 'default')
        mm = MainMenu(MENUPATH, self.SPGoodies.get_libdir_path(), \
            self.SPGoodies._menupath, \
            self.renderer)
        try:
            self.menu = mm.get_menuitems(self.menu_callback)
        except Exception, info:
            self.logger.exception('%s' % info)
            raise utils.MyError('%s' % info)
        
        self.screen = self.SPGoodies.get_screen()
        
        try:
            self.background = utils.load_image(os.path.join(MENUPATH, self.menu['background']))
        except utils.MyError, info:
            self.logger.error(info)
            self.logger.info("Set background to black")
            self.background = pygame.Surface((800, 500)).convert()
            self.background.fill(BLACK)
        self.screen.set_clip((0, 0, 800, 500))
        pygame.display.update(self.screen.blit(self.background, (0, 0)))
        self.screen.set_clip()
        self.saved_screen = self.screen.convert()# used to restore screen in start 
        self.renderer.set_screen(self.screen)
        
        self.displayed_buttons = None

        # We add menu buttons to the renderer in start
        # we also need a list of the buttons when they are a multi level because
        # we must be able to erase/display them all at once when the user hits one of them
        self.menubuttons = self.menu['menu']
        
    def get_helptitle(self):
        """Mandatory method"""
        return _("Menu")
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "menu"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("This is the menu used to select an activity."),
        _("Select an activity and click on the button, the activity will be started."),
        _("If the menu consist of more layers, sub menus, you can always get back to the main menu by using the 'exit' button."),
        " ",
        "Developers: Stas Zytkiewicz, Chris van Bael",
        "Artwork: Joshua, Robert",
        "Beta testers: Wladek & Marek",
        "Feedback: Yvonne",
        " ",
        "This program is free software; you can redistribute it and/or modify it under the terms of version 3 of the GNU General Public License as published by the Free Software Foundation.",
        "A copy of this license should be included in the file GPL-3."]
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
    
    def _get_ocwcol(self):
        # special method used by the core to get the menu bar color or image, if set.
        return self.menu['ocwcol']
    
    def _remove_buttons(self):
        # remove any buttons
        try:
            self.renderer.remove_widget( * self.menubuttons)
        except TypeError, info:
            self.logger.debug("Trying to remove buttons: %s" % info)
        self.renderer.refresh()
    
    def stop_timer(self):
        pass
    
    def start(self):
        """Mandatory method.
        This will start first level"""
        if not self.menu:
            self.logger.error("No menu data found")
            raise utils.MyError("No menu data found", 'start')
        
    def next_level(self, level):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        self.screen.set_clip(0, 0, 800, 500)
        pygame.display.update(self.screen.blit(self.saved_screen, (0, 0)))
        self.screen.set_clip()
        self._remove_buttons()# just to be sure
        # Reminder: * is the unpack operator
        try:
            self.renderer.add_widget( * self.menubuttons)
        except ValueError:# already added
            pass
        self.renderer.refresh()
        # we always return true as we don't have real levels        
        return True
        
    def loop(self, events):
        """Mandatory method
        TODO: Do we need a return value?"""
        # This loop is different from a normal activity loop as we only use
        # ocempgui stuff and no sprites
        self.renderer.distribute_events( * events)
        return 
    
    def menu_callback(self, widget, item):
        self.logger.debug("menu_callback called with %s,%s" % (widget, item))
        if widget:
            # clear the toplevel buttons
            self._remove_buttons()
            # display the submenu buttons
            self.renderer.add_widget( * item)
            # we need this when we want to erase the buttons when the user quits
            self.displayed_buttons = item
        else:
            self.logger.debug("argument is module name")
            # we make sure that no tooltip is left on the screen
            # tooltips are shared amongst tooltip classes so we just use the first
            # button to erase the tooltip.
            self.menubuttons[0].destroy_tooltip()
            # remove buttons from screen
            self.renderer.remove_widget( * self.menubuttons)
            self.SPGoodies._menu_activity_userchoice(item)
            return

class ParseXMLMenu:
    def __init__(self, MENUPATH, xmlpath):
        self.kind_of_menu = 'normal'
        self.MENUPATH = MENUPATH
        self.logger = logging.getLogger("schoolsplay.SPMenu.ParseXMLMenu")
        self.menuxmlpath = os.path.join(MENUPATH, xmlpath)
        try:
            self.xmldoc = minidom.parse(self.menuxmlpath)
        except (xml.parsers.expat.ExpatError, Exception), info:
            self.logger.critical("Failed to parse menu xml file %s" % self.menuxmlpath)
            self.logger.critical("%s" % info) 
            self.xmldoc = None
        else:
            self.logger.debug("Parsing menu file %s" % self.menuxmlpath)
    
    def which_menu(self):
        """This will return the kind of menu, normal or multi layer.
        this is set by the parse_nodes meyhod and is used by the MainMenu class
        to determine how to setup the menu objects."""
        return self.kind_of_menu
    
    def parse_nodes(self):
        """Returns None if the parsing fails"""
        if self.xmldoc == None:
            module_logger.critical("XML parse error: No XML content")
            return None
        self.RootMenuNode = self.xmldoc.firstChild
        if self.RootMenuNode.tagName != u'rootmenu':
            self.logger.critical("XML parse error: No rootmenu node")
            return None
        background = self.RootMenuNode.getAttribute('file')
        ocwcol = self.RootMenuNode.getAttribute('ocw')
        # do we have submenus?
        if self.xmldoc.getElementsByTagName(u'submenu'):
            self.kind_of_menu = 'multi'
            menu = self._make_submenu()
        else:
            menu = self._make_menu()
        if menu:
            menu['background'] = background
            if ocwcol:
                try:
                    t_ocwcol = tuple([int(x) for x in ocwcol.split(',')]) + (255, )
                except StandardError, info:
                    self.logger.info("failed to parse color value: %s, %s" % (repr(ocwcol), info))
                    self.logger.info("Assuming it's a image path")
                    menu['ocwcol'] = (os.path.join(self.MENUPATH, ocwcol), )# core excepts a tuple
                else:
                    menu['ocwcol'] = t_ocwcol
            else:
                menu['ocwcol'] = ocwcol
        # print statements only for debugging
        #print "parsed xml nodes:"
        #pprint.pprint(menu)
        return menu
        
    def _make_menu(self):
        menu = self._make_menuitem(self.xmldoc.getElementsByTagName(u'menuitem'))
        return menu
      
    def _make_submenu(self):
        """Return None on faillure"""
        menu = {}
        for SubMenuNode in self.xmldoc.getElementsByTagName(u'submenu'):
            iconfile = SubMenuNode.getAttribute(u'file')
            iconpath = os.path.join(self.MENUPATH, iconfile)
            if not os.path.exists(iconpath):
                self.logger.error("Couldn't find %s" % iconpath)
            try:
                xs, ys = SubMenuNode.childNodes[1].firstChild.data.split(',')
                x, y = int(xs), int(ys)
            except ValueError, info:
                self.logger.critical("XML parse error: %s" % info)
                return None
            except AttributeError, info:
                # No position given, that's critical.
                # We don't try to fix this, the user must provide a proper XML
                self.logger.critical("No submenu node position attr: %s" % info)
                return None
            submenu = self._make_menuitem(SubMenuNode.getElementsByTagName(u'menuitem'))
            if not submenu:# faillure
                return None
            menu[(iconpath, (x, y))] = submenu
        return menu
    
    def _make_menuitem(self, nodeslist):
        menu = {}
        for ItemNode in nodeslist:
            iconfile = ItemNode.getAttribute(u'file')
            iconpath = os.path.join(self.MENUPATH, iconfile)
            activity = ItemNode.getElementsByTagName(u'activity')
            rawposition = ItemNode.getElementsByTagName(u'position')
            try:
                xs, ys = rawposition[0].firstChild.data.split(',')
                x, y = int(xs), int(ys)
            except ValueError, info:
                self.logger.critical("XML parse error: %s" % info)
                return None
            except AttributeError, info:
                # No position given, that's critical.
                # We don't try to fix this, the user must provide a proper XML
                self.logger.critical("No submenu node position attr: %s" % info)
                return None
            # check if the activity exists
            file = activity[0].firstChild.data
            # try to import the module, if it fails we exclude it
            #try:
            #    foo = __import__('schoolsplay.lib.%s' % file)
            #except Exception:
            #    self.logger.exception("Failed to import %s, removing it from the menu." % file)
            #else:
            #    # free memory
            #    del foo
            menu[file] = (iconpath, (x, y))
        return menu
    
class MainMenu:
    def __init__(self, MENUPATH, ACTIVITYDIR, xmlpath, renderer):
        """This will parse the menu xml, load the activity icons and creates
        ocempgui imagebuttons.
        """
        self.theme = os.path.basename(MENUPATH)
        self.defaultpath = os.path.join(ACTIVITYDIR, 'SPData', 'menu', 'default')
        self.xm = ParseXMLMenu(MENUPATH, xmlpath)
        self.renderer = renderer
        if not os.path.exists(MENUPATH):
            raise utils.MyError("Path doesn't exists: %s" % os.path.join(MENUPATH, xmlpath))
        self.menu = self.xm.parse_nodes()
        self.logger = logging.getLogger("schoolsplay.SPMenu.MainMenu")
        
    def get_menuitems(self, cbf):
        """returns a list with ocempgui buttons connected to the cbf object.
        The buttons are already set to their positions and connected to the
        callback function. 
        events send to the callback are the name of the activity by which the 
        activity can be imported.
        cbf should be a callback function accepting one argument.
        """
        # Which kind of menu do we have?
        # This is set by the parser.
        if not self.menu:
            self.logger.critical("No menu found, probably parsing error")
            return None
        if self.xm.which_menu() == 'normal':# normal is single level
            ocp_menu = {}
            ocp_menu['background'] = self.menu['background']
            ocp_menu['ocwcol'] = self.menu['ocwcol']
            del self.menu['background']
            del self.menu['ocwcol']
            l = self.setup_ocp_buttons(self.menu, cbf)
            ocp_menu['kind'] = 'normal'
            ocp_menu['menu'] = l
        else:
            # it's multilayer, so the keys are tuples and the vals are the menu dicts
            ocp_menu = {}
            ocp_menu['background'] = self.menu['background']
            ocp_menu['ocwcol'] = self.menu['ocwcol']
            del self.menu['background']
            del self.menu['ocwcol']
            l = []
            for k, v in self.menu.items():
                subl = self.setup_ocp_buttons(v, cbf)
                img, pos = k
                but = ocw.ImageButton(img)
                but.topleft = pos
                # The submenu buttons passes a tuple with itself and the list with 
                # associated submenu buttons
                # each of them also connected to the same callback function.
                # see Activity.menu_callback for details how we handle this.
                but.connect_signal(ocwc.SIG_CLICKED, cbf,  * (but, subl))
                l.append(but)
            ocp_menu['kind'] = 'multi'
            # This differs from a normal menu, here we put a list with ocp buttons
            # which pass a list with ocp buttons as argument to the callback.
            ocp_menu['menu'] = l

        return ocp_menu
    
    def setup_ocp_buttons(self, menudict, cbf):
        l = []
        tt = ToolTip()
        for k, v in menudict.items():
            if not os.path.exists(v[0]) and self.theme != 'default':
                file = os.path.join(self.defaultpath, os.path.basename(v[0]))
                v = (file, v[1])
            img, pos = v
            try:
                but = ocw.ImageButton(img)
            except Exception:
                self.logger.exception("Failed to load/setup button image.\n I will disable the button:%s\n Traceback follows:" % os.path.basename(v[0]))
                continue
            but.topleft = pos
            try:
                text = getattr(ToolTipText, k)
            except AttributeError:
                self.logger.info("No tooltip text found for %s, setting tooltip to name only" % k)
                text = k
            but.tooltip = text
            but.destroy_tooltip = tt._destroy_tooltip
            but.connect_signal(ocwc.SIG_ENTER, tt._make_tooltip, but.tooltip, self.renderer)
            but.connect_signal(ocwc.SIG_LEAVE, tt._destroy_tooltip)
            but.connect_signal(ocwc.SIG_CLICKED, cbf,  * (None, k))
            l.append(but)
        return l
    
if __name__ == '__main__':
    
    import SPLogging
    SPLogging.set_level('debug')
    SPLogging.start()

    import pprint
    import pygame
    from pygame.constants import *
    pygame.init()
    # needed for load_image function
    screen = pygame.display.set_mode((800, 600))
    
    def callback(widget, item):
        global render
        print "received", widget, item
        if widget:
            render.remove_widget(widget)
            render.add_widget( * item)
        else:
            print "activity is module name"
    
    m = MainMenu(os.path.join(os.getcwd(), ACTIVITYDATADIR, 'lib/SPData/menu/default'), 'SP_menu.xml')
    menu = m.get_menuitems(callback)
    if not menu:
        sys.exit(1)
        
    print "Parsed menu"
    pprint.pprint(menu)
    
    render = ocw.Renderer()
    render.set_screen(screen)
    
    for but in menu['menu']:
        render.add_widget(but)
    render.refresh()
    runloop = 1 
    while runloop:
        pygame.event.pump()
        events = pygame.event.get()
        for event in events:
            if event.type is KEYDOWN and event.key is K_ESCAPE:
                runloop = 0
            # let ocempgui handles the gui events, if needed
            render.distribute_events( * events)
        
        
        
