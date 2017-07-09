# $Id: StatusBar.py,v 1.16.2.2 2007/01/20 12:56:26 marcusva Exp $
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

"""A widget class, which can display information of any kind using a
stack technique.
"""

from datetime import datetime
from Container import Container
from Constants import *
from StyleInformation import StyleInformation
import base

_TIMER = 50

class StatusBar (Container):
    """StatusBar () -> StatusBar

    A widget class, which can display information using a stack.

    The StatusBar widget class can display the current date and info
    messages using a message stack.
    
    Info messages can be enabled or disabled using the 'tips' attribute
    or show_tips() method. If the tips are enabled, only the topmost
    (at last added) tip will be displayed.

    statusbar.tips = True
    statusbar.show_tips (False)

    The push_tip() method will put the message on the top of the stack,
    while the pop_tip() method will remove the topmost message. If there
    are several messages on the stack, pop_tip() will reveal previously
    added messages, which will be displayed then.

    statusbar.push_tip ('This is a message') # 'This is a message' is shown
    statusbar.push_tip ('Another message')   # 'Another message' is shown
    statusbar.pop_tip ()                     # 'This is a message' is shown

    To get the currently displayed message, the 'current_tip' attribute
    or get_current_tip() method can be used.

    current = statusbar.current_tip
    current = statusbar.get_current_tip ()

    The width of the area, that displays the tips can be adjusted using
    the 'tip_width' attribute or set_tip_width () method.
    If the rendered text exceeds the width of the area, it will be cut down
    to its width.

    statusbar.tip_width = 50
    statusbar.set_tip_width (50)

    Displaying the actual date can be enabled or disabled with the
    'date' attribute or show_date() method.

    statusbar.date = True
    statusbar.show_date (False)

    The display format of it can be adjusted through the 'date_format'
    attribute or set_date_format() method. The format has to be a string
    in a format, which can be understood by the strftime() method.

    statusbar.date_format = '%x'
    statusbar.set_date_format ('%H: %M')

    The current date (which can differ from the displayed one) can be
    fetched through the 'current_date' attribute. Usually the update resolution
    for the date is set to one second. Due to the internal drawing and update
    code it can happen that the the displayed and current date differ by one
    second.

    The width of the area, that displays the date can be adjusted using
    the 'date_width' attribute or set_date_width () method.
    If the rendered date exceeds the width of the area, it will be cut
    down to its width.

    statusbar.date_width = 50
    statusbar.set_date_width (50)

    Additionally you are able to place widgets on the StatusBar through
    the usual Container methods. The widgets will be placed between the
    info message text and the date.

    Note:
    The StatusBar updates itself every 500 ms. Thus you will not have a
    real time clock in the date display, which updates itself correctly
    every second.
    
    Default action (invoked by activate()):
    None
    
    Mnemonic action (invoked by activate_mnemonic()):
    None
    
    Attributes:
    tips         - Indicates, whether the info messages should be shown.
    current_tip  - The current tooltip to display.
    tip_width    - The width of the tip area. Default is 80.
    date         - Indicates, whether the date should be shown.
    current_date - The current date to display.
    date_format  - The display format of the date. Default is '%x %H:%M'
    date_width   - The width of the date area. Default is 90.
    """
    def __init__ (self):
        Container.__init__ (self)

        # Info values.
        self._showtips = True
        self._tips = []
        self._tipwidth = 80

        self._timer = _TIMER

        self._xoffset = 0
        
        # Date.
        self._showdate = True
        self._dateformat = "%x %H:%M:%S"
        self._datewidth = 90
        self._signals[SIG_TICK] = None

        # Default size.
        self.minsize = 204, 24

    def set_focus (self, focus=True):
        """S.set_focus (focus=True) -> None

        Overrides the set_focus() behaviour for the StatusBar.

        The StatusBar class is not focusable by default.
        """
        return False

    def set_tip_width (self, width):
        """S.set_tip_width (...) -> None

        Sets the width of the tip area.

        Raises a TypeError, if the passed argument is not a positive
        integer.
        """
        if (type (width) != int) or (width < 0):
            raise TypeError ("width must be a positive integer")
        self._tipwidth = width
        self.dirty = True

    def set_date_width (self, width):
        """S.set_date_width (...) -> None

        Sets the width of the date area.

        Raises a TypeError, if the passed argument is not a positive
        integer.
        """
        if (type (width) != int) or (width < 0):
            raise TypeError ("width must be a positive integer")
        self._datewidth = width
        self.dirty = True

    def show_tips (self, show):
        """S.show_tips (...) -> None

        Shows or hides the info message display of the StatusBar.
        """
        if show != self._showtips:
            self._showtips = show
            self.dirty = True

    def show_date (self, show):
        """S.show_date (...) -> None

        Shows or hides the date display of the StatusBar.
        """
        if show != self._showdate:
            self._showdate = show
            self.dirty = True
    
    def set_date_format (self, format):
        """S.set_date_format (...) -> None

        Sets the display format for the date.

        The passed format string has to be in a format, which can be
        understood by the strftime() method.
        """
        self._dateformat = format
        self.dirty = True
    
    def get_current_tip (self):
        """S.get_current_tip () -> string or unicode

        Gets the current info message to display.
        """
        length = len (self._tips)
        if length > 0:
            return self._tips[length - 1]
        return ""
    
    def push_tip (self, tip):
        """S.push_tip (...) -> None

        Puts a info message on the queue of the StatusBar.

        Raises a TypeError, if the passed argument is not a string or
        unicode.
        """
        if type (tip) not in (str, unicode):
            raise TypeError ("tip must be a string or unicode")
        self._tips.append (tip)
        self.dirty = True
    
    def pop_tip (self):
        """S.pop_tip () -> None

        Removes the last info message from the StatusBar queue.
        """
        if len (self._tips) > 0:
            self._tips.pop ()
            self.dirty = True

    def calculate_size (self):
        """S.calculate_size () -> int, int.

        Calculates the size needed by the children.

        Calculates the size needed by the children and returns the
        resulting width and height.
        """
        border = base.GlobalStyle.get_border_size \
                 (self.__class__, self.style,
                  StyleInformation.get ("STATUSBAR_BORDER"))
        width = 2 * (border + self.padding)
        height = 0
        spacing = self.spacing
        
        for widget in self.children:
            width += widget.width + spacing
            if widget.height > height:
                height = widget.height
        height += 2 * (border + self.padding)

        # Add width for the tips and date.
        if self.tips:
            width += self.tip_width
            if self.date:
                width += self.spacing
        if self.date:
            width += self.date_width
        if not self.tips and not self.date:
            width -= self.spacing

        return width, height
    
    def dispose_widgets (self):
        """S.dispose_widgets (...) -> None
        
        Moves the children of the StatusBar to their correct positions.
        """
        
        border = base.GlobalStyle.get_border_size \
                 (self.__class__, self.style,
                  StyleInformation.get ("STATUSBAR_BORDER"))
        padding = self.padding
        spacing = self.spacing
        diff = (self.height - 2 * (border + padding)) / 2

        x = self._xoffset
        addy = border + padding + diff
        
        for widget in self.children:
            y = border + padding + diff - widget.height / 2
            y = addy - widget.height / 2
            widget.topleft = (x, y)
            x += widget.width + spacing
    
    def notify (self, event):
        """S.notify (...) -> None

        Notifies the StatusBar about an event.
        """
        if event.signal == SIG_TICK:
            if self._timer == 0:
                self._timer = _TIMER
                if self.date:
                    self.dirty = True
            self._timer -= 1
    
    def draw_bg (self):
        """S.draw_bg () -> Surface

        Draws the background surface of the StatusBar and returns it.

        Creates the visible surface of the StatusBar and returns it to
        the caller.
        """
        return base.GlobalStyle.engine.draw_statusbar (self)

    def draw (self):
        """S.draw () -> None

        Draws the StatusBar surface and places its children on it.
        """
        Container.draw (self)

        cls = self.__class__
        style = base.GlobalStyle
        border = style.get_border_size \
                 (cls, self.style, StyleInformation.get ("STATUSBAR_BORDER"))
        blit = self.image.blit
        rect = self.image.get_rect()
        
        self._xoffset = self.padding + border
        # Draw the current tip.
        if self.tips:
            surface_tip = style.engine.draw_string (self.current_tip,
                                                    self.state, cls,
                                                    self.style)
            r = surface_tip.get_rect ()
            r.x = self._xoffset
            r.centery = rect.centery
            blit (surface_tip, r, (0, 0, self.tip_width, r.height))
            self._xoffset += self.tip_width + self.spacing

        # Place the children of the StatusBar and blit them.
        self.dispose_widgets ()
        for widget in self.children:
            blit (widget.image, widget.rect)

        # Draw the date.
        if self.date:
            surface_date = style.engine.draw_string (self.current_date,
                                                     self.state, cls,
                                                     self.style)
            r = surface_date.get_rect ()
            r.right = rect.right - border - self.padding
            r.centery = rect.centery
            blit (surface_date, r, (0, 0, self._datewidth, r.height))

    tips = property (lambda self: self._showtips,
                     lambda self, var: self.show_tips (var),
                     doc = "Indicates, whether the tooltips should be shown.")
    tip_width = property (lambda self: self._tipwidth,
                          lambda self, var: self.set_tip_width (var),
                          doc = "The width of the tip area.")
    date = property (lambda self: self._showdate,
                     lambda self, var: self.show_date (var),
                     doc = "Indicates, whether the date should be shown.")
    date_width = property (lambda self: self._datewidth,
                           lambda self, var: self.set_date_width (var),
                           doc = "The width of the date area.")
    current_tip = property (lambda self: self.get_current_tip (),
                            doc = "The current tooltip to display.")
    current_date = property (lambda self: datetime.now ().strftime \
                             (self._dateformat),
                             doc = "The current date to display.")
    date_format = property (lambda self: self._dateformat,
                            lambda self, var: self.set_date_format (var),
                            doc = "Sets the display format of the date.")
