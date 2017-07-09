# $Id: Alignment.py,v 1.1.2.1 2007/01/28 11:24:30 marcusva Exp $
#
# Copyright (c) 2007, Marcus von Appen
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

"""A widget which controls the alignment of its child."""

from Bin import Bin
from Constants import *
import base

class Alignment (Bin):
    """Alignment (width, height) -> Alignment

    A Bin widget class which controls the alignment of its child.

    The Alignment widget allows its child to be aligned at its edges
    using the 'align' attribute and set_align() method. Dependant on the
    alignment type (see also ALIGN_TYPES) the child will be placed
    differently within the Alignment.

    alignment.align = ALIGN_TOP
    alignment.set_align (ALIGN_TOP)

    However, not every alignment make sense, so a ALIGN_TOP | ALIGN_BOTTOM
    would cause the widget to be placed at the top. The priority
    order for the alignment follows. The lower the value, the higher the
    priority.

    Alignment      Priority
    -----------------------
    ALIGN_TOP         0
    ALIGN_BOTTOM      1
    ALIGN_LEFT        0
    ALIGN_RIGHT       1
    ALIGN_NONE        2

    Default action (invoked by activate()):
    None
    
    Mnemonic action (invoked by activate_mnemonic()):
    None

    Attributes:
    align  - Alignment of the child.
    """
    def __init__ (self, width, height):
        Bin.__init__ (self)
        self._align = ALIGN_NONE
        self.minsize = width, height

    def set_focus (self, focus=True):
        """A.set_focus (...) -> bool

        Overrides the default widget input focus.

        Alignment widgets cannot be focused by default, thus this method
        always returns False and does not do anything.
        """
        return False

    def set_align (self, align):
        """A.set_align (...) -> None

        Sets the alignment for the child.

        Raises a TypeError, if the passed argument is not a value from
        ALIGN_TYPES.
        """
        if not constants_is_align (align):
            raise TypeError ("align must be a value from ALIGN_TYPES")
        self._align = align
        self.dirty = True

    def draw_bg (self):
        """A.draw_bg () -> Surface

        Draws the Alignment background surface and returns it.

        Creates the visible surface of the Alignment and returns it to the
        caller.
        """
        return base.GlobalStyle.engine.draw_alignment (self)

    def draw (self):
        """B.draw () -> None

        Draws the Alignment surface and places its child on it.
        """
        Bin.draw (self)

        rect = self.image.get_rect ()
        if self.child:
            self.child.center = rect.center

            if self.align & ALIGN_TOP == ALIGN_TOP:
                self.child.top = rect.top + self.padding
            elif self.align & ALIGN_BOTTOM == ALIGN_BOTTOM:
                self.child.bottom = rect.bottom - self.padding
            if self.align & ALIGN_LEFT == ALIGN_LEFT:
                self.child.left = rect.left + self.padding
            elif self.align & ALIGN_RIGHT == ALIGN_RIGHT:
                self.child.right = rect.right - self.padding

            self.image.blit (self.child.image, self.child.rect)

    align = property (lambda self: self._align,
                      lambda self, var: self.set_align (var),
                      doc = "The alignment to use for the child.")
