# $Id: Entry.py,v 1.45.2.5 2007/01/20 12:56:26 marcusva Exp $
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

"""A widget, which handles text input."""

from Editable import Editable
from childsplay_sp.ocempgui.draw import String
from Constants import *
import base

class Entry (Editable):
    """Entry (text="") -> Entry

    A widget class suitable for a single line of text input.

    The Entry widget is a text input box for a single line of text. It
    allows an unlimited amount of text input, but is usually more
    suitable for a small or medium amount, which can be scrolled, if the
    text size exceeds the visible widget size.
    
    The 'padding' attribute and set_padding() method are used to place a
    certain amount of pixels between the text and the outer edges of the
    Entry.

    entry.padding = 10
    entry.set_padding (10)

    The Entry supports different border types by setting its 'border'
    attribute to a valid value of the BORDER_TYPES constants.

    entry.border = BORDER_SUNKEN
    entry.set_border (BORDER_SUNKEN)

    It also features a password mode, which will cause it to display the
    text as asterisks ('*'). It will not encrypt or protect the internal
    text attribute however. The password mode can be set using the
    'password' attribute and set_password() method.

    entry.password = True
    entry.set_password (False)

    The Entry uses a default size for itself by setting the 'size'
    attribute to a width of 94 pixels and a height of 24 pixels.

    Default action (invoked by activate()):
    See the Editable class.
    
    Mnemonic action (invoked by activate_mnemonic()):
    None

    Signals:
    SIG_MOUSEDOWN - Invoked, when a mouse button gets pressed on the
                    Entry.
    SIG_MOUSEMOVE - Invoked, when the mouse moves over the Entry.

    Attributes:
    password - Characters will be drawn as '*' (asterisk).
    padding  - Additional padding between text and borders. Default is 2.
    border   - The border style to set for the Entry.
    """
    def __init__ (self, text=""):
        Editable.__init__ (self)
        self._realtext = None
        self._padding = 2
        self._border = BORDER_SUNKEN
        self._password = False
        
        self._offset = 0 # Front offset in pixels.

        # Pixel sizes of text to the left and right of caret, and char
        # the caret is at.
        self._leftsize = (0, 0)
        self._rightsize = (0, 0)
        self._cursize = (0, 0)
        self._font = None
        
        self._signals[SIG_MOUSEDOWN] = []
        self._signals[SIG_MOUSEMOVE] = []

        self.minsize = 94, 24 # Default size to use.
        self.text = text

    def set_padding (self, padding):
        """E.set_padding (...) -> None

        Sets the padding between the edges and text of the Entry.

        The padding value is the amount of pixels to place between the
        edges of the Entry and the displayed text.
        
        Raises a TypeError, if the argument is not a positive integer.
        """
        if (type (padding) != int) or (padding < 0):
            raise TypeError ("Argument must be a positive integer")
        self._padding = padding
        self.dirty = True

    def set_password (self, password):
        """E.set_password (...) -> None

        When this is set this to True, the entry's content will be drawn
        with '*' (asterisk) characters instead of the actual
        characters. This is useful for password dialogs, where it is
        undesirable for the password to be displayed on-screen.
        """
        self._password = password
        self.dirty = True

    def _set_caret_position (self, eventarea, position):
        """W._set_caret_position (...) -> None

        Sets the position of the caret based on the given pixel position.
        """
        # Get the relative mouse point.
        mpos = (position[0] - eventarea.x - self.padding,
                position[1] - eventarea.y - self.padding)
        
        if mpos[0] <= 0:
            # User clicked on the border or into the padding area.
            self.caret = 0
            return
        
        caret = self.caret
        mpoint = self._offset + mpos[0]
        left, right, current = self._get_text_overhang (caret)
        
        if mpoint > (left[0] + right[0]):
            # User clicked past the length of the text.
            self.caret = len (self.text)
            return

        # Find the click inside the text area
        while (mpoint > left[0]) and (caret <= len (self.text)):
            caret += 1
            left, right, current = self._get_text_overhang (caret)
        while (mpoint < left[0]) and (caret > 0):
            caret -= 1
            left, right, current = self._get_text_overhang (caret)

        # Move caret to left or right, based on center of clicked character
        if mpoint > (left[0] + (current[0] / 2) + self.border):
            caret += 1

        self.caret = caret

    def _get_text_overhang (self, pos):
        """E._get_text_overhang (...) -> (int, int), (int, int), (int, int)

        Gets the pixel sizes to the left and right of the caret and
        the character size the caret is at in this order..
        """
        # TODO: the text display should be separated in an own TextView
        # class.
        if self._font == None:
            self._cursize = (0, 0)
            return
        
        text = self.text
        if self.password:
            text = '*' * len (self.text)
        
        self._leftsize = self._font.size (text[:pos])
        self._rightsize = self._font.size (text[pos:])
        try:
            self._cursize = self._font.size (text[pos])
        except IndexError:
            self._cursize = (0, 0)
        return self._leftsize, self._rightsize, self._cursize

    def _calculate_offset (self, textwidth, font):
        """E._calculate_offset (...) -> int

        Calculates the left pixel offset for the Entry text.
        """
        self._font = font
        self._get_text_overhang (self.caret)
        
        bump_size = self.minsize[0] / 4

        while self._leftsize[0] < self._offset:
            new_offset = self._offset - bump_size
            self._offset = max (new_offset, 0)
        while self._leftsize[0] > (self._offset + textwidth):
            self._offset += bump_size
        return min (-self._offset, 0)
    
    def notify (self, event):
        """E.notify (...) -> None

        Notifies the Entry about an event.
        """
        if not self.sensitive:
            return
        
        if event.signal == SIG_MOUSEDOWN:
            eventarea = self.rect_to_client ()
            if eventarea.collidepoint (event.data.pos):
                self.run_signal_handlers (SIG_MOUSEDOWN, event.data)
                if event.data.button == 1:
                    self._caret_visible = True
                    self._set_caret_position (eventarea, event.data.pos)
                    if not self.focus:
                        self.activate ()
                event.handled = True

        elif event.signal == SIG_MOUSEMOVE:
            eventarea = self.rect_to_client ()
            if eventarea.collidepoint (event.data.pos):
                self.run_signal_handlers (SIG_MOUSEMOVE, event.data)
                self.entered = True
                event.handled = True
            else:
                self.entered = False

        Editable.notify (self, event)

    def set_border (self, border):
        """E.set_border (...) -> None

        Sets the border type to be used by the Entry.

        Raises a ValueError, if the passed argument is not a value from
        BORDER_TYPES
        """
        if border not in BORDER_TYPES:
            raise ValueError ("border must be a value from BORDER_TYPES")
        self._border = border
        self.dirty = True

    def draw_bg (self):
        """E.draw_bg () -> Surface

        Draws the surface of the Entry and returns it.

        Draws the background surface of the Entry and returns it.
 
        Creates the visible background surface of the Entry and returns
        it to the caller.
        """
        return base.GlobalStyle.engine.draw_entry (self)

    def draw (self):
        """E.draw () -> None

        Draws the Entry surface.
        """
        Editable.draw (self)
        cls = self.__class__
        style = base.GlobalStyle
        engine = style.engine
        st = self.style or style.get_style (cls)
        border = style.get_border_size (cls, st, self.border)
        text = self.text
        rect = self.image.get_rect ()

        if self.password:
            text = '*' * len (self.text)
        rtext = style.engine.draw_string (text, self.state, cls, st)

        # The 'inner' surface, which we will use for blitting the text.
        sf_text = engine.draw_rect (rect.width - 2 * (self.padding + border),
                                    rect.height - 2 * (self.padding + border),
                                    self.state, cls, st)

        # Adjust entry offset based on caret location.
        font = String.create_font \
               (style.get_style_entry (cls, st, "font", "name"),
                style.get_style_entry (cls, st, "font", "size"))
        rect_sftext = sf_text.get_rect ()
        blit_pos = self._calculate_offset (rect_sftext.width, font)
        
        sf_text.blit (rtext, (blit_pos, 0))

        # Draw caret.
        if self.focus and self.caret_visible:
            # The caret position is at the end of the left overhang.
            caret_pos = self._get_text_overhang (self.caret)[0][0]
            engine.draw_caret (sf_text, blit_pos + caret_pos, 1, 2, self.state,
                               cls, st)

        rect_sftext.center = rect.center
        self.image.blit (sf_text, rect_sftext)

    padding = property (lambda self: self._padding,
                        lambda self, var: self.set_padding (var),
                        doc = "The additional padding for the Entry.")
    border = property (lambda self: self._border,
                       lambda self, var: self.set_border (var),
                       doc = "The border style to set for the Entry.")
    password = property (lambda self: self._password,
                         lambda self, var: self.set_password (var),
                         doc = "Indicates the password mode for the Entry.")
