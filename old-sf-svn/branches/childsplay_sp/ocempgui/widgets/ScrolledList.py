# $Id: ScrolledList.py,v 1.61.2.6 2007/03/26 11:44:41 marcusva Exp $
#
# Copyright (c) 2004-2007, Marcus von Appen
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

"""A scrollable widget, which contains list elements."""

from pygame import KMOD_SHIFT, KMOD_CTRL, K_UP, K_DOWN, K_HOME, K_END, K_SPACE
from pygame import K_a, key
from childsplay_sp.ocempgui.widgets.components import ListItemCollection
from ScrolledWindow import ScrolledWindow
from ListViewPort import ListViewPort
from Constants import *
from StyleInformation import StyleInformation
import base

class ScrolledList (ScrolledWindow):
    """ScrolledList (width, height, collection=None) -> ScrolledList

    A widget class, that populates elements in a list-style manner.

    The ScrolledList displays data in a listed form and allows to browse
    through it using horizontal and vertical scrolling. Single or
    multiple items of the list can be selected or - dependant on the
    ListItem object - be edited, etc.

    The ScrolledList's child is a ListViewPort object, which takes care
    of drawing the attached list items. You can supply your own
    ListViewPort object through the 'child' attribute as described in
    the Bin class documentation.

    To set or reset an already created collection of items, the 'items'
    attribute and set_items() method can be used. The collection to set
    needs to be a ListItemCollection object.

    myitems = ListItemCollection()
    myitems.append (TextListItem ('First')
    scrolledlist.items = myitems
    scrolledlist.set_items (myitems)

    The ScrolledList allows different types of selections by modifying
    the 'selectionmode' attribute. Dependant on the set selection mode,
    you can then select multiple items at once (SELECTION_MULTIPLE),
    only one item at a time (SELECTION_SINGLE) or nothing at all
    (SELECTION_NONE). Modifying the selection mode does not have any
    effect on a currently made selection. See the selection constants
    section in the Constants documentation for more details.

    scrolledlist.selectionmode = SELECTION_NONE
    scrolledlist.set_selectionmode (SELECTION_SINGLE)

    To improve the appearance and selection behaviour of the single list
    items, the ScrolledList support additional spacing to place between
    them. It can be read and set through the 'spacing' attribute and
    set_spacing() method.

    scrolledlist.spacing = 4
    scrolledlist.set_spacing (0)
    
    Default action (invoked by activate()):
    See the ScrolledWindow class.
    
    Mnemonic action (invoked by activate_mnemonic()):
    None
    
    Signals:
    SIG_SELECTCHANGED - Invoked, when the item selection changed.
    SIG_LISTCHANGED   - Invoked, when the underlying item list changed.
    
    Attributes:
    items         - Item list of the ScrolledList.
    selectionmode - The selection mode for the ScrolledList. Default is
                    SELECTION_MULTIPLE.
    spacing       - Spacing to place between the list items. Default is 0.
    cursor        - The currently focused item.
    """
    def __init__ (self, width, height, collection=None):
        # Temporary placeholder for kwargs of the update() method.
        self.__lastargs = None

        ScrolledWindow.__init__ (self, width, height)

        self._spacing = 0

        # The item cursor position within the list.
        self._cursor = None

        # Used for selections.
        self._last_direction = None

        self._signals[SIG_LISTCHANGED] = []
        self._signals[SIG_SELECTCHANGED] = []

        # Items and selection.
        self._itemcollection = None
        self._selectionmode = SELECTION_MULTIPLE
        if collection:
            self.set_items (collection)
        else:
            self._itemcollection = ListItemCollection ()
            self._itemcollection.list_changed = self._list_has_changed
            self._itemcollection.item_changed = self._item_has_changed
        self.child = ListViewPort (self)

    def _list_has_changed (self, collection):
        """S._list_has_changed (...) -> None

        Update method for list_changed () notifications.
        """
        if not self.locked:
            self.child.update_items ()
            self.dirty = True
        self.run_signal_handlers (SIG_LISTCHANGED)

    def _item_has_changed (self, item):
        """S._item_has_changed (...) -> None

        Update method for item_changed() notifications.
        """
        if not self.locked:
            self.child.update_items ()

    def set_items (self, items):
        """S.set_items (...) -> None

        Sets a collection of items to display.
        """
        old = self._itemcollection
        self.vscrollbar.value = 0
        self.hscrollbar.value = 0
        if isinstance (items, ListItemCollection):
            self._itemcollection = items
        else:
            self._itemcollection = ListItemCollection (items)
        self._itemcollection.list_changed = self._list_has_changed
        self._itemcollection.item_changed = self._item_has_changed
        old.list_changed = None
        old.item_changed = None
        del old

        if len (self._itemcollection) > 0:
            self._cursor = self._itemcollection[0]
        else:
            self._cursor = None
        
        self._list_has_changed (self._itemcollection)

    def set_focus (self, focus=True):
        """S.set_focus (...) -> bool

        Sets the input and action focus of the ScrolledList.
        
        Sets the input and action focus of the ScrolledList and returns
        True upon success or False, if the focus could not be set.
        """
        if focus != self.focus:
            self.lock ()
            if focus and not self._cursor and (len (self.items) > 0):
                self._cursor = self.items[0]
                self._cursor.selected = True
            ScrolledWindow.set_focus (self, focus)
            self.unlock ()
        return self.focus
    
    def set_spacing (self, spacing):
        """S.set_spacing (...) -> None

        Sets the spacing to place between the list items of the ScrolledList.

        The spacing value is the amount of pixels to place between the
        items of the ScrolledList.

        Raises a TypeError, if the passed argument is not a positive
        integer.
        """
        if (type (spacing) != int) or (spacing < 0):
            raise TypeError ("spacing must be a positive integer")
        self._spacing = spacing
        self.child.update_items ()

    def set_selectionmode (self, mode):
        """S.set_selectionmode (...) -> None

        Sets the selection mode for the ScrolledList.

        The selection mode can be one of the SELECTION_TYPES list.
        SELECTION_NONE disables selecting any list item,
        SELECTION_SINGLE allows to select only one item from the list and 
        SELECTION_MULTIPLE allows to select multiple items from the list.

        Raises a ValueError, if the passed argument is not a value of
        the SELECTION_TYPES tuple.
        """
        if mode not in SELECTION_TYPES:
            raise ValueError ("mode must be a value from SELECTION_TYPES")
        self._selectionmode = mode

    def select (self, *items):
        """S.select (...) -> None

        Selects one or more specific items of the ScrolledList.

        Dependant on the set selection mode selecting an item has
        specific side effects. If the selection mode is set to
        SELECTION_SINGLE, selecting an item causes any other item to
        become deselected. As a counterpart SELECTION_MULTIPLE causes
        the items to get selected while leaving any other item untouched.
        The method causes the SIG_SELECTCHANGED event to be emitted,
        whenever the selection changes.

        Raises a LookupError, if the passed argument could not be
        found in the items attribute.
        """
        self.__select (*items)
        self.run_signal_handlers (SIG_SELECTCHANGED)

    def select_all (self):
        """S.select_all () -> None

        Selects all items of the ScrolledList.

        Selects all items of the ScrolledList, if the selection mode is
        set to SELECTION_MULTIPLE
        """
        if self.selectionmode == SELECTION_MULTIPLE:
            notselected = filter (lambda x: x.selected == False, self.items)
            for i in notselected:
                i.selected = True
            if len (notselected) > 0:
                self.run_signal_handlers (SIG_SELECTCHANGED)
    
    def deselect (self, *items):
        """S.deselect (...) -> None
        
        Deselects the specified items in the ScrolledList.

        The method causes the SIG_SELECTCHANGED event to be emitted, when
        the selection changes.

        Raises a LookupError, if the passed argument could not be
        found in the items attribute.
        """
        self.__deselect (*items)
        self.run_signal_handlers (SIG_SELECTCHANGED)

    def __select (self, *items):
        """S.__select (...) -> None
        
        Selects one or more specific items of the ScrolledList.
        """
        if self.selectionmode == SELECTION_NONE:
            # Do nothing here, maybe implement a specific event action
            # or s.th. like that...
            return

        self.lock ()
        if self.selectionmode == SELECTION_SINGLE:
            # Only the last item.
            if items[-1] not in self.items:
                raise LookupError ("item could not be found in list")
            items[-1].selected = True

        elif self.selectionmode == SELECTION_MULTIPLE:
            for item in items:
                if item not in self.items:
                    raise LookupError ("item could not be found in list")
                item.selected = True
        self.unlock ()

    def __deselect (self, *items):
        """S.__deselect (..:) -> None

        Deselects the specified items in the ScrolledList
        """
        self.lock ()
        for item in items:
            if item not in self.items:
                raise LookupError ("item could not be found in list")
            item.selected = False
            self.child.update_items ()
        self.unlock ()

    def get_selected (self):
        """S.get_selected () -> list

        Returns a list cotaining the selected items.
        """
        if self.items.length != 0:
            return [item for item in self.items if item.selected]
        return []

    def set_cursor (self, item, selected):
        """S.set_cursor (...) -> None

        Sets the cursor index to the desired item.
        """
        self._cursor = item
        self._scroll_to_cursor ()
        if item.selected == selected:
            self.child.dirty = True # Render the cursor
        else:
            item.selected = selected
            self.run_signal_handlers (SIG_SELECTCHANGED)

    def _cursor_next (self, selected):
        """S._cursor_next () -> None

        Advances the cursor to the next item in the list.
        """
        if not self._cursor:
            if self.items.length > 0:
                self._cursor = self.items[0]
            return
        index = self.items.index (self._cursor)
        if index < self.items.length - 1:
            self.set_cursor (self.items[index + 1], selected)

    def _cursor_prev (self, selected):
        """S._cursor_prev () -> None

        Advances the cursor to the previous item in the list.
        """
        if not self._cursor:
            if self.items.length > 0:
                self._cursor = self.items[0]
            return
        index = self.items.index (self._cursor)
        if index > 0:
            self.set_cursor (self.items[index - 1], selected)
        
    def _scroll_to_cursor (self):
        """S._scroll_to_cursor () -> None

        Scrolls the list to the cursor.
        """
        if not self.cursor or not self.child.images.has_key (self.cursor):
            return

        border = base.GlobalStyle.get_border_size \
                     (self.child.__class__, self.child.style,
                      StyleInformation.get ("ACTIVE_BORDER")) * 2

        x, y = self.child.get_item_position (self.cursor)
        w, h = self.child.width, self.child.height
        height = self.child.images[self.cursor][1].height + border + \
                 self.spacing
        # Bottom edge of the item.
        py = y + height

        if (self.vscrollbar.value - y > 0): # Scrolling up.
            self.vscrollbar.value = max (0, y - border)
        elif (py > self.vscrollbar.value + h):
            self.vscrollbar.value = min (abs (py - h + border),
                                         self.vscrollbar.maximum)
        
    def _navigate (self, key, mod):
        """S._navigate (key) -> None

        Deals with keyboard navigation.
        """
        multiselect = self.selectionmode == SELECTION_MULTIPLE
        selected = not mod & KMOD_CTRL and self.selectionmode != SELECTION_NONE
        
        if key == K_UP:
            if (mod & KMOD_SHIFT) and multiselect:
                if self._last_direction == K_DOWN:
                    if len (self.get_selected ()) > 1:
                        self._cursor.selected = False
                        self._cursor_prev (True)
                        return
                self._last_direction = key
                self._cursor_prev (True)
                return
            self.__deselect (*self.get_selected ())
            self._cursor_prev (selected)
        
        elif key == K_DOWN:
            if (mod & KMOD_SHIFT) and multiselect:
                if self._last_direction == K_UP:
                    if len (self.get_selected ()) > 1:
                        self._cursor.selected = False
                        self._cursor_next (True)
                        return
                self._last_direction = key
                self._cursor_next (True)
                return
            self.__deselect (*self.get_selected ())
            self._cursor_next (selected)

        elif key == K_END:
            if (mod & KMOD_SHIFT) and multiselect:
                start = self.items.index (self._cursor)
                items = self.get_selected ()
                self.__deselect (*items)
                if self._last_direction == K_UP:
                    if len (items) > 0:
                        start = self.items.index (items[-1])
                end = len (self.items) - 1
                self.__select (*self.items[start:end])
            else:
                self.__deselect (*self.get_selected ())
            self._last_direction = K_DOWN
            self.set_cursor (self.items[-1], selected)
            
        elif key == K_HOME:
            if (mod & KMOD_SHIFT) and multiselect:
                end = self.items.index (self._cursor)
                items = self.get_selected ()
                self.__deselect (*items)
                if self._last_direction == K_DOWN:
                    if len (items) > 0:
                        end = self.items.index (items[0])
                self.__select (*self.items[0:end])
            else:
                self.__deselect (*self.get_selected ())
            self._last_direction = K_UP
            self.set_cursor (self.items[0], selected)
        
        elif key == K_SPACE:
            if self._cursor.selected:
                self.set_cursor (self._cursor, False)
            else:
                self.set_cursor (self._cursor, True)

        elif (key == K_a) and mod & KMOD_CTRL and \
                 multiselect:
            self._last_direction = K_DOWN
            self.lock ()
            notselected = filter (lambda x: x.selected == False, self.items)
            for i in notselected:
                i.selected = True
            self.unlock ()
            self.set_cursor (self.items[-1], True)

    def _click (self, position):
        """S._click (...) -> None

        Deals with mouse clicks.
        """
        # Get the item and toggle the selection.
        item = self.child.get_item_at_pos (position)
        mods = key.get_mods ()
        if not item:
            return

        if self.selectionmode != SELECTION_MULTIPLE:
            self._last_direction = None
            selection = self.get_selected ()
            allowed = self.selectionmode != SELECTION_NONE
            if mods & KMOD_CTRL:
                if selection and item in selection:
                    selection.remove (item)
                self.__deselect (*selection)
                self.set_cursor (item, not item.selected and allowed)
            else:
                self.__deselect (*selection)
                self.set_cursor (item, allowed)
            return
        
        if item.selected:
            if mods & KMOD_CTRL:
                self.set_cursor (item, False)
            elif mods & KMOD_SHIFT:
                # The item usually should be somewhere in that selection.
                # Get its index and crop the selection according to that
                # index.
                selection = self.get_selected ()
                if len (selection) > 1:
                    start = self.items.index (selection[0])
                    end = self.items.index (selection[-1])
                    index = selection.index (item)
                    if self._last_direction == K_UP:
                        if index > 0:
                            self.__deselect (*selection[0:index])
                    elif self._last_direction == K_DOWN:
                        if index > 0:
                            self.__deselect (*selection[index:end + 1])
                    self.set_cursor (item, True)
                else:
                    self.set_cursor (selection[0], True)
            else:
                self._last_direction = None
                self.__deselect (*self.get_selected ())
                self.set_cursor (item, True)
        else:
            if mods & KMOD_CTRL:
                self.set_cursor (item, True)
            elif mods & KMOD_SHIFT:
                # No click on an existing selection. Expand the current.
                selection = self.get_selected ()
                start = self.items.index (self.cursor)
                index = self.items.index (item)
                if len (selection) != 0:
                    if self._last_direction == K_DOWN:
                        start = self.items.index (selection[0])
                        end = self.items.index (selection[-1])
                        if index < start:
                            self._last_direction = K_UP
                            self.__deselect (*selection)
                            self.__select (*self.items[index:start])
                        elif index > end:
                            self.__select (*self.items[end:index])
                        
                    elif self._last_direction == K_UP:
                        start = self.items.index (selection[0])
                        end = self.items.index (selection[-1])
                        if index > end:
                            self._last_direction = K_DOWN
                            self.__deselect (*selection)
                            self.__select (*self.items[end + 1:index])
                        elif index < start:
                            self.__select (*self.items[index:start])

                    else:
                        start = self.items.index (selection[0])
                        if index > start:
                            self.__select (*self.items[start:index])
                            self._last_direction = K_DOWN
                        else:
                            self.__select (*self.items[index:start])
                            self._last_direction = K_UP
            
                self.set_cursor (item, True)
            else:
                self._last_direction = None
                self.__deselect (*self.get_selected ())
                self.set_cursor (item, True)
    
    def notify (self, event):
        """S.notify (...) -> None

        Notifies the ScrolledList about an event.
        """
        if not self.sensitive:
            return

        if self.focus and (event.signal == SIG_KEYDOWN):
            if len (self.items) > 0:
                self._navigate (event.data.key, event.data.mod)
                event.handled = True
        elif event.signal == SIG_MOUSEDOWN:
            eventarea = self.rect_to_client ()
            if eventarea.collidepoint (event.data.pos):
                for c in self.controls:
                    c.notify (event)
                if not event.handled:
                    self.focus = True
                    self.run_signal_handlers (SIG_MOUSEDOWN, event.data)
                    if event.data.button == 1:
                        self._click (event.data.pos)
                    else:
                        ScrolledWindow.notify (self, event)
                event.handled = True
        else:
            ScrolledWindow.notify (self, event)

    selectionmode = property (lambda self: self._selectionmode,
                              lambda self, var: self.set_selectionmode (var),
                              doc = "The selection mode for the ScrolledList.")
    spacing = property (lambda self: self._spacing,
                        lambda self, var: self.set_spacing (var),
                        doc = "Additional spacing to place between the items.")
    items = property (lambda self: self._itemcollection,
                      lambda self, var: self.set_items (var),
                      doc = "The item collection of the ScrolledList.")
    cursor = property (lambda self: self._cursor,
                       doc = "The item, which is currently focused.")
