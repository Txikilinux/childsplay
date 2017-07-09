# $Id: ListViewPort.py,v 1.14.2.3 2006/09/16 11:28:20 marcusva Exp $
#
# Copyright (c) 2004-2006, Marcus von Appen
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

"""ViewPort proxy class for the ScrolledList."""

from pygame import Rect
from childsplay_sp.ocempgui.draw import Draw
from childsplay_sp.ocempgui.widgets.components import ListItemCollection
from childsplay_sp.ocempgui.widgets.components import TextListItem, FileListItem
from ViewPort import ViewPort
from Bin import Bin
from Constants import *
from StyleInformation import StyleInformation
import base

class ListViewPort (ViewPort):
    """ListViewPort (scrolledlist) -> ListViewPort

    A ViewPort proxy for ListItem objects.

    The ListViewPort is a proxy class, which is attached as widget to
    the ScrolledList. It takes care of updating and drawing the attached
    list items.

    The ListViewPort implements out-of-the-box support for the
    TextListItem and FileListItem classes and possible inheritors of
    those. If you want to to draw an own ListItem type, you should
    create a subclass, which overrides the draw_item() method according
    to your needs.

    To guarantee a correct behaviour, the attributes or methods of the
    ListViewPort should not be modified at runtime in any way. Instead a
    subclass should be created, which overrides the necessary parts.
    
    Default action (invoked by activate()):
    None
    
    Mnemonic action (invoked by activate_mnemonic()):
    None

    Attributes:
    images       - A dict containing the surfaces for the attached items.
    scrolledlist - The ScrolledList, the ListViewPort is attached to.
    """
    def __init__ (self, scrolledlist):
        self._scrolledlist = scrolledlist
        self._images = {}
        self._realwidth = 0
        self._realheight = 0
        ViewPort.__init__ (self, None)

    def get_real_width (self):
        """L.get_real_width () -> int

        Gets the real width occupied by the ListViewPort.
        """
        return self._realwidth

    def get_real_height (self):
        """L.get_real_height () -> int

        Gets the real height occupied by the ListViewPort.
        """
        return self._realheight

    def get_item_at_pos (self, position):
        """L.get_item_at_pos (...) -> ListItem

        Gets the item at the passed position coordinates.
        """
        eventarea = self.rect_to_client ()
        if not eventarea.collidepoint (position):
            return None
        position = position[0] - eventarea.left, position[1] - eventarea.top
        
        border = base.GlobalStyle.get_border_size \
                 (self.__class__, self.style,
                  StyleInformation.get ("ACTIVE_BORDER")) * 2

        posy = self.vadjustment
        items = self.scrolledlist.items
        width = eventarea.width
        bottom = eventarea.bottom
        images = self.images
        spacing = self.scrolledlist.spacing

        for item in items:
            rect = Rect (images [item][1])
            rect.y = posy
            rect.width = width + border
            if rect.bottom > bottom:
                rect.height = bottom - rect.bottom + border
            if rect.collidepoint (position):
                return item
            posy += images[item][1].height + spacing + border
        return None
    
    def get_item_position (self, item):
        """L.get_item_position (...) -> int, int

        Gets the relative position coordinates of an item.
        """
        y = 0
        items = self.scrolledlist.items
        active = base.GlobalStyle.get_border_size \
                 (self.__class__, self.style,
                  StyleInformation.get ("ACTIVE_BORDER")) * 2
        spacing = self.scrolledlist.spacing
        border = base.GlobalStyle.get_border_size \
                 (self.__class__, self.style,
                  StyleInformation.get ("VIEWPORT_BORDER"))

        for it in items:
            if it == item:
                break
            y += self._images[item][1].height + spacing + active
        return self.left + border, self.top + y + border
    
    def update_items (self):
        """L.update_items () -> None

        Updates the attached items of the ScrolledList.
        """
        draw_item = self.draw_item
        spacing = self.scrolledlist.spacing
        width, height = 0, 0
        items = self.scrolledlist.items
        engine = base.GlobalStyle.engine
        border = base.GlobalStyle.get_border_size \
                     (self.__class__, self.style,
                      StyleInformation.get ("ACTIVE_BORDER")) * 2

        for item in items:
            if item.dirty:
                item.dirty = False
                rect = draw_item (item, engine)[1]
            else:
                rect = self._images[item][1]
            if width < rect.width:
                width = rect.width
            height += rect.height + spacing + border

        # The last item does not need any spacing.
        if height > 0:
            height -= spacing

        # Set the step value of the attached scrolledlist.
        step = 1
        if items.length > 0:
            step = height / items.length + spacing / 2
        self.scrolledlist.vscrollbar.step = step

        self._realwidth = width + border
        self._realheight = height
        self.dirty = True
    
    def draw_item (self, item, engine):
        """L.draw_item (...) -> Surface

        Redraws a sepcific item.
        """
        surface = None
        if isinstance (item, FileListItem):
            surface = engine.draw_filelistitem (self, item)
        elif isinstance (item, TextListItem):
            surface = engine.draw_textlistitem (self, item)
        else:
            raise TypeError ("Unsupported item type %s" % type (item))
        val = (surface, surface.get_rect ())
        self._images[item] = val
        return val
    
    def draw (self):
        """L.draw () -> None

        Draws the ListViewPort surface and places its items on it.
        """
        Bin.draw (self)
        style = base.GlobalStyle
        cls  = self.__class__
        color = StyleInformation.get ("SELECTION_COLOR")
        active = StyleInformation.get ("ACTIVE_BORDER")
        border_active = style.get_border_size (cls, self.style, active)
        border = style.get_border_size \
                 (cls, self.style, StyleInformation.get ("VIEWPORT_BORDER"))
        active_space = StyleInformation.get ("ACTIVE_BORDER_SPACE")
        st = self.style
        state = self.state
        realwidth = self.real_width

        posy = 0
        draw_rect = Draw.draw_rect
        sdraw_rect = style.engine.draw_rect
        sdraw_border = style.engine.draw_border

        spacing = self.scrolledlist.spacing
        width = self.width - 2 * border
        height = self.height - 2 * border
        selheight = 0
        surface = None

        cursor_found = False
        cursor = self.scrolledlist.cursor
        items = self.scrolledlist.items
        focus = self.scrolledlist.focus
        images = self.images

        lower = abs (self.vadjustment) - spacing - 2 * border_active
        upper = abs (self.vadjustment) + height

        # Overall surface
        surface_all = sdraw_rect (max (realwidth, width), self.real_height,
                                  state, cls, st)
        blit = surface_all.blit

        for item in items:
            image, rect = images[item]

            # Draw only those which are visible.
            if (posy + rect.height < lower):
                posy += rect.height + 2 * border_active + spacing
                continue
            elif posy > upper:
                break
            
            selheight = rect.height + 2 * border_active
            if item.selected:
                # Highlight the selection.
                surface = draw_rect (max (width, realwidth), selheight, color)

                # Show input focus.
                if focus and (item == cursor):
                    sdraw_border (surface, state, cls, st, active,
                                  space=active_space)
                    cursor_found = True
                surface.blit (image, (border_active, border_active))
                blit (surface, (0, posy))

            elif focus and not cursor_found and (item == cursor):
                # Input focus.
                surface = sdraw_rect (max (width, realwidth), selheight, state,
                                      cls, st)
                sdraw_border (surface, state, cls, st, active,
                              space=active_space)
                surface.blit (image, (border_active, border_active))
                cursor_found = True
                blit (surface, (0, posy))
            else:
                # Regular image, move by the active border, so that
                # all items have the correct offset.
                blit (image, (border_active, posy + border_active))

            posy += selheight + spacing
        
        self.image.blit (surface_all, (border, border),
                         (abs (self.hadjustment), abs (self.vadjustment),
                          width, height))
        
    images = property (lambda self: self._images,
                       doc = "Dictionary of the item surfaces.")
    scrolledlist = property (lambda self: self._scrolledlist,
                             doc = "The ScrolledList of the ListViewPort.")
