# -*- coding: utf-8 -*-

# Copyright (c) 2007 Stas Zykiewicz <stas.zytkiewicz@gmail.com>
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

from xml.dom import minidom
# for exception raised by minidom
import xml.parsers.expat
import types
import gtk
import utils 

#create logger, logger was setup in utils
import logging
module_logger = logging.getLogger("schoolsplay.SPMenu")

from SPConstants import *
from SPWidgets import xpm_label_box

class Activity:
    """  This provides the activity menu internally used by MainCore.
    
    It's much like an 'regular' activity but it it's
    placed inside the SP base directory.
    """
    def __init__(self,SPGoodies):
        """SPGoodies is a class object that SP sets up and will contain references
        to objects, callback methods and observers
        This SPGoodies differs from the regular SPGoodies the activities get.
        The category buttons are connected in a way that they will send the corrensponding
        table with activity buttons packed into.
        See for more info the test code at the bottom of this module."""
        self.logger = logging.getLogger("schoolsplay.SPMenu.Activity")
        self.logger.info("Activity started")
        self.SPGoodies = SPGoodies
        MENUPATH = os.path.join(ACTIVITYDATADIR,'SPData','menu',self.SPGoodies._theme)
        mm = MainMenu(MENUPATH,self.SPGoodies._menupath)
        # this will become the main box to hold button tables
        self.mainbox = gtk.VBox(False, 0)
        # tooltips is setup by get_menuitems
        self.tooltips, self.menu = mm.get_menuitems(self.menu_callback,self.mainbox)
        # the 'mainbox' is now filled with table(s)
        #self.logger.debug("Parsed menu list: %s" % self.menu)
        # create a box and add it to the topframe
        # topbox will become the container for the submenu buttons
        self.topbox = gtk.HButtonBox()
        self.topbox.set_layout(gtk.BUTTONBOX_SPREAD)
        # Here we attach ourself to the frames received from the core.
        # The core will remove us when were finished.
        self._attach()
        
        for menubut in self.menu['menu']:
            self.topbox.add(menubut)
##        try:
##            self.background = utils.load_image(os.path.join(MENUPATH,self.menu['background']))
##        except utils.MyError,info:
##            self.logger.error(info)
##            self.logger.info("Set background to black")
##            self.background = pygame.Surface((800,500)).convert()
##            self.background.fill(BLACK)
        
        # Now show the submenu buttons.
        self.topbox.show_all()
        # we also need a list of the buttons when they are a multi level because
        # we must be able to erase/display them all at once when the user hits one of them
        self.menubuttons = self.menu['menu']
    
    def _attach(self):
        """called to attach ourselfs to the various parents"""
        self.frame = self.SPGoodies.get_parent()
        self.frame.add(self.mainbox)
        self.topalignment = self.SPGoodies._topframe_alignment
        self.topalignment.add(self.topbox)
        
    def _detach(self):
        """Called by the core to detach ourselfs from the various parents.
        This is needed so that the core can let activities attach them selfs to
        the same parent window."""
        if self.mainbox.get_parent():
            self.frame.remove(self.mainbox)
        if self.topbox.get_parent():
            self.topalignment.remove(self.topbox)

    def get_helptitle(self):
        """Mandatory method"""
        return "Menu"
    
    def get_name(self):
        """Mandatory method, returnt string must be in lowercase."""
        return "menu"
    
    def get_help(self):
        """Mandatory methods"""
        text = [_("This is the menu used to select an activity."),
        _("Select an activity and click on the button, the activity will be started."),
        _("If the menu consist of more layers, sub menus, you can always get back to the main menu by using the 'exit' button."),
        _("Activities have four levels and you can use the dice button to get to a next level."),
        _("You can't cycle through the levels using the dice button, at the last level you must use the stop button to get back to the menu."),
        " ",
        "Developers: Stas Zytkiewicz, Chris van Bael",
        "Artwork: Joshua, Robert",
        "Beta testers: Wladek and Marek",
        "Feedback: Yvonne",
        " ",
        "This program is free software; you can redistribute it and/or",
        "modify it under the terms of version 3 of the GNU General Public License",
        "as published by the Free Software Foundation.",
        "A copy of this license should be included in the file GPL-3."]
        return text 
    
    def _get_ocwcol(self):
        # special method used by the core to get the menu bar color or image, if set.
        return self.menu['ocwcol']
    
    def start(self):
        """Mandatory method.
        """
        self.logger.debug("menu start called")
        if not self.menu:
            self.logger.error("No menu data found")
            raise utils.MyError("No menu data found",'start')
        
    def next_level(self,level,dbmapper):
        """Mandatory method.
        Return True if there levels left.
        False when no more levels left."""
        self.logger.debug("Menu next_level called with:%s, %s" % (level,dbmapper))
        self._attach()
        # we always return true as we don't have real levels        
        return True
    
    def post_next_level(self):
        """Mandatory method.
        This is called by the core after 'next_level' *and* after the 321 count.
        You should place stuff in here that run in a seperate thread like sound play."""
        pass  

    def menu_callback(self,widget,table):
        """Button callback used by submenu buttons and activity buttons."""
        self.logger.debug("menu_callback called with %s,%s" % (widget,table))
        if type(table) in (types.UnicodeType,types.StringType):
            #print "received module name: %s" % table
            self.SPGoodies._menu_activity_userchoice(table)
        elif widget:
            # first we hide every table
            for child in self.mainbox.get_children():
                child.hide_all()
            # and then we only show the table we received
            table.show_all()
            # The following should not call show_all as that would show all the tables
            self.mainbox.show()
            self.frame.show()

class ParseXMLMenu:
    def __init__(self,MENUPATH,xmlpath):
        self.kind_of_menu = 'normal'
        self.MENUPATH = MENUPATH
        self.logger = logging.getLogger("schoolsplay.SPMenu.ParseXMLMenu")
        self.menuxmlpath = os.path.join(MENUPATH,xmlpath)
        try:
            self.xmldoc = minidom.parse(self.menuxmlpath)
        except (xml.parsers.expat.ExpatError,Exception),info:
            self.logger.critical("Failed to parse menu xml file %s" % self.menuxmlpath)
            self.logger.critical("%s" % info) 
            self.xmldoc = None
    
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
                    t_ocwcol = tuple([int(x) for x in ocwcol.split(',')])+(255,)
                except StandardError,info:
                    self.logger.info("failed to parse color value: %s, %s" % (repr(ocwcol),info))
                    self.logger.info("Assuming it's a image path")
                    menu['ocwcol'] = (os.path.join(self.MENUPATH,ocwcol),)# core excepts a tuple
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
            iconpath = os.path.join(self.MENUPATH,iconfile)
            try:
                xs,ys = SubMenuNode.childNodes[1].firstChild.data.split(',')
                x,y = int(xs),int(ys)
            except ValueError,info:
                self.logger.critical("XML parse error: %s" % info)
                return None
            except AttributeError,info:
                # No position given, that's critical.
                # We don't try to fix this, the user must provide a proper XML
                self.logger.critical("No submenu node position attr: %s" % info)
                return None
            submenu = self._make_menuitem(SubMenuNode.getElementsByTagName(u'menuitem'))
            if not submenu:# faillure
                return None
            menu[(iconpath,(x,y))] = submenu
        return menu
    
    def _make_menuitem(self,nodeslist):
        menu = {}
        for ItemNode in nodeslist:
            iconfile = ItemNode.getAttribute(u'file')
            iconpath = os.path.join(self.MENUPATH,iconfile)
            activity = ItemNode.getElementsByTagName(u'activity')
            rawposition = ItemNode.getElementsByTagName(u'position')
            tooltip = ItemNode.getElementsByTagName(u'tooltip')[0].firstChild.data
            try:
                xs,ys = rawposition[0].firstChild.data.split(',')
                x,y = int(xs),int(ys)
            except ValueError,info:
                self.logger.critical("XML parse error: %s" % info)
                return None
            except AttributeError,info:
                # No position given, that's critical.
                # We don't try to fix this, the user must provide a proper XML
                self.logger.critical("No submenu node position attr: %s" % info)
                return None
            # check if the activity exists
            file = activity[0].firstChild.data
            # try to import the module, if it fails we exclude it
##            try:
##                foo = __import__('lib/%s' % file)
##            except Exception:
##                self.logger.exception("Failed to import %s, removing it from the menu." % file)
##            else:
##                # free memory
##                del foo
##                menu[file] = (iconpath,(x,y))
            menu[file] = (iconpath,(x,y),tooltip)
        return menu
    
class MainMenu:
    def __init__(self,MENUPATH,xmlpath):
        """This will parse the menu xml, load the activity icons and creates
        gtk imagebuttons.
        """
        self.theme = os.path.basename(MENUPATH)
        self.defaultpath = os.path.join(ACTIVITYDATADIR,'SPData','menu','default')
        self.xm = ParseXMLMenu(MENUPATH,xmlpath)
        if not os.path.exists(MENUPATH):
            raise utils.MyError("Path doesn't exists: %s" % MENUPATH)
        self.menu = self.xm.parse_nodes()
        self.logger = logging.getLogger("schoolsplay.SPMenu.MainMenu")
        
    def get_menuitems(self,cbf,parentbox):
        """returns the box with gtk buttons connected to the cbf object
        packed into tables. Each table is passed by the menu buttons
        to the callback.
        The buttons are already packed in a table and connected to the
        callback function. 
        Events send by the activity buttons to the callback are the name of
        the activity by which the activity can be imported.
        @cbf should be a callback function accepting one argument.
        @parentbox must be a gtk.Vbox.
        """
        # We also define a tooltip object to register our tooltips.
        # This object is also passed to the caller.
        tooltips = gtk.Tooltips()
        # Which kind of menu do we have?
        # This is set by the parser.
        if not self.menu:
            self.logger.critical("No menu found, probably parsing error")
            return None
        # at this moment only multilayer menus are supported
        if self.xm.which_menu() == 'normal':# normal is single level
            ocp_menu = {}
            ocp_menu['background'] = self.menu['background']
            ocp_menu['ocwcol'] = self.menu['ocwcol']
            del self.menu['background']
            del self.menu['ocwcol']
            l = self.setup_ocp_buttons(self.menu,cbf)
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
            for k,v in self.menu.items():
                table = self.setup_ocp_buttons(v,cbf,tooltips)
                table.hide_all()
                # add table to the box
                parentbox.pack_start(table,False,False,0)
                img,pos = k
                # we ignore the pos parameter as we don't use fixed positions in GTK
                box = xpm_label_box(img)
                but = gtk.Button()
                tooltips.set_tip(but, _("Arithmetic's activity menu."))
                # The submenu buttons are connected with the list with associated 
                # submenu buttons as their data. We actually use the Gobject framework
                # to store our activity menu buttons list.
                # each of them also connected to the same callback function.
                # see Activity.menu_callback for details how we handle this.
                but.connect('clicked', cbf, table)
                but.add(box)
                but.show()
                l.append(but)
            ocp_menu['kind'] = 'multi'
            # This differs from a normal menu, here we put a list with ocp buttons
            # which pass a table with ocp buttons as argument to the callback.
            ocp_menu['menu'] = l
        return (tooltips,ocp_menu)
    
    def setup_ocp_buttons(self,menudict,cbf,tooltips):
        # TODO: find a way to fix these hardcoded values
        rw = 10
        cl = 20
        tb = gtk.Table(rows=rw, columns=cl, homogeneous=False)
        # populate table
        itemslist = menudict.items()
        # we setup a new list to sort the menu items
        newitemslist = []
        for item in itemslist:
            sortkey = item[1][1]
            newitemslist.append((sortkey,item))
        newitemslist.sort()
        # and revert it back into a sorted itemslist
        itemslist = []
        for item in newitemslist:
            itemslist.append(item[1])
        #print "itemslist",itemslist
        for item in itemslist:
            k,v = item
            img, pos,ttip = v
            r = pos[0]
            c = pos[1]
            #print "menu button",pos
            if not os.path.exists(img) and self.theme != 'default':
                file = os.path.join(self.defaultpath,os.path.basename(img))
            box = xpm_label_box(img)# we don't use text in the activity buttons
            but = gtk.Button()
            tooltips.set_tip(but,ttip)
            but.connect('clicked', cbf, k)
            but.add(box)
            # The button isn't shown, we let the parent do that.
            tb.attach(but,c,c+1,r,r+1,xoptions=False, yoptions=False, xpadding=4, ypadding=4)
        return tb
    
if __name__ == '__main__':
    
    import SPLogging
    SPLogging.set_level('debug')
    SPLogging.start()
    import gtk
    import pprint,types
        
    def callback(widget,table):
        global window,mainbox
        #print "received widget: %s with data: %s" % (widget,table)
        if type(table) is types.UnicodeType:
            #print "received module name: %s" % table
            pass
        else:
            # first we hide every table
            for child in mainbox.get_children():
                child.hide_all()
            # and then we only show the table we received
            table.show_all()
            mainbox.show()
    
    # this will become the main box to hold button tables
    mainbox = gtk.VBox(False, 0)
    m = MainMenu(os.path.join(os.getcwd(),'lib/SPData/menu/default'),'SP_menu.xml')
    tooltips, menu = m.get_menuitems(callback,mainbox)
    if not menu:
        print "no menu received, parsing error"
        sys.exit(1)

    # mainbox is now populated
    mainbox.hide_all()# to be sure
       
    print "Parsed menu"
    pprint.pprint(menu)
    
    # get a gtk window to show buttons  
    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    window.set_default_size(300,300)
    window.connect("delete_event", lambda a1,a2:gtk.main_quit())
    window.set_border_width(10)
    
    winbox = gtk.VBox(False,0)
    window.add(winbox)
    
    topbox = gtk.HBox(False,0)
    for menubut in menu['menu']:
        topbox.pack_start(menubut,False,False,4)
    winbox.pack_start(topbox,False,False,4)
    window.show_all()
    
    winbox.pack_start(mainbox,False,False,4)

    window.show()
    gtk.main()
        
        
        
