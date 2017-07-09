# $Id: Window.py,v 1.28.2.3 2006/09/14 23:32:01 marcusva Exp $
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

"""Toplevel Window class."""

from BaseWidget import BaseWidget
from Bin import Bin
from Container import Container
from Constants import *
from StyleInformation import StyleInformation
import base

class Window (Bin):
    """Window (title=None) -> Window

    A widget class, that implements a window-like behaviour.

    The Window class is a container, which provides a window-like look
    and feel, can be moved around the screen and supports an additional
    caption bar.

    The title to display on the Window caption bar can be set using the
    'title' attribute or set_title() method.

    window.title = 'Window caption'
    window.set_title ('Another title')

    It is possible to influence the position of the attached child with
    the 'align' attribute and set_align() method. Alignments can be
    combined bitwise to place the child at any of the eight possible
    positions.

    However, not every alignment make sense, so a ALIGN_TOP | ALIGN_BOTTOM
    would cause the child to be placed at the bottom. The priority
    order for the alignment follows. The lower the value, the higher the
    priority.
    
    Alignment      Priority
    -----------------------
    ALIGN_BOTTOM      0
    ALIGN_TOP         1
    ALIGN_LEFT        0
    ALIGN_RIGHT       1
    ALIGN_NONE        2
    
    Additionally the Window can be moved around the screen by pressing
    and holding the left mouse button on its caption bar and moving the
    mouse around.
    
    Default action (invoked by activate()):
    None
    
    Mnemonic action (invoked by activate_mnemonic()):
    None

    Signals:
    SIG_MOUSEDOWN - Invoked, when a mouse button is pressed on the
                    Window.
    SIG_MOUSEUP   - Invoked, when a mouse button is released on the
                    Window.
    SIG_MOUSEMOVE - Invoked, when the mouse moves over the Window.
    
    Attributes:
    title - The caption of the Window.
    align - Alignment of the child.
    """
    def __init__ (self, title=None):
        Bin.__init__ (self)
        self.__stopevents = False
        self._title = None

        self._align = ALIGN_NONE
        
        # Rectangle area for mouse click & movement on the window
        # caption.
        self._captionrect = None

        # State variables for button pressing and mouse movements.
        self.__pressed = False
        self.__oldpos = None

        self._keepactive = False
        
        self._signals[SIG_MOUSEDOWN] = []
        self._signals[SIG_MOUSEUP] = []
        self._signals[SIG_MOUSEMOVE] = []

        self.minsize = (100, 20)
        self.set_title (title)

    def set_focus (self, focus=True):
        """W.set_focus (...) -> None

        Sets the input and action focus of the window.
        
        Sets the input and action focus of the window and returns True
        upon success or False, if the focus could not be set.
        """
        self.lock ()
        if focus:
            self.state = STATE_ACTIVE
        elif (not self._keepactive) and (self.state == STATE_ACTIVE):
            self.state = STATE_NORMAL
        Bin.set_focus (self, focus)
        self.unlock ()
        return True

    def set_title (self, text=None):
        """W.set_title (...) -> None

        Sets the title caption to display on the Window.

        Sets the text to display as title on the Window.

        Raises a TypeError, if the passed argument is not a string or
        unicode.
        """
        if text and (type (text) not in (str, unicode)):
            raise TypeError ("text must be a string or unicode")
        self._title = text
        self.dirty = True

    def set_align (self, align):
        """W.set_align (...) -> None

        Sets the alignment for the child of the Window.
        """
        if not constants_is_align (align):
            raise TypeError ("align must be a value from ALIGN_TYPES")
        self._align = align
        self.dirty = True

    def _move_to_position (self, pos):
        """W._move_to_position (...) -> None

        Moves the Window to the position relative from itself.
        """
        self.topleft = (self.topleft[0] + pos[0] - self.__oldpos[0], \
                        self.topleft[1] + pos[1] - self.__oldpos[1])
        self._captionrect.topleft = self.topleft
        self.__oldpos = pos

    def notify (self, event):
        """W.notify (event) -> None

        Notifies the window about an event.
        """
        if not self.sensitive:
            return

        # Recursively notify all attached children.
        if self.child:
            self._notify_children (self.child, event)
        if self.__stopevents:
            return

        for control in self.controls:
            if event.handled:
                return
            self._notify_children (control, event)

        if event.signal in SIGNALS_MOUSE:
            eventarea = self.rect_to_client ()
            if event.signal == SIG_MOUSEDOWN:
                if eventarea.collidepoint (event.data.pos):
                    if not event.handled:
                        self.focus = True
                        self.run_signal_handlers (SIG_MOUSEDOWN, event.data)

                    if self._captionrect.collidepoint (event.data.pos):
                        if event.data.button == 1:
                            # Initiate window movement.
                            self.state = STATE_ACTIVE
                            self.__pressed = True
                            self.__oldpos = event.data.pos
                    event.handled = True
                else:
                    self.state = STATE_NORMAL

            elif event.signal == SIG_MOUSEUP:
                if eventarea.collidepoint (event.data.pos):
                    self.run_signal_handlers (SIG_MOUSEUP, event.data)
                    if event.data.button == 1:
                        if self.__pressed:
                            self.__pressed = False
                    event.handled = True
            
            elif event.signal == SIG_MOUSEMOVE:
                if self.__pressed:
                    # The window is moved.
                    self._move_to_position (event.data.pos)
                    event.handled = True
                elif eventarea.collidepoint (event.data.pos):
                    self.run_signal_handlers (SIG_MOUSEMOVE, event.data)
                    event.handled = True

        elif event.signal == SIG_FOCUSED:
            # Keep the active state of the window, if it contains the child
            if self._contains (self, event.data):
                if self.state != STATE_ACTIVE:
                    self.state = STATE_ACTIVE
                self._keepactive = True
            else:
                self._keepactive = False
        
        Bin.notify (self, event)

    def _notify_children (self, widget, event):
        """W._notify_children (...) -> None

        Notifies all widgets of the Window.
        """
        if not self.__stopevents:
            if not event.handled:
                widget.notify (event)
                if not self.__stopevents:
                    for control in widget.controls:
                        self._notify_children (control, event)
                    if isinstance (widget, Bin) and (widget.child != None):
                        self._notify_children (widget.child, event)
                    elif isinstance (widget, Container):
                        for child in widget.children:
                            self._notify_children (child, event)

    def _contains (self, parent, widget):
        """W.contains (...) -> bool

        Checks, whether the Window contains the widget.
        """
        contains = self._contains
        
        if parent == widget:
            return True
        for control in parent.controls:
            if control == widget:
                return True
            elif contains (control, widget):
                return True

        if isinstance (parent, Bin):
            if (parent.child != None) and contains (parent.child, widget):
                return True
        elif isinstance (parent, Container):
            for child in parent.children:
                if contains (child, widget):
                    return True
        return False

    def dispose_widget (self):
        """W.dispose_widget (...) -> int, int

        Moves the child of the Window to its correct position.
        """
        cls = self.__class__
        style = base.GlobalStyle
        st = self.style or style.get_style (cls)
        border = style.get_border_size (cls, st,
                                        StyleInformation.get ("WINDOW_BORDER"))
        dropshadow = style.get_style_entry (cls, st, "shadow")
        
        width = self.image.get_rect ().width
        height = self.image.get_rect ().height
        
        posx = (width - dropshadow - self.child.width) / 2
        posy = self._captionrect.height + \
               (height - self._captionrect.height - self.child.height - \
                dropshadow) / 2
        if self.align & ALIGN_LEFT:
            posx = border + self.padding
        elif self.align & ALIGN_RIGHT:
            posx = width - self.child.width - border - self.padding - \
                   dropshadow
        if self.align & ALIGN_TOP:
            posy = self._captionrect.height + self.padding
        elif self.align & ALIGN_BOTTOM:
            posy = height - self.child.height - border - self.padding - \
                   dropshadow
        return posx, posy

    def draw_bg (self):
        """W.draw_bg () -> Surface

        Draws the background surface of the Window and returns it.
        """
        return base.GlobalStyle.engine.draw_window (self)

    def draw (self):
        """W.draw () -> None
        
        Draws the Window.
        """
        Bin.draw (self)
        cls = self.__class__
        style = base.GlobalStyle
        st = self.style or style.get_style (cls)
        dropshadow = style.get_style_entry (cls, st, "shadow")
        rect = self.image.get_rect ()
        

        # Create the caption.
        surface_caption = style.engine.draw_caption (rect.width - dropshadow,
                                                     self.title, self.state,
                                                     cls, st)
        self._captionrect = rect
        self._captionrect = surface_caption.get_rect ()
        self._captionrect.topleft = self.topleft

        # Blit the caption.
        self.image.blit (surface_caption, (0, 0))

        # Position and blit the child.
        if self.child:
            posx, posy = self.dispose_widget ()
            self.child.topleft = posx, posy
            self.image.blit (self.child.image, (posx, posy))

    def destroy (self):
        """D.destroy () -> None

        Destroys the Window and removes it from its event system.
        """
        self.__stopevents = True
        Bin.destroy (self)
    
    title = property (lambda self: self._title,
                      lambda self, var: self.set_title (var),
                      doc = "The title caption of the Window.")
    align = property (lambda self: self._align,
                      lambda self, var: self.set_align (var),
                      doc = "The alignment of the child.")
