# $Id: ToggleButton.py,v 1.29.2.5 2007/01/26 22:51:33 marcusva Exp $
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

"""A button widget, which can retain its state."""

from ButtonBase import ButtonBase
from Label import Label
from Constants import *
import base

class ToggleButton (ButtonBase):
    """ToggleButton (text) -> ToggleButton

    A button widget class, which can retain its state.

    The default ToggleButton widget looks and behaves usually the same
    as the Button widget except that it will retain its state upon
    clicks.

    The state of the ToggleButton can be set with the 'active' attribute
    or set_active() method. If the ToggleButton is active, the 'state'
    attribute will be set to STATE_ACTIVE by default and will be reset,
    if the ToggleButton is not active anymore.

    toggle.active = True
    toggle.set_active (False)

    The ToggleButton supports different border types by setting its
    'border' attribute to a valid value of the BORDER_TYPES constants.

    toggle.border = BORDER_SUNKEN
    toggle.set_border (BORDER_SUNKEN)

    Default action (invoked by activate()):
    The Button emulates a SIG_TOGGLED event and runs the connected
    callbacks.
    
    Mnemonic action (invoked by activate_mnemonic()):
    See the Button class.
    
    Signals:
    SIG_TOGGLED - Invoked, when the ToggleButton is toggled.

    Attributes:
    active - The current state of the ToggleButton as boolean.
    border - The border style to set for the ToggleButton.
    text   - The text to display on the ToggleButton.
    """
    def __init__ (self, text=None):
        ButtonBase.__init__ (self)
        self._border = BORDER_RAISED

        # Internal click handler
        self.__click = False
        self._active = False
        
        # The ToggleButton emits a 'toggled' event.
        self._signals[SIG_TOGGLED] = []

        self.set_text (text)

    def set_text (self, text=None):
        """T.set_text (...) -> None

        Sets the text to display on the ToggleButton.

        Sets the text to display on the ToggleButton by referring to the
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
        """T.get_text () -> string

        Returns the set text of the ToggleButton.

        Returns the text set on the Label of the ToggleButton.
        """
        if self.child:
            return self.child.text
        return ""

    def set_border (self, border):
        """T.set_border (...) -> None

        Sets the border type to be used by the ToggleButton.

        Raises a ValueError, if the passed argument is not a value from
        BORDER_TYPES
        """
        if border not in BORDER_TYPES:
            raise ValueError ("border must be a value from BORDER_TYPES")
        self._border = border
        self.dirty = True

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
        """T.set_state (...) -> None

        Sets the state of the ToggleButton.

        Sets the state of the ToggleButton and causes its child to set
        its state to the same value.
        """
        if (self.active and (state != STATE_ACTIVE)) or (self.state == state):
            return

        self.lock ()
        if self.child:
            self.child.state = state
        ButtonBase.set_state (self, state)
        self.unlock ()

    def set_active (self, active):
        """T.set_active (...) -> None

        Sets the state of the ToggleButton.
        """
        if active:
            if not self._active:
                self._active = True
                if self.sensitive:
                    self.state = STATE_ACTIVE
                # Enforce an update here, because the state might have
                # been already modified in the notify() method.
                self.dirty = True
        else:
            if self._active:
                self._active = False
                if self.sensitive:
                    self.state = STATE_NORMAL
                # Enforce an update here, because the state might have
                # been already modified in the notify() method.
                self.dirty = True
    
    def activate (self):
        """T.activate () -> None

        Activates the ToggleButton default action.

        Activates the Button default action. This usually means toggling
        the button, emulated by inverting the 'active' attribute and
        running the attached callbacks for the SIG_TOGGLED signal.
        """
        self.lock ()
        if not self.sensitive:
            return
        self.focus = True
        self.set_active (not self.active)
        self.unlock ()
        self.run_signal_handlers (SIG_TOGGLED)

    def notify (self, event):
        """T.notify (event) -> None

        Notifies the ToggleButton about an event.
        """
        if not self.sensitive:
            return

        if event.signal in SIGNALS_MOUSE:
            eventarea = self.rect_to_client ()

            if event.signal == SIG_MOUSEDOWN:
                if eventarea.collidepoint (event.data.pos):
                    self.focus = True
                    # The button only acts upon left clicks.
                    if event.data.button == 1:
                        self.__click = True
                        self.state = STATE_ACTIVE
                    self.run_signal_handlers (SIG_MOUSEDOWN, event.data)
                    event.handled = True

            elif event.signal == SIG_MOUSEUP:
                if eventarea.collidepoint (event.data.pos):
                    self.run_signal_handlers (SIG_MOUSEUP, event.data)
                    if event.data.button == 1:
                        if self.__click:
                            # The usual order for a ToggleButton: get a
                            # click and toggle state upon it.
                            self.run_signal_handlers (SIG_CLICKED)
                            self.set_active (not self.active)
                            self.run_signal_handlers (SIG_TOGGLED)
                            if not self.active:
                                self.state = STATE_ENTERED
                    event.handled = True
                elif (event.data.button == 1) and self.__click and \
                         not self.active:
                    # Only a half click was made, reset the state of the
                    # ToggleButton.
                    self.state = STATE_NORMAL

            elif event.signal == SIG_MOUSEMOVE:
                ButtonBase.notify (self, event)
        else:
            # Any other event will be escalated to the parent(s).
            ButtonBase.notify (self, event)

    def draw_bg (self):
        """T.draw () -> Surface

        Draws the ToggleButton background surface and returns it.

        Creates the visible surface of the ToggleButton and returns it
        to the caller.
        """
        return base.GlobalStyle.engine.draw_button (self)

    def draw (self):
        """R.draw () -> None

        Draws the ToggleButton surface and places its Label on it.
        """
        ButtonBase.draw (self)
        if self.child:
            self.child.center = self.image.get_rect ().center
            self.image.blit (self.child.image, self.child.rect)

    active = property (lambda self: self._active,
                       lambda self, var: self.set_active (var),
                       doc = "The state of the ToggleButton.")
    text = property (lambda self: self.get_text (),
                     lambda self, var: self.set_text (var),
                     doc = "The text of the ToggleButton.")
    border = property (lambda self: self._border,
                       lambda self, var: self.set_border (var),
                       doc = "The border style to set for the ToggleButton.")
