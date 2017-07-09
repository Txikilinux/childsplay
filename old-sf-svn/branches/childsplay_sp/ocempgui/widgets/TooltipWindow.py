# $Id: TooltipWindow.py,v 1.1.2.2 2006/09/12 19:59:55 marcusva Exp $
#
# Copyright (c) 2006, Marcus von Appen
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

"""Tooltip Window class."""

from BaseWidget import BaseWidget
from Constants import *
from StyleInformation import StyleInformation
import base

class TooltipWindow (BaseWidget):
    """TooltipWindow (text) -> TooltipWindow

    A widget class that displays a line of text using a certain color.

    The TooltipWindow widgets is able to display a short amount of text.
    It is a completely non-interactive widget suitable for tooltip support
    and notification messages.

    The text to display on the TooltipWindow can be set through the 'text'
    attribute or set_text() method.

    window.text = 'A text to display'
    window.set_text ('A text to display')

    The 'padding' attribute and set_padding() method are used to place a
    certain amount of pixels between the text and the outer edges of the
    TooltipWindow.

    window.padding = 10
    window.set_padding (10)

    Default action (invoked by activate()):
    None
    
    Mnemonic action (invoked by activate_mnemonic()):
    None

    Attributes:
    text    - The text to display on the TooltipWindow.
    padding - Additional padding between text and borders. Default is 2.
    """
    def __init__ (self, text):
        BaseWidget.__init__ (self)
        self._padding = 2
        self._text = None
        self.set_text (text)

    def set_focus (self, focus=True):
        """T.set_focus (...) -> bool

        Overrides the default widget input focus.

        The TooltipWindow cannot be focused by default, thus this method
        always returns False and does not do anything.
        """
        return False

    def set_padding (self, padding):
        """T.set_padding (...) -> None

        Sets the padding between the edges and text of the TooltipWindow.

        The padding value is the amount of pixels to place between the
        edges of the TooltipWindow and the displayed text.

        Raises a TypeError, if the passed argument is not a positive
        integer.

        Note: If the 'size' attribute is set, it can influence the
        visible space between the text and the edges. That does not
        mean, that any padding is set.
        """
        if (type (padding) != int) or (padding < 0):
            raise TypeError ("padding must be a positive integer")
        self._padding = padding
        self.dirty = True

    def set_text (self, text):
        """T.set_text (...) -> None
        
        Sets the text of the TooltipWindow to the passed argument.

        Raises a TypeError, if the passed argument is not a string or
        unicode.
        """
        if type (text) not in (str, unicode):
            raise TypeError ("text must be a string or unicode")
        self._text = text
        self.dirty = True
    
    def draw_bg (self):
        """T.draw_bg () -> Surface

        Draws the background surface of the TooltipWindow and returns it.
        """
        return base.GlobalStyle.engine.draw_tooltipwindow (self)

    text = property (lambda self: self._text,
                     lambda self, var: self.set_text (var),
                     doc = "The text to display on the TooltipWindow.")
    padding = property (lambda self: self._padding,
                        lambda self, var: self.set_padding (var),
                        doc = "Additional padding between text and borders.")
