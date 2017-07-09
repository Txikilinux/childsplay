# $Id: ButtonBase.py,v 1.3.2.6 2006/09/16 11:28:20 marcusva Exp $
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

"""An abstract widget for button type widget implementations."""

from pygame import time as PygameTime
from pygame import K_SPACE, K_KP_ENTER, K_RETURN
from Bin import Bin
from Constants import *
import base

class ButtonBase (Bin):
    """
    ButtonBase () -> ButtonBase

    An abstract base class that implements basic button logic.

    The ButtonBase class is an abstract class, that implements a minimal
    set of events and methods to make it suitable for button type
    widgets. It implements the most important mouse signal types and how
    to handle them..

    Default action (invoked by activate()):
    The ButtonBase emulates a SIG_CLICKED event and runs the connected
    callbacks.

    Mnemonic action (invoked by activate_mnemonic()):
    The ButtonBase invokes the activate_mnemonic() method of its child
    (if any).

    Signals:
    SIG_MOUSEDOWN - Invoked, when a mouse button is pressed on the
                    ButtonBase.
    SIG_MOUSEUP   - Invoked, when a mouse button is released on the
                    ButtonBase.
    SIG_MOUSEMOVE - Invoked, when the mouse moves over the ButtonBase.
    SIG_CLICKED   - Invoked, when the left mouse button is pressed AND
                    released over the ButtonBase.
    """
    def __init__ (self):
        Bin.__init__ (self)
       
        # Internal click detector.
        self.__click = False

        # Signals, the button listens to.
        self._signals[SIG_MOUSEDOWN] = []
        self._signals[SIG_MOUSEUP] = []
        self._signals[SIG_MOUSEMOVE] = []
        self._signals[SIG_KEYDOWN] = None # Dummy for keyboard activation.
        self._signals[SIG_CLICKED] = []

    def activate_mnemonic (self, mnemonic):
        """B.activate_mnemonic (...) -> bool

        Activates the mnemonic of the ButtonBase its child.
        """
        if self.child:
            return self.child.activate_mnemonic (mnemonic)
        return False

    def activate (self):
        """B.activate () -> None

        Activates the ButtonBase default action.

        Activates the ButtonBase default action. This usually means a
        click, emulated by setting the state to STATE_ACTIVE, forcing an
        update, setting the state back to STATE_NORMAL and running the
        attached callbacks for the SIG_CLICKED event.
        """
        if not self.sensitive:
            return
        self.lock ()
        self.focus = True
        self.state = STATE_ACTIVE
        self.unlock ()
        PygameTime.delay (50)
        self.state = STATE_NORMAL
        self.run_signal_handlers (SIG_CLICKED)

    def notify (self, event):
        """B.notify (...) -> None

        Notifies the ButtonBase about an event.
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
                        if self.state == STATE_ACTIVE:
                            self.state = STATE_ENTERED
                        else:
                            self.state = STATE_NORMAL
                        
                        # Check for a previous left click.
                        if self.__click:
                            self.__click = False
                            self.run_signal_handlers (SIG_CLICKED)
                    event.handled = True
                            
                elif event.data.button == 1:
                    # Reset the 'clicked' state for the button, if the mouse
                    # button 1 is released at another location.
                    self.__click = False
                    self.state = STATE_NORMAL

            elif event.signal == SIG_MOUSEMOVE:
                if eventarea.collidepoint (event.data.pos):
                    if not self.__click:
                        self.state = STATE_ENTERED
                    else:
                        self.state = STATE_ACTIVE
                    
                    self.run_signal_handlers (SIG_MOUSEMOVE, event.data)
                    self.entered = True
                    event.handled = True
                else:
                    self.entered = False

        elif (event.signal == SIG_KEYDOWN) and self.focus:
            if event.data.key in (K_KP_ENTER, K_RETURN):
                # Activate the focused button, if the user presses
                # space, return or enter.
                self.activate ()
                event.handled = True
        
        Bin.notify (self, event)
