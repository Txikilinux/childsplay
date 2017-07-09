# $Id: INotifyable.py,v 1.4.2.1 2006/08/17 21:42:22 marcusva Exp $
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

"""Notifier interface class for event-capable objects."""

class INotifyable (object):
    """INotifyable () -> INotifyable

    A notifier interface class for event-capable objects.

    The INotifyable class is an interface, which should be used by
    objects, that make use of events using the EventManager class. It
    declares a single method, notify(), which consumes the events the
    object listens to.

    A short example for consuming events:

    class EventObject (INotifyable):
        def __init__ (self):
            ....
        def notify (self, event):
            if event.signal == 'EventObjectSignal':
                self.do_certain_action ()
            ...
    """
    def notify (self, event):
        """I.notify (...) -> None
        
        Notifies the object about an event.

        This method has to be implemented by inherited classes. Its
        signature matches the basic requirements of the EventManager
        class.
        """
        raise NotImplementedError

