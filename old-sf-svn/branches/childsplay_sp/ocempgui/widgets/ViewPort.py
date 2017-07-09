# $Id: ViewPort.py,v 1.9.2.2 2006/09/14 23:32:01 marcusva Exp $
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

"""A proxy class for widgets, that need to be scrolled."""

from pygame import Rect
from Bin import Bin
from BaseWidget import BaseWidget
from StyleInformation import StyleInformation
import base

class ViewPort (Bin):
    """ViewPort (widget) -> ViewPort

    A proxy class for widgets, which need scrolling abilities.

    The ViewPort class allows widgets to be scrolled by virtually adding
    horizontal and vertical offsets to the respective methods such as
    rect_to_client().

    Widgets which make use of the ViewPort class can easily scroll the
    encapsulated child(ren) by modifying the 'hadjustment' and
    'vadjustment' attributes of the ViewPort.

    viewport.hadjustment = 10 # Add a 10px horizontal offset.
    viewport.set_vadjustment (-15) # Reduce by a 15px vertical offset.

    The ViewPort however does not provide advanced scrolling features
    such as scrollbars. Instead it should be bound as child to a widget,
    which will implement such additives. Widgets, which make use of the
    ViewPort's functionality can receive the absolute width and height
    occupied by the ViewPorts child(ren) using the 'real_width' and
    'real_height' attributes and their respective methods.

    # Get the total width and height occupied by the ViewPort child.
    abswidth = viewport.real_width
    absheight = viewport.get_real_height ()

    Concrete usage and inheritance implementations of the ViewPort can
    be found in the ScrolledWindow, ListViewPort and ScrolledList
    classes.

    Default action (invoked by activate()):
    None
    
    Mnemonic action (invoked by activate_mnemonic()):
    None

    Attributes:
    
    """
    def __init__ (self, widget):
        Bin.__init__ (self)
        self._hadjustment = 0
        self._vadjustment = 0
        if widget:
            self.minsize = widget.size
        else:
            self.minsize = 10, 10
        self.child = widget

    def set_focus (self, focus=True):
        """V.set_focus (focus=True) -> None

        Overrides the set_focus() behaviour for the ViewPort.

        The ViewPort class is not focusable by default. It is a layout
        class for other widgets, so it does not need to get the input
        focus and thus it will return false without doing anything.
        """
        return False

    def set_hadjustment (self, value):
        """V.set_hadjustment (...) -> None

        Sets the horizontal adjustment to scroll.

        Raises a TypeError, if the passed argument is not an integer.
        """
        if type (value) != int:
            raise TypeError ("value must be an integer")
        self._hadjustment = value
        self.dirty = True

    def set_vadjustment (self, value):
        """V.set_vadjustment (...) -> None

        Sets the vertical adjustment to scroll.

        Raises a TypeError, if the passed argument is not an integer.
        """
        if type (value) != int:
            raise TypeError ("value must be an integer")
        self._vadjustment = value
        self.dirty = True

    def get_real_width (self):
        """V.get_real_width () -> int

        Gets the real width occupied by the ViewPort.
        """
        if self.child:
            return self.child.width
        return self.width

    def get_real_height (self):
        """V.get_real_height () -> int

        Gets the real height occupied by the ViewPort.
        """
        if self.child:
            return self.child.height
        return self.height

    def rect_to_client (self, rect=None):
        """V.rect_to_client () -> pygame.Rect

        Returns the absolute coordinates a rect is located at.

        If a rect argument is passed, its size and position are modified
        to match the criteria of the scrolling adjustments of the
        ViewPort. Besides that it exactly behaves like the original
        rect_to_client() method.
        """
        if rect:
            border = base.GlobalStyle.get_border_size \
                     (self.__class__, self.style,
                      StyleInformation.get ("VIEWPORT_BORDER"))
            rect.x = self.x + rect.x
            rect.y = self.y + rect.y
            if rect.right > self.right - border:
                rect.width = self.right - border - rect.left
            if rect.bottom > self.bottom - border:
                rect.height = self.bottom - border - rect.top

            if (self.parent != None) and isinstance (self.parent, BaseWidget):
                return self.parent.rect_to_client (rect)
            return rect
        return Bin.rect_to_client (self)

    def draw_bg (self):
        """V.draw_bg () -> Surface

        Draws the ViewPort background surface and returns it.

        Creates the visible surface of the ViewPort and returns it to the
        caller.
        """
        return base.GlobalStyle.engine.draw_viewport (self)
        
    def draw (self):
        """V.draw () -> None

        Draws the ViewPort surface and places its child on it.
        """
        border = base.GlobalStyle.get_border_size \
                 (self.__class__, self.style,
                  StyleInformation.get ("VIEWPORT_BORDER"))
        Bin.draw (self)

        if self.child:
            self.child.topleft = border + self.hadjustment, \
                                 border + self.vadjustment
            self.image.blit (self.child.image, (border, border),
                             (abs (self.hadjustment), abs (self.vadjustment),
                              self.width - 2 * border,
                              self.height - 2 * border))

    def update (self, **kwargs):
        """V.update (...) -> None

        Updates the ViewPort.

        Updates the ViewPort and causes its parent to update itself on
        demand.
        """
        if not self.dirty:
            border = base.GlobalStyle.get_border_size \
                     (self.__class__, self.style,
                      StyleInformation.get ("VIEWPORT_BORDER"))
            resize = kwargs.get ("resize", False)

            children = kwargs.get ("children", {})
            blit = self.image.blit
            items = children.items ()

            # Clean up the dirty areas on the widget.
            vals = []
            for child, rect in items:
                blit (self._bg, rect, rect)

                # r will be the area for the blit.
                r = Rect (abs (self.hadjustment), abs (self.vadjustment),
                          self.width - 2 * border, self.height - 2 * border)
                blit (child.image, (border, border), r)
                vals.append (r)

            # If a parent's available, reassign the child rects, so that
            # they point to the absolute position on the widget and build
            # one matching them all for an update.
            if self.parent:
                rect = Rect (self._oldrect)
                if len (vals) != 0:
                    for r in vals:
                        r.x += self.x
                        r.y += self.y
                    rect.unionall (vals[1:])
                self.parent.update (children={ self : rect }, resize=resize)
            self._lock = max (self._lock - 1, 0)
        else:
            Bin.update (self, **kwargs)
    
    hadjustment = property (lambda self: self._hadjustment,
                            lambda self, var: self.set_hadjustment (var),
                            doc = "The horizontal scrolling adjustment.")
    vadjustment = property (lambda self: self._vadjustment,
                            lambda self, var: self.set_vadjustment (var),
                            doc = "The vertical scrolling adjustment.")
    real_width = property (lambda self: self.get_real_width (),
                           doc = "The real width occupied by the ViewPort.")
    real_height = property (lambda self: self.get_real_height (),
                            doc = "The real height occupied by the ViewPort.")
