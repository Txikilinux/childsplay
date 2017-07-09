# $Id: CheckButton.py,v 1.14 2006/06/05 09:20:23 marcusva Exp $
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

"""A button widget with a check box."""

from ToggleButton import ToggleButton
from ButtonBase import ButtonBase
from Constants import *
from StyleInformation import StyleInformation
import base

class CheckButton (ToggleButton):
    """CheckButton (text) -> CheckButton

    A button widget class with a check displaying its state.

    The CheckButton widget has the same functionality as the
    ToggleButton widget, but uses a different look. It places a small
    check box besides its Label, which displays the state of the
    CheckButton.
    
    Default action (invoked by activate()):
    See the ToggleButton class.
    
    Mnemonic action (invoked by activate_mnemonic()):
    See the ToggleButton class.
    """
    def __init__ (self, text=None):
        ToggleButton.__init__ (self, text)

    def draw_bg (self):
        """C.draw_bg () -> Surface

        Draws the CheckButton background surface and returns it.

        Creates the visible surface of the CheckButton and returns it to
        the caller.
        """
        return base.GlobalStyle.engine.draw_checkbutton (self)

    def draw (self):
        """C.draw () -> None

        Draws the CheckButton surface.

        Creates the visible surface of the CheckButton and places a
        check box and its Label on it.
        """
        border_active = base.GlobalStyle.get_border_size \
                        (self.__class__, self.style,
                         StyleInformation.get ("ACTIVE_BORDER"))

        ButtonBase.draw (self)
        if self.child:
            self.child.centery = self.image.get_rect ().centery
            self.child.x = self.padding + border_active + \
                           StyleInformation.get ("CHECK_SPACING") + \
                           StyleInformation.get ("CHECK_SIZE")
            self.image.blit (self.child.image, self.child.rect)
