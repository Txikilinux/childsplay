# $Id: Box.py,v 1.1.2.1 2007/01/06 10:44:59 marcusva Exp $
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

"""A container, which allows absolute positioning of its widgets."""

from Container import Container
from Constants import *
import base

class Box (Container):
    """Box (width, height) -> Box

    A container widget which allows absolute positioning of its widgets.

    The Box widget places its attached children relative to it own
    topleft coordinates but does not layout them. Instead they are
    positioned absolutely, which includes possible overlapping blits
    outside of the visible Box area.

    Default action (invoked by activate()):
    None
    
    Mnemonic action (invoked by activate_mnemonic()):
    None
    """
    def __init__ (self, width, height):
        Container.__init__ (self)
        self.minsize = width, height

    def set_focus (self, focus=True):
        """B.set_focus (focus=True) -> None

        Overrides the set_focus() behaviour for the Box.

        The Box class is not focusable by default. It is a layout
        class for other widgets, so it does not need to get the input
        focus and thus it will return false without doing anything.
        """
        return False

    def draw_bg (self):
        """B.draw_bg () -> None

        Draws the Box background surface and returns it.

        Creates the visible surface of the Box and returns it to the
        caller.
        """
        return base.GlobalStyle.engine.draw_box (self)

    def draw (self):
        """B.draw () -> None

        Draws the Box surface and places its children on it.
        """
        Container.draw (self)

        blit = self.image.blit
        for widget in self.children:
            blit (widget.image, widget.rect)
