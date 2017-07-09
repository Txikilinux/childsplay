# $Id: TwistedRenderer.py,v 1.7.2.3 2006/12/25 13:05:46 marcusva Exp $
#
# Copyright (c) 2005, Benjamin Olsen
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

"""A Renderer that plays nicely with a threadedselectreactor from
Twisted.

Many thanks to Bob Ippolito for his work on threadedselectreactor and
the pygamedemo.py he created.

Written by Ben Olsen <ben@rickstranger.com>
"""

from pygame import QUIT, event
from pygame import error as PygameError
from pygame import time as PygameTime
from childsplay_sp.ocempgui.widgets import Renderer
from childsplay_sp.ocempgui.widgets.Constants import *

class TwistedRenderer (Renderer):
    """TwistedRenderer () -> TwistedRenderer

    A Renderer that allows the easy integration with Twisted.
    
    Because Twisted's threadedselectreactor *must* be shut down before
    the main loop shuts down, this Renderer will keep running until
    explicitly told to stop.

    Before starting the main loop, this Renderer will check to see if it
    has a Twisted reactor attached to it. This is an attribute set like
    any of the normal Renderer attributes:

    self.reactor = reactor

    If self.reactor is None (default), this will behave like a normal
    Renderer. If self.reactor has been set, the QUIT signal will call
    reactor.stop(), and then wait for reactor.addSystemEventTrigger to
    call self.stop(). This function will then stop the main loop.

    Usage
    -----
    Install the threadedselectreactor instead of the default reactor:

    from twisted.internet.threadedselectreactor import install
    install()
    from twisted.internet import reactor

    In the main section of your program, where you create the Renderer,
    just set TwistedRenderer's reactor:

    re = TwistedRenderer()
    re.reactor = reactor

    Everything else is handled internally by TwistedRenderer.

    Attributes:
    reactor - The twisted reactor attached to the TwistedRenderer.
    """
    def __init__ (self):
        Renderer.__init__ (self)
        self._reactor = None
        self._running = False
        
    def start (self):
        """T.start () -> None
        
        Overrides default start() to use self._running. If a reactor is
        attached, interleave self.waker
        """
        self._running = 1
        if self._reactor != None:
            self._reactor.interleave (self.waker)
        self._loop()
        
    def stop (self):
        """T.stop () -> None

        Tells the internal loop to stop running.
        """
        self._running = False
        
    def set_reactor (self, reactor):
        """T.set_reactor (...) -> None

        Sets the internal reactor.
        """
        if not hasattr (reactor, 'interleave'):
            raise AttributeError ("interleave() method not found in %s" %
                                  reactor)
        self._reactor = reactor
        self._reactor.addSystemEventTrigger ('after', 'shutdown', self.stop)

    def waker (self, func):
        """T.waker (...) -> None

        Used in threadedselectreactor.interleave.
        """
        event.post (event.Event (SIG_TWISTED, data=func))

    def distribute_events (self, *events):
        """T.distribute_events (...) -> None

        Overrides default distribute_events() to check for a reactor. If
        a reactor is found, the QUIT signal will call reactor.stop(). If
        there's no reactor attached, a QUIT signal will simply set
        self._running to False.
        """
        for event in events:
            if event.type == QUIT:
                if self._reactor != None:
                    self._reactor.stop ()
                else:
                    self._running = False

            elif event.type == SIG_TWISTED:
                event.data ()
            else:
                Renderer.distribute_events (self, (event))
        return True

    def _loop (self):
        """T._loop () -> None

        Overrides default _loop() so that it will not stop until
        self._running is false.
        """
        # Emit the tick event every 10 ms.
        PygameTime.set_timer (SIG_TICK, 10)
        delay = PygameTime.delay
        event_get = event.get
        pump = event.pump

        while self._running:
            pump ()
            # Get events and distribute them.
            events = event_get ()

            if not self.distribute_events (*events):
                return # QUIT event
            if self.timer > 0:
                delay (1000 / self.timer)

    reactor = property (lambda self: self._reactor,
                        lambda self, var: self.set_reactor (var),
                        doc = "The twisted reactor attached to the Renderer.")
