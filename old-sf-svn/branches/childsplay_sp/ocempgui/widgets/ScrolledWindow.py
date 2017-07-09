# $Id: ScrolledWindow.py,v 1.38.2.3 2007/01/26 22:51:33 marcusva Exp $
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

"""A widget class, which can contain other widgets and uses optional
scrollbars."""

from pygame import K_RIGHT, K_LEFT, K_HOME, K_END, K_DOWN, K_UP, K_PAGEDOWN
from pygame import K_PAGEUP
from ScrollBar import HScrollBar, VScrollBar
from Bin import Bin
from BaseWidget import BaseWidget
from ViewPort import ViewPort
from StyleInformation import StyleInformation
from Constants import *
import base

class ScrolledWindow (Bin):
    """ScrolledWindow (width, height) -> ScrolledWindow

    A widget class, which supports horizontal and vertical scrolling.

    The ScrolledWindow is a viewport, which enables its child to be
    scrolled horizontally and vertically. It offers various scrolling
    types, which customize the bahviour of the supplied scrollbars.

    The scrolling behaviour of the ScrolledWindow can be adjusted
    through the 'scrolling' attribute or set_scrolling() method and can
    be one of the SCROLL_TYPES constants.

    Default action (invoked by activate()):
    Gives the ScrolledWindow the input focus.
    
    Mnemonic action (invoked by activate_mnemonic()):
    None

    Signals:
    SIG_KEYDOWN   - Invoked, when a key is pressed while the ScrolledWindow
                    has the input focus.
    SIG_MOUSEDOWN - Invoked, when a mouse button is pressed over the
                    ScrolledWindow.
    
    Attributes:
    scrolling  - The scrolling behaviour of the ScrolledWindow.
    vscrollbar - The vertical scrollbar of the ScrolledWindow.
    hscrollbar - The horizontal scrollbar of the ScrolledWindow.
    """
    def __init__ (self, width, height):
        Bin.__init__ (self)
        self._scrolling = SCROLL_AUTO

        # Scrollbars.
        self._vscroll = VScrollBar (height, height)
        self._vscroll.connect_signal (SIG_VALCHANGED, self._scroll_child)
        self._vscroll.parent = self
        self._hscroll = HScrollBar (width, width)
        self._hscroll.connect_signal (SIG_VALCHANGED, self._scroll_child)
        self._hscroll.parent = self

        self._vscroll_visible = False
        self._hscroll_visible = False

        # Scrolling will be handled directly by the ScrolledWindow.
        self._hscroll.set_focus = lambda self: False
        self._vscroll.set_focus = lambda self: False

        self.controls.append (self._vscroll)
        self.controls.append (self._hscroll)

        self._signals[SIG_KEYDOWN] = None # Dummy
        self._signals[SIG_MOUSEDOWN] = []

        # Respect the size.
        if width < self._hscroll.minsize[0]:
            width = self._hscroll.minsize[0]
        if height < self._vscroll.minsize[1]:
            height = self._vscroll.minsize[1]
        self.minsize = width, height

    def set_scrolling (self, scrolling):
        """S.set_scrolling (...) -> None

        Sets the scrolling behaviour for the ScrolledWindow.

        The scrolling can be a value of the SCROLL_TYPES list.
        SCROLL_AUTO causes the ScrolledList to display its scrollbars on
        demand only, SCROLL_ALWAYS will show the scrollbars permanently
        and SCROLL_NEVER will disable the scrollbars.

        Raises a ValueError, if the passed argument is not a value of
        the SCROLL_TYPES tuple.
        """
        if scrolling not in SCROLL_TYPES:
            raise ValueError ("scrolling must be a value from SCROLL_TYPES")
        if self._scrolling != scrolling:
            self._scrolling = scrolling
            self.dirty = True

    def set_child (self, child=None):
        """B.set_child (...) -> None

        Sets the child to display in the ScrolledList.

        Creates a parent-child relationship from the ScrolledList to a
        widget. If the widget does not support native scrolling, it will
        be packed into a ViewPort.
        """
        self.lock ()
        if child and not isinstance (child, ViewPort):
            self.vscrollbar.value = 0
            self.hscrollbar.value = 0
            child = ViewPort (child)
            child.minsize = self.minsize
        Bin.set_child (self, child)
        self.unlock ()
        
    def activate (self):
        """S.activate () -> None

        Activates the ScrolledWindow default action.

        Activates the ScrolledWindow default action. This usually means
        giving the ScrolledWindow the input focus.
        """
        if not self.sensitive:
            return
        self.focus = True
    
    def notify (self, event):
        """S.notify (...) -> None

        Notifies the ScrolledWindow about an event.
        """
        if not self.sensitive:
            return
        
        if event.signal in SIGNALS_MOUSE:
            eventarea = self.rect_to_client ()
            if event.signal == SIG_MOUSEDOWN:
                if eventarea.collidepoint (event.data.pos):
                    self.focus = True
                    self.run_signal_handlers (SIG_MOUSEDOWN, event.data)

                    # Mouse wheel.
                    for c in self.controls:
                        c.notify (event)
                    if not event.handled:
                        if self._vscroll_visible:
                            if event.data.button == 4:
                                self.vscrollbar.decrease ()
                            elif event.data.button == 5:
                                self.vscrollbar.increase ()
                        elif self._hscroll_visible:
                            if event.data.button == 4:
                                self.hscrollbar.decrease ()
                            elif event.data.button == 5:
                                self.hscrollbar.increase ()
                    event.handled = True
        
        elif (event.signal == SIG_KEYDOWN) and self.focus:
            if self._hscroll_visible:
                # Horizontal scrollbar key movement
                if event.data.key == K_RIGHT:
                    self.hscrollbar.increase ()
                    event.handled = True
                elif event.data.key == K_LEFT:
                    self.hscrollbar.decrease ()
                    event.handled = True
                elif event.data.key == K_END:
                    self.hscrollbar.value = self.hscrollbar.maximum
                    event.handled = True
                elif event.data.key == K_HOME:
                    self.hscrollbar.value = self.hscrollbar.minimum
                    event.handled = True
            if self._vscroll_visible:
                # Vertical scrollbar key movement
                if event.data.key == K_DOWN:
                    self.vscrollbar.increase ()
                    event.handled = True
                elif event.data.key == K_UP:
                    self.vscrollbar.decrease ()
                    event.handled = True
                elif event.data.key == K_PAGEUP:
                    val = self.vscrollbar.value - 10 * self.vscrollbar.step
                    if val > self.vscrollbar.minimum:
                        self.vscrollbar.value = val
                    else:
                        self.vscrollbar.value = self.vscrollbar.minimum
                    event.handled = True
                elif event.data.key == K_PAGEDOWN:
                    val = self.vscrollbar.value + 10 * self.vscrollbar.step
                    if val < self.vscrollbar.maximum:
                        self.vscrollbar.value = val
                    else:
                        self.vscrollbar.value = self.vscrollbar.maximum
                    event.handled = True
                elif event.data.key == K_END:
                    self.vscrollbar.value = self.vscrollbar.maximum
                    event.handled = True
                elif event.data.key == K_HOME:
                    self.vscrollbar.value = self.vscrollbar.minimum
                    event.handled = True

        Bin.notify (self, event)

    def _scroll_child (self):
        """S._scroll_child () -> None

        Scrolls the child of the ScrolledWindow.
        """
        if self.child != None:
            self.child.lock ()
            self.child.hadjustment = - int (self.hscrollbar.value)
            self.child.vadjustment = - int (self.vscrollbar.value)
            self.child.unlock ()
    
    def _update_scrollbars (self):
        """S._update_scrollbars (...) -> bool, bool

        Updates the size and maximum values of the attached scrollbars.

        Updates the size and values of the attached scrollbars and
        returns boolean values about their visibility in the order
        hscrollbar, vscrollbar.
        """
        old_vals = self._vscroll_visible, self._hscroll_visible

        if self.scrolling == SCROLL_NEVER:
            if self.child:
                self.child.minsize = self.minsize
            self.hscrollbar.sensitive = False
            self.vscrollbar.sensitive = False
            self._vscroll_visible = False
            self._hscroll_visible = False
            return False, False

        self.hscrollbar.bottom = self.bottom - self.top
        self.vscrollbar.right = self.right - self.left
        
        width = 0
        height = 0

        if self.child:
            width = self.child.real_width + 2 * self.padding
            height = self.child.real_height + 2 * self.padding

        # We are using the draw_border() method for the inner surface,
        # so we have to add the borders to the scrolling maximum.
        if self.scrolling == SCROLL_ALWAYS:
            self.vscrollbar.minsize = (self.vscrollbar.minsize[0],
                                       self.minsize[1] - \
                                       self.hscrollbar.height)
            self.hscrollbar.minsize = (self.minsize[0] - self.vscrollbar.width,
                                       self.hscrollbar.minsize[1])
            if self.child:
                self.child.maxsize = \
                                (self.minsize[0] - self.vscrollbar.size[0],
                                 self.minsize[1] - self.hscrollbar.size[1])
                self.child.minsize = self.child.maxsize
            if width < self.hscrollbar.minsize[0]:
                width = self.hscrollbar.minsize[0]
            self.hscrollbar.maximum = width
            if height < self.vscrollbar.minsize[1]:
                height = self.vscrollbar.minsize[1]
            self.vscrollbar.maximum = height
            self._vscroll_visible = True
            self._hscroll_visible = True
            self.vscrollbar.sensitive = True
            self.hscrollbar.sensitive = True

        elif self.scrolling == SCROLL_AUTO:
            # Check the sizes, so we can determine, how the scrollbars
            # need to be adjusted.
            self._hscroll_visible = self.minsize[0] < width
            self._vscroll_visible = self.minsize[1] < height

            if self._hscroll_visible:
                self._vscroll_visible = (self.minsize[1] -
                                         self.hscrollbar.height) < height
            if self._vscroll_visible:
                self._hscroll_visible = (self.minsize[0] -
                                         self.vscrollbar.width) < width
            
            if self._vscroll_visible and self._hscroll_visible:
                # Both scrollbars need to be shown.
                self.vscrollbar.minsize = (self.vscrollbar.minsize[0],
                                           self.minsize[1] - \
                                           self.hscrollbar.height)
                self.hscrollbar.minsize = (self.minsize[0] - \
                                           self.vscrollbar.width,
                                           self.hscrollbar.minsize[1])
                if self.child:
                    self.child.maxsize = \
                                (self.minsize[0] - self.vscrollbar.size[0],
                                 self.minsize[1] - self.hscrollbar.size[1])
                    self.child.minsize = self.child.maxsize
                self.vscrollbar.maximum = height
                self.hscrollbar.maximum = width
                self.vscrollbar.sensitive = True
                self.hscrollbar.sensitive = True

            elif self._vscroll_visible:
                # Only the vertical.
                self.vscrollbar.minsize = (self.vscrollbar.minsize[0],
                                           self.minsize[1])
                if self.child:
                    self.child.maxsize = \
                                (self.minsize[0] - self.vscrollbar.minsize[0],
                                 self.minsize[1])
                    self.child.minsize = self.child.maxsize
                self.vscrollbar.maximum = height
                self.vscrollbar.sensitive = True
                self.hscrollbar.sensitive = False

            elif self._hscroll_visible:
                # Only the horizontal.
                self.hscrollbar.minsize = (self.minsize[0],
                                           self.hscrollbar.minsize[1])
                if self.child:
                    self.child.maxsize = \
                                (self.minsize[0],
                                 self.minsize[1] - self.hscrollbar.size[1])
                    self.child.minsize = self.child.maxsize
                self.hscrollbar.maximum = width
                self.hscrollbar.sensitive = True
                self.vscrollbar.sensitive = False

            else:
                if self.child:
                    self.child.minsize = self.minsize
                # Neither vertical nor horizontal
                self.hscrollbar.sensitive = False
                self.vscrollbar.sensitive = False

        if not self.sensitive:
            self.hscrollbar.sensitive = False
            self.vscrollbar.sensitive = False

        return self._hscroll_visible, self._vscroll_visible
        
    def draw_bg (self):
        """S.draw_bg () -> Surface

        Draws the ScrolledWindow background surface and returns it.

        Creates the visible background surface of the ScrolledWindow and
        returns it to the caller.
        """
        return base.GlobalStyle.engine.draw_scrolledwindow (self)

    def draw (self):
        """W.draw () -> None

        Draws the ScrolledWindow surface.

        Creates the visible surface of the ScrolledWindow.
        """
        Bin.draw (self)
        blit = self.image.blit

        # Update the srollbars.
        self.hscrollbar.lock ()
        self.vscrollbar.lock ()
        hscroll, vscroll = self._update_scrollbars ()
        self.hscrollbar.unlock ()
        self.vscrollbar.unlock ()

        if hscroll:
            blit (self.hscrollbar.image, self.hscrollbar.rect)

        if vscroll:
            blit (self.vscrollbar.image, self.vscrollbar.rect)

        if self.child:
            blit (self.child.image, self.child.rect)

    scrolling = property (lambda self: self._scrolling,
                          lambda self, var: self.set_scrolling (var),
                          doc = "The scrolling behaviour for the " \
                          "ScrolledWindow.")
    vscrollbar = property (lambda self: self._vscroll,
                           doc = "The vertical scrollbar.")
    hscrollbar = property (lambda self: self._hscroll,
                           doc = "The herizontal scrollbar.")
