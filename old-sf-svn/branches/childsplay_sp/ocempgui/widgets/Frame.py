# $Id: Frame.py,v 1.34.2.6 2007/09/23 07:37:49 marcusva Exp $
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

"""Widget classes, which can place their chidren in a horizontal or
vertical alignment.
"""

from Container import Container
from BaseWidget import BaseWidget
from Constants import *
import base

class Frame (Container):
    """Frame (widget=None) -> Frame

    A container widget class with decorative border.

    The Frame widget is a container widget, which can draw a decorative
    border around its children and supports a title widget, which will
    be displayed in the topleft corner of the frame. It also supports
    alignment of its children.

    The 'align' attribute and set_align() method allow enable the frame
    to align its children. Dependant on the alignment type (see also
    ALIGN_TYPES) and the concrete Frame implementation, the children
    will be placed differently within the frame.

    frame.align = ALIGN_TOP
    frame.set_align (ALIGN_TOP)

    The border to draw around the children can be influenced using the
    'border' attribute or set_border() method. The default is to draw a
    sunken border.

    frame.border = BORDER_ETCHED_IN
    frame.set_border (BORDER_ETCHED_IN)

    The 'widget' attribute contains the widget, which will be placed in
    the topleft corner of the frame. It is suitable as title widget and
    has no limitations about the type of the widget. It should be noted
    that the widget can be removed by assinging None or passing None to
    the set_title_widget() method. The old title widget of the Frame
    will be destroyed, if you reassign the property.

    frame.widget = Label ('Title')
    frame.set_title_widget (Label ('Title'))

    Default action (invoked by activate()):
    None
    
    Mnemonic action (invoked by activate_mnemonic()):
    None

    Attributes:
    align  - Alignment of the children.
    border - The border style to set for the frame.
    widget - Widget to put in the topleft corner of the frame.
    """
    def __init__ (self, widget=None):
        Container.__init__ (self)
        self._widget = None
        self._align = ALIGN_NONE
        self._border = BORDER_ETCHED_IN
        self.set_title_widget (widget)

    def set_focus (self, focus=True):
        """F.set_focus (focus=True) -> None

        Overrides the set_focus() behaviour for the Frame.

        The Frame class is not focusable by default. It is a layout
        class for other widgets, so it does not need to get the input
        focus and thus it will return false without doing anything.
        """
        return False

    def set_title_widget (self, widget):
        """F.set_title_widget (...) -> None

        Sets the widget to display in the topleft corner.

        Raises a TypeError, if the passed argument does not inherit from
        the BaseWidget class.
        """
        if widget and (not isinstance (widget, BaseWidget)):
            raise TypeError ("widget must inherit from BaseWidget")
        if self._widget:
            self._widget.parent = None
            self._controls.remove (self._widget)
            self._widget.destroy ()
        self._widget = widget
        if widget:
            widget.parent = self
            self._controls.append (widget)
            if (widget.manager == None) and (self.manager != None):
                widget.set_event_manager (self.manager)
        self.dirty = True

    def set_align (self, align):
        """F.set_align (...) -> None

        Sets the alignment for the widgets.

        Raises a TypeError, if the passed argument is not a value from
        ALIGN_TYPES.
        """
        if not constants_is_align (align):
            raise TypeError ("align must be a value from ALIGN_TYPES")
        self._align = align
        self.dirty = True

    def set_border (self, border):
        """F.set_border (...) -> None

        Sets the border type to be used by the Frame.

        Raises a ValueError, if the passed argument is not a value from
        BORDER_TYPES
        """
        if border not in BORDER_TYPES:
            raise ValueError ("border must be a value from BORDER_TYPES")
        self._border = border
        self.dirty = True

    def destroy (self):
        """F.destroy () -> None

        Destroys the Frame and removes it from its event system.
        """
        if self.widget:
            self.widget.parent = None
        Container.destroy (self)
    
    align = property (lambda self: self._align,
                      lambda self, var: self.set_align (var),
                      doc = "The alignment to use for the children.")
    border = property (lambda self: self._border,
                       lambda self, var: self.set_border (var),
                       doc = "The border style to set for the Frame.")
    widget = property (lambda self: self._widget,
                       lambda self, var: self.set_title_widget (var),
                       doc = "The title widget to set for the Frame.")

class HFrame (Frame):
    """HFrame (widget=None) -> HFrame

    A Frame widget class, which place its children horizontally.

    The HFrame class places its attached children in a horizontal manner
    and supports an alignment at the top or bottom of its edges.
    Left or right alignment settings will be ignored by it. 

    Default action (invoked by activate()):
    None
    
    Mnemonic action (invoked by activate_mnemonic()):
    None
    """
    def __init__ (self, widget=None):
        Frame.__init__ (self, widget)

    def calculate_size (self):
        """H.calculate_size () -> int, int

        Calculates the size needed by the children.

        Calculates the size needed by the children and returns the
        resulting width and height.
        """
        border = base.GlobalStyle.get_border_size (self.__class__, self.style,
                                                   self.border)

        width = 2 * (self.padding + border)
        height = 0
        add_width = 0
        add_top = border
        spacing = self.spacing
        
        # Calculate the widget sizes.
        if self.widget:
            add_width = self.widget.width
            if self.widget.height > border:
                add_top = self.widget.height

        for widget in self.children:
            width += widget.width + spacing
            if widget.height > height:
                height = widget.height
        if len (self.children) != 0:
            width -= spacing # The last one adds unnecessary spacing.
        if width <= add_width:
            width = add_width + 2 * (self.padding + border)
        # Only one border, the other one was added in add_top, if
        # necessary
        height += add_top + 2 * self.padding + border
        
        return width, height
    
    def dispose_widgets (self):
        """H.dispose_widgets (...) -> None

        Moves the children of the HFrame to their correct positions.
        """
        height = self.image.get_rect ().height
        border = base.GlobalStyle.get_border_size (self.__class__,self.style,
                                                   self.border)
        spacing = self.spacing
        padding = self.padding
        x = border + padding
        y = 0

        add_height = border
        if self.widget:
            self.widget.topleft = (x, y)
            y += self.widget.height + padding
            add_height = self.widget.height

        # Check the alignment.
        top = self.align & ALIGN_TOP == ALIGN_TOP
        bottom = self.align & ALIGN_BOTTOM == ALIGN_BOTTOM
        nothing = not top and not bottom
        
        centery = (height + add_height - border) / 2
        if nothing:
            for widget in self.children:
                y = centery - widget.height / 2
                widget.topleft = x, y
                x += widget.width + spacing
        elif bottom:
            for widget in self.children:
                y = (height - border - padding - widget.height)
                widget.topleft = x, y
                x += widget.width + spacing
        else:
            for widget in self.children:
                widget.topleft = x, y
                x += widget.width + spacing
    
    def draw_bg (self):
        """H.draw_bg () -> None

        Draws the HFrame background surface and returns it.

        Creates the visible surface of the HFrame and returns it to the
        caller.
        """
        return base.GlobalStyle.engine.draw_frame (self)

    def draw (self):
        """H.draw () -> None

        Draws the HFrame surface and places its children on it.
        """
        Frame.draw (self)

        self.dispose_widgets ()
        blit = self.image.blit

        if self.widget:
            blit (self.widget.image, self.widget.rect)
        for widget in self.children:
            blit (widget.image, widget.rect)

class VFrame (Frame):
    """
    A Frame widget class, which place its children vertically.

    The VFrame class places its attached children in a vertical manner
    and supports an alignment at the left or right of its edges. Top
    or bottom alignment settings will be ignored by it.

    Default action (invoked by activate()):
    None
    
    Mnemonic action (invoked by activate_mnemonic()):
    None
    """
    def __init__ (self, widget=None):
        Frame.__init__ (self, widget)

    def calculate_size (self):
        """V.calculate_size () -> int, int.

        Calculates the size needed by the children.

        Calculates the size needed by the children and returns the
        resulting width and height.
        """
        border = base.GlobalStyle.get_border_size (self.__class__, self.style,
                                                   self.border)

        width = 0
        height = 2 * self.padding + border
        add_width = 0
        add_top = border
        spacing = self.spacing
        
        # Calculate the widget sizes.
        if self.widget:
            add_width = self.widget.width
            if self.widget.height > border:
                add_top = self.widget.height
        height += add_top

        for widget in self.children:
            height += widget.height + spacing
            if widget.width > width:
                width = widget.width
        width += 2 * (self.padding + border)
        if width <= add_width:
            width = add_width + 2 * (self.padding + border)
        # Last one adds too much spacing.
        if len (self.children) != 0:
            height -= spacing

        return width, height
        
    def dispose_widgets (self):
        """V.dispose_widgets (...) -> None

        Moves the children of the VFrame to their correct positions.
        """
        width = self.image.get_rect ().width
        border = base.GlobalStyle.get_border_size (self.__class__, self.style,
                                                   self.border)
        spacing = self.spacing
        padding = self.padding
        x = padding + border
        y = 0

        add_height = border
        if self.widget:
            self.widget.topleft = x, y
            add_height = self.widget.height
        y += add_height + padding

        # Check the alignment.
        left = self.align & ALIGN_LEFT == ALIGN_LEFT
        right = self.align & ALIGN_RIGHT == ALIGN_RIGHT
        nothing = not left and not right

        centerx = width / 2
        if nothing:
            for widget in self.children:
                x = centerx - widget.width / 2
                widget.topleft = x, y
                y += widget.height + spacing
        elif right:
            for widget in self.children:
                x = (width - border - padding - widget.width)
                widget.topleft = x, y
                y += widget.height + spacing
        else:
            for widget in self.children:
                widget.topleft = x, y
                y += widget.height + spacing
            
    def draw_bg (self):
        """V.draw_bg () -> None

        Draws the VFrame background surface and returns it.

        Creates the visible surface of the VFrame and returns it to the
        caller.
        """
        return base.GlobalStyle.engine.draw_frame (self)

    def draw (self):
        """V.draw () -> None

        Draws the VFrame surface and places its children on it.
        """
        Frame.draw (self)

        self.dispose_widgets ()
        blit = self.image.blit

        if self.widget:
            blit (self.widget.image, self.widget.rect)
        for widget in self.children:
            blit (widget.image, widget.rect)
