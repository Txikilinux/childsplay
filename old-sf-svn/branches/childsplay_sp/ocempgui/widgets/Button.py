# $Id: Button.py,v 1.42.2.2 2007/01/28 11:24:30 marcusva Exp $
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

"""A widget, which acts upon different mouse events."""

from ButtonBase import ButtonBase
from Label import Label
from Constants import *
import base

class Button (ButtonBase):
    """Button (text=None) -> Button ()

    A widget class, which can react upon mouse events.

    The Button widget can listen to mouse events such as clicks or a
    pressed button and can display a short text.

    The text to display on the Button can be set using the 'text'
    attribute or the set_text() method. The text is displayed using a
    Label widget, which is placed upon the Button surface, thus all
    text capabilities of the Label, such as mnemonics, can be applied
    to the Button as well.

    button.text = '#Click me'      # Use the C character as mnemonic.
    button.text = 'Button'         # A simple text.
    button.set_text ('Button ##1') # Creates the text 'Button #1'

    To operate on the displayed Label directly (which is NOT
    recommended), the 'child' attribute and set_child() method can be
    used. They have a slightly different behaviour than the methods of
    the ButtonBase class and allow only Label widgets to be assigned to
    the Button. Additionally the Label its 'widget' attribute will be
    bound to the Button.

    button.child = Label ('#Button')
    button.set_child (None)

    The Button supports different border types by setting its 'border'
    attribute to a valid value of the BORDER_TYPES constants.

    button.border = BORDER_SUNKEN
    button.set_border (BORDER_SUNKEN)

    Note: Changing the 'state' attribute of the Button will also
    affect the state of the Label placed on the Button.

    Default action (invoked by activate()):
    See the ButtonBase class.
    
    Mnemonic action (invoked by activate_mnemonic()):
    See the ButtonBase class.
    
    Attributes:
    text   - The text to display on the Button.
    border - The border style to set for the Button.
    """
    def __init__ (self, text=None):
        ButtonBase.__init__ (self)
        self._border = BORDER_RAISED
        self.set_text (text)

    def set_text (self, text=None):
        """B.set_text (...) -> None

        Sets the text to display on the Button.

        Sets the text to display on the Button by referring to the
        'text' attribute of its child Label.
        """
        if text != None:
            if self.child:
                self.child.set_text (text)
            else:
                self.child = Label (text)
        else:
            self.child = None

    def get_text (self):
        """B.get_text () -> string

        Returns the set text of the Button.

        Returns the text set on the Label of the Button.
        """
        if self.child:
            return self.child.text
        return ""
    
    def set_child (self, child=None):
        """B.set_child (...) -> None

        Sets the Label to display on the Button.

        Creates a parent-child relationship from the Button to a Label
        and causes the Label to set its mnemonic widget to the Button.

        Raises a TypeError, if the passed argument does not inherit
        from the Label class.
        """
        self.lock ()
        if child and not isinstance (child, Label):
            raise TypeError ("child must inherit from Label")
        ButtonBase.set_child (self, child)
        if child:
            child.set_widget (self)
            if not child.style:
                child.style = self.style or \
                              base.GlobalStyle.get_style (self.__class__)
        self.unlock ()

    def set_state (self, state):
        """B.set_state (...) -> None

        Sets the state of the Button.

        Sets the state of the Button and causes its child to set its
        state to the same value.
        """
        if self.state == state:
            return

        self.lock ()
        if self.child:
            self.child.state = state
        ButtonBase.set_state (self, state)
        self.unlock ()

    def set_border (self, border):
        """B.set_border (...) -> None

        Sets the border type to be used by the Button.

        Raises a ValueError, if the passed argument is not a value from
        BORDER_TYPES
        """
        if border not in BORDER_TYPES:
            raise ValueError ("border must be a value from BORDER_TYPES")
        self._border = border
        self.dirty = True

    def draw_bg (self):
        """B.draw_bg () -> Surface

        Draws the Button background surface and returns it.

        Creates the visible surface of the Button and returns it to the
        caller.
        """
        return base.GlobalStyle.engine.draw_button (self)

    def draw (self):
        """B.draw () -> None

        Draws the Button surface and places its Label on it.
        """
        ButtonBase.draw (self)
        if self.child:
            self.child.center = self.image.get_rect ().center
            self.image.blit (self.child.image, self.child.rect)

    text = property (lambda self: self.get_text (),
                     lambda self, var: self.set_text (var),
                     doc = "The text of the Button.")
    border = property (lambda self: self._border,
                       lambda self, var: self.set_border (var),
                       doc = "The border style to set for the Button.")
